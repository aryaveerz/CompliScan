"""
CompliScan LM — ImageQualityAssessment Model.
Stores technical suitability screening results for evidence assets.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base
from shared.domain.enums import ImageQualityStatus

if TYPE_CHECKING:
    from backend.app.models.evidence import EvidenceAsset
    from backend.app.models.inspection import InspectionCase


class ImageQualityAssessment(Base):
    __tablename__ = "image_quality_assessments"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: f"IQA-{uuid.uuid4().hex[:12].upper()}",
    )
    evidence_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("evidence_assets.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    inspection_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("inspections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quality_status: Mapped[str] = mapped_column(
        String(50),
        default=ImageQualityStatus.USABLE.value,
        nullable=False,
        index=True,
    )
    assessment_version: Mapped[str] = mapped_column(String(50), nullable=False)

    # Image metrics
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    total_pixels: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    is_decoded: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Quantitative perception screening metrics
    sharpness_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    brightness_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    contrast_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Structured reason codes & metrics details
    reason_codes: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

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
    evidence: Mapped["EvidenceAsset"] = relationship("EvidenceAsset", back_populates="quality_assessment")
    inspection: Mapped["InspectionCase"] = relationship("InspectionCase")
