"""
CompliScan LM — Image Quality Assessment & Analysis Job Schemas.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from shared.domain.enums import ImageQualityStatus, QualityReasonCode, JobType, JobStatus


class ImageQualityAssessmentResponse(BaseModel):
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


class AnalysisJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    inspection_id: str
    evidence_id: Optional[str] = None
    job_type: JobType
    status: JobStatus
    attempts: int
    max_attempts: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
