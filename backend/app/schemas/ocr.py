"""
CompliScan LM — OCR Perception Schemas.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class BoundingBoxSchema(BaseModel):
    """Four-point polygon coordinates in original evidence image space."""
    points: List[List[float]] = Field(
        ...,
        description="Four [x, y] vertex coordinates in original image pixel space",
    )
    coordinate_space: str = Field(
        default="original_image",
        description="Reference coordinate system of bounding box points",
    )


class OCRTokenSchema(BaseModel):
    """Structured perception token produced by PP-OCRv4 detection and recognition."""
    token_index: int = Field(..., description="0-indexed sequence position of detected token")
    line_index: int = Field(..., description="0-indexed text line group identifier")
    text: str = Field(..., description="Recognized literal text string without semantic normalization")
    confidence: float = Field(..., description="Perception recognition confidence score in [0.0, 1.0]")
    bounding_box: BoundingBoxSchema = Field(..., description="Bounding box polygon in original image coordinates")


class OCRResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    evidence_id: str
    inspection_id: str
    ocr_engine: str
    ocr_engine_version: str
    processing_version: str
    processing_blocked: bool
    block_reason: Optional[str] = None
    total_tokens: int
    full_text: Optional[str] = None
    tokens: List[OCRTokenSchema]
    created_at: datetime
    updated_at: datetime
