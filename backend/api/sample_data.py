from services.rule_solver.models import InstitutionalFacts
from services.timeline_engine.models import TimelineEvent

# Pre-packaged benchmark institutional applications for demonstration

# Application 1: Fully Compliant Institution
APP_1_FACTS = InstitutionalFacts(
    institution_id="AICTE-2024-UG-001",
    institution_name="Savitribai Phule Institute of Technology",
    program="ENGINEERING_TECHNOLOGY",
    level="UG",
    location_type="URBAN",
    approved_intake=360,
    total_enrolment=1440,
    land_area_acres=2.85,
    built_up_area_sqm=12800.0,
    instructional_area_sqm=8200.0,
    administrative_area_sqm=2100.0,
    amenities_area_sqm=2500.0,
    computer_centers_count=6,
    smart_classrooms_count=18,
    total_faculty=80,
    professors=10,
    associate_professors=20,
    assistant_professors=50,
    faculty_with_phd=32,
    corpus_fund_lakhs=150.0,
    fire_safety_noc_valid=True,
    building_plan_approved=True,
    barrier_free_campus=True,
    provenance={
        "land_area_acres": {"doc_id": "DEED-001", "page": 2, "bbox": [120, 340, 280, 365], "source_text": "Total land holding: 2.85 Acres at Survey No. 402/1"},
        "built_up_area_sqm": {"doc_id": "ARCH-001", "page": 1, "bbox": [85, 210, 310, 235], "source_text": "Built-up Carpet Area: 12,800.00 Sq. Meters"}
    }
)

APP_1_TIMELINE = [
    TimelineEvent(
        event_id="EVT-101",
        entity_name="Society Registration",
        category="STATUTORY",
        start_date="2018-04-12",
        document_ref="Society_Reg_Certificate.pdf",
        page=1,
        metadata={"event_type": "SOCIETY_REGISTRATION"}
    ),
    TimelineEvent(
        event_id="EVT-102",
        entity_name="Land Purchase Deed Registration",
        category="LAND_TITLE",
        start_date="2019-02-15",
        document_ref="Land_Title_Deed.pdf",
        page=3,
        metadata={"event_type": "LAND_PURCHASE_DEED"}
    ),
    TimelineEvent(
        event_id="EVT-103",
        entity_name="Municipal Building Plan Approval",
        category="CONSTRUCTION",
        start_date="2019-09-20",
        document_ref="Building_Plan_Sanction.pdf",
        page=1,
        metadata={"event_type": "BUILDING_PLAN_APPROVAL"}
    ),
    TimelineEvent(
        event_id="EVT-104",
        entity_name="Architect Site & Carpet Area Certification",
        category="CONSTRUCTION",
        start_date="2021-03-10",
        document_ref="Architect_Carpet_Certificate.pdf",
        page=1,
        metadata={"event_type": "ARCHITECT_SITE_INSPECTION"}
    ),
    TimelineEvent(
        event_id="EVT-105",
        entity_name="Fire Safety NOC Issuance",
        category="STATUTORY_NOC",
        start_date="2024-01-10",
        end_date="2027-01-09",
        document_ref="Fire_Safety_NOC.pdf",
        page=1,
        metadata={"event_type": "FIRE_SAFETY_NOC"}
    ),
    TimelineEvent(
        event_id="EVT-106",
        entity_name="AICTE Approval Application Submission",
        category="STATUTORY",
        start_date="2024-05-15",
        document_ref="AICTE_Application_Form.pdf",
        page=1,
        metadata={"event_type": "APPLICATION_SUBMISSION"}
    )
]

# Application 2: Tampered & Back-dated Fraudulent Institution
# 1. Land Area altered from 1.75 to 2.80 acres (Bhulekh API mismatch + ELA tampering)
# 2. Chronological paradox: Architect inspection on 2018-01-15 BEFORE land was registered on 2019-08-10!
# 3. Fire NOC expired before application date
# 4. Professor appointed before PhD degree conferment
APP_2_FACTS = InstitutionalFacts(
    institution_id="AICTE-2024-FRAUD-002",
    institution_name="National Knowledge Institute of Tech & Research",
    program="ENGINEERING_TECHNOLOGY",
    level="UG",
    location_type="URBAN",
    approved_intake=360,
    total_enrolment=1440,
    land_area_acres=2.10,  # Caught in Circular conflict (1.8 vs 2.5 APH) + Bhulekh mismatch
    built_up_area_sqm=9200.0,  # Deficient: needs 11,520 sqm (8 sqm/student)
    instructional_area_sqm=6100.0,
    administrative_area_sqm=1500.0,
    amenities_area_sqm=1600.0,
    computer_centers_count=3,
    smart_classrooms_count=8,
    total_faculty=52,  # Deficient: FSR 1440/52 = 1:27.7 (limit 1:20)
    professors=2,      # Cadre imbalance: min 6 required
    associate_professors=6,  # min 11 required
    assistant_professors=44,
    faculty_with_phd=8,
    corpus_fund_lakhs=60.0,
    fire_safety_noc_valid=False,
    building_plan_approved=True,
    barrier_free_campus=False,
    provenance={
        "land_area_acres": {"doc_id": "DEED-002-SPLICED", "page": 1, "bbox": [105, 310, 275, 340], "source_text": "Land Parcel: 2.10 Acres at Survey No. 991/B"},
        "total_faculty": {"doc_id": "FACULTY-LIST-002", "page": 4, "bbox": [50, 420, 290, 450], "source_text": "Total Teaching Faculty: 52"}
    }
)

APP_2_TIMELINE = [
    TimelineEvent(
        event_id="EVT-201",
        entity_name="Society Registration",
        category="STATUTORY",
        start_date="2019-01-10",
        document_ref="Trust_Deed_Scan.pdf",
        page=1,
        metadata={"event_type": "SOCIETY_REGISTRATION"}
    ),
    TimelineEvent(
        event_id="EVT-202",
        entity_name="Architect Site Inspection & Carpet Area Certificate",
        category="CONSTRUCTION",
        start_date="2019-03-25",  # PARADOX: 5 months before land was purchased!
        document_ref="Architect_Certificate_Forged.pdf",
        page=1,
        metadata={"event_type": "ARCHITECT_SITE_INSPECTION"}
    ),
    TimelineEvent(
        event_id="EVT-203",
        entity_name="Land Title Registration Deed",
        category="LAND_TITLE",
        start_date="2019-08-10",
        document_ref="Land_Deed_Khasra_991B.pdf",
        page=2,
        metadata={"event_type": "LAND_PURCHASE_DEED"}
    ),
    TimelineEvent(
        event_id="EVT-204",
        entity_name="Municipal Building Plan Approval",
        category="CONSTRUCTION",
        start_date="2020-02-14",
        document_ref="Building_Approval_Scan.pdf",
        page=1,
        metadata={"event_type": "BUILDING_PLAN_APPROVAL"}
    ),
    TimelineEvent(
        event_id="EVT-205",
        entity_name="Fire Safety NOC (Expired)",
        category="STATUTORY_NOC",
        start_date="2021-01-10",
        end_date="2023-01-09",  # Expired before application!
        document_ref="Fire_NOC_2021.pdf",
        page=1,
        metadata={"event_type": "FIRE_SAFETY_NOC"}
    ),
    TimelineEvent(
        event_id="EVT-206",
        entity_name="Appointment of Dr. K. Mehta as Professor",
        category="FACULTY_APPOINTMENT",
        start_date="2022-07-01",  # Before PhD was awarded!
        document_ref="Joining_Letter_Mehta.pdf",
        page=1,
        metadata={"faculty_id": "FAC-MEHTA-99", "cadre": "PROFESSOR"}
    ),
    TimelineEvent(
        event_id="EVT-207",
        entity_name="Ph.D. Degree Award for Dr. K. Mehta",
        category="ACADEMIC",
        start_date="2023-11-20",  # Awarded 16 months AFTER appointment!
        document_ref="PhD_Provisional_Mehta.pdf",
        page=1,
        metadata={"faculty_id": "FAC-MEHTA-99", "milestone": "PHD_AWARD"}
    ),
    TimelineEvent(
        event_id="EVT-208",
        entity_name="AICTE Approval Application Submission",
        category="STATUTORY",
        start_date="2024-06-01",
        document_ref="AICTE_Application_2024.pdf",
        page=1,
        metadata={"event_type": "APPLICATION_SUBMISSION"}
    )
]
