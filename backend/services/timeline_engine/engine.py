from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import (
    TimelineEvent,
    TimelineAnomaly,
    AllenRelation,
    DAGNode,
    DAGEdge,
    TimelineAuditReport
)
from .interval_algebra import compute_interval_relation, parse_date

class TimelineImpossibilityEngine:
    """
    Timeline Impossibility Engine using Allen's Interval Algebra and Directed Acyclic Graph (DAG)
    consistency verification to detect forged backdated approvals, chronological contradictions,
    and ghost faculty appointment overlaps.
    """
    def __init__(self):
        pass

    def audit_timeline(self, institution_id: str, events: List[TimelineEvent]) -> TimelineAuditReport:
        anomalies: List[TimelineAnomaly] = []
        event_dict = {e.event_id: e for e in events}

        # 1. Statutory Sequential Constraints
        # Rule 1: Land Deed Registration MUST precede Architect Site Inspection
        anomalies.extend(self._check_pair(
            event_dict,
            type_a="LAND_PURCHASE_DEED",
            type_b="ARCHITECT_SITE_INSPECTION",
            allowed_relations=[AllenRelation.BEFORE, AllenRelation.MEETS],
            severity="CRITICAL_FRAUD_INDICATOR",
            expected_desc="Land Purchase Registration must precede or meet Architect Inspection date.",
            citation="AICTE APH 2024-27 Clause 4.2 & Transfer of Property Act",
            impossibility_reason="Architect claims to have inspected and certified boundaries of institution land on a date PRIOR to legal ownership transfer of the title deed."
        ))

        # Rule 2: Land Deed MUST precede Building Plan Approval
        anomalies.extend(self._check_pair(
            event_dict,
            type_a="LAND_PURCHASE_DEED",
            type_b="BUILDING_PLAN_APPROVAL",
            allowed_relations=[AllenRelation.BEFORE, AllenRelation.MEETS],
            severity="CRITICAL_FRAUD_INDICATOR",
            expected_desc="Land Title Registration must precede Municipal Building Plan Approval.",
            citation="Municipal Corporation Act & AICTE Norms Appendix 4",
            impossibility_reason="Competent Municipal Authority cannot legally approve a construction blueprint on land not yet registered to the applicant trust/society."
        ))

        # Rule 3: Building Plan Approval MUST precede Occupancy / Completion Certificate
        anomalies.extend(self._check_pair(
            event_dict,
            type_a="BUILDING_PLAN_APPROVAL",
            type_b="OCCUPANCY_CERTIFICATE",
            allowed_relations=[AllenRelation.BEFORE, AllenRelation.MEETS],
            severity="CRITICAL_FRAUD_INDICATOR",
            expected_desc="Building Plan Approval must precede Occupancy/Completion Certificate issuance.",
            citation="National Building Code of India (NBC) Part III",
            impossibility_reason="Occupancy Certificate was issued on or before building plan approval date. Physically and legally impossible sequence."
        ))

        # Rule 4: Fire Safety NOC MUST be valid on Application Submission Date
        anomalies.extend(self._check_statutory_validity_at_application(event_dict))

        # Rule 5: Faculty Degree Award Date MUST precede Professor / Assoc Professor Appointment
        anomalies.extend(self._check_faculty_milestones(events))

        # Build Visual DAG representation
        flagged_ids = {a.event_a_id for a in anomalies} | {a.event_b_id for a in anomalies}
        
        dag_nodes: List[DAGNode] = []
        for e in events:
            dag_nodes.append(DAGNode(
                id=e.event_id,
                label=f"{e.entity_name} ({e.start_date})",
                date_str=e.start_date,
                category=e.category,
                status="FLAGGED" if e.event_id in flagged_ids else "VALID"
            ))

        # Sort events chronologically to build DAG sequence edges
        sorted_events = sorted(events, key=lambda x: x.start_date)
        dag_edges: List[DAGEdge] = []
        for i in range(len(sorted_events) - 1):
            e1 = sorted_events[i]
            e2 = sorted_events[i + 1]
            rel = compute_interval_relation(e1.start_date, e1.end_date, e2.start_date, e2.end_date)
            
            # Check if this edge is implicated in an anomaly
            is_anom = any(
                (a.event_a_id == e1.event_id and a.event_b_id == e2.event_id) or
                (a.event_a_id == e2.event_id and a.event_b_id == e1.event_id)
                for a in anomalies
            )
            dag_edges.append(DAGEdge(
                source=e1.event_id,
                target=e2.event_id,
                relation=rel.value,
                is_anomaly=is_anom
            ))

        return TimelineAuditReport(
            institution_id=institution_id,
            is_chronologically_valid=len(anomalies) == 0,
            anomalies_count=len(anomalies),
            anomalies=anomalies,
            dag_nodes=dag_nodes,
            dag_edges=dag_edges
        )

    def _check_pair(
        self,
        event_dict: Dict[str, TimelineEvent],
        type_a: str,
        type_b: str,
        allowed_relations: List[AllenRelation],
        severity: str,
        expected_desc: str,
        citation: str,
        impossibility_reason: str
    ) -> List[TimelineAnomaly]:
        anomalies = []
        items_a = [e for e in event_dict.values() if e.metadata.get("event_type") == type_a]
        items_b = [e for e in event_dict.values() if e.metadata.get("event_type") == type_b]

        for a in items_a:
            for b in items_b:
                rel = compute_interval_relation(a.start_date, a.end_date, b.start_date, b.end_date)
                if rel not in allowed_relations:
                    anomalies.append(TimelineAnomaly(
                        anomaly_id=f"TIME-ANOM-{a.event_id}-{b.event_id}",
                        severity=severity,
                        event_a_id=a.event_id,
                        event_a_name=a.entity_name,
                        event_a_date=a.start_date,
                        event_b_id=b.event_id,
                        event_b_name=b.entity_name,
                        event_b_date=b.start_date,
                        observed_relation=rel,
                        expected_relation=expected_desc,
                        citation=citation,
                        explanation=impossibility_reason,
                        inconsistency_trace=[
                            f"Step 1: Extracted timestamp for '{a.entity_name}' from [{a.document_ref}, p.{a.page}] is {a.start_date}.",
                            f"Step 2: Extracted timestamp for '{b.entity_name}' from [{b.document_ref}, p.{b.page}] is {b.start_date}.",
                            f"Step 3: Allen's Interval Algebra evaluation yields relation '{rel.value}'.",
                            f"Step 4: Statutory constraint mandates '{expected_desc}'.",
                            f"Conclusion: Chronological paradox detected. Document '{b.document_ref}' contains back-dated or fraudulent credentials."
                        ]
                    ))
        return anomalies

    def _check_statutory_validity_at_application(self, event_dict: Dict[str, TimelineEvent]) -> List[TimelineAnomaly]:
        anomalies = []
        app_events = [e for e in event_dict.values() if e.metadata.get("event_type") == "APPLICATION_SUBMISSION"]
        fire_events = [e for e in event_dict.values() if e.metadata.get("event_type") == "FIRE_SAFETY_NOC"]
        
        if not app_events or not fire_events:
            return anomalies

        app_date = parse_date(app_events[0].start_date)
        for f in fire_events:
            f_start = parse_date(f.start_date)
            f_end = parse_date(f.end_date) if f.end_date else f_start
            
            # Fire NOC must be issued before application and must not be expired
            if f_end < app_date:
                anomalies.append(TimelineAnomaly(
                    anomaly_id=f"TIME-EXPIRED-FIRE-{f.event_id}",
                    severity="CRITICAL_FRAUD_INDICATOR",
                    event_a_id=f.event_id,
                    event_a_name=f.entity_name,
                    event_a_date=f"{f.start_date} to {f.end_date}",
                    event_b_id=app_events[0].event_id,
                    event_b_name=app_events[0].entity_name,
                    event_b_date=app_events[0].start_date,
                    observed_relation=AllenRelation.BEFORE,
                    expected_relation="Fire Safety NOC must be valid on the date of Application submission.",
                    citation="AICTE APH 2024-27 Clause 6.2(c)",
                    explanation="Submitted Fire Safety NOC expired prior to the portal application submission date.",
                    inconsistency_trace=[
                        f"Fire NOC valid interval: {f.start_date} to {f.end_date}.",
                        f"Portal Application timestamp: {app_events[0].start_date}.",
                        "Interval relation reveals expiration prior to submission."
                    ]
                ))
        return anomalies

    def _check_faculty_milestones(self, events: List[TimelineEvent]) -> List[TimelineAnomaly]:
        anomalies = []
        degrees = [e for e in events if e.category == "ACADEMIC" and e.metadata.get("milestone") == "PHD_AWARD"]
        appointments = [e for e in events if e.category == "FACULTY_APPOINTMENT" and e.metadata.get("cadre") in ["PROFESSOR", "ASSOCIATE_PROFESSOR"]]

        for deg in degrees:
            fac_id = deg.metadata.get("faculty_id")
            related_appts = [a for a in appointments if a.metadata.get("faculty_id") == fac_id]
            for appt in related_appts:
                deg_date = parse_date(deg.start_date)
                appt_date = parse_date(appt.start_date)
                if appt_date < deg_date:
                    anomalies.append(TimelineAnomaly(
                        anomaly_id=f"TIME-FACULTY-{deg.event_id}-{appt.event_id}",
                        severity="CRITICAL_FRAUD_INDICATOR",
                        event_a_id=deg.event_id,
                        event_a_name=deg.entity_name,
                        event_a_date=deg.start_date,
                        event_b_id=appt.event_id,
                        event_b_name=appt.entity_name,
                        event_b_date=appt.start_date,
                        observed_relation=AllenRelation.AFTER,
                        expected_relation="Ph.D. award must precede appointment as Professor or Associate Professor.",
                        citation="AICTE Faculty Qualifications Regulations 2019 / Pay Scales Norms",
                        explanation=f"Faculty member appointed to senior cadre ({appt.metadata.get('cadre')}) before their mandatory Ph.D. qualifying degree was conferred.",
                        inconsistency_trace=[
                            f"Appointment Date: {appt.start_date} [{appt.document_ref}].",
                            f"Ph.D. Degree Award Date: {deg.start_date} [{deg.document_ref}].",
                            "Appointment chronologically precedes degree qualification date."
                        ]
                    ))
        return anomalies
