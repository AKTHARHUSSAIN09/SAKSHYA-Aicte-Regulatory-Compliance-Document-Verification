from __future__ import annotations
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field

class UserRole(str, Enum):
    COLLEGE_NODAL_OFFICER = "COLLEGE_NODAL_OFFICER"
    AICTE_SCRUTINY_OFFICER = "AICTE_SCRUTINY_OFFICER"
    AICTE_REGIONAL_DIRECTOR = "AICTE_REGIONAL_DIRECTOR"
    APPELLATE_COMMITTEE = "APPELLATE_COMMITTEE"

class AuditLogEntry(BaseModel):
    log_id: str
    timestamp: str
    actor_id: str
    actor_name: str
    role: UserRole
    action: str                        # "APPLICATION_SUBMITTED", "AUDIT_EXECUTED", "OVERRIDE_RECORDED", "DEFICIENCY_NOTICE_ISSUED", "RECTIFICATION_SUBMITTED"
    target_entity: str                 # e.g., "APPLICATION:AICTE-2024-FRAUD-002"
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: str = "127.0.0.1"

class DeficiencyNotice(BaseModel):
    notice_id: str
    application_id: str
    institution_name: str
    issued_by: str
    issued_at: str
    deadline_date: str
    deficiencies: List[str]
    rectification_instructions: str
    status: str = "PENDING_RECTIFICATION"  # "PENDING_RECTIFICATION", "RECTIFIED", "EXPIRED"
