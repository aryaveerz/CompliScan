"""
CompliScan LM — Controlled Constants & Error Codes.
"""

from enum import Enum

# File size and type constraints
MAX_EVIDENCE_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB
ALLOWED_MIME_TYPES: list[str] = [
    "image/jpeg",
    "image/png",
    "image/webp",
]
ALLOWED_EXTENSIONS: list[str] = [
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
]


class ErrorCode(str, Enum):
    """Controlled API and Domain Error Codes."""
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_LIFECYCLE_STATE = "INVALID_LIFECYCLE_STATE"
    
    # Evidence Specific Errors
    EVIDENCE_INVALID_MIME = "EVIDENCE_INVALID_MIME"
    EVIDENCE_TOO_LARGE = "EVIDENCE_TOO_LARGE"
    EVIDENCE_DECODE_FAILED = "EVIDENCE_DECODE_FAILED"
    EVIDENCE_IMMUTABLE = "EVIDENCE_IMMUTABLE"
    EVIDENCE_NOT_FOUND = "EVIDENCE_NOT_FOUND"
    
    # Inspection Specific Errors
    INSPECTION_NOT_FOUND = "INSPECTION_NOT_FOUND"
    INSPECTION_READ_ONLY = "INSPECTION_READ_ONLY"
    
    # Processing Errors
    PROCESSING_FAILED = "PROCESSING_FAILED"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
