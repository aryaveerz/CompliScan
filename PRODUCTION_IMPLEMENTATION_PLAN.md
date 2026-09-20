# CompliScan LM — Master Production Implementation Plan
## Forensic Integrity, Real-World Inspection Workflow & Indian Government-Style Statutory Dossier

**Target Standard:** Pre-Production $\longrightarrow$ Production Hardening  
**Date:** 2026-09-20  
**Status:** In Execution  

---

## 1. Executive Directive & Governing Principle

CompliScan LM is transitioning from an MVP to a production-grade statutory Legal Metrology inspection platform. The system operates strictly under the immutable data flow:

$$\begin{aligned}
\text{Real Inspection} &\longrightarrow \text{Real Authenticated Inspector} \longrightarrow \text{Real Geo-Location} \\
&\longrightarrow \text{Real Packaging Evidence Assets (SHA-256)} \\
&\longrightarrow \text{Real PaddleOCR PP-OCRv4 (ONNX Tokens)} \\
&\longrightarrow \text{Real Structured Extraction (gemini-3.6-flash / Token-Grounded)} \\
&\longrightarrow \text{Deterministic Multi-Evidence Product Synthesis} \\
&\longrightarrow \text{Deterministic Statutory Rule Evaluation (Rule 6(1)(a)-(da))} \\
&\longrightarrow \text{Real Inspector Verification (Persisted Corrections/Remarks)} \\
&\longrightarrow \text{Real Reviewer Adjudication (Persisted Determinations/Rationales)} \\
&\longrightarrow \text{Immutable FinalAuditRecord (Sealed Ledger)} \\
&\longrightarrow \text{ReportDataBuilder (Pure Read/Transform Layer)} \\
&\longrightarrow \text{Indian Government-Style Statutory Inspection Dossier (PDF & DOCX)}
\end{aligned}$$

### Core Non-Negotiable Mandates
1. **Zero Dummy/Mock Data in Production:** All fallback values, hardcoded inspection records, placeholder companies ("Apex", "Acme", "Dabur" where evidence is "ITC / B Natural"), fake officer names, or synthetic token lists are completely eliminated from the production path.
2. **Explicit Representation of Missing State:** If data is not captured or persisted in domain state, it is explicitly shown as `NOT RECORDED`, `NOT AVAILABLE`, `NOT APPLICABLE`, `PENDING`, or `NO DATA`.
3. **No Impersonation of Government Authority:** The dossier uses formal Indian administrative-document styling (A4, serif/sans typography, navy/charcoal palette, disciplined borders, Document Control) under CompliScan LM's institutional identity (`COMPLISCAN LM — LEGAL METROLOGY INSPECTION & COMPLIANCE SYSTEM`), strictly avoiding unauthorized national emblems, fake stamps, or fabricated ministry letterheads.
4. **Pure Projection Report Generation:** Report generators (`PDFReportService`, `DOCXReportService`) receive exclusively the finalized, immutable `FinalAuditRecord` and DB evidence. They make zero external LLM calls, zero database mutations, and zero heuristic normalizations.

---

## 2. Phase-by-Phase Implementation Roadmap (Phases 0–50)

### Phase 0: Repository-Wide Production Data Audit
- Systematically scan frontend, backend, models, API routers, and schemas for hardcoded defaults, dummy dictionaries, and mock fallbacks.
- Ensure production APIs return empty lists/states rather than mock data when the database is empty.

### Phase 1: Real Inspector & Reviewer Identity Model
- Extend user schemas and audit records to support formal identity attributes: `full_name`, `officer_id`, `designation`, `department`, `unit_office`, `authenticated_user_id`.
- Ensure reports display persisted officer details or `NOT RECORDED` without UUID fabrication.

### Phase 2: Real Inspection Location Model
- Implement structured location tracking: `premises_name`, `address_line_1`, `address_line_2`, `locality`, `city`, `district`, `state`, `pin_code`, `latitude`, `longitude`, `capture_method` (`GPS`, `MANUAL`, `REGISTERED_PREMISES`, `NOT_RECORDED`).
- If unrecorded, display `Location: NOT RECORDED`.

### Phase 3: Inspection Lifecycle Timestamps
- Distinctly capture and format `inspection_started_at`, `inspection_completed_at`, `submitted_at`, `reviewed_at`, `finalized_at`, and `report_generated_at`.
- Provide both UTC and clear local timezone representation.

### Phase 4 & 5: Evidence & OCR Forensic Reconciliation
- Verify that every evidence asset has a valid SHA-256 fingerprint and real OCR tokens from PaddleOCR PP-OCRv4 ONNX.
- Annexure B must display real persisted tokens or an explicit note: `"No OCR tokens were persisted for this evidence asset."`

### Phase 6 & 7: Product / Brand / Evidence Consistency & Provenance
- Resolve the Juice dataset (`Test_Images/Juice`): Image tokens show **"B Natural Guava" (ITC Limited)**, NOT Dabur.
- Update token-grounded extraction rules to accurately extract B Natural Guava declarations directly from the real PaddleOCR ONNX tokens, maintaining strict token-index provenance.
- Add regression tests to prevent evidence/product mismatches.

### Phase 8: Conflict Preservation
- If conflicting declarations appear across package panels (e.g. front PDP vs side nutritional panel), preserve `observation_status = CONFLICTING` and route to `REQUIRES_REVIEW`.

### Phase 9 & 10: Persisted Inspector Verification & Reviewer Adjudication
- Capture real inspector corrections (`DeclarationCorrection`) and manual observations (`ManualObservation`). If no inspector remarks exist, render `NOT RECORDED`.
- Capture real reviewer determinations (`ReviewerDecision`) with explicit legal rationales.

### Phase 11 & 12: Complete Audit Trail & Decision Lineage
- Capture all lifecycle events (`CASE_CREATED`, `EVIDENCE_UPLOADED`, `OCR_COMPLETED`, `EXTRACTION_COMPLETED`, `SYNTHESIS_COMPLETED`, `EVALUATION_COMPLETED`, `INSPECTOR_VERIFIED`, `SUBMITTED_FOR_REVIEW`, `ADJUDICATED`, `FINALIZED`, `REPORT_DOWNLOADED`).
- Guarantee complete machine-verifiable lineage from Final Decision $\to$ Evidence Asset SHA-256.

### Phase 13–15: Zero Dummy UI Hardening & ReportDataBuilder Redesign
- Remove all mock fallbacks from frontend/backend.
- Redesign `ReportDataBuilder` to build a 12-section + 4-annexure administrative view model from persisted state only.

### Phase 16–21, 38–41: Indian Government-Style Statutory Dossier (PDF & DOCX)
- Standard A4 page setup with 20 mm administrative margins.
- Two-pass `NumberedCanvas` rendering `Page X of Y` and running departmental headers/footers.
- Formal Document Control Page.
- 12 Numbered Sections + 4 Annexures (Annexure A: Images, Annexure B: OCR Tokens, Annexure C: Statutory Matrix, Annexure D: Raw Immutable JSON).
- Monospace Courier wrapping for 64-character SHA-256 hashes without table distortion.

### Phase 42–46: Cryptographic Integrity & Automated Verification
- Compute tripartite hashes: Evidence SHA-256, FAR Snapshot Hash, Output Report (PDF/DOCX) SHA-256.
- Run comprehensive 28+ check test suite.
- Validate empty state and real Golden Path execution on `Test_Images/Juice`.

### Phase 47–50: Final Production Readiness Audit & Deliverables
- Verify all 20 Production Readiness Gates.
- Generate `PRODUCTION_FORENSIC_REMEDIATION_REPORT.md` and finalized PDF/DOCX reports.
