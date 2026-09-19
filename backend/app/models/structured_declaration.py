"""
CompliScan LM — StructuredDeclarationResult Model.
Stores structured Legal Metrology declarations extracted via Gemini 2.5 Flash.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.evidence import EvidenceAsset
    from backend.app.models.inspection import InspectionCase
    from backend.app.models.ocr import OCRResult


class StructuredDeclarationResult(Base):
    __tablename__ = "structured_declaration_results"
    __table_args__ = (
        UniqueConstraint("evidence_id", "extraction_version", "model_name", name="uq_extraction_evidence_version_model"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: f"DEC-{uuid.uuid4().hex[:12].upper()}",
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
    ocr_result_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("ocr_results.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Model & Prompt Provenance
    provider: Mapped[str] = mapped_column(
        String(50),
        default="google",
        nullable=False,
    )
    model_name: Mapped[str] = mapped_column(
        String(100),
        default="gemini-2.5-flash",
        nullable=False,
    )
    model_version: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    prompt_version: Mapped[str] = mapped_column(
        String(50),
        default="v1.0",
        nullable=False,
    )
    extraction_version: Mapped[str] = mapped_column(
        String(50),
        default="v1.0",
        nullable=False,
    )

    # Processing Status
    extraction_status: Mapped[str] = mapped_column(
        String(50),
        default="COMPLETED",
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

    # Structured Declarations Payload (Serialized Pydantic StructuredDeclarations)
    declarations: Mapped[dict] = mapped_column(
        JSON,
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
    evidence: Mapped["EvidenceAsset"] = relationship("EvidenceAsset", back_populates="structured_declarations")
    inspection: Mapped["InspectionCase"] = relationship("InspectionCase")
    ocr_result: Mapped["OCRResult"] = relationship("OCRResult")
