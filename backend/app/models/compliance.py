"""
CompliScan LM — Phase 3 Compliance Evaluation Models.
Stores persisted ApplicabilityResults and ComplianceFindings.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.inspection import InspectionCase
    from backend.app.models.evidence import EvidenceAsset
    from backend.app.models.ocr import OCRResult
    from backend.app.models.structured_declaration import StructuredDeclarationResult


class ApplicabilityResult(Base):
    """
    Persisted evaluation of whether a statutory requirement applies to an inspection.
    Explains the basis, context used, and rule citation.
    """
    __tablename__ = "applicability_results"
    __table_args__ = (
        UniqueConstraint("inspection_id", "requirement_name", "evaluation_version", name="uq_applicability_inspection_req_version"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: f"APP-{uuid.uuid4().hex[:12].upper()}",
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
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,  # APPLICABLE, NOT_APPLICABLE, REQUIRES_REVIEW
    )
    basis: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    rule_citation: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    context_used: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
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
    inspection: Mapped["InspectionCase"] = relationship("InspectionCase", back_populates="applicability_results")


class ComplianceFinding(Base):
    """
    Deterministic rule compliance finding linked to evidence, OCR tokens, and structured declarations.
    Authoritative result vocabulary: PASS, POTENTIAL_NON_COMPLIANCE, REQUIRES_REVIEW, NOT_APPLICABLE, INCOMPLETE, PROCESSING_FAILED.
    """
    __tablename__ = "compliance_findings"
    __table_args__ = (
        UniqueConstraint("inspection_id", "evidence_id", "requirement_name", "evaluation_version", name="uq_finding_inspection_evidence_req_version"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: f"FND-{uuid.uuid4().hex[:12].upper()}",
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
    ocr_result_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("ocr_results.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    structured_declaration_result_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("structured_declaration_results.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    requirement_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    result: Mapped[str] = mapped_column(
        String(50),
        nullable=False,  # PASS, POTENTIAL_NON_COMPLIANCE, REQUIRES_REVIEW, NOT_APPLICABLE, INCOMPLETE, PROCESSING_FAILED
        index=True,
    )
    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    applicability_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    rule_citation: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
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
    source_token_indices: Mapped[List[int]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    metadata_payload: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
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
    inspection: Mapped["InspectionCase"] = relationship("InspectionCase", back_populates="compliance_findings")
    evidence: Mapped[Optional["EvidenceAsset"]] = relationship("EvidenceAsset")
    ocr_result: Mapped[Optional["OCRResult"]] = relationship("OCRResult")
    structured_declaration_result: Mapped[Optional["StructuredDeclarationResult"]] = relationship("StructuredDeclarationResult")
