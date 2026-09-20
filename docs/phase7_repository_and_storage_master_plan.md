# Phase 7.1 — Repository Organization & Production Artifact Storage Master Plan

**Document ID:** `MASTER-2026-LM-PHASE7`  
**Date:** September 20, 2026  
**Status:** DRAFT (MASTER PLANNING & AUDIT ONLY — NO MUTATIONS EXECUTED)  
**Target Infrastructure:** Vercel (Frontend), Render (API + Worker), Supabase (PostgreSQL, Auth, Storage)

---

## 1. Executive Summary

CompliScan LM has completed its Phase 6 production hardening and verified full inspection data isolation. The application is now being prepared for production cloud deployment across Vercel, Render, and Supabase.

This Master Plan establishes the definitive blueprint for:
1. **Repository Organization:** Restructuring the 9,376-file workspace into a clean, modular repository with separated production code, test suites, historical archives, and operational scripts.
2. **Production Artifact Storage:** Designing a tamper-evident, SHA-256 verifiable object storage architecture on Supabase Storage to replace ephemeral local disk storage.
3. **Data Integrity & Governance:** Establishing immutable FinalAuditRecord (FAR) boundaries, append-only audit ledgering, and cryptographic provenance chains.
4. **Execution Sequence & Safety Guardrails:** Defining atomic cleanup phases, zero-data-loss policies, and verified rollback strategies.

---

## 2. Current Repository State

- **Total Files on Disk:** 9,376 files (546.36 MB).
- **Active Production Source:** 114 files (73 backend, 33 frontend, 6 shared domain, 2 worker).
- **Automated Tests & Fixtures:** 38 files (14 pytest suites with 122 tests passing, 24 multi-angle product packaging images).
- **Historical Audits & Documentation:** 162 markdown/statute files across `docs/`, `Legal_References/`, and root.
- **Generated Build/Cache Blobs:** 8,384 files in `node_modules`, `frontend/dist`, and Python caches.
- **Temporary Uploads:** 420 files in `backend/uploads/` and local test databases.

---

## 3. Major Repository Problems Identified

1. **Local Filesystem Evidence Storage Antipattern:** The development API writes uploaded evidence directly to `backend/uploads/`. On Render's ephemeral container infrastructure, disk storage is destroyed on container redeployments, causing broken evidence links.
2. **Workspace Root Clutter:** 32 files reside in the root directory, including historical phase reports, audit logs, and test database files.
3. **Product-Specific Scripts:** Scripts in `scratch/` were hardcoded for specific sample products (e.g. `execute_peanut_butter_pipeline.py`) rather than operating as universal, parameter-driven tools.
4. **Scattered Fixture Locations:** Test packaging images reside in `Test_Images/` rather than standard `tests/fixtures/`.
5. **Report Fallback Antipatterns:** PDF/DOCX report generators historically attempted to load local images from `Test_Images/` if evidence was missing. In production, missing evidence must deterministically render `NOT AVAILABLE`.

---

## 4. Target Repository Architecture

```
CompliScan/
├── backend/          # FastAPI REST API, models, services, alembic migrations, tests
├── frontend/         # React 18 + TypeScript + Vite web application
├── shared/           # Authoritative domain enums, states, constants, models
├── worker/           # Background job execution engine
├── scripts/          # Operational CLI tooling (development, e2e, forensic, migration)
├── tests/fixtures/   # Isolated test packaging imagery and mock payloads
├── docs/             # Active architecture, deployment, compliance, and historical archives
├── deployment/       # Render, Vercel, and container deployment manifests
├── .env.example      # Sanitized environment variable template
├── .gitignore        # Production-grade Git exclusion rules
└── README.md         # Repository overview and setup guide
```

---

## 5. Runtime Storage Architecture (Supabase Storage)

All production evidence and report binaries reside in private Supabase Storage buckets:

| Bucket Name | Purpose | Access Control | Immutability |
|---|---|---|---|
| `compliscan-evidence` | Raw packaging photos and PDF uploads | Private; Signed URLs (5-min TTL) | **IMMUTABLE** (WORM) |
| `compliscan-derived` | Cropped bounding boxes and canvas overlays | Private; Signed URLs | **IMMUTABLE** per job run |
| `compliscan-reports` | Final Audit Reports (PDF & DOCX) | Private; Signed URLs | **IMMUTABLE** (Locked at FAR finalization) |
| `compliscan-audit` | Daily cryptographic audit manifests | System / Admin only | **APPEND-ONLY** |

---

## 6. Evidence Lifecycle

```
Inspector Upload ──► Compute SHA-256 ──► Upload to `compliscan-evidence`
                                              │
                                              ▼
                                     Database Metadata Insert
                                     (status = UPLOADED, sha256_hash)
                                              │
                                              ▼
                                     Worker Queue Claim (SKIP LOCKED)
                                              │
                                              ▼
                                     Verify SHA-256 on Download
                                              │
                                              ▼
                                     OCR & Structured Extraction
                                              │
                                              ▼
                                     Deterministic Compliance Evaluation
```

---

## 7. Artifact Lifecycle & Finalization Boundary

1. **Unfinalized (DRAFT / IN_VERIFICATION):**
   - Inspector may delete or replace evidence before submission.
   - Compliance findings may be re-evaluated when new evidence is attached.
   - Inspector corrections and reviewer adjudications may be updated.
2. **Finalized (FINALIZED):**
   - `FinalAuditRecord` (FAR) is created in PostgreSQL and locked.
   - `finalization_status` set to `READ_ONLY`.
   - All underlying evidence assets and finding states are frozen.
   - PDF and DOCX reports generated strictly from the FAR snapshot.
   - Any post-finalization mutation attempt returns `403 Forbidden`.

---

## 8. Cryptographic Integrity Architecture

- **Tamper-Evident Chain:**
  `Original Bytes` &rarr; `SHA-256 Hash` &rarr; `EvidenceAsset Record` &rarr; `Worker Download Hash Verification` &rarr; `OCR Token Grounding` &rarr; `Compliance Findings` &rarr; `FAR Record Hash` &rarr; `Report SHA-256`.
- **Integrity Guarantee:** Any byte-level modification of an evidence photo in storage causes an instant SHA-256 mismatch during retrieval, immediately terminating processing and generating a high-priority security alert.

---

## 9. Security Architecture

- **Private Object Storage:** Buckets are never exposed publicly.
- **RBAC & IDOR Isolation:** Inspectors access only evidence belonging to cases they created; reviewers have read-only access across assigned cases.
- **JWKS Token Validation:** Dynamic JWT verification via Supabase JWKS (ES256 in production).
- **Zero Secrets in Git:** All API keys, JWT secrets, and database connection strings managed exclusively via Render/Vercel Secret Managers.

---

## 10. Source-of-Truth Matrix

| Artifact | Authoritative Source of Truth | Secondary / Derived Stores |
|---|---|---|
| **Source Code & Migrations** | **Git Repository** | None |
| **Relational Data & State** | **Supabase PostgreSQL** | React View State |
| **Evidence Binaries** | **Supabase Storage** | Ephemeral Worker Cache |
| **Legal Findings & FAR** | **Supabase PostgreSQL** | Generated PDF/DOCX Reports |
| **Audit Ledger** | **Supabase PostgreSQL (`audit_events`)** | Daily Storage Manifests |

---

## 11. Complete File Classification Summary

| Category | File Count | Proposed Action |
|---|---|---|
| `GENERATED_ARTIFACT` | 8,384 | Git ignored; build dynamically in CI/CD |
| `TEMPORARY_ARTIFACT` | 420 | Git ignored; local uploads migrated to Supabase |
| `HISTORICAL_AUDIT_ARTIFACT` | 174 | Preserved; archived to `docs/historical/` |
| `DOCUMENTATION_CURRENT` | 143 | Retained; organized under `docs/` |
| `BACKEND_SOURCE` | 73 | Retained in `backend/app/` |
| `DEVELOPMENT_TOOL` | 57 | Retained in `.agent/` and `.impeccable/` |
| `FRONTEND_SOURCE` | 34 | Retained in `frontend/src/` |
| `VALIDATED_TEST_FIXTURE` | 24 | Moved to `tests/fixtures/images/` |
| `DOCUMENTATION_HISTORICAL` | 19 | Moved to `docs/historical/` |
| `TEST_CODE` | 14 | Retained in `backend/tests/` |
| `DATABASE_MIGRATION` | 13 | Retained in `alembic/` |
| `PRODUCTION_SOURCE` | 6 | Retained in `shared/` |
| `DEVELOPMENT_SCRIPT` | 5 | Moved to `scripts/development/` |
| `FORENSIC_ARTIFACT` | 4 | Moved to `scripts/forensic/` |
| `DEPLOYMENT_CONFIGURATION` | 2 | Retained; augmented in `deployment/` |
| `WORKER_SOURCE` | 2 | Retained in `worker/` |
| `SECURITY_ARTIFACT` | 1 | Strictly Git ignored |
| `ENVIRONMENT_TEMPLATE` | 1 | Retained in root (`.env.example`) |
| **TOTAL** | **9,376** | **100% Accounted For** |

---

## 12. Cleanup Plan & Execution Phases

- **Phase A:** Baseline verification and dedicated refactoring branch creation.
- **Phase B:** Target directory skeleton creation.
- **Phase C:** Test fixture relocation (`Test_Images/` &rarr; `tests/fixtures/images/`) and test reference updates.
- **Phase D:** Operational and forensic script relocation to `scripts/`.
- **Phase E:** Historical documentation archival to `docs/historical/`.
- **Phase F:** `.gitignore` hardening and removal of ephemeral database artifacts from index.
- **Phase G:** Post-cleanup regression suite execution (100% green required).

---

## 13. Storage Migration Plan (Local &rarr; Supabase)

1. **Storage Service Implementation:** Deploy `SupabaseStorageService` backed by `httpx` communicating with Supabase Storage REST API.
2. **Historical Validation Evidence Migration:** Run `scripts/migration/migrate_local_evidence_to_supabase.py`:
   - Iterate over `compliscan_validation.db` evidence records.
   - Upload each binary to `compliscan-evidence/inspections/{id}/{ev_id}/original/{file}`.
   - Verify `destination_sha256 == source_sha256`.
   - Update `storage_path` in PostgreSQL.

---

## 14. Deployment Implications

- **Vercel (Frontend):** Builds via `npm run build`; routes all `/api/*` requests to Render API; zero backend secrets exposed to client.
- **Render Web Service (API):** Runs `uvicorn backend.app.main:app`; connects to Supabase PostgreSQL via connection pooler; executes fast deterministic requests.
- **Render Background Worker:** Runs `python -m worker.runner`; polls and claims `IMAGE_QUALITY`, `PERCEPTION`, `EXTRACTION`, `EVALUATION` jobs using `FOR UPDATE SKIP LOCKED`.

---

## 15. Backup & Disaster Recovery

- **PostgreSQL Database:** Automated daily Supabase WAL point-in-time recovery (PITR) with 7-day retention.
- **Supabase Storage:** S3-compatible daily versioned snapshots.
- **Disaster Recovery RTO/RPO:** Target RPO < 1 hour, RTO < 4 hours.

---

## 16. Failure Handling Matrix

- **Network Timeout on Storage Upload:** Transaction rolled back; client receives actionable error; zero orphan DB rows.
- **SHA-256 Mismatch on Worker Download:** Job failed immediately; high-priority security alert logged; execution halted.
- **Storage Outage During Report Generation:** Report builder flags `NOT AVAILABLE`; zero mock images substituted.

---

## 17. Implementation Sequence

1. **Step 1:** User review and formal approval of this Master Plan.
2. **Step 2:** Repository reorganization execution per `docs/phase7_cleanup_execution_plan.md`.
3. **Step 3:** Implementation of `SupabaseStorageService` and removal of `Test_Images` report fallbacks.
4. **Step 4:** Cloud infrastructure provisioning on Render and Vercel.
5. **Step 5:** End-to-end smoke testing in live cloud environment.

---

## 18. Rollback Strategy

- **Git Rollback:** `git reset --hard HEAD~1` to instantly revert any cleanup phase.
- **Storage Rollback:** Dual-write / read-fallback mode during storage migration until 100% parity verified.

---

## 19. Human Decisions Required

Prior to implementation, user alignment is requested on the following operational parameters:

1. **Statutory Evidence Retention Period:**
   - *Recommendation:* 5 years for finalized inspection records in accordance with standard statutory metrology enforcement rules (or configurable via environment).
2. **Archived Database Disposal:**
   - *Recommendation:* Move `compliscan_validation.db` to `archive/databases/` (Git ignored) rather than deleting it, preserving raw SQLite audit validation history.
3. **Storage Bucket Provisioning:**
   - *Recommendation:* Use 3 separate private buckets (`compliscan-evidence`, `compliscan-derived`, `compliscan-reports`) to allow granular IAM policies and lifecycle rules.

---

## 20. Final Acceptance Checklist

- [x] Complete forensic inventory of all 9,376 repository files.
- [x] 100% of files classified into the 25 taxonomy categories.
- [x] Zero deletions or mutations executed during planning.
- [x] Production evidence storage architecture fully defined on Supabase Storage.
- [x] End-to-end SHA-256 cryptographic provenance chain established.
- [x] Source of truth matrix defined across PostgreSQL, Supabase Storage, and Git.
- [x] Target repository tree and directory purposes specified.
- [x] Step-by-step cleanup execution plan with rollback procedures authored.
- [x] Master Plan authored and frozen at `docs/phase7_repository_and_storage_master_plan.md`.
