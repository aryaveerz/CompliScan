import sys
sys.path.insert(0, r"G:\CompliScan")
import json
from backend.app.db.session import SyncSessionLocal
from backend.app.models.inspection import InspectionCase
from backend.app.models.reviewer import ReviewerDecision
from backend.app.models.audit import AuditEvent

db = SyncSessionLocal()
case = db.query(InspectionCase).filter(InspectionCase.case_number == 'INSP-2026-DEL-LM-D88A').first()

print("=" * 80)
print("INDEPENDENT VERIFICATION OF REVIEWER DECISIONS & AUDIT EVENTS")
print("=" * 80)

decisions = db.query(ReviewerDecision).filter(ReviewerDecision.inspection_id == case.id).order_by(ReviewerDecision.created_at.asc()).all()
print(f"\n1. TOTAL PERSISTED REVIEWER DECISIONS: {len(decisions)}")
for idx, d in enumerate(decisions, 1):
    print(f"\n[{idx}] Decision ID: {d.id}")
    print(f"    Requirement: {d.requirement_name}")
    print(f"    Determination: {d.determination}")
    print(f"    Original -> Adjudicated: {d.original_result} -> {d.adjudicated_result}")
    print(f"    Is Override: {d.is_override}")
    print(f"    Verbatim Rationale: {d.rationale}")
    print(f"    Timestamp: {d.created_at}")

events = db.query(AuditEvent).filter(AuditEvent.inspection_id == case.id).order_by(AuditEvent.created_at.asc()).all()
print(f"\n2. TOTAL PERSISTED AUDIT EVENTS IN DATABASE: {len(events)}")
for idx, e in enumerate(events, 1):
    print(f"[{idx:02d}] ID: {e.id} | Timestamp: {e.created_at} | Event Type: {e.event_type} | Actor ID: {e.actor_id} | Actor Role: {e.actor_role}")
    print(f"     Details: {json.dumps(e.details)}")
