"""
CompliScan LM — Image Quality Assessment Service.
Performs deterministic, lightweight screening of evidence images for downstream perception.
STRICTLY SEPARATED from legal evaluation and compliance determinations.
"""

import io
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from PIL import Image
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.config import settings
from backend.app.models.evidence import EvidenceAsset
from backend.app.models.image_quality import ImageQualityAssessment
from shared.domain.enums import (
    ImageQualityStatus,
    QualityReasonCode,
)
from shared.domain.constants import ALLOWED_MIME_TYPES


@dataclass
class ImageQualityMetrics:
    """Quantitative perception screening metrics."""
    width: int
    height: int
    total_pixels: int
    mime_type: str
    is_decoded: bool
    sharpness_score: Optional[float] = None
    brightness_score: Optional[float] = None
    contrast_score: Optional[float] = None


@dataclass
class ImageQualityResult:
    """Full result of an Image Quality Assessment evaluation."""
    quality_status: ImageQualityStatus
    assessment_version: str
    metrics: ImageQualityMetrics
    reason_codes: List[QualityReasonCode]
    details: Dict[str, Any] = field(default_factory=dict)


class ImageQualityService:
    """
    Deterministic Image Quality screening service.

    Evaluates:
    1. Decodability & MIME validity
    2. Dimensions & total resolution against minimum perception bounds
    3. Sharpness / Blur via discrete Laplacian variance
    4. Exposure & Blank image screening via luminance distribution
    """

    @classmethod
    def compute_laplacian_variance(cls, gray_array: np.ndarray) -> float:
        """
        Compute discrete 2D Laplacian operator variance on a 2D grayscale float array.
        Uses 3x3 discrete Laplacian kernel [[0, 1, 0], [1, -4, 1], [0, 1, 0]].
        Pure NumPy vectorization — deterministic and fast without OpenCV dependency.
        """
        if gray_array.ndim != 2 or gray_array.shape[0] < 3 or gray_array.shape[1] < 3:
            return 0.0

        # Discrete 2D convolution with 3x3 Laplacian kernel
        lap = (
            gray_array[:-2, 1:-1]
            + gray_array[2:, 1:-1]
            + gray_array[1:-1, :-2]
            + gray_array[1:-1, 2:]
            - 4.0 * gray_array[1:-1, 1:-1]
        )
        return float(np.var(lap))

    @classmethod
    def assess_image_bytes(
        cls,
        content: bytes,
        mime_type: str = "image/jpeg",
    ) -> ImageQualityResult:
        """
        Perform deterministic quality assessment on raw image bytes.
        Does not mutate input bytes.
        """
        version = settings.QUALITY_VERSION

        # 1. MIME Validation
        if mime_type not in ALLOWED_MIME_TYPES:
            return ImageQualityResult(
                quality_status=ImageQualityStatus.UNUSABLE,
                assessment_version=version,
                metrics=ImageQualityMetrics(
                    width=0,
                    height=0,
                    total_pixels=0,
                    mime_type=mime_type,
                    is_decoded=False,
                ),
                reason_codes=[QualityReasonCode.UNSUPPORTED_IMAGE_TYPE],
                details={
                    "error": f"Unsupported MIME type: {mime_type}",
                    "allowed_types": ALLOWED_MIME_TYPES,
                },
            )

        # 2. Decode Attempt
        try:
            image_stream = io.BytesIO(content)
            with Image.open(image_stream) as img:
                # Force load pixel data
                img.load()
                width, height = img.size
                format_name = img.format

                if width <= 0 or height <= 0:
                    return ImageQualityResult(
                        quality_status=ImageQualityStatus.UNUSABLE,
                        assessment_version=version,
                        metrics=ImageQualityMetrics(
                            width=width,
                            height=height,
                            total_pixels=0,
                            mime_type=mime_type,
                            is_decoded=True,
                        ),
                        reason_codes=[QualityReasonCode.INVALID_DIMENSIONS],
                        details={"error": "Image dimensions must be greater than zero"},
                    )

                # Convert to grayscale 2D float array for signal calculations
                gray_img = img.convert("L")
                gray_arr = np.array(gray_img, dtype=np.float64)

        except Exception as e:
            return ImageQualityResult(
                quality_status=ImageQualityStatus.UNUSABLE,
                assessment_version=version,
                metrics=ImageQualityMetrics(
                    width=0,
                    height=0,
                    total_pixels=0,
                    mime_type=mime_type,
                    is_decoded=False,
                ),
                reason_codes=[QualityReasonCode.IMAGE_DECODE_FAILED],
                details={"error": f"Failed to decode image: {str(e)}"},
            )

        # 3. Compute Quantitative Metrics
        total_pixels = width * height
        sharpness = cls.compute_laplacian_variance(gray_arr)
        brightness = float(np.mean(gray_arr))
        contrast = float(np.std(gray_arr))

        metrics = ImageQualityMetrics(
            width=width,
            height=height,
            total_pixels=total_pixels,
            mime_type=mime_type,
            is_decoded=True,
            sharpness_score=round(sharpness, 2),
            brightness_score=round(brightness, 2),
            contrast_score=round(contrast, 2),
        )

        # 4. Evaluate Thresholds (Precedence: settings override > canonical defaults)
        reasons: List[QualityReasonCode] = []
        checks_detail: Dict[str, Any] = {}

        # 4a. Resolution Check
        is_low_res = (
            width < settings.QUALITY_MIN_WIDTH
            or height < settings.QUALITY_MIN_HEIGHT
            or total_pixels < settings.QUALITY_MIN_PIXELS
        )
        checks_detail["resolution"] = {
            "width": width,
            "min_width": settings.QUALITY_MIN_WIDTH,
            "height": height,
            "min_height": settings.QUALITY_MIN_HEIGHT,
            "total_pixels": total_pixels,
            "min_pixels": settings.QUALITY_MIN_PIXELS,
            "passed": not is_low_res,
        }
        if is_low_res:
            reasons.append(QualityReasonCode.LOW_RESOLUTION)

        # 4b. Sharpness / Blur Check
        is_blurry = sharpness < settings.QUALITY_BLUR_THRESHOLD
        checks_detail["sharpness"] = {
            "measured_laplacian_variance": round(sharpness, 2),
            "threshold": settings.QUALITY_BLUR_THRESHOLD,
            "passed": not is_blurry,
        }
        if is_blurry:
            reasons.append(QualityReasonCode.EXCESSIVE_BLUR)

        # 4c. Exposure Check (Extreme Underexposure or Overexposure)
        is_extreme_exposure = (
            brightness < settings.QUALITY_MIN_BRIGHTNESS
            or brightness > settings.QUALITY_MAX_BRIGHTNESS
        )
        checks_detail["exposure"] = {
            "mean_luminance": round(brightness, 2),
            "min_threshold": settings.QUALITY_MIN_BRIGHTNESS,
            "max_threshold": settings.QUALITY_MAX_BRIGHTNESS,
            "passed": not is_extreme_exposure,
        }
        if is_extreme_exposure:
            reasons.append(QualityReasonCode.EXTREME_EXPOSURE)

        # 4d. Contrast / Blank Image Check
        is_blank = contrast < settings.QUALITY_MIN_CONTRAST
        checks_detail["contrast"] = {
            "std_luminance": round(contrast, 2),
            "min_contrast_threshold": settings.QUALITY_MIN_CONTRAST,
            "passed": not is_blank,
        }
        if is_blank:
            reasons.append(QualityReasonCode.NEAR_BLANK_IMAGE)

        # 5. Final Classification
        if not reasons:
            status = ImageQualityStatus.USABLE
            reasons = [QualityReasonCode.QUALITY_ACCEPTABLE]
        else:
            status = ImageQualityStatus.NEEDS_REVIEW

        details = {
            "format": format_name,
            "checks": checks_detail,
            "thresholds_applied": {
                "min_width": settings.QUALITY_MIN_WIDTH,
                "min_height": settings.QUALITY_MIN_HEIGHT,
                "min_pixels": settings.QUALITY_MIN_PIXELS,
                "blur_threshold": settings.QUALITY_BLUR_THRESHOLD,
                "min_brightness": settings.QUALITY_MIN_BRIGHTNESS,
                "max_brightness": settings.QUALITY_MAX_BRIGHTNESS,
                "min_contrast": settings.QUALITY_MIN_CONTRAST,
            },
        }

        return ImageQualityResult(
            quality_status=status,
            assessment_version=version,
            metrics=metrics,
            reason_codes=reasons,
            details=details,
        )

    @classmethod
    async def persist_assessment(
        cls,
        db: AsyncSession,
        evidence: EvidenceAsset,
        result: ImageQualityResult,
    ) -> ImageQualityAssessment:
        """
        Persist ImageQualityAssessment idempotently.
        If an assessment already exists for the evidence_id, it is updated in place.
        """
        stmt = select(ImageQualityAssessment).where(
            ImageQualityAssessment.evidence_id == evidence.id
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()

        now = datetime.now(timezone.utc)
        reason_codes_values = [r.value for r in result.reason_codes]

        if existing:
            existing.quality_status = result.quality_status.value
            existing.assessment_version = result.assessment_version
            existing.width = result.metrics.width
            existing.height = result.metrics.height
            existing.total_pixels = result.metrics.total_pixels
            existing.mime_type = result.metrics.mime_type
            existing.is_decoded = result.metrics.is_decoded
            existing.sharpness_score = result.metrics.sharpness_score
            existing.brightness_score = result.metrics.brightness_score
            existing.contrast_score = result.metrics.contrast_score
            existing.reason_codes = reason_codes_values
            existing.details = result.details
            existing.updated_at = now
            await db.flush()
            return existing

        assessment = ImageQualityAssessment(
            evidence_id=evidence.id,
            inspection_id=evidence.inspection_id,
            quality_status=result.quality_status.value,
            assessment_version=result.assessment_version,
            width=result.metrics.width,
            height=result.metrics.height,
            total_pixels=result.metrics.total_pixels,
            mime_type=result.metrics.mime_type,
            is_decoded=result.metrics.is_decoded,
            sharpness_score=result.metrics.sharpness_score,
            brightness_score=result.metrics.brightness_score,
            contrast_score=result.metrics.contrast_score,
            reason_codes=reason_codes_values,
            details=result.details,
            created_at=now,
            updated_at=now,
        )
        db.add(assessment)
        await db.flush()
        return assessment
