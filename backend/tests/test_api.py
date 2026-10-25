import pytest
from pathlib import Path
import io
from PIL import Image
from fastapi.testclient import TestClient
from api.gateway import app

client = TestClient(app)

def test_health():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["engines"]["z3_smt_solver"] == "ACTIVE"
    assert data["integration_capabilities"]["pdf_text_extraction"] == "ACTIVE"

def test_local_login_accepts_authorized_demo_account_and_rejects_invalid_login():
    valid = client.post("/api/v1/auth/login", json={
        "email": "officer@sakshya.gov.in", "password": "Sakshya@2026"
    })
    assert valid.status_code == 200
    assert valid.json()["role"] == "AICTE_SCRUTINY_OFFICER"
    invalid = client.post("/api/v1/auth/login", json={
        "email": "officer@sakshya.gov.in", "password": "incorrect"
    })
    assert invalid.status_code == 401

def test_get_rules_and_conflicts():
    res = client.get("/api/v1/rules")
    assert res.status_code == 200
    assert len(res.json()) >= 8

    res_conf = client.get("/api/v1/rules/conflicts")
    assert res_conf.status_code == 200
    conflicts = res_conf.json()
    assert len(conflicts) > 0
    assert conflicts[0]["conflict_type"] == "SUBSET_AMBIGUITY"

def test_run_audit_endpoint():
    res = client.post("/api/v1/audit/run/AICTE-2024-UG-001")
    assert res.status_code == 200
    data = res.json()
    assert "brief" in data
    assert "audit_report" in data
    assert "timeline_report" in data
    assert data["timeline_report"]["is_chronologically_valid"] is True

def test_run_fraud_audit_endpoint():
    res = client.post("/api/v1/audit/run/AICTE-2024-FRAUD-002")
    assert res.status_code == 200
    data = res.json()
    assert data["timeline_report"]["is_chronologically_valid"] is False
    assert len(data["timeline_report"]["anomalies"]) >= 2
    assert data["brief"]["executive_verdict"] == "REJECT_WITH_LEGAL_SHOW_CAUSE"

def test_checklist_validation_and_manual_review_workflow():
    app_id = "AICTE-2024-FRAUD-002"
    checklist = client.get(f"/api/v1/applications/{app_id}/checklist")
    assert checklist.status_code == 200
    assert any(item["status"] == "MISSING" for item in checklist.json())

    validation = client.post(f"/api/v1/applications/{app_id}/validate")
    assert validation.status_code == 200
    assert validation.json()["status"] == "MANUAL_REVIEW_REQUIRED"
    assert any(item["type"] == "MISSING_DOCUMENT" for item in validation.json()["discrepancies"])

    review = client.post("/api/v1/reviews/manual", json={
        "application_id": app_id,
        "officer_id": "OFFICER-001",
        "role": "AICTE_SCRUTINY_OFFICER",
        "comment": "Source record requires officer confirmation."
    })
    assert review.status_code == 200
    assert review.json()["action"] == "MANUAL_REVIEW_RECORDED"

def test_upload_extraction_and_authority_verification():
    app_id = "AICTE-2024-UG-001"
    pdf = Path(__file__).parents[2] / "demo_test_documents" / "3_Genuine_Government_Deed.pdf"
    with pdf.open("rb") as handle:
        upload = client.post(f"/api/v1/applications/{app_id}/documents", files={
            "file": (pdf.name, handle, "application/pdf")
        }, data={"document_type": "LAND_DEED", "mandatory": "true"})
    assert upload.status_code == 200
    document = upload.json()
    assert document["extraction"]["page_count"] >= 1
    assert "content" not in document

    verification = client.post("/api/v1/authorities/verify-land", json={
        "survey_number": "KHASRA-402/1", "claimed_acres": 2.5, "society_name": "Shri Ram Educational Society"
    })
    assert verification.status_code == 200
    assert verification.json()["status"] == "VERIFIED"

def test_advanced_analysis_modules():
    app_id = "AICTE-2024-FRAUD-002"
    graph = client.get(f"/api/v1/evidence-graph/{app_id}")
    assert graph.status_code == 200
    assert any(node["type"] == "REGULATION" for node in graph.json()["nodes"])

    timeline = client.get(f"/api/v1/timelines/{app_id}")
    assert timeline.status_code == 200
    assert timeline.json()["report"]["is_chronologically_valid"] is False

    benchmark = client.post("/api/v1/attack-lab/run", json={"scenario": "FONT_SPLICING"})
    assert benchmark.status_code == 200
    assert benchmark.json()["detection_status"] == "CAUGHT_BY_DETECTOR"

    replay = client.post(f"/api/v1/applications/{app_id}/time-machine", json={
        "label": "Corrected evidence", "corrections": {"land_area_acres": 2.8, "fire_safety_noc_valid": True}
    })
    assert replay.status_code == 200
    assert "rule_changes" in replay.json()
    assert client.get(f"/api/v1/applications/{app_id}/time-machine").status_code == 200

def test_scanned_upload_is_encrypted_and_reports_ocr_capability():
    image = Image.new("RGB", (40, 40), "white")
    payload = io.BytesIO()
    image.save(payload, format="PNG")
    response = client.post("/api/v1/applications/AICTE-2024-UG-001/documents", files={
        "file": ("scan.png", payload.getvalue(), "image/png")
    })
    assert response.status_code == 200
    document = response.json()
    assert document["storage"]["encrypted_at_rest"] is True
    assert document["extraction"]["ocr_status"] in {"EXTRACTED", "MANUAL_REVIEW_REQUIRED"}
    assert "qr_code" in document["integrity"]

def test_video_evidence_reports_supported_or_manual_review_state():
    response = client.post("/api/v1/infrastructure/analyze-video", files={
        "file": ("site.mp4", b"not-a-real-video", "video/mp4")
    })
    assert response.status_code == 200
    assert response.json()["status"] in {"FRAME_ANALYZED", "MANUAL_REVIEW_REQUIRED"}
