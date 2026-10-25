from __future__ import annotations
from typing import Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field

class AuthorityStatus(str, Enum):
    VERIFIED = "VERIFIED"
    MISMATCH_DETECTED = "MISMATCH_DETECTED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"

class VerificationRecord(BaseModel):
    verification_id: str
    authority_name: str                # "DigiLocker NAD", "MCA21 Corporate / Trust Registry", "Bhulekh Land Records"
    document_ref: str
    target_identifier: str             # e.g., Khasra number, Trust Registration #, Faculty Degree Roll #
    status: AuthorityStatus
    claimed_data: Dict[str, Any]
    official_registry_data: Optional[Dict[str, Any]] = None
    mismatch_details: Optional[str] = None
    api_response_code: int = 200
    latency_ms: int = 120
    verified_at: str = ""
