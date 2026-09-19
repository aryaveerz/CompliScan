# CompliScan LM — Final Deployment Readiness & Report Semantics Audit

**Repository:** CompliScan LM (Legal Metrology Packaged Commodities Verification System)  
**Audit Target:** End-to-End Configuration, Secrets, Reports & Operational Readiness  
**Baseline Commit:** `401690f` (polish: finalize frontend precision and terminology)  
**Current Verification Branch:** `feature/deployment-readiness-audit`
**Date:** September 20, 2026

---

## 1. Baseline & Scope

- **Baseline Git Commit:** `401690f`
- **Previous MVP Milestone:** `efcf9ac`
- **Scope Verification:** This task is strictly a verification and configuration readiness pass. No architectural redesign, no compliance rule modification, no database schema changes, and no state machine alterations were made. Main remains frozen at `401690f`.

---

## 2. Runtime Architecture & Authority Model

CompliScan LM enforces a strict, hierarchical authority model:

```
[ AI / OCR (RapidOCR + Gemini) ]  ──► Suggests token bounding boxes & structured observations
                │
                ▼
[ Deterministic Rules Engine ]    ──► Evaluates LMPC 2011 rules (PASS, POTENTIAL_NON_COMPLIANCE, etc.)
                │
                ▼
[ Inspector Verification ]        ──► Human Inspector verifies token grounding on physical label
                │
                ▼
[ Reviewer Adjudication ]         ──► Human Reviewing Officer records legal determinations / overrides
                │
                ▼
[ FinalAuditRecord ]              ──► Immutable, frozen database snapshot at finalization
                │
                ▼
[ System Reports (PDF / DOCX) ]   ──► Generates official inspection documents solely from FinalAuditRecord
```

> [!IMPORTANT]
> **Authority Principle:** AI models and automated perception engines serve strictly as regulatory assistance. AI never certifies legality, and the software is not a statutory certification authority. Authoritative legal determinations are recorded exclusively by human Reviewing Officers and frozen into `FinalAuditRecord`.

---

## 3. Authoritative Vocabulary & Semantics

### A. Automated System Finding Vocabulary
Deterministic compliance evaluation uses strictly the 6-state `ComplianceResult` enum:
- `PASS`: Declarations satisfy statutory rules based on evidence tokens.
- `POTENTIAL_NON_COMPLIANCE`: Specific statutory requirements are unmet or violated.
- `REQUIRES_REVIEW`: Ambiguous declarations or discretionary thresholds require human evaluation.
- `NOT_APPLICABLE`: Rule does not apply to this commodity category / origin status.
- `INCOMPLETE`: Required evidence views or data points are missing.
- `PROCESSING_FAILED`: Upstream image decode, OCR, or extraction failure.

### B. Human Reviewer Decision Vocabulary
Individual requirement determinations use `ReviewerDeterminationType`:
- `CONFIRMED`: Reviewer agrees with the automated system finding.
- `OVERRIDDEN`: Reviewer records a formal legal override with mandatory statutory rationale.
- `REVISION_REQUESTED`: Reviewer requests corrections from the Inspector.
- `EVIDENCE_REQUESTED`: Reviewer requests additional visual package evidence.

### C. Inspection-Level Final Decision Vocabulary
Recorded in `FinalAuditRecord.final_decision` upon formal finalization:
- `COMPLIANT`: Package label complies with applicable Legal Metrology rules.
- `NON_COMPLIANCE_CONFIRMED`: Final determination of statutory non-compliance.
- `INCONCLUSIVE`: Case could not reach a definitive compliance determination.

---

## 4. Report Semantics Verification

Inspection reports were audited directly against `backend/app/services/pdf_report_service.py` and `backend/app/services/docx_report_service.py`.

### A. Document Header & Title
- **Subtitle:** `LEGAL METROLOGY (PACKAGED COMMODITIES) RULES, 2011`
- **Main Title:** `OFFICIAL REGULATORY INSPECTION & COMPLIANCE REPORT`
- **Terminology Rule:** Unsupported claims of "legal certification", "regulatory certificates", or "compliance certificates" are removed. The document is titled and structured as an authoritative finalized regulatory inspection report.

### B. Ordered Report Sections
Both the PDF and DOCX documents contain exactly four numbered sections following the context and decision headers:

1. **Inspection Context Snapshot Table:**
   - Inspection ID, Case Number, Product Name, Origin Status (`DOMESTIC` / `IMPORTED` / `UNKNOWN`), Rule-Set ID & Version (`LMPC-2011-MVP-RULES (v1.0)`), Evaluation Version (`v1.0`), Finalized Timestamp (UTC), Final Audit Record ID.
2. **Master Final Legal Determination Banner:**
   - Final Adjudicated Determination (`COMPLIANT` / `NON_COMPLIANCE_CONFIRMED` / `INCONCLUSIVE`), Adjudication Rationale.
3. **Section 1 — Evidence Inventory & Cryptographic Integrity Hashes:**
   - Evidence ID, Filename / View (`PRIMARY` / `DERIVED` / `SUPPLEMENTAL`), File Size (KB), SHA-256 Integrity Hash (Change Detection).
4. **Section 2 — Mandatory Requirement Applicability:**
   - Requirement Name, Applicability Status (`MANDATORY` / `EXEMPT`), Statutory Citation (e.g. Rule 6(1)(a)), Legal Basis / Rule Logic.
5. **Section 3 — Compliance Evaluation vs Reviewer Adjudication:**
   - Requirement Name, Automated System Finding (`PASS` / `POTENTIAL_NON_COMPLIANCE` / `REQUIRES_REVIEW` / `NOT_APPLICABLE`), Reviewer Action (`CONFIRMED` / `OVERRIDE`), Final Adjudicated Result, Reviewer Rationale / Override Reason.
6. **Section 4 — Finalization & Record Integrity Status:**
   - **Attestation Statement:** *"This report is generated from the immutable Legal Metrology FinalAuditRecord snapshot. All automated AI extractions and deterministic rules served strictly as regulatory assistance. The final legal determination herein represents the authoritative decision of the authorized Reviewer."*
   - **Record Status Metadata:** Finalized By User ID, Final Audit Record ID, Record State: `FINALIZED & READ_ONLY`.

### C. Cryptographic Hashes & Change Detection
- **SHA-256 Language:** Described strictly as `"SHA-256 Integrity Hash (Change Detection)"` or `"SHA-256 Evidence Hash"`.
- **Integrity Scope:** Hashes verify byte-level file integrity (detecting post-upload file tampering or corruption). They do not claim to prove physical or factual authenticity of the photographed commodity.

### D. Digital Signature Status
- **Signature Status:** **Generated PDF Report.**
- **No PKI Signature:** The PDF is generated programmatically using ReportLab. It contains visual record integrity status and evidence SHA-256 hashes, but is **not** cryptographically signed with an X.509 digital certificate.

### E. PDF vs DOCX Parity
- **Common Source of Truth:** Both formats are generated directly from the immutable `FinalAuditRecord`.
- **Parity:** 1:1 structural and data parity.
- **DOCX Role:** An editable administrative export for departmental filings. Editing a downloaded DOCX does not alter the immutable database record.

---

## 5. Inspector / Reviewer Report Authorization

Verified directly from FastAPI route implementations in `backend/app/api/v1/inspections.py` and `backend/app/api/v1/reviews.py`:

| Role | PDF Download | DOCX Download | Access Scope |
|---|---|---|---|
| **Inspector** | Authorized | Authorized | Own finalized inspections only (`created_by_id == current_user.id`). Attempting to download another inspector's report returns **HTTP 403 Forbidden**. |
| **Reviewer** | Authorized | Authorized | **All** finalized inspections across the organization. |
| **Admin** | Authorized | Authorized | **All** finalized inspections across the organization. |

### Pre-Finalization Access Invariant:
- Attempting to download a report (PDF or DOCX) for an unfinalized inspection returns **HTTP 404 Not Found** (`NotFoundError: Final audit record for inspection {id} not found`). Reports cannot be generated in draft or review states.

### Download Audit Logging:
- Every report retrieval emits an immutable `AuditEventType.REPORT_DOWNLOADED` event with `actor_id`, `actor_role`, `inspection_id`, `format` (`pdf` or `docx`), `case_number`, and `final_record_id`.

---

## 6. Dependency Verification

### `reportlab` & `python-docx`
- **Code Usage:** `backend/app/services/pdf_report_service.py` imports `reportlab` (Platypus flowables, styles, tables) and `backend/app/services/docx_report_service.py` imports `docx` (`python-docx`).
- **Audit Finding:** Prior to this audit, `reportlab` and `python-docx` were imported at runtime but omitted from `backend/requirements.txt`.
- **Remediation:** Explicitly pinned in `backend/requirements.txt` as `reportlab>=4.1.0` and `python-docx>=1.1.0`. No other dependencies were added.

---

## 7. Required Environment Variables Inventory

| Variable | Used By | Required? | Secret? | Classification | Example / Default | Purpose |
|---|---|---|---|---|---|---|
| `GEMINI_API_KEY` | Backend & Worker | **YES** | **YES** | REQUIRED SECRET | `AIzaSy...` | Server-side key for Gemini 2.5 Flash structured extraction. |
| `GEMINI_MODEL` | Backend & Worker | NO | NO | OPTIONAL | `gemini-2.5-flash` | Gemini model name. |
| `SUPABASE_URL` | Backend | **YES** | NO | REQUIRED NON-SECRET | `https://[REF].supabase.co` | Supabase project URL for GoTrue Auth and JWKS retrieval. |
| `SUPABASE_ANON_KEY` | Backend | **YES** | NO | REQUIRED NON-SECRET | `sb_publishable_...` | Supabase anon key for client authentication. |
| `SUPABASE_SERVICE_ROLE_KEY` | Backend & Scripts | **YES** | **YES** | REQUIRED SECRET | `sb_secret_...` | Admin service role key for user seeding and identity cleanup. |
| `SUPABASE_JWT_SECRET` | Backend | Conditional | **YES** | REQUIRED SECRET (if HS256) | `uuid-or-secret` | Supabase HS256 token verification key. |
| `SUPABASE_AUTH_AUDIENCE` | Backend | NO | NO | OPTIONAL | `authenticated` | Expected JWT `aud` claim. |
| `DATABASE_URL` | Backend & Worker | **YES** | **YES** | REQUIRED SECRET | `postgresql+asyncpg://...:6543/postgres?ssl=require` | Async connection string (Transaction Pooler). |
| `SYNC_DATABASE_URL` | Alembic Migrations | **YES** | **YES** | REQUIRED SECRET | `postgresql+psycopg://...:5432/postgres?sslmode=require` | Sync connection string (Session Pooler). |
| `SECRET_KEY` | Backend | **YES** in Prod | **YES** | REQUIRED SECRET | `random-hex-string` | Internal application secret. |
| `ENVIRONMENT` | Backend | NO | NO | OPTIONAL | `development` / `production` | Environment name. |
| `CORS_ORIGINS` | Backend | **YES** in Prod | NO | REQUIRED NON-SECRET | `["http://localhost:5173"]` | Allowed frontend origins. |
| `LOCAL_STORAGE_DIR` | Backend & Worker | NO | NO | OPTIONAL | `backend/uploads` | Local directory for evidence storage. |
| `WORKER_LEASE_SECONDS` | Worker | NO | NO | OPTIONAL | `60` | Job claim lease timeout. |
| `WORKER_POLL_INTERVAL_SECONDS` | Worker | NO | NO | OPTIONAL | `2.0` | Idle queue polling frequency. |
| `WORKER_MAX_JOB_ATTEMPTS` | Worker | NO | NO | OPTIONAL | `3` | Max job execution retries. |
| `SEED_INSPECTOR_PASSWORD` | Seed Script | NO | **YES** | DEVELOPMENT-ONLY | `Password@Insp1` | Seed password for demo inspector. |
| `SEED_REVIEWER_PASSWORD` | Seed Script | NO | **YES** | DEVELOPMENT-ONLY | `Password@rev1` | Seed password for demo reviewer. |

---

## 8. Final Configuration Verification

1. **Gemini Configuration:**
   - Server-side only; never passed to React/browser.
   - Key lookup: `settings.GEMINI_API_KEY`.
   - Missing key raises `ConfigurationError` immediately.
   - Failures leave the job in `FAILED` state without generating false compliance results.
2. **Supabase Auth Configuration:**
   - Live Supabase JWKS asymmetric validation (`ES256` / `RS256`) via `{SUPABASE_URL}/auth/v1/.well-known/jwks.json`.
   - Symmetric fallback (`HS256`) via `SUPABASE_JWT_SECRET`.
3. **Database & Migrations:**
   - Schema managed exclusively by Alembic (`alembic upgrade head`).
   - Latest revision: `f6a7b8c9d0e1_add_phase5_performance_indexes.py`.
4. **Worker Startup:**
   - Entrypoint: `python -m worker.runner`.
   - Required for processing image quality, OCR, extraction, and compliance jobs.
5. **Frontend API & Proxy:**
   - Dev: `frontend/vite.config.ts` proxies `/api` to `http://127.0.0.1:8000`.
   - Prod: Reverse proxy routes `/api/v1` to FastAPI backend.
6. **CORS:**
   - Explicit origins configured via `CORS_ORIGINS` (never `*` when credentials are enabled).
7. **Storage:**
   - Single-node local filesystem (`backend/uploads`) with SHA-256 change detection.

---

## 9. Remaining Verified Conditions

1. **Single-Node Storage Condition:** In multi-container environments, `LOCAL_STORAGE_DIR` must be mounted as a shared persistent volume.
2. **Worker Separation:** The API server and background worker runner are separate processes. Both must be running for inspections to process.
3. **Manual Migration Step:** `alembic upgrade head` must be executed before application startup.

---

## 10. Final Assessment

### **READY — CONFIGURATION AND REPORT SEMANTICS VERIFIED**

The CompliScan LM MVP is fully verified. Report semantics accurately reflect the authority model, all configuration secrets and environment variables are documented with safe placeholders, direct runtime dependencies are properly specified, and the complete workflow is reproducible end-to-end.
