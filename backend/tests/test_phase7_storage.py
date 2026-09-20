"""
CompliScan LM - Phase 7.3 Production Storage & Evidence Integrity Test Suite.
"""
import io, os, uuid, pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from PIL import Image, ImageDraw
from sqlalchemy import select
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.user import User
from backend.app.models.inspection import InspectionCase
from backend.app.models.evidence import EvidenceAsset
from backend.app.core.security import compute_sha256
from backend.app.core.errors import NotFoundError, AnalysisError, EvidenceError
from backend.app.services.storage_service import LocalStorageService, SupabaseStorageService, get_storage_service
from backend.app.services.evidence_service import EvidenceService
from backend.app.services.analysis_job_service import AnalysisJobService
from backend.app.core.config import settings
from shared.domain.enums import UserRole, EvidenceType
from shared.domain.constants import ErrorCode


def generate_test_jpeg(width=800, height=600):
    img = Image.new("RGB", (width, height), color=(120, 80, 40))
    d = ImageDraw.Draw(img)
    for x in range(0, width, 30):
        d.line([(x, 0), (x, height)], fill=(0, 0, 0), width=2)
    for y in range(0, height, 30):
        d.line([(0, y), (width, y)], fill=(0, 0, 0), width=2)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


class TestLocalStorageService:

    @pytest.mark.asyncio
    async def test_upload_and_download_roundtrip(self, tmp_path):
        svc = LocalStorageService(base_dir=str(tmp_path))
        content = b"test_evidence_binary_payload"
        bucket = "compliscan-evidence"
        path = "inspections/INS-001/EV-001/original/photo.jpg"
        canonical = await svc.upload_file(bucket, path, content, content_type="image/jpeg")
        assert canonical == f"{bucket}/{path}"
        retrieved = await svc.download_file(bucket, path)
        assert retrieved == content

    @pytest.mark.asyncio
    async def test_file_exists_and_delete(self, tmp_path):
        svc = LocalStorageService(base_dir=str(tmp_path))
        content = b"existence_test"
        bucket = "compliscan-evidence"
        path = "inspections/INS-002/EV-002/original/a.jpg"
        assert not await svc.file_exists(bucket, path)
        await svc.upload_file(bucket, path, content)
        assert await svc.file_exists(bucket, path)
        deleted = await svc.delete_file(bucket, path)
        assert deleted is True
        assert not await svc.file_exists(bucket, path)

    @pytest.mark.asyncio
    async def test_download_missing_raises_not_found(self, tmp_path):
        svc = LocalStorageService(base_dir=str(tmp_path))
        with pytest.raises(NotFoundError):
            await svc.download_file("compliscan-evidence", "missing/path/file.jpg")

    @pytest.mark.asyncio
    async def test_signed_url_local_returns_api_path(self, tmp_path):
        svc = LocalStorageService(base_dir=str(tmp_path))
        url = await svc.generate_signed_url("compliscan-evidence", "inspections/X/EV-X/a.jpg")
        assert "/api/v1/evidence/download" in url
        assert "path=" in url

    @pytest.mark.asyncio
    async def test_download_with_bucket_prefix_stripped(self, tmp_path):
        svc = LocalStorageService(base_dir=str(tmp_path))
        content = b"prefix_test_bytes"
        bucket = "compliscan-evidence"
        path = "inspections/INS-003/EV-003/original/x.jpg"
        await svc.upload_file(bucket, path, content)
        retrieved = await svc.download_file(bucket, f"{bucket}/{path}")
        assert retrieved == content


class TestGetStorageServiceFactory:

    def test_returns_local_by_default(self, monkeypatch):
        monkeypatch.setattr(settings, "STORAGE_BACKEND", "local")
        monkeypatch.setattr(settings, "ENVIRONMENT", "test")
        import backend.app.services.storage_service as ss
        ss._local_storage_instance = None
        ss._supabase_storage_instance = None
        svc = get_storage_service()
        assert isinstance(svc, LocalStorageService)
        ss._local_storage_instance = None

    def test_explicit_supabase_backend(self, monkeypatch):
        monkeypatch.setattr(settings, "SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "test_key")
        import backend.app.services.storage_service as ss
        ss._supabase_storage_instance = None
        svc = get_storage_service(backend_type="supabase")
        assert isinstance(svc, SupabaseStorageService)
        ss._supabase_storage_instance = None

    def test_production_env_forces_supabase(self, monkeypatch):
        monkeypatch.setattr(settings, "ENVIRONMENT", "production")
        monkeypatch.setattr(settings, "SUPABASE_URL", "https://prod.supabase.co")
        monkeypatch.setattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "prod_key")
        import backend.app.services.storage_service as ss
        ss._supabase_storage_instance = None
        svc = get_storage_service()
        assert isinstance(svc, SupabaseStorageService)
        ss._supabase_storage_instance = None
        monkeypatch.setattr(settings, "ENVIRONMENT", "test")


class TestEvidenceServiceStorageIntegration:

    @pytest.mark.asyncio
    async def test_upload_evidence_canonical_path_stored(self, tmp_path, monkeypatch):
        monkeypatch.setattr(settings, "LOCAL_STORAGE_DIR", str(tmp_path / "storage"))
        monkeypatch.setattr(settings, "STORAGE_BACKEND", "local")
        import backend.app.services.storage_service as ss
        ss._local_storage_instance = None
        image_bytes = generate_test_jpeg()
        sha256 = compute_sha256(image_bytes)
        async with AsyncSessionLocal() as db:
            inspector = User(email=f"insp.s3a.{uuid.uuid4().hex[:6]}@test.com", full_name="Insp S3A", role=UserRole.INSPECTOR.value, is_active=True)
            db.add(inspector); await db.flush()
            inspection = InspectionCase(case_number=f"INS-S3A-{uuid.uuid4().hex[:6].upper()}", product_name="Test", created_by_id=inspector.id)
            db.add(inspection); await db.flush()
            from fastapi import UploadFile
            from starlette.datastructures import Headers
            file = UploadFile(filename="test.jpg", file=io.BytesIO(image_bytes), headers=Headers({"content-type": "image/jpeg"}))
            asset = await EvidenceService.upload_evidence(db=db, inspection_id=inspection.id, file=file, evidence_type=EvidenceType.PRIMARY, current_user=inspector)
            assert asset.storage_path.startswith("compliscan-evidence/")
            assert inspection.id in asset.storage_path
            assert asset.sha256_hash == sha256
            svc = get_storage_service()
            path = asset.storage_path[len("compliscan-evidence/"):]
            assert await svc.file_exists("compliscan-evidence", path)
        ss._local_storage_instance = None

    @pytest.mark.asyncio
    async def test_get_evidence_binary_returns_correct_bytes(self, tmp_path, monkeypatch):
        monkeypatch.setattr(settings, "LOCAL_STORAGE_DIR", str(tmp_path / "storage"))
        monkeypatch.setattr(settings, "STORAGE_BACKEND", "local")
        import backend.app.services.storage_service as ss
        ss._local_storage_instance = None
        image_bytes = generate_test_jpeg()
        async with AsyncSessionLocal() as db:
            inspector = User(email=f"insp.s3b.{uuid.uuid4().hex[:6]}@test.com", full_name="Insp S3B", role=UserRole.INSPECTOR.value, is_active=True)
            db.add(inspector); await db.flush()
            inspection = InspectionCase(case_number=f"INS-S3B-{uuid.uuid4().hex[:6].upper()}", product_name="Test", created_by_id=inspector.id)
            db.add(inspection); await db.flush()
            from fastapi import UploadFile
            from starlette.datastructures import Headers
            file = UploadFile(filename="test.jpg", file=io.BytesIO(image_bytes), headers=Headers({"content-type": "image/jpeg"}))
            asset = await EvidenceService.upload_evidence(db=db, inspection_id=inspection.id, file=file, evidence_type=EvidenceType.PRIMARY, current_user=inspector)
            content, ret = await EvidenceService.get_evidence_binary(db=db, evidence_id=asset.id, current_user=inspector)
            assert content == image_bytes
            assert compute_sha256(content) == asset.sha256_hash
        ss._local_storage_instance = None

    @pytest.mark.asyncio
    async def test_delete_draft_evidence_removes_from_storage(self, tmp_path, monkeypatch):
        monkeypatch.setattr(settings, "LOCAL_STORAGE_DIR", str(tmp_path / "storage"))
        monkeypatch.setattr(settings, "STORAGE_BACKEND", "local")
        import backend.app.services.storage_service as ss
        ss._local_storage_instance = None
        image_bytes = generate_test_jpeg()
        async with AsyncSessionLocal() as db:
            inspector = User(email=f"insp.s3c.{uuid.uuid4().hex[:6]}@test.com", full_name="Insp S3C", role=UserRole.INSPECTOR.value, is_active=True)
            db.add(inspector); await db.flush()
            inspection = InspectionCase(case_number=f"INS-S3C-{uuid.uuid4().hex[:6].upper()}", product_name="Test", created_by_id=inspector.id)
            db.add(inspection); await db.flush()
            from fastapi import UploadFile
            from starlette.datastructures import Headers
            file = UploadFile(filename="test.jpg", file=io.BytesIO(image_bytes), headers=Headers({"content-type": "image/jpeg"}))
            asset = await EvidenceService.upload_evidence(db=db, inspection_id=inspection.id, file=file, evidence_type=EvidenceType.PRIMARY, current_user=inspector)
            svc = get_storage_service()
            path = asset.storage_path[len("compliscan-evidence/"):]
            assert await svc.file_exists("compliscan-evidence", path)
            await EvidenceService.delete_draft_evidence(db=db, inspection_id=inspection.id, evidence_id=asset.id, current_user=inspector)
            assert not await svc.file_exists("compliscan-evidence", path)
        ss._local_storage_instance = None

    @pytest.mark.asyncio
    async def test_upload_storage_failure_no_orphan_db_record(self, tmp_path, monkeypatch):
        monkeypatch.setattr(settings, "LOCAL_STORAGE_DIR", str(tmp_path / "storage"))
        monkeypatch.setattr(settings, "STORAGE_BACKEND", "local")
        import backend.app.services.storage_service as ss
        ss._local_storage_instance = None
        failing_svc = MagicMock()
        failing_svc.upload_file = AsyncMock(side_effect=RuntimeError("Simulated storage failure"))
        image_bytes = generate_test_jpeg()
        async with AsyncSessionLocal() as db:
            inspector = User(email=f"insp.s3d.{uuid.uuid4().hex[:6]}@test.com", full_name="Insp S3D", role=UserRole.INSPECTOR.value, is_active=True)
            db.add(inspector); await db.flush()
            inspection = InspectionCase(case_number=f"INS-S3D-{uuid.uuid4().hex[:6].upper()}", product_name="Test", created_by_id=inspector.id)
            db.add(inspection); await db.flush()
            inspection_id = inspection.id
            from fastapi import UploadFile
            from starlette.datastructures import Headers
            file = UploadFile(filename="fail.jpg", file=io.BytesIO(image_bytes), headers=Headers({"content-type": "image/jpeg"}))
            with patch("backend.app.services.evidence_service.get_storage_service", return_value=failing_svc):
                with pytest.raises(EvidenceError) as exc_info:
                    await EvidenceService.upload_evidence(db=db, inspection_id=inspection_id, file=file, evidence_type=EvidenceType.PRIMARY, current_user=inspector)
            assert exc_info.value.code == ErrorCode.INTERNAL_SERVER_ERROR
            stmt = select(EvidenceAsset).where(EvidenceAsset.inspection_id == inspection_id)
            assets = (await db.execute(stmt)).scalars().all()
            assert len(assets) == 0
        ss._local_storage_instance = None


class TestWorkerSHA256IntegrityVerification:

    @pytest.mark.asyncio
    async def test_correct_sha256_passes(self, tmp_path, monkeypatch):
        monkeypatch.setattr(settings, "LOCAL_STORAGE_DIR", str(tmp_path / "storage"))
        monkeypatch.setattr(settings, "STORAGE_BACKEND", "local")
        import backend.app.services.storage_service as ss
        ss._local_storage_instance = None
        image_bytes = generate_test_jpeg()
        sha256 = compute_sha256(image_bytes)
        svc = get_storage_service()
        await svc.upload_file("compliscan-evidence", "inspections/INS-WPASS/EV-V/original/img.jpg", image_bytes, "image/jpeg")
        async with AsyncSessionLocal() as db:
            inspector = User(email=f"worker.pass.{uuid.uuid4().hex[:6]}@test.com", full_name="Worker Pass", role=UserRole.INSPECTOR.value, is_active=True)
            db.add(inspector); await db.flush()
            inspection = InspectionCase(case_number=f"INS-WPASS-{uuid.uuid4().hex[:6].upper()}", product_name="Pass Test", created_by_id=inspector.id)
            db.add(inspection); await db.flush()
            asset = EvidenceAsset(id=f"EV-{uuid.uuid4().hex[:12].upper()}", inspection_id=inspection.id, evidence_type=EvidenceType.PRIMARY.value, original_filename="img.jpg", mime_type="image/jpeg", file_size_bytes=len(image_bytes), sha256_hash=sha256, storage_path="compliscan-evidence/inspections/INS-WPASS/EV-V/original/img.jpg", is_immutable=True, uploaded_by_id=inspector.id)
            db.add(asset); await db.commit()
            content = await AnalysisJobService._get_and_verify_evidence_binary(db=db, evidence=asset, job_id="JOB-PASS")
            assert content == image_bytes
        ss._local_storage_instance = None

    @pytest.mark.asyncio
    async def test_tampered_sha256_raises_analysis_error(self, tmp_path, monkeypatch):
        monkeypatch.setattr(settings, "LOCAL_STORAGE_DIR", str(tmp_path / "storage"))
        monkeypatch.setattr(settings, "STORAGE_BACKEND", "local")
        import backend.app.services.storage_service as ss
        ss._local_storage_instance = None
        original_bytes = generate_test_jpeg()
        tampered_bytes = original_bytes[:100] + b"TAMPERED!" + original_bytes[109:]
        correct_sha256 = compute_sha256(original_bytes)
        svc = get_storage_service()
        await svc.upload_file("compliscan-evidence", "inspections/INS-TAMPER/EV-T/original/img.jpg", tampered_bytes, "image/jpeg")
        async with AsyncSessionLocal() as db:
            inspector = User(email=f"worker.tamper.{uuid.uuid4().hex[:6]}@test.com", full_name="Worker Tamper", role=UserRole.INSPECTOR.value, is_active=True)
            db.add(inspector); await db.flush()
            inspection = InspectionCase(case_number=f"INS-WTAMP-{uuid.uuid4().hex[:6].upper()}", product_name="Tamper Test", created_by_id=inspector.id)
            db.add(inspection); await db.flush()
            asset = EvidenceAsset(id=f"EV-{uuid.uuid4().hex[:12].upper()}", inspection_id=inspection.id, evidence_type=EvidenceType.PRIMARY.value, original_filename="img.jpg", mime_type="image/jpeg", file_size_bytes=len(original_bytes), sha256_hash=correct_sha256, storage_path="compliscan-evidence/inspections/INS-TAMPER/EV-T/original/img.jpg", is_immutable=True, uploaded_by_id=inspector.id)
            db.add(asset); await db.flush()
            with pytest.raises(AnalysisError) as exc_info:
                await AnalysisJobService._get_and_verify_evidence_binary(db=db, evidence=asset, job_id="JOB-TAMPER")
            assert exc_info.value.code == ErrorCode.INTEGRITY_MISMATCH_ERROR
            assert "INTEGRITY_MISMATCH_ERROR" in str(exc_info.value.message)
        ss._local_storage_instance = None

    @pytest.mark.asyncio
    async def test_legacy_local_fallback_when_storage_not_found(self, tmp_path, monkeypatch):
        monkeypatch.setattr(settings, "LOCAL_STORAGE_DIR", str(tmp_path / "storage"))
        monkeypatch.setattr(settings, "STORAGE_BACKEND", "local")
        import backend.app.services.storage_service as ss
        ss._local_storage_instance = None
        image_bytes = generate_test_jpeg()
        sha256 = compute_sha256(image_bytes)
        legacy_dir = tmp_path / "legacy"
        legacy_dir.mkdir(parents=True)
        legacy_path = str(legacy_dir / "EV-LEGACY_photo.jpg")
        with open(legacy_path, "wb") as f: f.write(image_bytes)
        failing_svc = MagicMock()
        failing_svc.download_file = AsyncMock(side_effect=NotFoundError("Not found"))
        async with AsyncSessionLocal() as db:
            inspector = User(email=f"worker.legacy.{uuid.uuid4().hex[:6]}@test.com", full_name="Worker Legacy", role=UserRole.INSPECTOR.value, is_active=True)
            db.add(inspector); await db.flush()
            inspection = InspectionCase(case_number=f"INS-LEG-{uuid.uuid4().hex[:6].upper()}", product_name="Legacy Test", created_by_id=inspector.id)
            db.add(inspection); await db.flush()
            asset = EvidenceAsset(id=f"EV-{uuid.uuid4().hex[:12].upper()}", inspection_id=inspection.id, evidence_type=EvidenceType.PRIMARY.value, original_filename="photo.jpg", mime_type="image/jpeg", file_size_bytes=len(image_bytes), sha256_hash=sha256, storage_path=legacy_path, is_immutable=True, uploaded_by_id=inspector.id)
            db.add(asset); await db.flush()
            with patch("backend.app.services.analysis_job_service.get_storage_service", return_value=failing_svc):
                content = await AnalysisJobService._get_and_verify_evidence_binary(db=db, evidence=asset, job_id="JOB-LEGACY")
            assert content == image_bytes
        ss._local_storage_instance = None


class TestNoTestImagesFallbackInReportServices:

    def test_pdf_report_service_has_no_fixture_fallback(self):
        service_path = os.path.join(os.path.dirname(__file__), "..", "app", "services", "pdf_report_service.py")
        with open(service_path, "r", encoding="utf-8") as f:
            source = f.read()
        assert "tests/fixtures" not in source, "VIOLATION: pdf_report_service.py references tests/fixtures"
        assert "packaged_products" not in source, "VIOLATION: pdf_report_service.py references packaged_products"
        assert "Peanut_Butter" not in source, "VIOLATION: pdf_report_service.py references Peanut_Butter"

    def test_docx_report_service_has_no_fixture_fallback(self):
        service_path = os.path.join(os.path.dirname(__file__), "..", "app", "services", "docx_report_service.py")
        with open(service_path, "r", encoding="utf-8") as f:
            source = f.read()
        assert "tests/fixtures" not in source, "VIOLATION: docx_report_service.py references tests/fixtures"
        assert "packaged_products" not in source, "VIOLATION: docx_report_service.py references packaged_products"
        assert "Peanut_Butter" not in source, "VIOLATION: docx_report_service.py references Peanut_Butter"

    def test_evidence_service_has_no_save_evidence_file_method(self):
        assert not hasattr(EvidenceService, "save_evidence_file"), "VIOLATION: save_evidence_file() method still present"


class TestSupabaseStoragePathNormalization:

    @pytest.mark.asyncio
    async def test_upload_strips_leading_slash(self):
        svc = SupabaseStorageService(supabase_url="https://test.supabase.co", service_role_key="test_key")
        captured = []
        async def mock_post(url, content, headers):
            captured.append(url)
            r = MagicMock(); r.status_code = 200; return r
        import httpx
        with patch.object(httpx.AsyncClient, "post", new_callable=AsyncMock, side_effect=mock_post):
            canonical = await svc.upload_file("compliscan-evidence", "/inspections/X/file.jpg", b"data")
        assert canonical == "compliscan-evidence/inspections/X/file.jpg"
        assert "//inspections" not in captured[0]

    @pytest.mark.asyncio
    async def test_download_strips_bucket_prefix_from_path(self):
        svc = SupabaseStorageService(supabase_url="https://test.supabase.co", service_role_key="test_key")
        captured = []
        async def mock_get(url, headers):
            captured.append(url)
            r = MagicMock(); r.status_code = 200; r.content = b"evidence_data"; return r
        import httpx
        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock, side_effect=mock_get):
            content = await svc.download_file("compliscan-evidence", "compliscan-evidence/inspections/X/file.jpg")
        assert content == b"evidence_data"
        assert "compliscan-evidence/compliscan-evidence" not in captured[0]