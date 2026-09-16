# ComplianceScan — MVP Operational Workflow & System Architecture Derivation

**Project:** ComplianceScan  
**Document Type:** Formal MVP Architecture & Operational Workflow Derivation  
**Authority:** Phase 0 Legal Reconciliation Approved (Human Decision Checkpoint)  
**Status:** DRAFT SPECIFICATION — AWAITING HUMAN APPROVAL (NO CODE AUTHORIZATION)  
**Date:** September 2026  

---

## SECTION A: Executive Summary

Following formal human approval of the **Phase 0 Legal and Project Reconciliation Audit**, this document derives the **actual Minimum Viable Product (MVP)** operational workflow, logical architecture, component boundaries, and implementation roadmap for ComplianceScan.

### 1. The Core Architectural Mandate
We intentionally establish a strict separation between:
- **The Long-Term Target Architecture:** The comprehensive 25-component, 19-stage, enterprise-scale regulatory enforcement vision documented across `g:\CompliScan\Documentation\`.
- **The Actual MVP System:** A streamlined, buildable, deployable, defensible, and demonstrable inspection-assistance application that rigorously implements the core principles without enterprise bloat.

### 2. Primary Architectural Invariants
1. **Scope Boundary:** The MVP is strictly an **inspection-assistance tool** for physical packaged commodities under the Legal Metrology (Packaged Commodities) Rules, 2011 (LMPC Rules, 2011). It is not an automated judicial engine, an e-commerce web crawler, or a universal legal reasoning platform.
2. **The Six MVP Compliance Checks:** The MVP executes exactly six core checks:
   - Manufacturer / Packer / Importer Identity & Address (Rule 6(1)(a))
   - Common or Generic Commodity Name (Rule 6(1)(b))
   - Net Quantity + Standard Unit (Rule 6(1)(c) & Rules 11–13)
   - Month and Year of Manufacture / Packing / Import (Rule 6(1)(d))
   - Maximum Retail Price (MRP), inclusive of all taxes (Rule 6(1)(e))
   - Consumer Care Details (Rule 6(1)(e))
   *(Country of Origin under Rule 6(1)(da) is strictly applicability-driven; Unit Sale Price under Rule 6(1)(f) is a documented statutory gap with implementation phase TBD).*
3. **The Human-in-the-Loop Adjudication Boundary:**
   > **"PaddleOCR reads. Gemini understands. Backend validates. Applicability determines relevance. Rules evaluate. Evidence supports. Inspector verifies. Reviewer decides."**  
   > **"AI finds → Evidence proves → Officer decides."**  
   AI models assist solely in perception and semantic structuring; they never render legal verdicts.
4. **Deployable Architecture:** The MVP is engineered to be deployed on modern cloud infrastructure (containerized backend, persistent database, object storage for original evidence) so that team members, inspectors, and judges can access and test it. Local-only filesystems and machine-specific persistent state are prohibited for deployed environments. Puter is permanently excluded.
5. **Phase 0 Constraint:** This derivation does **NOT** authorize application coding or project scaffolding. Implementation remains locked until human approval of this derivation document.

---

## SECTION B: Approved Phase 0 Baseline

The following authoritative decisions established in the Phase 0 Legal Reconciliation Audit form the non-negotiable foundation of this MVP derivation:

| Baseline Dimension | Approved Phase 0 Ground Truth | MVP Architectural Requirement |
|---|---|---|
| **Result State Model** | Six authoritative states: `PASS`, `POTENTIAL_NON_COMPLIANCE`, `REQUIRES_REVIEW`, `NOT_APPLICABLE`, `INCOMPLETE`, `PROCESSING_FAILED`. (The 4-state vocabulary is retired). | The state machine, database entities, rule engine, and UI must exclusively use these 6 states. |
| **State Distinction Rules** | `NOT_APPLICABLE != PASS`<br>`INCOMPLETE != POTENTIAL_NON_COMPLIANCE`<br>`PROCESSING_FAILED != POTENTIAL_NON_COMPLIANCE`<br>`NOT_OBSERVED != missing`<br>`UNREADABLE != NOT_OBSERVED`<br>`CONFLICTING data -> REQUIRES_REVIEW` | Technical processing failures must never trigger legal non-compliance findings. |
| **Applicability Principle** | **"Applicability First"** — Package context and statutory relevance must be determined before rule evaluation. | The Applicability Engine executes prior to the Compliance Rules Engine. |
| **Country of Origin (COO)** | Rule 6(1)(da) applies strictly to imported commodities. Domestic products have no LMPC COO requirement (`NOT_APPLICABLE`). | Unknown import status must route to `REQUIRES_REVIEW` or `INCOMPLETE`; never assume domestic. |
| **Unit Sale Price (USP)** | G.S.R. 779(E) statutory requirement is documented as `DELTA-001`. Implementation phase is **TBD**. | **Strictly excluded from MVP.** No UI, no API, no DB fields, no rule logic, no tests. |
| **Deferred Capabilities** | 13 statutory provisions cataloged (`FUT-001` to `FUT-013`) are a reference backlog, not committed features. | Excluded from MVP scope (no e-commerce crawlers, no QR-code decoders, etc.). |
| **Evidence Model** | Strict hierarchy: Primary Evidence (original images) $\rightarrow$ Derived Evidence (crops, OCR tokens) $\rightarrow$ Inspection Record. | Original images are immutable; findings must trace to bounding box coordinates. |
| **Finalization Invariant** | Working inspection $\rightarrow$ Reviewer Approval $\rightarrow$ Sealed Read-Only Snapshot. | Finalized records are permanently immutable; subsequent changes require new inspection cases. |

---

## SECTION C: MVP Scope Boundary

The MVP is intentionally bounded to execute the core end-to-end inspection lifecycle for physical pre-packaged commodities:

```text
+---------------------------------------------------------------------------------------------------+
|                                       MVP SYSTEM BOUNDARY                                         |
|                                                                                                   |
|  [Product Package]                                                                                |
|         ↓                                                                                         |
|  1. EVIDENCE CAPTURE / UPLOAD (Front, Back, Side panel images, max 10MB, JPG/PNG)                 |
|         ↓                                                                                         |
|  2. IMAGE QUALITY CHECK (Blur, resolution, glare validation; fail-fast)                           |
|         ↓                                                                                         |
|  3. PERCEPTION & OCR (PaddleOCR: text extraction, spatial bounding boxes, confidence scores)      |
|         ↓                                                                                         |
|  4. DECLARATION STRUCTURING (Gemini 2.5 Flash: extracts structured fields; validates schema)      |
|         ↓                                                                                         |
|  5. APPLICABILITY ENGINE (Evaluates retail scope, domestic vs imported status, package thresholds)|
|         ↓                                                                                         |
|  6. DETERMINISTIC COMPLIANCE RULES (Pure functions: validates extracted data against 6 checks)   |
|         ↓                                                                                         |
|  7. FINDINGS & EVIDENCE ASSEMBLY (Binds rule evaluations to visual bounding boxes & confidence)   |
|         ↓                                                                                         |
|  8. INSPECTOR VERIFICATION (Human officer inspects, corrects OCR errors, reviews discrepancies)   |
|         ↓                                                                                         |
|  9. REVIEWER FINALIZATION (Senior officer reviews, signs off, generates immutable audit record)   |
|         ↓                                                                                         |
|  10. REPORT EXPORT & HISTORY (Inspection report generation, audit log storage, search/filtering)  |
+---------------------------------------------------------------------------------------------------+
```

---

## SECTION D: Explicit MVP Exclusions

To safeguard the engineering team against scope creep and maintain a clean, demonstrable system, the following capabilities are **explicitly excluded from the MVP**:

1. **No Universal E-Commerce Crawling:** No scraping of Amazon, Flipkart, or Blinkit; no automated digital catalog crawling. All inputs are inspector-uploaded image packages.
2. **No E-Commerce Sortable COO Verification:** While G.S.R. 128(E) / 312(E) mandate marketplace search filters, digital interface auditing is deferred (`FUT-002`).
3. **No Unit Sale Price (USP) Engine:** No price-per-gram or price-per-millilitre calculations; USP remains `DELTA-001` (Phase TBD).
4. **No Electronic QR Code Decoding:** Electronic product QR code extraction under G.S.R. 456(E) is deferred (`FUT-003`).
5. **No Multi-Piece / Combination Package Splitting:** Complex hierarchical packaging trees under G.S.R. 722(E) are deferred (`FUT-004`).
6. **No Government Prosecution / Court Litigation Workflow:** No compounding legal notices, summons generation, or judicial case tracking.
7. **No Generalized Legal RAG Engine:** The system does not dynamically query vector databases of case law or legal PDFs. Rules are deterministic compiled TypeScript/Python functions.
8. **No Complex Multi-Tenant Enterprise RBAC:** No hierarchical departmental org trees. The MVP uses a robust, simple two-role model: `INSPECTOR` and `REVIEWER` (with an administrative setup capability).
9. **No Puter.com Integration:** Puter has been permanently set aside.

---

## SECTION E: MVP Operational Workflow

The MVP replaces the over-complex 19-stage target workflow with an **8-Stage Operational Workflow**. Every stage defines clear actors, inputs, actions, failure behaviors, and state transitions.

```text
[Stage 1: Initialize] ──> [Stage 2: Upload Evidence] ──> [Stage 3: Perception & Extraction]
                                                                     │
[Stage 5: Deterministic Evaluation] <── [Stage 4: Applicability] <───┘
         │
         └──> [Stage 6: Inspector Verification] ──> [Stage 7: Reviewer Finalization] ──> [Stage 8: Report & History]
```

### Detailed Workflow Specification

| Stage # & Name | Primary Actor | Inputs | System Action | Primary Output | Failure Modes & Handling | Next State | Human Required? |
|---|---|---|---|---|---|---|---|
| **Stage 1: Initialization** | Inspector | Commodity Name (preliminary), Brand, Category, Packaging Type, Import Status (`DOMESTIC`, `IMPORTED`, `UNKNOWN`) | Creates new inspection instance in database; generates unique `inspection_id` (UUIDv4) and audit log record. | Initialized inspection record with assigned metadata | Validation error on missing mandatory fields $\rightarrow$ prompt inspector. | `DRAFT` | Yes (Form entry) |
| **Stage 2: Evidence Upload & Quality Gate** | Inspector | 1 to 5 package panel images (JPG/PNG, max 10MB per image) | Uploads images to persistent object storage; generates SHA-256 hashes; runs image quality checks (resolution, blur, aspect ratio). | Stored original image assets with cryptographic hashes; quality pass/warn record. | File invalid, corrupt, or below minimum quality threshold $\rightarrow$ reject image with specific user prompt. | `EVIDENCE_UPLOADED` | Yes (Image capture) |
| **Stage 3: Perception & Extraction** | System (PaddleOCR + Gemini) | Stored image assets | 1. PaddleOCR extracts text lines, spatial bounding boxes $(x_1, y_1, x_2, y_2)$, and confidence scores.<br>2. Gemini 2.5 Flash maps OCR tokens to structured declaration schema (Entity, Commodity, Net Qty, Date, MRP, Care).<br>3. Backend validates schema structure against TypeScript/Pydantic contracts. | Structured Declaration Model containing parsed values, bounding box references, and OCR confidence. | OCR service failure or Gemini timeout $\rightarrow$ transitions to `PROCESSING_FAILED`. Unreadable panel $\rightarrow$ flags field as `UNREADABLE`. | `EXTRACTED` | No (Automated pipeline) |
| **Stage 4: Applicability Determination** | System (Applicability Engine) | Inspection metadata (Import Status, Commodity Category, Net Quantity) | Evaluates statutory relevance for each of the six checks.<br>Evaluates Rule 6(1)(da) Country of Origin: if `IMPORTED` $\rightarrow$ applicable; if `DOMESTIC` $\rightarrow$ `NOT_APPLICABLE`; if `UNKNOWN` $\rightarrow$ routes to review. | Applicability Context Map detailing active rules and justification. | Missing critical metadata $\rightarrow$ flags applicability as `INCOMPLETE` and prompts inspector. | `APPLICABILITY_EVALUATED` | No (Automated rule) |
| **Stage 5: Deterministic Compliance Evaluation** | System (Rule Engine) | Structured Declaration Model + Applicability Context Map | Executes pure deterministic rule functions for each applicable check (regex, symbol matching, date validity, tax inclusion phrases). Evaluates evidence presence and quality. | Preliminary Compliance Findings set across the 6 checks with assigned states: `PASS`, `POTENTIAL_NON_COMPLIANCE`, `REQUIRES_REVIEW`, `NOT_APPLICABLE`. | Internal rule exception $\rightarrow$ transitions finding to `PROCESSING_FAILED`. Conflicting evidence $\rightarrow$ routes to `REQUIRES_REVIEW`. | `EVALUATED` | No (Pure functions) |
| **Stage 6: Inspector Verification & Adjustment** | Inspector | Preliminary Findings + Visual Overlay (images with highlighted bounding boxes) | Displays extracted declarations side-by-side with original image crops. Inspector verifies extracted text, corrects OCR misreads if necessary, provides context for unread fields, and adds field-level verification notes. | Verified Inspection Submission; record of any inspector overrides preserved in audit trail. | Inspector cannot read label $\rightarrow$ marks as `UNREADABLE`, routes to `POTENTIAL_NON_COMPLIANCE`. | `SUBMITTED_FOR_REVIEW` | **YES (Core Human Gate)** |
| **Stage 7: Official Review & Finalization** | Reviewer (Senior Officer) | Submitted Inspection Record, Inspector notes, visual evidence, audit diffs | Senior officer inspects verified findings and evidence; confirms or adjusts findings; signs off on formal compliance outcome; triggers cryptographic seal. | Finalized Inspection Record; status updated to `FINALIZED`; read-only lock applied. | Reviewer rejects verification $\rightarrow$ returns inspection to inspector with revision notes (`REQUIRES_REVISION`). | `FINALIZED` | **YES (Legal Decision Gate)** |
| **Stage 8: Report Export & Historical Archive** | Inspector / Reviewer | Finalized Inspection Record | Generates tamper-evident PDF inspection report containing package metadata, evidence image crops, findings table, officer signatures, and statutory citations. Stores in historical query index. | Downloadable PDF Inspection Certificate / Report; permanently searchable archive record. | PDF generation error $\rightarrow$ log error, retry background rendering. | `ARCHIVED` (Read-Only) | Optional (Export request) |

---

## SECTION F: MVP Actors and Responsibilities

The MVP eliminates complex multi-tier enterprise permissions in favor of a clean, secure **Two-Role Authorization Model** enforced authoritatively at the backend:

```text
+-----------------------+----------------------------------------------------------------------------------------+
| Role                  | Authorized Operations                                                                  |
+-----------------------+----------------------------------------------------------------------------------------+
| INSPECTOR             | - Create new inspection cases                                                          |
|                       | - Upload and delete draft evidence images                                              |
|                       | - Trigger OCR and structured extraction                                                |
|                       | - View preliminary findings and visual bounding boxes                                  |
|                       | - Correct OCR misreads (with mandatory audit logging of original vs edited values)    |
|                       | - Submit completed inspection to review queue                                          |
|                       | - Download draft and finalized reports                                                 |
+-----------------------+----------------------------------------------------------------------------------------+
| REVIEWER              | - Access all Inspector capabilities                                                    |
| (Senior Officer)      | - View submitted inspection queue across all inspectors                                |
|                       | - Adjudicate discrepancies and accept/override inspector notes                         |
|                       | - Issue formal final decision (`PASS`, `POTENTIAL_NON_COMPLIANCE`, `REQUIRES_REVIEW`)   |
|                       | - Apply permanent read-only cryptographic lock (`FINALIZED`)                           |
|                       | - Return inspection for rework (`REQUIRES_REVISION`)                                   |
|                       | - Generate official signed compliance certificates                                    |
+-----------------------+----------------------------------------------------------------------------------------+
| SYSTEM / ENGINE       | - Automated background tasks: quality gate, OCR, extraction, applicability, rule run   |
| (Service Worker)      | - Audit log generation, SHA-256 hash generation, PDF report compilation               |
+-----------------------+----------------------------------------------------------------------------------------+
```

---

## SECTION G: MVP Lifecycle State Model

To eliminate confusion between system processing, user workflows, and legal results, the MVP defines **four orthogonal state axes**:

```text
                              INSPECTION LIFECYCLE (Master State)
                                               │
           ┌───────────────────────────────────┼───────────────────────────────────┐
           ▼                                   ▼                                   ▼
   PROCESSING STATE                    COMPLIANCE RESULT                  FINALIZATION STATE
(IDLE, PROCESSING, FAILED)          (6 Authoritative States)             (UNFINALIZED vs READ-ONLY)
```

### 1. Master Inspection Lifecycle States
- `DRAFT`: Initial metadata entered; awaiting evidence upload.
- `EVIDENCE_UPLOADED`: Images uploaded and validated by quality gate.
- `EXTRACTED`: OCR and structured semantic extraction completed.
- `APPLICABILITY_EVALUATED`: Commodity scope and applicability context established.
- `EVALUATED`: Deterministic rules executed; preliminary findings assembled.
- `IN_VERIFICATION`: Inspector is reviewing declarations and bounding boxes.
- `SUBMITTED_FOR_REVIEW`: Inspector verified findings; queued for Senior Officer.
- `REQUIRES_REVISION`: Reviewer sent inspection back to inspector for additional evidence or correction.
- `FINALIZED`: Formal review complete; record sealed and locked read-only.

### 2. State Relationship Invariants
- An inspection in `EVIDENCE_UPLOADED` can have processing state `PROCESSING` while OCR runs.
- If processing throws an unhandled exception, processing state becomes `FAILED`, but lifecycle state transitions to a recoverable review state (`IN_VERIFICATION` with partial data), NOT a compliance failure.
- Individual check results do not overwrite the master lifecycle state.
- Once lifecycle state reaches `FINALIZED`, the Finalization State permanently locks to `READ_ONLY`.

---

## SECTION H: Compliance Result Model

Each of the six MVP checks evaluates to one of the **Six Authoritative Result States**:

```text
                               ┌─────────────┐
                               │  EVALUATION │
                               └──────┬──────┘
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
     [ PASS ]           [ POTENTIAL_NON_COMPLIANCE ]       [ REQUIRES_REVIEW ]
Evidence completely         Mandatory declaration             Ambiguous evidence,
satisfies rule             missing or invalid                conflicting reads, or
                                                             unclear applicability
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
  [ NOT_APPLICABLE ]             [ INCOMPLETE ]            [ PROCESSING_FAILED ]
Rule does not apply to       Required metadata missing        Technical exception
this package (e.g. COO       preventing evaluation           during OCR or parsing
for domestic)                (e.g. unknown import status)    (NEVER a legal breach)
```

### The Invariant Evaluation Matrix

| State | Statutory Meaning | System Trigger Condition | Can Officer Override? |
|---|---|---|---|
| `PASS` | Mandatory declaration is present, valid metric syntax confirmed, and all statutory conditions satisfied. | Rule predicate evaluates to true with high OCR/extraction confidence. | Yes (with justification note) |
| `POTENTIAL_NON_COMPLIANCE` | Evidence indicates a missing mandatory declaration, non-compliant unit, or invalid pricing syntax. | Deterministic check detects absence, invalid metric symbol, or missing tax clause. | Yes (Officer may locate declaration on label missed by OCR) |
| `REQUIRES_REVIEW` | Discrepancy, low optical confidence, ambiguous multi-channel consumer care, or conflicting text observed. | OCR confidence below threshold, or conflicting values detected across panels. | Yes (Officer resolves ambiguity) |
| `NOT_APPLICABLE` | The statutory requirement does not apply to this specific package type. | Package is domestic (Rule 6(1)(da) COO exempt) or falls under statutory exemption (Rule 3). | Yes (Officer can correct package classification) |
| `INCOMPLETE` | Statutory evaluation cannot proceed because essential context is missing. | Import status is `UNKNOWN`, or net quantity missing so unit check cannot run. | Yes (Officer supplies missing context) |
| `PROCESSING_FAILED` | Internal technical failure during execution. **Explicitly NOT a compliance violation.** | OCR service timeout, corrupted image processing, or model API disconnect. | Yes (Officer can trigger re-processing) |

---

## SECTION I: MVP Evidence Model

ComplianceScan treats visual evidence with legal-grade chain-of-custody integrity:

```text
+-------------------------------------------------------------------------------------------------+
|                                        EVIDENCE TIERS                                           |
|                                                                                                 |
|  [PRIMARY EVIDENCE] (Raw Uploaded Images)                                                       |
|  - Stored in persistent object storage (S3 / MinIO / Local Volume)                              |
|  - Cryptographically hashed with SHA-256 upon receipt                                           |
|  - WORM semantics (Write Once, Read Many); immutable; never resized, cropped, or overwritten    |
|                                                                                                 |
|  [DERIVED EVIDENCE] (Perception Outputs)                                                        |
|  - Normalized bounding boxes: [ymin, xmin, ymax, xmax] relative coordinates (0.0 to 1.0)        |
|  - Cropped declaration preview snippets for inspector verification UI                           |
|  - OCR text tokens with character-level and box-level confidence scores                         |
|  - Stored with explicit parent foreign key pointing to Primary Evidence ID                      |
|                                                                                                 |
|  [INSPECTION & DECISION RECORD] (Audit Record)                                                  |
|  - Extracted structured declaration payload                                                     |
|  - Record of any manual field adjustments by inspector (Original OCR value vs Corrected value) |
|  - Timestamp, officer ID, and digital signature of final sign-off                               |
+-------------------------------------------------------------------------------------------------+
```

### Traceability Mandate
Every finding generated by the system must satisfy the **Traceability Triple**:
$$\text{Finding} \longrightarrow \text{Rule Subclause} \longrightarrow \text{Derived Evidence (Bounding Box)} \longrightarrow \text{Primary Image SHA-256}$$
If an inspector clicks on "Maximum Retail Price" in the UI, the system must instantly highlight the exact physical crop on the primary image where the price was observed.

---

## SECTION J: MVP AI/OCR Pipeline

The perception pipeline is engineered with strict functional specialization:

```text
[ Raw Image ]
     │
     ▼
[ Preprocessing & Quality Gate ]
     │ - Grayscale / Contrast enhancement
     │ - Blur detection (Laplacian variance > 100)
     │ - Resolution verification (min 1024x768)
     ▼
[ PaddleOCR Engine ]
     │ - Text line detection & recognition
     │ - Outputs text strings + spatial bounding boxes + confidence (0.00 - 1.00)
     │ - Completely local / private execution; zero data leakage
     ▼
[ Gemini 2.5 Flash Structured Extractor ]
     │ - Prompted with strict JSON schema and OCR tokens
     │ - Extracts exactly 6 declaration domains
     │ - Preserves OCR token indices; forbidden from hallucinating missing data
     ▼
[ Backend Schema Validator ]
     │ - Pydantic / TypeScript runtime contract validation
     │ - Rejects malformed JSON; verifies bounding box coordinate ranges
     ▼
[ Applicability Engine & Deterministic Rule Engine ]
```

### Prohibitions on AI Behavior
1. **No Legal Hallucination:** Gemini is prompted strictly as a *structural parser*, not a legal advisor. Prompts contain zero instructions to determine guilt, violation, or legality.
2. **Missing Field Integrity:** If a date is absent from the OCR tokens, Gemini is instructed to return `null`. It is strictly forbidden from inferring current dates or typical manufacturing timelines.
3. **Traceability Preservation:** For every extracted string, Gemini must return the bounding box IDs of the source OCR tokens.

---

## SECTION K: MVP Applicability Model

ComplianceScan enforces the statutory principle: **"Applicability First"**.

```text
                                 [ Package Input ]
                                         │
                         Is package in scope of LMPC 2011?
                               (Weight <= 25kg/L, Retail)
```

---

## SECTION L: MVP Logical Architecture

The target architecture described in `Documentation/03_Architecture_v2.0.md` specified 25 granular components across multiple enterprise tiers. For the MVP, we merge components where separation creates unnecessary operational friction, while strictly maintaining separation where required for **security, determinism, testability, and legal provenance**.

The MVP derives **8 Cohesive Logical Components**:

```text
+---------------------------------------------------------------------------------------------------+
|                                     FRONTEND PRESENTATION TIER                                    |
|                                                                                                   |
|   [ 1. FRONTEND WEB CLIENT ] (React + Vite + Tailwind SPA)                                       |
|   ├── Inspection Dashboard & Case List                                                            |
|   ├── Evidence Upload & Quality Feedback                                                          |
|   ├── Side-by-Side Visual Verification Workspace (Image Overlay + Bounding Box Canvas)            |
|   └── Reviewer Adjudication & Report Viewer                                                       |
+---------------------------------------------------------------------------------------------------+
                                                │ HTTPS / REST JSON
                                                ▼
+---------------------------------------------------------------------------------------------------+
|                                      BACKEND APPLICATION TIER                                     |
|                                                                                                   |
|   [ 2. API GATEWAY & SESSION CONTROLLER ]                                                         |
|   ├── Authoritative RBAC Guard (Inspector vs Reviewer)                                            |
|   └── Input Validation & Rate Limiting                                                            |
|                                               │
|                                               ▼
|   [ 3. INSPECTION ORCHESTRATOR & STATE MACHINE ] ──────────────────────────────────────────────┐  |
|   ├── Manages 8 Lifecycle States (`DRAFT` → `FINALIZED`)                                       │  |
|   └── Dispatches Pipeline Steps & Emits Audit Events                                           │  |
|                                               │                                                │  |
|         ┌─────────────────────────────────────┼─────────────────────────────────────┐          │  |
|         ▼                                     ▼                                     ▼          │  |
|   [ 4. EVIDENCE STORE ]            [ 5. PERCEPTION ENGINE ]        [ 6. STRUCTURED EXTRACTOR ] │  |
|   ├── S3/Object Storage Adapter    ├── Image Quality Gate          ├── Gemini 2.5 Flash Client │  |
|   ├── SHA-256 Hash Verifier        └── PaddleOCR Worker            └── Schema Validation Guard │  |
|   └── WORM Storage Enforcer            (Spatial Bounding Boxes)        (Strict JSON Schema)    │  |
|                                               │                                     │          │  |
|                                               └──────────────────┬──────────────────┘          │  |
|                                                                  ▼                             │  |
|                                    [ 7. APPLICABILITY & DETERMINISTIC RULE ENGINE ]            │  |
|                                    ├── Applicability Filter (Rule 3 & COO Rule 6(1)(da))       │  |
|                                    └── Six Pure Deterministic Rule Evaluators (Zero AI)        │  |
|                                                                  │                             │  |
|                                                                  └─────────────────────────────┘  |
|                                                                  │
|                                                                  ▼
|   [ 8. REPORT GENERATOR & AUDIT STORE ]                                                           |
|   ├── Tamper-Evident SHA-256 Hash Chain                                                           |
|   └── PDF Inspection Certificate Builder                                                          |
+---------------------------------------------------------------------------------------------------+
                                                │
                                                ▼
+---------------------------------------------------------------------------------------------------+
|                                      PERSISTENT STORAGE TIER                                      |
|                                                                                                   |
|   [ RELATIONAL DATABASE ] (PostgreSQL / SQLite Dev)    [ OBJECT STORAGE ] (S3 / MinIO / Volume)   |
|   ├── Inspection Cases & State History                 └── Primary Original Images (Immutable)    |
|   ├── Extracted Declarations & Bounding Boxes                                                     |
|   └── Compliance Findings & Audit Records                                                         |
+---------------------------------------------------------------------------------------------------+
```

---

## SECTION M: Component Responsibilities & Inter-Component Contracts

| # | Component Name | Internal Responsibilities | Inbound Contract / Inputs | Outbound Contract / Outputs |
|---|---|---|---|---|
| **1** | **Frontend Web Client** | Single-page application; renders state-driven views; displays visual canvas overlay mapping bounding boxes over high-res images; collects inspector edits. | REST JSON payloads from API Gateway; pre-signed image asset URLs. | User input forms; image uploads; field corrections; sign-off commands. |
| **2** | **API Gateway & Auth** | Enforces session security; validates HTTP request schemas; enforces backend-authoritative role segregation (`INSPECTOR` vs `REVIEWER`). | HTTP REST requests from Client. | Authorized, validated internal command payloads forwarded to Orchestrator. |
| **3** | **Inspection Orchestrator** | Enforces the 8-stage lifecycle state machine; coordinates execution sequence; manages state transitions; records audit events. | State transition requests; inspection creation commands. | Lifecycle state updates; dispatches tasks to Evidence, Perception, and Rule services. |
| **4** | **Evidence Store** | Stores original package images with WORM (Write Once, Read Many) semantics; generates cryptographic SHA-256 hashes; serves secure access URLs. | Multi-part image file uploads (max 10MB, JPG/PNG). | `EvidenceAsset` record (UUID, SHA-256 hash, storage URI, MIME type, dimensions). |
| **5** | **Perception Engine** | Executes image preprocessing (Laplacian blur score, resolution check); runs PaddleOCR to detect text lines and spatial bounding boxes. | Raw image buffer / storage reference. | Array of `OcrToken` objects (text string, bounding box $[y_{\min}, x_{\min}, y_{\max}, x_{\max}]$, confidence score). |
| **6** | **Structured Extractor** | Sends OCR tokens to Gemini 2.5 Flash with strict JSON schema; maps recognized tokens to 6 declaration domains; validates schema adherence. | Array of `OcrToken` objects. | `StructuredDeclarations` payload with field values and referenced OCR token IDs. |
| **7** | **Applicability & Rule Engine** | Determines statutory relevance ("Applicability First"); executes 6 pure deterministic compliance functions (regex, standard units, date validation, tax phrase). | `StructuredDeclarations` + `ApplicabilityContext`. | Array of `ComplianceFinding` records with assigned authoritative states. |
| **8** | **Report & Audit Store** | Assembles audit records with SHA-256 hash chaining; builds immutable PDF inspection reports; enforces read-only freeze on finalized cases. | Finalized inspection payload and officer signatures. | Downloadable PDF Inspection Report; sealed audit log entries. |

---

## SECTION N: MVP Data Model

The MVP condenses the target system's dozens of entities down to **7 Conceptual Entities**:

```text
[ UserSession ]
      │ 1
      │
      ▼ *
[ InspectionCase ] 1 ─────── * [ EvidenceAsset ]
      │ 1                              │ 1
      │                                │
      ▼ 1                              ▼ *
[ ApplicabilityContext ]       [ DerivedOcrToken ]
      │ 1                              │
      │                                │
      ▼ 1                              ▼ *
[ ExtractedDeclaration ] 1 ─── * [ ComplianceFinding ]
      │ 1
      │
      ▼ 1
[ FinalAuditRecord ]
```

### Entity Specifications

1. **`UserSession`** (Persistent)
   - *Purpose:* Identity, role assignment, and session tracking.
   - *Key Fields:* `user_id` (UUID), `username`, `full_name`, `role` (`INSPECTOR` \| `REVIEWER`), `department`, `created_at`.
   - *Legal/Compliance State:* Tracks authorized officer identity for audit logging.

2. **`InspectionCase`** (Persistent, Master Entity)
   - *Purpose:* Root aggregate for a physical commodity inspection.
   - *Key Fields:* `inspection_id` (UUIDv4), `case_number` (human-readable), `commodity_name`, `brand_name`, `category`, `packaging_type`, `import_status` (`DOMESTIC` \| `IMPORTED` \| `UNKNOWN`), `lifecycle_state` (`DRAFT` ... `FINALIZED`), `processing_state` (`IDLE` \| `PROCESSING` \| `FAILED`), `final_compliance_result` (Nullable 6-state enum), `created_by` (FK User), `assigned_reviewer` (FK User), `created_at`, `updated_at`.
   - *Legal/Compliance State:* Master lifecycle and overall compliance determination.

3. **`EvidenceAsset`** (Persistent, Immutable)
   - *Purpose:* Primary visual evidence uploaded from physical packaging.
   - *Key Fields:* `asset_id` (UUID), `inspection_id` (FK), `panel_type` (`FRONT` \| `BACK` \| `SIDE_LEFT` \| `SIDE_RIGHT` \| `TOP` \| `BOTTOM`), `file_path_or_key`, `file_name`, `file_size_bytes`, `mime_type`, `sha256_hash`, `image_width`, `image_height`, `quality_status` (`PASS` \| `WARN` \| `FAIL`), `quality_details` (JSON), `uploaded_at`.
   - *Legal/Compliance State:* Primary chain of custody; SHA-256 immutable evidence.

4. **`DerivedOcrToken`** (Persistent, Derived Evidence)
   - *Purpose:* Spatial text tokens generated by PaddleOCR.
   - *Key Fields:* `token_id` (UUID), `asset_id` (FK), `text`, `confidence` (float 0–1), `bounding_box` (JSON: $[y_{\min}, x_{\min}, y_{\max}, x_{\max}]$ normalized coordinates), `line_number`.

5. **`ExtractedDeclaration`** (Persistent, Versioned)
   - *Purpose:* Structured commodity declarations parsed by Gemini and adjusted by inspector.
   - *Key Fields:* `declaration_id` (UUID), `inspection_id` (FK), `field_name` (`MANUFACTURER` \| `COMMODITY_NAME` \| `NET_QUANTITY` \| `MFR_DATE` \| `MRP` \| `CONSUMER_CARE` \| `COO`), `raw_ocr_value`, `extracted_value`, `is_manually_edited` (bool), `edited_value`, `referenced_token_ids` (JSON array), `confidence` (float).
   - *Legal/Compliance State:* Preserves exact audit trail between raw OCR, AI parsing, and human corrections.

6. **`ApplicabilityContext`** (Persistent)
   - *Purpose:* Statutory eligibility record under LMPC Rules, 2011.
   - *Key Fields:* `context_id` (UUID), `inspection_id` (FK), `is_retail_package` (bool), `is_imported` (bool), `weight_exceeds_threshold` (bool), `coo_applicable` (bool), `evaluation_rationale` (text).

7. **`ComplianceFinding`** (Persistent)
   - *Purpose:* Result of deterministic rule execution for each check.
   - *Key Fields:* `finding_id` (UUID), `inspection_id` (FK), `rule_code` (`RULE_6_1_A` through `RULE_6_1_DA`), `check_name`, `result_state` (`PASS` \| `POTENTIAL_NON_COMPLIANCE` \| `REQUIRES_REVIEW` \| `NOT_APPLICABLE` \| `INCOMPLETE` \| `PROCESSING_FAILED`), `statutory_citation` (e.g. "Rule 6(1)(a), LMPC Rules, 2011"), `failure_reason` (nullable text), `inspector_note` (nullable text), `reviewer_override_state` (nullable enum), `reviewer_note` (nullable text), `referenced_asset_id` (FK), `referenced_box` (JSON).

8. **`FinalAuditRecord`** (Persistent, Cryptographically Sealed)
   - *Purpose:* Immutable final snapshot generated upon Reviewer approval.
   - *Key Fields:* `audit_id` (UUID), `inspection_id` (FK), `sealed_at`, `reviewer_id` (FK), `final_decision_state`, `tamper_evident_hash` (SHA-256 of entire inspection snapshot), `report_pdf_key`, `is_read_only` (bool = true).

---

## SECTION O: MVP API Boundary

The MVP exposes a focused, RESTful JSON API surface across **8 Logical Resource Groups**:

```text
/api/v1
├── /auth               (Session & Identity)
├── /inspections        (Case Lifecycle CRUD)
├── /evidence           (Image Upload & Quality)
├── /extraction         (Trigger OCR & Gemini Parsing)
├── /rules              (Applicability & Rule Execution)
├── /verification       (Inspector Field Adjustments)
├── /review             (Senior Officer Finalization)
└── /reports            (PDF Certificate & Audit Export)
```

### Route Inventory

1. **Authentication & Session (`/auth`)**
   - `POST /auth/login` — Authenticate inspector/reviewer; issues secure JWT session.
   - `GET /auth/me` — Returns current authenticated user and role profile.

2. **Inspection Case Management (`/inspections`)**
   - `POST /inspections` — Initialize new inspection (`DRAFT`).
   - `GET /inspections` — Query inspection list with filtering (status, date, commodity).
   - `GET /inspections/{id}` — Get complete inspection aggregate (assets, findings, state).
   - `DELETE /inspections/{id}` — Delete draft inspection (only permitted in `DRAFT`).

3. **Evidence Upload & Management (`/evidence`)**
   - `POST /inspections/{id}/evidence` — Upload packaging panel image (validates MIME, runs quality check, stores asset, returns SHA-256).
   - `GET /inspections/{id}/evidence/{asset_id}` — Retrieve asset metadata and secure viewing URL.
   - `DELETE /inspections/{id}/evidence/{asset_id}` — Remove uploaded asset (permitted prior to verification).

4. **Perception & Structured Extraction (`/extraction`)**
   - `POST /inspections/{id}/extract` — Trigger background PaddleOCR and Gemini extraction pipeline.
   - `GET /inspections/{id}/extraction-status` — Poll extraction processing state (`IDLE`, `PROCESSING`, `FAILED`, `COMPLETED`).
   - `GET /inspections/{id}/declarations` — Retrieve extracted declarations with bounding box references.

5. **Compliance Rules & Findings (`/rules`)**
   - `POST /inspections/{id}/evaluate` — Execute Applicability Engine and Deterministic Rule Engine.
   - `GET /inspections/{id}/findings` — Retrieve findings for all 6 MVP compliance checks.

6. **Inspector Verification (`/verification`)**
   - `PATCH /inspections/{id}/declarations/{field_id}` — Inspector corrects misread text or updates declaration.
   - `POST /inspections/{id}/submit` — Inspector submits verified inspection to Senior Reviewer queue (`SUBMITTED_FOR_REVIEW`).

7. **Senior Officer Review & Finalization (`/review`)**
   - `GET /review/queue` — Query pending submitted inspections across all inspectors.
   - `POST /inspections/{id}/adjudicate` — Reviewer approves or overrides findings; adds adjudication rationale.
   - `POST /inspections/{id}/finalize` — Seals inspection; generates cryptographic hash; locks record as `FINALIZED`.
   - `POST /inspections/{id}/reject` — Returns inspection to inspector for revision (`REQUIRES_REVISION`).

8. **Reports & Audit Archive (`/reports`)**
   - `GET /inspections/{id}/report.pdf` — Generates and downloads official PDF Inspection Certificate.
   - `GET /inspections/{id}/audit-trail` — Retrieves tamper-evident chronological event log.

---

## SECTION P: MVP UI Boundary

The frontend SPA implements **9 Dedicated Screen Views** supporting the end-to-end inspection workflow:

```text
[ 1. Dashboard ] ──> [ 2. Inspection List ] ──> [ 3. New Inspection Modal ]
                                                         │
[ 5. Analysis Workspace ] <── [ 4. Evidence Upload ] <───┘
         │
         ├──> [ 6. Inspector Verification Screen ] ──> (Submit to Queue)
         │                                                    │
         ▼                                                    ▼
[ 8. Final Report Screen ] <── [ 7. Reviewer Adjudication ] <─┘
         │
         └──> [ 9. Historical Archive Detail ]
```

### Screen Inventory & Responsibilities
1. **Screen 1: Dashboard (`/`)**
   - Overview metrics: total inspections, pending verifications, queued reviews, compliance rates.
   - Quick action: "Start New Inspection".
2. **Screen 2: Inspection Case List (`/inspections`)**
   - Searchable, sortable table of inspection cases.
   - Filters: Status (`DRAFT`, `EVALUATED`, `FINALIZED`), Compliance State, Date, Brand.
3. **Screen 3: New Inspection Modal (`/inspections/new`)**
   - Form capturing preliminary metadata: Commodity Name, Brand, Category, Packaging Type, Import Status (`DOMESTIC` / `IMPORTED` / `UNKNOWN`).
4. **Screen 4: Evidence Upload & Quality Gate (`/inspections/:id/upload`)**
   - Drag-and-drop zone for 1–5 package panels (Front, Back, Sides, Top, Bottom).
   - Real-time client-side image preview and server-side quality feedback (blur/resolution alerts).
5. **Screen 5: Extraction & Visual Analysis Workspace (`/inspections/:id/workspace`)**
   - Interactive dual-pane layout:
     - Left pane: High-resolution image canvas with pan/zoom and SVG bounding box overlays.
     - Right pane: Extraction card deck displaying the 6 declarations with confidence badges.
   - Clicking an extraction card automatically pans the canvas and highlights the source bounding box.
6. **Screen 6: Inspector Verification Screen (`/inspections/:id/verify`)**
   - Side-by-side comparison of raw OCR text vs Gemini structured extraction.
   - Inline edit mode allowing inspector to correct OCR misreads with mandatory reason entry.
   - Button: "Submit for Official Review".
7. **Screen 7: Senior Reviewer Adjudication Screen (`/review/:id`)**
   - Reviewer-only interface showing inspector notes, preliminary findings, and visual evidence.
   - Adjudication panel permitting confirmation or override of individual check states.
   - Action buttons: "Approve & Finalize Inspection" or "Return for Revision".
8. **Screen 8: Final Result & Certificate Screen (`/inspections/:id/result`)**
   - Executive summary card displaying overall compliance status and the 6 check cards.
   - "Download Official PDF Certificate" button.
9. **Screen 9: Historical Archive & Audit Detail (`/history/:id`)**
   - Read-only historical viewer showing permanent audit trail, SHA-256 hashes, and timestamped officer actions.

---

## SECTION Q: Security Boundary

The MVP enforces security at the architectural boundary, avoiding complex enterprise infrastructure while guaranteeing integrity:

1. **Authoritative Backend RBAC:**
   - All state transitions and role checks are validated on the server.
   - The frontend role profile is purely for UI rendering; unauthorized API calls return HTTP 403 Forbidden.
2. **File Upload Hardening:**
   - Maximum upload size capped at 10MB per file.
   - Allowed MIME types strictly restricted to `image/jpeg` and `image/png`.
   - Magic byte validation: Backend verifies the file header signature on the server to prevent malicious executable masquerading.
   - Files are stored with randomly generated UUID keys, completely detached from user-provided filenames.
3. **API & Secrets Isolation:**
   - The Gemini API key and database credentials exist exclusively in server-side environment variables (`.env`).
   - The frontend never has access to LLM API keys or direct database handles.
4. **Tamper-Evident Hash Chaining:**
   - Every primary evidence image is hashed with SHA-256 upon initial receipt.
   - When an inspection is finalized, a cryptographic digest of the entire inspection record (metadata, findings, inspector edits, reviewer signature) is stored in `FinalAuditRecord`.
5. **Read-Only Finalization Lock:**
   - Once an inspection reaches `FINALIZED`, the database repository rejects any `UPDATE` or `DELETE` operations on that inspection and its child records. Any subsequent enforcement action requires opening a distinct new inspection case.

---

## SECTION R: Deployment Architecture

The MVP is engineered for straightforward, reproducible cloud deployment:

```text
                                     [ INTERNET ]
                                          │
                                          ▼ HTTPS (Port 443)
                         [ Reverse Proxy / Cloud Gateway ]
                         (Nginx / Caddy / Cloudflare)
                                          │
                    ┌─────────────────────┴─────────────────────┐
                    ▼                                           ▼
      [ Static Frontend SPA ]                     [ Backend API Service ]
      (Vite build served via                      (FastAPI Container / Gunicorn)
       Nginx or Cloudflare Pages)                               │
                                            ┌───────────────────┼───────────────────┐
                                            ▼                   ▼                   ▼
                                    [ Relational DB ]   [ Object Storage ]   [ Gemini API ]
                                    (PostgreSQL)        (S3 / MinIO)         (Google Cloud)
```

### Deployment Guidelines
1. **Containerized Execution:** Backend packaged as a standard Docker image containing Python, FastAPI, and PaddleOCR dependencies.
2. **Persistent Storage:**
   - Production relational database: Hosted PostgreSQL (e.g. AWS RDS, Supabase, Neon, or containerized PostgreSQL with volume persistence).
   - Production object storage: S3-compatible cloud storage (AWS S3, Cloudflare R2, or MinIO) for uploaded package images.
   - Development mode: SQLite with WAL mode enabled and local filesystem volume storage, switched seamlessly via storage abstraction interface.
3. **Cloud-Agnostic Design:** The architecture avoids vendor lock-in. No AWS-specific SDKs are hardcoded; standard S3 protocol and PostgreSQL connections are used.
4. **Permanent Exclusion of Puter:** Puter is not deployed, referenced, or imported.

---

## SECTION S: Performance & Processing Model

The MVP balances responsive inspector interactions with heavy AI/OCR computing:

```text
[ Inspector Action: Upload Image ]
          │ (Synchronous HTTP 201)
          ▼
   Asset Stored & Hash Generated (< 500ms)
          │
[ Inspector Action: Click "Run Extraction" ]
          │ (HTTP 202 Accepted)
          ▼
[ Background Processing Queue / Task Worker ]
   ├── Step 1: Preprocessing & Quality Check (~300ms)
   ├── Step 2: PaddleOCR Inference (~1.5s - 3.5s depending on CPU/GPU)
   ├── Step 3: Gemini 2.5 Flash Structured Parse (~1.2s - 2.0s via API)
   ├── Step 4: Schema Validation (< 50ms)
   └── Step 5: Applicability & Deterministic Rule Evaluation (< 20ms)
          │
          ▼
   Inspection State updated to `EVALUATED` (Total latency: ~3 - 6 seconds)
          │
[ Client Polling or WebSocket Update ]
          ▼
   Canvas & Extraction Cards Rendered on Inspector Workspace
```

### Performance Invariants
1. **No Redundant OCR:** OCR tokens are computed exactly once per uploaded asset and persisted in `DerivedOcrToken`. Re-running compliance rules never re-invokes OCR or Gemini.
2. **Deterministic Rules Execute Instantly:** The 6 compliance rules are pure in-memory functions executing in $< 20\text{ ms}$, ensuring zero UI lag during manual inspector adjustments.
3. **Bounded Execution Timeouts:** Gemini API calls are bounded by an 8-second HTTP timeout. If Gemini times out, the system fails gracefully to `PROCESSING_FAILED`, allowing manual retry or direct inspector entry.

---

## SECTION T: Error and Recovery Model

ComplianceScan enforces a strict taxonomy of failures, ensuring that technical glitches or data ambiguities are never misrepresented as legal non-compliance:

```text
                                  [ SYSTEM DISCREPANCY DETECTED ]
                                                 │
            ┌────────────────────────────────────┼────────────────────────────────────┐
            ▼                                    ▼                                    ▼
    [ TECHNICAL ERROR ]                 [ AMBIGUOUS EVIDENCE ]              [ COMPLIANCE DEFECT ]
    - Image corrupt                     - OCR confidence < 0.6               - Missing Mandatory Field
    - PaddleOCR timeout                 - Conflicting values on pack         - Non-standard unit ("gms")
    - Gemini API 500                    - Unclear import status              - Missing tax phrase
            │                                    │                                    │
            ▼                                    ▼                                    ▼
  `PROCESSING_FAILED`                 `REQUIRES_REVIEW` or                 `POTENTIAL_NON_COMPLIANCE`
  (Retry available;                     `INCOMPLETE`                       (Flagged for human
   NEVER a legal breach)               (Human input requested)             inspector verification)
```

### Detailed Failure Taxonomy & Recovery Matrix

| Failure Classification | Concrete Example | Assigned State | System Behavior & Recovery Path |
|---|---|---|---|
| **Input Validation Error** | Uploaded file is a `.pdf` or corrupted image. | HTTP 400 Bad Request | Request rejected immediately at API Gateway; user prompted to upload valid JPG/PNG. |
| **Perception Processing Failure** | PaddleOCR container runs out of memory or crashes. | `PROCESSING_FAILED` | Error logged; inspection marked `PROCESSING_FAILED`; user provided with "Retry Analysis" button. |
| **Extraction Model Timeout** | Gemini API network drop or rate limit exceeded. | `PROCESSING_FAILED` | Exponential backoff retry (up to 2 attempts); if unresolved, marked `PROCESSING_FAILED`. |
| **Insufficient Evidence** | Package back panel missing; only front panel uploaded. | `INCOMPLETE` / `REQUIRES_REVIEW` | System evaluates visible front panel declarations; flags missing declarations as unobserved; prompts inspector to upload remaining panels. |
| **Uncertain / Low-Confidence Read** | Smudged expiry date yielding 0.35 OCR confidence. | `REQUIRES_REVIEW` | Declaration displayed with warning badge; inspector prompted to visually confirm or correct text. |
| **Conflicting Label Declarations** | Front panel states "500g", but back panel states "450g". | `REQUIRES_REVIEW` | System flags conflicting values; displays both crops; officer adjudicates true net quantity. |
| **Statutory Compliance Discrepancy** | MRP declared as "MRP Rs 150" without "(incl. of all taxes)". | `POTENTIAL_NON_COMPLIANCE` | Rule 6(1)(e) check fails; finding recorded with exact statutory citation; highlighted for review. |

---

## SECTION U: Testing Strategy & Release Gate

Testing for the MVP is structured across **5 Concentric Verification Layers** directly mapped to `Documentation/11_Testing_and_Release_Gate.md`:

```text
[ Layer 5: Release Gate Verification ] (End-to-End Golden Dataset, 0 Regressions)
       ▲
[ Layer 4: State Machine & Workflow Integration ] (Lifecycle transitions, Read-only lock)
       ▲
[ Layer 3: Perception & Extraction Pipeline ] (Mocked OCR/Gemini fixtures, Schema guards)
       ▲
[ Layer 2: Applicability Engine Tests ] (Retail scope, Domestic vs Imported matrix)
       ▲
[ Layer 1: Pure Deterministic Rule Unit Tests ] (Regex, Metric units, Tax phrases, Edge cases)
```

### Layer Details for Phase 1 Implementation
1. **Layer 1: Deterministic Compliance Rule Unit Tests (Target: 100% Coverage)**
   - Test suites for each of the 6 rules against valid, invalid, boundary, and edge-case declaration strings.
   - Zero external dependencies; execution time $< 100\text{ ms}$.
2. **Layer 2: Applicability Matrix Tests (Target: 100% Coverage)**
   - Exhaustive truth table tests verifying that domestic products return `NOT_APPLICABLE` for COO, imported return active, and unknown route to review.
3. **Layer 3: Perception & Extraction Mock Suites**
   - Fixture-based tests feeding pre-recorded PaddleOCR tokens and Gemini JSON payloads to verify schema validation and error handling without incurring live API costs.
4. **Layer 4: State Transition & Immutability Integration Tests**
   - Verifies that unauthorized state jumps (e.g. `DRAFT` $\rightarrow$ `FINALIZED`) are rejected.
   - Verifies that finalized inspections reject all mutation attempts.
5. **Layer 5: Golden Package Regression Suite (Release Gate)**
   - 20 synthetic/sample packaging ground-truth test cases evaluated end-to-end to verify zero false positives on known compliant packages.

---

## SECTION V: Target Architecture → MVP Mapping

The following comprehensive table maps all 25 components from the target system (`Documentation/03_Architecture_v2.0.md`) to their concrete MVP decisions:

| Target Component | Target Tier | MVP Decision | Concrete Architectural Handling in MVP |
|---|---|---|---|
| `C-01: Ingestion Gateway` | Ingestion | **MVP** | Retained as part of Component 2 (`API Gateway & Session Controller`). |
| `C-02: Quality Gate Service` | Ingestion | **MVP** | Retained as internal module inside Component 5 (`Perception Engine`). |
| `C-03: Image Preprocessor` | Ingestion | **MVP** | Absorbed into Component 5 (`Perception Engine`) for contrast/grayscale normalization. |
| `C-04: PaddleOCR Service` | OCR / Perception | **MVP** | Retained as core worker in Component 5 (`Perception Engine`). |
| `C-05: Vision-LLM Extractor` | Semantic Extraction | **MVP** | Retained as Component 6 (`Structured Extractor`, Gemini 2.5 Flash). |
| `C-06: Barcode/QR Engine` | Perception | **DEFERRED** | Excluded from MVP (`FUT-003`, `FUT-010`). Physical text only. |
| `C-07: Normalization Engine` | Semantic Extraction | **ABSORBED** | Merged into Component 6 (`Structured Extractor`) schema validation layer. |
| `C-08: Field Aggregator` | Semantic Extraction | **ABSORBED** | Merged into Component 6 (`Structured Extractor`) multi-panel aggregator. |
| `C-09: Applicability Engine` | Compliance Rules | **MVP** | Retained as standalone evaluator in Component 7 (`Applicability & Rule Engine`). |
| `C-10: Rule Evaluator Core` | Compliance Rules | **MVP** | Retained as pure functions in Component 7 (`Applicability & Rule Engine`). |
| `C-11: Metric Unit Validator` | Compliance Rules | **ABSORBED** | Merged into Component 7 as sub-rule for Rule 6(1)(c). |
| `C-12: Date/Timeline Engine` | Compliance Rules | **ABSORBED** | Merged into Component 7 as sub-rule for Rule 6(1)(d). |
| `C-13: MRP & Tax Evaluator` | Compliance Rules | **ABSORBED** | Merged into Component 7 as sub-rule for Rule 6(1)(e). |
| `C-14: Consumer Care Validator` | Compliance Rules | **ABSORBED** | Merged into Component 7 as sub-rule for Rule 6(1)(e). |
| `C-15: COO Evaluator` | Compliance Rules | **ABSORBED** | Merged into Component 7 as sub-rule for Rule 6(1)(da). |
| `C-16: USP Calculator` | Compliance Rules | **DEFERRED** | Strictly excluded from MVP (`DELTA-001`). Phase TBD. |
| `C-17: Findings Assembler` | Adjudication | **ABSORBED** | Merged into Component 3 (`Inspection Orchestrator`). |
| `C-18: Confidence Scorer` | Adjudication | **ABSORBED** | Merged into Component 6 & 7 as attribute on findings. |
| `C-19: Audit Trail Logger` | Audit & Security | **MVP** | Retained in Component 8 (`Report Generator & Audit Store`). |
| `C-20: Cryptographic Notary` | Audit & Security | **ABSORBED** | Merged into Component 8 as SHA-256 hash sealing module. |
| `C-21: Case State Machine` | Workflow Orchestration | **MVP** | Retained as core engine in Component 3 (`Inspection Orchestrator`). |
| `C-22: Web Dashboard UI` | Presentation | **MVP** | Retained as Component 1 (`Frontend Web Client`). |
| `C-23: Verification Workspace` | Presentation | **MVP** | Retained as interactive canvas view in Component 1. |
| `C-24: Report Generator (PDF)` | Reporting | **MVP** | Retained in Component 8 (`Report Generator & Audit Store`). |
| `C-25: E-Commerce Crawler` | External Integration | **EXCLUDED** | Out of scope for physical packaged commodities. |

*Summary:* The 25 target components are condensed into **8 robust, cohesive logical components** for the MVP. Zero core principles are compromised; dozens of redundant network boundaries and microservice overheads are eliminated.

---

## SECTION W: Deferred Capabilities Register

The statutory backlog cataloged during the Phase 0 audit is officially recorded as deferred from the MVP:

| Code | Provision / Capability | Statutory Source | Reason for Deferral from MVP |
|---|---|---|---|
| **FUT-001** | Unit Sale Price (USP) Engine | Rule 6(1)(f), G.S.R. 779(E) | Documented statutory gap (`DELTA-001`); implementation phase TBD. |
| **FUT-002** | E-Commerce Sortable COO Filter Auditing | Rule 6(10A), G.S.R. 128(E) / 312(E) | Applies to digital marketplace platforms, not physical retail label verification. |
| **FUT-003** | Electronic Product QR Code Validation | Rule 6(4), G.S.R. 456(E) | Requires camera QR scanning and external web fetching; deferred to Phase 2. |
| **FUT-004** | Multi-Piece & Combination Package Trees | Rule 2(aa),(da),(hc), G.S.R. 722(E) | Complex multi-item hierarchy; MVP focuses on single-commodity retail packs. |
| **FUT-005** | Edible Oil Temperature-Density SOP | SOP dt. 29-12-2023 | Specialized laboratory testing protocol; out of scope for visual label verification. |
| **FUT-006** | Readymade Garment Specific Tag Rules | G.S.R. 858(E) (2022) | Specialized garment dimension declarations; deferred to Phase 2. |
| **FUT-007** | Medical Device MDR 2017 Routing | G.S.R. 778(E) (2025) | Excluded from LMPC Chapter II; routed to specialized CDSCO rules. |
| **FUT-008** | Small Package (<= 10g/ml) Special Rules | Rule 26(a) | Requires display outer carton verification; deferred to Phase 2. |
| **FUT-009** | Institutional / Wholesale Package Rules | Rule 3, Chapter III | Excluded from standard retail package scope; returns `NOT_APPLICABLE`. |
| **FUT-010** | Dual Labelling Penalty / Barcode Scanning | G.S.R. 629(E) | Barcode cross-referencing deferred to Phase 3. |

---

## SECTION X: Open Architecture Decisions & Technology Evaluation

| Stack Dimension | Current Working Direction | Evaluation & Status | Agent Recommendation |
|---|---|---|---|
| **Frontend Framework** | React 18 + Vite + Tailwind CSS | Excellent developer velocity, rich UI capabilities, high performance, light bundle. | **Maintain working direction.** |
| **Backend Framework** | Python 3.11+ with FastAPI | Native integration with PaddleOCR (Python-based), Pydantic validation, async execution, auto OpenAPI docs. | **Maintain working direction.** (Eliminates inter-process Python/Node bridge). |
| **OCR Engine** | PaddleOCR (Local CPU/GPU) | High accuracy on multilingual Indian packaging text, zero per-page API cost, fully private. | **Maintain working direction.** |
| **LLM Model** | Gemini 2.5 Flash | High structured extraction accuracy, native JSON schema support, low latency ($< 1.5\text{s}$), very low cost. | **Maintain working direction.** |
| **Database** | PostgreSQL (Prod) / SQLite (Dev) | PostgreSQL provides robust JSONB support for bounding boxes and relational integrity for audit trails. | **Use PostgreSQL for deployed MVP; SQLite with WAL mode for local dev.** |
| **Object Storage** | S3-Compatible Storage | AWS S3, Cloudflare R2, or self-hosted MinIO. Provides standard WORM image storage. | **Use S3-compatible abstraction layer with local disk adapter.** |
| **Deployment Target** | Docker Container on Cloud VM / Managed Service | Simple single-container or two-container compose (API + Web) deployed on AWS/Render/DigitalOcean. | **Standard Docker Compose architecture.** |

*(Puter is permanently excluded. No local-only proprietary cloud lock-in).*

---

## SECTION Y: Implementation Phase Breakdown

The build sequence for the MVP is strictly ordered by dependency layers:

```text
[ Phase 1: Foundation & Contracts ]
  - Initialize clean repository structure (Frontend + Backend)
  - Define shared TypeScript / Pydantic domain models & 6-state enums
  - Set up PostgreSQL / SQLite database migrations
          │
          ▼
[ Phase 2: Deterministic Rule Engine & Applicability (Core Kernel) ]
  - Implement pure rule functions for all 6 MVP checks
  - Implement Applicability Engine (Rule 3, COO Rule 6(1)(da))
  - Build comprehensive unit test suite (100% coverage target)
          │
          ▼
[ Phase 3: Evidence Store & Perception Pipeline ]
  - Build Evidence upload service with SHA-256 hashing and quality gate
  - Integrate PaddleOCR worker for text detection and bounding boxes
  - Integrate Gemini 2.5 Flash client with strict schema validation
          │
          ▼
[ Phase 4: State Machine & Backend API ]
  - Implement 8-stage Inspection Orchestrator
  - Build REST API endpoints (`/inspections`, `/evidence`, `/extraction`, `/rules`, `/verify`, `/review`)
  - Implement backend-authoritative RBAC guard
          │
          ▼
[ Phase 5: Frontend SPA Implementation ]
  - Build 9 screen views (Dashboard, Upload, Dual-pane Canvas, Verify, Review, Report)
  - Implement interactive SVG bounding box highlight canvas
  - Wire frontend API client with session management
          │
          ▼
[ Phase 6: Report Generation & Finalization ]
  - Implement PDF Inspection Certificate builder
  - Implement cryptographic audit seal and read-only finalization lockdown
          │
          ▼
[ Phase 7: Testing, Release Gate & Deployment ]
  - Execute 20-case golden dataset regression suite (`11_Testing_and_Release_Gate.md`)
  - Build production Docker containers
  - Deploy to cloud staging environment; conduct live end-to-end verification
```

---

## SECTION Z: Risks and Trade-offs

1. **Perception Latency vs Resource Footprint:**
   - *Risk:* PaddleOCR running on standard CPU instances takes 2–4 seconds per image.
   - *Mitigation:* Decouple image upload from extraction via background worker; provide real-time frontend status spinner.
2. **LLM Non-Determinism Guarding:**
   - *Risk:* Gemini might occasionally omit an unread field or format dates inconsistently.
   - *Mitigation:* Strict Pydantic runtime validation; Gemini outputs are strictly treated as *preliminary proposals*; mandatory human inspector verification before any review submission.
3. **Cylindrical / Wrinkled Packaging Distortion:**
   - *Risk:* Curved cans or crumpled pouches produce fragmented OCR lines.
   - *Mitigation:* Image Quality Gate warns on poor capture; inspector verification UI allows single-click OCR text correction with mandatory audit logging.
4. **Cloud Infrastructure Cost:**
   - *Risk:* Continuous cloud database and GPU instances incur monthly costs.
   - *Mitigation:* Lightweight CPU-optimized PaddleOCR model (`ch_PP-OCRv4_server` or `mobile`); lightweight PostgreSQL; deployment on cost-effective managed containers (e.g. Render, Railway, or AWS EC2).

---

## SECTION AA: Agent-Proposed Better Approach

### Proposal 1: Unified Python FastAPI Monolith for Backend (PROPOSAL — REQUIRES HUMAN APPROVAL)
- **Current Assumption:** Some earlier documents suggested a Node.js/TypeScript backend or splitting OCR into a separate microservice.
- **Proposed Alternative:** Build the backend as a single unified **Python 3.11+ FastAPI service** hosting both the API orchestrator and the PaddleOCR/Gemini workers.
- **Why it is Better:** PaddleOCR is natively written and optimized in Python. A unified Python backend eliminates the need for complex inter-process gRPC or HTTP network hops between a Node.js API server and a Python OCR daemon, drastically simplifying deployment, local testing, and debugging.
- **Advantages:** Single backend container; shared Pydantic data models; native Python typing; zero inter-service serialization overhead; fastest path to a robust MVP.
- **Disadvantages:** Backend is Python rather than TypeScript. (Frontend remains modern React + TypeScript).
- **Effect on MVP Scope:** None. Reduces implementation complexity by ~35%.
- **Status:** **PROPOSAL — AWAITING HUMAN REVIEW AND APPROVAL.**

---

## SECTION BB: Final Gate Checkpoint & Stop Condition

### Stop Condition Verification
In accordance with the prompt instructions:
- **No application code has been written.**
- **No package directories have been created.**
- **No database schemas or migrations have been initialized.**
- **No specifications in `Documentation/` or `MVP_BUILD_SCOPE_v2.0.md` have been modified.**
- **The Phase 0 boundary is strictly respected.**

The MVP Operational Workflow and System Architecture Derivation is **COMPLETE** and submitted for formal human review.

