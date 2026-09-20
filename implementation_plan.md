# Phase 7.1 Implementation Plan — Cloud Deployment Foundation (Vercel + Render + Supabase)

Prepare CompliScan LM for cloud deployment across **Vercel** (Frontend SPA), **Render** (FastAPI Web Service & Background Worker), and **Supabase** (PostgreSQL Database, Auth, and Object Storage), while strictly preserving all existing statutory invariants, deterministic evaluation rules, and the 86-test verification suite.

---

## User Review Required

> [!IMPORTANT]
> **Key Architecture Decisions for Phase 7.1**:
> 1. **Supabase Object Storage Layer**: Evidence uploads will stream directly to Supabase Storage bucket (`compliscan-evidence`) in production (`ENVIRONMENT=production` or `STORAGE_BACKEND=supabase`) with zero dependence on ephemeral Render disk storage. Local filesystem storage remains available for local offline development and automated test isolation.
> 2. **Removal of Test Directory Fallbacks in Reports**: Remove all hardcoded `Test_Images/Peanut_Butter` and `Test_Images/Juice` search loops in `pdf_report_service.py` and `docx_report_service.py`. If evidence is missing or cannot be retrieved, the report will truthfully format `[Evidence Asset Preserved: {filename} (SHA-256: {hash})]`.
> 3. **Unified Evidence Byte Retrieval**: Refactor `AnalysisJobService` and `EvidenceService` to retrieve evidence bytes through an async `EvidenceService.get_evidence_bytes(evidence)` abstraction rather than direct POSIX `open(evidence.storage_path)`.
> 4. **Render & Vercel Manifests**: Provide `render.yaml` (FastAPI Web Service on `$PORT` + Background Worker running `python -m worker.runner`) and `frontend/vercel.json` (SPA history rewrites) with environment-driven `VITE_API_BASE_URL`.

---

## Proposed Changes

### 1. Storage Abstraction & Supabase Storage Client
#### [NEW] [storage_service.py](file:///g:/CompliScan/backend/app/services/storage_service.py)
- Create `StorageService` interface with `LocalStorageBackend` and `SupabaseStorageBackend`.
- `SupabaseStorageBackend` uses async `httpx` to communicate with `{SUPABASE_URL}/storage/v1/object/{SUPABASE_STORAGE_BUCKET}`.
- Support `upload_file(path, bytes, content_type)`, `download_file(path) -> bytes`, `delete_file(path)`.

#### [MODIFY] [config.py](file:///g:/CompliScan/backend/app/core/config.py)
- Add `STORAGE_BACKEND: str = "local"` (defaults to `"supabase"` if `ENVIRONMENT == "production"` and `SUPABASE_URL` is set).
- Fix `assemble_cors_origins` validator to avoid falling back to wildcard `["*"]` when invalid.

#### [MODIFY] [evidence_service.py](file:///g:/CompliScan/backend/app/services/evidence_service.py)
- Update `save_evidence_file` to delegate to `StorageService`.
- Add `get_evidence_bytes(evidence: EvidenceAsset) -> bytes` to safely retrieve image bytes from the active storage backend.

#### [MODIFY] [analysis_job_service.py](file:///g:/CompliScan/backend/app/services/analysis_job_service.py)
- Replace direct `open(evidence.storage_path, "rb")` calls with `await EvidenceService.get_evidence_bytes(evidence)`.

---

### 2. Report Generation Hardening (Eliminate Test Directory Fallbacks)
#### [MODIFY] [pdf_report_service.py](file:///g:/CompliScan/backend/app/services/pdf_report_service.py)
- Remove lines 591–596 (`for candidate_dir in [os.path.join("Test_Images", "Peanut_Butter"), os.path.join("Test_Images", "Juice")]:`).
- Handle missing image files cleanly without hardcoded test folder traversal.

#### [MODIFY] [docx_report_service.py](file:///g:/CompliScan/backend/app/services/docx_report_service.py)
- Remove lines 374–378 (same `Test_Images` fallback loop).
- Handle missing image files cleanly with standard placeholder text.

---

### 3. Frontend Vercel Deployment Configuration
#### [MODIFY] [client.ts](file:///g:/CompliScan/frontend/src/api/client.ts)
- Update `API_BASE` resolution to:
  `const API_BASE = (import.meta.env.VITE_API_BASE_URL ? `${import.meta.env.VITE_API_BASE_URL.replace(/\/$/, '')}/api/v1` : '/api/v1');`

#### [NEW] [vercel.json](file:///g:/CompliScan/frontend/vercel.json)
- SPA routing rewrite rule:
  ```json
  {
    "rewrites": [
      { "source": "/(.*)", "destination": "/index.html" }
    ]
  }
  ```

---

### 4. Render Web Service & Worker Configuration
#### [NEW] [render.yaml](file:///g:/CompliScan/render.yaml)
- Define Render Blueprint:
  1. `type: web`, `name: compliscan-api`, `env: python`, `buildCommand: pip install -r requirements.txt`, `startCommand: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`, `healthCheckPath: /api/v1/health`
  2. `type: worker`, `name: compliscan-worker`, `env: python`, `buildCommand: pip install -r requirements.txt`, `startCommand: python -m worker.runner`

#### [NEW] [Dockerfile](file:///g:/CompliScan/Dockerfile) (Optional standard multi-stage container specification)
- Standard Debian/Python 3.11 container with Tesseract OCR, Poppler, and Uvicorn.

---

### 5. Deployment & Storage Tests
#### [NEW] [test_storage_and_deployment.py](file:///g:/CompliScan/backend/tests/test_storage_and_deployment.py)
- Test `StorageService` local and mock Supabase storage behavior.
- Test evidence byte retrieval through `EvidenceService.get_evidence_bytes`.
- Test report generation when evidence storage is remote or local.
- Verify CORS environment variable assembly.
- Verify `/api/v1/health` endpoint structure.

---

### 6. Phase 7.1 Cloud Deployment Readiness Report
#### [NEW] [phase7_cloud_deployment_readiness.md](file:///g:/CompliScan/docs/phase7_cloud_deployment_readiness.md)
- Complete 22-section audit and readiness report detailing configuration, storage migration, test results, and deployment procedures.

---

## Verification Plan

### Automated Tests
- Run full backend test suite:
  ```powershell
  python -m pytest backend/tests/ -q
  ```
  *(Expected: All 86 existing tests + new storage/deployment tests passing)*

### Frontend Build
- Run frontend build:
  ```powershell
  cd frontend; npm run build
  ```

### Local E2E Flow Validation
- Validate evidence upload -> storage -> hash calculation -> report generation without local test directory fallbacks.
