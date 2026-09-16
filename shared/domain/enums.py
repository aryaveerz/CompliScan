"""
CompliScan LM — Controlled Enumerations.
"""

from enum import Enum


class UserRole(str, Enum):
    """Operational inspection roles."""
    INSPECTOR = "INSPECTOR"
    REVIEWER = "REVIEWER"


class OriginStatus(str, Enum):
    """
    Origin Status feeding applicability.
    - DOMESTIC: Manufactured/packed domestically in India
    - IMPORTED: Imported from abroad (triggers Rule 6(1)(b) Country of Origin check)
    - UNKNOWN: Origin cannot be determined at creation time
    """
    DOMESTIC = "DOMESTIC"
    IMPORTED = "IMPORTED"
    UNKNOWN = "UNKNOWN"


class EvidenceType(str, Enum):
    """Classification of evidence artifacts."""
    PRIMARY = "PRIMARY"          # Original uploaded package / label image
    DERIVED = "DERIVED"          # OCR token, crop, or canvas overlay artifact
    SUPPLEMENTAL = "SUPPLEMENTAL"# Supplementary evidence uploaded upon request


class ComplianceResult(str, Enum):
    """
    Strict 6-value result vocabulary.
    Must never be conflated with confidence scores or processing errors.
    """
    PASS = "PASS"
    POTENTIAL_NON_COMPLIANCE = "POTENTIAL_NON_COMPLIANCE"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    INCOMPLETE = "INCOMPLETE"
    PROCESSING_FAILED = "PROCESSING_FAILED"


class AuditEventType(str, Enum):
    """Discrete system and human audit log events."""
    INSPECTION_CREATED = "INSPECTION_CREATED"
    PRODUCT_CONTEXT_UPDATED = "PRODUCT_CONTEXT_UPDATED"
    EVIDENCE_UPLOADED = "EVIDENCE_UPLOADED"
    EVIDENCE_DELETED = "EVIDENCE_DELETED"
    EVIDENCE_ACCEPTED = "EVIDENCE_ACCEPTED"
    STATUS_TRANSITION = "STATUS_TRANSITION"
    DECLARATION_CORRECTED = "DECLARATION_CORRECTED"
    VERIFICATION_SUBMITTED = "VERIFICATION_SUBMITTED"
    REVIEWER_DETERMINATION = "REVIEWER_DETERMINATION"
    INSPECTION_FINALIZED = "INSPECTION_FINALIZED"
