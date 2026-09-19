"""
CompliScan LM — Phase 4 Inspector Verification Schemas.
Pydantic schemas for declaration corrections, manual observations, and review submission.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field


class DeclarationCorrectionCreate(BaseModel):
    requirement_name: str = Field(..., min_length=1, description="Requirement name being corrected (e.g. manufacturer_details)")
    field_name: Optional[str] = Field(None, description="Specific field in declaration if applicable")
    previous_value: Optional[Dict[str, Any]] = Field(None, description="Previous extracted JSON structure")
    corrected_value: Dict[str, Any] = Field(..., description="Corrected JSON structure")
    reason: str = Field(..., min_length=3, description="Mandatory reason for manual correction")
    evidence_id: Optional[str] = Field(None, description="Optional associated evidence asset ID")


class DeclarationCorrectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    inspection_id: str
    evidence_id: Optional[str] = None
    requirement_name: str
    field_name: Optional[str] = None
    previous_value: Optional[Dict[str, Any]] = None
    corrected_value: Dict[str, Any]
    reason: str
    inspector_id: str
    created_at: datetime


class ManualObservationCreate(BaseModel):
    requirement_name: str = Field(..., min_length=1, description="Requirement name or domain (e.g. general_packaging, mrp)")
    observation_text: str = Field(..., min_length=3, description="Detailed physical or contextual observation")


class ManualObservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    inspection_id: str
    requirement_name: str
    observation_text: str
    inspector_id: str
    created_at: datetime


class VerificationSubmitRequest(BaseModel):
    notes: Optional[str] = Field(None, description="Optional submission notes for the Reviewer")


class VerificationStateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inspection_id: str
    status: str
    is_ready_for_submission: bool
    blocking_reasons: List[str]
    corrections: List[DeclarationCorrectionResponse]
    observations: List[ManualObservationResponse]
