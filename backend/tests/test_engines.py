import pytest
from services.rule_solver import (
    STANDARD_APH_RULES,
    Z3RuleConflictFinder,
    DeterministicComplianceEngine,
    ComplianceStatus
)
from services.timeline_engine import (
    TimelineImpossibilityEngine,
    compute_interval_relation,
    AllenRelation
)
from services.forensics_engine import (
    DocumentForensicsEngine,
    ErrorLevelAnalysisDetector
)
from api.sample_data import (
    APP_1_FACTS,
    APP_1_TIMELINE,
    APP_2_FACTS,
    APP_2_TIMELINE
)
from PIL import Image

def test_z3_rule_conflict_finder():
    """Verifies that Z3 mathematically catches the conflict between APH and Circular."""
    finder = Z3RuleConflictFinder(STANDARD_APH_RULES)
    conflicts = finder.find_all_conflicts()
    assert len(conflicts) > 0
    conflict = conflicts[0]
    assert conflict.category == "LAND_REQUIREMENT"
    assert conflict.conflict_type == "SUBSET_AMBIGUITY"
    assert conflict.counterexample_model is not None
    # Counterexample should be a value between 1.8 and 2.5 (e.g. 2.0)
    counter_val = conflict.counterexample_model["counterexample_value"]
    assert 1.8 <= float(counter_val) < 2.5

def test_deterministic_compliance_engine():
    """Verifies compliance audit on genuine and deficient institutions."""
    engine = DeterministicComplianceEngine(STANDARD_APH_RULES)
    # Register an override so conflict is resolved in favor of the Circular
    conflicts = engine.active_conflicts
    engine.register_override(
        conflict_id=conflicts[0].conflict_id,
        winning_rule_id="CIRCULAR-2024-LAND-RELAX-URBAN",
        note="Circular 2024 active"
    )
    
    # Audit App 1 (Genuine)
    report_1 = engine.audit_institution(APP_1_FACTS)
    assert report_1.overall_status == ComplianceStatus.COMPLIANT
    assert report_1.deficient_count == 0

    # Audit App 2 (Deficient in faculty, built-up area, etc.)
    report_2 = engine.audit_institution(APP_2_FACTS)
    assert report_2.overall_status == ComplianceStatus.DEFICIENT
    assert report_2.deficient_count > 0

def test_allen_interval_algebra():
    """Verifies Allen's temporal interval calculations."""
    # A before B
    assert compute_interval_relation("2020-01-01", "2020-01-10", "2020-02-01", "2020-02-10") == AllenRelation.BEFORE
    # A meets B
    assert compute_interval_relation("2020-01-01", "2020-01-10", "2020-01-10", "2020-01-20") == AllenRelation.MEETS
    # A overlaps B
    assert compute_interval_relation("2020-01-01", "2020-01-15", "2020-01-10", "2020-01-25") == AllenRelation.OVERLAPS

def test_timeline_impossibility_engine():
    """Verifies that the Timeline Engine flags chronological paradoxes in App 2."""
    engine = TimelineImpossibilityEngine()
    
    # App 1 should be completely valid
    rep_1 = engine.audit_timeline(APP_1_FACTS.institution_id, APP_1_TIMELINE)
    assert rep_1.is_chronologically_valid is True
    assert rep_1.anomalies_count == 0

    # App 2 has 3 impossible sequences
    rep_2 = engine.audit_timeline(APP_2_FACTS.institution_id, APP_2_TIMELINE)
    assert rep_2.is_chronologically_valid is False
    assert rep_2.anomalies_count >= 2

def test_ela_detector():
    """Verifies that ELA generates a valid heatmap and variance metrics."""
    ela = ErrorLevelAnalysisDetector()
    im = Image.new("RGB", (200, 200), color=(255, 255, 255))
    score, stats, heatmap_b64 = ela.analyze_image(im)
    assert isinstance(score, float)
    assert "mean_error" in stats
    assert heatmap_b64.startswith("data:image/png;base64,")
