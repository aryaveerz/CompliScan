"""
CompliScan LM — Evidence Schemas.
"""

from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict
from shared.domain.enums import EvidenceType


class EvidenceResponse(BaseModel):
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


class EvidenceListResponse(BaseModel):
    items: List[EvidenceResponse]
    total: int
