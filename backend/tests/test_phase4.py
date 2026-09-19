"""
CompliScan LM — Phase 4 Comprehensive Test Suite.
Verifies Inspector Verification, Reviewer Governance, Evidence Requests (ER-xxxxx),
Revision Workflows, Atomic Finalization, FinalAuditRecord Immutability,
PDF Report Generation, RBAC/IDOR, and Full End-to-End Acceptance Workflows.
"""

import io
import uuid
import pytest
from PIL import Image, ImageDraw
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
from backend.app.models.verification import DeclarationCorrection, ManualObservation
from backend.app.models.reviewer import ReviewerDecision
from backend.app.models.evidence_request import EvidenceRequest
from backend.app.models.final_audit import FinalAuditRecord
from backend.app.models.audit import AuditEvent
from backend.app.services.verification_service import VerificationService
from backend.app.services.reviewer_service import ReviewerService
from backend.app.services.finalization_service import FinalizationService
from backend.app.services.pdf_report_service import PDFReportService
from backend.app.services.evidence_service import EvidenceService
from backend.app.services.compliance_service import ComplianceEvaluationService
from backend.app.services.applicability_service import ApplicabilityService
from backend.tests.conftest import create_test_supabase_token
from shared.domain.enums import (
    UserRole,
    OriginStatus,
    EvidenceType,
    ImageQualityStatus,
    ObservationStatus,
    ApplicabilityStatus,
    ComplianceResult,
    AuditEventType,
    ReviewerDeterminationType,
    EvidenceRequestStatus,
    FinalDecision,
)
from shared.domain.states import InspectionLifecycleState, ProcessingState, FinalizationStatus


def create_dummy_image_bytes(text: str = "CompliScan Dummy Product") -> bytes:
    img = Image.new("RGB", (600, 300), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((20, 50), text, fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


async def setup_test_users(db):
    inspector1 = User(id="USR-INSP-1", email="inspector1@compliscan.gov.in", full_name="Inspector Sharma", role=UserRole.INSPECTOR.value)
    inspector2 = User(id="USR-INSP-2", email="inspector2@compliscan.gov.in", full_name="Inspector Verma", role=UserRole.INSPECTOR.value)
    reviewer = User(id="USR-REV-1", email="reviewer@compliscan.gov.in", full_name="Reviewer Mukherjee", role=UserRole.REVIEWER.value)
    db.add_all([inspector1, inspector2, reviewer])
    await db.commit()
    return inspector1, inspector2, reviewer


async def setup_inspected_case(db, inspector_id: str, origin_status: OriginStatus = OriginStatus.DOMESTIC):
    inspection = InspectionCase(
        id=f"INS-{uuid.uuid4().hex[:8].upper()}",
        case_number=f"INSP-2026-{uuid.uuid4().hex[:4].upper()}",
        product_name="Heritage Organic Tea 500g",
        origin_status=origin_status.value,
        product_category="Food & Beverages",
        status=InspectionLifecycleState.EVALUATED.value,
        processing_state=ProcessingState.IDLE.value,
        finalization_status=FinalizationStatus.UNFINALIZED.value,
        created_by_id=inspector_id,
    )
    db.add(inspection)
    await db.flush()

    # Evidence Asset
    ev = EvidenceAsset(
        id=f"EV-{uuid.uuid4().hex[:8].upper()}",
        inspection_id=inspection.id,
        evidence_type=EvidenceType.PRIMARY.value,
        original_filename="front_panel.jpg",
        mime_type="image/jpeg",
        file_size_bytes=10240,
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        storage_path="/tmp/front_panel.jpg",
        uploaded_by_id=inspector_id,
    )
    db.add(ev)
    await db.flush()

    # Applicability & Compliance Findings
    app_recs = await ApplicabilityService.evaluate_and_persist(db, inspection.id, inspector_id)
    findings = await ComplianceEvaluationService.evaluate_inspection_compliance(db, inspection.id, inspector_id)
    await db.commit()
    return inspection, ev, app_recs, findings


# ── 1. State Machine & Inspector Verification Tests (Categories A & B) ──────────

@pytest.mark.asyncio
async def test_inspector_verification_and_state_transitions():
    async with AsyncSessionLocal() as db:
        insp1, _, rev = await setup_test_users(db)
        case, ev, _, findings = await setup_inspected_case(db, insp1.id)

        # 1. Verification State inspection
        vstate = await VerificationService.get_verification_state(db, case.id)
        assert vstate.is_ready_for_submission is True
        assert len(vstate.blocking_reasons) == 0

        # 2. Inspector adds Declaration Correction
        from backend.app.schemas.verification import DeclarationCorrectionCreate, ManualObservationCreate
        cor = await VerificationService.add_declaration_correction(
            db=db,
            inspection_id=case.id,
            inspector_id=insp1.id,
            correction_in=DeclarationCorrectionCreate(
                requirement_name="manufacturer_identity",
                field_name="name",
                previous_value={"name": "Hertage Tea"},
                corrected_value={"name": "Heritage Tea Private Limited"},
                reason="Corrected spelling from physical package inspection",
                evidence_id=ev.id,
            ),
        )
        assert cor.id.startswith("COR-")
        assert cor.requirement_name == "manufacturer_identity"

        # 3. Inspector adds Manual Observation
        obs = await VerificationService.add_manual_observation(
            db=db,
            inspection_id=case.id,
            inspector_id=insp1.id,
            observation_in=ManualObservationCreate(
                requirement_name="consumer_care",
                observation_text="Consumer care number verified clearly visible on side panel",
            ),
        )
        assert obs.id.startswith("OBS-")
        assert obs.requirement_name == "consumer_care"

        # 4. Check audit events recorded
        audit_events = (await db.execute(select(AuditEvent).where(AuditEvent.inspection_id == case.id))).scalars().all()
        event_types = [a.event_type for a in audit_events]
        assert AuditEventType.DECLARATION_MANUALLY_CORRECTED.value in event_types
        assert AuditEventType.MANUAL_OBSERVATION_RECORDED.value in event_types


# ── 2. Inspector Submission Tests (Category C) ─────────────────────────────────

@pytest.mark.asyncio
async def test_inspector_submission_for_review():
    async with AsyncSessionLocal() as db:
        insp1, _, _ = await setup_test_users(db)
        case, _, _, _ = await setup_inspected_case(db, insp1.id)

        from backend.app.schemas.verification import VerificationSubmitRequest
        submitted_case = await VerificationService.submit_for_review(
            db=db,
            inspection_id=case.id,
            inspector_id=insp1.id,
            submit_in=VerificationSubmitRequest(notes="All 7 mandatory declarations verified"),
        )
        assert submitted_case.status == InspectionLifecycleState.SUBMITTED_FOR_REVIEW.value
        assert submitted_case.submitted_at is not None

        # Check audit event
        audit_events = (await db.execute(select(AuditEvent).where(AuditEvent.inspection_id == case.id))).scalars().all()
        event_types = [a.event_type for a in audit_events]
        assert AuditEventType.INSPECTION_SUBMITTED_FOR_REVIEW.value in event_types


# ── 3. Reviewer Governance, Decision & Override Tests (Categories D & E) ────────

@pytest.mark.asyncio
async def test_reviewer_queue_and_decisions():
    async with AsyncSessionLocal() as db:
        insp1, _, rev = await setup_test_users(db)
        case, _, _, findings = await setup_inspected_case(db, insp1.id)
        await VerificationService.submit_for_review(db, case.id, insp1.id)

        # 1. Review Queue
        queue = await ReviewerService.get_review_queue(db)
        assert len(queue) >= 1
        queue_item = next(q for q in queue if q.id == case.id)
        assert queue_item.case_number == case.case_number
        assert queue_item.inspector_name == "Inspector Sharma"

        # 2. Record Reviewer Confirmation
        from backend.app.schemas.reviewer import ReviewerDecisionCreate
        finding_mrp = next(f for f in findings if f.requirement_name == "mrp")
        dec_confirm = await ReviewerService.record_reviewer_decision(
            db=db,
            inspection_id=case.id,
            reviewer_id=rev.id,
            decision_in=ReviewerDecisionCreate(
                requirement_name="mrp",
                determination=ReviewerDeterminationType.CONFIRMED,
                adjudicated_result=ComplianceResult(finding_mrp.result),
                rationale="MRP declaration verified with statutory inclusive of all taxes wording",
                finding_id=finding_mrp.id,
            ),
        )
        assert dec_confirm.is_override is False
        assert dec_confirm.adjudicated_result == finding_mrp.result
        # Ensure finding.result was NOT mutated
        assert finding_mrp.result in (ComplianceResult.PASS.value, ComplianceResult.POTENTIAL_NON_COMPLIANCE.value, ComplianceResult.INCOMPLETE.value)

        # 3. Record Reviewer Override with mandatory rationale
        finding_coo = next(f for f in findings if f.requirement_name == "country_of_origin")
        dec_override = await ReviewerService.record_reviewer_decision(
            db=db,
            inspection_id=case.id,
            reviewer_id=rev.id,
            decision_in=ReviewerDecisionCreate(
                requirement_name="country_of_origin",
                determination=ReviewerDeterminationType.OVERRIDDEN,
                adjudicated_result=ComplianceResult.PASS,
                rationale="Reviewer confirmed domestic manufacturer declaration serves as origin proof per Rule 6(1)(da)",
                finding_id=finding_coo.id,
            ),
        )
        assert dec_override.is_override is True
        assert dec_override.determination == ReviewerDeterminationType.OVERRIDDEN.value

        # Check audit event
        audit_events = (await db.execute(select(AuditEvent).where(AuditEvent.inspection_id == case.id))).scalars().all()
        event_types = [a.event_type for a in audit_events]
        assert AuditEventType.REVIEWER_DECISION_RECORDED.value in event_types
        assert AuditEventType.REVIEWER_OVERRIDE_RECORDED.value in event_types


# ── 4. Evidence Request Workflow Tests (Category F) ────────────────────────────

@pytest.mark.asyncio
async def test_evidence_request_workflow():
    async with AsyncSessionLocal() as db:
        insp1, _, rev = await setup_test_users(db)
        case, ev1, _, _ = await setup_inspected_case(db, insp1.id)
        await VerificationService.submit_for_review(db, case.id, insp1.id)

        # 1. Reviewer creates Evidence Request
        from backend.app.schemas.reviewer import EvidenceRequestCreate, EvidenceRequestFulfillRequest
        er = await ReviewerService.create_evidence_request(
            db=db,
            inspection_id=case.id,
            reviewer_id=rev.id,
            er_in=EvidenceRequestCreate(
                requirement_name="consumer_care",
                request_reason="Consumer care telephone number is partially obscured by glare",
                requested_condition="Provide clear, well-lit photo of rear panel consumer care box",
                requested_evidence_type="SUPPLEMENTAL",
            ),
        )
        assert er.id.startswith("ER-")
        assert er.status == EvidenceRequestStatus.OPEN.value

        # 2. Inspector uploads new evidence asset to fulfill request
        ev2 = EvidenceAsset(
            id=f"EV-{uuid.uuid4().hex[:8].upper()}",
            inspection_id=case.id,
            evidence_type=EvidenceType.SUPPLEMENTAL.value,
            original_filename="rear_panel_clear.jpg",
            mime_type="image/jpeg",
            file_size_bytes=15000,
            sha256_hash="f4c8996fb92427ae41e4649b934ca495991b7852b855e3b0c44298fc1c149afb",
            storage_path="/tmp/rear_panel_clear.jpg",
            uploaded_by_id=insp1.id,
        )
        db.add(ev2)
        await db.flush()

        # 3. Fulfill request
        fulfilled_er = await ReviewerService.fulfill_evidence_request(
            db=db,
            er_id=er.id,
            user_id=insp1.id,
            fulfill_in=EvidenceRequestFulfillRequest(
                evidence_id=ev2.id,
                response_note="Uploaded high-resolution macro photo of consumer care details",
            ),
        )
        assert fulfilled_er.status == EvidenceRequestStatus.FULFILLED.value
        assert fulfilled_er.response_evidence_id == ev2.id

        # Check audit event
        audit_events = (await db.execute(select(AuditEvent).where(AuditEvent.inspection_id == case.id))).scalars().all()
        event_types = [a.event_type for a in audit_events]
        assert AuditEventType.EVIDENCE_REQUEST_CREATED.value in event_types
        assert AuditEventType.EVIDENCE_REQUEST_FULFILLED.value in event_types


# ── 5. Revision Workflow Tests (Category G) ────────────────────────────────────

@pytest.mark.asyncio
async def test_revision_workflow():
    async with AsyncSessionLocal() as db:
        insp1, _, rev = await setup_test_users(db)
        case, _, _, _ = await setup_inspected_case(db, insp1.id)
        await VerificationService.submit_for_review(db, case.id, insp1.id)

        # 1. Reviewer requests revision
        from backend.app.schemas.reviewer import ReviewRevisionRequest
        revised_case = await ReviewerService.request_revision(
            db=db,
            inspection_id=case.id,
            reviewer_id=rev.id,
            revision_in=ReviewRevisionRequest(
                reason="Net quantity unit is ambiguously extracted as 'gms' instead of standard 'g'",
                requested_changes="Please correct net quantity declaration and verify standard unit compliance",
            ),
        )
        assert revised_case.status == InspectionLifecycleState.REQUIRES_REVISION.value

        # 2. Inspector corrects and resubmits
        from backend.app.schemas.verification import DeclarationCorrectionCreate
        await VerificationService.add_declaration_correction(
            db=db,
            inspection_id=case.id,
            inspector_id=insp1.id,
            correction_in=DeclarationCorrectionCreate(
                requirement_name="net_quantity",
                field_name="unit",
                previous_value={"value": 500, "unit": "gms"},
                corrected_value={"value": 500, "unit": "g"},
                reason="Normalized unit symbol to statutory standard per Schedule VI",
            ),
        )

        resubmitted_case = await VerificationService.submit_for_review(db, case.id, insp1.id)
        assert resubmitted_case.status == InspectionLifecycleState.SUBMITTED_FOR_REVIEW.value


# ── 6. Finalization & FinalAuditRecord Immutability Tests (Categories H, I, J) ──

@pytest.mark.asyncio
async def test_atomic_finalization_and_immutability():
    async with AsyncSessionLocal() as db:
        insp1, _, rev = await setup_test_users(db)
        case, ev, app_recs, findings = await setup_inspected_case(db, insp1.id)
        await VerificationService.submit_for_review(db, case.id, insp1.id)

        # Adjudicate all findings
        from backend.app.schemas.reviewer import ReviewerDecisionCreate, FinalizeInspectionRequest
        for f in findings:
            await ReviewerService.record_reviewer_decision(
                db=db,
                inspection_id=case.id,
                reviewer_id=rev.id,
                decision_in=ReviewerDecisionCreate(
                    requirement_name=f.requirement_name,
                    determination=ReviewerDeterminationType.CONFIRMED,
                    adjudicated_result=ComplianceResult.PASS,
                    rationale="Statutory declaration compliant with LMPC Rules, 2011",
                    finding_id=f.id,
                ),
            )

        # Finalize atomically
        far = await FinalizationService.finalize_inspection(
            db=db,
            inspection_id=case.id,
            reviewer_id=rev.id,
            finalize_in=FinalizeInspectionRequest(
                final_decision=FinalDecision.COMPLIANT,
                final_rationale="All pre-packaged commodity mandatory declarations verified compliant under Legal Metrology Rules, 2011",
            ),
        )

        assert far.id.startswith("FAR-")
        assert far.final_decision == FinalDecision.COMPLIANT.value
        assert far.inspection_id == case.id
        assert len(far.evidence_snapshot) >= 1
        assert len(far.compliance_findings_snapshot) == len(findings)
        assert len(far.reviewer_decisions_snapshot) == len(findings)

        # Verify inspection is now FINALIZED and READ_ONLY
        await db.refresh(case)
        assert case.status == InspectionLifecycleState.FINALIZED.value
        assert case.finalization_status == FinalizationStatus.READ_ONLY.value

        # Category I: Immutability Verification - Attempt mutations on finalized case
        from backend.app.core.errors import ConflictError, InvalidStateError

        # 1. Attempt declaration correction
        with pytest.raises(ConflictError):
            from backend.app.schemas.verification import DeclarationCorrectionCreate
            await VerificationService.add_declaration_correction(
                db=db,
                inspection_id=case.id,
                inspector_id=insp1.id,
                correction_in=DeclarationCorrectionCreate(
                    requirement_name="mrp",
                    corrected_value={"mrp": 100},
                    reason="Invalid post-finalization attempt",
                ),
            )

        # 2. Attempt reviewer decision mutation
        with pytest.raises(ConflictError):
            await ReviewerService.record_reviewer_decision(
                db=db,
                inspection_id=case.id,
                reviewer_id=rev.id,
                decision_in=ReviewerDecisionCreate(
                    requirement_name="mrp",
                    determination=ReviewerDeterminationType.OVERRIDDEN,
                    adjudicated_result=ComplianceResult.POTENTIAL_NON_COMPLIANCE,
                    rationale="Invalid post-finalization attempt",
                ),
            )

        # 3. Attempt duplicate finalization
        with pytest.raises(ConflictError):
            await FinalizationService.finalize_inspection(
                db=db,
                inspection_id=case.id,
                reviewer_id=rev.id,
                finalize_in=FinalizeInspectionRequest(
                    final_decision=FinalDecision.COMPLIANT,
                    final_rationale="Duplicate attempt",
                ),
            )


# ── 7. PDF Report Generation Tests (Category K) ────────────────────────────────

@pytest.mark.asyncio
async def test_pdf_report_generation():
    async with AsyncSessionLocal() as db:
        insp1, _, rev = await setup_test_users(db)
        case, _, _, findings = await setup_inspected_case(db, insp1.id)
        await VerificationService.submit_for_review(db, case.id, insp1.id)

        from backend.app.schemas.reviewer import ReviewerDecisionCreate, FinalizeInspectionRequest
        for f in findings:
            await ReviewerService.record_reviewer_decision(
                db=db,
                inspection_id=case.id,
                reviewer_id=rev.id,
                decision_in=ReviewerDecisionCreate(
                    requirement_name=f.requirement_name,
                    determination=ReviewerDeterminationType.CONFIRMED,
                    adjudicated_result=ComplianceResult.PASS,
                    rationale="Statutory declaration compliant with LMPC Rules, 2011",
                    finding_id=f.id,
                ),
            )

        far = await FinalizationService.finalize_inspection(
            db=db,
            inspection_id=case.id,
            reviewer_id=rev.id,
            finalize_in=FinalizeInspectionRequest(
                final_decision=FinalDecision.COMPLIANT,
                final_rationale="Product packaging meets all Legal Metrology standards",
            ),
        )

        pdf_bytes = PDFReportService.generate_pdf_report(far)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 1000
        # PDF Header signature check
        assert pdf_bytes.startswith(b"%PDF-")


# ── 8. RBAC / IDOR API Endpoints Tests (Category L) ────────────────────────────

@pytest.mark.asyncio
async def test_rbac_and_idor_api_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        async with AsyncSessionLocal() as db:
            insp1, insp2, rev = await setup_test_users(db)
            case, _, _, findings = await setup_inspected_case(db, insp1.id)

        token_insp1 = create_test_supabase_token(user_id=insp1.id, email=insp1.email)
        token_insp2 = create_test_supabase_token(user_id=insp2.id, email=insp2.email)
        token_rev = create_test_supabase_token(user_id=rev.id, email=rev.email)

        # 1. Cross-inspector IDOR test: Inspector 2 cannot submit Inspector 1's case
        res_idor = await client.post(
            f"/api/v1/inspections/{case.id}/submit-for-review",
            headers={"Authorization": f"Bearer {token_insp2}"},
            json={},
        )
        assert res_idor.status_code == 403

        # 2. Inspector 1 submits own case
        res_submit = await client.post(
            f"/api/v1/inspections/{case.id}/submit-for-review",
            headers={"Authorization": f"Bearer {token_insp1}"},
            json={"notes": "Ready for governance"},
        )
        assert res_submit.status_code == 200

        # 3. RBAC test: Inspector cannot finalize case
        res_insp_finalize = await client.post(
            f"/api/v1/inspections/{case.id}/finalize",
            headers={"Authorization": f"Bearer {token_insp1}"},
            json={"final_decision": "COMPLIANT", "final_rationale": "Unauthorized finalize attempt"},
        )
        assert res_insp_finalize.status_code == 403

        # 4. Reviewer accesses review queue
        res_queue = await client.get(
            "/api/v1/reviews/queue",
            headers={"Authorization": f"Bearer {token_rev}"},
        )
        assert res_queue.status_code == 200
        assert len(res_queue.json()) >= 1


# ── 9. End-to-End Golden Path Acceptance Test (Category M) ─────────────────────

@pytest.mark.asyncio
async def test_full_e2e_golden_path():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        async with AsyncSessionLocal() as db:
            insp1, _, rev = await setup_test_users(db)

        token_insp = create_test_supabase_token(user_id=insp1.id, email=insp1.email)
        token_rev = create_test_supabase_token(user_id=rev.id, email=rev.email)

        # Step 1: Create Inspection
        res_create = await client.post(
            "/api/v1/inspections",
            headers={"Authorization": f"Bearer {token_insp}"},
            json={
                "product_name": "Premium Basmati Rice 5kg",
                "origin_status": "DOMESTIC",
                "product_category": "Food & Grains",
            },
        )
        assert res_create.status_code == 201
        case_id = res_create.json()["id"]

        # Step 2: Upload Evidence Asset
        img_bytes = create_dummy_image_bytes("Basmati Rice 5kg Net Wt")
        res_upload = await client.post(
            f"/api/v1/inspections/{case_id}/evidence",
            headers={"Authorization": f"Bearer {token_insp}"},
            files={"file": ("rice_label.jpg", img_bytes, "image/jpeg")},
            data={"evidence_type": "PRIMARY"},
        )
        assert res_upload.status_code == 201
        ev_id = res_upload.json()["id"]

        # Step 3: Run Deterministic Compliance Evaluation
        res_eval = await client.post(
            f"/api/v1/inspections/{case_id}/evaluate",
            headers={"Authorization": f"Bearer {token_insp}"},
        )
        assert res_eval.status_code == 200
        findings = res_eval.json()["findings"]
        assert len(findings) >= 6

        # Step 4: Inspector records Manual Correction and Observation
        res_cor = await client.post(
            f"/api/v1/inspections/{case_id}/corrections",
            headers={"Authorization": f"Bearer {token_insp}"},
            json={
                "requirement_name": "net_quantity",
                "field_name": "quantity",
                "previous_value": {"value": 5000, "unit": "g"},
                "corrected_value": {"value": 5, "unit": "kg"},
                "reason": "Corrected unit display to standard retail format",
                "evidence_id": ev_id,
            },
        )
        assert res_cor.status_code == 201

        res_obs = await client.post(
            f"/api/v1/inspections/{case_id}/manual-observations",
            headers={"Authorization": f"Bearer {token_insp}"},
            json={
                "requirement_name": "general_packaging",
                "observation_text": "Packaging tamper seal is fully intact and verified",
            },
        )
        assert res_obs.status_code == 201

        # Step 5: Inspector submits case for Review
        res_submit = await client.post(
            f"/api/v1/inspections/{case_id}/submit-for-review",
            headers={"Authorization": f"Bearer {token_insp}"},
            json={"notes": "Submitted with verified 5kg net quantity"},
        )
        assert res_submit.status_code == 200
        assert res_submit.json()["status"] == "SUBMITTED_FOR_REVIEW"

        # Step 6: Reviewer adjudicates findings
        for f in findings:
            res_dec = await client.post(
                f"/api/v1/inspections/{case_id}/reviewer-decisions",
                headers={"Authorization": f"Bearer {token_rev}"},
                json={
                    "requirement_name": f["requirement_name"],
                    "determination": "CONFIRMED",
                    "adjudicated_result": "PASS",
                    "rationale": "Adjudicated compliant per statutory requirements under Rule 6",
                    "finding_id": f["id"],
                },
            )
            assert res_dec.status_code == 201

        # Step 7: Reviewer Finalizes Inspection
        res_finalize = await client.post(
            f"/api/v1/inspections/{case_id}/finalize",
            headers={"Authorization": f"Bearer {token_rev}"},
            json={
                "final_decision": "COMPLIANT",
                "final_rationale": "Commodity packaging conforms with all Legal Metrology Packaged Commodities Rules",
            },
        )
        assert res_finalize.status_code == 201
        far_data = res_finalize.json()
        assert far_data["id"].startswith("FAR-")
        assert far_data["final_decision"] == "COMPLIANT"

        # Step 8: Fetch Immutable Final Record & PDF Report
        res_far = await client.get(
            f"/api/v1/inspections/{case_id}/final-record",
            headers={"Authorization": f"Bearer {token_insp}"},
        )
        assert res_far.status_code == 200

        res_pdf = await client.get(
            f"/api/v1/inspections/{case_id}/final-report",
            headers={"Authorization": f"Bearer {token_insp}"},
        )
        assert res_pdf.status_code == 200
        assert res_pdf.headers["content-type"] == "application/pdf"
        assert res_pdf.content.startswith(b"%PDF-")

        # Step 9: Attempt mutation on finalized case - Backend Rejection
        res_mut = await client.post(
            f"/api/v1/inspections/{case_id}/corrections",
            headers={"Authorization": f"Bearer {token_insp}"},
            json={
                "requirement_name": "mrp",
                "corrected_value": {"mrp": 500},
                "reason": "Forbidden post-finalization edit",
            },
        )
        assert res_mut.status_code in (400, 409)
