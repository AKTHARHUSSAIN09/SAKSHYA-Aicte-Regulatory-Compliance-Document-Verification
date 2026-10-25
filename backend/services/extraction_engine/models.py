from __future__ import annotations
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field

class DocumentCategory(str, Enum):
    LAND_DEED = "LAND_DEED"
    BUILDING_SANCTION = "BUILDING_SANCTION"
    FIRE_NOC = "FIRE_NOC"
    SOCIETY_REGISTRATION = "SOCIETY_REGISTRATION"
    FACULTY_ROSTER = "FACULTY_ROSTER"
    AUDIT_BALANCE_SHEET = "AUDIT_BALANCE_SHEET"
    UNKNOWN = "UNKNOWN"

class ExtractedEntity(BaseModel):
    field_name: str                    # e.g., "land_area_acres", "certificate_number", "valid_until"
    field_value: Any
    confidence: float                  # 0.0 to 1.0
    page_number: int
    bounding_box: List[int]            # [x1, y1, x2, y2]
    source_snippet: str
    is_expired: bool = False
    expiration_date: Optional[str] = None

class DocumentExtractionResult(BaseModel):
    document_id: str
    file_name: str
    detected_category: DocumentCategory
    page_count: int
    extracted_entities: List[ExtractedEntity] = Field(default_factory=list)
    raw_text_length: int = 0
    extraction_timestamp: str = ""
