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

# ─────────────────────────────────────────────────────────────────────────────
# Image Quality Assessment — Canonical Engineering Defaults
#
# NOTE: These are technical engineering parameters designed to screen image
# suitability for downstream OCR/perception. They are NOT legal/statutory thresholds.
# ─────────────────────────────────────────────────────────────────────────────
QUALITY_ASSESSMENT_VERSION: str = "1.0.0"

# Minimum dimension parameters
QUALITY_MIN_WIDTH: int = 600
QUALITY_MIN_HEIGHT: int = 600
QUALITY_MIN_PIXELS: int = 400_000

# Sharpness / Blur parameter (Laplacian variance on grayscale image)
QUALITY_BLUR_THRESHOLD: float = 100.0

# Exposure parameters (Mean pixel luminance on 0-255 scale)
QUALITY_MIN_BRIGHTNESS: float = 25.0
QUALITY_MAX_BRIGHTNESS: float = 235.0

# Contrast / Uniformity parameter (Standard deviation of luminance)
QUALITY_MIN_CONTRAST: float = 15.0


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

    # Analysis & Job Specific Errors
    JOB_NOT_FOUND = "JOB_NOT_FOUND"
    JOB_EXECUTION_FAILED = "JOB_EXECUTION_FAILED"
    QUALITY_ASSESSMENT_NOT_FOUND = "QUALITY_ASSESSMENT_NOT_FOUND"

    # Processing Errors
    PROCESSING_FAILED = "PROCESSING_FAILED"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
