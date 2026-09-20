# COMPLISCAN LM — PHASE 7.0 REPOSITORY CLEANUP & ORGANIZATION PLAN
## Controlled Repository Lifecycle, Retention, and Organization Blueprint

**Audit Date:** 2026-09-20  
**Principle:** PLAN ONLY — ZERO DELETIONS OR MOVES PERFORMED IN THIS PHASE.

---

## 1. Candidate Classification Framework

| Category | Definition | Action Rule |
|---|---|---|
| **`KEEP`** | Active production code, active tests, migrations, schemas, deployment manifests, UI components, test fixtures. | Retain in active tree. |
| **`ARCHIVE`** | Historical milestone logs, interim reconnaissance notes, previous validation dumps. | Retain in `docs/archive/` or dedicated audit folders; never delete. |
| **`EXCLUDE`** | Ephemeral databases (`compliscan.db`), local uploads (`backend/uploads/`), cache folders (`.pytest_cache/`). | Ensure strictly listed in `.gitignore`. |
| **`MOVE`** | Universal dataset-agnostic CLI utilities (`scratch/execute_e2e_pipeline.py`, `scratch/run_forensic_verification.py`). | Propose move to `scripts/` in Phase 7.2. |

---

## 2. Itemized Action Plan for Future Implementation (Phase 7.2)

| File / Directory Path | Current Classification | Proposed Action in Phase 7.2 | Rationale & Safety Invariant |
|---|---|---|---|
| `Test_Images/` | `VALIDATED_TEST_FIXTURE` | **KEEP** in root | Standardized test fixture imagery for automated regression testing. **Never production evidence.** |
| `scratch/runs/*/` | `HISTORICAL_AUDIT_RECORD` | **KEEP** in `scratch/runs/` | Authoritative historical audit records and sealed FAR JSON snapshots. Must never be deleted. |
| `Emblem_of_India.svg.webp` | `SOURCE_CODE` / `ASSET` | **KEEP** in root | Active visual asset used on formal PDF statutory inspection reports. |
| `phase0_*.md` to `phase5_*.md` | `HISTORICAL_ARTIFACT` | **ARCHIVE** ──► `docs/archive/` | Historical milestone completion logs; preserves audit trail while decluttering root. |
| `PRODUCTION_*.md`, `REPORT_*.md` | `HISTORICAL_ARTIFACT` | **ARCHIVE** ──► `docs/archive/` | Historical implementation plans and audit notes. |
| `scratch/run_forensic_verification.py`| `TOOL` | **MOVE** ──► `scripts/` | Universal forensic verification CLI utility. |
| `scratch/execute_e2e_pipeline.py` | `TOOL` | **MOVE** ──► `scripts/` | Dataset-agnostic universal E2E pipeline runner. |
| `scratch/execute_validation_pipeline.py` | `TOOL` | **MOVE** ──► `scripts/` | Declaration validation runner tool. |
| `scratch/run_negative_tests.py` | `TOOL` | **MOVE** ──► `scripts/` | Standalone declaration validation test runner. |
