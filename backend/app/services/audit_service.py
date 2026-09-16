"""
CompliScan LM — Audit Service.
Append-only audit event logging.
"""

from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.audit import AuditEvent
from shared.domain.enums import AuditEventType


class AuditService:
    @staticmethod
    async def log_event(
        db: AsyncSession,
        event_type: AuditEventType,
        inspection_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        actor_role: Optional[str] = None,
        details: Optional[Any] = None,
    ) -> AuditEvent:
        """Create and persist an append-only audit event."""
        event = AuditEvent(
            inspection_id=inspection_id,
            actor_id=actor_id,
            actor_role=actor_role,
            event_type=event_type.value if isinstance(event_type, AuditEventType) else str(event_type),
            details=details,
        )
        db.add(event)
        await db.flush()
        return event
