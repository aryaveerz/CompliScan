"""
CompliScan LM — Shared Pydantic Schema Contracts.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from shared.domain.enums import (
    OriginStatus,
    EvidenceType,
    UserRole,
    ImageQualityStatus,
    QualityReasonCode,
    JobType,
    JobStatus,
)
from shared.domain.states import InspectionLifecycleState, ProcessingState, FinalizationStatus


class ProductContextBase(BaseModel):
    """Product context input contract."""
    product_name: str = Field(..., min_length=1, max_length=255, description="Common or brand name of the product")
    origin_status: OriginStatus = Field(default=OriginStatus.UNKNOWN, description="Domestic, Imported, or Unknown")
    product_category: Optional[str] = Field(None, max_length=100, description="Optional category metadata")
    reference_url: Optional[str] = Field(None, max_length=500, description="Optional online reference URL (metadata only)")
    notes: Optional[str] = Field(None, max_length=2000, description="Optional inspector notes")


class EvidenceAssetBase(BaseModel):
    """Evidence artifact contract."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    inspection_id: str
    evidence_type: EvidenceType
    original_filename: str
    mime_type: str
    file_size_bytes: int
    sha256_hash: str
    storage_path: str
    is_immutable: bool
    uploaded_by_id: str
    created_at: datetime


class ImageQualityAssessmentBase(BaseModel):
    """Image Quality Assessment contract."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    evidence_id: str
    inspection_id: str
    quality_status: ImageQualityStatus
    assessment_version: str
    width: int
    height: int
    total_pixels: int
    mime_type: str
    is_decoded: bool
    sharpness_score: Optional[float] = None
    brightness_score: Optional[float] = None
    contrast_score: Optional[float] = None
    reason_codes: List[QualityReasonCode]
    details: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class AnalysisJobBase(BaseModel):
    """Analysis Job contract."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    inspection_id: str
    evidence_id: Optional[str] = None
    job_type: JobType
    status: JobStatus
    worker_id: Optional[str] = None
    attempts: int
    max_attempts: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class UserBase(BaseModel):
    """User profile base contract."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
