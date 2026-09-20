# COMPLISCAN LM — PHASE 7.0 MASTER PRODUCTION ARCHITECTURE AUDIT
## Comprehensive Multi-User Cloud Architecture, Evidence Integrity, and Deployment Readiness Blueprint

**Audit Date:** 2026-09-20  
**Audit Standard:** Forensic Repository Grounding & Precise State Classification  
**Status:** RECONCILED MASTER BLUEPRINT — AUDIT & PLANNING ONLY (ZERO CODE MUTATIONS)

---

## 1. Executive Summary & Current-State Classification

**Current System Classification:** **`PRODUCTION READY WITH CONDITIONS`**

### Classification Basis:
CompliScan LM exhibits a robust, production-hardened core for single-node institutional operations. All 86 backend automated tests pass, the frontend Vite build compiles cleanly, asymmetric ES256 Supabase JWKS authentication is verified, worker job queues are protected by `FOR UPDATE SKIP LOCKED`, and finalization immutability is sealed via SHA-256 integrity hashes.

However, the system cannot be designated as *unconditionally scalable multi-node cloud production ready* until two specific deployment tasks are executed in Phase 7.1:
1. **Local Filesystem Evidence Storage (Current State):** Uploaded packaging images are saved to `backend/uploads/` on the local host. In a multi-container or horizontally scaled Render deployment, instances cannot share local disk, causing 404s on cross-node downloads until Supabase Object Storage is wired into `EvidenceService`.
2. **Hardcoded Test Directory Fallback in Reports (Current State):** `pdf_report_service.py` (L591) and `docx_report_service.py` (L374) contain fallback search loops for `Test_Images/Peanut_Butter` and `Test_Images/Juice` when evidence files are missing on disk.

---

## 2. Planning Document Reconciliation Matrix

| Topic | Document | Current Statement in Repo / Docs | Target Reconciled Statement | Conflict Identified | Resolution |
|---|---|---|---|---|---|
| **Evidence Storage** | `phase7_evidence_storage_architecture.md` | "Supabase Storage bucket configured in config.py" | `CURRENT — VERIFIED`: Local disk `backend/uploads/`. `TARGET — PROPOSED`: Supabase Storage bucket `compliscan-evidence`. | Docs previously implied storage was active. | Explicitly classify storage as `IMPLEMENTATION REQUIRED` for Phase 7.1. |
| **Authentication Flow** | `phase7_deployment_architecture.md` | Mentioned both direct and backend-mediated flows. | `CURRENT — VERIFIED`: Backend-mediated login via `POST /api/v1/auth/login` delegating to Supabase GoTrue; ES256 JWKS validation on Render API. | Ambiguity between direct Supabase JS vs FastAPI proxy. | Standardize on **Backend-Mediated Supabase Auth**. Zero Supabase secrets on client. |
| **CORS Origins** | `phase7_deployment_architecture.md` | `CORS_ORIGINS` included `localhost:5173` alongside production. | `TARGET — PROPOSED`: Strict separation. Dev: `http://localhost:5173`. Prod: Exact Vercel domain (`https://compliscan.vercel.app`). | Localhost in production CORS. | Remove localhost from production CORS recommendations. |
| **Gemini Model** | `phase7_master_production_architecture_audit.md` | `gemini-3.6-flash` | `CURRENT — VERIFIED`: `gemini-3.6-flash` authoritative across config, `.env`, and extraction service. | Historical docs cited `gemini-2.5-flash`. | Maintain `gemini-3.6-flash` as current verified reality; document 2.5 as historical. |
| **Test Images Classification** | `phase7_repository_inventory.md` | `EVIDENCE_ORIGINAL` | `CURRENT — VERIFIED`: `VALIDATED_TEST_FIXTURE`. Never production evidence. | Test files classified as original evidence. | Reclassified to `VALIDATED_TEST_FIXTURE`. |
| **Report Image Fallback** | `phase7_master_production_architecture_audit.md` | Fallback loops in PDF/DOCX builders. | `TARGET — PROPOSED`: Remove all `Test_Images` search loops. If missing, render `Retrieval Status: NOT AVAILABLE`. | Demo fallback masked missing evidence. | Formally mandate removal in Phase 7.1. |
| **Render Region** | `phase7_deployment_architecture.md` | "region: singapore" | `TARGET — PROPOSED`: Region selection is a `DEPLOYMENT DECISION` (Singapore proposed for low latency to Supabase AWS `ap-northeast-2`). | Hardcoded region as architectural requirement. | Mark region as `PROPOSED`, requiring operator confirmation. |
| **Report Storage** | `phase7_master_production_architecture_audit.md` | Dynamic generation only. | `TARGET — PROPOSED`: Option C (Persist canonical finalized report in `compliscan-reports/` with on-demand regeneration from FAR). | Unspecified report persistence model. | Standardize on Option C with separate storage namespace. |
| **Evidence Deletion Policy** | `phase7_evidence_storage_architecture.md` | General immutability. | `TARGET — PROPOSED`: Explicit policy: Draft evidence deletable by owner; finalized evidence strictly immutable (`READ_ONLY`). | Undefined pre-finalization deletion behavior. | Formalize explicit pre vs post-finalization deletion rules. |
| **Anti-Tampering Terms** | `phase7_security_readiness.md` | "Non-repudiation / tamper-proof" | `CURRENT — VERIFIED`: `tamper-evident`, `hash-verifiable`, `integrity-verifiable`, `provenance-traceable`. | Overstated cryptographic claims. | Replaced with technically accurate terminology. |

---

## 3. Authoritative Data Ownership Model

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        AUTHORITATIVE DATA OWNERSHIP HIERARCHY                          │
├─────────────────────────────┬───────────────────────────┬──────────────────────────────┤
│ Entity / Artifact           │ Nature & Role             │ Authoritative Storage Target │
├─────────────────────────────┼───────────────────────────┼──────────────────────────────┤
│ Original Evidence Binary    │ Source of Physical Truth  │ Supabase Storage (Object)    │
│ EvidenceAsset               │ Metadata & Byte Identity  │ PostgreSQL (Table)           │
│ ImageQualityAssessment      │ Derived Quality Telemetry │ PostgreSQL (Table)           │
│ OCRResult (Tokens & Boxes)  │ Derived Perception Data   │ PostgreSQL (Table)           │
│ StructuredDeclarationResult │ AI-Derived Extraction     │ PostgreSQL (Table)           │
│ ProductDeclaration          │ Synthesized Docket State  │ PostgreSQL (Table)           │
│ ComplianceFinding           │ Deterministic Rule Output │ PostgreSQL (Table)           │
│ Inspector Verification      │ Human Officer Confirm     │ PostgreSQL (Table)           │
│ ReviewerDecision            │ Human Legal Adjudication  │ PostgreSQL (Table)           │
│ FinalAuditRecord (FAR)      │ Immutable Case Snapshot   │ PostgreSQL (Table)           │
│ FAR Integrity Hash          │ Cryptographic Anchor      │ Sealed inside FAR record     │
│ PDF / DOCX Dossiers         │ Derived Output Documents  │ Generated from FAR / Storage │
│ AuditEvent                  │ Append-Only Event Journal │ PostgreSQL (Table)           │
└─────────────────────────────┴───────────────────────────┴──────────────────────────────┘
```

---

## 4. Authoritative Source-of-Truth Matrix

| Data Entity | Source of Truth | Storage Backend | Mutable State? | Integrity Mechanism | Derived Directly From |
|---|---|---|---|---|---|
| **Original Evidence** | Ingested Package Image | Supabase Storage (`compliscan-evidence`) | **NO** (Immutable post-upload) | SHA-256 computed on raw bytes | Physical Package / Camera |
| **EvidenceAsset** | Upload Metadata Record | PostgreSQL (`evidence_assets`) | **NO** (Draft deletable by owner) | `sha256_hash` (64-hex string) | Ingestion stream + `StorageService` |
| **OCRResult** | Extracted Tokens & Boxes | PostgreSQL (`ocr_results`) | **NO** (Derived perception) | Associated `evidence_id` foreign key | EvidenceAsset binary bytes |
| **StructuredDeclaration** | Gemini Extracted Fields | PostgreSQL (`structured_declaration_results`) | **NO** (Derived extraction) | Token-level provenance indices | OCRResult tokens |
| **ProductDeclaration** | Synthesized Package State | PostgreSQL (`product_declarations`) | **NO** (Synthesized aggregate) | Cross-panel corroboration map | All docket `StructuredDeclarations` |
| **ComplianceFinding** | Statutory Findings (7) | PostgreSQL (`compliance_findings`) | **NO** (Rule evaluation) | Deterministic LMPC 2011 rule logic | `ProductDeclaration` |
| **Inspector Verification** | Manual Observations/Edits | PostgreSQL (`declaration_corrections`) | **Mutable in DRAFT only** | Inspector `user_id` + timestamp | Human Inspecting Officer |
| **ReviewerDecision** | Statutory Adjudication | PostgreSQL (`reviewer_decisions`) | **Mutable in SUBMITTED only** | Mandatory legal rationale text | Human Reviewing Officer |
| **FinalAuditRecord** | **Master Audit Snapshot** | PostgreSQL (`final_audit_records`) | **STRICTLY IMMUTABLE** | `integrity_hash` = SHA-256(canonical JSON) | Sealed 7-gate finalization snapshot |
| **AuditEvent** | Chronological Audit Log | PostgreSQL (`audit_events`) | **STRICTLY APPEND-ONLY** | Auto-incrementing sequence + timestamps | System and user actions |
| **PDF Dossier** | Departmental Inspection PDF | Storage (`compliscan-reports`) / Dynamic | **Immutable per FAR** | PDF SHA-256 checksum | `FinalAuditRecord` via `ReportDataBuilder` |
| **DOCX Dossier** | Departmental Inspection DOCX | Storage (`compliscan-reports`) / Dynamic | **Immutable per FAR** | DOCX SHA-256 checksum | `FinalAuditRecord` via `ReportDataBuilder` |

---

## 5. Master Architecture Diagram (Trust & Secret Boundaries)

```
                                 PUBLIC INTERNET (HTTPS / TLS 1.3)
                                                 │
   ══════════════════════════════════════════════╪═══════════════════════════════════════════════ [Trust Boundary 1: Browser Ingress]
                                                 ▼
                        ┌──────────────────────────────────────────────────┐
                        │                 VERCEL FRONTEND                  │
                        │            React 18 SPA + Vite + Tailwind        │
                        │           CameraCapture PDP Video Stream         │
                        │  Public Client Config: VITE_API_BASE_URL ONLY    │
                        └────────────────────────┬─────────────────────────┘
                                                 │
                                                 │ HTTPS / JSON REST (Authorization: Bearer <JWT>)
   ══════════════════════════════════════════════╪═══════════════════════════════════════════════ [Trust Boundary 2: API Gateway]
                                                 ▼
                        ┌──────────────────────────────────────────────────┐
                        │             RENDER WEB SERVICE (API)             │
                        │               FastAPI (Python 3.11+)             │
                        │         Binds: 0.0.0.0:$PORT, /api/v1/health     │
                        │     CORS: Exact Production Vercel Origin         │
                        │   Holds: Server Secrets (DB, Storage, Gemini)    │
                        └──────────────┬───────────────────┬───────────────┘
                                       │                   │
                    ┌──────────────────┘                   └──────────────────┐
                    ▼                                                         ▼
   ┌─────────────────────────────────┐                       ┌─────────────────────────────────┐
   │         SUPABASE CLOUD          │                       │      GOOGLE GENERATIVE AI       │
   │                                 │                       │                                 │
   │  [1] Supabase Auth (GoTrue)     │                       │  Model: gemini-3.6-flash        │
   │      - Asymmetric ES256 JWKS    │                       │  Task: Semantic Structuring     │
   │      - Role Claims & Tokens     │                       │  Guardrails: Zero Hallucination │
   │                                 │                       │  Token Provenance Validation    │
   │  [2] PostgreSQL 15+ (AWS ap-ne) │                       └─────────────────────────────────┘
   │      - PgBouncer Pooler (6543)  │                                        ▲
   │      - Direct SSL Engine (5432) │                                        │
   │      - Queue: SKIP LOCKED       │                                        │ Perception Call
   │                                 │                                        │
   │  [3] Supabase Storage           │                                        │
   │      - Bucket: compliscan-ev    │                                        │
   │      - SHA-256 Byte Integrity   │                                        │
   └────────────────┬────────────────┘                                        │
                    ▲                                                         │
                    │ Database Queue & Storage Streaming                      │
                    ▼                                                         │
   ┌──────────────────────────────────────────────────────────────────────────┴────────┐
   │                        RENDER BACKGROUND WORKER                                   │
   │                        Process: python -m worker.runner                           │
   │    - Claims queued jobs via SELECT ... FOR UPDATE SKIP LOCKED                     │
   │    - Performs Image Quality Assessment (IQA) & Barcode/QR Decoding                │
   │    - Performs OCR & Gemini 3.6 Flash Structured Extraction                        │
   │    - Transitions analysis state: PENDING -> RUNNING -> COMPLETED / FAILED         │
   └───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Subsystem Reality & Blueprint Specifications

### 6.1 Authentication Architecture (Canonical Model)
- **Model:** **Backend-Mediated Supabase Auth**.
- **Login Flow:** User submits credentials to `POST /api/v1/auth/login`. FastAPI `AuthService` proxies to Supabase GoTrue `sign_in_with_password()`.
- **Token Delivery:** FastAPI returns `access_token` (JWT) and user profile. Frontend stores JWT in browser `localStorage`.
- **API Authorization:** Frontend passes `Authorization: Bearer <token>` on all requests.
- **Token Validation:** FastAPI `verify_supabase_token()` dynamically fetches public keys from Supabase JWKS (`https://<ref>.supabase.co/auth/v1/.well-known/jwks.json`), verifies the asymmetric **ES256 (ECDSA P-256)** signature, validates expiration and claims (`aud == "authenticated"`), and maps `sub` UUID to `public.users`.
- **Secret Isolation:** `SUPABASE_SERVICE_ROLE_KEY` is strictly held on Render server-side. Zero admin keys enter the Vercel frontend bundle.

### 6.2 Evidence Storage & Integrity
- **Current State (`CURRENT — VERIFIED`):** Files written to local disk `backend/uploads/{inspection_id}/{evidence_id}_{safe_filename}`.
- **Target State (`TARGET — PROPOSED`):** `EvidenceService` delegates to `StorageService` using `SupabaseStorageBackend` in production and `LocalStorageBackend` in offline tests.
- **Path Standard:** `inspections/{inspection_id}/{evidence_id}/original/{safe_filename}`.
- **Anti-Tampering Chain:** Raw Bytes ──► SHA-256 ──► `EvidenceAsset.sha256_hash` ──► Storage Upload ──► Download & SHA-256 Verification ──► FAR Snapshot Sealing ──► FAR Integrity Hash.

### 6.3 Perception & AI Semantic Extraction
- **Current Model (`CURRENT — VERIFIED`):** `gemini-3.6-flash` authoritative across `.env`, `config.py`, and `extraction_service.py`.
- **Provenance Gate:** Every extracted field cites exact integer token indices from OCR. `ExtractionService.validate_provenance()` rejects any out-of-bounds or phantom indices.
- **Synthesis Engine:** `ProductEvidenceSynthesisService` merges multi-image observations into a unified docket declaration without majority-vote erasure of conflicts.

### 6.4 Deterministic Compliance & Reviewer Governance
- **Compliance Evaluation:** Deterministic rule functions evaluating Legal Metrology (Packaged Commodities) Rules 2011 (Rule 6(1)(a)-(g)). Zero LLM legal decisions.
- **Reviewer Adjudication:** Mandatory legal rationale required for CONFIRMED or OVERRIDDEN determinations.
- **Finalization:** Strict 7-gate validation verifying all prerequisites before creating the immutable `FinalAuditRecord` and transitioning state to `READ_ONLY`.

### 6.5 Report Generation & Parity
- **Source of Truth:** Derived strictly from immutable `FinalAuditRecord` via `ReportDataBuilder`.
- **Parity:** 1:1 structural and data parity between `PDFReportService` (ReportLab) and `DOCXReportService` (python-docx).
- **Fallback Rule (`TARGET — PROPOSED`):** Remove all `Test_Images/` search loops. Missing evidence renders:
  `Retrieval Status: NOT AVAILABLE | Integrity Status: NOT VERIFIED`.

---

## 7. Reconciled Implementation Phase Roadmap

```
Phase 7.1: Cloud Storage & Report Hardening (IMPLEMENTATION)
    ├── Implement StorageService (SupabaseStorageBackend in prod, Local in test)
    ├── Refactor EvidenceService & AnalysisJobService to stream bytes via StorageService
    └── Remove Test_Images fallback loops from PDF and DOCX report builders

Phase 7.2: Repository Cleanup & Manifest Creation
    ├── Author render.yaml (FastAPI Web Service + Worker) & frontend/vercel.json
    ├── Update frontend/src/api/client.ts for VITE_API_BASE_URL
    └── Archive historical root markdown logs to docs/archive/

Phase 7.3: Deployment & Multi-User Verification
    ├── Configure production CORS_ORIGINS (exact Vercel domain)
    ├── Deploy Supabase Storage bucket, Render services, and Vercel frontend
    └── Execute multi-user concurrency and IDOR isolation test suite

Phase 7.4: Live Public Internet & Mobile Camera E2E Verification
    ├── Execute full public internet E2E inspection over HTTPS
    ├── Execute mobile browser CameraCapture E2E verification
    └── Perform database backup (pg_dump) and non-destructive restore validation
```
