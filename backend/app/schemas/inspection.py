"""
CompliScan LM — Inspection Schemas.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from shared.domain.states import InspectionLifecycleState, ProcessingState, FinalizationStatus
from shared.domain.enums import OriginStatus
from backend.app.schemas.evidence import EvidenceResponse
from backend.app.schemas.auth import UserResponse


class InspectionCreateRequest(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=255, description="Product common or brand name")
    origin_status: OriginStatus = Field(default=OriginStatus.UNKNOWN, description="Origin status feeding applicability")
    product_category: Optional[str] = Field(None, max_length=100, description="Optional metadata category")
    reference_url: Optional[str] = Field(None, max_length=500, description="Optional metadata reference URL")
    notes: Optional[str] = Field(None, max_length=2000, description="Optional inspector notes")


class InspectionUpdateRequest(BaseModel):
    product_name: Optional[str] = Field(None, min_length=1, max_length=255)
    origin_status: Optional[OriginStatus] = None
    product_category: Optional[str] = Field(None, max_length=100)
    reference_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=2000)


class InspectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_number: str
    status: InspectionLifecycleState
    processing_state: ProcessingState
    finalization_status: FinalizationStatus
    
    # Product context
    product_name: str
    origin_status: OriginStatus
    product_category: Optional[str] = None
    reference_url: Optional[str] = None
    notes: Optional[str] = None

    # Actors & Ownership
    created_by_id: str
    reviewer_id: Optional[str] = None
    created_by: Optional[UserResponse] = None
    reviewer: Optional[UserResponse] = None

    # Evidence
    evidence_assets: List[EvidenceResponse] = []

    # Timestamps
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime] = None
    finalized_at: Optional[datetime] = None


class InspectionListResponse(BaseModel):
    items: List[InspectionResponse]
    total: int
