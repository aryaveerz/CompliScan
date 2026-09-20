# CompliScan LM — Forensic Remediation & Hardening Master Implementation Plan

This plan implements comprehensive architectural remediation and hardening for CompliScan LM based on real-runtime forensic audit findings on the Juice dataset (`G:\CompliScan\Test_Images\Juice`).

## User Review Required

> [!IMPORTANT]
> **Key Architecture Decisions**:
> 1. **Centralized AI Model**: Strictly using `gemini-3.6-flash` across all backend services and configuration files.
> 2. **Product Evidence Synthesis**: Refactoring compliance evaluation to evaluate one synthesized `ProductDeclaration` per docket (7 findings) while preserving all per-image immutable evidence records.
> 3. **Database Migration**: Updating `structured_declaration_results.block_reason` to `TEXT` and adding `block_code VARCHAR(50)`.
> 4. **Departmental Report Design**: Updating PDF and DOCX reports to follow an Indian Legal Metrology departmental inspection format with clear separation of AI, deterministic rules, inspector verification, reviewer adjudication, and annexures.

---

## Proposed Changes

### 1. Configuration & AI Model Centralization
#### [MODIFY] [config.py](file:///g:/CompliScan/backend/app/core/config.py)
#### [MODIFY] [.env](file:///g:/CompliScan/.env)
- Set `GEMINI_MODEL = "gemini-3.6-flash"` as default and authoritative setting.
- Ensure all extraction callers read from `settings.GEMINI_MODEL`.

### 2. Database Schema & Migration
#### [NEW] [alembic migration](file:///g:/CompliScan/backend/alembic/versions/)
- Alter `structured_declaration_results.block_reason` to `TEXT`.
- Add `block_code` (`VARCHAR(50)`) to `structured_declaration_results`.
- Add `telemetry` (`JSONB` / `JSON`) column to `structured_declaration_results` for Gemini latency, token counts, and trace metadata.

### 3. Extraction Schema & Provenance Hardening
#### [MODIFY] [structured_declaration.py](file:///g:/CompliScan/backend/app/schemas/structured_declaration.py)
#### [MODIFY] [extraction_service.py](file:///g:/CompliScan/backend/app/services/extraction_service.py)
#### [MODIFY] [extraction_v1.py](file:///g:/CompliScan/backend/app/services/prompts/extraction_v1.py)
- Support observation statuses: `OBSERVED`, `NOT_OBSERVED`, `AMBIGUOUS`, `CONFLICTING`, `UNREADABLE`.
- Support distinct organizational roles: `manufacturer`, `packer`, `importer`, `marketer`, `brand_owner`.
- Support explicit QR status: `QR_PRESENT`, `QR_DECODED`, `QR_NOT_DECODED`, `QR_CONTENT_NOT_VERIFIED`.
- Enforce strict token-level provenance validation (verify index in OCRResult, asset match, raw text correspondence).
- Bounded HTTP retry logic (distinguish 429/5xx transient from 400/401/403 permanent).
- Set state to `PROCESSING_FAILED` with `GEMINI_MODEL_UNAVAILABLE` or `GEMINI_API_ERROR` on failure—never `POTENTIAL_NON_COMPLIANCE`.

### 4. Product Evidence Synthesis Engine
#### [NEW] [product_synthesis_service.py](file:///g:/CompliScan/backend/app/services/product_synthesis_service.py)
#### [NEW] [product_synthesis.py](file:///g:/CompliScan/backend/app/schemas/product_synthesis.py)
#### [MODIFY] [compliance_service.py](file:///g:/CompliScan/backend/app/services/compliance_service.py)
- Create `ProductEvidenceSynthesisService` to aggregate multi-image declarations into a single unified `ProductDeclaration`.
- Track corroborations across images and detect field-level conflicts (`CONFLICTING` / `REQUIRES_REVIEW`).
- Point `ComplianceEvaluationService` to evaluate the synthesized `ProductDeclaration`, producing **1 finding per applicable statutory domain** (7 findings total for the docket) with references to supporting evidence assets.

### 5. Report Generation Hardening (PDF & DOCX)
#### [MODIFY] [pdf_report_service.py](file:///g:/CompliScan/backend/app/services/pdf_report_service.py)
#### [MODIFY] [docx_report_service.py](file:///g:/CompliScan/backend/app/services/docx_report_service.py)
- Structure reports according to Indian Legal Metrology departmental inspection format:
  - Header & Docket Particulars
  - Section A: Packaged Commodity Particulars
  - Section B: Evidence Register (with SHA-256 hashes)
  - Section C: Synthesized Declarations & Verification Matrix
  - Section D: Technical System Processing Record (IQA, OCR, Gemini Telemetry)
  - Section E: Inspecting Officer Verification
  - Section F: Reviewing Officer Adjudication
  - Section G: Final Audit Record & Conclusion
  - Section H: Annexures
- Maintain 1:1 strict data parity between PDF and DOCX generated from `FinalAuditRecord`.

### 6. Automated Testing & Verification
#### [NEW] [test_remediation_suite.py](file:///g:/CompliScan/backend/tests/test_remediation_suite.py)
- Unit & integration tests for:
  - Model config & startup availability.
  - OCR bounding box and zero-token safety.
  - Provenance validation & phantom token rejection.
  - Multi-image synthesis and conflict resolution.
  - Deterministic Legal Metrology evaluation.
  - FinalAuditRecord immutability & report parity.
  - Failure injection (Gemini 400, 404, 429, timeout -> PROCESSING_FAILED).

### 7. Real Juice E2E Golden Path & Forensic Artifact Generation
- Execute all 4 Juice images through the remediated pipeline.
- Write structured forensic reports and matrices under `G:\CompliScan\docs\remediation\juice\`.

---

## Verification Plan

### Automated Tests
- Run full backend test suite:
  ```powershell
  C:\Users\singh\AppData\Local\Programs\Python\Python314\python.exe -m pytest backend/tests/ -q
  ```
- Run frontend build:
  ```powershell
  cd frontend; npm run build
  ```

### Real-World Dataset Validation
- Run end-to-end Juice audit script with `gemini-3.6-flash`.
- Verify generated PDF and DOCX reports.
- Verify SHA-256 and lineage logs.
