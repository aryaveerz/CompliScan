"""
CompliScan LM — AuditEvent Model.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base
from shared.domain.enums import AuditEventType

if TYPE_CHECKING:
    from backend.app.models.inspection import InspectionCase


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: f"AUD-{uuid.uuid4().hex[:12].upper()}")
    inspection_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("inspections.id"), nullable=True, index=True)
    actor_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    actor_role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    event_type: Mapped[str] = mapped_column(String(100), default=AuditEventType.INSPECTION_CREATED.value, nullable=False)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    inspection: Mapped[Optional["InspectionCase"]] = relationship("InspectionCase", back_populates="audit_events")
