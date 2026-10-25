from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import AuditLogEntry, DeficiencyNotice, UserRole

class SecurityAuditLedger:
    """
    Module 9: Human Review, Audit Trail & Security.
    Maintains an immutable event-sourced audit ledger for all regulatory compliance actions,
    admin overrides, deficiency notices, and officer decisions.
    """
    def __init__(self):
        self.log_entries: List[AuditLogEntry] = []
        self.deficiency_notices: Dict[str, DeficiencyNotice] = {}

    def record_action(
        self,
        actor_id: str,
        actor_name: str,
        role: UserRole,
        action: str,
        target_entity: str,
        details: Dict[str, Any]
    ) -> AuditLogEntry:
        now = datetime.utcnow().isoformat() + "Z"
        entry = AuditLogEntry(
            log_id=f"LOG-{len(self.log_entries) + 1:05d}",
            timestamp=now,
            actor_id=actor_id,
            actor_name=actor_name,
            role=role,
            action=action,
            target_entity=target_entity,
            details=details
        )
        self.log_entries.append(entry)
        return entry

    def issue_deficiency_notice(
        self,
        application_id: str,
        institution_name: str,
        officer_id: str,
        deficiencies: List[str],
        instructions: str,
        deadline_date: str
    ) -> DeficiencyNotice:
        now = datetime.utcnow().isoformat() + "Z"
        notice_id = f"DEF-NOTICE-{application_id}"
        notice = DeficiencyNotice(
            notice_id=notice_id,
            application_id=application_id,
            institution_name=institution_name,
            issued_by=officer_id,
            issued_at=now,
            deadline_date=deadline_date,
            deficiencies=deficiencies,
            rectification_instructions=instructions,
            status="PENDING_RECTIFICATION"
        )
        self.deficiency_notices[notice_id] = notice
        
        self.record_action(
            actor_id=officer_id,
            actor_name="AICTE Scrutiny Officer",
            role=UserRole.AICTE_SCRUTINY_OFFICER,
            action="DEFICIENCY_NOTICE_ISSUED",
            target_entity=f"APPLICATION:{application_id}",
            details={"notice_id": notice_id, "deficiencies_count": len(deficiencies)}
        )
        return notice

    def get_logs_for_application(self, application_id: str) -> List[AuditLogEntry]:
        target = f"APPLICATION:{application_id}"
        return [entry for entry in self.log_entries if entry.target_entity == target]
