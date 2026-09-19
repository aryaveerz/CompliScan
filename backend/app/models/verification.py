"""
CompliScan LM — Inspector Verification & Manual Observation Models.
Stores inspector corrections to extracted declaration values and structured manual observations.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.inspection import InspectionCase
    from backend.app.models.evidence import EvidenceAsset
    from backend.app.models.user import User


class DeclarationCorrection(Base):
    """
    Inspector correction to extracted declaration values.
    Preserves audit history of changes made by the inspector prior to submission.
    """
    __tablename__ = "declaration_corrections"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: f"COR-{uuid.uuid4().hex[:12].upper()}",
    )
    inspection_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("inspections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    evidence_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("evidence_assets.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    requirement_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    field_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    previous_value: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )
    corrected_value: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    inspector_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    inspection: Mapped["InspectionCase"] = relationship("InspectionCase", back_populates="declaration_corrections")
    inspector: Mapped["User"] = relationship("User")
    evidence: Mapped[Optional["EvidenceAsset"]] = relationship("EvidenceAsset")


class ManualObservation(Base):
    """
    Inspector manual physical or contextual observations where automated perception is insufficient.
    """
    __tablename__ = "manual_observations"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: f"OBS-{uuid.uuid4().hex[:12].upper()}",
    )
    inspection_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("inspections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    requirement_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    observation_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    inspector_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    inspection: Mapped["InspectionCase"] = relationship("InspectionCase", back_populates="manual_observations")
    inspector: Mapped["User"] = relationship("User")
