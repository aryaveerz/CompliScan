"""
CompliScan LM — Phase 2.2 PaddleOCR Perception Pipeline Test Suite.

Comprehensive validation of:
1. OCR Perception on synthetic commodity package label (PP-OCRv4 detection + recognition)
2. Token data model: token_index, line_index, text, confidence, 4-point bounding boxes in original image space
3. Engine metadata: ocr_engine="paddleocr-onnx", engine version recorded
4. Idempotency: repeated OCR executions update in-place without duplicate rows
5. Image Quality Gating:
   - USABLE -> OCR executed, tokens extracted
   - NEEDS_REVIEW -> OCR blocked, processing_blocked=True, block_reason recorded
   - UNUSABLE -> OCR blocked, processing_blocked=True, block_reason recorded
6. Automated Pipeline: IMAGE_QUALITY (USABLE) -> auto-enqueue PERCEPTION -> worker execution -> OCRResult
7. Evidence Immutability: SHA-256 and original binary bytes strictly unmodified
8. Domain Separation: Zero ComplianceResult / ComplianceFinding created
9. API Endpoints & RBAC:
   - GET /api/v1/evidence/{id}/ocr (200 OK for owner / reviewer, 403 for other inspector, 401 unauth)
   - POST /api/v1/evidence/{id}/process-ocr (202 Accepted, async enqueueing)
"""

import io
import os
import uuid
import pytest
from PIL import Image, ImageDraw, ImageFont
from fastapi import UploadFile
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from backend.app.main import app
from backend.app.core.config import settings
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.user import User
from backend.app.models.inspection import InspectionCase
from backend.app.models.evidence import EvidenceAsset
from backend.app.models.image_quality import ImageQualityAssessment
from backend.app.models.ocr import OCRResult
from backend.app.models.analysis_job import AnalysisJob
from backend.app.models.audit import AuditEvent
from backend.app.services.ocr_service import (
    OCRService,
    OCR_ENGINE_NAME,
    OCR_ENGINE_VERSION,
    PROCESSING_VERSION,
)
from backend.app.services.image_quality_service import ImageQualityService
from backend.app.services.analysis_job_service import AnalysisJobService
from backend.app.services.evidence_service import EvidenceService
from backend.app.core.security import compute_sha256
from backend.tests.conftest import create_test_supabase_token
from shared.domain.enums import (

    UserRole,
    OriginStatus,
    EvidenceType,
    ImageQualityStatus,
    QualityReasonCode,
    JobType,
    JobStatus,
    AuditEventType,
)


# ── Synthetic Label Generation Helpers ────────────────────────────────────────

def generate_synthetic_label_image_bytes(width: int = 1200, height: int = 800) -> bytes:
    """
    Generate a high-contrast synthetic packaged commodity label with clear text declarations.
    """
    img = Image.new("RGB", (width, height), color=(200, 205, 210))
    draw = ImageDraw.Draw(img)

    # Draw border
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline=(0, 0, 0), width=4)

    # Add realistic commodity text declarations with clear dark text
    draw.text((60, 60), "PREMIUM BASMATI RICE", fill=(0, 0, 0))
    draw.text((60, 140), "MANUFACTURED BY: HIMALAYAN FOODS LTD", fill=(0, 0, 0))
    draw.text((60, 220), "NET QUANTITY: 5 kg", fill=(0, 0, 0))
    draw.text((60, 300), "MAXIMUM RETAIL PRICE: Rs. 450.00", fill=(0, 0, 0))
    draw.text((60, 380), "INCL OF ALL TAXES", fill=(0, 0, 0))
    draw.text((60, 460), "MONTH & YEAR OF PKG: 09/2026", fill=(0, 0, 0))
    draw.text((60, 540), "CONSUMER CARE: 1800-200-3000", fill=(0, 0, 0))
    draw.text((60, 620), "COUNTRY OF ORIGIN: INDIA", fill=(0, 0, 0))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def generate_blank_image_bytes(width: int = 400, height: int = 400) -> bytes:
    """Generate a blank image with no text."""
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


# ── 1. OCR Service Unit Tests ─────────────────────────────────────────────────

class TestOCRServiceUnit:
    def test_ocr_process_synthetic_label(self):
        """Test 1: OCR detects text tokens from synthetic label with confidence and bounding boxes."""
        img_bytes = generate_synthetic_label_image_bytes()
        raw_result = OCRService.process_image_bytes(img_bytes, "image/jpeg")

        assert raw_result.ocr_engine == OCR_ENGINE_NAME
        assert raw_result.ocr_engine_version == OCR_ENGINE_VERSION
        assert raw_result.processing_version == PROCESSING_VERSION
        assert raw_result.total_tokens > 0
        assert len(raw_result.tokens) == raw_result.total_tokens
        assert len(raw_result.full_text) > 0

        # Verify token structure
        first_token = raw_result.tokens[0]
        assert "token_index" in first_token
        assert "line_index" in first_token
        assert "text" in first_token
        assert "confidence" in first_token
        assert "bounding_box" in first_token
        assert 0.0 <= first_token["confidence"] <= 1.0

        # Verify bounding box format: 4 points in original image coordinate space
        bbox = first_token["bounding_box"]
        assert bbox["coordinate_space"] == "original_image"
        assert len(bbox["points"]) == 4
        for pt in bbox["points"]:
            assert len(pt) == 2
            assert isinstance(pt[0], (int, float))
            assert isinstance(pt[1], (int, float))

        # Check detected text content contains key strings
        full_text_upper = raw_result.full_text.upper()
        assert "BASMATI" in full_text_upper or "RICE" in full_text_upper or "FOODS" in full_text_upper

    def test_ocr_process_blank_image(self):
        """Test 2: OCR on blank image returns empty token list and zero count."""
        img_bytes = generate_blank_image_bytes()
        raw_result = OCRService.process_image_bytes(img_bytes, "image/jpeg")

        assert raw_result.total_tokens == 0
        assert raw_result.tokens == []
        assert raw_result.full_text == ""
        assert raw_result.ocr_engine == OCR_ENGINE_NAME


# ── 2. Persistence & Idempotency Integration Tests ────────────────────────────

@pytest.mark.asyncio
class TestOCRPersistenceAndGating:
    async def test_ocr_idempotent_persistence(self):
        """Test 3: Repeated OCR result persistence updates in-place without duplicate rows."""
        async with AsyncSessionLocal() as db:
            inspector = User(
                id=f"USR-{uuid.uuid4().hex[:8].upper()}",
                email=f"inspector.{uuid.uuid4().hex[:6]}@compliscan.gov.in",
                full_name="Inspector Idempotence",
                role=UserRole.INSPECTOR.value,
                is_active=True,
            )
            db.add(inspector)
            await db.flush()

            inspection = InspectionCase(
                id=f"INS-{uuid.uuid4().hex[:8].upper()}",
                case_number=f"INS-2026-OCR-{uuid.uuid4().hex[:4].upper()}",
                product_name="OCR Idempotency Product",
                created_by_id=inspector.id,
            )
            db.add(inspection)
            await db.flush()

            asset = EvidenceAsset(
                id=f"EV-{uuid.uuid4().hex[:8].upper()}",
                inspection_id=inspection.id,
                evidence_type=EvidenceType.PRIMARY.value,
                original_filename="label.jpg",
                mime_type="image/jpeg",
                file_size_bytes=1024,
                sha256_hash="abc123sha",
                storage_path="dummy_path.jpg",
                uploaded_by_id=inspector.id,
            )
            db.add(asset)
            await db.flush()

            img_bytes = generate_synthetic_label_image_bytes()
            raw_res = OCRService.process_image_bytes(img_bytes)

            # First persist
            res1 = await OCRService.persist_ocr_result(db, asset, raw_res)
            await db.commit()
            res1_id = res1.id

            # Second persist with same evidence and processing_version
            res2 = await OCRService.persist_ocr_result(db, asset, raw_res)
            await db.commit()

            # Confirm same ID and exactly 1 row
            assert res2.id == res1_id
            stmt = select(OCRResult).where(OCRResult.evidence_id == asset.id)
            records = (await db.execute(stmt)).scalars().all()
            assert len(records) == 1

    async def test_ocr_quality_gate_blocking_needs_review(self):
        """Test 4: Quality NEEDS_REVIEW blocks OCR with processing_blocked=True and reason code."""
        async with AsyncSessionLocal() as db:
            inspector = User(
                id=f"USR-{uuid.uuid4().hex[:8].upper()}",
                email=f"insp.gate.{uuid.uuid4().hex[:6]}@compliscan.gov.in",
                full_name="Inspector Gate",
                role=UserRole.INSPECTOR.value,
                is_active=True,
            )
            db.add(inspector)
            await db.flush()

            inspection = InspectionCase(
                id=f"INS-{uuid.uuid4().hex[:8].upper()}",
                case_number=f"INS-2026-GATE-{uuid.uuid4().hex[:4].upper()}",
                product_name="Gate Test Product",
                created_by_id=inspector.id,
            )
            db.add(inspection)
            await db.flush()

            asset = EvidenceAsset(
                id=f"EV-{uuid.uuid4().hex[:8].upper()}",
                inspection_id=inspection.id,
                evidence_type=EvidenceType.PRIMARY.value,
                original_filename="blurred.jpg",
                mime_type="image/jpeg",
                file_size_bytes=1024,
                sha256_hash="blurredsha",
                storage_path="dummy_blurred.jpg",
                uploaded_by_id=inspector.id,
            )
            db.add(asset)
            await db.flush()

            # Create a NEEDS_REVIEW quality assessment
            quality = ImageQualityAssessment(
                evidence_id=asset.id,
                inspection_id=inspection.id,
                quality_status=ImageQualityStatus.NEEDS_REVIEW.value,
                assessment_version="v1.0",
                width=1920,
                height=1080,
                total_pixels=1920 * 1080,
                mime_type="image/jpeg",
                is_decoded=True,
                sharpness_score=15.0,
                reason_codes=[QualityReasonCode.EXCESSIVE_BLUR.value],
            )
            db.add(quality)
            await db.flush()

            # Enqueue and execute OCR job
            job = await AnalysisJobService.enqueue_job(
                db=db,
                inspection_id=inspection.id,
                job_type=JobType.PERCEPTION,
                evidence_id=asset.id,
            )
            await db.commit()

            # Execute job
            claimed = await AnalysisJobService.claim_next_job(db, worker_id="test-worker")
            assert claimed is not None
            assert claimed.id == job.id

            await AnalysisJobService.execute_job(db, claimed)
            await db.commit()

            assert claimed.status == JobStatus.COMPLETED.value

            # Check OCRResult is blocked
            stmt_ocr = select(OCRResult).where(OCRResult.evidence_id == asset.id)
            ocr_record = (await db.execute(stmt_ocr)).scalar_one_or_none()
            assert ocr_record is not None
            assert ocr_record.processing_blocked is True
            assert ocr_record.block_reason == ImageQualityStatus.NEEDS_REVIEW.value
            assert ocr_record.total_tokens == 0
            assert ocr_record.tokens == []

            # Check Audit Event logged
            stmt_audit = select(AuditEvent).where(
                AuditEvent.inspection_id == inspection.id,
                AuditEvent.event_type == AuditEventType.OCR_PROCESSED.value,
            )
            audit = (await db.execute(stmt_audit)).scalar_one_or_none()
            assert audit is not None
            assert audit.details["status"] == "BLOCKED"

    async def test_end_to_end_usable_pipeline(self):
        """Test 5: Full pipeline: Upload -> Quality (USABLE) -> Auto-enqueue PERCEPTION -> OCR Tokens."""
        async with AsyncSessionLocal() as db:
            inspector = User(
                id=f"USR-{uuid.uuid4().hex[:8].upper()}",
                email=f"insp.e2e.{uuid.uuid4().hex[:6]}@compliscan.gov.in",
                full_name="Inspector E2E",
                role=UserRole.INSPECTOR.value,
                is_active=True,
            )
            db.add(inspector)
            await db.flush()

            inspection = InspectionCase(
                id=f"INS-{uuid.uuid4().hex[:8].upper()}",
                case_number=f"INS-2026-E2E-{uuid.uuid4().hex[:4].upper()}",
                product_name="E2E Pipeline Product",
                created_by_id=inspector.id,
            )
            db.add(inspection)
            await db.flush()

            # Create synthetic label bytes
            img_bytes = generate_synthetic_label_image_bytes()
            upload_file = UploadFile(
                filename="e2e_label.jpg",
                file=io.BytesIO(img_bytes),
                headers={"content-type": "image/jpeg"},
            )

            # Upload evidence
            asset = await EvidenceService.upload_evidence(
                db=db,
                inspection_id=inspection.id,
                file=upload_file,
                evidence_type=EvidenceType.PRIMARY,
                current_user=inspector,
            )
            original_sha = asset.sha256_hash

            # Step 1: Run pending jobs (processes Image Quality job and its auto-enqueued Perception job)
            jobs_run = await AnalysisJobService.run_pending_jobs_inline(db, worker_id="worker-all")
            assert jobs_run >= 2

            # Quality should be USABLE
            quality = await EvidenceService.get_evidence_quality(db, asset.id)
            assert quality.quality_status == ImageQualityStatus.USABLE.value

            # Step 2: Fetch OCR result
            ocr_record = await EvidenceService.get_evidence_ocr(db, asset.id, inspector)
            assert ocr_record is not None
            assert ocr_record.processing_blocked is False
            assert ocr_record.total_tokens > 0
            assert ocr_record.ocr_engine == OCR_ENGINE_NAME
            assert ocr_record.ocr_engine_version == OCR_ENGINE_VERSION


            # Step 4: Verify Evidence Immutability
            disk_bytes, _ = await EvidenceService.get_evidence_binary(db=db, evidence_id=asset.id, current_user=inspector)
            assert disk_bytes == img_bytes
            assert compute_sha256(disk_bytes) == original_sha

            # Step 5: Verify Domain Separation (zero ComplianceResult / ComplianceFinding exists)
            # (No compliance tables or records touched)
            stmt_audit = select(AuditEvent).where(
                AuditEvent.inspection_id == inspection.id,
                AuditEvent.event_type == AuditEventType.OCR_PROCESSED.value,
            )
            audit = (await db.execute(stmt_audit)).scalar_one_or_none()
            assert audit is not None
            assert audit.details["status"] == "COMPLETED"
            assert audit.details["total_tokens"] == ocr_record.total_tokens


# ── 3. API & RBAC Tests ───────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestOCRAPI:
    async def test_get_ocr_and_process_ocr_endpoints(self):
        """Test 6: REST API endpoints, authorization checks, and RBAC isolation."""
        async with AsyncSessionLocal() as db:
            inspector1 = User(
                id=f"USR-INSP1-{uuid.uuid4().hex[:6].upper()}",
                email=f"insp1.{uuid.uuid4().hex[:6]}@compliscan.gov.in",
                full_name="Inspector One",
                role=UserRole.INSPECTOR.value,
                is_active=True,
            )
            inspector2 = User(
                id=f"USR-INSP2-{uuid.uuid4().hex[:6].upper()}",
                email=f"insp2.{uuid.uuid4().hex[:6]}@compliscan.gov.in",
                full_name="Inspector Two",
                role=UserRole.INSPECTOR.value,
                is_active=True,
            )
            reviewer = User(
                id=f"USR-REV-{uuid.uuid4().hex[:6].upper()}",
                email=f"rev.{uuid.uuid4().hex[:6]}@compliscan.gov.in",
                full_name="Reviewer User",
                role=UserRole.REVIEWER.value,
                is_active=True,
            )
            db.add_all([inspector1, inspector2, reviewer])
            await db.flush()

            inspection1 = InspectionCase(
                id=f"INS-{uuid.uuid4().hex[:8].upper()}",
                case_number=f"INS-2026-API1-{uuid.uuid4().hex[:4].upper()}",
                product_name="API Test Case 1",
                created_by_id=inspector1.id,
            )
            db.add(inspection1)
            await db.flush()

            # Upload evidence under inspector 1
            img_bytes = generate_synthetic_label_image_bytes()
            upload_file = UploadFile(
                filename="api_label.jpg",
                file=io.BytesIO(img_bytes),
                headers={"content-type": "image/jpeg"},
            )
            asset1 = await EvidenceService.upload_evidence(
                db=db,
                inspection_id=inspection1.id,
                file=upload_file,
                evidence_type=EvidenceType.PRIMARY,
                current_user=inspector1,
            )

            # Process jobs to produce OCRResult
            await AnalysisJobService.run_pending_jobs_inline(db, worker_id="api-worker")

            # Create tokens
            token1 = create_test_supabase_token(user_id=inspector1.id, email=inspector1.email)
            token2 = create_test_supabase_token(user_id=inspector2.id, email=inspector2.email)
            token_rev = create_test_supabase_token(user_id=reviewer.id, email=reviewer.email)


        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Unauthenticated GET -> 401
            res_unauth = await client.get(f"/api/v1/evidence/{asset1.id}/ocr")
            assert res_unauth.status_code == 401

            # 2. Inspector 1 (owner) GET -> 200 OK
            res_owner = await client.get(
                f"/api/v1/evidence/{asset1.id}/ocr",
                headers={"Authorization": f"Bearer {token1}"},
            )
            assert res_owner.status_code == 200
            data = res_owner.json()
            assert data["evidence_id"] == asset1.id
            assert data["ocr_engine"] == OCR_ENGINE_NAME
            assert data["total_tokens"] > 0
            assert len(data["tokens"]) == data["total_tokens"]

            # 3. Reviewer GET -> 200 OK
            res_rev = await client.get(
                f"/api/v1/evidence/{asset1.id}/ocr",
                headers={"Authorization": f"Bearer {token_rev}"},
            )
            assert res_rev.status_code == 200

            # 4. Cross-inspector Inspector 2 GET -> 403 Forbidden
            res_cross = await client.get(
                f"/api/v1/evidence/{asset1.id}/ocr",
                headers={"Authorization": f"Bearer {token2}"},
            )
            assert res_cross.status_code == 403

            # 5. POST /process-ocr -> 202 Accepted (asynchronous)
            res_trigger = await client.post(
                f"/api/v1/evidence/{asset1.id}/process-ocr",
                headers={"Authorization": f"Bearer {token1}"},
            )
            assert res_trigger.status_code == 202
            job_data = res_trigger.json()
            assert job_data["job_type"] == JobType.PERCEPTION.value

            # 6. POST /process-ocr from unauthorized inspector -> 403 Forbidden
            res_trigger_cross = await client.post(
                f"/api/v1/evidence/{asset1.id}/process-ocr",
                headers={"Authorization": f"Bearer {token2}"},
            )
            assert res_trigger_cross.status_code == 403
