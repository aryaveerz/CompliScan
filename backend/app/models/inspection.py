"""
CompliScan LM — InspectionCase Aggregate Root Model.
"""

from datetime import datetime, timezone
import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base
from shared.domain.states import InspectionLifecycleState, ProcessingState, FinalizationStatus
from shared.domain.enums import OriginStatus

if TYPE_CHECKING:
    from backend.app.models.user import User
    from backend.app.models.evidence import EvidenceAsset
    from backend.app.models.audit import AuditEvent
    from backend.app.models.compliance import ApplicabilityResult, ComplianceFinding
    from backend.app.models.verification import DeclarationCorrection, ManualObservation
    from backend.app.models.reviewer import ReviewerDecision
    from backend.app.models.evidence_request import EvidenceRequest
    from backend.app.models.final_audit import FinalAuditRecord


class InspectionCase(Base):
    __tablename__ = "inspections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: f"INS-{uuid.uuid4().hex[:12].upper()}")
    case_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=InspectionLifecycleState.DRAFT.value, index=True, nullable=False)
    processing_state: Mapped[str] = mapped_column(String(50), default=ProcessingState.IDLE.value, nullable=False)
    finalization_status: Mapped[str] = mapped_column(String(50), default=FinalizationStatus.UNFINALIZED.value, nullable=False)

    # Product Context
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    origin_status: Mapped[str] = mapped_column(String(50), default=OriginStatus.UNKNOWN.value, nullable=False)
    product_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reference_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Ownership & Reviewer
    created_by_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    reviewer_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    finalized_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id], back_populates="created_inspections")
    reviewer: Mapped[Optional["User"]] = relationship("User", foreign_keys=[reviewer_id], back_populates="assigned_inspections")
    evidence_assets: Mapped[List["EvidenceAsset"]] = relationship("EvidenceAsset", back_populates="inspection", cascade="all, delete-orphan")
    audit_events: Mapped[List["AuditEvent"]] = relationship("AuditEvent", back_populates="inspection", cascade="all, delete-orphan")
    applicability_results: Mapped[List["ApplicabilityResult"]] = relationship("ApplicabilityResult", back_populates="inspection", cascade="all, delete-orphan")
    compliance_findings: Mapped[List["ComplianceFinding"]] = relationship("ComplianceFinding", back_populates="inspection", cascade="all, delete-orphan")
    declaration_corrections: Mapped[List["DeclarationCorrection"]] = relationship("DeclarationCorrection", back_populates="inspection", cascade="all, delete-orphan")
    manual_observations: Mapped[List["ManualObservation"]] = relationship("ManualObservation", back_populates="inspection", cascade="all, delete-orphan")
    reviewer_decisions: Mapped[List["ReviewerDecision"]] = relationship("ReviewerDecision", back_populates="inspection", cascade="all, delete-orphan")
    evidence_requests: Mapped[List["EvidenceRequest"]] = relationship("EvidenceRequest", back_populates="inspection", cascade="all, delete-orphan")
    final_audit_record: Mapped[Optional["FinalAuditRecord"]] = relationship("FinalAuditRecord", back_populates="inspection", uselist=False, cascade="all, delete-orphan")
