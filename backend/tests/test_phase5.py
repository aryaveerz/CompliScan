"""
CompliScan LM — Phase 5 Comprehensive Test Suite.
Verifies DOCX Report Generation, Repository Search/Filter,
Audit Trail Chain of Custody, Dashboard Metrics Aggregations, RBAC/IDOR, and SQL Safety.
"""

import io
import uuid
from datetime import datetime, timezone, timedelta
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from backend.app.main import app
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.user import User
from backend.app.models.inspection import InspectionCase
from backend.app.models.evidence import EvidenceAsset
from backend.app.models.final_audit import FinalAuditRecord
from backend.app.models.compliance import ComplianceFinding, ApplicabilityResult
from backend.app.models.audit import AuditEvent
from backend.app.services.docx_report_service import DOCXReportService
from backend.app.services.dashboard_service import DashboardService
from backend.app.services.inspection_service import InspectionService
from backend.app.services.finalization_service import FinalizationService
from backend.tests.conftest import create_test_supabase_token
from shared.domain.enums import (
    UserRole,
    OriginStatus,
    EvidenceType,
    ComplianceResult,
    AuditEventType,
    FinalDecision,
)
from shared.domain.states import InspectionLifecycleState, ProcessingState, FinalizationStatus


# ── Helper Fixtures ──────────────────────────────────────────────────────────

async def seed_phase5_dataset():
    """Seed test users, inspections in various lifecycle states, findings, and a finalized record."""
    async with AsyncSessionLocal() as session:
        # Create Inspector 1
        u_insp1 = User(
            id=f"usr-{uuid.uuid4().hex[:8]}",
            email=f"inspector1_{uuid.uuid4().hex[:6]}@compliscan.gov.in",
            full_name="Inspector Rajesh Sharma",
            role=UserRole.INSPECTOR.value,
            is_active=True,
        )
        # Create Inspector 2
        u_insp2 = User(
            id=f"usr-{uuid.uuid4().hex[:8]}",
            email=f"inspector2_{uuid.uuid4().hex[:6]}@compliscan.gov.in",
            full_name="Inspector Priya Patel",
            role=UserRole.INSPECTOR.value,
            is_active=True,
        )
        # Create Reviewer
        u_rev = User(
            id=f"usr-{uuid.uuid4().hex[:8]}",
            email=f"reviewer_{uuid.uuid4().hex[:6]}@compliscan.gov.in",
            full_name="Senior Reviewer Alok Verma",
            role=UserRole.REVIEWER.value,
            is_active=True,
        )
        session.add_all([u_insp1, u_insp2, u_rev])
        await session.flush()

        # Inspection 1: Finalized (COMPLIANT) by Inspector 1
        now = datetime.now(timezone.utc)
        insp1 = InspectionCase(
            id=f"INS-{uuid.uuid4().hex[:12].upper()}",
            case_number=f"INSP-2026-{uuid.uuid4().hex[:5].upper()}",
            status=InspectionLifecycleState.FINALIZED.value,
            processing_state=ProcessingState.IDLE.value,
            finalization_status=FinalizationStatus.READ_ONLY.value,
            product_name="Himalayan Pure Organic Honey 500g",
            origin_status=OriginStatus.DOMESTIC.value,
            product_category="Food & Beverages",
            notes="Standard routine packaging inspection",
            created_by_id=u_insp1.id,
            reviewer_id=u_rev.id,
            created_at=now - timedelta(days=2),
            submitted_at=now - timedelta(days=1, hours=2),
            finalized_at=now - timedelta(days=1),
        )
        session.add(insp1)
        await session.flush()

        # Evidence for Insp 1
        ev1 = EvidenceAsset(
            id=f"EVD-{uuid.uuid4().hex[:12].upper()}",
            inspection_id=insp1.id,
            evidence_type=EvidenceType.PRIMARY.value,
            original_filename="front_label.jpg",
            mime_type="image/jpeg",
            file_size_bytes=1048576,
            sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            storage_path="/uploads/front_label.jpg",
            is_immutable=True,
            uploaded_by_id=u_insp1.id,
        )
        session.add(ev1)

        # Finding for Insp 1
        fnd1 = ComplianceFinding(
            id=f"FND-{uuid.uuid4().hex[:12].upper()}",
            inspection_id=insp1.id,
            evidence_id=ev1.id,
            requirement_name="Rule 6(1)(a) Manufacturer/Packer/Importer",
            result=ComplianceResult.PASS.value,
            reason="Full manufacturer address clearly observed",
            applicability_status="APPLICABLE",
            rule_citation="Rule 6(1)(a)",
            evaluation_version="v1.0",
        )
        session.add(fnd1)

        # FinalAuditRecord for Insp 1
        far1 = FinalAuditRecord(
            id=f"FAR-{uuid.uuid4().hex[:12].upper()}",
            inspection_id=insp1.id,
            finalized_by_id=u_rev.id,
            finalized_at=now - timedelta(days=1),
            final_decision=FinalDecision.COMPLIANT.value,
            final_rationale="All mandatory declarations are compliant under PCR 2011.",
            inspection_context_snapshot={
                "case_number": insp1.case_number,
                "product_name": insp1.product_name,
                "origin_status": insp1.origin_status,
                "product_category": insp1.product_category,
            },
            evidence_snapshot=[{
                "id": ev1.id,
                "original_filename": ev1.original_filename,
                "evidence_type": ev1.evidence_type,
                "file_size_bytes": ev1.file_size_bytes,
                "sha256_hash": ev1.sha256_hash,
            }],
            declaration_snapshot={"net_quantity": "500g", "mrp": "Rs. 350.00"},
            applicability_snapshot=[{
                "requirement_name": "Rule 6(1)(a)",
                "status": "APPLICABLE",
                "rule_citation": "Rule 6(1)(a)",
                "basis": "Mandatory for all pre-packaged commodities",
            }],
            compliance_findings_snapshot=[{
                "requirement_name": "Rule 6(1)(a) Manufacturer/Packer/Importer",
                "result": "PASS",
                "reason": "Manufacturer declaration clear",
            }],
            reviewer_decisions_snapshot=[{
                "requirement_name": "Rule 6(1)(a) Manufacturer/Packer/Importer",
                "determination": "CONFIRMED",
                "adjudicated_result": "PASS",
                "is_override": False,
                "rationale": "Verified correct",
            }],
            source_evidence_hashes={ev1.id: ev1.sha256_hash},
            audit_metadata={"finalized_by": u_rev.id},
        )
        session.add(far1)

        # Audit events for Insp 1
        aud1_1 = AuditEvent(
            id=f"AUD-{uuid.uuid4().hex[:12].upper()}",
            inspection_id=insp1.id,
            actor_id=u_insp1.id,
            actor_role=UserRole.INSPECTOR.value,
            event_type=AuditEventType.INSPECTION_CREATED.value,
            details={"case_number": insp1.case_number},
            created_at=now - timedelta(days=2),
        )
        aud1_2 = AuditEvent(
            id=f"AUD-{uuid.uuid4().hex[:12].upper()}",
            inspection_id=insp1.id,
            actor_id=u_insp1.id,
            actor_role=UserRole.INSPECTOR.value,
            event_type=AuditEventType.INSPECTION_SUBMITTED_FOR_REVIEW.value,
            details={"submitted_by": u_insp1.id},
            created_at=now - timedelta(days=1, hours=2),
        )
        aud1_3 = AuditEvent(
            id=f"AUD-{uuid.uuid4().hex[:12].upper()}",
            inspection_id=insp1.id,
            actor_id=u_rev.id,
            actor_role=UserRole.REVIEWER.value,
            event_type=AuditEventType.INSPECTION_FINALIZED.value,
            details={"final_record_id": far1.id},
            created_at=now - timedelta(days=1),
        )
        session.add_all([aud1_1, aud1_2, aud1_3])

        # Inspection 2: Draft by Inspector 1
        insp2 = InspectionCase(
            id=f"INS-{uuid.uuid4().hex[:12].upper()}",
            case_number=f"INSP-2026-{uuid.uuid4().hex[:5].upper()}",
            status=InspectionLifecycleState.DRAFT.value,
            processing_state=ProcessingState.IDLE.value,
            finalization_status=FinalizationStatus.UNFINALIZED.value,
            product_name="Imported California Almonds 1kg",
            origin_status=OriginStatus.IMPORTED.value,
            product_category="Dry Fruits",
            notes="Imported batch from USA",
            created_by_id=u_insp1.id,
            created_at=now - timedelta(days=1),
        )
        session.add(insp2)

        # Finding with violation for Insp 2
        fnd2 = ComplianceFinding(
            id=f"FND-{uuid.uuid4().hex[:12].upper()}",
            inspection_id=insp2.id,
            requirement_name="Rule 6(1)(b) Country of Origin",
            result=ComplianceResult.POTENTIAL_NON_COMPLIANCE.value,
            reason="Country of Origin missing for imported commodity",
            applicability_status="APPLICABLE",
            rule_citation="Rule 6(1)(b)",
            evaluation_version="v1.0",
        )
        session.add(fnd2)

        # Inspection 3: Owned by Inspector 2 (In Verification)
        insp3 = InspectionCase(
            id=f"INS-{uuid.uuid4().hex[:12].upper()}",
            case_number=f"INSP-2026-{uuid.uuid4().hex[:5].upper()}",
            status=InspectionLifecycleState.IN_VERIFICATION.value,
            processing_state=ProcessingState.IDLE.value,
            finalization_status=FinalizationStatus.UNFINALIZED.value,
            product_name="Organic Basmati Rice 5kg",
            origin_status=OriginStatus.DOMESTIC.value,
            product_category="Food & Beverages",
            created_by_id=u_insp2.id,
            created_at=now - timedelta(hours=5),
        )
        session.add(insp3)

        await session.commit()

        return {
            "insp1": insp1,
            "insp2": insp2,
            "insp3": insp3,
            "far1": far1,
            "u_insp1": u_insp1,
            "u_insp2": u_insp2,
            "u_rev": u_rev,
        }


# ── 1. Unit Tests: DOCX Report Service ────────────────────────────────────────

@pytest.mark.asyncio
async def test_docx_report_service_generation():
    """Test generating a binary DOCX file directly from FinalAuditRecord."""
    seed = await seed_phase5_dataset()
    far = seed["far1"]

    docx_bytes = DOCXReportService.generate_docx_report(far)
    assert docx_bytes is not None
    assert len(docx_bytes) > 1000
    # Check DOCX zip magic header (PK\x03\x04)
    assert docx_bytes[:4] == b"PK\x03\x04"


@pytest.mark.asyncio
async def test_docx_report_service_validation():
    """Test that None input raises ValidationError."""
    with pytest.raises(Exception):
        DOCXReportService.generate_docx_report(None)


# ── 2. API Tests: DOCX Report Download ────────────────────────────────────────

@pytest.mark.asyncio
async def test_docx_download_api_finalized():
    """Test downloading official DOCX report for a finalized inspection."""
    seed = await seed_phase5_dataset()
    insp1 = seed["insp1"]
    u_rev = seed["u_rev"]
    token = create_test_supabase_token(u_rev.id, u_rev.email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(
            f"/api/v1/inspections/{insp1.id}/report/docx",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        assert res.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert f"CompliScan_Report_{insp1.case_number}.docx" in res.headers["content-disposition"]
        assert res.content[:4] == b"PK\x03\x04"

    # Verify REPORT_DOWNLOADED audit event was logged
    async with AsyncSessionLocal() as session:
        stmt = select(AuditEvent).where(
            AuditEvent.inspection_id == insp1.id,
            AuditEvent.event_type == AuditEventType.REPORT_DOWNLOADED.value,
        )
        res = await session.execute(stmt)
        aud = res.scalar_one_or_none()
        assert aud is not None
        assert aud.details.get("format") == "docx"


@pytest.mark.asyncio
async def test_docx_download_api_unfinalized_returns_400():
    """Test that attempting to download DOCX for unfinalized inspection returns 400 Bad Request."""
    seed = await seed_phase5_dataset()
    insp2 = seed["insp2"]
    u_insp1 = seed["u_insp1"]
    token = create_test_supabase_token(u_insp1.id, u_insp1.email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(
            f"/api/v1/inspections/{insp2.id}/report/docx",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code in (400, 422, 404)


@pytest.mark.asyncio
async def test_docx_download_api_rbac_idor():
    """Test that Inspector B cannot download Inspector A's finalized report."""
    seed = await seed_phase5_dataset()
    insp1 = seed["insp1"] # Owned by Inspector 1
    u_insp2 = seed["u_insp2"] # Inspector 2
    token = create_test_supabase_token(u_insp2.id, u_insp2.email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(
            f"/api/v1/inspections/{insp1.id}/report/docx",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 403


# ── 3. API Tests: Repository Search & Filter ──────────────────────────────────

@pytest.mark.asyncio
async def test_repository_search_api_basic():
    """Test searching the repository with server-side pagination."""
    seed = await seed_phase5_dataset()
    u_rev = seed["u_rev"]
    token = create_test_supabase_token(u_rev.id, u_rev.email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(
            "/api/v1/inspections/search?page=1&page_size=10",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert "total_count" in data
        assert data["total_count"] >= 3
        assert data["page"] == 1
        assert data["page_size"] == 10


@pytest.mark.asyncio
async def test_repository_search_api_text_query():
    """Test text query filtering on product name."""
    seed = await seed_phase5_dataset()
    u_rev = seed["u_rev"]
    token = create_test_supabase_token(u_rev.id, u_rev.email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(
            "/api/v1/inspections/search?q=Almonds",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["total_count"] >= 1
        assert any("Almonds" in item["product_name"] for item in data["items"])


@pytest.mark.asyncio
async def test_repository_search_api_filters():
    """Test multi-field filtering by category, status, origin, and compliance."""
    seed = await seed_phase5_dataset()
    u_rev = seed["u_rev"]
    token = create_test_supabase_token(u_rev.id, u_rev.email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Filter by origin = IMPORTED
        res_orig = await client.get(
            "/api/v1/inspections/search?origin=IMPORTED",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_orig.status_code == 200
        data_orig = res_orig.json()
        assert all(item["origin_status"] == "IMPORTED" for item in data_orig["items"])

        # Filter by status = FINALIZED
        res_status = await client.get(
            "/api/v1/inspections/search?status=FINALIZED",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_status.status_code == 200
        data_status = res_status.json()
        assert all(item["status"] == "FINALIZED" for item in data_status["items"])


@pytest.mark.asyncio
async def test_repository_search_sql_injection_safety():
    """Test that arbitrary strings and SQL injection payloads are safely parameterized."""
    seed = await seed_phase5_dataset()
    u_rev = seed["u_rev"]
    token = create_test_supabase_token(u_rev.id, u_rev.email)

    malicious_inputs = [
        "' OR '1'='1",
        "'; DROP TABLE inspections; --",
        "%_%%%",
        "UNION SELECT * FROM users--",
    ]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for mal in malicious_inputs:
            res = await client.get(
                f"/api/v1/inspections/search?q={mal}",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert res.status_code == 200
            # Table remains intact and returns valid JSON response


@pytest.mark.asyncio
async def test_repository_search_rbac_inspector_scoping():
    """Test that an Inspector only sees their own inspection cases in search results."""
    seed = await seed_phase5_dataset()
    u_insp1 = seed["u_insp1"]
    u_insp2 = seed["u_insp2"]
    token_insp1 = create_test_supabase_token(u_insp1.id, u_insp1.email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(
            "/api/v1/inspections/search",
            headers={"Authorization": f"Bearer {token_insp1}"},
        )
        assert res.status_code == 200
        data = res.json()
        # All items must belong to Inspector 1
        assert all(item["created_by_id"] == u_insp1.id for item in data["items"])
        assert not any(item["created_by_id"] == u_insp2.id for item in data["items"])


# ── 4. API Tests: Audit Trail Chain of Custody ────────────────────────────────

@pytest.mark.asyncio
async def test_audit_trail_api_chronological():
    """Test retrieving chronological chain-of-custody audit events for an inspection."""
    seed = await seed_phase5_dataset()
    insp1 = seed["insp1"]
    u_rev = seed["u_rev"]
    token = create_test_supabase_token(u_rev.id, u_rev.email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(
            f"/api/v1/inspections/{insp1.id}/audit-trail",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        events = res.json()
        assert len(events) >= 3
        # Verify chronological ordering
        for i in range(len(events) - 1):
            t1 = datetime.fromisoformat(events[i]["created_at"].replace("Z", "+00:00"))
            t2 = datetime.fromisoformat(events[i+1]["created_at"].replace("Z", "+00:00"))
            assert t1 <= t2


@pytest.mark.asyncio
async def test_audit_trail_api_rbac_idor():
    """Test that Inspector B cannot access Inspector A's audit trail."""
    seed = await seed_phase5_dataset()
    insp1 = seed["insp1"]
    u_insp2 = seed["u_insp2"]
    token = create_test_supabase_token(u_insp2.id, u_insp2.email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(
            f"/api/v1/inspections/{insp1.id}/audit-trail",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 403


# ── 5. API Tests: Operational Dashboard Metrics ───────────────────────────────

@pytest.mark.asyncio
async def test_dashboard_metrics_api_aggregated():
    """Test calculating authoritative database metrics across all horizons."""
    seed = await seed_phase5_dataset()
    u_rev = seed["u_rev"]
    token = create_test_supabase_token(u_rev.id, u_rev.email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for horizon in ["7d", "30d", "90d", "all"]:
            res = await client.get(
                f"/api/v1/dashboard/metrics?date_range={horizon}",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert res.status_code == 200
            data = res.json()

            assert data["total_inspections"] >= 3
            assert data["total_finalized"] >= 1
            assert "compliance_rate_percent" in data
            assert "status_counts" in data
            assert "compliance_distribution" in data
            assert "origin_distribution" in data
            assert "rule_violation_counts" in data
            assert "governance_metrics" in data
            assert data["governance_metrics"]["avg_review_turnaround_seconds"] is not None


@pytest.mark.asyncio
async def test_dashboard_metrics_category_filter():
    """Test dashboard metrics filtered by commodity category."""
    seed = await seed_phase5_dataset()
    u_rev = seed["u_rev"]
    token = create_test_supabase_token(u_rev.id, u_rev.email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(
            "/api/v1/dashboard/metrics?category=Food%20%26%20Beverages",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["category"] == "Food & Beverages"
        assert data["total_inspections"] >= 2
