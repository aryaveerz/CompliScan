"""
CompliScan LM — Evidence Request Models.
Enables formal Reviewer-to-Inspector requests for supplemental packaging evidence.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.inspection import InspectionCase
    from backend.app.models.evidence import EvidenceAsset
    from backend.app.models.user import User


class EvidenceRequest(Base):
    """
    Formal Reviewer request for additional visual evidence to establish a specific fact or declaration.
    Unique identification: ER-00001, ER-...
    """
    __tablename__ = "evidence_requests"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: f"ER-{uuid.uuid4().hex[:8].upper()}",
    )
    inspection_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("inspections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reviewer_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    requirement_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    request_reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    requested_condition: Mapped[str] = mapped_column(
        Text,
        nullable=False,  # Specifies what fact or condition needs to be proven
    )
    requested_evidence_type: Mapped[str] = mapped_column(
        String(50),
        default="SUPPLEMENTAL",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="OPEN",  # OPEN, FULFILLED, CANCELLED
        nullable=False,
        index=True,
    )

    # Response Linkage
    response_evidence_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("evidence_assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    response_note: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    resolved_by_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=True,
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    inspection: Mapped["InspectionCase"] = relationship("InspectionCase", back_populates="evidence_requests")
    reviewer: Mapped["User"] = relationship("User", foreign_keys=[reviewer_id])
    resolved_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[resolved_by_id])
    response_evidence: Mapped[Optional["EvidenceAsset"]] = relationship("EvidenceAsset")
