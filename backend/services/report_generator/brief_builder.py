from typing import Dict, Any, List, Optional
from datetime import datetime

class OfficerBriefBuilder:
    """
    Officer Brief Engine.
    Generates explainable, court-admissible audit reports that pair every deficiency,
    tampering detection, and timeline paradox side-by-side with statutory clause citations
    and document coordinates.
    """
    def __init__(self):
        pass

    def build_brief(
        self,
        institution_name: str,
        application_id: str,
        audit_report: Any,
        timeline_report: Any,
        forensic_reports: List[Any],
        authority_records: List[Any]
    ) -> Dict[str, Any]:
        
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Calculate Executive Verdict
        has_fraud = any(f.verdict.value == "FRAUDULENT" for f in forensic_reports)
        has_time_anomaly = not timeline_report.is_chronologically_valid
        has_deficiencies = audit_report.deficient_count > 0
        has_conflict = len(audit_report.conflicts_detected) > 0

        if has_fraud or (has_time_anomaly and any(a.severity == "CRITICAL_FRAUD_INDICATOR" for a in timeline_report.anomalies)):
            verdict = "REJECT_WITH_LEGAL_SHOW_CAUSE"
            verdict_badge = "CRITICAL NON-COMPLIANCE & TAMPERING DETECTED"
        elif has_conflict:
            verdict = "REFERRED_TO_RULE_CONFLICT_COMMITTEE"
            verdict_badge = "HELD FOR REGULATORY OVERRIDE"
        elif has_deficiencies:
            verdict = "DEFICIENT_REQUIRES_RECTIFICATION"
            verdict_badge = "DEFICIENCY NOTICE ISSUED"
        else:
            verdict = "RECOMMENDED_FOR_APPROVAL"
            verdict_badge = "ALL STATUTORY NORMS COMPLIANT"

        brief = {
            "brief_id": f"BRIEF-{application_id}",
            "application_id": application_id,
            "institution_name": institution_name,
            "generated_at": now,
            "executive_verdict": verdict,
            "verdict_badge": verdict_badge,
            "summary_metrics": {
                "rules_evaluated": audit_report.rules_evaluated,
                "compliant_rules": audit_report.compliant_count,
                "deficient_rules": audit_report.deficient_count,
                "timeline_anomalies": timeline_report.anomalies_count,
                "forensic_tampering_flags": sum(len(f.findings) for f in forensic_reports),
                "authority_mismatches": sum(1 for r in authority_records if r.status.value == "MISMATCH_DETECTED")
            },
            "compliance_ledger": [
                {
                    "rule_id": r.rule_id,
                    "title": r.rule_title,
                    "status": r.status.value,
                    "required": str(r.required_value),
                    "actual": str(r.actual_value),
                    "shortfall": f"{r.shortfall} {r.unit}" if r.shortfall else "None",
                    "citation": r.citation,
                    "explanation": r.explanation,
                    "document_anchor": r.document_anchor
                }
                for r in audit_report.results
            ],
            "timeline_paradoxes": [
                {
                    "id": a.anomaly_id,
                    "severity": a.severity,
                    "event_a": f"{a.event_a_name} ({a.event_a_date})",
                    "event_b": f"{a.event_b_name} ({a.event_b_date})",
                    "relation": a.observed_relation.value,
                    "explanation": a.explanation,
                    "citation": a.citation,
                    "proof_trace": a.inconsistency_trace
                }
                for a in timeline_report.anomalies
            ],
            "forensics_ledger": [
                {
                    "document_id": f.document_id,
                    "file_name": f.file_name,
                    "verdict": f.verdict.value,
                    "fraud_score": f.overall_fraud_score,
                    "findings": [
                        {
                            "title": item.title,
                            "severity": item.severity,
                            "desc": item.description,
                            "visual_evidence": item.visual_evidence_b64
                        }
                        for item in f.findings
                    ]
                }
                for f in forensic_reports
            ],
            "authority_verification": [
                {
                    "authority": r.authority_name,
                    "identifier": r.target_identifier,
                    "status": r.status.value,
                    "details": r.mismatch_details or "Registry data matched institutional claims with 100% fidelity."
                }
                for r in authority_records
            ]
        }
        return brief
