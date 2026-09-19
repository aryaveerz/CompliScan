"""
CompliScan LM — Reviewer Governance & Decision Models.
Stores formal recorded reviewer adjudications and overrides.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.inspection import InspectionCase
    from backend.app.models.compliance import ComplianceFinding
    from backend.app.models.user import User


class ReviewerDecision(Base):
    """
    Formal reviewer determination on an inspection case or requirement finding.
    Strictly separated from automated ComplianceFinding.result.
    """
    __tablename__ = "reviewer_decisions"
    __table_args__ = (
        UniqueConstraint("inspection_id", "requirement_name", name="uq_reviewer_decision_inspection_req"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: f"REV-{uuid.uuid4().hex[:12].upper()}",
    )
    inspection_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("inspections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    finding_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("compliance_findings.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    requirement_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    reviewer_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    determination: Mapped[str] = mapped_column(
        String(50),
        nullable=False,  # CONFIRMED, OVERRIDDEN, REVISION_REQUESTED, EVIDENCE_REQUESTED
    )
    original_result: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    adjudicated_result: Mapped[str] = mapped_column(
        String(50),
        nullable=False,  # PASS, POTENTIAL_NON_COMPLIANCE, REQUIRES_REVIEW, NOT_APPLICABLE, INCOMPLETE
    )
    is_override: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    rationale: Mapped[str] = mapped_column(
        Text,
        nullable=False,  # Mandatory recorded justification
    )

    rule_set_id: Mapped[str] = mapped_column(
        String(100),
        default="LMPC-2011-MVP-RULES",
        nullable=False,
    )
    rule_set_version: Mapped[str] = mapped_column(
        String(50),
        default="v1.0",
        nullable=False,
    )
    evaluation_version: Mapped[str] = mapped_column(
        String(50),
        default="v1.0",
        nullable=False,
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
    inspection: Mapped["InspectionCase"] = relationship("InspectionCase", back_populates="reviewer_decisions")
    reviewer: Mapped["User"] = relationship("User")
    finding: Mapped[Optional["ComplianceFinding"]] = relationship("ComplianceFinding")
