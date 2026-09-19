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
    Must never be conflated with confidence scores, image quality, or processing errors.
    """
    PASS = "PASS"
    POTENTIAL_NON_COMPLIANCE = "POTENTIAL_NON_COMPLIANCE"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    INCOMPLETE = "INCOMPLETE"
    PROCESSING_FAILED = "PROCESSING_FAILED"


class ImageQualityStatus(str, Enum):
    """
    Technical engineering classification of image suitability for downstream perception/OCR.
    STRICTLY SEPARATE from ComplianceResult and legal evaluation.
    """
    USABLE = "USABLE"              # Technically suitable for downstream perception
    NEEDS_REVIEW = "NEEDS_REVIEW"  # Technical limitations flagged (e.g. low resolution, blur, exposure)
    UNUSABLE = "UNUSABLE"          # Fatal technical failure (e.g. decode failure, zero dimensions)


class QualityReasonCode(str, Enum):
    """Structured engineering reason codes for Image Quality Assessment."""
    QUALITY_ACCEPTABLE = "QUALITY_ACCEPTABLE"
    IMAGE_DECODE_FAILED = "IMAGE_DECODE_FAILED"
    UNSUPPORTED_IMAGE_TYPE = "UNSUPPORTED_IMAGE_TYPE"
    INVALID_DIMENSIONS = "INVALID_DIMENSIONS"
    LOW_RESOLUTION = "LOW_RESOLUTION"
    EXCESSIVE_BLUR = "EXCESSIVE_BLUR"
    NEAR_BLANK_IMAGE = "NEAR_BLANK_IMAGE"
    EXTREME_EXPOSURE = "EXTREME_EXPOSURE"


class JobType(str, Enum):
    """Asynchronous analysis job types."""
    IMAGE_QUALITY = "IMAGE_QUALITY"
    PERCEPTION = "PERCEPTION"
    EXTRACTION = "EXTRACTION"
    EVALUATION = "EVALUATION"


class JobStatus(str, Enum):
    """Durable analysis job execution state."""
    PENDING = "PENDING"
    CLAIMED = "CLAIMED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ObservationStatus(str, Enum):
    """
    Purely perceptual status of a declaration in evidence OCR tokens.
    STRICTLY SEPARATE from legal applicability and compliance evaluation.
    """
    OBSERVED = "OBSERVED"
    NOT_OBSERVED = "NOT_OBSERVED"
    AMBIGUOUS = "AMBIGUOUS"
    CONFLICTING = "CONFLICTING"
    UNREADABLE = "UNREADABLE"


class ApplicabilityStatus(str, Enum):
    """
    Evaluation of statutory rule applicability.
    STRICTLY SEPARATE from perception observation status and final compliance determination.
    """
    APPLICABLE = "APPLICABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"


class EvidenceRequestStatus(str, Enum):
    """Status of an explicit Evidence Request from Reviewer."""
    OPEN = "OPEN"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"


class ReviewerDeterminationType(str, Enum):
    """Reviewer judgment on a specific requirement or inspection."""
    CONFIRMED = "CONFIRMED"
    OVERRIDDEN = "OVERRIDDEN"
    REVISION_REQUESTED = "REVISION_REQUESTED"
    EVIDENCE_REQUESTED = "EVIDENCE_REQUESTED"


class FinalDecision(str, Enum):
    """Authoritative legal inspection determination recorded upon finalization."""
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANCE_CONFIRMED"
    INCONCLUSIVE = "INCONCLUSIVE"


class AuditEventType(str, Enum):
    """Discrete system and human audit log events."""
    INSPECTION_CREATED = "INSPECTION_CREATED"
    PRODUCT_CONTEXT_UPDATED = "PRODUCT_CONTEXT_UPDATED"
    EVIDENCE_UPLOADED = "EVIDENCE_UPLOADED"
    EVIDENCE_DELETED = "EVIDENCE_DELETED"
    EVIDENCE_ACCEPTED = "EVIDENCE_ACCEPTED"
    IMAGE_QUALITY_ASSESSED = "IMAGE_QUALITY_ASSESSED"
    OCR_PROCESSED = "OCR_PROCESSED"
    DECLARATIONS_EXTRACTED = "DECLARATIONS_EXTRACTED"
    APPLICABILITY_EVALUATED = "APPLICABILITY_EVALUATED"
    COMPLIANCE_EVALUATED = "COMPLIANCE_EVALUATED"
    STATUS_TRANSITION = "STATUS_TRANSITION"
    DECLARATION_CORRECTED = "DECLARATION_CORRECTED"
    DECLARATION_MANUALLY_CORRECTED = "DECLARATION_MANUALLY_CORRECTED"
    MANUAL_OBSERVATION_RECORDED = "MANUAL_OBSERVATION_RECORDED"
    VERIFICATION_SUBMITTED = "VERIFICATION_SUBMITTED"
    INSPECTION_SUBMITTED_FOR_REVIEW = "INSPECTION_SUBMITTED_FOR_REVIEW"
    REVIEW_REVISION_REQUESTED = "REVIEW_REVISION_REQUESTED"
    REVIEWER_DECISION_RECORDED = "REVIEWER_DECISION_RECORDED"
    REVIEWER_OVERRIDE_RECORDED = "REVIEWER_OVERRIDE_RECORDED"
    EVIDENCE_REQUEST_CREATED = "EVIDENCE_REQUEST_CREATED"
    EVIDENCE_REQUEST_FULFILLED = "EVIDENCE_REQUEST_FULFILLED"
    INSPECTION_FINALIZED = "INSPECTION_FINALIZED"
    REPORT_DOWNLOADED = "REPORT_DOWNLOADED"
    REPOSITORY_ACCESSED = "REPOSITORY_ACCESSED"
