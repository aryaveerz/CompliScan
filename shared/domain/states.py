"""
CompliScan LM — Lifecycle and Operational States.

Defines the master lifecycle sequence, processing states, and finalization flags.
Backend is authoritative for all state transitions.
"""

from enum import Enum


class InspectionLifecycleState(str, Enum):
    """
    Master 9-stage lifecycle sequence for InspectionCase.
    Follows:
    DRAFT → EVIDENCE_UPLOADED → EXTRACTED → APPLICABILITY_EVALUATED →
    EVALUATED → IN_VERIFICATION → SUBMITTED_FOR_REVIEW → REQUIRES_REVISION → FINALIZED
    """
    DRAFT = "DRAFT"
    EVIDENCE_UPLOADED = "EVIDENCE_UPLOADED"
    EXTRACTED = "EXTRACTED"
    APPLICABILITY_EVALUATED = "APPLICABILITY_EVALUATED"
    EVALUATED = "EVALUATED"
    IN_VERIFICATION = "IN_VERIFICATION"
    SUBMITTED_FOR_REVIEW = "SUBMITTED_FOR_REVIEW"
    REQUIRES_REVISION = "REQUIRES_REVISION"
    FINALIZED = "FINALIZED"


class ProcessingState(str, Enum):
    """Asynchronous technical processing state."""
    IDLE = "IDLE"
    PROCESSING = "PROCESSING"
    FAILED = "FAILED"


class FinalizationStatus(str, Enum):
    """Immutable finalization lock."""
    UNFINALIZED = "UNFINALIZED"
    READ_ONLY = "READ_ONLY"
