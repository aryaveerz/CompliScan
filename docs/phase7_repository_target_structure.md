# Phase 7.1 — Repository Target Structure Specification

**Document ID:** `SPEC-2026-TREE-001`  
**Date:** September 20, 2026  
**Status:** DRAFT (PLANNING ONLY — NO MUTATIONS EXECUTED)  

---

## 1. Target Directory Architecture

```
CompliScan/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── compliance.py
│   │   │   │   ├── evidence.py
│   │   │   │   ├── inspections.py
│   │   │   │   ├── reports.py
│   │   │   │   ├── reviewer.py
│   │   │   │   └── verification.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── errors.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   ├── models/
│   │   │   ├── analysis_job.py
│   │   │   ├── audit.py
│   │   │   ├── compliance.py
│   │   │   ├── evidence.py
│   │   │   ├── final_audit.py
│   │   │   ├── image_quality.py
│   │   │   ├── inspection.py
│   │   │   ├── ocr.py
│   │   │   ├── product_declaration.py
│   │   │   ├── reviewer.py
│   │   │   ├── structured_declaration.py
│   │   │   ├── user.py
│   │   │   └── verification.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── compliance.py
│   │   │   ├── evidence.py
│   │   │   ├── final_audit.py
│   │   │   ├── image_quality.py
│   │   │   ├── inspection.py
│   │   │   ├── ocr.py
│   │   │   ├── report.py
│   │   │   ├── reviewer.py
│   │   │   └── verification.py
│   │   ├── services/
│   │   │   ├── analysis_job_service.py
│   │   │   ├── applicability_service.py
│   │   │   ├── audit_service.py
│   │   │   ├── compliance_service.py
│   │   │   ├── date_intelligence_service.py
│   │   │   ├── declaration_validation_service.py
│   │   │   ├── docx_report_service.py
│   │   │   ├── evidence_service.py
│   │   │   ├── image_quality_service.py
│   │   │   ├── inspection_service.py
│   │   │   ├── ocr_service.py
│   │   │   ├── pdf_report_service.py
│   │   │   ├── product_synthesis_service.py
│   │   │   ├── report_data_builder.py
│   │   │   ├── reviewer_service.py
│   │   │   ├── storage_service.py          # Unified StorageService abstraction
│   │   │   └── structured_extraction_service.py
│   │   └── main.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_compliance.py
│   │   ├── test_declaration_validation.py
│   │   ├── test_extraction.py
│   │   ├── test_image_quality.py
│   │   ├── test_ocr.py
│   │   ├── test_phase1.py
│   │   ├── test_phase4.py
│   │   ├── test_phase5.py
│   │   ├── test_phase6_verification.py
│   │   ├── test_production_report_suite.py
│   │   ├── test_remediation_suite.py
│   │   └── test_supabase_auth.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   │   ├── CreateInspectionPage.tsx
│   │   │   ├── InspectionListPage.tsx
│   │   │   ├── InspectionWorkspacePage.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   └── ReviewerAdjudicationPage.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── auth.ts
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   │   └── assets/
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── shared/
│   └── domain/
│       ├── constants.py
│       ├── enums.py
│       ├── models.py
│       └── states.py
│
├── worker/
│   ├── runner.py
│   └── tasks.py
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── scripts/
│   ├── development/
│   │   ├── seed_users.py
│   │   └── generate_test_tokens.py
│   ├── e2e/
│   │   └── run_inspection_pipeline.py
│   ├── forensic/
│   │   └── run_rule_verification.py
│   └── migration/
│       └── migrate_local_evidence_to_supabase.py
│
├── tests/
│   └── fixtures/
│       ├── images/
│       │   ├── packaged_products/
│       │   │   ├── juice/
│       │   │   ├── peanut_butter/
│       │   │   ├── serum/
│       │   │   └── tablet/
│       │   └── synthetic_negatives/
│       └── json/
│           └── gemini_mock_responses.json
│
├── docs/
│   ├── architecture/
│   │   ├── phase7_production_evidence_storage_architecture.md
│   │   ├── phase7_artifact_source_of_truth_matrix.md
│   │   └── phase7_master_production_architecture_audit.md
│   ├── deployment/
│   │   ├── phase7_deployment_architecture.md
│   │   └── render_and_vercel_setup_guide.md
│   ├── compliance/
│   │   └── legal_metrology_packaged_commodities_rules_2011.md
│   ├── historical/
│   │   ├── phase0/
│   │   ├── phase1/
│   │   ├── phase2/
│   │   ├── phase3/
│   │   ├── phase4/
│   │   ├── phase5/
│   │   └── phase6/
│   └── Legal_References/
│
├── deployment/
│   ├── render.yaml
│   ├── vercel.json
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── .gitignore
├── .env.example
├── alembic.ini
├── LICENSE
└── README.md
```

---

## 2. Directory Purpose Definitions

- **`backend/`**: FastAPI REST API backend, SQLAlchemy models, compliance rule engines, services, and pytest automated test suites.
- **`frontend/`**: React 18 / TypeScript / Vite user interface for inspectors and reviewers.
- **`shared/`**: Single source of truth for cross-cutting domain definitions (enums, state machines, error codes).
- **`worker/`**: Asynchronous background worker executing durable analysis jobs claimed via `FOR UPDATE SKIP LOCKED`.
- **`alembic/`**: Authoritative database schema migration definitions.
- **`scripts/`**: Operational, development, e2e validation, and data migration CLI tools (categorized by function).
- **`tests/fixtures/`**: Static test packaging label imagery and mock JSON payloads for automated testing (isolated from runtime code).
- **`docs/`**: Active architectural specifications, deployment guides, compliance references, and chronological historical audit archives.
- **`deployment/`**: Cloud infrastructure manifests (Render blueprints, Vercel SPA routing, container definitions).

---

## 3. Migration Mapping: Current &rarr; Target

| Current Path | Target Path | Action | Rationale |
|---|---|---|---|
| `Test_Images/` | `tests/fixtures/images/packaged_products/` | MOVE | Standardizes test assets under `tests/` directory |
| `Legal_References/` | `docs/Legal_References/` | MOVE | Integrates legal reference material into documentation tree |
| `Documentation/` | `docs/historical/legacy_documentation/` | ARCHIVE | Preserves legacy system specifications |
| `backend/scripts/seed_supabase_users.py` | `scripts/development/seed_users.py` | MOVE | Standardizes operational scripts under `scripts/` |
| `scratch/execute_e2e_pipeline.py` | `scripts/e2e/run_inspection_pipeline.py` | MOVE | Promotes root e2e runner to standard test script |
| `scratch/run_forensic_verification.py` | `scripts/forensic/run_rule_verification.py` | MOVE | Promotes forensic audit script to `scripts/forensic/` |
| Root `phase0_*.md` to `phase6_*.md` | `docs/historical/phase{0..6}/` | ARCHIVE | Cleans workspace root while maintaining full audit trail |
| Root `Emblem_of_India.svg.webp` | `frontend/public/assets/emblem_of_india.webp` | MOVE | Relocates UI asset to frontend public directory |
| Root `compliscan.db`, `compliscan_validation.db` | `.gitignore` (Local test only) | REMOVE FROM GIT | Prevents local SQLite files from entering version control |
