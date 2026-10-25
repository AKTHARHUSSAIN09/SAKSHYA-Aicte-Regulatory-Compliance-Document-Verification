from typing import List, Dict, Any, Optional
import io
from datetime import datetime
from PIL import Image
import fitz  # PyMuPDF

from .models import DocumentForensicReport, ForensicFinding, ForensicVerdict
from .metadata_analyzer import PDFMetadataForensics
from .ela_detector import ErrorLevelAnalysisDetector
from .hash_verifier import PerceptualHashDeduplicator

class DocumentForensicsEngine:
    """
    Unified Multi-Layer Forensic Analysis Engine.
    Executes:
    1. PyMuPDF stream & metadata inspection (Canva, Photoshop, ModDate < CreationDate)
    2. OpenCV Error Level Analysis (ELA) for image compression variance & spliced numbers
    3. SHA-256 and perceptual dHash cross-institutional deduplication
    """
    def __init__(self):
        self.metadata_analyzer = PDFMetadataForensics()
        self.ela_detector = ErrorLevelAnalysisDetector()
        self.dedup_verifier = PerceptualHashDeduplicator()

    def analyze_document(
        self,
        document_id: str,
        file_name: str,
        file_bytes: bytes,
        institution_id: str = "INST-001",
        institution_name: str = "Unknown College"
    ) -> DocumentForensicReport:
        findings: List[ForensicFinding] = []
        scores: List[float] = []
        meta_summary: Dict[str, Any] = {}
        pil_first_page: Optional[Image.Image] = None

        is_pdf = file_name.lower().endswith(".pdf") or file_bytes[:4] == b"%PDF"

        # 1. PDF Metadata Analysis
        if is_pdf:
            meta_score, meta_findings, meta_summary = self.metadata_analyzer.analyze_pdf_bytes(file_bytes)
            scores.append(meta_score)
            for f in meta_findings:
                findings.append(ForensicFinding(
                    finding_id=f"FIND-META-{len(findings)+1}",
                    category="METADATA_ANALYSIS",
                    severity=f.get("severity", "MEDIUM"),
                    risk_score=f.get("risk_score", 0.5),
                    title=f.get("title", "Metadata Anomaly"),
                    description=f.get("description", ""),
                    technical_details=f.get("technical_details", {})
                ))

            # Extract first page as image for ELA
            try:
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                if len(doc) > 0:
                    page = doc[0]
                    pix = page.get_pixmap(dpi=150)
                    pil_first_page = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            except Exception:
                pass
        else:
            try:
                pil_first_page = Image.open(io.BytesIO(file_bytes))
            except Exception:
                pass

        # 2. Error Level Analysis (ELA)
        if pil_first_page:
            try:
                ela_score, stats, heatmap_b64 = self.ela_detector.analyze_image(pil_first_page)
                scores.append(ela_score)
                if stats.get("tampered_clusters_count", 0) > 0 or ela_score >= 0.4:
                    findings.append(ForensicFinding(
                        finding_id=f"FIND-ELA-{len(findings)+1}",
                        category="ERROR_LEVEL_ANALYSIS",
                        severity="CRITICAL" if ela_score >= 0.6 else "HIGH",
                        risk_score=ela_score,
                        title="Pixel Compression Variance Detected (ELA)",
                        description=(
                            f"Error Level Analysis identified {stats.get('tampered_clusters_count', 0)} localized "
                            f"pixel regions with abnormal compression signatures. This typically indicates "
                            f"spliced numerical figures, superimposed seals, or modified certificate dates."
                        ),
                        technical_details=stats,
                        visual_evidence_b64=heatmap_b64
                    ))
            except Exception as e:
                pass

        # 3. Deduplication Check
        sha, phash, dedup_findings = self.dedup_verifier.register_and_check(
            doc_id=document_id,
            institution_id=institution_id,
            institution_name=institution_name,
            file_bytes=file_bytes,
            pil_image=pil_first_page
        )
        for df in dedup_findings:
            scores.append(df.get("risk_score", 0.8))
            findings.append(ForensicFinding(
                finding_id=f"FIND-DEDUP-{len(findings)+1}",
                category="DEDUPLICATION",
                severity=df.get("severity", "CRITICAL"),
                risk_score=df.get("risk_score", 0.9),
                title=df.get("title", "Duplicate Document"),
                description=df.get("description", ""),
                technical_details=df.get("technical_details", {})
            ))

        # Overall composite fraud score
        overall_score = max(scores) if scores else 0.0
        overall_score = min(round(overall_score, 2), 1.0)

        if overall_score >= 0.7:
            verdict = ForensicVerdict.FRAUDULENT
        elif overall_score >= 0.4:
            verdict = ForensicVerdict.SUSPICIOUS
        else:
            verdict = ForensicVerdict.AUTHENTIC

        return DocumentForensicReport(
            document_id=document_id,
            file_name=file_name,
            sha256_hash=sha,
            phash=phash,
            overall_fraud_score=overall_score,
            verdict=verdict,
            findings=findings,
            metadata_summary=meta_summary,
            analysis_timestamp=datetime.utcnow().isoformat() + "Z"
        )
