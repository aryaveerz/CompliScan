"""
CompliScan LM — Shared Domain Contracts.

This package provides domain types, enums, states, constants, and shared schemas
shared between backend, worker, and testing layers. It contains contracts only,
not framework runtime, route handlers, or business execution logic.
"""

from shared.domain.states import (
    InspectionLifecycleState,
    ProcessingState,
    FinalizationStatus,
)
from shared.domain.enums import (
    UserRole,
    OriginStatus,
    EvidenceType,
    ComplianceResult,
    AuditEventType,
)
from shared.domain.constants import (
    MAX_EVIDENCE_SIZE_BYTES,
    ALLOWED_MIME_TYPES,
    ALLOWED_EXTENSIONS,
    ErrorCode,
)

__all__ = [
    "InspectionLifecycleState",
    "ProcessingState",
    "FinalizationStatus",
    "UserRole",
    "OriginStatus",
    "EvidenceType",
    "ComplianceResult",
    "AuditEventType",
    "MAX_EVIDENCE_SIZE_BYTES",
    "ALLOWED_MIME_TYPES",
    "ALLOWED_EXTENSIONS",
    "ErrorCode",
]
