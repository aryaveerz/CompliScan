# COMPLISCAN LM — PHASE 7.0 REPOSITORY FORENSIC INVENTORY
## Complete Inventory, File Classification, and Lifecycle Mapping

**Audit Date:** 2026-09-20  
**Classification Standard:** Precise Lifecycle & Source Separation  
**Status:** RECONCILED BLUEPRINT — AUDIT & PLANNING ONLY (ZERO CODE MUTATIONS)

---

## 1. Classification Categories

| Classification | Meaning & Policy |
|---|---|
| **`SOURCE_CODE`** | Active production backend services, schemas, models, API routers, worker runner. |
| **`FRONTEND_SOURCE`** | Active React 18, TypeScript, Vite components, pages, context, styles. |
| **`CONFIGURATION`** | Production and development settings, Pydantic BaseSettings, `.env.example`. |
| **`DATABASE_SCHEMA`** | SQLAlchemy ORM declarative models and session factories. |
| **`MIGRATION`** | Alembic migration scripts and database evolution history. |
| **`DEPLOYMENT`** | Cloud manifests, `render.yaml`, `vercel.json`, container configs. |
| **`TEST_CODE`** | Automated pytest suites in `backend/tests/` (86 tests). |
| **`VALIDATED_TEST_FIXTURE`** | Controlled test images (`Test_Images/`) used strictly for offline validation. **NEVER production evidence.** |
| **`HISTORICAL_ARTIFACT`** | Prior milestone logs, reconciliation reports, archived architecture notes. |
| **`HISTORICAL_AUDIT_RECORD`** | Sealed execution runs (`scratch/runs/*/final_audit_record.json`) from test campaigns. |
| **`TOOL`** | Universal dataset-agnostic CLI utilities (`scratch/execute_e2e_pipeline.py`, `scratch/run_forensic_verification.py`). |

---

## 2. Complete Inventory Matrix

### 2.1 Backend Subsystem (`backend/`)

| File Path | Classification | Current State | Purpose & Role | Future Action |
|---|---|---|---|---|
| `backend/app/main.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | FastAPI application entrypoint, CORS, lifespan, exception handlers | **KEEP** |
| `backend/app/core/config.py` | `CONFIGURATION` | `CURRENT — VERIFIED` | Pydantic Settings, env parsing, canonical defaults (`gemini-3.6-flash`) | **KEEP** |
| `backend/app/core/security.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | Supabase JWKS ES256 verification, token decode, SHA-256 computation | **KEEP** |
| `backend/app/core/errors.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | Domain exception hierarchy & FastAPI HTTP error handlers | **KEEP** |
| `backend/app/db/base.py` | `DATABASE_SCHEMA` | `CURRENT — VERIFIED` | SQLAlchemy ORM DeclarativeBase | **KEEP** |
| `backend/app/db/session.py` | `DATABASE_SCHEMA` | `CURRENT — VERIFIED` | Async/sync session factories (PostgreSQL & SQLite) | **KEEP** |
| `backend/app/models/*.py` | `DATABASE_SCHEMA` | `CURRENT — VERIFIED` | 13 ORM models: user, inspection, evidence, ocr, declaration, compliance, etc. | **KEEP** |
| `backend/app/schemas/*.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | Pydantic validation schemas for API requests/responses | **KEEP** |
| `backend/app/api/v1/*.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | API routes: auth, inspections, evidence, compliance, reviews, verification, dashboard, health | **KEEP** |
| `backend/app/api/deps.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | FastAPI dependency injections: get_current_user, require_inspector, require_reviewer | **KEEP** |
| `backend/app/services/evidence_service.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | Evidence validation, hashing, saving, retrieval (Local filesystem) | **KEEP** (Refactor for Supabase Storage in Phase 7.1) |
| `backend/app/services/image_quality_service.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | Laplacian blur, brightness, contrast, dimensions | **KEEP** |
| `backend/app/services/barcode_service.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | OpenCV Barcode/QR detection and EAN-13 decoding | **KEEP** |
| `backend/app/services/ocr_service.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | Tesseract/Cloud OCR token extraction with bounding boxes | **KEEP** |
| `backend/app/services/extraction_service.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | Gemini 3.6 Flash extraction & token provenance check | **KEEP** |
| `backend/app/services/prompts/extraction_v1.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | Versioned system instruction and prompt builder | **KEEP** |
| `backend/app/services/product_synthesis_service.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | Multi-image declaration synthesis & conflict tracking | **KEEP** |
| `backend/app/services/declaration_validation_service.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | Date validation, temporal checks, cross-panel conflicts | **KEEP** |
| `backend/app/services/compliance_service.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | Deterministic LMPC 2011 statutory rule evaluators | **KEEP** |
| `backend/app/services/finalization_service.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | 7-gate validation, immutable FinalAuditRecord creation | **KEEP** |
| `backend/app/services/report_data_builder.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | Transforms FAR into typed ReportViewModel | **KEEP** |
| `backend/app/services/pdf_report_service.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | ReportLab statutory PDF dossier generation (contains Test_Images fallback) | **KEEP** (Remove Test_Images fallback in Phase 7.1) |
| `backend/app/services/docx_report_service.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | python-docx statutory DOCX dossier generation (contains Test_Images fallback) | **KEEP** (Remove Test_Images fallback in Phase 7.1) |
| `backend/app/services/analysis_job_service.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | Durable queue, SKIP LOCKED job claiming, lease recovery | **KEEP** |
| `backend/app/services/audit_service.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | Append-only AuditEvent logger | **KEEP** |
| `backend/app/services/auth_service.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | Backend-mediated Supabase Auth sign-in and user provisioning | **KEEP** |
| `backend/app/services/supabase_auth_client.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | HTTP client communicating with Supabase GoTrue API | **KEEP** |
| `backend/tests/*.py` | `TEST_CODE` | `CURRENT — VERIFIED` | 12 test suites (86 passing tests) | **KEEP** |

---

### 2.2 Frontend Subsystem (`frontend/`)

| File Path | Classification | Current State | Purpose & Role | Future Action |
|---|---|---|---|---|
| `frontend/src/main.tsx` | `FRONTEND_SOURCE` | `CURRENT — VERIFIED` | React 18 DOM mount entrypoint | **KEEP** |
| `frontend/src/App.tsx` | `FRONTEND_SOURCE` | `CURRENT — VERIFIED` | AppShell routing, AuthProvider, protected routes | **KEEP** |
| `frontend/src/api/client.ts` | `FRONTEND_SOURCE` | `CURRENT — VERIFIED` | REST API client (`API_BASE = '/api/v1'`) | **KEEP** (Wire `VITE_API_BASE_URL` in Phase 7.2) |
| `frontend/src/context/AuthContext.tsx` | `FRONTEND_SOURCE` | `CURRENT — VERIFIED` | Global authentication state and JWT token management | **KEEP** |
| `frontend/src/components/CameraCapture.tsx` | `FRONTEND_SOURCE` | `CURRENT — VERIFIED` | In-browser camera capture with guidelines and preview | **KEEP** |
| `frontend/src/components/*.tsx` | `FRONTEND_SOURCE` | `CURRENT — VERIFIED` | UI components: Header, Sidebar, EvidenceUploader, StatusBadge, etc. | **KEEP** |
| `frontend/src/pages/*.tsx` | `FRONTEND_SOURCE` | `CURRENT — VERIFIED` | Pages: DashboardPage, InspectionListPage, NewInspectionPage, InspectionWorkspacePage, HistoryPage, LoginPage | **KEEP** |
| `frontend/package.json` | `CONFIGURATION` | `CURRENT — VERIFIED` | NPM dependencies and scripts (build, dev, preview) | **KEEP** |
| `frontend/vite.config.ts` | `CONFIGURATION` | `CURRENT — VERIFIED` | Vite bundler configuration | **KEEP** |

---

### 2.3 Database Migrations & Background Worker

| File Path | Classification | Current State | Purpose & Role | Future Action |
|---|---|---|---|---|
| `alembic/env.py` | `MIGRATION` | `CURRENT — VERIFIED` | Alembic runtime environment loading SQLAlchemy metadata | **KEEP** |
| `alembic/versions/*.py` | `MIGRATION` | `CURRENT — VERIFIED` | 9 migration revisions (Head: `h8i9j0k1l2m3`) | **KEEP** |
| `worker/runner.py` | `SOURCE_CODE` | `CURRENT — VERIFIED` | Standalone worker process polling queue via `FOR UPDATE SKIP LOCKED` | **KEEP** |

---

### 2.4 Test Fixtures, Tools, Historical Records & Documentation

| File Path | Classification | Current State | Purpose & Role | Future Action |
|---|---|---|---|---|
| `Test_Images/` | `VALIDATED_TEST_FIXTURE` | `CURRENT — VERIFIED` | Controlled test imagery for Juice and Peanut Butter datasets. **Never production evidence.** | **KEEP** for automated regression tests |
| `scratch/execute_e2e_pipeline.py` | `TOOL` | `CURRENT — VERIFIED` | Dataset-agnostic universal E2E pipeline runner | **KEEP** (Move to `scripts/` in Phase 7.2) |
| `scratch/run_forensic_verification.py` | `TOOL` | `CURRENT — VERIFIED` | Universal forensic verification CLI tool | **KEEP** (Move to `scripts/` in Phase 7.2) |
| `scratch/runs/*/` | `HISTORICAL_AUDIT_RECORD` | `CURRENT — VERIFIED` | Immutable FAR JSON dumps and audit records from test runs | **KEEP** (Never delete historical records) |
| `docs/remediation/` | `HISTORICAL_ARTIFACT` | `CURRENT — VERIFIED` | Forensic audit reports and manifests for Juice & Peanut Butter | **KEEP** |
| `docs/final_validation/` | `HISTORICAL_ARTIFACT` | `CURRENT — VERIFIED` | Phase 6 validation matrix and executive reports | **KEEP** |
| `Emblem_of_India.svg.webp` | `SOURCE_CODE` / `ASSET` | `CURRENT — VERIFIED` | Official emblem asset used on PDF statutory reports | **KEEP** |
| `phase0_*.md` to `phase5_*.md` | `HISTORICAL_ARTIFACT` | `CURRENT — VERIFIED` | Historical phase completion logs in root | **ARCHIVE** to `docs/archive/` in Phase 7.2 |
