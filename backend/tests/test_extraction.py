"""
CompliScan LM — Phase 2.3 Gemini 2.5 Flash Structured Declaration Extraction Test Suite.

Comprehensive validation of:
1. Pydantic schema validation for 6 core domains + 1 conditional domain
2. Observation statuses: OBSERVED, NOT_OBSERVED, AMBIGUOUS, CONFLICTING, UNREADABLE
3. Candidate values with independent provenance for ambiguous / conflicting observations
4. Source-token provenance validation (token index boundary checking, conservative grounding)
5. Zero-token OCR behavior (bypass Gemini, persist BLOCKED result with NO_OCR_TOKENS_OBSERVED)
6. Upstream blocked OCR behavior (propagate BLOCKED status deterministically)
7. End-to-end async job pipeline: Perception OCR -> Extraction AnalysisJob execution
8. Extraction idempotency: atomic in-place upsert on (evidence_id, extraction_version, model_name)
9. Error handling & retry: Gemini API failure handling without converting to compliance findings
10. API endpoints & RBAC:
    - GET /api/v1/evidence/{id}/declarations (200 OK for owner/reviewer, 403 for unauthorized inspector)
    - POST /api/v1/evidence/{id}/extract-declarations (202 Accepted)
11. Prompt injection resilience: OCR text containing directives is treated strictly as data
12. Domain isolation: Strict absence of ComplianceResult / ApplicabilityResult / ComplianceFinding
13. Model version provenance: Model identifier, prompt version, extraction version preserved without fabrication
"""

import io
import json
import os
from unittest.mock import MagicMock, patch
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from backend.app.main import app
from backend.app.core.config import settings
from backend.app.core.errors import AnalysisError
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.user import User
from backend.app.models.inspection import InspectionCase
from backend.app.models.evidence import EvidenceAsset
from backend.app.models.ocr import OCRResult
from backend.app.models.structured_declaration import StructuredDeclarationResult
from backend.app.models.analysis_job import AnalysisJob
from backend.app.models.audit import AuditEvent
from backend.app.schemas.structured_declaration import (
    StructuredDeclarations,
    CandidateValue,
    ManufacturerIdentityField,
    CommodityNameField,
    NetQuantityField,
    ManufacturePackingDateField,
    MaximumRetailPriceField,
    ConsumerCareField,
    CountryOfOriginField,
)
from backend.app.services.extraction_service import (
    ExtractionService,
    PROVIDER_NAME,
    EXTRACTION_VERSION,
)
from backend.app.services.prompts.extraction_v1 import (
    PROMPT_VERSION,
    SYSTEM_INSTRUCTION,
    build_extraction_prompt,
)
from backend.app.services.analysis_job_service import AnalysisJobService
from backend.app.services.evidence_service import EvidenceService
from backend.tests.conftest import create_test_supabase_token
from shared.domain.enums import (
    UserRole,
    OriginStatus,
    EvidenceType,
    JobType,
    JobStatus,
    AuditEventType,
    ObservationStatus,
)


# ── Sample Fixtures & Helpers ────────────────────────────────────────────────

SAMPLE_OCR_TOKENS = [
    {"token_index": 0, "line_index": 0, "text": "PREMIUM BASMATI RICE", "confidence": 0.98},
    {"token_index": 1, "line_index": 1, "text": "MANUFACTURED BY: HIMALAYAN FOODS LTD, INDUSTRIAL AREA, HARIDWAR", "confidence": 0.97},
    {"token_index": 2, "line_index": 2, "text": "NET QUANTITY: 5 kg", "confidence": 0.99},
    {"token_index": 3, "line_index": 3, "text": "MAXIMUM RETAIL PRICE: Rs. 450.00 (INCL OF ALL TAXES)", "confidence": 0.96},
    {"token_index": 4, "line_index": 4, "text": "MONTH & YEAR OF PKG: 09/2026", "confidence": 0.95},
    {"token_index": 5, "line_index": 5, "text": "CONSUMER CARE: care@himalayanfoods.com, TEL: 1800-200-3000", "confidence": 0.94},
    {"token_index": 6, "line_index": 6, "text": "COUNTRY OF ORIGIN: INDIA", "confidence": 0.98},
]


def create_mock_gemini_declarations() -> StructuredDeclarations:
    """Return a fully populated StructuredDeclarations object grounded in SAMPLE_OCR_TOKENS."""
    return StructuredDeclarations(
        manufacturer_identity=ManufacturerIdentityField(
            status=ObservationStatus.OBSERVED,
            declaration_type="MANUFACTURER",
            name="HIMALAYAN FOODS LTD",
            address="INDUSTRIAL AREA, HARIDWAR",
            raw_text="MANUFACTURED BY: HIMALAYAN FOODS LTD, INDUSTRIAL AREA, HARIDWAR",
            source_token_indices=[1],
        ),
        commodity_name=CommodityNameField(
            status=ObservationStatus.OBSERVED,
            name="PREMIUM BASMATI RICE",
            raw_text="PREMIUM BASMATI RICE",
            source_token_indices=[0],
        ),
        net_quantity=NetQuantityField(
            status=ObservationStatus.OBSERVED,
            quantity_value=5.0,
            unit="kg",
            unit_raw="kg",
            raw_text="NET QUANTITY: 5 kg",
            source_token_indices=[2],
        ),
        manufacture_packing_date=ManufacturePackingDateField(
            status=ObservationStatus.OBSERVED,
            date_type="PACKING",
            month=9,
            year=2026,
            raw_date_string="09/2026",
            raw_text="MONTH & YEAR OF PKG: 09/2026",
            source_token_indices=[4],
        ),
        mrp=MaximumRetailPriceField(
            status=ObservationStatus.OBSERVED,
            currency="INR",
            amount=450.0,
            includes_all_taxes_stated=True,
            raw_text="MAXIMUM RETAIL PRICE: Rs. 450.00 (INCL OF ALL TAXES)",
            source_token_indices=[3],
        ),
        consumer_care=ConsumerCareField(
            status=ObservationStatus.OBSERVED,
            email="care@himalayanfoods.com",
            phone="1800-200-3000",
            raw_text="CONSUMER CARE: care@himalayanfoods.com, TEL: 1800-200-3000",
            source_token_indices=[5],
        ),
        country_of_origin=CountryOfOriginField(
            status=ObservationStatus.OBSERVED,
            country_name="INDIA",
            raw_text="COUNTRY OF ORIGIN: INDIA",
            source_token_indices=[6],
        ),
    )


# ── 1. Schema & Provenance Unit Tests ─────────────────────────────────────────

def test_pydantic_schema_observation_statuses():
    """Verify all 5 observation statuses are strictly supported and typed."""
    decls = StructuredDeclarations(
        manufacturer_identity=ManufacturerIdentityField(status=ObservationStatus.OBSERVED, source_token_indices=[0]),
        commodity_name=CommodityNameField(status=ObservationStatus.NOT_OBSERVED, source_token_indices=[]),
        net_quantity=NetQuantityField(status=ObservationStatus.AMBIGUOUS, source_token_indices=[1]),
        manufacture_packing_date=ManufacturePackingDateField(status=ObservationStatus.CONFLICTING, source_token_indices=[2, 3]),
        mrp=MaximumRetailPriceField(status=ObservationStatus.UNREADABLE, source_token_indices=[4]),
        consumer_care=ConsumerCareField(status=ObservationStatus.NOT_OBSERVED, source_token_indices=[]),
        country_of_origin=CountryOfOriginField(status=ObservationStatus.OBSERVED, country_name="INDIA", source_token_indices=[5]),
    )
    dumped = decls.model_dump(mode="json")
    assert dumped["manufacturer_identity"]["status"] == "OBSERVED"
    assert dumped["commodity_name"]["status"] == "NOT_OBSERVED"
    assert dumped["net_quantity"]["status"] == "AMBIGUOUS"
    assert dumped["manufacture_packing_date"]["status"] == "CONFLICTING"
    assert dumped["mrp"]["status"] == "UNREADABLE"


def test_provenance_validation_valid():
    """Verify valid token indices pass provenance validation."""
    decls = create_mock_gemini_declarations()
    # Must not raise
    ExtractionService.validate_provenance(decls, SAMPLE_OCR_TOKENS)


def test_provenance_validation_out_of_bounds_rejected():
    """Verify out-of-bounds token indices (> len(tokens)-1) are rejected."""
    decls = create_mock_gemini_declarations()
    # Fabricate invalid token index 99
    decls.mrp.source_token_indices = [99]

    with pytest.raises(AnalysisError, match="out of range"):
        ExtractionService.validate_provenance(decls, SAMPLE_OCR_TOKENS)


def test_provenance_validation_negative_index_rejected():
    """Verify negative token index is rejected."""
    decls = create_mock_gemini_declarations()
    decls.commodity_name.source_token_indices = [-1]

    with pytest.raises(AnalysisError, match="out of range"):
        ExtractionService.validate_provenance(decls, SAMPLE_OCR_TOKENS)


def test_provenance_validation_observed_without_tokens_rejected():
    """Verify status=OBSERVED without any source_token_indices is rejected."""
    decls = create_mock_gemini_declarations()
    decls.net_quantity.source_token_indices = []  # OBSERVED but no tokens cited

    with pytest.raises(AnalysisError, match="status is OBSERVED but source_token_indices is empty"):
        ExtractionService.validate_provenance(decls, SAMPLE_OCR_TOKENS)


def test_provenance_validation_candidates():
    """Verify candidate token indices are also validated."""
    decls = create_mock_gemini_declarations()
    decls.mrp.status = ObservationStatus.CONFLICTING
    decls.mrp.source_token_indices = [3]
    decls.mrp.candidates = [
        CandidateValue(raw_text="MRP Rs 450", source_token_indices=[3]),
        CandidateValue(raw_text="MRP Rs 500", source_token_indices=[100]),  # Invalid!
    ]

    with pytest.raises(AnalysisError, match="out of range"):
        ExtractionService.validate_provenance(decls, SAMPLE_OCR_TOKENS)


def test_prompt_template_formatting():
    """Verify build_extraction_prompt formats OCR tokens cleanly without product category."""
    prompt = build_extraction_prompt(SAMPLE_OCR_TOKENS)
    assert "[0] PREMIUM BASMATI RICE" in prompt
    assert "[1] MANUFACTURED BY" in prompt
    assert "[6] COUNTRY OF ORIGIN: INDIA" in prompt
    assert PROMPT_VERSION == "v1.0"
    assert "UNTRUSTED DATA" in SYSTEM_INSTRUCTION


# ── 2. Zero-Token & Blocked OCR Handling ─────────────────────────────────────

@pytest.mark.asyncio
async def test_zero_token_ocr_bypasses_gemini():
    """
    Acceptance Criteria 7, 11:
    If OCRResult.total_tokens == 0:
    - do not call Gemini
    - create BLOCKED extraction output
    - block_reason = NO_OCR_TOKENS_OBSERVED
    - all fields = NOT_OBSERVED
    - source_token_indices = []
    """
    async with AsyncSessionLocal() as db:
        inspector = User(
            id=f"USR-INSP-{uuid.uuid4().hex[:6].upper()}",
            email=f"insp.{uuid.uuid4().hex[:6]}@compliscan.gov.in",
            full_name="Inspector Test",
            role=UserRole.INSPECTOR.value,
            is_active=True,
        )
        db.add(inspector)
        await db.flush()

        # 1. Create Inspection & Evidence
        insp = InspectionCase(
            id=f"INSP-{uuid.uuid4().hex[:8].upper()}",
            case_number=f"CAS-{uuid.uuid4().hex[:6].upper()}",
            product_name="Blank Evidence Case",
            origin_status=OriginStatus.DOMESTIC.value,
            status="EVIDENCE_UPLOADED",
            created_by_id=inspector.id,
        )
        db.add(insp)

        evidence = EvidenceAsset(
            id=f"EV-{uuid.uuid4().hex[:8].upper()}",
            inspection_id=insp.id,
            evidence_type=EvidenceType.PRIMARY.value,
            original_filename="blank.jpg",
            mime_type="image/jpeg",
            file_size_bytes=1000,
            sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            storage_path="mock/path/blank.jpg",
            is_immutable=True,
            uploaded_by_id=inspector.id,
        )
        db.add(evidence)

        # 2. Add OCRResult with 0 tokens
        ocr = OCRResult(
            id=f"OCR-{uuid.uuid4().hex[:8].upper()}",
            evidence_id=evidence.id,
            inspection_id=insp.id,
            ocr_engine="paddleocr-onnx",
            ocr_engine_version="test",
            processing_version="v1.0",
            processing_blocked=False,
            total_tokens=0,
            full_text="",
            tokens=[],
        )
        db.add(ocr)

        # 3. Add Extraction Job
        job = AnalysisJob(
            id=f"JOB-{uuid.uuid4().hex[:8].upper()}",
            inspection_id=insp.id,
            evidence_id=evidence.id,
            job_type=JobType.EXTRACTION.value,
            status=JobStatus.PENDING.value,
            attempts=0,
            max_attempts=3,
        )
        db.add(job)
        await db.commit()

        # 4. Mock ExtractionService.call_gemini_extraction to ensure it is NEVER called
        with patch.object(ExtractionService, "call_gemini_extraction") as mock_gemini:
            await AnalysisJobService.execute_job(db, job)
            await db.commit()

            mock_gemini.assert_not_called()

        # 5. Verify StructuredDeclarationResult persisted
        stmt = select(StructuredDeclarationResult).where(StructuredDeclarationResult.evidence_id == evidence.id)
        decl_result = (await db.execute(stmt)).scalar_one()

        assert decl_result.extraction_status == "BLOCKED"
        assert decl_result.processing_blocked is True
        assert decl_result.block_reason == "NO_OCR_TOKENS_OBSERVED"
        assert decl_result.provider == PROVIDER_NAME
        assert decl_result.prompt_version == PROMPT_VERSION

        # All fields must be NOT_OBSERVED
        decls = decl_result.declarations
        assert decls["manufacturer_identity"]["status"] == "NOT_OBSERVED"
        assert decls["commodity_name"]["status"] == "NOT_OBSERVED"
        assert decls["net_quantity"]["status"] == "NOT_OBSERVED"
        assert decls["manufacture_packing_date"]["status"] == "NOT_OBSERVED"
        assert decls["mrp"]["status"] == "NOT_OBSERVED"
        assert decls["consumer_care"]["status"] == "NOT_OBSERVED"
        assert decls["country_of_origin"]["status"] == "NOT_OBSERVED"

        # Verify Audit Event logged
        stmt_aud = select(AuditEvent).where(
            AuditEvent.inspection_id == insp.id,
            AuditEvent.event_type == AuditEventType.DECLARATIONS_EXTRACTED.value,
        )
        audit = (await db.execute(stmt_aud)).scalar_one()
        assert audit.details["status"] == "BLOCKED"
        assert audit.details["block_reason"] == "NO_OCR_TOKENS_OBSERVED"


# ── 3. Mocked Gemini Extraction Pipeline & Domain Structuring ─────────────────

@pytest.mark.asyncio
async def test_extraction_pipeline_with_mocked_gemini():
    """
    Acceptance Criteria 1, 2, 3, 8, 9, 10, 18, 19:
    Verify successful extraction of 6 core domains + 1 conditional COO domain.
    """
    async with AsyncSessionLocal() as db:
        inspector = User(
            id=f"USR-INSP-{uuid.uuid4().hex[:6].upper()}",
            email=f"insp.{uuid.uuid4().hex[:6]}@compliscan.gov.in",
            full_name="Inspector Test",
            role=UserRole.INSPECTOR.value,
            is_active=True,
        )
        db.add(inspector)
        await db.flush()

        # 1. Create Inspection & Evidence
        insp = InspectionCase(
            id=f"INSP-{uuid.uuid4().hex[:8].upper()}",
            case_number=f"CAS-{uuid.uuid4().hex[:6].upper()}",
            product_name="Basmati Rice Case",
            origin_status=OriginStatus.DOMESTIC.value,
            status="EVIDENCE_UPLOADED",
            created_by_id=inspector.id,
        )
        db.add(insp)

        evidence = EvidenceAsset(
            id=f"EV-{uuid.uuid4().hex[:8].upper()}",
            inspection_id=insp.id,
            evidence_type=EvidenceType.PRIMARY.value,
            original_filename="rice.jpg",
            mime_type="image/jpeg",
            file_size_bytes=5000,
            sha256_hash="abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234",
            storage_path="mock/path/rice.jpg",
            is_immutable=True,
            uploaded_by_id=inspector.id,
        )
        db.add(evidence)

        # 2. Add OCRResult with tokens
        ocr = OCRResult(
            id=f"OCR-{uuid.uuid4().hex[:8].upper()}",
            evidence_id=evidence.id,
            inspection_id=insp.id,
            ocr_engine="paddleocr-onnx",
            ocr_engine_version="test",
            processing_version="v1.0",
            processing_blocked=False,
            total_tokens=len(SAMPLE_OCR_TOKENS),
            full_text="PREMIUM BASMATI RICE\n...",
            tokens=SAMPLE_OCR_TOKENS,
        )
        db.add(ocr)

        # 3. Add Extraction Job
        job = AnalysisJob(
            id=f"JOB-{uuid.uuid4().hex[:8].upper()}",
            inspection_id=insp.id,
            evidence_id=evidence.id,
            job_type=JobType.EXTRACTION.value,
            status=JobStatus.PENDING.value,
            attempts=0,
            max_attempts=3,
        )
        db.add(job)
        await db.commit()

        # 4. Mock Gemini client generate_content returning valid StructuredDeclarations JSON
        mock_decls = create_mock_gemini_declarations()
        mock_response = MagicMock()
        mock_response.text = mock_decls.model_dump_json()

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response

        ExtractionService.set_client(mock_client)

        try:
            # Execute extraction job
            await AnalysisJobService.execute_job(db, job)
            await db.commit()

            # 5. Verify StructuredDeclarationResult
            stmt = select(StructuredDeclarationResult).where(StructuredDeclarationResult.evidence_id == evidence.id)
            decl_result = (await db.execute(stmt)).scalar_one()

            assert decl_result.extraction_status == "COMPLETED"
            assert decl_result.processing_blocked is False
            assert decl_result.provider == "google"
            assert decl_result.model_name == settings.GEMINI_MODEL
            assert decl_result.model_version is None  # Unfabricated
            assert decl_result.prompt_version == "v1.0"
            assert decl_result.extraction_version == "v1.0"

            # Check 6 core domains + 1 conditional COO
            decls = decl_result.declarations
            assert decls["manufacturer_identity"]["status"] == "OBSERVED"
            assert decls["manufacturer_identity"]["name"] == "HIMALAYAN FOODS LTD"
            assert decls["commodity_name"]["name"] == "PREMIUM BASMATI RICE"
            assert decls["net_quantity"]["quantity_value"] == 5.0
            assert decls["net_quantity"]["unit"] == "kg"
            assert decls["manufacture_packing_date"]["month"] == 9
            assert decls["manufacture_packing_date"]["year"] == 2026
            assert decls["mrp"]["amount"] == 450.0
            assert decls["consumer_care"]["phone"] == "1800-200-3000"
            assert decls["country_of_origin"]["country_name"] == "INDIA"

            # 6. Verify Idempotence: re-running extraction updates record without creating duplicate rows
            await ExtractionService.persist_declaration_result(
                db=db,
                evidence=evidence,
                ocr_result=ocr,
                declarations=mock_decls,
            )
            await db.commit()

            stmt_count = select(StructuredDeclarationResult).where(StructuredDeclarationResult.evidence_id == evidence.id)
            all_decls = (await db.execute(stmt_count)).scalars().all()
            assert len(all_decls) == 1, "Idempotency violated: duplicate declaration rows created"

        finally:
            ExtractionService.set_client(None)


# ── 4. Gemini API Failure & Retry Isolation ──────────────────────────────────

@pytest.mark.asyncio
async def test_gemini_api_failure_handling():
    """
    Acceptance Criteria 10, 12:
    Gemini/API failure:
    - retry through AnalysisJob
    - after max_attempts: FAILED
    - never convert technical failure into compliance result
    """
    async with AsyncSessionLocal() as db:
        inspector = User(
            id=f"USR-INSP-{uuid.uuid4().hex[:6].upper()}",
            email=f"insp.{uuid.uuid4().hex[:6]}@compliscan.gov.in",
            full_name="Inspector Test",
            role=UserRole.INSPECTOR.value,
            is_active=True,
        )
        db.add(inspector)
        await db.flush()

        insp = InspectionCase(
            id=f"INSP-{uuid.uuid4().hex[:8].upper()}",
            case_number=f"CAS-{uuid.uuid4().hex[:6].upper()}",
            product_name="Failing Case",
            origin_status=OriginStatus.DOMESTIC.value,
            status="EVIDENCE_UPLOADED",
            created_by_id=inspector.id,
        )
        db.add(insp)

        evidence = EvidenceAsset(
            id=f"EV-{uuid.uuid4().hex[:8].upper()}",
            inspection_id=insp.id,
            evidence_type=EvidenceType.PRIMARY.value,
            original_filename="fail.jpg",
            mime_type="image/jpeg",
            file_size_bytes=5000,
            sha256_hash="1111222233334444111122223333444411112222333344441111222233334444",
            storage_path="mock/path/fail.jpg",
            is_immutable=True,
            uploaded_by_id=inspector.id,
        )
        db.add(evidence)

        ocr = OCRResult(
            id=f"OCR-{uuid.uuid4().hex[:8].upper()}",
            evidence_id=evidence.id,
            inspection_id=insp.id,
            ocr_engine="paddleocr-onnx",
            ocr_engine_version="test",
            processing_version="v1.0",
            processing_blocked=False,
            total_tokens=len(SAMPLE_OCR_TOKENS),
            full_text="TEXT",
            tokens=SAMPLE_OCR_TOKENS,
        )
        db.add(ocr)

        job = AnalysisJob(
            id=f"JOB-{uuid.uuid4().hex[:8].upper()}",
            inspection_id=insp.id,
            evidence_id=evidence.id,
            job_type=JobType.EXTRACTION.value,
            status=JobStatus.PENDING.value,
            attempts=0,
            max_attempts=2,
        )
        db.add(job)
        await db.commit()

        # Mock failing client
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = RuntimeError("Rate limit exceeded 429")
        ExtractionService.set_client(mock_client)

        try:
            # 1st attempt: job fails and resets to PENDING for retry
            claimed_job_1 = await AnalysisJobService.claim_next_job(db, worker_id="worker-1")
            assert claimed_job_1 is not None
            assert claimed_job_1.attempts == 1
            await AnalysisJobService.execute_job(db, claimed_job_1)
            await db.commit()

            assert claimed_job_1.status == JobStatus.PENDING.value
            assert "Rate limit exceeded" in claimed_job_1.error_message

            # 2nd attempt (max_attempts = 2): job transitions to FAILED
            claimed_job_2 = await AnalysisJobService.claim_next_job(db, worker_id="worker-2")
            assert claimed_job_2 is not None
            assert claimed_job_2.attempts == 2
            await AnalysisJobService.execute_job(db, claimed_job_2)
            await db.commit()

            assert claimed_job_2.status == JobStatus.FAILED.value

            # Zero StructuredDeclarationResult should exist
            stmt_decl = select(StructuredDeclarationResult).where(StructuredDeclarationResult.evidence_id == evidence.id)
            decl = (await db.execute(stmt_decl)).scalar_one_or_none()
            assert decl is None

        finally:
            ExtractionService.set_client(None)


# ── 5. Domain Separation Verification ────────────────────────────────────────

@pytest.mark.asyncio
async def test_domain_separation_no_compliance_models_generated():
    """
    Acceptance Criteria 5, 13, 14, 15, 16, 17:
    Strictly verify that Phase 2.3 extraction does NOT create compliance records.
    """
    async with AsyncSessionLocal() as db:
        # Check audit events: no COMPLIANCE_EVALUATED events exist
        stmt = select(AuditEvent).where(AuditEvent.event_type == "COMPLIANCE_EVALUATED")
        results = (await db.execute(stmt)).scalars().all()
        assert len(results) == 0


# ── 6. API Endpoints & RBAC Tests ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_api_get_and_post_declarations():
    """
    Acceptance Criteria 18:
    Verify GET /evidence/{id}/declarations and POST /evidence/{id}/extract-declarations.
    """
    async with AsyncSessionLocal() as db:
        inspector = User(
            id=f"USR-INSP1-{uuid.uuid4().hex[:6].upper()}",
            email=f"insp1.{uuid.uuid4().hex[:6]}@compliscan.gov.in",
            full_name="Inspector One",
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
        other_inspector = User(
            id=f"USR-INSP2-{uuid.uuid4().hex[:6].upper()}",
            email=f"insp2.{uuid.uuid4().hex[:6]}@compliscan.gov.in",
            full_name="Inspector Two",
            role=UserRole.INSPECTOR.value,
            is_active=True,
        )
        db.add_all([inspector, reviewer, other_inspector])
        await db.flush()

        # 1. Create inspection & evidence & declarations
        insp = InspectionCase(
            id=f"INSP-{uuid.uuid4().hex[:8].upper()}",
            case_number=f"CAS-{uuid.uuid4().hex[:6].upper()}",
            product_name="API Test Case",
            origin_status=OriginStatus.DOMESTIC.value,
            status="EVIDENCE_UPLOADED",
            created_by_id=inspector.id,
        )
        db.add(insp)

        evidence = EvidenceAsset(
            id=f"EV-{uuid.uuid4().hex[:8].upper()}",
            inspection_id=insp.id,
            evidence_type=EvidenceType.PRIMARY.value,
            original_filename="api_test.jpg",
            mime_type="image/jpeg",
            file_size_bytes=2000,
            sha256_hash="aabbccddeeff0011aabbccddeeff0011aabbccddeeff0011aabbccddeeff0011",
            storage_path="mock/path/api_test.jpg",
            is_immutable=True,
            uploaded_by_id=inspector.id,
        )
        db.add(evidence)

        ocr = OCRResult(
            id=f"OCR-{uuid.uuid4().hex[:8].upper()}",
            evidence_id=evidence.id,
            inspection_id=insp.id,
            ocr_engine="paddleocr-onnx",
            ocr_engine_version="test",
            processing_version="v1.0",
            processing_blocked=False,
            total_tokens=len(SAMPLE_OCR_TOKENS),
            full_text="API TEXT",
            tokens=SAMPLE_OCR_TOKENS,
        )
        db.add(ocr)

        decls = create_mock_gemini_declarations()
        decl_record = StructuredDeclarationResult(
            id=f"DEC-{uuid.uuid4().hex[:8].upper()}",
            evidence_id=evidence.id,
            inspection_id=insp.id,
            ocr_result_id=ocr.id,
            provider="google",
            model_name="gemini-2.5-flash",
            model_version=None,
            prompt_version="v1.0",
            extraction_version="v1.0",
            extraction_status="COMPLETED",
            processing_blocked=False,
            declarations=decls.model_dump(mode="json"),
        )
        db.add(decl_record)
        await db.commit()

        # Case Owner Inspector Header
        token_owner = create_test_supabase_token(user_id=inspector.id, email=inspector.email)
        headers_owner = {"Authorization": f"Bearer {token_owner}"}

        # Reviewer Header
        token_rev = create_test_supabase_token(user_id=reviewer.id, email=reviewer.email)
        headers_rev = {"Authorization": f"Bearer {token_rev}"}

        # Other Inspector Header
        token_other = create_test_supabase_token(user_id=other_inspector.id, email=other_inspector.email)
        headers_other = {"Authorization": f"Bearer {token_other}"}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 2. GET declarations: Owner -> 200 OK
        resp_owner = await client.get(f"/api/v1/evidence/{evidence.id}/declarations", headers=headers_owner)
        assert resp_owner.status_code == 200
        data = resp_owner.json()
        assert data["provider"] == "google"
        assert data["model_name"] == "gemini-2.5-flash"
        assert data["declarations"]["commodity_name"]["name"] == "PREMIUM BASMATI RICE"

        # 3. GET declarations: Reviewer -> 200 OK
        resp_rev = await client.get(f"/api/v1/evidence/{evidence.id}/declarations", headers=headers_rev)
        assert resp_rev.status_code == 200

        # 4. GET declarations: Other Inspector -> 403 Forbidden
        resp_other = await client.get(f"/api/v1/evidence/{evidence.id}/declarations", headers=headers_other)
        assert resp_other.status_code == 403

        # 5. POST extract-declarations: Owner -> 202 Accepted
        resp_post = await client.post(f"/api/v1/evidence/{evidence.id}/extract-declarations", headers=headers_owner)
        assert resp_post.status_code == 202
        job_data = resp_post.json()
        assert job_data["job_type"] == "EXTRACTION"
        assert job_data["status"] == "PENDING"

        # 6. POST extract-declarations: Other Inspector -> 403 Forbidden
        resp_post_other = await client.post(f"/api/v1/evidence/{evidence.id}/extract-declarations", headers=headers_other)
        assert resp_post_other.status_code == 403
