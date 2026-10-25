import hashlib
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image

class PerceptualHashDeduplicator:
    """
    Perceptual Hashing (dHash) and Cryptographic SHA-256 Deduplication.
    Identifies exact and near-duplicate documents reused across different college applications.
    """
    def __init__(self):
        # In-memory registry for cross-institution deduplication index
        # key: doc_hash -> {doc_id, institution_id, institution_name, doc_type}
        self.sha256_index: Dict[str, Dict[str, Any]] = {}
        self.phash_index: List[Dict[str, Any]] = []

    def compute_sha256(self, file_bytes: bytes) -> str:
        return hashlib.sha256(file_bytes).hexdigest()

    def compute_dhash(self, pil_image: Image.Image, hash_size: int = 8) -> str:
        """
        Computes 64-bit difference hash (dHash).
        Robust against minor compression, brightness, or resolution adjustments.
        """
        gray = pil_image.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        pixels = list(gray.getdata())
        
        diff = []
        for row in range(hash_size):
            for col in range(hash_size):
                idx = row * (hash_size + 1) + col
                diff.append(pixels[idx] > pixels[idx + 1])
                
        # Convert boolean list to hex string
        decimal_val = 0
        hex_string = []
        for index, value in enumerate(diff):
            if value:
                decimal_val += 2 ** (index % 4)
            if (index % 4) == 3:
                hex_string.append(hex(decimal_val)[2:])
                decimal_val = 0
        return "".join(hex_string)

    def hamming_distance(self, h1: str, h2: str) -> int:
        """Computes bitwise Hamming distance between two hex hashes."""
        val1 = int(h1, 16)
        val2 = int(h2, 16)
        xor_val = val1 ^ val2
        return bin(xor_val).count("1")

    def register_and_check(
        self,
        doc_id: str,
        institution_id: str,
        institution_name: str,
        file_bytes: bytes,
        pil_image: Optional[Image.Image] = None
    ) -> Tuple[str, Optional[str], List[Dict[str, Any]]]:
        sha = self.compute_sha256(file_bytes)
        phash = self.compute_dhash(pil_image) if pil_image else None
        findings = []

        # 1. Exact Byte Duplicate Check
        if sha in self.sha256_index:
            existing = self.sha256_index[sha]
            if existing["institution_id"] != institution_id:
                findings.append({
                    "title": "Exact Cryptographic Duplicate Reused Across Institutions",
                    "severity": "CRITICAL",
                    "risk_score": 1.0,
                    "description": (
                        f"Exact identical document (SHA-256: {sha[:12]}...) was previously submitted by "
                        f"'{existing['institution_name']}' (ID: {existing['institution_id']}). "
                        f"Possible document recycling or cross-college fraud."
                    ),
                    "technical_details": existing
                })

        # 2. Perceptual Near-Duplicate Check
        if phash:
            for item in self.phash_index:
                if item["institution_id"] != institution_id:
                    dist = self.hamming_distance(phash, item["phash"])
                    # Distance <= 5 indicates near-identical visual layout / certificate template reuse
                    if dist <= 5:
                        findings.append({
                            "title": "Perceptual Near-Duplicate Document Detected",
                            "severity": "HIGH",
                            "risk_score": 0.85,
                            "description": (
                                f"Document visually mirrors a certificate submitted by '{item['institution_name']}' "
                                f"(Hamming distance: {dist}/64). Layout, borders, and structure are cloned."
                            ),
                            "technical_details": {
                                "matched_institution": item["institution_name"],
                                "matched_doc_id": item["doc_id"],
                                "hamming_distance": dist
                            }
                        })
                        break

        # Register document into index
        entry = {
            "doc_id": doc_id,
            "institution_id": institution_id,
            "institution_name": institution_name,
            "sha256": sha,
            "phash": phash
        }
        self.sha256_index[sha] = entry
        if phash:
            self.phash_index.append(entry)

        return sha, phash, findings
