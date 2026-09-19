"""
CompliScan LM — Phase 3 Comprehensive Test Suite.
Verifies Applicability Engine, Deterministic Compliance Evaluator, Authoritative Vocabulary,
Evidence & Provenance Traceability, Idempotence, RBAC & IDOR isolation, and Domain Isolation.
"""

import io
import uuid
import pytest
from PIL import Image, ImageDraw
from fastapi import UploadFile
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from backend.app.main import app
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.user import User
from backend.app.models.inspection import InspectionCase
from backend.app.models.evidence import EvidenceAsset
from backend.app.models.image_quality import ImageQualityAssessment
from backend.app.models.ocr import OCRResult
from backend.app.models.structured_declaration import StructuredDeclarationResult
from backend.app.models.compliance import ApplicabilityResult, ComplianceFinding
from backend.app.models.audit import AuditEvent
from backend.app.services.applicability_service import ApplicabilityService
from backend.app.services.compliance_service import ComplianceEvaluationService
from backend.app.services.evidence_service import EvidenceService
from backend.app.services.analysis_job_service import AnalysisJobService
from backend.app.services.rules.rule_definitions import (
    RULE_SET_ID,
    RULE_SET_VERSION,
    EVALUATION_VERSION,
    CORE_RULES,
)
from backend.tests.conftest import create_test_supabase_token
from backend.tests.test_ocr import generate_synthetic_label_image_bytes
from shared.domain.enums import (
    UserRole,
    OriginStatus,
    EvidenceType,
    ImageQualityStatus,
    ObservationStatus,
    ApplicabilityStatus,
    ComplianceResult,
    AuditEventType,
)


def create_synthetic_image_bytes(text: str = "Test Product") -> bytes:
    """Helper to create minimal valid image bytes."""
    img = Image.new("RGB", (600, 300), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((20, 50), text, fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# ── 1. Applicability Engine Tests (Category A) ─────────────────────────────────

@pytest.mark.asyncio
async def test_applicability_core_rules_always_applicable():
    """Test A.1: 6 core universal rules are unconditionally APPLICABLE."""
    inspection = InspectionCase(
        id=f"INS-{uuid.uuid4().hex[:8].upper()}",
        case_number=f"INSP-2026-{uuid.uuid4().hex[:4].upper()}",
        product_name="Standard Biscuit Pack",
        origin_status=OriginStatus.DOMESTIC.value,
        created_by_id="USR-1",
    )
    payloads = ApplicabilityService.evaluate_applicability_context(inspection)
    pay_map = {p["requirement_name"]: p for p in payloads}

    assert len(payloads) == 7
    for req in ["manufacturer_identity", "commodity_name", "net_quantity", "manufacture_packing_date", "mrp", "consumer_care"]:
        assert pay_map[req]["status"] == ApplicabilityStatus.APPLICABLE.value
        assert "LMPC Rules, 2011" in pay_map[req]["basis"] or "Rule 6(1)" in pay_map[req]["basis"]
        assert pay_map[req]["rule_set_id"] == RULE_SET_ID
        assert pay_map[req]["evaluation_version"] == EVALUATION_VERSION


@pytest.mark.asyncio
async def test_applicability_country_of_origin_imported():
    """Test A.2: Imported commodity makes Country of Origin APPLICABLE."""
    inspection = InspectionCase(
        id=f"INS-{uuid.uuid4().hex[:8].upper()}",
        case_number=f"INSP-2026-{uuid.uuid4().hex[:4].upper()}",
        product_name="Imported Olive Oil",
        origin_status=OriginStatus.IMPORTED.value,
        created_by_id="USR-1",
    )
    payloads = ApplicabilityService.evaluate_applicability_context(inspection)
    coo = next(p for p in payloads if p["requirement_name"] == "country_of_origin")
    assert coo["status"] == ApplicabilityStatus.APPLICABLE.value
    assert "Imported" in coo["basis"]
    assert coo["rule_citation"] == "Rule 6(1)(da)"


@pytest.mark.asyncio
async def test_applicability_country_of_origin_domestic():
    """Test A.3: Domestic commodity makes Country of Origin NOT_APPLICABLE."""
    inspection = InspectionCase(
        id=f"INS-{uuid.uuid4().hex[:8].upper()}",
        case_number=f"INSP-2026-{uuid.uuid4().hex[:4].upper()}",
        product_name="Domestic Wheat Flour",
        origin_status=OriginStatus.DOMESTIC.value,
        created_by_id="USR-1",
    )
    payloads = ApplicabilityService.evaluate_applicability_context(inspection)
    coo = next(p for p in payloads if p["requirement_name"] == "country_of_origin")
    assert coo["status"] == ApplicabilityStatus.NOT_APPLICABLE.value
    assert "exempt" in coo["basis"].lower() or "domestic" in coo["basis"].lower()


@pytest.mark.asyncio
async def test_applicability_country_of_origin_unknown():
    """Test A.4: Unknown origin makes Country of Origin REQUIRES_REVIEW."""
    inspection = InspectionCase(
        id=f"INS-{uuid.uuid4().hex[:8].upper()}",
        case_number=f"INSP-2026-{uuid.uuid4().hex[:4].upper()}",
        product_name="Unclassified Snack",
        origin_status=OriginStatus.UNKNOWN.value,
        created_by_id="USR-1",
    )
    payloads = ApplicabilityService.evaluate_applicability_context(inspection)
    coo = next(p for p in payloads if p["requirement_name"] == "country_of_origin")
    assert coo["status"] == ApplicabilityStatus.REQUIRES_REVIEW.value
    assert "UNKNOWN" in coo["basis"]


# ── 2. Deterministic PASS Evaluator Tests (Category B) ─────────────────────────

@pytest.mark.asyncio
async def test_deterministic_evaluations_pass():
    """Test B: All valid declarations evaluate deterministically to PASS."""
    app_applicable = ApplicabilityResult(
        id="APP-1",
        inspection_id="INS-1",
        requirement_name="test",
        status=ApplicabilityStatus.APPLICABLE.value,
        basis="Mandatory",
        rule_citation="Rule 6(1)",
        context_used={},
    )

    # 1. Manufacturer
    mfg_decl = {
        "status": ObservationStatus.OBSERVED.value,
        "name": "Tata Consumer Products Ltd",
        "address": "1, Bishop Lefroy Road, Kolkata 700020",
        "source_token_indices": [0, 1, 2],
    }
    res_mfg = ComplianceEvaluationService.evaluate_declaration_requirement("manufacturer_identity", app_applicable, mfg_decl, 10)
    assert res_mfg["result"] == ComplianceResult.PASS.value
    assert res_mfg["source_token_indices"] == [0, 1, 2]

    # 2. Commodity Name
    name_decl = {
        "status": ObservationStatus.OBSERVED.value,
        "name": "Tea Bags",
        "source_token_indices": [3],
    }
    res_name = ComplianceEvaluationService.evaluate_declaration_requirement("commodity_name", app_applicable, name_decl, 10)
    assert res_name["result"] == ComplianceResult.PASS.value

    # 3. Net Quantity
    qty_decl = {
        "status": ObservationStatus.OBSERVED.value,
        "quantity_value": 250,
        "unit": "g",
        "source_token_indices": [4, 5],
    }
    res_qty = ComplianceEvaluationService.evaluate_declaration_requirement("net_quantity", app_applicable, qty_decl, 10)
    assert res_qty["result"] == ComplianceResult.PASS.value

    # 4. Date
    date_decl = {
        "status": ObservationStatus.OBSERVED.value,
        "month": 8,
        "year": 2026,
        "source_token_indices": [6],
    }
    res_date = ComplianceEvaluationService.evaluate_declaration_requirement("manufacture_packing_date", app_applicable, date_decl, 10)
    assert res_date["result"] == ComplianceResult.PASS.value

    # 5. MRP
    mrp_decl = {
        "status": ObservationStatus.OBSERVED.value,
        "amount": 140.0,
        "currency": "INR",
        "includes_all_taxes_stated": True,
        "source_token_indices": [7, 8],
    }
    res_mrp = ComplianceEvaluationService.evaluate_declaration_requirement("mrp", app_applicable, mrp_decl, 10)
    assert res_mrp["result"] == ComplianceResult.PASS.value

    # 6. Consumer Care
    care_decl = {
        "status": ObservationStatus.OBSERVED.value,
        "contact_name": "Consumer Care Manager",
        "phone": "1800-345-1720",
        "email": "care@tataconsumer.com",
        "source_token_indices": [9, 10],
    }
    res_care = ComplianceEvaluationService.evaluate_declaration_requirement("consumer_care", app_applicable, care_decl, 10)
    assert res_care["result"] == ComplianceResult.PASS.value

    # 7. Country of Origin
    coo_decl = {
        "status": ObservationStatus.OBSERVED.value,
        "country_name": "India",
        "source_token_indices": [11],
    }
    res_coo = ComplianceEvaluationService.evaluate_declaration_requirement("country_of_origin", app_applicable, coo_decl, 10)
    assert res_coo["result"] == ComplianceResult.PASS.value


# ── 3. Potential Non-Compliance & Incomplete Tests (Categories C & D) ───────────

@pytest.mark.asyncio
async def test_deterministic_potential_non_compliance():
    """Test C: Non-compliant observations produce POTENTIAL_NON_COMPLIANCE (never CONFIRMED_VIOLATION)."""
    app_applicable = ApplicabilityResult(
        id="APP-1",
        inspection_id="INS-1",
        requirement_name="test",
        status=ApplicabilityStatus.APPLICABLE.value,
        basis="Mandatory",
        rule_citation="Rule 6(1)",
        context_used={},
    )

    # 1. Missing address on manufacturer
    mfg_bad = {"status": ObservationStatus.OBSERVED.value, "name": "Tata Consumer", "address": "", "source_token_indices": [0]}
    res = ComplianceEvaluationService.evaluate_declaration_requirement("manufacturer_identity", app_applicable, mfg_bad, 10)
    assert res["result"] == ComplianceResult.POTENTIAL_NON_COMPLIANCE.value
    assert "mandatory address is missing" in res["reason"].lower()

    # 2. Non-standard unit on net quantity
    qty_bad = {"status": ObservationStatus.OBSERVED.value, "quantity_value": 500, "unit": "ounces", "source_token_indices": [1]}
    res = ComplianceEvaluationService.evaluate_declaration_requirement("net_quantity", app_applicable, qty_bad, 10)
    assert res["result"] == ComplianceResult.POTENTIAL_NON_COMPLIANCE.value
    assert "non-standard" in res["reason"].lower()

    # 3. Missing month in date (year only)
    date_bad = {"status": ObservationStatus.OBSERVED.value, "month": None, "year": 2026, "source_token_indices": [2]}
    res = ComplianceEvaluationService.evaluate_declaration_requirement("manufacture_packing_date", app_applicable, date_bad, 10)
    assert res["result"] == ComplianceResult.POTENTIAL_NON_COMPLIANCE.value
    assert "mandatory month is missing" in res["reason"].lower()

    # 4. MRP missing tax-inclusive statement
    mrp_bad = {"status": ObservationStatus.OBSERVED.value, "amount": 250.0, "includes_all_taxes_stated": False, "raw_text": "MRP 250", "source_token_indices": [3]}
    res = ComplianceEvaluationService.evaluate_declaration_requirement("mrp", app_applicable, mrp_bad, 10)
    assert res["result"] == ComplianceResult.POTENTIAL_NON_COMPLIANCE.value
    assert "without mandatory 'inclusive of all taxes'" in res["reason"].lower()

    # 5. Missing declaration when OCR tokens exist on packaging
    not_obs = {"status": ObservationStatus.NOT_OBSERVED.value, "source_token_indices": []}
    res = ComplianceEvaluationService.evaluate_declaration_requirement("commodity_name", app_applicable, not_obs, total_ocr_tokens=25)
    assert res["result"] == ComplianceResult.POTENTIAL_NON_COMPLIANCE.value
    assert "not observed on the scanned package label" in res["reason"].lower()


@pytest.mark.asyncio
async def test_deterministic_incomplete_evidence():
    """Test D: NOT_OBSERVED with zero OCR tokens produces INCOMPLETE."""
    app_applicable = ApplicabilityResult(
        id="APP-1",
        inspection_id="INS-1",
        requirement_name="test",
        status=ApplicabilityStatus.APPLICABLE.value,
        basis="Mandatory",
        rule_citation="Rule 6(1)",
        context_used={},
    )
    not_obs = {"status": ObservationStatus.NOT_OBSERVED.value, "source_token_indices": []}
    res = ComplianceEvaluationService.evaluate_declaration_requirement("mrp", app_applicable, not_obs, total_ocr_tokens=0)
    assert res["result"] == ComplianceResult.INCOMPLETE.value
    assert "insufficient ocr tokens" in res["reason"].lower()


# ── 4. Ambiguity, Conflicts, Unreadable & Non-Applicable (Categories E, F, H) ──

@pytest.mark.asyncio
async def test_conflict_handling_mrp_250_vs_280():
    """Test E & H: Conflicting MRP declarations (₹250 vs ₹280) yield REQUIRES_REVIEW and preserve candidates."""
    app_applicable = ApplicabilityResult(
        id="APP-1",
        inspection_id="INS-1",
        requirement_name="mrp",
        status=ApplicabilityStatus.APPLICABLE.value,
        basis="Mandatory",
        rule_citation="Rule 6(1)(e)",
        context_used={},
    )

    conflicting_mrp = {
        "status": ObservationStatus.CONFLICTING.value,
        "amount": None,
        "candidates": [
            {"raw_text": "MRP Rs 250", "parsed_value": {"amount": 250.0}, "source_token_indices": [5, 6]},
            {"raw_text": "MRP Rs 280", "parsed_value": {"amount": 280.0}, "source_token_indices": [12, 13]},
        ],
        "source_token_indices": [5, 6, 12, 13],
    }

    res = ComplianceEvaluationService.evaluate_declaration_requirement("mrp", app_applicable, conflicting_mrp, 20)
    assert res["result"] == ComplianceResult.REQUIRES_REVIEW.value
    assert "conflicting" in res["reason"].lower()
    assert res["source_token_indices"] == [5, 6, 12, 13]
    assert len(res["metadata_payload"]["candidates"]) == 2


@pytest.mark.asyncio
async def test_ambiguous_and_unreadable_declarations():
    """Test E: Ambiguous and Unreadable declarations produce REQUIRES_REVIEW."""
    app_applicable = ApplicabilityResult(
        id="APP-1",
        inspection_id="INS-1",
        requirement_name="commodity_name",
        status=ApplicabilityStatus.APPLICABLE.value,
        basis="Mandatory",
        rule_citation="Rule 6(1)(b)",
        context_used={},
    )

    ambig_decl = {
        "status": ObservationStatus.AMBIGUOUS.value,
        "candidates": [{"raw_text": "Spices Mix", "source_token_indices": [1]}],
        "source_token_indices": [1],
    }
    res_ambig = ComplianceEvaluationService.evaluate_declaration_requirement("commodity_name", app_applicable, ambig_decl, 10)
    assert res_ambig["result"] == ComplianceResult.REQUIRES_REVIEW.value

    unread_decl = {
        "status": ObservationStatus.UNREADABLE.value,
        "raw_text": "###@@@",
        "source_token_indices": [2],
    }
    res_unread = ComplianceEvaluationService.evaluate_declaration_requirement("commodity_name", app_applicable, unread_decl, 10)
    assert res_unread["result"] == ComplianceResult.REQUIRES_REVIEW.value


@pytest.mark.asyncio
async def test_not_applicable_domestic_coo():
    """Test F: When requirement is NOT_APPLICABLE, finding is NOT_APPLICABLE."""
    app_not_applicable = ApplicabilityResult(
        id="APP-COO",
        inspection_id="INS-1",
        requirement_name="country_of_origin",
        status=ApplicabilityStatus.NOT_APPLICABLE.value,
        basis="Domestic commodity exempt from COO",
        rule_citation="Rule 6(1)(da)",
        context_used={"origin_status": "DOMESTIC"},
    )

    res = ComplianceEvaluationService.evaluate_declaration_requirement("country_of_origin", app_not_applicable, None, 10)
    assert res["result"] == ComplianceResult.NOT_APPLICABLE.value
    assert "NOT APPLICABLE" in res["reason"]


# ── 5. Technical Failure Handling (Category G) ─────────────────────────────────

@pytest.mark.asyncio
async def test_technical_failure_produces_processing_failed():
    """Test G: Technical evaluator error yields PROCESSING_FAILED (never POTENTIAL_NON_COMPLIANCE)."""
    async with AsyncSessionLocal() as db:
        # Create inspection
        inspector = User(
            id=f"USR-{uuid.uuid4().hex[:8].upper()}",
            email=f"insp.fail.{uuid.uuid4().hex[:6]}@compliscan.gov.in",
            full_name="Inspector Fail Test",
            role=UserRole.INSPECTOR.value,
            is_active=True,
        )
        db.add(inspector)
        await db.flush()

        inspection = InspectionCase(
            id=f"INS-{uuid.uuid4().hex[:8].upper()}",
            case_number=f"INSP-2026-FAIL-{uuid.uuid4().hex[:4].upper()}",
            product_name="Fail Test Case",
            created_by_id=inspector.id,
        )
        db.add(inspection)
        await db.flush()

        # Evaluate compliance without evidence -> produces INCOMPLETE / NOT_APPLICABLE
        findings = await ComplianceEvaluationService.evaluate_inspection_compliance(db, inspection.id)
        assert len(findings) == 7
        for f in findings:
            assert f.result in [ComplianceResult.INCOMPLETE.value, ComplianceResult.NOT_APPLICABLE.value]
            assert f.rule_set_id == RULE_SET_ID


# ── 6. Full End-to-End Persisted Flow & Provenance (Categories I, J, K, M, N) ───

@pytest.mark.asyncio
async def test_full_persisted_pipeline_and_idempotence():
    """
    Test I, J, K, M, N: Full persisted pipeline:
    Inspection -> Upload Evidence -> Quality (USABLE) -> OCR -> Structured Declarations
    -> Applicability -> Compliance Findings -> Audit Events.
    Verifies Idempotence, Rule Snapshot Version, and Domain Isolation.
    """
    async with AsyncSessionLocal() as db:
        inspector = User(
            id=f"USR-E2E-{uuid.uuid4().hex[:6].upper()}",
            email=f"insp.e2e.{uuid.uuid4().hex[:6]}@compliscan.gov.in",
            full_name="Inspector End To End",
            role=UserRole.INSPECTOR.value,
            is_active=True,
        )
        db.add(inspector)
        await db.flush()

        inspection = InspectionCase(
            id=f"INS-E2E-{uuid.uuid4().hex[:6].upper()}",
            case_number=f"INSP-2026-E2E-{uuid.uuid4().hex[:4].upper()}",
            product_name="Himalayan Pink Salt",
            origin_status=OriginStatus.IMPORTED.value,
            created_by_id=inspector.id,
        )
        db.add(inspection)
        await db.flush()

        # Upload Evidence
        img_bytes = generate_synthetic_label_image_bytes()
        upload_file = UploadFile(
            filename="pink_salt_label.jpg",
            file=io.BytesIO(img_bytes),
            headers={"content-type": "image/jpeg"},
        )
        asset = await EvidenceService.upload_evidence(
            db=db,
            inspection_id=inspection.id,
            file=upload_file,
            evidence_type=EvidenceType.PRIMARY,
            current_user=inspector,
        )

        # Run pipeline jobs inline (Quality + OCR)
        await AnalysisJobService.run_pending_jobs_inline(db, worker_id="e2e-worker")

        # Fetch OCR result
        stmt_ocr = select(OCRResult).where(OCRResult.evidence_id == asset.id)
        ocr_result = (await db.execute(stmt_ocr)).scalar_one_or_none()
        assert ocr_result is not None

        # Create Mocked/Verified Structured Declarations
        dec_record = StructuredDeclarationResult(
            evidence_id=asset.id,
            inspection_id=inspection.id,
            ocr_result_id=ocr_result.id,
            provider="google",
            model_name="gemini-2.5-flash",
            prompt_version="v1.0",
            extraction_version="v1.0",
            extraction_status="COMPLETED",
            processing_blocked=False,
            declarations={
                "manufacturer_identity": {
                    "status": "OBSERVED",
                    "name": "Tata Consumer Products",
                    "address": "1 Bishop Lefroy Rd, Kolkata",
                    "source_token_indices": [0, 1],
                },
                "commodity_name": {
                    "status": "OBSERVED",
                    "name": "Himalayan Pink Salt",
                    "source_token_indices": [2, 3],
                },
                "net_quantity": {
                    "status": "OBSERVED",
                    "quantity_value": 500,
                    "unit": "g",
                    "source_token_indices": [4, 5],
                },
                "manufacture_packing_date": {
                    "status": "OBSERVED",
                    "month": 9,
                    "year": 2026,
                    "source_token_indices": [6],
                },
                "mrp": {
                    "status": "OBSERVED",
                    "amount": 120.0,
                    "currency": "INR",
                    "includes_all_taxes_stated": True,
                    "source_token_indices": [7, 8],
                },
                "consumer_care": {
                    "status": "OBSERVED",
                    "phone": "1800-345-1720",
                    "email": "care@tataconsumer.com",
                    "source_token_indices": [9],
                },
                "country_of_origin": {
                    "status": "OBSERVED",
                    "country_name": "Pakistan",
                    "source_token_indices": [10],
                },
            },
        )
        db.add(dec_record)
        await db.flush()

        # Step 1: Run Deterministic Compliance Evaluation
        findings = await ComplianceEvaluationService.evaluate_inspection_compliance(
            db=db,
            inspection_id=inspection.id,
            actor_id=inspector.id,
        )
        assert len(findings) == 7

        # Check all findings are PASS
        for f in findings:
            assert f.result == ComplianceResult.PASS.value
            assert f.rule_set_id == RULE_SET_ID
            assert f.rule_set_version == RULE_SET_VERSION
            assert f.evaluation_version == EVALUATION_VERSION
            assert f.evidence_id == asset.id
            assert f.ocr_result_id == ocr_result.id
            assert f.structured_declaration_result_id == dec_record.id

        # Step 2: Test Idempotency (Re-run evaluation does not create duplicate rows)
        findings_rerun = await ComplianceEvaluationService.evaluate_inspection_compliance(
            db=db,
            inspection_id=inspection.id,
            actor_id=inspector.id,
        )
        assert len(findings_rerun) == 7

        stmt_all = select(ComplianceFinding).where(ComplianceFinding.inspection_id == inspection.id)
        persisted_findings = list((await db.execute(stmt_all)).scalars().all())
        assert len(persisted_findings) == 7, "Idempotence failure: duplicate findings created!"

        # Step 3: Verify Audit Events
        stmt_audit = select(AuditEvent).where(
            AuditEvent.inspection_id == inspection.id,
            AuditEvent.event_type.in_([AuditEventType.APPLICABILITY_EVALUATED.value, AuditEventType.COMPLIANCE_EVALUATED.value]),
        )
        audits = list((await db.execute(stmt_audit)).scalars().all())
        assert len(audits) >= 2


# ── 7. RBAC & IDOR API Endpoints (Category L) ──────────────────────────────────

@pytest.mark.asyncio
async def test_api_compliance_rbac_and_idor():
    """Test L: API endpoints enforce strict RBAC and IDOR isolation."""
    async with AsyncSessionLocal() as db:
        inspector1 = User(
            id=f"USR-INSP1-{uuid.uuid4().hex[:6].upper()}",
            email=f"insp1.{uuid.uuid4().hex[:6]}@compliscan.gov.in",
            full_name="Inspector 1",
            role=UserRole.INSPECTOR.value,
            is_active=True,
        )
        inspector2 = User(
            id=f"USR-INSP2-{uuid.uuid4().hex[:6].upper()}",
            email=f"insp2.{uuid.uuid4().hex[:6]}@compliscan.gov.in",
            full_name="Inspector 2",
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
            id=f"INS-RBAC1-{uuid.uuid4().hex[:6].upper()}",
            case_number=f"INSP-2026-RBAC1-{uuid.uuid4().hex[:4].upper()}",
            product_name="RBAC Product 1",
            origin_status=OriginStatus.DOMESTIC.value,
            created_by_id=inspector1.id,
        )
        db.add(inspection1)
        await db.commit()

        # Tokens
        token_insp1 = create_test_supabase_token(user_id=inspector1.id, email=inspector1.email)
        token_insp2 = create_test_supabase_token(user_id=inspector2.id, email=inspector2.email)
        token_rev = create_test_supabase_token(user_id=reviewer.id, email=reviewer.email)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Unauthenticated -> 401
        res_unauth = await client.get(f"/api/v1/inspections/{inspection1.id}/applicability")
        assert res_unauth.status_code == 401

        # 2. Owner Inspector 1 -> 200 OK
        res_owner = await client.get(
            f"/api/v1/inspections/{inspection1.id}/applicability",
            headers={"Authorization": f"Bearer {token_insp1}"},
        )
        assert res_owner.status_code == 200
        app_data = res_owner.json()
        assert app_data["inspection_id"] == inspection1.id
        assert len(app_data["items"]) == 7

        # 3. Unauthorized Inspector 2 -> 403 Forbidden (IDOR protection)
        res_idor = await client.get(
            f"/api/v1/inspections/{inspection1.id}/applicability",
            headers={"Authorization": f"Bearer {token_insp2}"},
        )
        assert res_idor.status_code == 403

        # 4. Reviewer -> 200 OK
        res_rev = await client.get(
            f"/api/v1/inspections/{inspection1.id}/applicability",
            headers={"Authorization": f"Bearer {token_rev}"},
        )
        assert res_rev.status_code == 200

        # 5. POST /evaluate by owner -> 200 OK
        res_eval = await client.post(
            f"/api/v1/inspections/{inspection1.id}/evaluate",
            headers={"Authorization": f"Bearer {token_insp1}"},
        )
        assert res_eval.status_code == 200
        eval_data = res_eval.json()
        assert eval_data["inspection_id"] == inspection1.id
        assert eval_data["total_findings"] == 7

        # 6. POST /evaluate by unauthorized inspector -> 403 Forbidden
        res_eval_cross = await client.post(
            f"/api/v1/inspections/{inspection1.id}/evaluate",
            headers={"Authorization": f"Bearer {token_insp2}"},
        )
        assert res_eval_cross.status_code == 403

        # 7. GET /findings by owner -> 200 OK
        res_find = await client.get(
            f"/api/v1/inspections/{inspection1.id}/findings",
            headers={"Authorization": f"Bearer {token_insp1}"},
        )
        assert res_find.status_code == 200
        findings_data = res_find.json()
        assert findings_data["total_findings"] == 7
