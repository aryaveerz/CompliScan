# COMPLISCAN LM — PHASE 7.0 DATA LIFECYCLE ARCHITECTURE
## End-to-End Evidence Ingestion, Perception, Verification, Adjudication & Dossier Sealing

**Audit Date:** 2026-09-20  
**Status:** RECONCILED BLUEPRINT — AUDIT & PLANNING ONLY (ZERO CODE MUTATIONS)

---

## 1. Complete End-to-End Lifecycle Flow

```
[1] Physical Packaged Commodity
       │  (Inspector capture via CameraCapture.tsx or file upload)
       ▼
[2] Input Validation & Decodability
       │  (MIME check <=10MB, PIL Image.open().verify())
       ▼
[3] Cryptographic Hashing (SHA-256)
       │  (Computed strictly on raw incoming binary bytes)
       ▼
[4] Persistent Evidence Storage
       │  (CURRENT: Local filesystem backend/uploads/)
       │  (TARGET: Supabase Storage: inspections/{id}/{ev_id}/original/{name})
       ▼
[5] EvidenceAsset Database Record Created
       │  (id: EV-*, sha256_hash, file_size, mime_type, storage_path)
       │  (AuditEvent: EVIDENCE_UPLOADED)
       ▼
[6] Image Quality Assessment (IQA) & Barcode Detection (Async Worker)
       │  (Worker downloads bytes via StorageService, verifies SHA-256)
       │  (Laplacian blur, brightness, contrast, EAN-13 barcode/QR decoded)
       │  (ImageQualityAssessment record persisted in PostgreSQL)
       ▼
[7] Optical Character Recognition (OCR Engine)
       │  (Tesseract / Cloud OCR ──► Tokens with bounding box coordinates)
       │  (OCRResult record persisted with tokens JSONB)
       ▼
[8] Gemini 3.6 Flash Structured Declaration Extraction
       │  (ExtractionService structures tokens into 7 statutory domains)
       │  (ExtractionService.validate_provenance() verifies token grounding)
       │  (StructuredDeclarationResult persisted with telemetry)
       ▼
[9] Product Evidence Synthesis (ProductEvidenceSynthesisService)
       │  (Multi-panel corroboration, conflict detection, observation status)
       │  (ProductDeclaration record created for inspection docket)
       ▼
[10] Declaration Validation Engine (DeclarationValidationService)
       │  (Validates date logic, MRP formatting, cross-panel consistency)
       ▼
[11] Deterministic Compliance Evaluation (ComplianceService)
       │  (Evaluates synthesized ProductDeclaration against LMPC 2011 Rules)
       │  (Generates 7 ComplianceFinding records: PASS / POTENTIAL_NON_COMPLIANCE)
       ▼
[12] Inspecting Officer Verification & Manual Observations
       │  (Inspector reviews findings, adds observations, submits for review)
       │  (Lifecycle state: DRAFT ──► SUBMITTED_FOR_REVIEW)
       │  (AuditEvent: INSPECTION_SUBMITTED)
       ▼
[13] Reviewing Officer Adjudication (ReviewerService)
       │  (Reviewer confirms or overrides findings with mandatory legal rationale)
       │  (ReviewerDecision records persisted)
       │  (AuditEvent: REVIEWER_DECISION_RECORDED)
       ▼
[14] 7-Gate Pre-Condition Validation (FinalizationService)
       │  (Verifies SUBMITTED state, 0 processing jobs, 0 open requests, evidence exists,
       │   applicability exists, findings exist, reviewer decisions complete)
       ▼
[15] FinalAuditRecord (FAR) Sealing & Hash Generation
       │  (Generates canonical JSON snapshot of all 14 stages)
       │  (Computes SHA-256 integrity_hash over canonical snapshot)
       │  (Persists FinalAuditRecord, marks inspection READ_ONLY & FINALIZED)
       │  (AuditEvent: INSPECTION_FINALIZED)
       ▼
[16] Statutory Report Generation (PDF & DOCX)
       │  (ReportDataBuilder builds typed ReportViewModel strictly from FAR snapshot)
       │  (PDFReportService & DOCXReportService generate 1:1 identical dossiers)
       │  (TARGET: Persisted in compliscan-reports/ with SHA-256 checksums)
```

---

## 2. Stage-by-Stage Forensic Matrix

| Stage | Persisted Entity | Storage Target | Cryptographic Hash / Identifier | Actor / Trigger | Failure Behavior |
|---|---|---|---|---|---|
| **1. Evidence Ingestion** | Raw Image Binary | Supabase Storage (`compliscan-evidence`) | SHA-256 computed on binary | Inspector (Frontend) | HTTP 413 (size), 415 (MIME), 422 (corrupt) |
| **2. Evidence Asset** | `evidence_assets` table | PostgreSQL | `EV-{UUID12}`, `sha256_hash` | System (`EvidenceService`) | Transaction rollback |
| **3. IQA & Barcodes** | `image_quality_assessments` | PostgreSQL | `IQA-{UUID12}` | Worker (`ImageQualityService`) | Job retry / `PROCESSING_FAILED` |
| **4. OCR Tokens** | `ocr_results` table | PostgreSQL | `OCR-{UUID12}`, token indices | Worker (`OCRService`) | Job retry / 0 tokens recorded |
| **5. AI Extraction** | `structured_declaration_results` | PostgreSQL | `DEC-{UUID12}`, trace ID | Worker (`ExtractionService`) | Bounded retry (4x); `PROCESSING_FAILED` on API error |
| **6. Synthesis** | `product_declarations` table | PostgreSQL | `PD-{UUID12}` | Worker (`ProductEvidenceSynthesisService`) | Retains raw conflicts (`CONFLICTING` status) |
| **7. Compliance** | `compliance_findings` table | PostgreSQL | `CF-{UUID12}`, Rule Citation | System (`ComplianceService`) | Evaluates `REQUIRES_REVIEW` on conflict |
| **8. Adjudication** | `reviewer_decisions` table | PostgreSQL | `RD-{UUID12}` | Reviewer (Frontend) | HTTP 400 if rationale missing |
| **9. Finalization** | `final_audit_records` table | PostgreSQL | `FAR-{UUID10}`, `integrity_hash` | Reviewer (`FinalizationService`) | HTTP 400 / 409 if any of 7 gates fail |
| **10. Reports** | PDF / DOCX Dossiers | Storage (`compliscan-reports`) | SHA-256 of generated files | Authorized Officer (`ReportDataBuilder`) | Renders `NOT AVAILABLE` if asset missing |
