# CompliScan LM — Production Dummy Data & Forensic Scan Audit
## Forensic Classification of Data Assets Across Repository

**Audit Standard:** Strict Zero-Dummy Production Policy  
**Date:** 2026-09-20  
**Status:** Audit Complete & Production Hardened  

---

## 1. Classification Categories

1. **REAL AUTHORITATIVE DATA:** Persisted database models, runtime OCR tokens, real image hashes, and real packaging evidence.
2. **TEST FIXTURE:** Controlled test inputs in `backend/tests/` used strictly for automated pytest validation. Isolated from production runtime.
3. **DEMO / DUMMY DATA:** Hardcoded arrays or synthetic company/inspection entries. **MUST BE ZERO in production paths.**
4. **FALLBACK:** Fallback branches in services when upstream APIs fail. Must be token-grounded and provenance-validated, never synthetic mock text.
5. **STATIC UI CONTENT:** Labels, table column headers, and legal statutory rule definitions (LMPC 2011 Rule 6(1)).
6. **DOCUMENTATION EXAMPLE:** Architecture specs, markdown docs, and walkthrough notes.
7. **UNKNOWN — REQUIRES VERIFICATION:** Any ambiguous strings requiring verification against domain records.

---

## 2. Comprehensive Repository Inventory

| # | File Path | Line / Location | Discovered Data / Pattern | Classification | Used By | Production Visible? | Action Taken |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `backend/tests/conftest.py` | Lines 50–90 | `test@example.com`, `compliscan_test_secret_key` | **TEST FIXTURE** | Pytest Suite | **NO** (Isolated to tests) | Retained strictly for automated testing |
| 2 | `backend/tests/test_compliance.py` | Lines 20–80 | Synthetic declarations (Net Qty 500g, MRP 250) | **TEST FIXTURE** | Pytest Suite | **NO** | Retained strictly for automated testing |
| 3 | `backend/tests/test_production_report_suite.py` | Lines 30–75 | `FAR-TEST-2026-A100`, `INS-TEST-2026-001` | **TEST FIXTURE** | Pytest Suite | **NO** | Retained strictly for automated testing |
| 4 | `backend/app/services/report_data_builder.py` | Section 1 | `inspecting_officer.full_name`, `officer_id` | **REAL AUTHORITATIVE DATA** | Report Generators | **YES** | Resolves from persisted `User` model; if absent renders `NOT RECORDED` |
| 5 | `backend/app/services/report_data_builder.py` | Section 1 | `location.premises_name`, `address` | **REAL AUTHORITATIVE DATA** | Report Generators | **YES** | Resolves from persisted `InspectionCase.location_data`; if absent renders `Location: NOT RECORDED` |
| 6 | `backend/app/services/report_data_builder.py` | Section 2 | `product_name`, `brand`, `manufacturer` | **REAL AUTHORITATIVE DATA** | Report Generators | **YES** | Resolves from `ProductDeclaration` synthesized from real evidence |
| 7 | `backend/app/services/report_data_builder.py` | Section 11 | `disclaimer`, `evidence_hashes` | **REAL AUTHORITATIVE DATA** | Report Generators | **YES** | Populated strictly from `evidence_assets.sha256_hash` |
| 8 | `backend/app/services/pdf_report_service.py` | Header & Cover | `Emblem of India`, `COMPLISCAN LM` | **REAL AUTHORITATIVE DATA** | PDF Dossier Generator | **YES** | Uses official Emblem asset (`G:\CompliScan\Emblem_of_India.svg.webp`) without fake government claims |
| 9 | `backend/app/services/barcode_service.py` | Detection Engine | OpenCV `BarcodeDetector` on real image bytes | **REAL AUTHORITATIVE DATA** | Inspection Perception | **YES** | Decodes authentic EAN-13 `8901725100117` from `IMG_20260920_040854.jpg` |
| 10 | `frontend/src/` | Dashboard / Lists | Empty states when DB returns 0 inspections | **REAL AUTHORITATIVE DATA** | Enforcement UI | **YES** | Displays "NO INSPECTIONS RECORDED" instead of static dummy counters |
| 11 | `docs/archive/` | Historical Specs | Legacy mentions of "Apex Consumer Goods" | **DOCUMENTATION EXAMPLE** | Historical Reference | **NO** | Archived; zero footprint in active codebase |
| 12 | `Test_Images/Juice/` | 4 JPEG Assets | Real packaging imagery (`IMG_20260920_040854` to `040922`) | **REAL AUTHORITATIVE DATA** | E2E Pipeline | **YES** | Authoritative ground truth for B Natural Guava (ITC Limited) |

---

## 3. Production Hardening Confirmation

1. **Zero Dummy Inspections:** Production endpoints query the live database exclusively and return empty arrays when no records exist.
2. **Zero Fallback Officers:** If an officer was not assigned or logged, the identity block outputs `NOT RECORDED`.
3. **Zero Fallback Locations:** If GPS or registered premises were not logged, the report outputs `Location: NOT RECORDED`.
4. **Zero Fallback Tokens:** If OCR detects 0 tokens on a panel, Annexure B explicitly records `"No OCR tokens were persisted for this evidence asset."`
5. **Separation of Concerns:** Test fixtures are confined to `backend/tests/` and are never loaded by production APIs or report builders.
