"""
CompliScan LM — Declaration Validation Schemas.
Deterministic models for date extraction, derivation, reconciliation, and temporal validation.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DateType(str, Enum):
    MANUFACTURE_DATE = "MANUFACTURE_DATE"
    PACKING_DATE = "PACKING_DATE"
    EXPIRY_DATE = "EXPIRY_DATE"
    BEST_BEFORE_DATE = "BEST_BEFORE_DATE"
    BEST_BEFORE_DURATION = "BEST_BEFORE_DURATION"
    BATCH_DATE = "BATCH_DATE"
    OTHER_DATE = "OTHER_DATE"


class DateObservationStatus(str, Enum):
    OBSERVED = "OBSERVED"
    DERIVED = "DERIVED"
    INFERRED = "INFERRED"
    MISSING = "MISSING"
    INVALID = "INVALID"
    CONFLICTING = "CONFLICTING"
    AMBIGUOUS = "AMBIGUOUS"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"


class TemporalValidationResult(str, Enum):
    PAST = "PAST"
    CURRENT = "CURRENT"
    FUTURE = "FUTURE"
    SAME_DATE = "SAME_DATE"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class DateObservationRecord(BaseModel):
    field_name: str
    raw_text: str
    normalized_date: Optional[str] = None  # YYYY-MM-DD or YYYY-MM
    date_type: DateType = DateType.OTHER_DATE
    observation_status: DateObservationStatus = DateObservationStatus.OBSERVED
    evidence_id: Optional[str] = None
    ocr_result_id: Optional[str] = None
    ocr_token_ids: List[int] = Field(default_factory=list)
    confidence: Optional[float] = None
    extraction_method: str = "DETERMINISTIC_REGEX_PARSER"
    extraction_version: str = "v1.0"
    derivation_method: Optional[str] = None
    source_observations: List[Dict[str, Any]] = Field(default_factory=list)


class DateConflictRecord(BaseModel):
    conflict_type: str = "DATE_DECLARATION_CONFLICT"
    observation_a: Dict[str, Any]
    observation_b: Dict[str, Any]
    evidence_ids: List[str] = Field(default_factory=list)
    ocr_token_ids: List[int] = Field(default_factory=list)
    calculation_method: Optional[str] = None
    conflict_status: str = "REQUIRES_REVIEW"
    validation_timestamp: str
    reason: str


class TemporalEvaluationRecord(BaseModel):
    validation_type: str = "EXPIRY_DATE_STATUS"
    observed_date: Optional[str] = None
    reference_date: str  # Inspection date YYYY-MM-DD
    comparison_operator: str = "<"  # "<", "==", ">"
    result: TemporalValidationResult = TemporalValidationResult.UNKNOWN
    evaluation_version: str = "v1.0"
    is_past_expiry: bool = False
    details: Optional[str] = None


class ScopeIntegrityResult(BaseModel):
    inspection_id: str
    is_isolated: bool = True
    violating_evidence_ids: List[str] = Field(default_factory=list)
    violating_token_maps: Dict[str, List[int]] = Field(default_factory=dict)
    notes: List[str] = Field(default_factory=list)


class DeclarationValidationSummary(BaseModel):
    inspection_id: str
    validation_engine_version: str = "v1.0"
    evaluated_at: str
    inspection_date_used: str
    date_observations: List[DateObservationRecord] = Field(default_factory=list)
    derived_dates: List[DateObservationRecord] = Field(default_factory=list)
    conflicts: List[DateConflictRecord] = Field(default_factory=list)
    temporal_validations: List[TemporalEvaluationRecord] = Field(default_factory=list)
    scope_integrity: ScopeIntegrityResult
    overall_validation_status: str = "VALID"
    statutory_finding_recommendation: Optional[str] = None
    notes: List[str] = Field(default_factory=list)
