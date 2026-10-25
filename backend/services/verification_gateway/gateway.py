from typing import Dict, Any, List, Optional
from datetime import datetime
from .models import VerificationRecord, AuthorityStatus

class IssuingAuthorityGateway:
    """
    Issuing Authority Verification Gateway.
    Interfaces with DigiLocker NAD, MCA21 Society/Trust Registry, and State Land Records (Bhulekh).
    Provides robust fallback to manual officer queue with explicit status tracking.
    """
    def __init__(self):
        # Mock database of official state records for realistic simulation
        self.mock_bhulekh_db = {
            "KHASRA-402/1": {
                "owner_name": "Shri Ram Educational Society",
                "registered_acres": 2.50,
                "district": "Pune",
                "status": "CLEAR_TITLE",
                "encumbrance": "NONE"
            },
            "KHASRA-991/B": {
                "owner_name": "National Knowledge Trust",
                "registered_acres": 1.75,  # Mismatch: College claimed 2.80 acres!
                "district": "Bengaluru Rural",
                "status": "DISPUTED_TITLE",
                "encumbrance": "LITIGATION_PENDING"
            }
        }
        self.mock_mca21_db = {
            "SOC-MAH-2018-0912": {
                "society_name": "Shri Ram Educational Society",
                "registration_date": "2018-04-12",
                "status": "ACTIVE",
                "board_members": ["Dr. R. Sharma", "A. Verma"]
            }
        }
        self.mock_digilocker_db = {
            "DEG-IITB-2014-998": {
                "candidate_name": "Dr. Rajesh Kumar",
                "degree": "Ph.D. in Computer Science",
                "university": "IIT Bombay",
                "conferment_year": 2014,
                "verified": True
            }
        }

    def verify_land_record(self, survey_number: str, claimed_acres: float, society_name: str) -> VerificationRecord:
        record = self.mock_bhulekh_db.get(survey_number)
        now = datetime.utcnow().isoformat() + "Z"
        
        if not record:
            return VerificationRecord(
                verification_id=f"VERIF-LAND-{survey_number}",
                authority_name="State Land Records (Bhulekh)",
                document_ref="Land_Title_Deed.pdf",
                target_identifier=survey_number,
                status=AuthorityStatus.SOURCE_UNAVAILABLE,
                claimed_data={"survey_number": survey_number, "claimed_acres": claimed_acres, "society": society_name},
                mismatch_details="Survey record not found in digitised state land database. Routed to revenue officer manual verification queue.",
                api_response_code=404,
                verified_at=now
            )

        # Check area mismatch
        reg_acres = record["registered_acres"]
        if abs(reg_acres - claimed_acres) > 0.05 or record["status"] != "CLEAR_TITLE":
            return VerificationRecord(
                verification_id=f"VERIF-LAND-{survey_number}",
                authority_name="State Land Records (Bhulekh)",
                document_ref="Land_Title_Deed.pdf",
                target_identifier=survey_number,
                status=AuthorityStatus.MISMATCH_DETECTED,
                claimed_data={"survey_number": survey_number, "claimed_acres": claimed_acres, "society": society_name},
                official_registry_data=record,
                mismatch_details=(
                    f"Discrepancy detected: Application claims {claimed_acres:.2f} acres, but official Bhulekh registry "
                    f"records only {reg_acres:.2f} acres for title holder '{record['owner_name']}'. "
                    f"Title Status: {record['status']} ({record['encumbrance']})."
                ),
                api_response_code=200,
                verified_at=now
            )

        return VerificationRecord(
            verification_id=f"VERIF-LAND-{survey_number}",
            authority_name="State Land Records (Bhulekh)",
            document_ref="Land_Title_Deed.pdf",
            target_identifier=survey_number,
            status=AuthorityStatus.VERIFIED,
            claimed_data={"survey_number": survey_number, "claimed_acres": claimed_acres},
            official_registry_data=record,
            api_response_code=200,
            verified_at=now
        )

    def verify_faculty_degree(self, roll_number: str, candidate_name: str, degree_name: str) -> VerificationRecord:
        record = self.mock_digilocker_db.get(roll_number)
        now = datetime.utcnow().isoformat() + "Z"

        if not record:
            return VerificationRecord(
                verification_id=f"VERIF-NAD-{roll_number}",
                authority_name="DigiLocker NAD (National Academic Depository)",
                document_ref="PhD_Degree_Certificate.pdf",
                target_identifier=roll_number,
                status=AuthorityStatus.MANUAL_REVIEW_REQUIRED,
                claimed_data={"candidate": candidate_name, "degree": degree_name, "roll_number": roll_number},
                mismatch_details="University records for this graduation batch have not yet been synchronized with NAD. Manual document inspection required.",
                api_response_code=204,
                verified_at=now
            )

        return VerificationRecord(
            verification_id=f"VERIF-NAD-{roll_number}",
            authority_name="DigiLocker NAD (National Academic Depository)",
            document_ref="PhD_Degree_Certificate.pdf",
            target_identifier=roll_number,
            status=AuthorityStatus.VERIFIED,
            claimed_data={"candidate": candidate_name, "degree": degree_name},
            official_registry_data=record,
            api_response_code=200,
            verified_at=now
        )
