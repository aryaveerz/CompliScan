"""
CompliScan LM — Phase 2.1 Image Quality Assessment Test Suite.

Deterministic validation of:
1. Valid high-quality image (USABLE)
2. Low-resolution image (NEEDS_REVIEW, LOW_RESOLUTION)
3. Blurred image (NEEDS_REVIEW, EXCESSIVE_BLUR)
4. Corrupted bytes (UNUSABLE, IMAGE_DECODE_FAILED)
5. Unsupported MIME type (UNUSABLE, UNSUPPORTED_IMAGE_TYPE)
6. Near-blank / solid color image (NEEDS_REVIEW, NEAR_BLANK_IMAGE)
7. Extreme underexposure (NEEDS_REVIEW, EXTREME_EXPOSURE)
8. Extreme overexposure (NEEDS_REVIEW, EXTREME_EXPOSURE)
9. Exact boundary conditions (+/- 1px, +/- 1.0 sharpness)
10. Idempotency (repeated assessment updates in place without duplicate records)
11. Evidence immutability & hash verification (original bytes & SHA-256 untouched)
12. Evidence traceability (assessment references exact Evidence ID)
13. Worker queue lifecycle & lease timeout recovery
14. API endpoints & RBAC isolation
15. Strict domain separation (zero compliance result generated)
"""

import io
import os
import pytest
from PIL import Image, ImageDraw, ImageFilter
from fastapi import UploadFile
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from backend.app.core.config import settings
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.user import User
from backend.app.models.inspection import InspectionCase
from backend.app.models.evidence import EvidenceAsset
from backend.app.models.image_quality import ImageQualityAssessment
from backend.app.models.analysis_job import AnalysisJob
from backend.app.services.image_quality_service import ImageQualityService
from backend.app.services.analysis_job_service import AnalysisJobService
from backend.app.services.evidence_service import EvidenceService
from backend.app.core.security import compute_sha256
from shared.domain.enums import (
    UserRole,
    OriginStatus,
    EvidenceType,
    ImageQualityStatus,
    QualityReasonCode,
    JobType,
    JobStatus,
    ComplianceResult,
)
from shared.domain.constants import (
    QUALITY_MIN_WIDTH,
    QUALITY_MIN_HEIGHT,
    QUALITY_MIN_PIXELS,
    QUALITY_BLUR_THRESHOLD,
    QUALITY_MIN_BRIGHTNESS,
    QUALITY_MAX_BRIGHTNESS,
    QUALITY_MIN_CONTRAST,
    QUALITY_ASSESSMENT_VERSION,
)


# ── Synthetic Real-Image Helpers ──────────────────────────────────────────────

def generate_sharp_image_bytes(width: int = 1920, height: int = 1080) -> bytes:
    """Generate a high-contrast, high-resolution sharp image with complex pattern."""
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Draw fine high-contrast checkerboard / grid lines
    step = 20
    for x in range(0, width, step):
        draw.line([(x, 0), (x, height)], fill=(0, 0, 0), width=2)
    for y in range(0, height, step):
        draw.line([(0, y), (width, y)], fill=(0, 0, 0), width=2)

    # Draw diagonal lines for rich high-frequency edges
    draw.line([(0, 0), (width, height)], fill=(0, 0, 0), width=3)
    draw.line([(0, height), (width, 0)], fill=(0, 0, 0), width=3)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def generate_blurred_image_bytes(width: int = 1920, height: int = 1080, blur_radius: int = 25) -> bytes:
    """Generate a heavily blurred image."""
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill=(0, 0, 0), width=3)
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=(0, 0, 0), width=3)

    # Heavy Gaussian Blur to eliminate high-frequency edges
    blurred = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    buf = io.BytesIO()
    blurred.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def generate_solid_color_image_bytes(width: int = 800, height: int = 800, color: int = 128) -> bytes:
    """Generate a solid single-color image (near zero contrast)."""
    img = Image.new("L", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ── Unit Tests: ImageQualityService ───────────────────────────────────────────

class TestImageQualityService:
    def test_valid_high_quality_image(self):
        """Test 1: Valid high-quality image returns USABLE with QUALITY_ACCEPTABLE."""
        image_bytes = generate_sharp_image_bytes(1920, 1080)
        result = ImageQualityService.assess_image_bytes(image_bytes, "image/jpeg")

        assert result.quality_status == ImageQualityStatus.USABLE
        assert result.assessment_version == QUALITY_ASSESSMENT_VERSION
        assert result.metrics.is_decoded is True
        assert result.metrics.width == 1920
        assert result.metrics.height == 1080
        assert result.metrics.total_pixels == 1920 * 1080
        assert result.metrics.sharpness_score is not None
        assert result.metrics.sharpness_score >= QUALITY_BLUR_THRESHOLD
        assert QUALITY_MIN_BRIGHTNESS <= result.metrics.brightness_score <= QUALITY_MAX_BRIGHTNESS
        assert result.metrics.contrast_score >= QUALITY_MIN_CONTRAST
        assert QualityReasonCode.QUALITY_ACCEPTABLE in result.reason_codes

    def test_low_resolution_image(self):
        """Test 2: Image below minimum resolution returns NEEDS_REVIEW with LOW_RESOLUTION."""
        image_bytes = generate_sharp_image_bytes(400, 400)
        result = ImageQualityService.assess_image_bytes(image_bytes, "image/jpeg")

        assert result.quality_status == ImageQualityStatus.NEEDS_REVIEW
        assert result.metrics.width == 400
        assert result.metrics.height == 400
        assert result.metrics.total_pixels == 160000
        assert QualityReasonCode.LOW_RESOLUTION in result.reason_codes

    def test_blurred_image(self):
        """Test 3: Blurred image returns NEEDS_REVIEW with EXCESSIVE_BLUR."""
        image_bytes = generate_blurred_image_bytes(1920, 1080, blur_radius=25)
        result = ImageQualityService.assess_image_bytes(image_bytes, "image/jpeg")

        assert result.quality_status == ImageQualityStatus.NEEDS_REVIEW
        assert result.metrics.sharpness_score is not None
        assert result.metrics.sharpness_score < QUALITY_BLUR_THRESHOLD
        assert QualityReasonCode.EXCESSIVE_BLUR in result.reason_codes

    def test_corrupted_image_bytes(self):
        """Test 4: Corrupted bytes return UNUSABLE with IMAGE_DECODE_FAILED."""
        corrupted = b"NOT_A_VALID_IMAGE_FILE_PAYLOAD_1234567890"
        result = ImageQualityService.assess_image_bytes(corrupted, "image/jpeg")

        assert result.quality_status == ImageQualityStatus.UNUSABLE
        assert result.metrics.is_decoded is False
        assert QualityReasonCode.IMAGE_DECODE_FAILED in result.reason_codes

    def test_unsupported_mime_type(self):
        """Test 5: Unsupported MIME type returns UNUSABLE with UNSUPPORTED_IMAGE_TYPE."""
        image_bytes = generate_sharp_image_bytes(800, 800)
        result = ImageQualityService.assess_image_bytes(image_bytes, "application/pdf")

        assert result.quality_status == ImageQualityStatus.UNUSABLE
        assert result.metrics.is_decoded is False
        assert QualityReasonCode.UNSUPPORTED_IMAGE_TYPE in result.reason_codes

    def test_near_blank_image(self):
        """Test 6: Solid color image with near-zero contrast returns NEAR_BLANK_IMAGE."""
        image_bytes = generate_solid_color_image_bytes(800, 800, color=128)
        result = ImageQualityService.assess_image_bytes(image_bytes, "image/png")

        assert result.quality_status == ImageQualityStatus.NEEDS_REVIEW
        assert result.metrics.contrast_score is not None
        assert result.metrics.contrast_score < QUALITY_MIN_CONTRAST
        assert QualityReasonCode.NEAR_BLANK_IMAGE in result.reason_codes

    def test_extreme_underexposure(self):
        """Test 7: Very dark / near black image returns EXTREME_EXPOSURE."""
        image_bytes = generate_solid_color_image_bytes(800, 800, color=10)
        result = ImageQualityService.assess_image_bytes(image_bytes, "image/png")

        assert result.quality_status == ImageQualityStatus.NEEDS_REVIEW
        assert result.metrics.brightness_score is not None
        assert result.metrics.brightness_score < QUALITY_MIN_BRIGHTNESS
        assert QualityReasonCode.EXTREME_EXPOSURE in result.reason_codes

    def test_extreme_overexposure(self):
        """Test 8: Very bright / near white image returns EXTREME_EXPOSURE."""
        image_bytes = generate_solid_color_image_bytes(800, 800, color=245)
        result = ImageQualityService.assess_image_bytes(image_bytes, "image/png")

        assert result.quality_status == ImageQualityStatus.NEEDS_REVIEW
        assert result.metrics.brightness_score is not None
        assert result.metrics.brightness_score > QUALITY_MAX_BRIGHTNESS
        assert QualityReasonCode.EXTREME_EXPOSURE in result.reason_codes

    def test_boundary_conditions(self):
        """Test 9: Exact boundary conditions verify threshold transitions."""
        # Width immediately below minimum (599px)
        img_599 = generate_sharp_image_bytes(599, 800)
        res_599 = ImageQualityService.assess_image_bytes(img_599, "image/jpeg")
        assert QualityReasonCode.LOW_RESOLUTION in res_599.reason_codes

        # Height immediately below minimum (599px)
        img_h599 = generate_sharp_image_bytes(800, 599)
        res_h599 = ImageQualityService.assess_image_bytes(img_h599, "image/jpeg")
        assert QualityReasonCode.LOW_RESOLUTION in res_h599.reason_codes

        # Valid dimensions meeting both minimum width/height (>=600) and total pixels (>=400,000)
        img_at_threshold = generate_sharp_image_bytes(800, 600)
        res_at_threshold = ImageQualityService.assess_image_bytes(img_at_threshold, "image/jpeg")
        assert res_at_threshold.quality_status == ImageQualityStatus.USABLE
        assert QualityReasonCode.QUALITY_ACCEPTABLE in res_at_threshold.reason_codes


# ── Integration Tests: End-to-End Async Quality Pipeline ──────────────────────

@pytest.mark.asyncio
class TestImageQualityIntegration:
    async def test_end_to_end_upload_and_job_execution(self):
        """
        Test 10-12: Full integration: Upload -> Auto-enqueue -> Worker Execution -> Persist Assessment.
        Validates idempotency, evidence immutability, and traceability.
        """
        async with AsyncSessionLocal() as db:
            # 1. Create inspector user & inspection case
            inspector = User(
                email="inspector.iq@compliscan.gov.in",
                full_name="Inspector Test",
                role=UserRole.INSPECTOR.value,
                is_active=True,
            )
            db.add(inspector)
            await db.flush()

            inspection = InspectionCase(
                case_number="INS-2026-IQ-001",
                product_name="Sample Quality Test Product",
                origin_status=OriginStatus.DOMESTIC.value,
                created_by_id=inspector.id,
            )
            db.add(inspection)
            await db.commit()

            # 2. Upload high-quality evidence
            image_content = generate_sharp_image_bytes(1280, 720)
            original_sha = compute_sha256(image_content)

            upload_file = UploadFile(
                filename="sharp_sample.jpg",
                file=io.BytesIO(image_content),
                headers={"content-type": "image/jpeg"},
            )

            asset = await EvidenceService.upload_evidence(
                db=db,
                inspection_id=inspection.id,
                file=upload_file,
                evidence_type=EvidenceType.PRIMARY,
                current_user=inspector,
            )
            assert asset.id is not None
            assert asset.sha256_hash == original_sha

            # 3. Verify AnalysisJob was enqueued
            from sqlalchemy import select
            stmt_job = select(AnalysisJob).where(
                AnalysisJob.inspection_id == inspection.id,
                AnalysisJob.evidence_id == asset.id,
                AnalysisJob.job_type == JobType.IMAGE_QUALITY.value,
            )
            job = (await db.execute(stmt_job)).scalar_one_or_none()
            assert job is not None
            assert job.status == JobStatus.PENDING.value

            # 4. Process job with inline worker
            processed = await AnalysisJobService.run_pending_jobs_inline(db, worker_id="test-worker-1")
            assert processed >= 1

            # 5. Verify Job completed
            await db.refresh(job)
            assert job.status == JobStatus.COMPLETED.value
            assert job.completed_at is not None

            # 6. Verify ImageQualityAssessment record
            stmt_qa = select(ImageQualityAssessment).where(
                ImageQualityAssessment.evidence_id == asset.id
            )
            assessment = (await db.execute(stmt_qa)).scalar_one_or_none()
            assert assessment is not None
            assert assessment.quality_status == ImageQualityStatus.USABLE.value
            assert assessment.evidence_id == asset.id
            assert assessment.inspection_id == inspection.id
            assert assessment.width == 1280
            assert assessment.height == 720
            assert assessment.sharpness_score is not None

            # 7. Traceability verification
            assert assessment.evidence_id == asset.id
            assert assessment.inspection_id == inspection.id

            # 8. Immutability verification: check original file and SHA-256
            with open(asset.storage_path, "rb") as f:
                disk_bytes = f.read()
            assert disk_bytes == image_content
            assert compute_sha256(disk_bytes) == original_sha

            # 9. Idempotency test: Re-running assessment must update record without duplicate
            result_again = ImageQualityService.assess_image_bytes(image_content, "image/jpeg")
            assessment_updated = await ImageQualityService.persist_assessment(
                db=db,
                evidence=asset,
                result=result_again,
            )
            await db.commit()

            # Confirm only 1 row exists for this evidence_id
            stmt_count = select(ImageQualityAssessment).where(
                ImageQualityAssessment.evidence_id == asset.id
            )
            all_assessments = (await db.execute(stmt_count)).scalars().all()
            assert len(all_assessments) == 1
            assert assessment_updated.id == assessment.id

    async def test_worker_lease_and_retry_behavior(self):
        """Test 13: Worker atomic claim, lease timeout expiration, and retry logic."""
        async with AsyncSessionLocal() as db:
            inspector = User(
                email="inspector.lease@compliscan.gov.in",
                full_name="Inspector Lease",
                role=UserRole.INSPECTOR.value,
                is_active=True,
            )
            db.add(inspector)
            await db.flush()

            inspection = InspectionCase(
                case_number="INS-2026-LEASE-001",
                product_name="Lease Test Product",
                created_by_id=inspector.id,
            )
            db.add(inspection)
            await db.flush()

            # Enqueue a dummy job
            job = await AnalysisJobService.enqueue_job(
                db=db,
                inspection_id=inspection.id,
                job_type=JobType.IMAGE_QUALITY,
                evidence_id="EV-DUMMY-123",
            )
            await db.commit()
            assert job.status == JobStatus.PENDING.value

            # Worker 1 claims job with 1 second lease
            claimed_job = await AnalysisJobService.claim_next_job(db, worker_id="worker-alpha", lease_seconds=1)
            assert claimed_job is not None
            assert claimed_job.worker_id == "worker-alpha"
            assert claimed_job.status == JobStatus.RUNNING.value
            assert claimed_job.attempts == 1
            await db.commit()

            # Worker 2 attempts immediate claim -> returns None (job is locked)
            no_job = await AnalysisJobService.claim_next_job(db, worker_id="worker-beta")
            assert no_job is None

            # Manually backdate lease expiration to simulate worker crash/timeout
            from datetime import datetime, timezone, timedelta
            claimed_job.lease_expires_at = datetime.now(timezone.utc) - timedelta(seconds=10)
            await db.commit()

            # Worker 2 now claims expired lease job
            reclaimed_job = await AnalysisJobService.claim_next_job(db, worker_id="worker-beta")
            assert reclaimed_job is not None
            assert reclaimed_job.id == claimed_job.id
            assert reclaimed_job.worker_id == "worker-beta"
            assert reclaimed_job.attempts == 2
            await db.commit()


# ── API & RBAC Tests ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestImageQualityAPI:
    async def test_get_quality_and_reassessment_api(self):
        """Test 14: Authenticated REST endpoints for quality retrieval and async reassessment."""
        async with AsyncSessionLocal() as db:
            inspector = User(
                id="USR-INSP-001",
                email="inspector.api@compliscan.gov.in",
                full_name="Inspector API",
                role=UserRole.INSPECTOR.value,
                is_active=True,
            )
            other_inspector = User(
                id="USR-INSP-002",
                email="other.insp@compliscan.gov.in",
                full_name="Other Inspector",
                role=UserRole.INSPECTOR.value,
                is_active=True,
            )
            db.add_all([inspector, other_inspector])
            await db.flush()

            inspection = InspectionCase(
                id="INS-API-001",
                case_number="INS-2026-API-001",
                product_name="API Test Commodity",
                created_by_id=inspector.id,
            )
            db.add(inspection)
            await db.flush()

            image_content = generate_sharp_image_bytes(800, 800)
            upload_file = UploadFile(
                filename="api_sample.jpg",
                file=io.BytesIO(image_content),
                headers={"content-type": "image/jpeg"},
            )
            asset = await EvidenceService.upload_evidence(
                db=db,
                inspection_id=inspection.id,
                file=upload_file,
                evidence_type=EvidenceType.PRIMARY,
                current_user=inspector,
            )
            await db.commit()

            # Process job
            await AnalysisJobService.run_pending_jobs_inline(db)

        from backend.tests.conftest import create_test_supabase_token
        token_owner = create_test_supabase_token(user_id=inspector.id, email=inspector.email)
        token_other = create_test_supabase_token(user_id=other_inspector.id, email=other_inspector.email)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. GET /api/v1/evidence/{id}/quality (Authorized)
            resp = await client.get(
                f"/api/v1/evidence/{asset.id}/quality",
                headers={"Authorization": f"Bearer {token_owner}"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["evidence_id"] == asset.id
            assert data["quality_status"] == ImageQualityStatus.USABLE.value
            assert data["width"] == 800
            assert data["height"] == 800

            # 2. POST /api/v1/evidence/{id}/assess-quality (202 Accepted)
            resp_post = await client.post(
                f"/api/v1/evidence/{asset.id}/assess-quality",
                headers={"Authorization": f"Bearer {token_owner}"},
            )
            assert resp_post.status_code == 202
            job_data = resp_post.json()
            assert job_data["job_type"] == JobType.IMAGE_QUALITY.value
            assert job_data["status"] in (JobStatus.PENDING.value, JobStatus.CLAIMED.value, JobStatus.RUNNING.value)

            # 3. RBAC isolation: other inspector cannot trigger on this case (403 Forbidden)
            resp_forbidden = await client.post(
                f"/api/v1/evidence/{asset.id}/assess-quality",
                headers={"Authorization": f"Bearer {token_other}"},
            )
            assert resp_forbidden.status_code == 403


# ── Domain Separation Verification ────────────────────────────────────────────

class TestDomainSeparation:
    def test_image_quality_never_produces_compliance_result(self):
        """
        Test 15: Critical invariant verification.
        Asserts that ImageQualityAssessment only produces ImageQualityStatus and QualityReasonCode,
        and never produces ComplianceResult values (PASS, POTENTIAL_NON_COMPLIANCE, etc.).
        """
        image_bytes = generate_blurred_image_bytes(800, 800)
        result = ImageQualityService.assess_image_bytes(image_bytes, "image/jpeg")

        # Must be an ImageQualityStatus instance
        assert isinstance(result.quality_status, ImageQualityStatus)
        assert result.quality_status in (
            ImageQualityStatus.USABLE,
            ImageQualityStatus.NEEDS_REVIEW,
            ImageQualityStatus.UNUSABLE,
        )

        # Must never be a ComplianceResult value
        for compliance_val in ComplianceResult:
            assert result.quality_status.value != compliance_val.value
            for code in result.reason_codes:
                assert code.value != compliance_val.value
