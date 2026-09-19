# CompliScan LM — Final Deployment Readiness Audit

**Repository:** CompliScan LM (Legal Metrology Packaged Commodities Verification System)  
**Audit Target:** End-to-End Configuration, Secrets, Reports & Operational Readiness  
**Baseline Commit:** `401690f` (polish: finalize frontend precision and terminology)  
**Date:** September 20, 2026  

---

## 1. Baseline

The audit was conducted strictly against the frozen MVP baseline:
- **Baseline Git Commit:** `401690f`
- **Previous Milestone:** `efcf9ac`
- **Scope Verification:** No feature development, no schema alterations, no state machine changes, and no compliance rule redesign were performed. Only configuration, documentation, and dependency precision fixes were made.

---

## 2. Runtime Architecture

CompliScan LM operates as an asynchronous, queue-driven, two-tiered regulatory inspection workflow:

```
[ Frontend (React / Vite) ] ── (HTTP / REST + Bearer JWT) ──► [ Backend (FastAPI :8000) ]
                                                                       │
                                              ┌────────────────────────┴────────────────────────┐
                                              ▼                                                 ▼
                                     [ Supabase Auth (GoTrue) ]                     [ PostgreSQL / SQLite ]
                                    (Token issuance & JWKS ES256)                   (Durable Analysis Jobs Queue)
                                                                                                │
                                                                                                ▼
                                                                                   [ Worker (python -m worker.runner) ]
                                                                                                │
                                         ┌──────────────────────────────────────────────────────┴─────────────────────────────────┐
                                         ▼                                                      ▼                                 ▼
                         [ RapidOCR PP-OCRv4 (ONNX) ]                               [ Gemini 2.5 Flash API ]         [ Deterministic Rules Engine ]
                          (Detection & Token Coordinates)                             (7 Statutory Domains)            (Statutory Findings Generation)
```

### Complete End-to-End Workflow:
1. **Authentication:** User logs in via Supabase Auth GoTrue; FastAPI validates JWT via ES256 JWKS or configured secret.
2. **Inspection Case Creation:** Inspector creates inspection docket (`DRAFT` state).
3. **Evidence Ingestion:** Package label images uploaded; SHA-256 computed; saved to `LOCAL_STORAGE_DIR`; `IMAGE_QUALITY` job enqueued.
4. **Image Quality Assessment:** Worker runs deterministic blur/brightness/contrast/resolution evaluation; if `USABLE`, auto-enqueues `PERCEPTION` job.
5. **OCR Perception:** Worker runs PaddleOCR PP-OCRv4 (RapidOCR ONNX Runtime); produces immutable token stream with bounding boxes; auto-enqueues `EXTRACTION` job.
6. **Gemini Semantic Extraction:** Worker calls Gemini 2.5 Flash via `google-genai` SDK with strict Pydantic structured output schema (`StructuredDeclarations`); validates token provenance.
7. **Applicability Evaluation:** Determines mandatory rules based on product category, origin status, and declared commodity.
8. **Deterministic Compliance Evaluation:** Evaluates statutory rules against extracted declarations without hallucination.
9. **Inspector Verification:** Inspector inspects tokens against visual image overlay and signs off on verification checklist.
10. **Submission:** Inspector transitions docket from `DRAFT` to `SUBMITTED_FOR_REVIEW`.
11. **Reviewer Adjudication:** Reviewing Officer reviews findings, records confirmation or override with mandatory statutory rationale.
12. **Finalization:** Atomically constructs the immutable `FinalAuditRecord` and freezes docket to `READ_ONLY`.
13. **Regulatory Reporting:** On-demand generation of official **PDF** and editable **DOCX** reports derived solely from `FinalAuditRecord`.
14. **Audit Trail & Dashboard:** Complete chronological ledger of all lifecycle and download events.

---

## 3. Required Environment Variables

The following authoritative inventory contains all configuration variables used across the repository:

| Variable | Used By | Required? | Secret? | Classification | Example Format | Purpose |
|---|---|---|---|---|---|---|
| `GEMINI_API_KEY` | Backend & Worker | **YES** | **YES** | REQUIRED SECRET | `AIzaSy...` | API key for Google Gemini 2.5 Flash semantic extraction. Server-side only. |
| `GEMINI_MODEL` | Backend & Worker | NO (has default) | NO | OPTIONAL | `gemini-2.5-flash` | Name of the Gemini model used for structured extraction. |
| `SUPABASE_URL` | Backend | **YES** | NO | REQUIRED NON-SECRET | `https://[REF].supabase.co` | Supabase project endpoint for Auth GoTrue REST API and JWKS endpoint. |
| `SUPABASE_ANON_KEY` | Backend | **YES** | NO | REQUIRED NON-SECRET | `sb_publishable_...` | Supabase client anon/publishable key for user authentication. |
| `SUPABASE_SERVICE_ROLE_KEY` | Backend & Scripts | **YES** | **YES** | REQUIRED SECRET | `sb_secret_...` | Supabase secret key for admin user seeding and orphan cleanup. |
| `SUPABASE_JWT_SECRET` | Backend | Conditional | **YES** | REQUIRED SECRET (if HS256) | `uuid-or-secret-string` | Secret key for Supabase Auth HS256 token verification. Not needed for ES256 JWKS. |
| `SUPABASE_AUTH_AUDIENCE` | Backend | NO (has default) | NO | OPTIONAL | `authenticated` | Expected JWT `aud` claim (default: `"authenticated"`). |
| `DATABASE_URL` | Backend & Worker | **YES** | **YES** | REQUIRED SECRET | `postgresql+asyncpg://...:6543/postgres?ssl=require` | Asynchronous database connection string (Transaction Pooler). |
| `SYNC_DATABASE_URL` | Alembic Migrations | **YES** | **YES** | REQUIRED SECRET | `postgresql+psycopg://...:5432/postgres?sslmode=require` | Synchronous database connection string (Session Pooler). |
| `SECRET_KEY` | Backend | **YES** in Prod | **YES** | REQUIRED SECRET | `random-hex-string` | Application internal encryption key. |
| `ENVIRONMENT` | Backend | NO (has default) | NO | OPTIONAL | `production` / `development` | Operating environment name. |
| `DEBUG` | Backend | NO (has default) | NO | DEVELOPMENT-ONLY | `False` | Debug mode toggle. |
| `CORS_ORIGINS` | Backend | **YES** in Prod | NO | REQUIRED NON-SECRET | `["https://app.domain.gov.in"]` | Allowed CORS origins for cross-origin browser requests. |
| `LOCAL_STORAGE_DIR` | Backend & Worker | NO (has default) | NO | OPTIONAL | `backend/uploads` | Persistent directory for single-node evidence asset storage. |
| `WORKER_LEASE_SECONDS` | Worker | NO (has default) | NO | OPTIONAL | `60` | Job claim lease lock duration in seconds. |
| `WORKER_POLL_INTERVAL_SECONDS` | Worker | NO (has default) | NO | OPTIONAL | `2.0` | Queue polling sleep interval when idle. |
| `WORKER_MAX_JOB_ATTEMPTS` | Worker | NO (has default) | NO | OPTIONAL | `3` | Maximum automatic job retry attempts before failing. |
| `SEED_INSPECTOR_PASSWORD` | Seed Script | NO | **YES** | DEVELOPMENT-ONLY | `Password@Insp1` | Password used by `seed_supabase_users.py` to provision inspector. |
| `SEED_REVIEWER_PASSWORD` | Seed Script | NO | **YES** | DEVELOPMENT-ONLY | `Password@rev1` | Password used by `seed_supabase_users.py` to provision reviewer. |

---

## 4. Gemini Configuration

- **Environment Variable:** `GEMINI_API_KEY`
- **Model Name:** `gemini-2.5-flash` (configurable via `GEMINI_MODEL`)
- **SDK Provider:** Official `google-genai` Python SDK (`from google import genai`)
- **Runtime Location:** Consumed exclusively within `backend/app/services/extraction_service.py` by background worker execution during `JobType.EXTRACTION`.
- **Frontend Exposure:** **ZERO.** `GEMINI_API_KEY` is not present in frontend code or Vite variables and is never transmitted over client APIs.
- **Worker Dependency:** Worker requires `GEMINI_API_KEY` to process extraction jobs.
- **Missing / Invalid Key Behavior:**
  - If `GEMINI_API_KEY` is empty, `ExtractionService.get_client()` raises `ConfigurationError("GEMINI_API_KEY is not configured in backend settings.")`.
  - If the key is invalid or Gemini API times out / returns malformed output, `AnalysisError` is raised.
  - The worker catches this, records `job.error_message`, and retries up to 3 times before setting `job.status = "FAILED"`.
  - **Crucial Rule Maintained:** Technical AI failures are **NEVER converted into a PASS, POTENTIAL_NON_COMPLIANCE, or NOT_APPLICABLE**. They remain explicit processing failure states.

---

## 5. Supabase Configuration

The application integrates with Supabase as follows:
- **Supabase Auth (GoTrue):** User accounts and passwords live in Supabase GoTrue Auth. Login requests are authenticated via GoTrue REST API (`/auth/v1/token?grant_type=password`).
- **Supabase PostgreSQL:** Application data is stored in the Supabase PostgreSQL database via SQLAlchemy asyncpg connection.
- **Supabase Storage:** Not required for MVP; the MVP uses local filesystem storage (`backend/uploads`).
- **Required Supabase Values:**
  - `SUPABASE_URL`: `https://[PROJECT-REF].supabase.co`
  - `SUPABASE_ANON_KEY`: Supabase anon/publishable API key
  - `SUPABASE_SERVICE_ROLE_KEY`: Supabase secret service role key (for user seeding script and orphan identity cleanup)
  - `DATABASE_URL`: Connection string to PostgreSQL transaction pooler (port 6543)
  - `SYNC_DATABASE_URL`: Connection string to PostgreSQL session pooler (port 5432)

---

## 6. Database Configuration & Migrations

- **Database Engine:** PostgreSQL (Supabase Managed or self-hosted) with SQLAlchemy 2.0.
- **Migration System:** Alembic.
- **Latest Migration (`head`):** `f6a7b8c9d0e1_add_phase5_performance_indexes.py`.
- **Migration Startup Behavior:** Migrations are **NOT** run automatically on FastAPI startup (by design, to avoid multi-instance concurrency locks).
- **Migration Command:**
  ```bash
  alembic upgrade head
  ```
- **Execution Requirement:** The operator must run `alembic upgrade head` before starting the FastAPI server and background worker.

---

## 7. Authentication Architecture

- **Protocol:** OpenID Connect / OAuth2 Bearer Tokens issued by Supabase GoTrue Auth.
- **Token Verification:**
  - **Asymmetric JWKS (Primary/Live Mode):** Verifies tokens using public ECDSA P-256 (`ES256`) or RSA (`RS256`) keys fetched directly from `{SUPABASE_URL}/auth/v1/.well-known/jwks.json`. Cached in-memory with automatic 1-hour refresh.
  - **Symmetric Secret (Fallback/Testing Mode):** Verifies `HS256` tokens using `SUPABASE_JWT_SECRET`.
- **Claims Enforced:**
  - `exp`: Expiration timestamp (strictly validated).
  - `sub`: User UUID (mapped 1:1 to `public.users.id`).
  - `aud`: Audience (`"authenticated"`).
  - `iss`: Issuer (`{SUPABASE_URL}/auth/v1`).
- **Role Enforcement (RBAC):** Roles (`INSPECTOR`, `REVIEWER`, `ADMIN`) are stored authoritatively in `public.users.role` and verified via FastAPI `require_role()` dependency guards.

---

## 8. Worker

- **Startup Entrypoint:**
  ```bash
  python -m worker.runner
  ```
- **Architecture:** Standalone polling process that claims jobs from `analysis_jobs` queue table using atomic `with_for_update(skip_locked=True)` row-level locking.
- **What happens if only FastAPI is started?**
  - Inspection dockets and evidence uploads succeed at the API layer.
  - Background analysis jobs (`IMAGE_QUALITY`, `PERCEPTION`, `EXTRACTION`, `EVALUATION`) remain in `PENDING` status.
  - Analysis does not progress to OCR or compliance evaluation until `python -m worker.runner` is started.

---

## 9. Evidence Storage

- **Storage Location:** Configured via `LOCAL_STORAGE_DIR` (default: `backend/uploads`).
- **Subdirectory Layout:** `backend/uploads/{inspection_id}/{evidence_id}_{safe_filename}`.
- **Integrity Validation:** Every evidence file has its SHA-256 computed on upload and stored in `evidence_assets.sha256_hash`.
- **Single-Node Condition:** Backend and Worker must have access to the same physical disk directory or shared volume mount.
- **Container Persistence:** In Docker/Kubernetes, `LOCAL_STORAGE_DIR` must be mounted as a persistent volume to ensure evidence is not lost across container restarts.

---

## 10. OCR Runtime

- **Perception Engine:** RapidOCR (`rapidocr-onnxruntime>=1.2.3`) running PaddleOCR PP-OCRv4 models via `onnxruntime>=1.20.0`.
- **Model Distribution:** PP-OCRv4 ONNX model weights are packaged directly within `rapidocr-onnxruntime`.
- **Offline Readiness:** Does not require runtime internet access or dynamic model downloads. Works fully offline once Python packages are installed.

---

## 11. PDF Report Structure

Generated dynamically in-memory via ReportLab strictly from the immutable `FinalAuditRecord`.

**Complete Ordered Section Breakdown:**
1. **Header Banner:** `"LEGAL METROLOGY (PACKAGED COMMODITIES) RULES, 2011"` / `"OFFICIAL REGULATORY INSPECTION & COMPLIANCE REPORT"`.
2. **Inspection Context Snapshot Table:** Inspection ID, Case Number, Product Name, Origin Status, Rule-Set ID & Version, Evaluation Version, Finalized Timestamp, Final Record ID.
3. **Master Final Legal Determination Banner:** Final Adjudicated Determination (`COMPLIANT` / `NON_COMPLIANT` / `PASS` / `FAIL`), Final Adjudication Rationale.
4. **Section 1 — Evidence Inventory & Cryptographic Integrity Hashes:** Evidence ID, Filename / View, File Size, SHA-256 Integrity Hash (Change Detection).
5. **Section 2 — Mandatory Requirement Applicability:** Requirement Name, Applicability Status (`MANDATORY` / `EXEMPT`), Statutory Citation (e.g. Rule 6(1)(a)), Legal Basis / Rule Logic.
6. **Section 3 — Compliance Evaluation vs Reviewer Adjudication:** Requirement Name, Automated System Finding, Reviewer Action (`CONFIRMED` / `OVERRIDE`), Final Adjudicated Result, Reviewer Rationale / Override Reason.
7. **Section 4 — Legal Metrology Officer Sign-Off & Archival Seal:** Official Regulatory Certification statement, Finalized By User ID, Archival Record ID, Audit State: `FINALIZED & READ_ONLY`.

- **Visual Evidence in PDF:** Text and hashes are included; raw image binaries and bounding box diagrams are not rendered inside the PDF.
- **Digital Signatures:** No cryptographic PKI (X.509) digital signature is attached; the document features an immutable visual archival seal and SHA-256 evidence integrity hashes.

---

## 12. DOCX Report Structure

Generated dynamically in-memory via `python-docx` strictly from the immutable `FinalAuditRecord`.
- **Data Parity:** 1:1 structural and data parity with the official PDF report.
- **Sections:** Identical four-section structure (Context Snapshot, Master Decision, Evidence Hashes, Applicability, Compliance vs Adjudication, Sign-Off Seal).
- **Authoritative Status:** The DOCX is provided as an editable export format for administrative filings; the immutable `FinalAuditRecord` stored in the database remains the sole authoritative source of truth.

---

## 13. Inspector Permissions

- **PDF Download:** Authorized for inspections created by the Inspector (`created_by_id == current_user.id`) **AFTER** finalization.
- **DOCX Download:** Authorized for inspections created by the Inspector **AFTER** finalization.
- **IDOR Protection:** Attempting to download reports for another inspector's inspection returns HTTP 403 Forbidden.

---

## 14. Reviewer Permissions

- **PDF Download:** Authorized for **ANY** finalized inspection across the system.
- **DOCX Download:** Authorized for **ANY** finalized inspection across the system.
- **Inspection Access:** Full read access across all inspection dockets in the organization.

---

## 15. Finalization Requirement

- **Pre-Finalization Reports:** Reports **CANNOT** be downloaded before an inspection is finalized.
- **Behavior:** Attempting to call `/report/pdf`, `/report/docx`, or `/final-report` on an unfinalized inspection returns HTTP 404 (`Final audit record for inspection {inspection_id} not found`).
- **Design Invariant:** Reports are only ever generated from frozen, immutable `FinalAuditRecord` instances.

---

## 16. Report Audit Events

- **Audit Logging:** Every report download triggers an immutable audit log entry.
- **Event Type:** `AuditEventType.REPORT_DOWNLOADED`.
- **Logged Details:**
  - `inspection_id`: Target inspection UUID.
  - `actor_id`: User UUID of the downloader.
  - `actor_role`: Role (`INSPECTOR`, `REVIEWER`, `ADMIN`).
  - `format`: `"pdf"` or `"docx"`.
  - `case_number`: Case docket identifier.
  - `final_record_id`: UUID of the referenced `FinalAuditRecord`.
  - `timestamp`: UTC timestamp of download.

---

## 17. Manual Configuration Checklist

See [deployment_configuration_checklist.md](file:///g:/CompliScan/docs/deployment_configuration_checklist.md) for full parameters. In summary, an operator must supply:
1. `GEMINI_API_KEY` in `.env`.
2. Supabase project credentials (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`) in `.env`.
3. Database connection URLs (`DATABASE_URL`, `SYNC_DATABASE_URL`) in `.env`.
4. Run `alembic upgrade head`.
5. Run `python backend/scripts/seed_supabase_users.py`.

---

## 18. Startup Runbook

See [deployment_runbook.md](file:///g:/CompliScan/docs/deployment_runbook.md) for the complete 16-step operational procedure.

---

## 19. Fresh Deployment Test

- **Configuration Template:** Verified `.env.example` contains all variables with safe placeholders.
- **Dependencies:** Updated `backend/requirements.txt` to include `reportlab>=4.1.0` and `python-docx>=1.1.0`.
- **Database Migrations:** Clean Alembic migration graph confirmed ending at `f6a7b8c9d0e1_add_phase5_performance_indexes.py`.
- **User Provisioning:** Seed script `backend/scripts/seed_supabase_users.py` verified idempotent and safe.

---

## 20. Security Check

- **Git Secret Scan:** Confirmed `.env` is ignored by `.gitignore` and not tracked in git.
- **Tracked Files:** No live API keys, JWT secrets, or production passwords exist in version-controlled files.
- **Frontend Safety:** No server secrets (Gemini API key, database passwords, Supabase service-role keys) are referenced in frontend source files or exposed via `VITE_` variables.

---

## 21. Known Production Conditions

1. **Single-Node Filesystem Storage:** Evidence files are stored locally in `backend/uploads`. In multi-container setups, this path must be mounted to a shared persistent volume.
2. **Worker Process Separation:** The FastAPI API server does not process the background analysis queue inline; `python -m worker.runner` must be run as a dedicated process or container.
3. **Database Migration Step:** `alembic upgrade head` must be executed manually during deployment before starting the application services.

---

## 22. Final Assessment

### **READY — END-TO-END CONFIGURATION DOCUMENTED**

CompliScan LM is completely documented and ready for operational deployment. An operator with access to a Supabase project and a Google Gemini API key can configure and run the full end-to-end Legal Metrology compliance workflow reliably without encountering undocumented settings, hidden dependencies, or unexpected startup failures.
