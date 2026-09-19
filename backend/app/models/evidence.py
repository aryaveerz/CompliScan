"""
CompliScan LM — EvidenceAsset Model.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base
from shared.domain.enums import EvidenceType

if TYPE_CHECKING:
    from backend.app.models.user import User
    from backend.app.models.inspection import InspectionCase
    from backend.app.models.image_quality import ImageQualityAssessment
    from backend.app.models.ocr import OCRResult
    from backend.app.models.structured_declaration import StructuredDeclarationResult



class EvidenceAsset(Base):
    __tablename__ = "evidence_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: f"EV-{uuid.uuid4().hex[:12].upper()}")
    inspection_id: Mapped[str] = mapped_column(String(36), ForeignKey("inspections.id"), nullable=False, index=True)
    evidence_type: Mapped[str] = mapped_column(String(50), default=EvidenceType.PRIMARY.value, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    is_immutable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    uploaded_by_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    inspection: Mapped["InspectionCase"] = relationship("InspectionCase", back_populates="evidence_assets")
    uploaded_by: Mapped["User"] = relationship("User", back_populates="uploaded_evidence")
    quality_assessment: Mapped[Optional["ImageQualityAssessment"]] = relationship(
        "ImageQualityAssessment",
        back_populates="evidence",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    ocr_result: Mapped[Optional["OCRResult"]] = relationship(
        "OCRResult",
        back_populates="evidence",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    structured_declarations: Mapped[Optional["StructuredDeclarationResult"]] = relationship(
        "StructuredDeclarationResult",
        back_populates="evidence",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
