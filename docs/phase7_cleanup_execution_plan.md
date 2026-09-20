# Phase 7.1 — Repository Cleanup Execution Plan

**Document ID:** `EXEC-2026-CLEAN-001`  
**Date:** September 20, 2026  
**Status:** DRAFT (PLANNING ONLY — NO MUTATIONS EXECUTED)  

---

## 1. Execution Principles & Pre-Conditions

Cleanup execution will proceed only after formal user review and approval of the master planning documents.

### Invariant Rules During Execution:
1. **Zero Data Loss:** No historical FAR, audit finding, test fixture, or documentation file will be deleted. Unused development artifacts are archived rather than purged.
2. **Atomic Git Checkpoints:** Every migration phase is isolated to a discrete, revertible Git commit.
3. **Continuous Automated Validation:** Backend test suite (`pytest`) and frontend production build (`tsc && vite build`) must pass at 100% green before and after every move phase.
4. **Reference Path Integrity:** Any moved file (e.g. `Test_Images/` to `tests/fixtures/`) must have all import/file path references updated and statically verified before concluding the step.

---

## 2. Step-by-Step Cleanup Sequence

### Phase A: Pre-Cleanup Baseline & Checkpoint
1. Run `git status` and record clean state on dedicated branch `refactor/phase7-repo-cleanup`.
2. Execute full baseline verification:
   - Backend: `pytest backend/tests` (Confirm 122/122 passed).
   - Frontend: `npm run build` (Confirm 0 errors).
3. Create local backup snapshot of full workspace metadata in `scratch/pre_cleanup_manifest.json`.

### Phase B: Create Target Directory Skeleton
Create the target directory tree without moving or deleting existing files:
- `scripts/development/`
- `scripts/e2e/`
- `scripts/forensic/`
- `scripts/migration/`
- `tests/fixtures/images/packaged_products/`
- `tests/fixtures/images/synthetic_negatives/`
- `tests/fixtures/json/`
- `docs/architecture/`
- `docs/deployment/`
- `docs/compliance/`
- `docs/historical/` (subfolders `phase0` through `phase6`)
- `deployment/`

### Phase C: Relocate Test Fixtures & Update Test References
1. Move `Test_Images/` contents to `tests/fixtures/images/packaged_products/`.
2. Update path constants in backend test fixtures:
   - `backend/tests/conftest.py`
   - `backend/tests/test_extraction.py`
   - `backend/tests/test_image_quality.py`
   - `backend/tests/test_ocr.py`
   - `backend/tests/test_compliance.py`
3. Execute `pytest backend/tests` to verify 100% pass rate.
4. Commit: `refactor(tests): relocate test fixtures to tests/fixtures/`.

### Phase D: Relocate Operational & Forensic Scripts
1. Move `backend/scripts/seed_supabase_users.py` &rarr; `scripts/development/seed_users.py`.
2. Move `scratch/execute_e2e_pipeline.py` &rarr; `scripts/e2e/run_inspection_pipeline.py`.
3. Move `scratch/run_forensic_verification.py` &rarr; `scripts/forensic/run_rule_verification.py`.
4. Update import statements (`from backend.app...`, `from shared.domain...`) in relocated scripts.
5. Execute smoke tests on relocated scripts.
6. Commit: `refactor(scripts): organize scripts into dedicated domains`.

### Phase E: Archive Historical Documentation & Clean Root
1. Move root-level historical logs (`phase0_*.md` through `phase6_*.md`, `DUMMY_DATA_AUDIT.md`, `multi_user_concurrency_audit_report.md`, `camera_capture_implementation_report.md`) to corresponding `docs/historical/` subfolders.
2. Relocate `Documentation/` to `docs/historical/legacy_documentation/`.
3. Relocate `Emblem_of_India.svg.webp` to `frontend/public/assets/emblem_of_india.webp`.
4. Verify all internal markdown links.
5. Commit: `docs(archive): reorganize historical documentation into docs/historical/`.

### Phase F: Update `.gitignore` & Clean Ephemeral Database Artifacts
1. Update `.gitignore` to explicitly ignore:
   - `compliscan.db`, `compliscan_test.db`, `compliscan_validation.db`
   - `backend/uploads/`
   - `scratch/runs/`
   - `*.db-journal`, `*.log`, `*.tmp`
2. Remove tracked ephemeral artifacts from Git index (using `git rm --cached`).
3. Commit: `chore(git): harden .gitignore for production deployment`.

### Phase G: Final Post-Cleanup Regression Verification
1. Run TypeScript typecheck: `npx tsc --noEmit` &rarr; Verify 0 errors.
2. Run frontend production build: `npm run build` &rarr; Verify 0 errors.
3. Run backend test suite: `pytest backend/tests` &rarr; Verify 122/122 passed.
4. Run full repository link & reference audit script to confirm zero broken relative paths.

---

## 3. Rollback Procedure

If any step in the cleanup sequence causes unresolvable regressions:
1. **Immediate Git Hard Reset:**
   ```bash
   git reset --hard HEAD~1
   git clean -fd
   ```
2. **Verify Restored State:**
   - Execute `pytest backend/tests` to confirm full restoration of baseline functionality.
3. **Post-Incident Analysis:**
   - Log exact failure reason in `scratch/cleanup_incident_log.md` before re-attempting.
