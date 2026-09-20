# Phase 7.1 — Artifact Source of Truth Matrix

**Document ID:** `SOT-2026-LM-001`  
**Date:** September 20, 2026  
**Status:** DRAFT (PLANNING ONLY — NO MUTATIONS EXECUTED)  

---

## 1. Executive Principle

In CompliScan LM, every artifact category has a single, unambiguous **Authoritative Source of Truth**. 

- **Git Repository:** Authoritative ONLY for application source code, database migrations, configuration templates, and static test fixtures. Git must **never** store production runtime data, uploaded evidence, or user records.
- **Supabase PostgreSQL:** Authoritative for all relational data, operational state machines, metadata, structured declarations, rule findings, user accounts, and immutable FinalAuditRecords.
- **Supabase Storage:** Authoritative for raw binary blobs (original evidence photos, derived token crops, generated PDF/DOCX reports).
- **Derived View-Models:** Ephemeral runtime projections (e.g. `ReportDataBuilder`, `BuildDeclarationsContext`, frontend React state) computed dynamically from authoritative database records.

---

## 2. Master Source of Truth Matrix

| Artifact Category | PostgreSQL | Supabase Storage | Git Repository | Ephemeral Worker / React UI | Authoritative Source of Truth | Notes & Invariants |
|---|---|---|---|---|---|---|
| **Application Source Code** | No | No | **YES** | No | **Git Repository** | Version controlled, CI/CD deployed |
| **Database Schema & Migrations** | `alembic_version` | No | **YES** (`alembic/`) | No | **Git Repository** | Applied via Alembic migrations |
| **User & RBAC Accounts** | **YES** (`users`) | No | No | JWT Claims | **PostgreSQL** | Supabase Auth synchronized |
| **Inspection Case Aggregate** | **YES** (`inspections`) | No | No | React Workspace | **PostgreSQL** | State machine authoritative |
| **Evidence Metadata & SHA-256** | **YES** (`evidence_assets`)| No | No | React Canvas | **PostgreSQL** | Contains exact 64-char SHA-256 |
| **Original Evidence Binary** | Stored Path | **YES** (`compliscan-evidence`) | **PROHIBITED** | Local scratch during OCR | **Supabase Storage** | Immutable WORM byte storage |
| **OCR Raw Tokens & Bounding Boxes**| **YES** (`ocr_results`) | No | No | Worker memory | **PostgreSQL** | Full token coordinates in JSON |
| **Structured Declarations** | **YES** (`structured_declaration_results`) | No | No | UI Matrix | **PostgreSQL** | Gemini perception extraction |
| **Applicability Evaluations** | **YES** (`applicability_results`)| No | No | UI Rules Panel | **PostgreSQL** | Statutory rule applicability |
| **Compliance Findings** | **YES** (`compliance_findings`)| No | No | UI Matrix | **PostgreSQL** | Deterministic 6-value result |
| **Inspector Corrections** | **YES** (`declaration_corrections`)| No | No | Overrides map | **PostgreSQL** | Human inspector verified |
| **Reviewer Adjudications** | **YES** (`reviewer_decisions`)| No | No | Adjudication drawer | **PostgreSQL** | Reviewer governance decision |
| **FinalAuditRecord (FAR)** | **YES** (`final_audit_records`)| Canonical JSON backup | No | View-model | **PostgreSQL** | Immutable legal determination |
| **Final Audit Report (PDF)** | Stored SHA-256 & Path | **YES** (`compliscan-reports`)| **PROHIBITED** | Generated stream | **Supabase Storage** | Derived output artifact |
| **Final Audit Report (DOCX)** | Stored SHA-256 & Path | **YES** (`compliscan-reports`)| **PROHIBITED** | Generated stream | **Supabase Storage** | Derived output artifact |
| **Audit Ledger Events** | **YES** (`audit_events`) | Daily CSV snapshot | No | UI Ledger View | **PostgreSQL** | Append-only immutable log |
| **Test Packaging Images** | No | No | **YES** (`tests/fixtures/`) | Test scratch | **Git Repository** | Static multi-product test suite |
| **Legal Metrology Regulations** | Seed rules in code | No | **YES** (`Legal_References/`) | Rule definitions | **Git Repository** | Reference PDF/MD statutes |
| **Environment Secrets** | No | No | **PROHIBITED** | Render / Vercel env | **Secret Manager** | Encrypted in deployment settings |

---

## 3. Storage Hierarchy Rules

1. **Reports Are Derived, Not Authoritative:** A generated PDF or DOCX report is never the primary record of truth. The primary truth is the `FinalAuditRecord` row in PostgreSQL. If a report binary is deleted or lost, it can be re-rendered deterministically from the FAR.
2. **Binary Integrity Precedes Analysis:** No OCR, Gemini extraction, or rule evaluation may execute unless `HASH(downloaded_bytes) == EvidenceAsset.sha256_hash`.
3. **No File System Assumptions in Backend:** Code must never assume `/tmp` or `backend/uploads/` persists across HTTP requests. All file interactions must pass through `StorageService`.
4. **Git Zero Data Contamination:** Under no circumstances may inspection-specific photos, user uploads, or client database dumps be committed to Git.
