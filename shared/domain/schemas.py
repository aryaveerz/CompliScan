"""
CompliScan LM — Shared Pydantic Schema Contracts.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from shared.domain.enums import OriginStatus, EvidenceType, UserRole
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


class UserBase(BaseModel):
    """User profile base contract."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
