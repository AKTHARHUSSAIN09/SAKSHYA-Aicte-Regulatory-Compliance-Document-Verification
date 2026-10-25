from __future__ import annotations
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field

class ForensicVerdict(str, Enum):
    AUTHENTIC = "AUTHENTIC"
    SUSPICIOUS = "SUSPICIOUS"
    FRAUDULENT = "FRAUDULENT"

class ForensicFinding(BaseModel):
    finding_id: str
    category: str                      # "METADATA_ANALYSIS", "ERROR_LEVEL_ANALYSIS", "DEDUPLICATION", "DIGITAL_SIGNATURE"
    severity: str                      # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    risk_score: float                  # 0.0 to 1.0
    title: str
    description: str
    technical_details: Dict[str, Any] = Field(default_factory=dict)
    visual_evidence_b64: Optional[str] = None  # Base64 encoded ELA heatmap crop or overlay

class DocumentForensicReport(BaseModel):
    document_id: str
    file_name: str
    sha256_hash: str
    phash: Optional[str] = None
    overall_fraud_score: float         # 0.0 to 1.0 (>= 0.7 = FRAUDULENT, >= 0.4 = SUSPICIOUS)
    verdict: ForensicVerdict
    findings: List[ForensicFinding] = Field(default_factory=list)
    metadata_summary: Dict[str, Any] = Field(default_factory=dict)
    analysis_timestamp: str = ""
