"""
CompliScan LM — OCRResult Model.
Stores raw PaddleOCR perception tokens and metadata.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, JSON, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.evidence import EvidenceAsset
    from backend.app.models.inspection import InspectionCase


class OCRResult(Base):
    __tablename__ = "ocr_results"
    __table_args__ = (
        UniqueConstraint("evidence_id", "processing_version", name="uq_ocr_evidence_version"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: f"OCR-{uuid.uuid4().hex[:12].upper()}",
    )
    evidence_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("evidence_assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    inspection_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("inspections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ocr_engine: Mapped[str] = mapped_column(
        String(50),
        default="paddleocr-onnx",
        nullable=False,
    )
    ocr_engine_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    processing_version: Mapped[str] = mapped_column(
        String(50),
        default="v1.0",
        nullable=False,
    )
    processing_blocked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    block_reason: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    total_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    full_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    tokens: Mapped[List[dict]] = mapped_column(
        JSON,
        default=list,
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
    evidence: Mapped["EvidenceAsset"] = relationship("EvidenceAsset", back_populates="ocr_result")
    inspection: Mapped["InspectionCase"] = relationship("InspectionCase")
