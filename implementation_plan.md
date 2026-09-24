# Implementation Plan — Phase 7.4: Production Deployment + Complete Production Readiness Audit

This plan outlines the systematic execution of **Phase 7.4** for CompliScan LM. Phase 7.4 has two objectives:
1. Validate cloud deployment readiness against target architecture (Vercel Frontend $\rightarrow$ Render FastAPI API $\rightarrow$ Supabase PostgreSQL/Auth/Storage $\rightarrow$ Render Background Worker $\rightarrow$ Gemini API).
2. Perform a exhaustive forensic and production-readiness audit across 22 required audit dimensions, providing empirical evidence and generating mandatory compliance artifacts before declaring final status.

---

## User Review Required

> [!IMPORTANT]
> **Strict Non-Evasion Rule**: Production readiness status will NOT be declared early. Any failure discovered during the 22 audit phases will be explicitly logged with severity (`BLOCKER`, `HIGH`, `MEDIUM`, `LOW`, `DOCUMENTATION ONLY`). The final status will be strictly chosen from:
> - `PRODUCTION READY`
> - `PRODUCTION READY WITH DOCUMENTED NON-BLOCKING CONDITIONS`
> - `NOT PRODUCTION READY`

> [!WARNING]
> **Cloud Environment & Secret Safety**: Verification of environment secrets will ensure zero private credentials (`GEMINI_API_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `DATABASE_URL`, JWT secrets) are leaked in git, frontend bundles, logs, or API responses.

---

## Proposed Audit & Execution Workflow

### Component 1: Baseline Checkpoint & Environment Audit
- Verify Git repository cleanliness on dedicated release branch `release/phase7.4-production-readiness` (commit `5691557`).
- Run backend unit/integration tests (142/142 PASS baseline).
- Run frontend TypeScript typecheck (`tsc --noEmit`) and Vite build (`npm run build` / `pnpm run build`).
- Audit environment variables across frontend (`VITE_API_BASE_URL` public only) vs backend/worker secrets.

### Component 2: Supabase, Storage, & Infrastructure Audit
- Audit Supabase PostgreSQL schema, migrations, foreign keys, indexes, and Auth configuration.
- Audit Supabase Storage buckets (`compliscan-evidence`, `compliscan-derived`, `compliscan-reports`, `compliscan-audit`) for private RLS policies and signed URL authorization.
- Audit Render FastAPI API and Render Background Worker deployment parameters (`FOR UPDATE SKIP LOCKED`, lease recovery, zero persistent disk reliance).

### Component 3: Forensic Security & Integrity Audits
- **Evidence Integrity / Anti-Tampering**: Execute controlled payload modification test to prove worker aborts, marks `FAILED`, logs `INTEGRITY_MISMATCH_ERROR`, and emits `AuditEvent` on SHA-256 mismatch.
- **Authorization & IDOR**: Verify cross-user and cross-tenant access controls for inspectors and reviewers.
- **Finalization Immutability**: Verify post-finalization mutation attempts on evidence, findings, review rationales, and FAR artifacts are rejected.
- **Data Isolation**: Verify Inspection A vs Inspection B state scoping and clean workspace rebuilding.
- **Gemini AI Execution**: Audit model configuration, telemetry logging, error handling, and zero fixture fallback.

### Component 4: Static & Forensic Search for Contamination
- Perform deep codebase scan for `Test_Images`, hardcoded product names (`Peanut_Butter`, `Sunflower`, `Apex Consumer Goods`), hardcoded MRP/dates, `localhost`/`127.0.0.1`, SQLite dependencies, and `backend/uploads`.

### Component 5: Final Production Readiness Documentation
- Create `docs/phase7_production_readiness_final_audit.md` containing the 32-category audit matrix, exact commit hashes, security findings, storage findings, and final production status.
- Create `docs/phase7_production_readiness_evidence_manifest.md` containing concrete logs, test execution outputs, SHA-256 hashes, and verification artifacts.

---

## Verification Plan

### Automated Verification
```powershell
# 1. Backend regression suite
& "C:\Users\singh\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m pytest backend/tests -v

# 2. Frontend typecheck and production build
pnpm exec tsc --noEmit
pnpm run build
```

### Forensic Code Scans
- Ripgrep scan for forbidden production string patterns (`Test_Images`, `Peanut_Butter`, `localhost`, `SQLite`).
- Inspection of `dist/` frontend bundle for secret leaks.
