"""
CompliScan LM — Phase 4 Reviewer Governance & Decision Schemas.
Pydantic schemas for reviewer decisions, revision requests, evidence requests, queue items, and final audit records.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field
from shared.domain.enums import ReviewerDeterminationType, ComplianceResult, FinalDecision, EvidenceRequestStatus


class ReviewerDecisionCreate(BaseModel):
    requirement_name: str = Field(..., min_length=1, description="Requirement name being adjudicated")
    determination: ReviewerDeterminationType = Field(..., description="Reviewer action (CONFIRMED, OVERRIDDEN, REVISION_REQUESTED, EVIDENCE_REQUESTED)")
    adjudicated_result: ComplianceResult = Field(..., description="Final adjudicated result for this requirement")
    rationale: str = Field(..., min_length=5, description="Mandatory justification for reviewer decision/override")
    finding_id: Optional[str] = Field(None, description="Optional associated automated finding ID")


class ReviewerDecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    inspection_id: str
    finding_id: Optional[str] = None
    requirement_name: str
    reviewer_id: str
    determination: str
    original_result: Optional[str] = None
    adjudicated_result: str
    is_override: bool
    rationale: str
    rule_set_id: str
    rule_set_version: str
    evaluation_version: str
    created_at: datetime
    updated_at: datetime


class ReviewRevisionRequest(BaseModel):
    reason: str = Field(..., min_length=5, description="Primary reason why revision is requested")
    requested_changes: str = Field(..., min_length=5, description="Specific corrections or actions requested from inspector")


class EvidenceRequestCreate(BaseModel):
    requirement_name: str = Field(..., min_length=1, description="Target regulatory requirement")
    request_reason: str = Field(..., min_length=5, description="Why additional evidence is required")
    requested_condition: str = Field(..., min_length=5, description="What specific fact, panel, or condition needs to be established")
    requested_evidence_type: str = Field(default="SUPPLEMENTAL", description="Type of evidence requested")


class EvidenceRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    inspection_id: str
    reviewer_id: str
    requirement_name: str
    request_reason: str
    requested_condition: str
    requested_evidence_type: str
    status: str
    response_evidence_id: Optional[str] = None
    response_note: Optional[str] = None
    resolved_by_id: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class EvidenceRequestFulfillRequest(BaseModel):
    evidence_id: str = Field(..., description="ID of newly uploaded evidence asset fulfilling request")
    response_note: Optional[str] = Field(None, description="Optional note from inspector")


class FinalizeInspectionRequest(BaseModel):
    final_decision: FinalDecision = Field(..., description="Overall master legal decision (COMPLIANT, NON_COMPLIANCE_CONFIRMED, INCONCLUSIVE)")
    final_rationale: str = Field(..., min_length=5, description="Overall master finalization justification")


class FinalAuditRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    inspection_id: str
    finalized_by_id: str
    finalized_at: datetime
    final_decision: str
    final_rationale: str
    inspection_context_snapshot: Dict[str, Any]
    evidence_snapshot: List[Dict[str, Any]]
    declaration_snapshot: Dict[str, Any]
    applicability_snapshot: List[Dict[str, Any]]
    compliance_findings_snapshot: List[Dict[str, Any]]
    reviewer_decisions_snapshot: List[Dict[str, Any]]
    rule_set_id: str
    rule_set_version: str
    evaluation_version: str
    source_evidence_hashes: Dict[str, str]
    audit_metadata: Dict[str, Any]
    created_at: datetime


class ReviewQueueItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_number: str
    product_name: str
    origin_status: str
    status: str
    created_by_id: str
    inspector_name: Optional[str] = None
    submitted_at: Optional[datetime] = None
    findings_count: int = 0
    potential_violations_count: int = 0
    open_evidence_requests_count: int = 0
