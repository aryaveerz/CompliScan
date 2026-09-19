# CompliScan LM — MVP Implementation Specification

**Project:** CompliScan LM
**SIH Problem Statement:** PS ID 26034
**Status:** FINAL — CONTROLLING IMPLEMENTATION SPECIFICATION
**Version:** 1.0
**Date:** 2026-09-16

This document converts the locked architecture, resolved decisions, requirement-complete MVP proposal, and Antigravity review into an implementation contract.

> **Implementation rule:** build what is specified. Do not silently redesign, expand scope, or give AI authority that this specification does not grant.

---

# 1. Decision & Review Basis

This specification preserves all previously locked architecture decisions and the seven resolved review decisions:

- M-01 — PostgreSQL-backed durable analysis job queue using Supabase PostgreSQL.
- M-02 — Inspector vs Reviewer correction boundary.
- P-01 — Shared domain package between backend and worker.
- P-02 — Durable worker queue/communication mechanism.
- P-03 — Explicit correction command model.
- P-04 — `FinalAuditRecord` as immutable point-in-time snapshot.
- P-05 — Field-level Gemini output validation.

### Antigravity review incorporated

The requirement-complete MVP was reviewed by Antigravity on 2026-09-16 with the verdict:

**APPROVED WITH TARGETED ADJUSTMENTS**

The review found no blocking architecture revision and assessed the requirement coverage as near-complete. It specifically validated the evidence-aware missing logic, bounded font-size screening, bounded placement screening, physical/online input modes, evidence-linked findings, PDF + DOCX reporting, repository/history, dashboard, RBAC, and deterministic rule evaluation.

The four targeted adjustments are incorporated as follows:

1. **Product Context Form — FINAL:** Product Name + Origin Status, with optional Category/Reference/Notes. Origin Status feeds applicability; Category is metadata only in MVP.
2. **Controlled Format Anomaly Checklist — FINAL:** finite, deterministic checks; no open-ended AI “misleading label” detector.
3. **`docxtpl` — APPROVED FOR PHASE 5:** templated editable DOCX generated from `FinalAuditRecord`.
4. **Frontend Canvas Overlay — APPROVED FOR PHASE 2:** stored OCR bounding boxes rendered over the untouched original evidence.

Antigravity also identified implementation risks to respect: safe PostgreSQL job claiming, conservative downstream invalidation, OCR model packaging/cold-start handling, and protection of finalized snapshots.

---

# 2. Product Objective & Core Promise

CompliScan LM is a web-based inspection-assistance system for packaged-commodity labels and product information within an approved, controlled MVP legal scope.

Core workflow:

```text
SCAN
  ↓
UNDERSTAND
  ↓
DETERMINE APPLICABILITY
  ↓
VALIDATE
  ↓
PROVE WITH EVIDENCE
  ↓
INSPECTOR VERIFIES
  ↓
REVIEWER DECIDES
  ↓
FINALIZE
  ↓
REPORT + HISTORY
```

Core principle:

> **AI finds → Evidence proves → Officer decides.**

The system is not an autonomous legal enforcement system.

---

# 3. MVP Scope & Explicit Exclusions

### Supported input

**Mode A — Physical package:** photographs of front/rear/side/top/bottom/close-up or supplemental evidence.

**Mode B — Online listing:** manually supplied screenshot, product image, or product-information capture. An optional URL/reference is metadata only. The MVP does **not** fetch or crawl URLs.

### Explicitly excluded

- Native Android/iOS applications.
- Web crawler or automatic e-commerce scraping.
- Universal Legal Metrology coverage.
- Dynamic legal-rule update pipeline.
- Rule Manager UI/operational role.
- Broad category-specific legal engine.
- USP check.
- Unit Sale Price as a universal MVP check.
- Autonomous AI legal decision.
- Automatic enforcement action.
- Exact physical font-size measurement from an unscaled image.
- Universal packaging-layout legal interpretation.
- Open-ended AI “misleading label” judgement.
- Microservices.
- Redis/ARQ requirement for MVP.
- Enterprise workflow bloat.
- Any unapproved feature.

Any excluded capability requires explicit human scope approval.

---

# 4. Core Compliance Scope

The six core deterministic domains are:

1. **Manufacturer / Packer / Importer identity and address**
2. **Common / Generic Product Name**
3. **Net Quantity + Standard Unit**
4. **Month / Year of Manufacture / Packing / Import**
5. **MRP inclusive of all taxes**
6. **Consumer Care Details**

### Country of Origin

Country of Origin is applicability-driven, not a seventh universal check:

```text
Imported  → COO applicable
Domestic  → NOT_APPLICABLE
Unknown   → REVIEW / INCOMPLETE as appropriate
```

The Inspector supplies Origin Status. AI may provide supporting observations but must not silently override Inspector context.

### Product Category

Product Category is metadata only in MVP. It must not automatically select a new category-specific legal rule set.

---

# 5. Product Context

Create Inspection must collect:

- Product Name — required.
- Origin Status — required: `DOMESTIC`, `IMPORTED`, `UNKNOWN`.
- Product Category — optional metadata.
- Reference / URL — optional metadata; never fetched by MVP.
- Inspector Notes — optional.

Origin Status is an explicit applicability input rather than a fact that Gemini must infer from a photograph.

---

# 6. Result Vocabulary & Semantics

Use exactly:

```text
PASS
POTENTIAL_NON_COMPLIANCE
REQUIRES_REVIEW
NOT_APPLICABLE
INCOMPLETE
PROCESSING_FAILED
```

Definitions:

- **PASS:** applicable requirement is supported as satisfied by sufficient evidence.
- **POTENTIAL_NON_COMPLIANCE:** deterministic evaluation identifies a potential non-compliant condition with sufficient supporting evidence.
- **REQUIRES_REVIEW:** ambiguity, conflict, visual limitation, uncertainty, or another condition prevents safe definitive evaluation.
- **NOT_APPLICABLE:** requirement does not apply.
- **INCOMPLETE:** evidence/information is insufficient to complete assessment.
- **PROCESSING_FAILED:** technical processing failed.

Mandatory distinctions:

```text
NOT_OBSERVED ≠ MISSING
UNREADABLE ≠ MISSING
INSUFFICIENT_EVIDENCE ≠ NON_COMPLIANCE
PROCESSING_FAILED ≠ NON_COMPLIANCE
NOT_APPLICABLE ≠ PASS
```

Also keep separate:

```text
OCR confidence
AI extraction confidence
Evidence sufficiency
Compliance result
```

---

# 7. Operational Workflow & States

### Eight lifecycle stages

```text
1. INITIALIZE
      ↓
2. CAPTURE EVIDENCE
      ↓
3. ANALYZE
   ├── Image Quality
   ├── OCR
   └── Structured Extraction
      ↓
4. DETERMINE APPLICABILITY
      ↓
5. EVALUATE COMPLIANCE
      ↓
6. INSPECTOR VERIFICATION
      ↓
7. REVIEWER DECISION
      ↓
8. FINALIZE
```

After finalization:

```text
FINALIZED
 ├── PDF
 ├── DOCX
 ├── HISTORY / AUDIT
 ├── SEARCH
 └── DASHBOARD
```

### Master lifecycle

`DRAFT → EVIDENCE_UPLOADED → EXTRACTED → APPLICABILITY_EVALUATED → EVALUATED → IN_VERIFICATION → SUBMITTED_FOR_REVIEW → REQUIRES_REVISION → FINALIZED`

### Processing state

`IDLE | PROCESSING | FAILED`

### Finalization

`UNFINALIZED | READ_ONLY`

The backend is authoritative for all transitions. Frontend state is never authoritative.

---

# 8. Global Invalidation Invariant

Any upstream correction must invalidate affected downstream state and recompute it.

```text
Upstream correction
      ↓
Identify affected downstream state
      ↓
Invalidate stale state
      ↓
Recompute
      ↓
Preserve previous state/history
      ↓
Audit transition
```

For MVP, conservative invalidation of applicability/evaluation is acceptable.

Example: correcting an extracted declaration after verification makes the previous verification stale and requires re-verification.

---

# 9. Roles & RBAC

Operational roles:

- `INSPECTOR`
- `REVIEWER`

### Inspector

Can create inspections, enter context, upload/accept evidence, initiate analysis, view OCR/declarations/findings, correct extracted declarations, add observations, verify, respond to evidence requests, and submit.

Cannot finalize, change legal rules, delete accepted primary evidence, mutate finalized records, alter audit history, or approve their own final decision.

### Reviewer

Can access the review queue, inspect evidence/OCR/declarations/applicability/findings/history, confirm findings, override with reason, request revision, request evidence, and finalize.

Cannot modify legal rules, silently rewrite extraction, delete finalized history, or review their own submission.

```text
Inspection
 ├── Underlying Data → Inspector
 └── Assessment/Decision → Reviewer
```

The backend enforces these permissions. The UI is not a security boundary.

---

# 10. Evidence Lifecycle & Integrity

```text
DRAFT UPLOAD
    ↓
PRIMARY EVIDENCE
    ↓
DERIVED EVIDENCE
    ↓
INSPECTION RECORD
    ↓
IMMUTABLE FINAL SNAPSHOT
```

Draft uploads may be removed/replaced before acceptance.

Accepted primary evidence is immutable. New evidence gets a new Evidence ID, SHA-256, metadata, and audit event.

Derived evidence includes OCR tokens, bounding boxes, crops, and highlights and must reference source evidence.

SHA-256 provides tamper-evident integrity/change detection. It does not prove factual truth or authenticity.

Evidence handling requires authentication, authorization, MIME/size/decode validation, secure storage, server-generated IDs, hashing, and audit events.

---

# 11. Perception: Image Quality & PaddleOCR

### Image quality

Assess resolution, blur, brightness/contrast, text visibility, severe cropping, orientation, and related engineering quality signals.

* **Canonical Configuration:** Threshold defaults live in `shared/domain/constants.py`, with optional environment overrides in `backend/app/core/config.py`.
* **Decoupled Quality Status:** Image quality outputs `QualityStatus` (`SUFFICIENT`, `DEGRADED`, `UNUSABLE`) and `ImageQualityAssessment`. Poor image quality indicates perception readability, NOT a compliance failure or missing declaration (`ComplianceResult`).

### PaddleOCR Perception Pipeline

PaddleOCR is perception-only.

* **Engine & Runtime:** Uses `rapidocr-onnxruntime` (ONNX runtime execution of PP-OCRv4 models), selected for verified compatibility with Python 3.14 on Windows and zero C++ compile overhead.
* **Output Structure (`OcrResult`):**
  - Raw detected text lines and concatenated text block.
  - Token list (`tokens`) containing `text`, `confidence` (float 0.0-1.0), and 4-point bounding box (`bbox: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]`).
  - Metadata: `processing_version` (e.g. `rapidocr_ppocrv4_v1`), execution time, engine specs.
* **Idempotency & Deduplication:** Persisted in `ocr_results` with `UNIQUE(evidence_id, processing_version)` constraint.

PaddleOCR must not make legal decisions.

OCR bounding boxes are persisted as `DerivedOcrToken` / `ocr_results` data.

---

# 12. Visual Highlighting

Preferred implementation:

```text
Original Image
      +
Stored OCR Bounding Boxes
      ↓
Frontend Canvas Overlay
```

The original evidence image must never be modified to create highlights.

The UI should support:

- OCR regions,
- selected declaration,
- finding-linked regions,
- evidence highlighting.

This is a Phase 2 acceptance requirement.

---

# 13. Semantic Extraction: Gemini

Use Gemini 2.5 Flash for semantic extraction/structuring.

```text
OCR observations
      ↓
Gemini
      ↓
Structured extraction
      ↓
Field-level validation
      ↓
Validated observations
```

Gemini must not:

- make final legal decisions,
- replace deterministic rules,
- invent values,
- silently resolve conflicts,
- infer unsupported facts.

If evidence is uncertain, absent, unreadable, or conflicting, preserve that condition.

---

# 14. Field-Level AI Validation

Validate every structured Gemini response for:

- schema structure,
- required fields,
- data types,
- formats,
- source traceability,
- missing/malformed/unsupported values,
- uncertainty,
- conflicts.

Validation failure is an analysis/data-quality issue, not automatically a compliance violation.

---

# 15. Applicability Engine

Applicability runs before compliance evaluation.

```text
Validated Observations
       +
Product Context
       ↓
Applicability
       ↓
Applicable Requirements
       ↓
Deterministic Evaluation
```

The engine must persist applicability context and relevant rule/version information.

Do not infer broad category-specific law in MVP.

---

# 16. Deterministic Compliance Engine

The backend is the compliance evaluation authority.

Each of the six domains has a separate deterministic evaluator.

```text
Validated observation
      +
Applicability
      +
Controlled rule/version
      ↓
Evaluator
      ↓
Finding
```

LLM output cannot override deterministic evaluation.

---

# 17. Evidence-Aware Missing Logic

A field is not “missing” merely because OCR/Gemini did not find it.

Example:

```text
No MRP detected
      ↓
Is relevant image area readable?
  ├── No → UNREADABLE / REVIEW
  └── Yes
       ↓
Is relevant package area sufficiently captured?
  ├── No → INSUFFICIENT_EVIDENCE
  └── Yes
       ↓
    MISSING
```

This distinction is a core product invariant.

---

# 18. Readability, Font Size & Placement

### Readability

Use image-quality and OCR-derived signals as screening indicators. Do not treat OCR confidence alone as a legal readability threshold.

### Font-size

Use bounding-box/text height for screening or relative estimation.

If no physical scale is available:

```text
UNABLE TO ESTABLISH PRECISE PHYSICAL SIZE
```

Never assume DPI or fabricate millimetres.

### Placement

Use detected bounding-box region and, where available, Inspector-tagged package face/configured expected region.

Unexpected placement may become `REQUIRES_REVIEW`.

Do not claim universal legal verification of packaging layout.

---

# 19. Controlled Format Anomaly Checklist

The MVP anomaly engine is finite and controlled:

1. MRP representation anomaly
2. Quantity-unit anomaly
3. Date representation anomaly
4. Consumer-care representation anomaly
5. Conflicting extracted values
6. Ambiguous extracted values
7. Unsupported declaration format

An anomaly normally produces:

`REQUIRES_REVIEW`

unless an explicitly controlled deterministic rule establishes another result.

Do not build an open-ended AI “misleading label detector”.

---

# 20. Findings & Evidence Traceability

Every finding should explain:

- what was evaluated,
- what was observed,
- what condition/rule was applied,
- why the result occurred,
- supporting evidence,
- limitations/confidence where relevant.

Traceability:

```text
Finding
  ↓
Rule / reason
  ↓
Observed declaration
  ↓
OCR token
  ↓
Bounding box
  ↓
Derived evidence
  ↓
Original evidence
```

The UI must distinguish AI observations, system findings, Inspector corrections/verification, Reviewer decisions, and final outcome.

---

# 21. Human Workflow

### Inspector correction

Conceptual command:

```text
CorrectDeclaration
├── inspection_id
├── declaration_id
├── old_value
├── new_value
├── reason
├── source_evidence_id
└── actor
```

Also persist timestamp/version as required.

Correction triggers affected downstream invalidation/recomputation and re-verification.

### Reviewer determination

```text
ReviewerDetermination
├── finding_id
├── decision
├── reason
├── evidence_reference
├── actor
└── timestamp
```

Actions:

`CONFIRM | OVERRIDE | REQUEST_REVISION | REQUEST_EVIDENCE`

Overrides require a reason.

### Evidence request

Use an Evidence Request ID such as `ER-00017` and state what fact/condition must be established. Do not force a fixed photograph count.

---

# 22. Finalization & FinalAuditRecord

Finalization is atomic.

```text
Reviewed inspection
      ↓
FinalAuditRecord
      ↓
Immutable
      ↓
READ_ONLY
```

The snapshot must contain/reference:

- inspection identity,
- finalized evidence,
- declarations,
- applicability,
- findings,
- reviewer determinations,
- final outcome,
- reviewer identity,
- timestamp,
- relevant rule/version references,
- integrity references.

Difference:

```text
AuditEvent = What happened?
FinalAuditRecord = What was final?
```

Reports are generated from the FinalAuditRecord. They must not rerun AI or compliance evaluation after finalization.

---

# 23. Durable Analysis Queue & Worker

Target architecture:

```text
FastAPI
   ↓
Supabase PostgreSQL
   ↓
analysis_jobs
   ↓
Worker
 ├── PaddleOCR
 └── Gemini
   ↓
PostgreSQL results
```

Job states:

`QUEUED | PROCESSING | COMPLETED | FAILED`

Requirements:

- durable job IDs,
- atomic claim,
- no duplicate ownership,
- bounded retries,
- lease/timeout recovery,
- idempotency,
- backpressure,
- observable failures.

PostgreSQL row locking such as `FOR UPDATE SKIP LOCKED` may be used for safe claiming.

Do not use FastAPI BackgroundTasks as the durable job mechanism.

Redis/ARQ is not required for MVP.

---

# 24. Shared Domain Package

```text
CompliScan/
├── backend/
├── worker/
└── shared/
    └── domain/
        ├── states
        ├── enums
        ├── schemas
        ├── domain types
        └── constants
```

Shared domain contains contracts, not duplicated business authority.

Do not put FastAPI routes, auth middleware, repositories, OCR runtime, Gemini runtime, or deployment configuration in the shared package.

---

# 25. Technology Stack

```text
Frontend: React + TypeScript + Vite + Tailwind CSS
Backend: Python 3.11+ + FastAPI
Database: PostgreSQL
Platform: Supabase
Storage: Supabase Storage
Authentication: Supabase Auth
OCR: PaddleOCR
LLM: Gemini 2.5 Flash
ORM: SQLAlchemy
Migrations: Alembic
Containers: Docker
Processing: Separate Worker
PDF: WeasyPrint
DOCX: docxtpl + Jinja2
```

Architecture boundary:

```text
React → FastAPI → Supabase
                  ↑
                Worker
```

Frontend does not directly manipulate domain inspection data.

---

# 26. Domain Data Model

Nine conceptual entities:

1. `User`
2. `InspectionCase`
3. `EvidenceAsset`
4. `DerivedOcrToken`
5. `ExtractedDeclaration`
6. `ApplicabilityContext`
7. `ComplianceFinding`
8. `FinalAuditRecord`
9. `AuditEvent`

`InspectionCase` is the root aggregate.

Avoid competing mutable final-result stores.

---

# 27. API Boundary

API root:

`/api/v1`

Logical groups:

```text
/auth
/inspections
/evidence
/analysis
/findings
/verification
/review
/reports
/audit
```

Backend is authoritative for:

- auth validation,
- RBAC,
- lifecycle,
- evidence operations,
- applicability,
- compliance evaluation,
- review,
- finalization.

Analysis may return `202 Accepted` with a durable job ID in the worker architecture.

Evidence acceptance must be explicit. Only draft evidence is removable.

Corrections are commands, not silent mutation.

Finalized records are read-only.

Audit is read-only.

---

# 28. UI Routes & Behavior

Routes:

```text
/dashboard
/inspections
/inspections/new
/inspections/:id
/inspections/:id/verify
/inspections/:id/result
/inspections/:id/history
/review/:id
```

Inspector:

```text
Dashboard → Inspections → Create → Context → Evidence/Analysis → Verification → Submit
```

Reviewer:

```text
Review Queue → Reviewer Workspace → Decision → Finalize
```

After finalization:

```text
Result → PDF / DOCX / History
```

Responsive web is sufficient; native mobile is out of scope.

---

# 29. Reporting, Repository, Search & Dashboard

### PDF

Include inspection identity, context, evidence summary, declarations, applicability, findings, results, evidence references, reviewer decision, and finalization information.

### DOCX

Editable equivalent of the finalized report using `docxtpl`.

### Repository

Search/filter by at least:

- inspection ID,
- product name,
- status,
- result,
- date.

### History

Show lifecycle, evidence, analysis, corrections, verification, review, requests, and finalization events.

### Dashboard

Use real stored data, not mock counters. Metrics may include total, in-progress, submitted, finalized, potential non-compliance, review, and incomplete cases.

Visibility is role-scoped:
- Inspector → own inspections.
- Reviewer → permitted review queue/cases.

---

# 30. Security Requirements

Minimum controls:

- authenticated API access,
- backend RBAC,
- object-level authorization,
- Inspector/Reviewer separation,
- secure evidence handling,
- MIME/size/decode validation,
- accepted-evidence immutability,
- SHA-256,
- append-only audit behavior,
- finalized read-only behavior,
- secret management,
- secure error handling,
- no client-trusted authorization.

Never hardcode API keys, credentials, access tokens, or passwords.

Use environment/configuration management.

---

# 31. Legal Scope & Provenance

The runtime rule engine uses the approved controlled Legal Metrology rule snapshot.

The downloaded official legal references are provenance/research material; they are not all automatically runtime rules.

Preserve relevant rule/version/effective-date information.

Do not dynamically scrape legal rules.

Do not claim universal legal coverage.

The system must distinguish technical processing limitations from legal conclusions.

---

# 32. Reporting Language & Safety

Preferred language:

- Potential Non-Compliance
- Requires Review
- Not Applicable
- Incomplete Evidence
- Unable to Establish

Avoid wording that says AI itself has legally determined guilt, illegality, or enforcement action.

The product is an inspection-assistance system.

---

# 33. Implementation Phases

## Phase 0 — Repository Audit

No implementation.

Inspect the existing repository and produce an audit covering:

- current frontend/backend,
- database artifacts,
- auth,
- reusable code,
- obsolete/conflicting code,
- configuration/secrets risks,
- mapping to this specification.

**STOP after audit.**

## Phase 1 — Foundation

Build project structure, shared domain, React/FastAPI/Supabase foundation, Auth/RBAC, Product Context, inspection creation, evidence lifecycle, migrations, basic UI.

Golden path:

`Login → Create Inspection → Product Context → Upload Evidence → View Inspection`

## Phase 2 — Perception

Image validation, quality, PaddleOCR, OCR persistence, bounding boxes, derived evidence, canvas overlay.

Golden path:

`Image → Quality → OCR → Tokens + Boxes → Visual Highlight`

## Phase 3 — Extraction + Compliance

Gemini, field validation, applicability, six evaluators, evidence-aware missing logic, readability, font-size screening, placement screening, controlled anomaly checks, evidence-linked findings.

## Phase 4 — Human Workflow

Inspector corrections, invalidation/recomputation, verification, submission, Reviewer queue/workspace, determinations, evidence requests, revision cycle, finalization.

## Phase 5 — Reports + Repository

FinalAuditRecord, PDF, DOCX/docxtpl, repository, search/filter, history, dashboard.

## Phase 6 — Hardening

Security, authorization, evidence integrity, state-transition tests, queue/retry reliability, failure handling, Docker/deployment, performance, demo hardening.

---

# 34. Testing Requirements

### Unit

Test validators, applicability, six evaluators, anomaly checks, state transitions, and result semantics.

### Integration

Test FastAPI/PostgreSQL, evidence lifecycle, analysis jobs, OCR persistence, extraction, corrections, review, finalization.

### Authorization

Test cross-inspection access, Inspector restrictions, Reviewer restrictions, self-review denial, finalization permissions, finalized mutation denial.

### Evidence

Test MIME/size/decode validation, hashing, immutability, draft replacement, derived linkage.

### Reports

Test PDF/DOCX generation and snapshot consistency.

---

# 35. Critical Acceptance Tests

1. OCR failure → `PROCESSING_FAILED`, not non-compliance.
2. Unreadable MRP → unreadable/review, not automatically missing.
3. Missing relevant image area → insufficient evidence.
4. Clear absence with sufficient evidence → missing finding.
5. Inspector correction → old/new preserved, recompute, audit, re-verification.
6. Reviewer override → reason + actor + timestamp.
7. Finalization → snapshot + read-only + mutation denial.
8. Submitting Inspector cannot be Reviewer.
9. Accepted primary evidence cannot be modified/deleted.
10. Finalized report derives from FinalAuditRecord.

---

# 36. SIH Requirement Coverage

| Requirement | MVP implementation |
|---|---|
| Scan package images | Physical evidence upload |
| Product information | Product Context + extracted declarations |
| Online product information | Screenshot/product-image evidence |
| Mandatory declarations | OCR + semantic extraction |
| Automated extraction | PaddleOCR + Gemini |
| Correctness | Deterministic evaluators |
| Completeness | Evidence-aware evaluation |
| Missing declarations | Evidence-aware logic |
| Placement | Bounded placement screening |
| Readability | Image/OCR screening |
| Font size | Bounded screening/estimation |
| Non-standard declarations | Controlled anomaly checks |
| Supporting evidence | Evidence assets + traceability |
| Reports | PDF + editable DOCX |
| Violation summary | Findings/result view |
| Repository/history | Search + audit/history |
| Dashboard | Real stored-data metrics |
| Web/mobile accessibility | Responsive web |
| RBAC/security | Inspector/Reviewer + backend enforcement |
| Rule-based checking | Deterministic rule engine |
| Technical documentation | Architecture + implementation specification |

---

# 37. Antigravity Implementation Protocol

Antigravity must work phase-by-phase.

### Before coding a phase

- inspect relevant existing code,
- confirm current phase scope,
- identify conflicts,
- identify dependencies.

### During coding

- implement only the approved phase,
- preserve locked decisions,
- write tests,
- avoid unrelated refactors.

### If uncertain

```text
Uncertainty
  ↓
Explain issue
  ↓
Propose options
  ↓
Human decision
```

Do not guess.

### If architecture improvement is discovered

Do not silently replace an approved decision. Document:

- current decision,
- problem,
- proposed change,
- impact,
- reason.

Wait for human approval.

The previous architecture review is complete. Do not restart a broad architecture review unless a real blocking implementation issue appears.

---

# 38. No-Silent-Feature-Creep Rules

Do not add features because they “would be useful”.

In particular, do not add:

- crawler,
- native mobile app,
- admin/rule-management UI,
- universal legal engine,
- dynamic legal update system,
- USP,
- category-specific rules,
- autonomous AI legal decision,
- microservices,
- Redis/ARQ,
- enterprise workflow,
- unrelated analytics.

Feature requests outside this specification must go through change control.

---

# 39. Change Control

Every proposed change is classified as:

```text
BUG FIX
IMPLEMENTATION DETAIL
SCOPE CHANGE
ARCHITECTURE CHANGE
LEGAL/RULE CHANGE
```

Implementation details may be resolved within the locked architecture.

Scope, architecture, and legal/rule changes require explicit human approval and, where material, an updated specification.

No silent changes.

---

# 40. Golden Demo

The demo should use prepared evidence that visibly exercises:

- clear declarations,
- missing/absent declaration,
- unreadable/ambiguous area,
- format anomaly,
- placement screening,
- font-size screening,
- Inspector correction,
- Reviewer decision,
- finalization,
- PDF,
- DOCX,
- search/history,
- dashboard.

The target demonstration is the complete chain:

```text
Physical / Online Evidence
        ↓
Image Quality
        ↓
PaddleOCR
        ↓
OCR Bounding Boxes
        ↓
Gemini Structured Extraction
        ↓
Field-Level Validation
        ↓
Applicability
        ↓
Six Deterministic Checks
        ↓
Readability
        ↓
Font-Size Screening
        ↓
Placement Screening
        ↓
Format Anomaly Checks
        ↓
Evidence-Linked Findings
        ↓
Inspector Correction / Verification
        ↓
Reviewer Decision
        ↓
Immutable FinalAuditRecord
        ↓
PDF + DOCX
        ↓
History + Search + Dashboard
```

---

# 41. Phase Sign-Off Gate

No phase is complete because code exists.

Required:

```text
Implementation
    ↓
Automated Tests
    ↓
Manual Acceptance
    ↓
Human Review
    ↓
Phase Sign-Off
    ↓
Next Phase
```

A failed phase must be fixed before downstream implementation continues.

---

# 42. Final Status & Immediate Next Action

```text
Architecture                         LOCKED
Requirement-complete MVP             APPROVED
Antigravity review                   COMPLETE
Product Context                      FINAL
Format Anomaly Scope                 FINAL
DOCX / docxtpl                       APPROVED FOR PHASE 5
Canvas Overlay                       APPROVED FOR PHASE 2

Implementation Specification         FINAL
Implementation                        NOT YET STARTED

NEXT ACTION                           PHASE 0 REPOSITORY AUDIT
```

**Phase 0 must audit the existing repository before implementation begins.**

Antigravity must not modify the repository during the audit unless explicitly authorized after the audit.

---

# 43. Closing Invariants

> **Build what is specified.**
>
> **Do not silently invent what is not specified.**
>
> **AI observes. Rules evaluate. Evidence supports. Humans decide.**
>
> **Every correction preserves history.**
>
> **Every final decision becomes an immutable snapshot.**
