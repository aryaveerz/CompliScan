"""
CompliScan LM — FinalAuditRecord Model.
Immutable authoritative snapshot of an inspection case upon formal reviewer finalization.
"""

from datetime import datetime, timezone
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.inspection import InspectionCase
    from backend.app.models.user import User


class FinalAuditRecord(Base):
    """
    Authoritative, immutable snapshot of an inspection case at the moment of finalization.
    Contains complete static JSON records of context, evidence hashes, declarations,
    applicability, compliance findings, reviewer determinations, and audit trail metadata.
    """
    __tablename__ = "final_audit_records"
    __table_args__ = (
        UniqueConstraint("inspection_id", name="uq_final_audit_inspection_id"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: f"FAR-{uuid.uuid4().hex[:12].upper()}",
    )
    inspection_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("inspections.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        index=True,
    )
    finalized_by_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
    )
    finalized_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Master Legal Determination
    final_decision: Mapped[str] = mapped_column(
        String(50),
        nullable=False,  # COMPLIANT, NON_COMPLIANCE_CONFIRMED, INCONCLUSIVE
        index=True,
    )
    final_rationale: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Immutable Snapshots
    inspection_context_snapshot: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )
    evidence_snapshot: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
    )
    declaration_snapshot: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )
    applicability_snapshot: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
    )
    compliance_findings_snapshot: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
    )
    reviewer_decisions_snapshot: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
    )

    # Provenance
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
    source_evidence_hashes: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,  # Mapping of evidence_id -> sha256_hash
    )
    audit_metadata: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    inspection: Mapped["InspectionCase"] = relationship("InspectionCase", back_populates="final_audit_record")
    finalized_by: Mapped["User"] = relationship("User")
