# CompliScan LM — Validation Findings & Forensic Analysis

**Document Version:** 1.0.0  
**Date:** September 20, 2026  
**Scope:** Forensic End-to-End Automated Validation Campaign (Campaigns 00–25)  
**Dataset:** 25 Real Product Package Images (7 Categories)

---

## 1. Summary of Findings

Across 181 executed automated test cases spanning perception, OCR token generation, Gemini 2.5 structured extraction, statutory applicability, deterministic rule evaluation, human inspector workflow, reviewer governance, finalization immutability, reporting, security IDOR isolation, and concurrency:

- **Total Test Cases Executed:** 181
- **Passed:** 181 (100%)
- **Material Defects (P0/P1):** 0
- **Non-blocking Issues / Documented Scope Boundaries (INFO/P3):** 6

---

## 2. Categorized Findings & Forensic Observations

### Finding 1: Single-View Field-of-View (FOV) Information Incompleteness
- **Layer:** Perception / Data Quality
- **Classification:** Expected MVP Boundary / Operational Reality
- **Observation:** Single-image evidence submissions (e.g., front-only packaging for *Juice* or *Serum*) naturally do not depict back-of-pack statutory declarations (such as complete manufacturer address, consumer care email/telephone, or MRP).
- **Engine Behavior:** The pipeline safely classifies missing fields as `NOT_OBSERVED` or `UNREADABLE`. The deterministic compliance engine converts these to `REQUIRES_REVIEW` or `INCOMPLETE`.
- **Verdict:** Compliant with regulatory safety rules. No false violations or false passes were generated.

### Finding 2: OCR Orientation and Curved Geometry Sensitivity
- **Layer:** OCR Perception (RapidOCR / PP-OCRv4 ONNX)
- **Classification:** Operational Condition
- **Observation:** On cylindrical containers (*Lotion*, *Peanut Butter*) with high perspective distortion or extreme side angles, OCR confidence on peripheral tokens drops below 0.65.
- **Engine Behavior:** Low-confidence tokens retain bounding box coordinates within normalized image space. Bounding box coordinates and polygon vertex arrays are preserved for inspector verification visual overlays.
- **Verdict:** Correct. Inspector verification UI allows zooming, panning, and manual verification with bounding box highlight.

### Finding 3: Foreign Manufacturer Address vs Domestic Marketer Disambiguation
- **Layer:** Structured Extraction (Gemini 2.5 Flash) & Statutory Applicability
- **Classification:** Regulatory Scope Boundary
- **Observation:** On imported items (*Serum*), packaging often displays both an overseas manufacturing address and a domestic Indian importer/marketer address.
- **Engine Behavior:** Structured extraction captures candidates for both importer and manufacturer. The rule engine marks statutory country of origin as `APPLICABLE` for `IMPORTED` items (Rule 6(1)(e)) and `NOT_APPLICABLE` for domestic items.
- **Verdict:** Authoritative rule engine correctly isolates statutory requirements based on origin metadata.

### Finding 4: Concurrency & Worker Lease Isolation
- **Layer:** Analysis Job Queue / Asynchronous Execution
- **Classification:** Architecture & Reliability
- **Observation:** Under simulated concurrent worker execution, `claim_next_job` utilizing `SELECT ... FOR UPDATE SKIP LOCKED` guarantees strictly atomic job dispatch. Worker 1 claims pending jobs while Worker 2 receives `None`.
- **Verdict:** Validated. No duplicate execution, race conditions, or leased lock leaks.

### Finding 5: Finalization Immutability & Authoritative Record Protection
- **Layer:** Finalization / Security
- **Classification:** Data Integrity
- **Observation:** Once an inspection reaches `FINALIZED` status with an immutable `FinalAuditRecord`, all subsequent attempts to upload evidence, edit declarations, alter findings, or modify reviewer decisions are rejected with `IllegalStateError` (HTTP 409 Conflict).
- **Verdict:** Authoritative record integrity is preserved.

### Finding 6: Zero-Token OCR Gating
- **Layer:** Pipeline Safety / LLM Cost Protection
- **Classification:** Architecture & Cost Efficiency
- **Observation:** Images that yield zero OCR tokens (e.g., blank or severely corrupted files) are gated before Gemini LLM invocation. No hallucinated structured declarations or spurious compliance findings are generated.
- **Verdict:** Safe failure gating confirmed.
