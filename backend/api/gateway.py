from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from uuid import uuid4
from pydantic import BaseModel, Field
import io
import subprocess
import tempfile
from pathlib import Path
import json
from PIL import Image

from services.rule_solver import (
    STANDARD_APH_RULES,
    DeterministicComplianceEngine,
    Z3RuleConflictFinder,
    ComplianceStatus,
    InstitutionalFacts
)
from services.timeline_engine import TimelineImpossibilityEngine, TimelineEvent
from services.forensics_engine import DocumentForensicsEngine
from services.verification_gateway import IssuingAuthorityGateway
from services.report_generator.brief_builder import OfficerBriefBuilder
from services.report_generator.pdf_compiler import PDFOfficerBriefCompiler
from services.infrastructure_cv import InfrastructureGeoVerifier, BlueprintAnalyzer
from services.audit_trail import SecurityAuditLedger, UserRole
from services.extraction_engine import IntelligentOCRExtractor
from services.secure_storage import EncryptedDocumentVault
from services.document_intelligence import inspect_signature_and_qr, ocr_image, ffmpeg_available

from .sample_data import (
    APP_1_FACTS,
    APP_1_TIMELINE,
    APP_2_FACTS,
    APP_2_TIMELINE
)

app = FastAPI(
    title="Sakshya Regulatory Compliance & Fraud Detection API",
    description="Dual-Engine Decision Support System for AICTE Regulatory Approvals across 9 Core Modules",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/v1/auth/login")
def login(req: LoginRequest):
    """Local demonstration authentication. Replace with an approved SSO/identity provider in production."""
    accounts = {
        "officer@sakshya.gov.in": ("Sakshya@2026", "AICTE_SCRUTINY_OFFICER", "Scrutiny Officer"),
        "director@sakshya.gov.in": ("Sakshya@2026", "AICTE_REGIONAL_DIRECTOR", "Regional Director"),
        "nodal@sakshya.gov.in": ("Sakshya@2026", "COLLEGE_NODAL_OFFICER", "Institution Nodal Officer"),
    }
    account = accounts.get(req.email.lower())
    if not account or req.password != account[0]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": f"local-demo-{uuid4().hex}", "token_type": "bearer", "email": req.email.lower(), "role": account[1], "display_name": account[2]}

# Core Engines & Services
rule_engine = DeterministicComplianceEngine(STANDARD_APH_RULES)
timeline_engine = TimelineImpossibilityEngine()
forensics_engine = DocumentForensicsEngine()
authority_gateway = IssuingAuthorityGateway()
brief_builder = OfficerBriefBuilder()
pdf_compiler = PDFOfficerBriefCompiler()
geo_verifier = InfrastructureGeoVerifier()
blueprint_analyzer = BlueprintAnalyzer()
audit_ledger = SecurityAuditLedger()
extractor = IntelligentOCRExtractor()
document_vault = EncryptedDocumentVault()

CHECKLISTS = {
    "UG": [("LAND_DEED", "Land title deed", True), ("BUILDING_SANCTION", "Building-plan sanction", True), ("FIRE_NOC", "Fire-safety NOC", True), ("SOCIETY_REGISTRATION", "Society/trust registration", True), ("FACULTY_ROSTER", "Faculty roster", True), ("AUDIT_BALANCE_SHEET", "Audited balance sheet", False)],
    "PG": [("LAND_DEED", "Land title deed", True), ("BUILDING_SANCTION", "Building-plan sanction", True), ("FIRE_NOC", "Fire-safety NOC", True), ("FACULTY_ROSTER", "Faculty roster", True)],
    "DIPLOMA": [("LAND_DEED", "Land title deed", True), ("BUILDING_SANCTION", "Building-plan sanction", True), ("FIRE_NOC", "Fire-safety NOC", True)],
}
TIME_MACHINE_SNAPSHOTS: Dict[str, List[Dict[str, Any]]] = {}
PERSISTENCE_FILE = Path(__file__).resolve().parents[1] / "data" / "application_records.json"

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _checklist_for(level: str) -> List[Dict[str, Any]]:
    return [{"type": t, "name": n, "mandatory": m} for t, n, m in CHECKLISTS.get(level.upper(), CHECKLISTS["UG"])]

def _document_summary(document: Dict[str, Any]) -> Dict[str, Any]:
    """Never expose uploaded bytes in JSON responses."""
    return {key: value for key, value in document.items() if key != "content"}

APPLICATION_CATEGORY_CHECKLISTS = {
    "EOA": [("PREVIOUS_APPROVAL", "Previous approval / EoA letter", True), ("AFFIDAVIT", "Affidavit / undertaking", True), ("FACULTY_ROSTER", "Faculty roster", True)],
    "PROGRAMME_CHANGE": [("PREVIOUS_APPROVAL", "Previous approval / EoA letter", True), ("CURRICULUM", "Programme / course proposal", True), ("FACULTY_ROSTER", "Faculty capability record", True)],
    "INTAKE_CHANGE": [("PREVIOUS_APPROVAL", "Previous approval / EoA letter", True), ("FACULTY_ROSTER", "Faculty roster", True), ("INFRASTRUCTURE_EVIDENCE", "Infrastructure evidence", True)],
    "OTHER": [("AFFIDAVIT", "Affidavit / undertaking", True), ("SUPPORTING_EVIDENCE", "Category-specific supporting evidence", False)],
}

def _application_checklist(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    if data.get("source") != "USER_SUBMITTED":
        return _checklist_for(data["facts"].level)
    category = data.get("application_details", {}).get("category", "EOA")
    items = [*APPLICATION_CATEGORY_CHECKLISTS.get(category, APPLICATION_CATEGORY_CHECKLISTS["OTHER"]),
             *[(item["type"], item["name"], item["mandatory"]) for item in _checklist_for(data["facts"].level)]]
    seen = set()
    return [{"type": item[0], "name": item[1], "mandatory": item[2]} for item in items if not (item[0] in seen or seen.add(item[0]))]

def _persist_user_applications() -> None:
    PERSISTENCE_FILE.parent.mkdir(parents=True, exist_ok=True)
    records = {}
    for app_id, data in APPLICATIONS.items():
        if data.get("source") != "USER_SUBMITTED":
            continue
        records[app_id] = {
            "facts": data["facts"].model_dump(),
            "timeline": [event.model_dump() for event in data["timeline"]],
            "status": data["status"], "documents": [_document_summary(document) for document in data["documents"]],
            "profile": data.get("profile", {}), "application_details": data.get("application_details", {}),
            "audit_history": data.get("audit_history", []), "source": "USER_SUBMITTED",
        }
    PERSISTENCE_FILE.write_text(json.dumps(records, indent=2), encoding="utf-8")

def _restore_user_applications() -> None:
    if not PERSISTENCE_FILE.exists():
        return
    try:
        records = json.loads(PERSISTENCE_FILE.read_text(encoding="utf-8"))
        for app_id, data in records.items():
            APPLICATIONS[app_id] = {**data, "facts": InstitutionalFacts.model_validate(data["facts"]),
                "timeline": [TimelineEvent.model_validate(event) for event in data.get("timeline", [])]}
    except (ValueError, KeyError):
        # Keep the seeded demo workspace usable if a local demo persistence file is malformed.
        return

# In-memory application registry
APPLICATIONS = {
    APP_1_FACTS.institution_id: {
        "facts": APP_1_FACTS,
        "timeline": APP_1_TIMELINE,
        "status": "VERIFIED",
        "documents": [
            {"id": "DOC-101", "name": "Land_Title_Deed.pdf", "type": "LAND_DEED", "mandatory": True, "uploaded": True},
            {"id": "DOC-102", "name": "Building_Plan_Sanction.pdf", "type": "BUILDING_SANCTION", "mandatory": True, "uploaded": True},
            {"id": "DOC-103", "name": "Fire_Safety_NOC.pdf", "type": "FIRE_NOC", "mandatory": True, "uploaded": True},
            {"id": "DOC-104", "name": "Society_Reg_Certificate.pdf", "type": "SOCIETY_REGISTRATION", "mandatory": True, "uploaded": True},
            {"id": "DOC-105", "name": "Faculty_Roster_Qualifications.pdf", "type": "FACULTY_ROSTER", "mandatory": True, "uploaded": True}
        ]
    },
    APP_2_FACTS.institution_id: {
        "facts": APP_2_FACTS,
        "timeline": APP_2_TIMELINE,
        "status": "CRITICAL_DEFICIENCIES",
        "documents": [
            {"id": "DOC-201", "name": "Land_Deed_Khasra_991B.pdf", "type": "LAND_DEED", "mandatory": True, "uploaded": True},
            {"id": "DOC-202", "name": "Building_Approval_Scan.pdf", "type": "BUILDING_SANCTION", "mandatory": True, "uploaded": True},
            {"id": "DOC-203", "name": "Fire_NOC_2021.pdf", "type": "FIRE_NOC", "mandatory": True, "uploaded": True, "is_expired": True},
            {"id": "DOC-204", "name": "Barrier_Free_Facility_Cert.pdf", "type": "BARRIER_FREE_CERT", "mandatory": True, "uploaded": False} # Missing document!
        ]
    }
}

# Additional demonstration institutions.  These are deliberately varied so the
# officer workspace can exercise verified, manual-review, and critical paths.
def _demo_application(
    institution_id: str,
    institution_name: str,
    level: str,
    location_type: str,
    land_area_acres: float,
    built_up_area_sqm: float,
    total_faculty: int,
    status: str,
    fire_noc_valid: bool = True,
    barrier_free: bool = True,
):
    facts = InstitutionalFacts(
        institution_id=institution_id,
        institution_name=institution_name,
        level=level,
        location_type=location_type,
        land_area_acres=land_area_acres,
        built_up_area_sqm=built_up_area_sqm,
        instructional_area_sqm=built_up_area_sqm * 0.62,
        administrative_area_sqm=built_up_area_sqm * 0.18,
        amenities_area_sqm=built_up_area_sqm * 0.20,
        computer_centers_count=5,
        smart_classrooms_count=14,
        total_faculty=total_faculty,
        professors=max(4, total_faculty // 9),
        associate_professors=max(8, total_faculty // 4),
        assistant_professors=max(20, total_faculty - max(4, total_faculty // 9) - max(8, total_faculty // 4)),
        faculty_with_phd=max(12, total_faculty // 2),
        corpus_fund_lakhs=120.0,
        fire_safety_noc_valid=fire_noc_valid,
        building_plan_approved=True,
        barrier_free_campus=barrier_free,
    )
    prefix = institution_id.rsplit("-", 1)[-1]
    timeline = [
        TimelineEvent(event_id=f"EVT-{prefix}-1", entity_name="Society Registration", category="STATUTORY", start_date="2018-03-12", document_ref="Society_Registration.pdf", metadata={"event_type": "SOCIETY_REGISTRATION"}),
        TimelineEvent(event_id=f"EVT-{prefix}-2", entity_name="Land Title Registration", category="LAND_TITLE", start_date="2019-06-18", document_ref="Land_Title_Deed.pdf", metadata={"event_type": "LAND_PURCHASE_DEED"}),
        TimelineEvent(event_id=f"EVT-{prefix}-3", entity_name="Building Plan Approval", category="CONSTRUCTION", start_date="2020-02-04", document_ref="Building_Plan.pdf", metadata={"event_type": "BUILDING_PLAN_APPROVAL"}),
        TimelineEvent(event_id=f"EVT-{prefix}-4", entity_name="Fire Safety NOC", category="STATUTORY_NOC", start_date="2024-01-15", end_date="2027-01-14", document_ref="Fire_Safety_NOC.pdf", metadata={"event_type": "FIRE_SAFETY_NOC"}),
        TimelineEvent(event_id=f"EVT-{prefix}-5", entity_name="Application Submission", category="STATUTORY", start_date="2024-05-20", document_ref="AICTE_Application.pdf", metadata={"event_type": "APPLICATION_SUBMISSION"}),
    ]
    documents = [
        {"id": f"DOC-{prefix}-1", "name": "Land_Title_Deed.pdf", "type": "LAND_DEED", "mandatory": True, "uploaded": True},
        {"id": f"DOC-{prefix}-2", "name": "Building_Plan.pdf", "type": "BUILDING_SANCTION", "mandatory": True, "uploaded": True},
        {"id": f"DOC-{prefix}-3", "name": "Fire_Safety_NOC.pdf", "type": "FIRE_NOC", "mandatory": True, "uploaded": fire_noc_valid, "is_expired": not fire_noc_valid},
        {"id": f"DOC-{prefix}-4", "name": "Faculty_Roster.pdf", "type": "FACULTY_ROSTER", "mandatory": True, "uploaded": status != "MANUAL_REVIEW_REQUIRED"},
    ]
    return {"facts": facts, "timeline": timeline, "status": status, "documents": documents}


for demo in [
    ("AICTE-2024-PG-003", "Raman Institute of Advanced Studies", "PG", "METRO", 3.20, 14600.0, 94, "VERIFIED", True, True),
    ("AICTE-2024-DIP-004", "Sardar Patel Polytechnic", "DIPLOMA", "URBAN", 2.55, 8600.0, 58, "MANUAL_REVIEW_REQUIRED", True, True),
    ("AICTE-2024-FRAUD-005", "Eastern Valley College of Engineering", "UG", "URBAN", 1.85, 9100.0, 49, "CRITICAL_DEFICIENCIES", False, False),
    ("AICTE-2024-UG-006", "Meghnad Saha College of Technology", "UG", "RURAL", 4.10, 15100.0, 88, "VERIFIED", True, True),
    ("AICTE-2024-PG-007", "Kaveri School of Computing", "PG", "MEGA_METRO", 2.35, 11200.0, 67, "MANUAL_REVIEW_REQUIRED", True, True),
    ("AICTE-2024-FRAUD-008", "Deccan Institute of Applied Sciences", "UG", "URBAN", 2.05, 9800.0, 54, "CRITICAL_DEFICIENCIES", False, True),
    ("AICTE-2024-DIP-009", "Nalanda Technical Academy", "DIPLOMA", "RURAL", 3.75, 10400.0, 72, "VERIFIED", True, True),
    ("AICTE-2024-UG-010", "Vikram Institute of Engineering", "UG", "METRO", 2.62, 11800.0, 69, "MANUAL_REVIEW_REQUIRED", True, True),
    ("AICTE-2024-PG-011", "C. V. Raman School of Innovation", "PG", "URBAN", 3.05, 13700.0, 86, "VERIFIED", True, True),
    ("AICTE-2024-DIP-012", "Bharat Institute of Polytechnic Studies", "DIPLOMA", "METRO", 2.40, 8300.0, 55, "MANUAL_REVIEW_REQUIRED", True, True),
    ("AICTE-2024-FRAUD-013", "Horizon College of Technical Sciences", "UG", "MEGA_METRO", 1.70, 8900.0, 46, "CRITICAL_DEFICIENCIES", False, False),
    ("AICTE-2024-UG-014", "Kalam Institute of Engineering", "UG", "RURAL", 4.35, 15800.0, 96, "VERIFIED", True, True),
    ("AICTE-2024-PG-015", "Aryabhata Centre for Digital Engineering", "PG", "URBAN", 2.48, 10900.0, 64, "MANUAL_REVIEW_REQUIRED", True, True),
    ("AICTE-2025-DEMO-016", "Satyendra Nath Bose Institute of Engineering", "UG", "URBAN", 3.15, 13600.0, 82, "VERIFIED", True, True),
]:
    APPLICATIONS[demo[0]] = _demo_application(*demo)

APPLICATIONS["AICTE-2025-DEMO-016"].update({
    "profile": {"permanent_id": "AICTE-2025-DEMO-016", "location": "Mysuru, Karnataka", "institution_type": "PRIVATE"},
    "application_details": {"category": "EOA", "reference_number": "AICTE/EOA/2024-25/DEMO-016", "academic_year": "2024-25",
                            "programmes": ["Computer Science Engineering", "Electronics & Communication Engineering"], "approved_intake": 300, "proposed_intake": 300,
                            "previous_approval_reference": "AICTE/EOA/2023-24/DEMO-016"},
    "source": "SEEDED_DEMONSTRATION",
})

_restore_user_applications()

# Request/Response Schemas
class OverrideRequest(BaseModel):
    conflict_id: str
    winning_rule_id: str
    admin_officer_id: str
    justification_note: str

class NoticeRequest(BaseModel):
    application_id: str
    institution_name: str
    officer_id: str
    deficiencies: List[str]
    instructions: str
    deadline_date: str

class GeoVerifyRequest(BaseModel):
    target_latitude: float
    target_longitude: float

# -------------------------------------------------------------
# Module 1: Application Management & Document Upload Checklists
# -------------------------------------------------------------
@app.get("/api/v1/applications")
def list_applications():
    res = []
    for app_id, data in APPLICATIONS.items():
        f = data["facts"]
        docs = data["documents"]
        uploaded_types = {document["type"] for document in docs if document.get("uploaded", False)}
        missing = [item["name"] for item in _application_checklist(data) if item["mandatory"] and item["type"] not in uploaded_types]
        res.append({
            "institution_id": f.institution_id,
            "institution_name": f.institution_name,
            "program": f.program,
            "location_type": f.location_type,
            "enrolment": f.total_enrolment,
            "land_acres": f.land_area_acres,
            "faculty_count": f.total_faculty,
            "total_documents": len(docs),
            "missing_mandatory_documents": missing,
            "case_status": data["status"],
            "application_category": data.get("application_details", {}).get("category", "EOA"),
            "application_reference_number": data.get("application_details", {}).get("reference_number", app_id),
            "permanent_id": data.get("profile", {}).get("permanent_id", f.institution_id),
            "audit_status": data.get("audit_history", [])[-1].get("status") if data.get("audit_history") else "NOT_RUN",
            "last_audit_at": data.get("audit_history", [])[-1].get("timestamp") if data.get("audit_history") else None,
            "source": data.get("source", "SEEDED_DEMONSTRATION")
        })
    return res

@app.get("/api/v1/applications/{app_id}")
def get_application_details(app_id: str):
    if app_id not in APPLICATIONS:
        raise HTTPException(status_code=404, detail="Application ID not found")
    data = APPLICATIONS[app_id]
    return {
        "facts": data["facts"].model_dump(),
        "timeline_events": [e.model_dump() for e in data["timeline"]],
        "checklist": _application_checklist(data),
        "documents": [_document_summary(d) for d in data["documents"]],
        "profile": data.get("profile", {}), "application_details": data.get("application_details", {}),
        "audit_history": data.get("audit_history", []), "status": data["status"], "source": data.get("source", "SEEDED_DEMONSTRATION")
    }

@app.get("/api/v1/applications/{app_id}/checklist")
def get_application_checklist(app_id: str):
    if app_id not in APPLICATIONS:
        raise HTTPException(status_code=404, detail="Application ID not found")
    data = APPLICATIONS[app_id]
    uploaded_types = {d["type"] for d in data["documents"] if d.get("uploaded")}
    return [{**item, "uploaded": item["type"] in uploaded_types,
             "status": "COMPLETE" if item["type"] in uploaded_types else ("MISSING" if item["mandatory"] else "OPTIONAL")}
            for item in _application_checklist(data)]

@app.post("/api/v1/applications/{app_id}/documents")
async def upload_application_document(app_id: str, file: UploadFile = File(...), document_type: str = Form("UNKNOWN"), mandatory: bool = Form(False)):
    """Accept a PDF/image, retain only in the local demo vault, and run extraction and forensics."""
    if app_id not in APPLICATIONS:
        raise HTTPException(status_code=404, detail="Application ID not found")
    allowed = {"application/pdf", "image/png", "image/jpeg", "image/tiff"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=415, detail="Only PDF, PNG, JPEG, and TIFF documents are accepted")
    content = await file.read()
    if not content or len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Document must be between 1 byte and 20 MB")
    document_id = f"DOC-{uuid4().hex[:12].upper()}"
    if file.content_type == "application/pdf" or file.filename.lower().endswith(".pdf"):
        try:
            extraction = extractor.process_pdf(document_id, file.filename, content).model_dump()
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"Unreadable PDF: {exc}")
    else:
        scan = ocr_image(content)
        extraction = {"document_id": document_id, "file_name": file.filename, "detected_category": "UNKNOWN", "page_count": 1,
                      "extracted_entities": [], "raw_text_length": scan.get("raw_text_length", 0), "raw_text": scan.get("text", ""),
                      "extraction_timestamp": _now(), "manual_ocr_required": scan["status"] != "EXTRACTED", "ocr_status": scan["status"], "ocr_reason": scan.get("reason")}
    forensic = forensics_engine.analyze_document(document_id, file.filename, content, app_id, APPLICATIONS[app_id]["facts"].institution_name).model_dump()
    integrity = inspect_signature_and_qr(file.filename, content)
    storage = document_vault.store(document_id, content)
    doc = {"id": document_id, "name": file.filename, "type": document_type if document_type != "UNKNOWN" else extraction.get("detected_category", "UNKNOWN"),
           "mandatory": mandatory, "uploaded": True, "content_type": file.content_type, "size_bytes": len(content), "uploaded_at": _now(),
           "extraction": extraction, "forensics": forensic, "integrity": integrity, "storage": storage}
    APPLICATIONS[app_id]["documents"].append(doc)
    if APPLICATIONS[app_id].get("source") == "USER_SUBMITTED":
        _persist_user_applications()
    audit_ledger.record_action("INSTITUTION-PORTAL", "Institution Nodal Officer", UserRole.COLLEGE_NODAL_OFFICER,
        "DOCUMENT_UPLOADED", f"APPLICATION:{app_id}", {"document_id": document_id, "document_type": doc["type"]})
    return _document_summary(doc)

@app.get("/api/v1/applications/{app_id}/documents/{document_id}/extraction")
def get_document_extraction(app_id: str, document_id: str):
    if app_id not in APPLICATIONS:
        raise HTTPException(status_code=404, detail="Application ID not found")
    document = next((d for d in APPLICATIONS[app_id]["documents"] if d["id"] == document_id), None)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"document_id": document_id, "extraction": document.get("extraction"), "forensics": document.get("forensics")}

# -------------------------------------------------------------
# Module 6: Regulatory Compliance Engine & Z3 Conflict Matrix
# -------------------------------------------------------------
@app.get("/api/v1/rules")
def get_rules():
    return [
        {
            "rule_id": r.rule_id,
            "category": r.category,
            "description": r.description,
            "source": r.source.model_dump(),
            "variable_name": r.variable_name,
            "operator": r.operator,
            "target_value": r.target_value,
            "condition": r.condition
        }
        for r in rule_engine.rules
    ]

@app.get("/api/v1/rules/conflicts")
def get_rule_conflicts():
    conflicts = rule_engine.active_conflicts
    return [c.model_dump() for c in conflicts]

@app.post("/api/v1/rules/override")
def register_override(req: OverrideRequest):
    rule_engine.register_override(
        conflict_id=req.conflict_id,
        winning_rule_id=req.winning_rule_id,
        note=f"{req.justification_note} (Approved by Officer: {req.admin_officer_id})"
    )
    audit_ledger.record_action(
        actor_id=req.admin_officer_id,
        actor_name="AICTE Senior Administrator",
        role=UserRole.AICTE_REGIONAL_DIRECTOR,
        action="RULE_OVERRIDE_RECORDED",
        target_entity=f"CONFLICT:{req.conflict_id}",
        details={"winning_rule": req.winning_rule_id, "note": req.justification_note}
    )
    return {
        "status": "OVERRIDE_RECORDED",
        "conflict_id": req.conflict_id,
        "active_rule": req.winning_rule_id
    }

# -------------------------------------------------------------
# Module 8 & 3: Audit Execution & Explainable Officer Brief
# -------------------------------------------------------------
@app.post("/api/v1/audit/run/{app_id}")
def run_full_audit(app_id: str):
    if app_id not in APPLICATIONS:
        raise HTTPException(status_code=404, detail="Application ID not found")

    app_data = APPLICATIONS[app_id]
    facts = app_data["facts"]
    events = app_data["timeline"]

    # 1. Deterministic Rule Audit
    audit_report = rule_engine.audit_institution(facts)

    # 2. Timeline Impossibility Engine
    timeline_report = timeline_engine.audit_timeline(facts.institution_id, events)

    # 3. Issuing Authority Verification
    authority_records = []
    if app_id == APP_1_FACTS.institution_id:
        authority_records.append(authority_gateway.verify_land_record("KHASRA-402/1", facts.land_area_acres, facts.institution_name))
        authority_records.append(authority_gateway.verify_faculty_degree("DEG-IITB-2014-998", "Dr. Rajesh Kumar", "Ph.D."))
    else:
        authority_records.append(authority_gateway.verify_land_record("KHASRA-991/B", facts.land_area_acres, facts.institution_name))
        authority_records.append(authority_gateway.verify_faculty_degree("DEG-UNKNOWN-99", "Dr. K. Mehta", "Ph.D."))

    # 4. Forensics
    forensic_reports = []
    if app_id == APP_2_FACTS.institution_id:
        from services.forensics_engine.models import DocumentForensicReport, ForensicFinding, ForensicVerdict
        forensic_reports.append(DocumentForensicReport(
            document_id="DOC-DEED-991B",
            file_name="Land_Title_Deed_Khasra_991B.pdf",
            sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            overall_fraud_score=0.92,
            verdict=ForensicVerdict.FRAUDULENT,
            findings=[
                ForensicFinding(
                    finding_id="FIND-1",
                    category="METADATA_ANALYSIS",
                    severity="CRITICAL",
                    risk_score=0.88,
                    title="Design Software Footprint (Canva v2.4.1)",
                    description="PDF stream contains Producer 'Canva' and Creator 'Canva PDF Generator'. Official land deeds are never created in graphic design suites."
                ),
                ForensicFinding(
                    finding_id="FIND-2",
                    category="ERROR_LEVEL_ANALYSIS",
                    severity="CRITICAL",
                    risk_score=0.94,
                    title="Localized Pixel Splicing at Land Area Coordinate [105, 310]",
                    description="ELA variance of 48.6 (mean 4.2) indicates digital splicing where '1.75' was altered to '2.10' acres."
                )
            ],
            metadata_summary={"creator": "Canva", "producer": "Canva PDF Engine", "is_tampered": True}
        ))

    # 5. Build Officer Brief
    brief = brief_builder.build_brief(
        institution_name=facts.institution_name,
        application_id=facts.institution_id,
        audit_report=audit_report,
        timeline_report=timeline_report,
        forensic_reports=forensic_reports,
        authority_records=authority_records
    )

    audit_ledger.record_action(
        actor_id="AICTE-SYSTEM",
        actor_name="Sakshya Automated Audit Service",
        role=UserRole.AICTE_SCRUTINY_OFFICER,
        action="FULL_APPLICATION_AUDIT_EXECUTED",
        target_entity=f"APPLICATION:{app_id}",
        details={"verdict": brief["executive_verdict"], "deficient_count": audit_report.deficient_count}
    )

    if brief["executive_verdict"] == "RECOMMENDED_FOR_APPROVAL":
        app_data["status"] = "VERIFIED_CHECKS_PASSED"
    elif brief["executive_verdict"] == "DEFICIENT_REQUIRES_RECTIFICATION":
        app_data["status"] = "DEFICIENCIES_FOUND"
    else:
        app_data["status"] = "MANUAL_REVIEW_REQUIRED"
    app_data.setdefault("audit_history", []).append({"timestamp": _now(), "status": app_data["status"],
        "verdict": brief["executive_verdict"], "brief_id": brief["brief_id"]})
    if app_data.get("source") == "USER_SUBMITTED":
        _persist_user_applications()

    return {
        "brief": brief,
        "audit_report": audit_report.model_dump(),
        "timeline_report": timeline_report.model_dump(),
        "authority_records": [r.model_dump() for r in authority_records],
        "forensic_reports": [f.model_dump() for f in forensic_reports]
    }

@app.get("/api/v1/officer-brief/pdf/{app_id}")
def download_officer_brief_pdf(app_id: str):
    """Generates and streams a pixel-perfect, court-admissible PDF audit brief."""
    if app_id not in APPLICATIONS:
        raise HTTPException(status_code=404, detail="Application ID not found")
    
    # Run audit to get fresh brief
    audit_res = run_full_audit(app_id)
    brief = audit_res["brief"]
    pdf_bytes = pdf_compiler.compile_pdf_bytes(brief)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=AICTE_Officer_Brief_{app_id}.pdf"
        }
    )

class CreateAppRequest(BaseModel):
    institution_id: str
    institution_name: str
    application_reference_number: Optional[str] = None
    application_category: str = "EOA"
    academic_year: str = "2025-26"
    institution_location: str = ""
    institution_type: str = "PRIVATE"
    existing_institution_record: Optional[str] = None
    previous_approval_reference: Optional[str] = None
    relevant_programmes: List[str] = Field(default_factory=list)
    proposed_intake: Optional[int] = None
    use_existing_institution: bool = False
    program: str = "ENGINEERING_TECHNOLOGY"
    level: str = "UG"
    location_type: str = "URBAN"
    approved_intake: int = 360
    total_enrolment: int = 1440
    land_area_acres: float = 2.6
    built_up_area_sqm: float = 12000.0
    total_faculty: int = 75
    professors: int = 9
    associate_professors: int = 18
    assistant_professors: int = 48
    fire_safety_noc_valid: bool = True
    building_plan_approved: bool = True
    barrier_free_campus: bool = True

@app.post("/api/v1/applications/create")
def create_institutional_application(req: CreateAppRequest):
    """Creates a persistent DRAFT. Documents and audit run only after explicit confirmation."""
    application_id = (req.application_reference_number or req.institution_id).strip().upper()
    if application_id in APPLICATIONS:
        raise HTTPException(status_code=409, detail="Application reference already exists. Select the existing record or use a new application reference.")
    new_facts = InstitutionalFacts(
        institution_id=application_id,
        institution_name=req.institution_name,
        program=req.program,
        level=req.level,
        location_type=req.location_type,
        approved_intake=req.approved_intake,
        total_enrolment=req.total_enrolment,
        land_area_acres=req.land_area_acres,
        built_up_area_sqm=req.built_up_area_sqm,
        instructional_area_sqm=req.built_up_area_sqm * 0.6,
        administrative_area_sqm=req.built_up_area_sqm * 0.2,
        amenities_area_sqm=req.built_up_area_sqm * 0.2,
        computer_centers_count=5,
        smart_classrooms_count=15,
        total_faculty=req.total_faculty,
        professors=req.professors,
        associate_professors=req.associate_professors,
        assistant_professors=req.assistant_professors,
        faculty_with_phd=int(req.total_faculty * 0.4),
        corpus_fund_lakhs=100.0,
        fire_safety_noc_valid=req.fire_safety_noc_valid,
        building_plan_approved=req.building_plan_approved,
        barrier_free_campus=req.barrier_free_campus
    )
    
    # Generate sequential timeline
    new_timeline = [
        TimelineEvent(
            event_id=f"EVT-{application_id}-1",
            entity_name="Application Draft Created",
            category="STATUTORY",
            start_date=datetime.now(timezone.utc).date().isoformat(),
            document_ref="Portal_Draft",
            metadata={"event_type": "APPLICATION_DRAFT"}
        )
    ]
    APPLICATIONS[application_id] = {
        "facts": new_facts, "timeline": new_timeline, "status": "DRAFT", "documents": [], "source": "USER_SUBMITTED",
        "profile": {"permanent_id": req.institution_id, "location": req.institution_location, "institution_type": req.institution_type,
                    "existing_record": req.existing_institution_record, "use_existing_institution": req.use_existing_institution},
        "application_details": {"category": req.application_category, "reference_number": application_id, "academic_year": req.academic_year,
                    "programmes": req.relevant_programmes, "approved_intake": req.approved_intake, "proposed_intake": req.proposed_intake,
                    "previous_approval_reference": req.previous_approval_reference}, "audit_history": [],
    }
    _persist_user_applications()
    audit_ledger.record_action("INSTITUTION-PORTAL", "Institution Nodal Officer", UserRole.COLLEGE_NODAL_OFFICER,
        "APPLICATION_DRAFT_CREATED", f"APPLICATION:{application_id}", {"category": req.application_category, "academic_year": req.academic_year})
    return {"status": "DRAFT_CREATED", "application_id": application_id, "institution_id": req.institution_id, "checklist": _application_checklist(APPLICATIONS[application_id])}

@app.get("/api/v1/applications/{app_id}/submission-summary")
def application_submission_summary(app_id: str):
    if app_id not in APPLICATIONS:
        raise HTTPException(status_code=404, detail="Application ID not found")
    data = APPLICATIONS[app_id]
    checklist = get_application_checklist(app_id)
    missing = [item for item in checklist if item["mandatory"] and not item["uploaded"]]
    profile = data.get("profile", {})
    details = data.get("application_details", {})
    incomplete_fields = [label for label, value in {
        "Institution location": profile.get("location"), "Institution type": profile.get("institution_type"),
        "Application category": details.get("category"), "Academic year": details.get("academic_year")
    }.items() if not value]
    warnings = []
    hashes = {}
    for document in data["documents"]:
        digest = (document.get("storage") or {}).get("sha256")
        if digest:
            hashes.setdefault(digest, []).append(document["name"])
    for names in hashes.values():
        if len(names) > 1:
            warnings.append({"type": "DUPLICATE_DOCUMENT", "message": f"Potential duplicate upload: {', '.join(names)}"})
    return {"application_id": app_id, "status": data["status"], "profile": profile, "application_details": details,
            "documents": [_document_summary(document) for document in data["documents"]], "checklist": checklist,
            "missing_mandatory_documents": missing, "incomplete_fields": incomplete_fields, "warnings": warnings,
            "ready_to_confirm": not missing and not incomplete_fields}

@app.post("/api/v1/applications/{app_id}/confirm-and-audit")
def confirm_and_audit_application(app_id: str):
    summary = application_submission_summary(app_id)
    if not summary["ready_to_confirm"]:
        APPLICATIONS[app_id]["status"] = "AWAITING_DOCUMENTS"
        _persist_user_applications()
        raise HTTPException(status_code=409, detail={"message": "Application is incomplete. Upload required documents before audit.", "summary": summary})
    APPLICATIONS[app_id]["status"] = "PROCESSING"
    _persist_user_applications()
    return run_full_audit(app_id)


# -------------------------------------------------------------
# Modules 2, 3, 5 & 9: Evidence validation and human review
# -------------------------------------------------------------
@app.post("/api/v1/applications/{app_id}/validate")
def validate_application_evidence(app_id: str):
    if app_id not in APPLICATIONS:
        raise HTTPException(status_code=404, detail="Application ID not found")
    data, facts = APPLICATIONS[app_id], APPLICATIONS[app_id]["facts"]
    checklist = get_application_checklist(app_id)
    discrepancies: List[Dict[str, Any]] = []
    for item in checklist:
        if item["mandatory"] and not item["uploaded"]:
            discrepancies.append({"severity": "HIGH", "type": "MISSING_DOCUMENT", "document_type": item["type"], "message": f"Required {item['name']} is missing."})
    for doc in data["documents"]:
        extraction = doc.get("extraction") or {}
        for entity in extraction.get("extracted_entities", []):
            if entity.get("is_expired"):
                discrepancies.append({"severity": "HIGH", "type": "EXPIRED_DOCUMENT", "document_id": doc["id"], "page": entity.get("page_number"), "message": f"{doc['name']} expired on {entity.get('expiration_date')}."})
            if entity.get("field_name") == "land_area_acres" and abs(float(entity["field_value"]) - facts.land_area_acres) > 0.05:
                discrepancies.append({"severity": "HIGH", "type": "CROSS_DOCUMENT_MISMATCH", "document_id": doc["id"], "page": entity.get("page_number"), "message": f"Document states {entity['field_value']} acres; application states {facts.land_area_acres} acres.", "source_snippet": entity.get("source_snippet")})
        forensic = doc.get("forensics") or {}
        if forensic.get("verdict") in {"SUSPICIOUS", "FRAUDULENT"}:
            discrepancies.append({"severity": "CRITICAL", "type": "FORENSIC_ALERT", "document_id": doc["id"], "message": f"{doc['name']} requires manual review: {forensic.get('verdict')}."})
    status = "MANUAL_REVIEW_REQUIRED" if discrepancies else "VALIDATED"
    data["status"] = status
    audit_ledger.record_action("AICTE-SYSTEM", "Sakshya Evidence Validator", UserRole.AICTE_SCRUTINY_OFFICER,
        "CROSS_DOCUMENT_VALIDATION_EXECUTED", f"APPLICATION:{app_id}", {"discrepancy_count": len(discrepancies), "status": status})
    return {"application_id": app_id, "status": status, "checklist": checklist, "discrepancies": discrepancies,
            "evidence_count": sum(1 for d in data["documents"] if d.get("uploaded")), "generated_at": _now()}

class LandVerificationRequest(BaseModel):
    survey_number: str
    claimed_acres: float
    society_name: str

@app.post("/api/v1/authorities/verify-land")
def verify_land_authority(req: LandVerificationRequest):
    """Uses configured demonstration registry data; unavailable responses require officer review."""
    return authority_gateway.verify_land_record(req.survey_number, req.claimed_acres, req.society_name).model_dump()

class ManualReviewRequest(BaseModel):
    application_id: str
    officer_id: str
    role: UserRole
    comment: str
    override_reason: Optional[str] = None

@app.post("/api/v1/reviews/manual")
def record_manual_review(req: ManualReviewRequest):
    if req.application_id not in APPLICATIONS:
        raise HTTPException(status_code=404, detail="Application ID not found")
    if req.role not in {UserRole.AICTE_SCRUTINY_OFFICER, UserRole.AICTE_REGIONAL_DIRECTOR}:
        raise HTTPException(status_code=403, detail="Only authorized AICTE officers may record a review")
    action = "MANUAL_OVERRIDE_RECORDED" if req.override_reason else "MANUAL_REVIEW_RECORDED"
    return audit_ledger.record_action(req.officer_id, "AICTE Authorized Officer", req.role, action,
        f"APPLICATION:{req.application_id}", {"comment": req.comment, "override_reason": req.override_reason}).model_dump()

# -------------------------------------------------------------
# Advanced regulatory analysis modules
# -------------------------------------------------------------
@app.get("/api/v1/evidence-graph/{app_id}")
def get_regulatory_evidence_graph(app_id: str):
    """Build a traceable graph from the application, its evidence, rules and detected anomalies."""
    if app_id not in APPLICATIONS:
        raise HTTPException(status_code=404, detail="Application ID not found")
    data, facts = APPLICATIONS[app_id], APPLICATIONS[app_id]["facts"]
    nodes = [{"id": f"APP:{app_id}", "type": "APPLICATION", "label": facts.institution_name, "flagged": False}]
    edges: List[Dict[str, Any]] = []
    for doc in data["documents"]:
        doc_id = f"DOC:{doc['id']}"
        flagged = bool((doc.get("forensics") or {}).get("overall_fraud_score", 0) >= 0.4) or doc.get("is_expired", False)
        nodes.append({"id": doc_id, "type": "DOCUMENT", "label": doc["name"], "flagged": flagged})
        edges.append({"from": f"APP:{app_id}", "to": doc_id, "relation": "SUBMITTED_AS_EVIDENCE", "anomaly": flagged})
        for entity in (doc.get("extraction") or {}).get("extracted_entities", []):
            entity_id = f"ENTITY:{doc['id']}:{entity['field_name']}"
            nodes.append({"id": entity_id, "type": "EXTRACTED_FIELD", "label": f"{entity['field_name']}: {entity['field_value']}", "flagged": entity.get("is_expired", False)})
            edges.append({"from": doc_id, "to": entity_id, "relation": f"EXTRACTED_ON_PAGE_{entity.get('page_number', 1)}", "anomaly": entity.get("is_expired", False)})
    for rule in rule_engine.rules:
        rule_id = f"RULE:{rule.rule_id}"
        nodes.append({"id": rule_id, "type": "REGULATION", "label": f"{rule.rule_id} · {rule.source.clause_reference}", "flagged": False})
        edges.append({"from": f"APP:{app_id}", "to": rule_id, "relation": "EVALUATED_AGAINST", "anomaly": False})
    return {"application_id": app_id, "nodes": nodes, "edges": edges, "generated_at": _now()}

@app.get("/api/v1/timelines/{app_id}")
def evaluate_timeline(app_id: str):
    if app_id not in APPLICATIONS:
        raise HTTPException(status_code=404, detail="Application ID not found")
    data = APPLICATIONS[app_id]
    report = timeline_engine.audit_timeline(app_id, data["timeline"])
    return {"events": [event.model_dump() for event in data["timeline"]], "report": report.model_dump()}

class AttackLabRequest(BaseModel):
    scenario: str

@app.post("/api/v1/attack-lab/run")
def run_attack_lab(req: AttackLabRequest):
    """Returns safe synthetic benchmark observations; it never creates a document intended to deceive."""
    scenarios = {
        "FONT_SPLICING": ("ERROR_LEVEL_ANALYSIS", 0.94, "Localized compression boundary detected around a simulated numeric alteration."),
        "CANVA_METADATA": ("METADATA_ANALYSIS", 0.88, "Synthetic graphic-suite producer marker detected in document metadata."),
        "EXIF_GPS_FORGERY": ("GEO_VERIFICATION", 0.85, "Synthetic photo coordinates are outside the registered campus perimeter."),
        "TEMPLATE_CLONING": ("PERCEPTUAL_HASH", 0.91, "Synthetic certificate image matches a previously registered template."),
    }
    if req.scenario not in scenarios:
        raise HTTPException(status_code=422, detail="Unknown benchmark scenario")
    detector, score, explanation = scenarios[req.scenario]
    return {"scenario": req.scenario, "synthetic": True, "detector": detector, "fraud_score": score,
            "detection_status": "CAUGHT_BY_DETECTOR", "explanation": explanation, "executed_at": _now()}

class TimeMachineRequest(BaseModel):
    corrections: Dict[str, Any] = {}
    label: str = "What-if correction"

@app.post("/api/v1/applications/{app_id}/time-machine")
def run_regulatory_time_machine(app_id: str, req: TimeMachineRequest):
    """Compare the recorded assessment with a non-persistent, auditable correction scenario."""
    if app_id not in APPLICATIONS:
        raise HTTPException(status_code=404, detail="Application ID not found")
    original = APPLICATIONS[app_id]["facts"]
    allowed = set(InstitutionalFacts.model_fields)
    rejected = sorted(set(req.corrections) - allowed)
    if rejected:
        raise HTTPException(status_code=422, detail=f"Unsupported correction fields: {', '.join(rejected)}")
    projected = InstitutionalFacts.model_validate({**original.model_dump(), **req.corrections})
    baseline = rule_engine.audit_institution(original)
    projected_report = rule_engine.audit_institution(projected)
    snapshot = {"snapshot_id": f"SNAP-{uuid4().hex[:10].upper()}", "label": req.label, "application_id": app_id,
                "corrections": req.corrections, "baseline_status": baseline.overall_status, "projected_status": projected_report.overall_status,
                "baseline_deficiencies": baseline.deficient_count, "projected_deficiencies": projected_report.deficient_count,
                "rule_changes": [{"rule_id": after.rule_id, "before": before.status, "after": after.status}
                    for before, after in zip(baseline.results, projected_report.results) if before.status != after.status], "created_at": _now()}
    TIME_MACHINE_SNAPSHOTS.setdefault(app_id, []).append(snapshot)
    return snapshot

@app.get("/api/v1/applications/{app_id}/time-machine")
def get_regulatory_history(app_id: str):
    if app_id not in APPLICATIONS:
        raise HTTPException(status_code=404, detail="Application ID not found")
    return TIME_MACHINE_SNAPSHOTS.get(app_id, [])

# -------------------------------------------------------------
# Module 4: Document Anomaly & Forensics
# -------------------------------------------------------------
@app.post("/api/v1/forensics/analyze-upload")
async def analyze_uploaded_document(
    file: UploadFile = File(...),
    institution_id: str = Form("INST-CUSTOM"),
    institution_name: str = Form("Applicant College")
):
    content = await file.read()
    report = forensics_engine.analyze_document(
        document_id=f"DOC-{file.filename}",
        file_name=file.filename,
        file_bytes=content,
        institution_id=institution_id,
        institution_name=institution_name
    )
    return report.model_dump()

# -------------------------------------------------------------
# Module 7: Infrastructure Compliance Assistance (Geo & Blueprints)
# -------------------------------------------------------------
@app.post("/api/v1/infrastructure/verify-geo")
async def verify_infrastructure_geo(
    file: UploadFile = File(...),
    target_lat: float = Form(18.5204),
    target_lon: float = Form(73.8567)
):
    content = await file.read()
    try:
        im = Image.open(io.BytesIO(content))
        res = geo_verifier.verify_campus_photo(im, target_lat, target_lon)
        return res.model_dump()
    except Exception as e:
        return {"has_exif": False, "status": "FILE_READ_ERROR", "notes": str(e)}

@app.post("/api/v1/infrastructure/verify-blueprint")
async def verify_infrastructure_blueprint(file: UploadFile = File(...)):
    content = await file.read()
    try:
        im = Image.open(io.BytesIO(content))
        res = blueprint_analyzer.analyze_floor_plan(im)
        return res
    except Exception as e:
        return {"geometry_verified": False, "notes": str(e)}

@app.post("/api/v1/infrastructure/analyze-video")
async def analyze_infrastructure_video(file: UploadFile = File(...)):
    """Extracts a representative frame for the same image/CV evidence pipeline when FFmpeg is installed."""
    if file.content_type not in {"video/mp4", "video/quicktime", "video/x-msvideo"}:
        raise HTTPException(status_code=415, detail="Only MP4, MOV, and AVI video evidence is accepted")
    if not ffmpeg_available():
        return {"status": "MANUAL_REVIEW_REQUIRED", "reason": "FFmpeg is not installed; video frame extraction is unavailable."}
    content = await file.read()
    with tempfile.TemporaryDirectory() as temp_dir:
        source, frame = Path(temp_dir) / "source", Path(temp_dir) / "frame.jpg"
        source.write_bytes(content)
        result = subprocess.run(["ffmpeg", "-y", "-i", str(source), "-frames:v", "1", str(frame)], capture_output=True, timeout=30)
        if result.returncode != 0 or not frame.exists():
            return {"status": "MANUAL_REVIEW_REQUIRED", "reason": "Unable to extract a representative video frame."}
        image = Image.open(frame)
        return {"status": "FRAME_ANALYZED", "frame_forensics": forensics_engine.analyze_document(
            f"VID-{file.filename}", f"{file.filename}.jpg", frame.read_bytes(), "VIDEO-EVIDENCE", "Infrastructure Evidence"
        ).model_dump(), "blueprint_like_geometry": blueprint_analyzer.analyze_floor_plan(image)}

# -------------------------------------------------------------
# Module 9: Human Review, Audit Trail & Security
# -------------------------------------------------------------
@app.post("/api/v1/deficiency-notice/issue")
def issue_deficiency_notice(req: NoticeRequest):
    notice = audit_ledger.issue_deficiency_notice(
        application_id=req.application_id,
        institution_name=req.institution_name,
        officer_id=req.officer_id,
        deficiencies=req.deficiencies,
        instructions=req.instructions,
        deadline_date=req.deadline_date
    )
    return notice.model_dump()

@app.get("/api/v1/audit/logs/{application_id}")
def get_audit_logs(application_id: str):
    logs = audit_ledger.get_logs_for_application(application_id)
    return [l.model_dump() for l in logs]

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "HEALTHY",
        "system": "Sakshya AICTE Compliance Engine",
        "version": "1.0.0",
        "engines": {
            "z3_smt_solver": "ACTIVE",
            "timeline_engine": "ACTIVE",
            "document_forensics": "ACTIVE",
            "issuing_authority_gateway": "ACTIVE",
        },
        "integration_capabilities": {
            "pdf_text_extraction": "ACTIVE",
            "image_only_ocr": "MANUAL_REVIEW_REQUIRED",
            "issuing_authority_records": "DEMONSTRATION_CONNECTOR_MANUAL_REVIEW_FALLBACK",
            "digital_signature_and_qr": "MANUAL_REVIEW_REQUIRED",
            "secure_storage": "LOCAL_IN_MEMORY_DEMO_ONLY",
        },
        "modules_active": [
            "1. Application Management & Uploads",
            "2. OCR & Intelligent Data Extraction",
            "3. Cross-Document Record Validation",
            "4. Document Anomaly & Forgery Detection",
            "5. Original Issuing-Authority Verification",
            "6. Regulatory Compliance Engine (Z3 SMT)",
            "7. Infrastructure Compliance Assistance (CV)",
            "8. Officer Dashboard & Reporting",
            "9. Human Review, Audit Trail & Security"
        ]
    }
