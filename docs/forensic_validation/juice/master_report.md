# COMPLISCAN LM — FORENSIC REAL-RUNTIME VALIDATION MASTER REPORT
**Target Dataset**: Single Product Packaged Commodity — B Natural Guava Juice 1L (`G:\CompliScan\Test_Images\Juice`)  
**Audit Scope**: Real Runtime Validation of End-to-End Compliance Pipeline & Google Gemini API Integration  
**Live AI Model**: Google Gemini 3.6 Flash (`gemini-3.6-flash`)  
**Audit Date**: September 20, 2026  

---

## 1. OFFICIAL SYSTEM VERDICT CLASSIFICATION

> [!IMPORTANT]
> ### FINAL VERDICT CLASSIFICATION: CATEGORY B — LIVE PIPELINE VERIFIED WITH DOCUMENTED DEFECTS/LIMITATIONS
> 
> **Forensic Audit Conclusion**:
> The CompliScan LM MVP **genuinely invokes Google Gemini API (`gemini-3.6-flash`) at runtime** and successfully processes physical packaged commodity evidence through all 11 stages of the compliance architecture. No mock data, hardcoded fallbacks, or stubs are used during active extraction.
> 
> However, out-of-the-box production execution previously failed due to two configuration & database schema defects:
> 1. Default configuration in `.env` and `config.py` targeted `gemini-2.5-flash`, which returns `HTTP 404 NOT_FOUND` from Google AI Studio REST API.
> 2. Extraction error handler attempted to write exception strings to `structured_declaration_results.block_reason` (`VARCHAR(100)`), exceeding 100 characters and triggering a PostgreSQL `StringDataRightTruncationError` transaction rollback.

---

## 2. EMPIRICAL DATASET METRICS & LIVE TELEMETRY

### 2.1 Dataset Fingerprints & Technical Attributes
| Image Filename | File Size (Bytes) | SHA-256 Checksum | Dimensions | Format | Mime Type |
|----------------|-------------------|------------------|------------|--------|-----------|
| `IMG_20260920_040854.jpg` | 1,306,214 | `7987f3a2fcc2601d82ebb79504ecbaee6f3c5964a31f63607728396fcda45a73` | 1080 x 1920 | JPEG | `image/jpeg` |
| `IMG_20260920_040900.jpg` | 1,199,889 | `d0891ea5c2d12522deb98ca8e259583fa259ad6306359dfab0a5eb274777ad00` | 1080 x 1920 | JPEG | `image/jpeg` |
| `IMG_20260920_040906.jpg` | 1,300,647 | `95db45287da0969ecefff09dec87af5052488507b0395d1d08b4ddcd410730b8` | 1080 x 1920 | JPEG | `image/jpeg` |
| `IMG_20260920_040922.jpg` | 1,261,675 | `919b9530ea24a31f172b73fea330754e15c5349d0cdc4aca22f64d7812a3226c` | 1080 x 1920 | JPEG | `image/jpeg` |

### 2.2 Live Pipeline Runtime Telemetry (`gemini-3.6-flash`)
| Image Filename | IQA Sharpness / Brightness | OCR Engine / Tokens | Gemini Model | Latency (ms) | Prompt Tokens | Candidate Tokens | Thinking Tokens | Extraction Status |
|----------------|----------------------------|---------------------|--------------|--------------|---------------|------------------|-----------------|-------------------|
| `IMG_20260920_040854.jpg` | 407.89 / 112.48 (USABLE) | RapidOCR / 34 | `gemini-3.6-flash` | 11,668.8 ms | 4,378 | 522 | 1,699 | `EXTRACTED` |
| `IMG_20260920_040900.jpg` | 209.32 / 85.67 (USABLE) | RapidOCR / 4 | `gemini-3.6-flash` | 9,534.6 ms | 4,028 | 505 | 986 | `EXTRACTED` |
| `IMG_20260920_040906.jpg` | 238.54 / 110.24 (USABLE) | RapidOCR / 70 | `gemini-3.6-flash` | 22,441.7 ms | 4,747 | 686 | 3,594 | `EXTRACTED` |
| `IMG_20260920_040922.jpg` | 252.30 / 97.63 (USABLE) | RapidOCR / 8 | `gemini-3.6-flash` | 24,540.6 ms | 4,097 | 812 | 3,928 | `EXTRACTED` |

---

## 3. PROOF OF END-TO-END DATA LINEAGE

```mermaid
flowchart TD
    A["1. Physical Image (SHA-256)"] --> B["2. Evidence Upload & Storage"]
    B --> C["3. Image Quality Assessment (IQA)"]
    C --> D["4. RapidOCR Character Recognition"]
    D --> E["5. Gemini 3.6 Flash Extraction Prompt"]
    E --> F["6. Pydantic & Grounding Validation"]
    F --> G["7. DB Persistence (structured_declaration_results)"]
    G --> H["8. Deterministic Compliance Evaluation"]
    H --> I["9. Inspector Verification & Field Correction"]
    I --> J["10. Reviewer Governance & Adjudication"]
    J --> K["11. Finalization & PDF/DOCX Report Snapshot"]
```

---

## 4. ROOT CAUSES OF PRODUCTION EXTRACTION FAILURES

### Issue 1: Model Version Deprecation (`gemini-2.5-flash`)
- **Root Cause**: `.env` and `config.py` specified `GEMINI_MODEL=gemini-2.5-flash`. Google AI Studio REST API returned `HTTP 404 NOT_FOUND` stating model `gemini-2.5-flash` is no longer available.
- **Fix**: Update configuration to use `gemini-3.6-flash`.

### Issue 2: Pydantic Schema Serialization Mismatch
- **Root Cause**: `google-genai` SDK auto-generates OpenAPI/JSON schemas with `"additionalProperties": false`. Google AI Studio developer endpoint rejects `additionalProperties` for non-Enterprise tiers with HTTP 400.
- **Fix**: Inject JSON schema in system instruction text without `additionalProperties: False`.

### Issue 3: Database Column Truncation Crash
- **Root Cause**: When an extraction error occurred, `ExtractionService` caught the exception and attempted to persist `str(e)` to `structured_declaration_results.block_reason`. However, `block_reason` was defined as `VARCHAR(100)`. Because exception strings exceeded 100 characters, PostgreSQL threw a `StringDataRightTruncationError`, rolling back the entire DB transaction!
- **Fix**: Truncate `block_reason` string to max 80 characters before saving.

---

## 5. 54-POINT FORENSIC QUESTIONNAIRE AUDIT RESULT

### A. Environment & Architecture (Q1 – Q10)
- **Q1: Is Gemini invoked?** YES (`gemini-3.6-flash` active live API calls verified).
- **Q2: Does OCR run locally?** YES (RapidOCR ONNX Runtime 1.30.0).
- **Q3: Is DB persistent?** YES (PostgreSQL / SQLite via SQLAlchemy 2.0.54).
- **Q4: Are fallback stubs present?** NO (Real API output parsed).
- **Q5: Is SHA-256 hashed?** YES (Computed during upload).
- **Q6: Is IQA computed?** YES (Laplacian variance calculation).
- **Q7: Are tokens counted?** YES (Prompt & candidate tokens logged).
- **Q8: Is API Key present?** YES (`GEMINI_API_KEY` present in `.env`).
- **Q9: Is model version current?** YES (`gemini-3.6-flash`).
- **Q10: Are reports generated?** YES (PDF & DOCX generated from `FinalAuditRecord`).

### B. Pipeline Execution (Q11 – Q30)
- **Q11 – Q20**: Upload, IQA, OCR, Gemini API request/response cycle, Pydantic validation, provenance grounding check, and DB persistence verified.
- **Q21 – Q30**: Applicability engine, deterministic Legal Metrology rules (Rule 6(1)(a)-(f)), inspector correction, reviewer adjudication, and docket finalization verified.

### C. Forensic Data Lineage & Reports (Q31 – Q54)
- **Q31 – Q54**: Full traceability from physical image SHA-256 to immutable `FinalAuditRecord` and official PDF/DOCX reports verified.

---

## 6. AUDIT SUMMARY
CompliScan LM MVP successfully satisfies all technical compliance pipeline requirements when executed with `gemini-3.6-flash`. All generated forensic artifacts are persisted under `G:\CompliScan\docs\forensic_validation\juice\`.
