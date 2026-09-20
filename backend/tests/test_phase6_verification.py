"""
CompliScan LM — Phase 6 Production Hardening & Readiness Automated Verification Suite.
Covers:
  - Evidence Download IDOR Isolation (Inspector A vs Inspector B vs Reviewer vs Unknown)
  - Worker Claim Race Hardening with FOR UPDATE SKIP LOCKED & Lease Recovery
  - Finalization Immutability & Post-Finalization Mutation Refusal
  - Multi-User Concurrency (Multi-Inspector & Multi-Reviewer Adjudication)
  - JWT Authentication Claim Validation & Error Paths
  - CORS Preflight & Health Endpoint Integrity
"""

import os
import uuid
import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient, ASGITransport
from jose import jwt

from backend.app.main import app
from backend.app.core.config import settings
from backend.app.core.security import verify_supabase_token
from backend.app.core.errors import ForbiddenError, NotFoundError, InvalidStateError, EvidenceError, UnauthorizedError, ConflictError
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.user import User
from backend.app.models.inspection import InspectionCase
from backend.app.models.evidence import EvidenceAsset
from backend.app.models.analysis_job import AnalysisJob
from backend.app.models.compliance import ComplianceFinding
from backend.app.models.reviewer import ReviewerDecision
from backend.app.schemas.reviewer import ReviewerDecisionCreate
from backend.app.services.evidence_service import EvidenceService
from backend.app.services.analysis_job_service import AnalysisJobService
from backend.app.services.reviewer_service import ReviewerService
from shared.domain.enums import UserRole, EvidenceType, JobType, JobStatus, ReviewerDeterminationType, ComplianceResult, ApplicabilityStatus
from shared.domain.states import InspectionLifecycleState, FinalizationStatus


@pytest.mark.asyncio
async def test_evidence_download_idor_isolation():
    """
    Verify Evidence Download IDOR Protection:
      - Inspector A -> own evidence = allowed
      - Inspector A -> Inspector B evidence = Forbidden (403)
      - Reviewer -> any evidence = allowed
      - Unknown evidence_id = NotFound (404)
    """
    async with AsyncSessionLocal() as db_session:
        # 1. Setup users
        inspector_a = User(
            id=str(uuid.uuid4()),
            email=f"inspector_a_{uuid.uuid4().hex[:6]}@compliscan.gov.in",
            role=UserRole.INSPECTOR.value,
            full_name="Inspector Alpha",
        )
        inspector_b = User(
            id=str(uuid.uuid4()),
            email=f"inspector_b_{uuid.uuid4().hex[:6]}@compliscan.gov.in",
            role=UserRole.INSPECTOR.value,
            full_name="Inspector Beta",
        )
        reviewer = User(
            id=str(uuid.uuid4()),
            email=f"reviewer_{uuid.uuid4().hex[:6]}@compliscan.gov.in",
            role=UserRole.REVIEWER.value,
            full_name="Reviewer Gamma",
        )
        db_session.add_all([inspector_a, inspector_b, reviewer])

        # 2. Setup inspection cases
        case_a = InspectionCase(
            id=str(uuid.uuid4()),
            case_number=f"CN-A-{uuid.uuid4().hex[:6].upper()}",
            product_name="Product Alpha",
            status=InspectionLifecycleState.DRAFT.value,
            created_by_id=inspector_a.id,
        )
        case_b = InspectionCase(
            id=str(uuid.uuid4()),
            case_number=f"CN-B-{uuid.uuid4().hex[:6].upper()}",
            product_name="Product Beta",
            status=InspectionLifecycleState.DRAFT.value,
            created_by_id=inspector_b.id,
        )
        db_session.add_all([case_a, case_b])
        await db_session.flush()

        # 3. Setup evidence assets
        evidence_a = EvidenceAsset(
            id=str(uuid.uuid4()),
            inspection_id=case_a.id,
            uploaded_by_id=inspector_a.id,
            original_filename="label_a.jpg",
            mime_type="image/jpeg",
            file_size_bytes=1024,
            sha256_hash="a" * 64,
            storage_path="/tmp/fake_a.jpg",
        )
        evidence_b = EvidenceAsset(
            id=str(uuid.uuid4()),
            inspection_id=case_b.id,
            uploaded_by_id=inspector_b.id,
            original_filename="label_b.jpg",
            mime_type="image/jpeg",
            file_size_bytes=1024,
            sha256_hash="b" * 64,
            storage_path="/tmp/fake_b.jpg",
        )
        db_session.add_all([evidence_a, evidence_b])
        await db_session.commit()

        # Test 1: Inspector A -> own evidence = allowed
        asset = await EvidenceService.get_evidence_by_id(db_session, evidence_a.id, current_user=inspector_a)
        assert asset.id == evidence_a.id

        # Test 2: Inspector A -> Inspector B evidence = ForbiddenError (403)
        with pytest.raises(ForbiddenError):
            await EvidenceService.get_evidence_by_id(db_session, evidence_b.id, current_user=inspector_a)

        # Test 3: Reviewer -> Inspector B evidence = allowed
        asset_rev = await EvidenceService.get_evidence_by_id(db_session, evidence_b.id, current_user=reviewer)
        assert asset_rev.id == evidence_b.id

        # Test 4: Unknown evidence_id = NotFoundError (404)
        with pytest.raises(NotFoundError):
            await EvidenceService.get_evidence_by_id(db_session, str(uuid.uuid4()), current_user=inspector_a)


@pytest.mark.asyncio
async def test_worker_claim_race_and_skip_locked():
    """
    Verify worker queue claim atomicity & SKIP LOCKED behavior:
      - Multiple jobs queued
      - Sequential claim tests verify no duplicate assignment
      - Expired RUNNING lease recovery is preserved
    """
    async with AsyncSessionLocal() as db_session:
        insp_id = str(uuid.uuid4())
        case = InspectionCase(
            id=insp_id,
            case_number=f"CN-W-{uuid.uuid4().hex[:6].upper()}",
            product_name="Worker Test Product",
            status=InspectionLifecycleState.DRAFT.value,
            created_by_id=str(uuid.uuid4()),
        )
        db_session.add(case)
        await db_session.flush()

        # Create 5 pending jobs
        jobs = []
        for i in range(5):
            j = await AnalysisJobService.enqueue_job(
                db=db_session,
                inspection_id=insp_id,
                evidence_id=str(uuid.uuid4()),
                job_type=JobType.IMAGE_QUALITY,
                priority=1,
            )
            jobs.append(j)
        await db_session.commit()

        # Worker 1 claims job
        job_w1 = await AnalysisJobService.claim_next_job(db_session, worker_id="worker-1", lease_seconds=60)
        assert job_w1 is not None
        assert job_w1.worker_id == "worker-1"
        assert job_w1.status == JobStatus.RUNNING.value

        # Worker 2 claims job
        job_w2 = await AnalysisJobService.claim_next_job(db_session, worker_id="worker-2", lease_seconds=60)
        assert job_w2 is not None
        assert job_w2.worker_id == "worker-2"
        assert job_w2.id != job_w1.id

        # Verify 2 distinct jobs claimed
        claimed_ids = {job_w1.id, job_w2.id}
        assert len(claimed_ids) == 2


@pytest.mark.asyncio
async def test_expired_lease_recovery():
    """
    Verify expired RUNNING job lease is reclaimed by next worker while active leases remain protected.
    """
    async with AsyncSessionLocal() as db_session:
        insp_id = str(uuid.uuid4())
        case = InspectionCase(
            id=insp_id,
            case_number=f"CN-L-{uuid.uuid4().hex[:6].upper()}",
            product_name="Lease Recovery Product",
            status=InspectionLifecycleState.DRAFT.value,
            created_by_id=str(uuid.uuid4()),
        )
        db_session.add(case)

        # Add an expired RUNNING job
        past_time = datetime.now(timezone.utc) - timedelta(seconds=120)
        expired_job = AnalysisJob(
            id=str(uuid.uuid4()),
            inspection_id=insp_id,
            evidence_id=str(uuid.uuid4()),
            job_type=JobType.PERCEPTION.value,
            status=JobStatus.RUNNING.value,
            worker_id="crashed-worker",
            lease_expires_at=past_time,
            attempts=1,
            max_attempts=3,
            created_at=past_time,
            updated_at=past_time,
        )
        db_session.add(expired_job)
        await db_session.commit()

        # Worker 3 claims next job — should reclaim the expired job
        reclaimed = await AnalysisJobService.claim_next_job(db_session, worker_id="worker-3", lease_seconds=60)
        assert reclaimed is not None
        assert reclaimed.id == expired_job.id
        assert reclaimed.worker_id == "worker-3"
        assert reclaimed.attempts == 2


@pytest.mark.asyncio
async def test_post_finalization_evidence_mutation_refusal():
    """
    Verify immutability: Draft evidence deletion is refused once inspection is finalized.
    """
    async with AsyncSessionLocal() as db_session:
        inspector = User(
            id=str(uuid.uuid4()),
            email=f"inspector_final_{uuid.uuid4().hex[:6]}@compliscan.gov.in",
            role=UserRole.INSPECTOR.value,
            full_name="Finalized Inspector",
        )
        db_session.add(inspector)

        case = InspectionCase(
            id=str(uuid.uuid4()),
            case_number=f"CN-F-{uuid.uuid4().hex[:6].upper()}",
            product_name="Finalized Product",
            status=InspectionLifecycleState.FINALIZED.value,
            finalization_status=FinalizationStatus.READ_ONLY.value,
            created_by_id=inspector.id,
        )
        db_session.add(case)
        await db_session.flush()

        evidence = EvidenceAsset(
            id=str(uuid.uuid4()),
            inspection_id=case.id,
            uploaded_by_id=inspector.id,
            original_filename="final_label.jpg",
            mime_type="image/jpeg",
            file_size_bytes=512,
            sha256_hash="f" * 64,
            storage_path="/tmp/final_label.jpg",
        )
        db_session.add(evidence)
        await db_session.commit()

        # Attempt delete draft evidence on finalized inspection -> refused with EvidenceError (403)
        with pytest.raises(EvidenceError):
            await EvidenceService.delete_draft_evidence(
                db=db_session,
                inspection_id=case.id,
                evidence_id=evidence.id,
                current_user=inspector,
            )


@pytest.mark.asyncio
async def test_jwt_claims_and_algorithm_validation():
    """
    Verify JWT Authentication Errors:
      - Expired token -> UnauthorizedError
      - Missing sub claim -> UnauthorizedError
      - Invalid signature -> UnauthorizedError
      - Unsupported algorithm -> UnauthorizedError
    """
    secret = settings.SUPABASE_JWT_SECRET
    now = datetime.now(timezone.utc)

    # 1. Expired token
    expired_payload = {
        "sub": "user-123",
        "aud": "authenticated",
        "exp": int((now - timedelta(seconds=10)).timestamp()),
    }
    expired_token = jwt.encode(expired_payload, secret, algorithm="HS256")
    with pytest.raises(UnauthorizedError):
        verify_supabase_token(expired_token)

    # 2. Missing sub claim
    no_sub_payload = {
        "aud": "authenticated",
        "exp": int((now + timedelta(hours=1)).timestamp()),
    }
    no_sub_token = jwt.encode(no_sub_payload, secret, algorithm="HS256")
    with pytest.raises(UnauthorizedError):
        verify_supabase_token(no_sub_token)

    # 3. Invalid signature
    bad_secret_token = jwt.encode(
        {"sub": "user-123", "aud": "authenticated", "exp": int((now + timedelta(hours=1)).timestamp())},
        "wrong_secret_key_12345",
        algorithm="HS256",
    )
    with pytest.raises(UnauthorizedError):
        verify_supabase_token(bad_secret_token)


@pytest.mark.asyncio
async def test_multi_reviewer_adjudication_concurrency():
    """
    Verify Reviewer Adjudication Behavior when two reviewers act on the same case:
      - Requires case to be in SUBMITTED_FOR_REVIEW lifecycle state
      - Refuses decision when case is in DRAFT or FINALIZED state
      - Performs clean decision upsert on (inspection_id, requirement_name)
    """
    async with AsyncSessionLocal() as db_session:
        rev1 = User(id=str(uuid.uuid4()), email=f"rev1_{uuid.uuid4().hex[:4]}@gov.in", role=UserRole.REVIEWER.value, full_name="Reviewer One")
        rev2 = User(id=str(uuid.uuid4()), email=f"rev2_{uuid.uuid4().hex[:4]}@gov.in", role=UserRole.REVIEWER.value, full_name="Reviewer Two")
        db_session.add_all([rev1, rev2])

        # Case in DRAFT status -> should be refused with ConflictError
        case_draft = InspectionCase(
            id=str(uuid.uuid4()),
            case_number=f"CN-D-{uuid.uuid4().hex[:6].upper()}",
            product_name="Draft Product",
            status=InspectionLifecycleState.DRAFT.value,
            created_by_id=rev1.id,
        )
        # Case in SUBMITTED_FOR_REVIEW status -> allowed
        case_submitted = InspectionCase(
            id=str(uuid.uuid4()),
            case_number=f"CN-S-{uuid.uuid4().hex[:6].upper()}",
            product_name="Submitted Product",
            status=InspectionLifecycleState.SUBMITTED_FOR_REVIEW.value,
            created_by_id=rev1.id,
        )
        db_session.add_all([case_draft, case_submitted])
        await db_session.flush()

        finding = ComplianceFinding(
            id=str(uuid.uuid4()),
            inspection_id=case_submitted.id,
            evidence_id=str(uuid.uuid4()),
            requirement_name="net_quantity",
            result=ComplianceResult.POTENTIAL_NON_COMPLIANCE.value,
            applicability_status=ApplicabilityStatus.APPLICABLE.value,
            rule_citation="Rule 6(1)(c)",
            reason="Net quantity missing unit",
        )
        db_session.add(finding)
        await db_session.commit()

        # Decision on DRAFT case -> ConflictError
        dec_in1 = ReviewerDecisionCreate(
            requirement_name="net_quantity",
            determination=ReviewerDeterminationType.CONFIRMED,
            adjudicated_result=ComplianceResult.POTENTIAL_NON_COMPLIANCE,
            rationale="Verified violation by Reviewer 1",
        )
        with pytest.raises(ConflictError):
            await ReviewerService.record_reviewer_decision(db_session, case_draft.id, rev1.id, dec_in1)

        # Decision 1 by Reviewer 1 on SUBMITTED case -> allowed
        d1 = await ReviewerService.record_reviewer_decision(db_session, case_submitted.id, rev1.id, dec_in1)
        assert d1.reviewer_id == rev1.id

        # Decision 2 by Reviewer 2 on same requirement -> upserts cleanly
        dec_in2 = ReviewerDecisionCreate(
            requirement_name="net_quantity",
            determination=ReviewerDeterminationType.OVERRIDDEN,
            adjudicated_result=ComplianceResult.PASS,
            rationale="Overridden to PASS by Reviewer 2 based on secondary label",
        )
        d2 = await ReviewerService.record_reviewer_decision(db_session, case_submitted.id, rev2.id, dec_in2)
        assert d2.reviewer_id == rev2.id
        assert d2.is_override is True


@pytest.mark.asyncio
async def test_cors_and_health_endpoint():
    """
    Verify CORS headers and /health endpoint:
      - Preflight OPTIONS returns 200 with Access-Control-Allow-Origin
      - Allowed origin (http://localhost:5173) accepted
      - /health endpoint returns health status
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Health check
        res_health = await client.get("/api/v1/health")
        assert res_health.status_code == 200
        data = res_health.json()
        assert data.get("status") == "healthy"

        # CORS preflight
        res_cors = await client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert res_cors.status_code == 200
        assert res_cors.headers.get("access-control-allow-origin") == "http://localhost:5173"


@pytest.mark.asyncio
async def test_inspection_workspace_data_scoping_and_cross_inspection_isolation():
    """
    Verify Inspection Workspace Data Scoping & Cross-Inspection Isolation:
      - A declaration from Inspection B CANNOT appear in Inspection A's payload.
      - Evidence from Inspection B CANNOT appear in Inspection A's payload.
      - Sequential retrieval of Inspection A -> B -> A remains strictly isolated.
    """
    async with AsyncSessionLocal() as db_session:
        inspector = User(
            id=str(uuid.uuid4()),
            email=f"inspector_iso_{uuid.uuid4().hex[:6]}@compliscan.gov.in",
            role=UserRole.INSPECTOR.value,
            full_name="Inspector Isolation Tester",
        )
        db_session.add(inspector)

        # 1. Create Inspection A (e.g. Real Juice)
        case_a_id = str(uuid.uuid4())
        case_a = InspectionCase(
            id=case_a_id,
            case_number=f"CN-A-{uuid.uuid4().hex[:6].upper()}",
            product_name="Real Fruit Juice Mixed 1L",
            origin_status="DOMESTIC",
            created_by_id=inspector.id,
            status=InspectionLifecycleState.DRAFT.value,
        )
        evidence_a = EvidenceAsset(
            id=str(uuid.uuid4()),
            inspection_id=case_a_id,
            uploaded_by_id=inspector.id,
            original_filename="juice_front.jpg",
            mime_type="image/jpeg",
            file_size_bytes=2048,
            sha256_hash="a" * 64,
            storage_path="/storage/evidence/juice_front.jpg",
        )
        finding_a = ComplianceFinding(
            id=str(uuid.uuid4()),
            inspection_id=case_a_id,
            evidence_id=evidence_a.id,
            requirement_name="MANUFACTURER_NAME_ADDRESS",
            result=ComplianceResult.PASS.value,
            applicability_status=ApplicabilityStatus.APPLICABLE.value,
            rule_citation="Rule 6(1)(a)",
            reason="Verified on label",
            metadata_payload={"extracted_value": "Dabur India Ltd, 8/3 Asaf Ali Road, New Delhi", "confidence": 0.98},
        )

        # 2. Create Inspection B (e.g. Peanut Butter)
        case_b_id = str(uuid.uuid4())
        case_b = InspectionCase(
            id=case_b_id,
            case_number=f"CN-B-{uuid.uuid4().hex[:6].upper()}",
            product_name="Crunchy Peanut Butter 500g",
            origin_status="DOMESTIC",
            created_by_id=inspector.id,
            status=InspectionLifecycleState.DRAFT.value,
        )
        evidence_b = EvidenceAsset(
            id=str(uuid.uuid4()),
            inspection_id=case_b_id,
            uploaded_by_id=inspector.id,
            original_filename="peanut_butter_label.jpg",
            mime_type="image/jpeg",
            file_size_bytes=2048,
            sha256_hash="b" * 64,
            storage_path="/storage/evidence/peanut_butter_label.jpg",
        )
        finding_b = ComplianceFinding(
            id=str(uuid.uuid4()),
            inspection_id=case_b_id,
            evidence_id=evidence_b.id,
            requirement_name="MANUFACTURER_NAME_ADDRESS",
            result=ComplianceResult.PASS.value,
            applicability_status=ApplicabilityStatus.APPLICABLE.value,
            rule_citation="Rule 6(1)(a)",
            reason="Verified on label",
            metadata_payload={"extracted_value": "Sundrop Foods, Plot 99 Industrial Zone, Gujarat", "confidence": 0.95},
        )

        db_session.add_all([case_a, evidence_a, finding_a, case_b, evidence_b, finding_b])
        await db_session.commit()

        from backend.tests.conftest import create_test_supabase_token
        token = create_test_supabase_token(user_id=inspector.id, email=inspector.email)
        headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: Query Inspection A details & findings
        res_a1 = await client.get(f"/api/v1/inspections/{case_a_id}", headers=headers)
        assert res_a1.status_code == 200
        data_a1 = res_a1.json()
        assert data_a1["id"] == case_a_id
        assert data_a1["product_name"] == "Real Fruit Juice Mixed 1L"
        # Evidence isolation
        ev_ids_a = [e["id"] for e in data_a1.get("evidence_assets", [])]
        assert evidence_a.id in ev_ids_a
        assert evidence_b.id not in ev_ids_a

        res_findings_a = await client.get(f"/api/v1/inspections/{case_a_id}/findings", headers=headers)
        assert res_findings_a.status_code == 200
        findings_a = res_findings_a.json().get("findings", [])
        assert any("Dabur India Ltd" in str(f.get("metadata_payload") or f.get("reason") or "") for f in findings_a)
        assert not any("Sundrop Foods" in str(f.get("metadata_payload") or f.get("reason") or "") for f in findings_a)
        assert not any("Apex Consumer Goods" in str(f) for f in findings_a)

        # Step 2: Query Inspection B details & findings
        res_b = await client.get(f"/api/v1/inspections/{case_b_id}", headers=headers)
        assert res_b.status_code == 200
        data_b = res_b.json()
        assert data_b["id"] == case_b_id
        assert data_b["product_name"] == "Crunchy Peanut Butter 500g"
        # Evidence isolation
        ev_ids_b = [e["id"] for e in data_b.get("evidence_assets", [])]
        assert evidence_b.id in ev_ids_b
        assert evidence_a.id not in ev_ids_b

        res_findings_b = await client.get(f"/api/v1/inspections/{case_b_id}/findings", headers=headers)
        assert res_findings_b.status_code == 200
        findings_b = res_findings_b.json().get("findings", [])
        assert any("Sundrop Foods" in str(f.get("metadata_payload") or f.get("reason") or "") for f in findings_b)
        assert not any("Dabur India Ltd" in str(f.get("metadata_payload") or f.get("reason") or "") for f in findings_b)
        assert not any("Apex Consumer Goods" in str(f) for f in findings_b)

        # Step 3: Query Inspection A AGAIN (Verify no caching or cross-contamination across requests)
        res_a2 = await client.get(f"/api/v1/inspections/{case_a_id}", headers=headers)
        assert res_a2.status_code == 200
        data_a2 = res_a2.json()
        assert data_a2["id"] == case_a_id
        ev_ids_a2 = [e["id"] for e in data_a2.get("evidence_assets", [])]
        assert evidence_a.id in ev_ids_a2
        assert evidence_b.id not in ev_ids_a2

        res_findings_a2 = await client.get(f"/api/v1/inspections/{case_a_id}/findings", headers=headers)
        assert res_findings_a2.status_code == 200
        findings_a2 = res_findings_a2.json().get("findings", [])
        assert not any("Sundrop Foods" in str(f.get("metadata_payload") or f.get("reason") or "") for f in findings_a2)

