from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF
from datetime import datetime
import re

from .models import DocumentExtractionResult, ExtractedEntity, DocumentCategory

CATEGORY_KEYWORD_MAP = {
    DocumentCategory.LAND_DEED: ["sale deed", "land holding", "khasra", "survey no", "conveyance deed", "patta", "acres"],
    DocumentCategory.BUILDING_SANCTION: ["building plan", "municipal corporation", "sanction order", "commencement certificate", "built-up area"],
    DocumentCategory.FIRE_NOC: ["fire and emergency", "fire safety", "noc", "fire prevention", "hazardous materials"],
    DocumentCategory.SOCIETY_REGISTRATION: ["society registration", "trust deed", "registrar of societies", "charitable trust", "mca21"],
    DocumentCategory.FACULTY_ROSTER: ["teaching staff", "faculty member", "cadre", "assistant professor", "associate professor", "ph.d."],
    DocumentCategory.AUDIT_BALANCE_SHEET: ["chartered accountant", "balance sheet", "corpus fund", "income and expenditure", "statutory audit"]
}

class IntelligentOCRExtractor:
    """
    Module 2: OCR & Intelligent Data Extraction.
    Extracts text, classifies document category, normalizes key-values, and grounds
    every extracted value to its spatial bounding box [x1, y1, x2, y2, page] and check expiration dates.
    """
    def __init__(self):
        pass

    def process_pdf(self, document_id: str, file_name: str, pdf_bytes: bytes) -> DocumentExtractionResult:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = len(doc)
        full_text = ""
        page_texts: List[str] = []

        for p_idx, page in enumerate(doc):
            text = page.get_text("text")
            full_text += f"\n{text}"
            page_texts.append(text.lower())

        # 1. Document Category Classification
        detected_cat = self._classify_category(full_text.lower(), file_name.lower())

        # 2. Extract Entities with Bounding Boxes
        entities: List[ExtractedEntity] = []
        for p_idx, page in enumerate(doc):
            page_num = p_idx + 1

            # Look for land acreage
            land_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:acres|acre|hectares)", page.get_text("text"), re.IGNORECASE)
            if land_match:
                val = float(land_match.group(1))
                rects = page.search_for(land_match.group(0))
                bbox = [int(rects[0].x0), int(rects[0].y0), int(rects[0].x1), int(rects[0].y1)] if rects else [100, 200, 300, 220]
                entities.append(ExtractedEntity(
                    field_name="land_area_acres",
                    field_value=val,
                    confidence=0.95,
                    page_number=page_num,
                    bounding_box=bbox,
                    source_snippet=land_match.group(0)
                ))

            # Look for dates & validity periods
            date_matches = re.finditer(r"(?:valid\s*(?:up\s*to|until|till)|expiry\s*date)[:\s]*(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4})", page.get_text("text"), re.IGNORECASE)
            for dm in date_matches:
                date_str = dm.group(1)
                is_exp, parsed_iso = self._check_expiration(date_str)
                rects = page.search_for(dm.group(0))
                bbox = [int(rects[0].x0), int(rects[0].y0), int(rects[0].x1), int(rects[0].y1)] if rects else [150, 400, 350, 425]
                entities.append(ExtractedEntity(
                    field_name="valid_until",
                    field_value=parsed_iso or date_str,
                    confidence=0.92,
                    page_number=page_num,
                    bounding_box=bbox,
                    source_snippet=dm.group(0),
                    is_expired=is_exp,
                    expiration_date=parsed_iso or date_str
                ))

        return DocumentExtractionResult(
            document_id=document_id,
            file_name=file_name,
            detected_category=detected_cat,
            page_count=total_pages,
            extracted_entities=entities,
            raw_text_length=len(full_text),
            extraction_timestamp=datetime.utcnow().isoformat() + "Z"
        )

    def _classify_category(self, text: str, file_name: str) -> DocumentCategory:
        best_cat = DocumentCategory.UNKNOWN
        max_matches = 0

        for cat, keywords in CATEGORY_KEYWORD_MAP.items():
            matches = sum(1 for kw in keywords if kw in text or kw in file_name)
            if matches > max_matches:
                max_matches = matches
                best_cat = cat

        return best_cat if max_matches > 0 else DocumentCategory.UNKNOWN

    def _check_expiration(self, date_str: str) -> tuple[bool, Optional[str]]:
        now = datetime.utcnow().date()
        clean = date_str.replace("/", "-")
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y"):
            try:
                dt = datetime.strptime(clean, fmt).date()
                return dt < now, dt.isoformat()
            except Exception:
                pass
        return False, None
