# Phase 7.1 — Repository Inventory and Cleanup Plan

**Document ID:** `PLAN-2026-REPO-001`  
**Date:** September 20, 2026  
**Status:** DRAFT (PLANNING ONLY — NO MUTATIONS EXECUTED)  
**Target Scope:** `G:\CompliScan\` (Root, Backend, Frontend, Docs, Scripts, Fixtures, Artifacts)

---

## 1. Executive Summary

CompliScan LM is preparing for internet-facing deployment across **Vercel** (Frontend), **Render** (FastAPI Backend + Background Worker), and **Supabase** (PostgreSQL Database, Auth, and Object Storage).

Prior to production deployment, the repository must transition from a multi-phase development/forensic workspace into a production-grade codebase. The repository currently contains:
- **9,376 total files** (546.36 MB total on disk).
- **8,384 generated build/cache artifacts** (`node_modules`, `frontend/dist`, `__pycache__`, `.pytest_cache`).
- **420 temporary runtime artifacts** (including 400+ local uploads in `backend/uploads/` and `backend/backend/uploads/` from historical test runs, plus local SQLite test databases).
- **174 historical audit artifacts** (phase reports, screenshot logs, validation runs).
- **143 current engineering documentation files** (including statutory legal references in `Legal_References/`).
- **114 core application source files** (73 backend, 33 frontend, 6 shared domain, 2 worker).
- **38 test files & validated fixtures** (14 backend pytest suites, 24 multi-angle product packaging label images).

This document establishes the inventory, taxonomy classifications, unused/duplicate file identification, and proposed target destinations for every artifact category.

---

## 2. Complete Repository Taxonomy Classification

| Category | File Count | Description & Scope | Proposed Disposition |
|---|---|---|---|
| `GENERATED_ARTIFACT` | 8,384 | `node_modules`, `.pytest_cache`, `__pycache__`, `frontend/dist` | Standard `.gitignore` enforcement; rebuild in CI/CD |
| `TEMPORARY_ARTIFACT` | 420 | `backend/uploads/` images, `*.db`, `*.log`, scratch image outputs | Exclude from Git; transition to Supabase Storage |
| `HISTORICAL_AUDIT_ARTIFACT` | 174 | `scratch/runs/`, `qa_screenshots/`, root historical reports | Archive into `docs/historical/` and `tests/fixtures/` |
| `DOCUMENTATION_CURRENT` | 143 | Architecture specifications, `Legal_References/`, system guides | Retain & organize in `docs/` hierarchy |
| `BACKEND_SOURCE` | 73 | `backend/app/` (API routers, models, services, core security) | Retain in `backend/app/` |
| `DEVELOPMENT_TOOL` | 57 | `.agent/skills/`, `.impeccable/` IDE configurations | Retain in root development tooling |
| `FRONTEND_SOURCE` | 34 | `frontend/src/`, `frontend/public/`, build configs, static assets | Retain in `frontend/` |
| `VALIDATED_TEST_FIXTURE` | 24 | `Test_Images/` (Juice, Peanut Butter, Serum, Tablet packaging) | Move to `tests/fixtures/images/` |
| `DOCUMENTATION_HISTORICAL` | 19 | Phase 0–6 audits, historical reconciliation logs | Move to `docs/historical/` |
| `TEST_CODE` | 14 | `backend/tests/` pytest test suites and `conftest.py` | Retain in `backend/tests/` |
| `DATABASE_MIGRATION` | 13 | `alembic/` migration scripts, `alembic.ini` | Retain in `alembic/` |
| `PRODUCTION_SOURCE` | 6 | `shared/domain/` (enums, states, constants, models) | Retain in `shared/` |
| `DEVELOPMENT_SCRIPT` | 5 | Utility seeds, token generators in `backend/scripts/` | Move to `scripts/development/` |
| `FORENSIC_ARTIFACT` | 4 | Forensic verification pipelines in `scratch/` | Move to `scripts/forensic/` |
| `DEPLOYMENT_CONFIGURATION` | 2 | `backend/requirements.txt`, `.gitignore` | Retain & augment with `render.yaml`, `vercel.json` |
| `WORKER_SOURCE` | 2 | `worker/` background worker entrypoints | Retain in `worker/` |
| `SECURITY_ARTIFACT` | 1 | `.env` (local secrets) | Strictly `.gitignore` protected; secrets to Secret Manager |
| `ENVIRONMENT_TEMPLATE` | 1 | `.env.example` (clean template with placeholders) | Retain in repository root |
| `UNKNOWN` | 0 | All files resolved and classified | N/A |
| **TOTAL** | **9,376** | **Entire Repository** | **100% Accounted For** |

---

## 3. Major Repository Problems Identified

1. **Local Filesystem Evidence Storage Antipattern:**
   - The development backend saves uploaded evidence to `backend/uploads/INS-{ID}/EV-{ID}_{filename}`.
   - On Render, the container filesystem is ephemeral and recreated on every deployment or instance restart. Storing evidence on local disk causes data loss and broken evidence links.
2. **Repository Root Clutter:**
   - 32 files reside directly in the root directory, including historical phase logs (`phase0_reconnaissance_report.md`, `phase1_implementation_report.md`, `phase6_production_readiness_audit.md`, `final_system_validation.md`, `COMPLISCAN_LM_MVP_CAPABILITIES_AND_JUSTIFICATION.txt`).
3. **Product-Specific Pipeline Scripts:**
   - `scratch/` contains product-specific scripts (`execute_e2e_pipeline.py`, `run_forensic_verification.py`, `inspect_juice_detail.py`) rather than unified, parameter-driven CLI tooling.
4. **Scattered Test Fixtures:**
   - Test packaging images reside in `Test_Images/` rather than a standard `tests/fixtures/` structure, and historical validation artifacts reside in `scratch/runs/`.
5. **Hardcoded Fallbacks in Report Generators:**
   - `backend/app/services/pdf_report_service.py` and `backend/app/services/docx_report_service.py` contained legacy fallbacks attempting to read from `Test_Images/` if evidence was missing from disk. In production, missing evidence must explicitly report `NOT AVAILABLE` rather than substituting test imagery.
6. **Untracked Local SQLite Databases:**
   - `compliscan.db`, `compliscan_test.db`, and `compliscan_validation.db` reside in the workspace root. Production database operations must target Supabase PostgreSQL exclusively.

---

## 4. Script Classification & Universal Tooling Plan

| Current Script Path | Purpose | Type | Target Path | Proposed Action |
|---|---|---|---|---|
| `backend/scripts/seed_supabase_users.py` | Seed initial inspector/reviewer accounts | Development | `scripts/development/seed_users.py` | MOVE |
| `scratch/run_forensic_verification.py` | Full forensic validation of LM rules | Forensic | `scripts/forensic/run_rule_verification.py` | REFACTOR to universal CLI |
| `scratch/execute_e2e_pipeline.py` | End-to-end multi-product inspection run | E2E Test | `scripts/e2e/run_inspection_pipeline.py` | REFACTOR to take `--image` param |
| `scratch/check_juice_db.py` | Inspect SQLite validation tables | Scratch | `scratch/` | ARCHIVE |
| `scratch/inspect_juice_detail.py` | Inspect finding payloads | Scratch | `scratch/` | ARCHIVE |
| `scratch/auth_runner.py` | Test Supabase authentication | Development | `scripts/development/test_auth.py` | MOVE |

---

## 5. Test Fixture Reorganization

Current structure:
- `Test_Images/Juice/` (4 images)
- `Test_Images/Peanut_Butter/` (4 images)
- `Test_Images/Serum/` (4 images)
- `Test_Images/Tablet/` (4 images)
- `Test_Images/Aadhaar/` (4 images)
- `Test_Images/Synthetic_Negative/` (4 images)

Target structure:
- `tests/fixtures/images/packaged_products/` (Juice, Peanut Butter, Serum, Tablet)
- `tests/fixtures/images/non_packaging/` (Aadhaar, Document, Generic)
- `tests/fixtures/images/synthetic_negatives/` (Blur, Low-res, Corrupt)
- `tests/fixtures/json/` (Sample Gemini responses, OCR token maps)

---

## 6. Deletion Candidates vs. Archival Candidates

### 6.1 Safe Deletion Candidates (Post-Approval Only)
- **None during Phase 7.1.** All historical outputs and scripts are preserved in archive directories to maintain forensic traceability.

### 6.2 Archival Candidates (Move to `docs/historical/` or `archive/`)
- Root phase reports:
  - `phase0_activity_and_reconciliation_log.md` &rarr; `docs/historical/phase0/`
  - `phase0_reconciliation_report.md` &rarr; `docs/historical/phase0/`
  - `phase0_reconnaissance_report.md` &rarr; `docs/historical/phase0/`
  - `phase1_implementation_report.md` &rarr; `docs/historical/phase1/`
  - `phase1_review_report.md` &rarr; `docs/historical/phase1/`
  - `phase2_2_implementation_report.md` &rarr; `docs/historical/phase2/`
  - `phase3_implementation_report.md` &rarr; `docs/historical/phase3/`
  - `phase4_implementation_report.md` &rarr; `docs/historical/phase4/`
  - `phase5_discovery_report.md` &rarr; `docs/historical/phase5/`
  - `phase5_implementation_report.md` &rarr; `docs/historical/phase5/`
  - `phase6_production_readiness_audit.md` &rarr; `docs/historical/phase6/`
  - `camera_capture_implementation_report.md` &rarr; `docs/historical/features/`
  - `multi_user_concurrency_audit_report.md` &rarr; `docs/historical/audits/`
  - `DUMMY_DATA_AUDIT.md` &rarr; `docs/historical/audits/`
  - `PRODUCTION_FORENSIC_REMEDIATION_REPORT.md` &rarr; `docs/historical/audits/`
- Historical validation test databases (`compliscan_validation.db` &rarr; `archive/databases/`).

---

## 7. Rollback & Safety Principles

1. **Zero Deletions Without Git Commit:** Any move or archive operation will occur on a clean Git branch with verified working tree status.
2. **Automated Test Checkpoints:** `pytest backend/tests` and `npm run build` must be executed and pass before and after any directory restructuring.
3. **Reference Verification:** Static regex sweeps must verify that all import paths, test asset paths, and documentation links remain valid post-move.
