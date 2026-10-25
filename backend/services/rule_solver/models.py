from __future__ import annotations
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

class ComplianceStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    DEFICIENT = "DEFICIENT"
    MANUAL_SCRUTINY_REQUIRED = "MANUAL_SCRUTINY_REQUIRED"
    CONFLICT_FLAGGED = "CONFLICT_FLAGGED"

class RuleSource(BaseModel):
    document_name: str
    year: int
    clause_reference: str
    title: str
    effective_date: str
    authority: str = "AICTE"

class RuleDefinition(BaseModel):
    rule_id: str
    category: str  # e.g., "LAND_REQUIREMENT", "FACULTY_STUDENT_RATIO", "BUILT_UP_AREA", "CADRE_RATIO"
    description: str
    source: RuleSource
    is_active: bool = True
    parameters: Dict[str, Any]
    # SMT representation metadata
    variable_name: str
    operator: str  # ">=", "<=", "==", "in", "ratio"
    target_value: Any
    condition: Optional[Dict[str, Any]] = None  # e.g., {"location_type": "URBAN", "program": "ENGINEERING"}

class RuleConflict(BaseModel):
    conflict_id: str
    rule_a_id: str
    rule_b_id: str
    rule_a_clause: str
    rule_b_clause: str
    category: str
    conflict_type: str  # "CONTRADICTION", "SUBSET_AMBIGUITY", "UNSAT_OVERLAP"
    explanation: str
    counterexample_model: Optional[Dict[str, Any]] = None
    requires_admin_override: bool = True
    override_active: bool = False
    override_note: Optional[str] = None

class InstitutionalFacts(BaseModel):
    institution_id: str
    institution_name: str
    program: str = "ENGINEERING_TECHNOLOGY"
    level: str = "UG"  # "UG", "PG", "DIPLOMA"
    location_type: str = "URBAN"  # "MEGA_METRO", "METRO", "URBAN", "RURAL"
    approved_intake: int = 360
    total_enrolment: int = 1440
    
    # Land & Infrastructure
    land_area_acres: float
    built_up_area_sqm: float
    instructional_area_sqm: float
    administrative_area_sqm: float
    amenities_area_sqm: float
    computer_centers_count: int
    smart_classrooms_count: int
    
    # Faculty metrics
    total_faculty: int
    professors: int
    associate_professors: int
    assistant_professors: int
    faculty_with_phd: int
    
    # Financial & Regulatory
    corpus_fund_lakhs: float
    fire_safety_noc_valid: bool
    building_plan_approved: bool
    barrier_free_campus: bool
    
    # Provenance tracking (extracted keys map to document & bbox)
    provenance: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

class AuditItemResult(BaseModel):
    rule_id: str
    category: str
    clause_reference: str
    rule_title: str
    status: ComplianceStatus
    required_value: Any
    actual_value: Any
    shortfall: Optional[float] = None
    unit: str = ""
    citation: str
    explanation: str
    smt_verified: bool = True
    document_anchor: Optional[Dict[str, Any]] = None

class InstitutionalAuditReport(BaseModel):
    institution_id: str
    timestamp: str
    overall_status: ComplianceStatus
    rules_evaluated: int
    compliant_count: int
    deficient_count: int
    scrutiny_count: int
    conflicts_detected: List[RuleConflict] = Field(default_factory=list)
    results: List[AuditItemResult] = Field(default_factory=list)
