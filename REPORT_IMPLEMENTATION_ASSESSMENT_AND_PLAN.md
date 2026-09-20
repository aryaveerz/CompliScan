# CompliScan LM — Inspection Report Implementation Assessment & Technical Plan

**Document Version:** 1.0  
**Status:** Pre-Implementation Architectural Assessment  
**Target:** 12-Section & 4-Annexure Production-Quality Legal Metrology Report System  

---

## Executive Summary

This document presents the complete architectural reconnaissance, gap analysis, and implementation plan for the **CompliScan LM Final Inspection Report System**. 

The implementation adheres to the core engineering axiom:
$$\text{AI Finds} \longrightarrow \text{Evidence Proves} \longrightarrow \text{Deterministic Rules Evaluate} \longrightarrow \text{Inspector Verifies} \longrightarrow \text{Reviewer Decides} \longrightarrow \text{FinalAuditRecord Preserves}$$

The PDF/DOCX report generation pipeline does **not** act as an independent source of truth, nor does it perform ad-hoc AI/LLM calls. All data rendered into the report originates strictly from the immutable `FinalAuditRecord` and persisted domain state.

---

## 1. Current Architecture Discovered

The existing CompliScan LM backend follows a strict, layered asynchronous pipeline:

```
[Evidence Ingestion]
        │
        ▼  (Compute Original SHA-256)
[OpenCV Image Quality Check] (Sharpness/Exposure)
        │
        ▼
[RapidOCR / PaddleOCR PP-OCRv4] (Local ONNX Text Perception & Token Bounding Boxes)
        │
        ▼
[Google Gemini 3.6 Flash] (Information Structuring & Token-Index Mapping)
        │
        ▼
[Multi-Image Synthesis Service] (Cross-Surface Conflict Detection & Lineage)
        │
        ▼
[Deterministic Legal Metrology Rule Engine] (Rule 6(1)(a)-(da) Statutory Findings)
        │
        ▼
[Inspector Verification & Remarks]
        │
        ▼
[Senior Reviewing Officer Adjudication] (Confirm / Override / State Rationale)
        │
        ▼
[Finalization Service] (Creates Immutable FinalAuditRecord + Cryptographic Seal)
        │
        ▼
[Report Generation Service] (ReportLab PDF & python-docx)
```

---

## 2. Existing Report Functionality

- **`PDFReportService`** (`backend/app/services/pdf_report_service.py`):
  - Uses `ReportLab` to construct a 5-section PDF directly from `FinalAuditRecord`.
  - Enforces that no report can be generated without a finalized `FinalAuditRecord`.
- **`DOCXReportService`** (`backend/app/services/docx_report_service.py`):
  - Uses `python-docx` to construct an editable Microsoft Word document with 100% data parity.
- **REST Endpoints**:
  - `GET /api/v1/inspections/{inspection_id}/final-report`
  - `GET /api/v1/inspections/{inspection_id}/report/pdf`
  - `GET /api/v1/inspections/{inspection_id}/report/docx`
- **Audit Logging**: Emits `AuditEventType.REPORT_DOWNLOADED` with user ID and timestamp upon every report generation.

---

## 3. Existing Domain Models & Data Lineage

| Model | File | Key Fields / Role in Reporting |
| :--- | :--- | :--- |
| **`InspectionCase`** | `backend/app/models/inspection.py` | `id`, `case_number`, `product_name`, `origin_status`, `created_by_id`, `reviewer_id`, `created_at`, `finalized_at` |
| **`EvidenceAsset`** | `backend/app/models/evidence.py` | `id`, `original_filename`, `file_path`, `sha256_hash`, `evidence_type`, `image_quality_status`, `ocr_tokens` |
| **`ProductDeclaration`** | `backend/app/models/product_declaration.py` | Synthesized multi-image declarations, field-level `supporting_evidence_ids`, token indices, confidence scores |
| **`ComplianceFinding`** | `backend/app/models/compliance.py` | Statutory findings (`PASS`, `POTENTIAL_NON_COMPLIANCE`, `REQUIRES_REVIEW`), applicable rules, citations |
| **`ReviewerDecision`** | `backend/app/models/reviewer.py` | Reviewer determinations, overrides, and legal rationales |
| **`AuditEvent`** | `backend/app/models/audit.py` | Chronological event logs (`actor_id`, `actor_role`, `event_type`, `details`, `created_at`) |
| **`FinalAuditRecord`** | `backend/app/models/final_audit.py` | Immutable snapshots of context, evidence, declarations, compliance, reviewer decisions, and composite hash |

---

## 4. Existing State Machine & Lifecycle

The inspection lifecycle is enforced through `shared.domain.states.InspectionLifecycleState`:

$$\text{DRAFT} \longrightarrow \text{EVIDENCE\_UPLOADED} \longrightarrow \text{EXTRACTED} \longrightarrow \text{EVALUATED} \longrightarrow \text{UNDER\_INSPECTION} \longrightarrow \text{SUBMITTED\_FOR\_REVIEW} \longrightarrow \text{REVIEWED} \longrightarrow \text{FINALIZED} \longrightarrow \text{READ\_ONLY}$$

- Once an inspection reaches `FINALIZED`, the `FinalizationService` marks the `finalization_status` as `FINALIZED` and locks all mutable endpoints.
- Generating the official report is permitted only on `FINALIZED` records.

---

## 5. Existing Audit Implementation

- The `audit_events` table captures all lifecycle transitions:
  - `INSPECTION_CREATED`
  - `EVIDENCE_UPLOADED`
  - `OCR_PROCESSING_COMPLETED`
  - `DECLARATIONS_EXTRACTED`
  - `DECLARATIONS_SYNTHESIZED`
  - `COMPLIANCE_EVALUATED`
  - `INSPECTION_SUBMITTED_FOR_REVIEW`
  - `REVIEW_DECISION_RECORDED`
  - `INSPECTION_FINALIZED`
  - `REPORT_DOWNLOADED`
- In `FinalizationService`, the full chronological audit trail is serialized into `FinalAuditRecord.audit_metadata["audit_trail"]` to guarantee permanent immutability.

---

## 6. Existing PDF / Report Implementation

- **Library**: `ReportLab` (v4.x) using `SimpleDocTemplate`, `Paragraph`, `Table`, `KeepTogether`, and `HRFlowable`.
- **Current Layout**: 5 high-level sections (Particulars of Commodity, Evidence Register & Hashes, Declaration-Wise Verification, Statutory Compliance Findings vs Reviewer Adjudication, Sign-off).
- **Styling**: Indian Legal Metrology departmental styling with clean slate/navy color schemes (`#0f172a`, `#1e3a8a`, `#e2e8f0`).

---

## 7. Existing Frontend Screens Relevant to Reports

- **`InspectionWorkspacePage.tsx`**: Header bar and summary drawer expose "Download PDF Report" and "Download DOCX Report" when `status === 'FINALIZED'`.
- **`FinalRecordSection.tsx`**: Renders the finalized audit snapshot, hash verification, and one-click report downloads.
- **`HistoryPage.tsx`**: Archive table displaying closed dockets with PDF/Word download action icons.
- **`AuditTimeline.tsx`**: Visualizes chronological audit trail events.

---

## 8. What Already Satisfies the Specification

1. **Strict Immutability**: Reports are derived 100% from `FinalAuditRecord`.
2. **Evidence Integrity**: SHA-256 fingerprints are computed at upload time from raw bytes and persisted.
3. **Traceability**: Synthesized fields reference supporting `EvidenceAsset` IDs and OCR token bounding boxes.
4. **Separation of Roles**: AI structuring, deterministic rule evaluations, and human reviewer determinations are strictly partitioned.
5. **Download Auditing**: `AuditEventType.REPORT_DOWNLOADED` is logged whenever a user exports a report.

---

## 9. Gap Analysis (What is Missing)

1. **Formal 12-Section & 4-Annexure Report Structure**:
   - **Document Control Block**: Header metadata table (Rule set, Evaluation version, OCR engine, AI model, Record status).
   - **Section 1**: Inspection Details (Location, Officer ID, Reviewing Officer, Timestamps).
   - **Section 2**: Product / Commodity Particulars (Brand, Variant, Net Qty, Batch, Origin).
   - **Section 3**: Evidence Register (File dimensions, types, SHA-256 fingerprints).
   - **Section 4**: Declaration Extraction (Observed text, token references, confidence).
   - **Section 5**: Applicability & Rule-Wise Checks (Statutory rules matrix).
   - **Section 6**: Observations / Potential Non-Compliance (Specific non-compliance rationales).
   - **Section 7**: Evidence & Visual Corroboration (Photographs with derived bounding box annotations).
   - **Section 8**: Inspector Verification & Remarks (Inspector notes and corrections).
   - **Section 9**: Reviewing Officer's Determination (Reviewer overrides and legal determinations).
   - **Section 10**: Final Compliance Summary (Dynamic count cards and final sign-off banner).
   - **Section 11**: Evidence Integrity & Anti-Tampering Record (Cryptographic evidence integrity statement).
   - **Section 12**: Complete Chronological Audit Trail table.
   - **Annexure A**: Original Evidence Images (Full-width embedded figures with metadata).
   - **Annexure B**: Detailed OCR Token & Bounding Box Registry.
   - **Annexure C**: Detailed Statutory Rule-Wise Findings Matrix.
   - **Annexure D**: Raw Structured `FinalAuditRecord` Snapshot.
2. **Report SHA-256**: Calculating the SHA-256 hash of the final PDF bytes and exposing it in Document Control / API response.
3. **Intermediate Report Data Builder**: A dedicated view-model aggregator (`ReportDataBuilder`) separating domain extraction from document rendering.
4. **Multi-Page Layout Polish**: Page number callbacks (`Page X of Y`), running headers, and table auto-wrap for long 64-character SHA-256 hashes.

---

## 10. Required Changes & Technical Design

### Architectural Pipeline
```
[Database / FinalAuditRecord]
             │
             ▼
[ReportDataBuilder (View Model DTO)]
             │
      ┌──────┴──────────────────────┐
      ▼                             ▼
[PDFReportService (ReportLab)]  [DOCXReportService (python-docx)]
      │                             │
      ▼                             ▼
[Final PDF Bytes]             [Final DOCX Bytes]
      │
      ▼
[Compute Report SHA-256]
      │
      ▼
[Delivered Report with Audit Log]
```

### Key Components to Build:
1. **`backend/app/services/report_data_builder.py`**:
   - Transforms `FinalAuditRecord` + associated `EvidenceAsset` records into a clean, strongly typed `ReportViewModel`.
   - Computes dynamic counts (Assessed, Pass, Potential Non-Compliance, Requires Review).
   - Prepares visual evidence figures and derived bounding box overlays.
2. **`backend/app/services/pdf_report_service.py`**:
   - Upgraded to render all 12 sections and 4 annexures.
   - Custom `NumberedCanvas` for `Page X of Y` footers and running headers.
   - Long-hash wrapping in Courier font.
3. **`backend/app/services/docx_report_service.py`**:
   - Upgraded to match the 12-section + 4-annexure structure for complete Word document parity.

---

## 11. Proposed Implementation Order

- **Phase 1**: Implement `ReportDataBuilder` (`backend/app/services/report_data_builder.py`).
- **Phase 2**: Rebuild `PDFReportService` with `NumberedCanvas`, Document Control, and Sections 1–6.
- **Phase 3**: Implement Section 7 & Annexure A with embedded evidence images and derived bounding box overlays.
- **Phase 4**: Implement Sections 8–12 and Annexures B, C, and D in `PDFReportService`.
- **Phase 5**: Update `DOCXReportService` for 100% visual and data parity.
- **Phase 6**: Update API endpoints (`inspections.py`, `reviews.py`) to compute Report SHA-256 and log audit events.
- **Phase 7**: Execute automated verification tests (`pytest`) and validate with real Juice dataset (`INSP-2026-DEL-LM-A694`).

---

## 12. Files / Modules to Create or Modify

1. **`backend/app/services/report_data_builder.py`** *(NEW)*
2. **`backend/app/services/pdf_report_service.py`** *(MODIFY)*
3. **`backend/app/services/docx_report_service.py`** *(MODIFY)*
4. **`backend/app/api/v1/inspections.py`** *(MODIFY)*
5. **`backend/app/api/v1/reviews.py`** *(MODIFY)*
6. **`backend/tests/test_pdf_report_generation.py`** *(MODIFY / EXTEND)*

---

## 13. Quality Assurance & Acceptance Checklist

- [ ] Report strictly derives data from `FinalAuditRecord` (no ad-hoc queries).
- [ ] Document Control block renders real metadata (Rule version, OCR engine, AI model, Record status).
- [ ] All 12 formal sections render in proper sequence without page layout breakage.
- [ ] Annexure A embeds actual evidence images with SHA-256 fingerprints and figure titles.
- [ ] Long 64-character SHA-256 hashes wrap cleanly without clipping table borders.
- [ ] Section 7 derived visual bounding box overlays do not alter original evidence images.
- [ ] Dynamic counts in Section 10 match actual findings.
- [ ] Report SHA-256 is dynamically calculated from output bytes.
- [ ] Full automated test suite passes with 100% success rate.
