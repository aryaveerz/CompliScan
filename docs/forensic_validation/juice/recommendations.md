# COMPLISCAN LM — FORENSIC RECOMMENDATIONS & REMEDIATION PLAN
**Target Dataset**: Packaged Commodity — B Natural Guava Juice 1L (`G:\CompliScan\Test_Images\Juice`)  
**Audit Scope**: Production Readiness, Schema Hardening, and LLM Resilience  

---

## 1. HIGH-PRIORITY CODE REMEDIATIONS

### R-01: Update Production Model Configuration to Gemini 3.6 Flash
- **Current Issue**: `.env` and `backend/app/core/config.py` default to `GEMINI_MODEL=gemini-2.5-flash`. Google AI Studio API returns `HTTP 404 NOT_FOUND` for 2.5 flash requests, rendering default extraction dead-on-arrival.
- **Remediation**:
  - Update `.env`: `GEMINI_MODEL=gemini-3.6-flash`.
  - Update `backend/app/core/config.py` default value to `gemini-3.6-flash`.

### R-02: Fix Schema Serialization for Google AI Studio API
- **Current Issue**: Pydantic's `model_json_schema()` includes `"additionalProperties": false`. The Google AI Studio REST API rejects `additionalProperties` for standard developer keys with HTTP 400.
- **Remediation**:
  - Strip `"additionalProperties"` from the JSON schema before passing to `response_schema` or format as prompt text instructions.

### R-03: Database Column Expansion for `block_reason`
- **Current Issue**: `structured_declaration_results.block_reason` is constrained to `VARCHAR(100)`. Any exception string longer than 100 characters throws a PostgreSQL `StringDataRightTruncationError` during rollback, failing the DB session.
- **Remediation**:
  - Migration script to alter `block_reason` column type to `TEXT`.
  - Truncate exception strings to max 80 characters before calling `persist_blocked_result()`.

### R-04: Multi-Image Evidence Synthesis
- **Current Issue**: Currently, each image asset creates independent extraction results, resulting in 28 findings (4 assets × 7 domains).
- **Remediation**:
  - Implement a docket-level evidence aggregation layer that synthesizes declarations across all uploaded images for a product docket into a unified master declaration set before applicability rules run.

---

## 2. PRODUCTION HARDENING ROADMAP

| Phase | Milestone | Priority | Estimated Effort |
|-------|-----------|----------|------------------|
| **Phase 1** | Model Config & Schema Hardening | Critical | 1 Day |
| **Phase 2** | Database Column Expansion & Exception Truncation | High | 0.5 Days |
| **Phase 3** | Multi-Image Evidence Synthesis Engine | Medium | 2 Days |
| **Phase 4** | Gemini Rate-Limit & Backoff Resilience Queue | Medium | 1.5 Days |
