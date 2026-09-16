"""
CompliScan LM — Audit Schemas.
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict
from shared.domain.enums import AuditEventType


class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    inspection_id: Optional[str] = None
    actor_id: Optional[str] = None
    actor_role: Optional[str] = None
    event_type: AuditEventType
    details: Optional[Any] = None
    created_at: datetime
