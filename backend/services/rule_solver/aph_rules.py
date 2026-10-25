from typing import List
from .models import RuleDefinition, RuleSource

# Standard AICTE Approval Process Handbook (APH) Rules & Supplementary Circulars
STANDARD_APH_RULES: List[RuleDefinition] = [
    RuleDefinition(
        rule_id="APH-2024-LAND-URBAN",
        category="LAND_REQUIREMENT",
        description="Minimum land required for Engineering & Technology UG institutions in Urban areas",
        source=RuleSource(
            document_name="AICTE Approval Process Handbook 2024-27",
            year=2024,
            clause_reference="Clause 4.1, Table 4.1(a)",
            title="Norms for Land Requirement",
            effective_date="2024-01-01"
        ),
        variable_name="land_area_acres",
        operator=">=",
        target_value=2.5,
        condition={"program": "ENGINEERING_TECHNOLOGY", "level": "UG", "location_type": "URBAN"},
        parameters={"min_acres": 2.5}
    ),
    RuleDefinition(
        rule_id="APH-2024-LAND-RURAL",
        category="LAND_REQUIREMENT",
        description="Minimum land required for Engineering & Technology UG institutions in Rural areas",
        source=RuleSource(
            document_name="AICTE Approval Process Handbook 2024-27",
            year=2024,
            clause_reference="Clause 4.1, Table 4.1(a)",
            title="Norms for Land Requirement",
            effective_date="2024-01-01"
        ),
        variable_name="land_area_acres",
        operator=">=",
        target_value=7.5,
        condition={"program": "ENGINEERING_TECHNOLOGY", "level": "UG", "location_type": "RURAL"},
        parameters={"min_acres": 7.5}
    ),
    RuleDefinition(
        rule_id="APH-2024-LAND-METRO",
        category="LAND_REQUIREMENT",
        description="Minimum land required for Engineering & Technology UG institutions in Mega/Metro areas",
        source=RuleSource(
            document_name="AICTE Approval Process Handbook 2024-27",
            year=2024,
            clause_reference="Clause 4.1, Table 4.1(a)",
            title="Norms for Land Requirement",
            effective_date="2024-01-01"
        ),
        variable_name="land_area_acres",
        operator=">=",
        target_value=1.5,
        condition={"program": "ENGINEERING_TECHNOLOGY", "level": "UG", "location_type": "METRO"},
        parameters={"min_acres": 1.5}
    ),
    RuleDefinition(
        rule_id="CIRCULAR-2024-LAND-RELAX-URBAN",
        category="LAND_REQUIREMENT",
        description="Supplementary Circular relaxing Urban Land norms for Greenfield Engineering Institutions with FSI >= 2.0",
        source=RuleSource(
            document_name="AICTE Circular F.No. 1-104/AICTE/P&AP/2024",
            year=2024,
            clause_reference="Section 2.3",
            title="Relaxation of Land Norms in Dense Urban Centers",
            effective_date="2024-06-15"
        ),
        variable_name="land_area_acres",
        operator=">=",
        target_value=1.8,
        condition={"program": "ENGINEERING_TECHNOLOGY", "level": "UG", "location_type": "URBAN"},
        parameters={"min_acres": 1.8, "requires_vertical_fsi": True}
    ),
    RuleDefinition(
        rule_id="APH-2024-FSR-ENGG-UG",
        category="FACULTY_STUDENT_RATIO",
        description="Faculty-to-Student Ratio (FSR) mandated for Engineering & Technology UG programs (1:20)",
        source=RuleSource(
            document_name="AICTE Approval Process Handbook 2024-27",
            year=2024,
            clause_reference="Clause 7.1, Appendix 7",
            title="Faculty Cadre and Student-to-Faculty Ratio",
            effective_date="2024-01-01"
        ),
        variable_name="faculty_student_ratio",
        operator="<=",
        target_value=20.0,
        condition={"program": "ENGINEERING_TECHNOLOGY", "level": "UG"},
        parameters={"max_students_per_faculty": 20.0}
    ),
    RuleDefinition(
        rule_id="APH-2024-CADRE-RATIO",
        category="CADRE_RATIO",
        description="Cadre Ratio of Professor : Associate Professor : Assistant Professor shall be 1:2:6",
        source=RuleSource(
            document_name="AICTE Approval Process Handbook 2024-27",
            year=2024,
            clause_reference="Clause 7.2",
            title="Cadre Distribution Norms",
            effective_date="2024-01-01"
        ),
        variable_name="cadre_ratio",
        operator="ratio",
        target_value={"prof": 1, "assoc": 2, "asst": 6},
        condition={"program": "ENGINEERING_TECHNOLOGY"},
        parameters={"prof_ratio": 1/9, "assoc_ratio": 2/9, "asst_ratio": 6/9}
    ),
    RuleDefinition(
        rule_id="APH-2024-BUILTUP-AREA",
        category="BUILT_UP_AREA",
        description="Minimum Built-up Carpet Area requirement per student enrolled",
        source=RuleSource(
            document_name="AICTE Approval Process Handbook 2024-27",
            year=2024,
            clause_reference="Clause 5.1, Appendix 4",
            title="Norms for Essential Infrastructure and Instructional Area",
            effective_date="2024-01-01"
        ),
        variable_name="built_up_area_sqm",
        operator=">=",
        target_value=8.0,  # 8 sqm per enrolled student
        condition={"program": "ENGINEERING_TECHNOLOGY", "level": "UG"},
        parameters={"sqm_per_student": 8.0}
    ),
    RuleDefinition(
        rule_id="APH-2024-FIRE-SAFETY",
        category="SAFETY_REGULATORY",
        description="Mandatory valid Fire Safety NOC from State/Municipal Authority",
        source=RuleSource(
            document_name="AICTE Approval Process Handbook 2024-27",
            year=2024,
            clause_reference="Clause 6.2(c)",
            title="Essential Statutory Approvals",
            effective_date="2024-01-01"
        ),
        variable_name="fire_safety_noc_valid",
        operator="==",
        target_value=True,
        condition={},
        parameters={"must_be_valid": True}
    ),
    RuleDefinition(
        rule_id="APH-2024-BARRIER-FREE",
        category="ACCESSIBILITY",
        description="Barrier-free environment for differently-abled persons (ramps, tactile paths, accessible toilets)",
        source=RuleSource(
            document_name="AICTE Approval Process Handbook 2024-27",
            year=2024,
            clause_reference="Clause 6.3(f)",
            title="Inclusivity and Barrier-Free Access Norms",
            effective_date="2024-01-01"
        ),
        variable_name="barrier_free_campus",
        operator="==",
        target_value=True,
        condition={},
        parameters={"mandated": True}
    )
]
