"""
CompliScan LM — Phase 3 Compliance Evaluation Schemas.
Pydantic schemas for Applicability evaluation and Deterministic Compliance Findings.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from shared.domain.enums import ApplicabilityStatus, ComplianceResult


class ApplicabilityItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    inspection_id: str
    requirement_name: str
    status: ApplicabilityStatus
    basis: str
    rule_citation: str
    context_used: Dict[str, Any]
    rule_set_id: str
    rule_set_version: str
    evaluation_version: str
    created_at: datetime
    updated_at: datetime


class ApplicabilityListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inspection_id: str
    items: List[ApplicabilityItemResponse]
    rule_set_id: str
    rule_set_version: str
    evaluation_version: str


class ComplianceFindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    inspection_id: str
    evidence_id: Optional[str] = None
    ocr_result_id: Optional[str] = None
    structured_declaration_result_id: Optional[str] = None
    requirement_name: str
    result: ComplianceResult
    reason: str
    applicability_status: ApplicabilityStatus
    rule_citation: str
    rule_set_id: str
    rule_set_version: str
    evaluation_version: str
    source_token_indices: List[int]
    metadata_payload: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ComplianceEvaluationSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inspection_id: str
    rule_set_id: str
    rule_set_version: str
    evaluation_version: str
    findings: List[ComplianceFindingResponse]
    total_findings: int
    summary_counts: Dict[str, int]
