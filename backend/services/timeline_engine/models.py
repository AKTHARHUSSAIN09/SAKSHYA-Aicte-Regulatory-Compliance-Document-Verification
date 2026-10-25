from __future__ import annotations
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import date

class AllenRelation(str, Enum):
    BEFORE = "BEFORE"                  # A ends before B starts
    MEETS = "MEETS"                    # A ends exactly when B starts
    OVERLAPS = "OVERLAPS"              # A starts before B, ends during B
    DURING = "DURING"                  # A is strictly contained within B
    STARTS = "STARTS"                  # A starts with B, ends earlier
    FINISHES = "FINISHES"              # A starts later than B, ends with B
    EQUALS = "EQUALS"                  # Identical intervals
    
    # Inverses
    AFTER = "AFTER"                    # B before A
    MET_BY = "MET_BY"                  # B meets A
    OVERLAPPED_BY = "OVERLAPPED_BY"    # B overlaps A
    CONTAINS = "CONTAINS"              # B during A
    STARTED_BY = "STARTED_BY"          # B starts A
    FINISHED_BY = "FINISHED_BY"        # B finishes A

class TimelineEvent(BaseModel):
    event_id: str
    entity_name: str                   # e.g., "Land Purchase Deed", "Architect Inspection"
    category: str                      # "LAND_TITLE", "CONSTRUCTION", "STATUTORY_NOC", "FACULTY_APPOINTMENT", "ACADEMIC"
    start_date: str                    # YYYY-MM-DD
    end_date: Optional[str] = None     # YYYY-MM-DD (defaults to start_date for instantaneous events)
    document_ref: str                  # e.g., "Deed_Reg_789.pdf"
    page: int = 1
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TimelineAnomaly(BaseModel):
    anomaly_id: str
    severity: str                      # "CRITICAL_FRAUD_INDICATOR", "HIGH_RISK_INCONSISTENCY", "WARNING"
    event_a_id: str
    event_a_name: str
    event_a_date: str
    event_b_id: str
    event_b_name: str
    event_b_date: str
    observed_relation: AllenRelation
    expected_relation: str
    citation: str
    explanation: str
    inconsistency_trace: List[str]     # Step-by-step logical proof of impossibility

class DAGNode(BaseModel):
    id: str
    label: str
    date_str: str
    category: str
    status: str = "VALID"              # "VALID" or "FLAGGED"

class DAGEdge(BaseModel):
    source: str
    target: str
    relation: str
    is_anomaly: bool = False

class TimelineAuditReport(BaseModel):
    institution_id: str
    is_chronologically_valid: bool
    anomalies_count: int
    anomalies: List[TimelineAnomaly] = Field(default_factory=list)
    dag_nodes: List[DAGNode] = Field(default_factory=list)
    dag_edges: List[DAGEdge] = Field(default_factory=list)
