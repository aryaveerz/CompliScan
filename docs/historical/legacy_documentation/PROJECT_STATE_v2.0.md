# PROJECT STATE

**Project:** ComplianceScan
**SIH'26 Problem Statement:** 26034
**Problem:** Software System to check compliance of Packaged Commodities under Legal Metrology (Packaged Commodities) Rules, 2011 by scanning products, images and labels.
**Last Updated:** 2026-09-19
**Current Phase:** Phase 2.1 Complete | Phase 2.2 Planned

---

# 1. Purpose

`PROJECT_STATE.md` is the living record of the **actual state of the ComplianceScan implementation**.

It exists to answer:

- What has been decided?
- What is currently in scope?
- What is the target system?
- What is actually implemented?
- What is verified?
- What remains unverified?
- What is deferred?
- What is blocked?
- What should happen next?

This document must describe reality, not intention.

The implementation agent must not treat the target architecture or specification documents as proof that functionality already exists.

---

# 2. Current Project Position

The project has completed a major scope-control and architecture-alignment decision.

The team has deliberately separated:

```text
TARGET / FULL SYSTEM
        │
        │ reference architecture + future capabilities
        ▼
CURRENT ONE-DAY MVP
        │
        │ controlled implementation subset
        ▼
ACTUAL IMPLEMENTATION STATE
```

The project is **not** attempting to implement the complete target system in one day.

The current objective is:

> **Build one complete, reliable, deployable vertical slice of the packaged-commodity inspection workflow.**

The target architecture remains valid and is **not being replaced** by a separate "small MVP architecture."

---

# 3. Current Strategic Decision

The following strategic decision is locked:

> **ONE COMPLETE USER JOURNEY > MANY PARTIAL SUBSYSTEMS**

The MVP must demonstrate a coherent flow from evidence input through analysis, applicability, compliance evaluation, evidence-backed findings, Inspector verification, result generation, persistence, and deployment/demo readiness.

The agent must not spend the remaining implementation time building disconnected target-system features.

---

# 4. Core Product Principle

The project is governed by:

> **AI finds → Evidence proves → Officer decides.**

The system is an inspection-assistance tool.

It does not autonomously make the final legal determination.

The intended responsibility split is:

```text
PaddleOCR
    ↓
Reads

Gemini 2.5 Flash
    ↓
Understands

Backend
    ↓
Validates

Applicability Engine
    ↓
Determines relevance

Compliance Rules
    ↓
Evaluate

Evidence System
    ↓
Supports

Inspector
    ↓
Verifies

Reviewer
    ↓
Decides
```

---

# 5. SIH Context

### Organization

Ministry of Consumer Affairs, Food & Public Distribution

### Department

Department of Consumer Affairs (DoCA)

### Category

Software

### Theme

Miscellaneous

### Problem Statement

Software system to check compliance of packaged commodities under the Legal Metrology (Packaged Commodities) Rules, 2011 through product/image/label scanning and automated extraction/validation.

The project aims to demonstrate a practical inspection-assistance workflow rather than claim complete statutory enforcement automation.

---

# 6. Current MVP Objective

The one-day MVP must establish this vertical slice:

```text
Representative Package Image
        ↓
Image Input
        ↓
Image Processing / Quality
        ↓
PaddleOCR
        ↓
OCR Text + Bounding Boxes + Confidence
        ↓
Gemini 2.5 Flash
        ↓
Structured Declarations
        ↓
Backend Validation
        ↓
Applicability
        ↓
Six Supported Compliance Checks
        ↓
Findings + Evidence
        ↓
Inspector Verification
        ↓
MVP Result
        ↓
Basic Output
        ↓
Persistent Deployment / Demonstration
```

This is the current implementation target.

---

# 7. Current Compliance Scope

The MVP is limited to six core declaration checks:

1. Manufacturer / Packer / Importer
2. Common / Generic Product Name
3. Net Quantity + Standard Unit
4. Month / Year of Manufacture / Packing / Import
5. MRP inclusive of all taxes
6. Consumer Care Details

## Country of Origin

Country of Origin is applicability-driven:

```text
Imported = YES
    → Applicable

Imported = NO
    → NOT_APPLICABLE

Imported = UNKNOWN
    → REVIEW / BLOCK AS APPROPRIATE
```

Country of Origin is therefore not treated as universally mandatory.

---

# 8. Explicitly Deferred Features

The following remain target-system capabilities or future work and are not part of the one-day critical path unless explicitly approved:

- Unit Sale Price
- broad category-specific compliance rules
- universal exemption handling
- dynamic regulatory/rule update pipeline
- definitive universal packaging placement verification
- definitive font-size legal verdict from uncontrolled photographs
- internet-wide product crawling
- full Physical ↔ Online Verification
- advanced repository functionality
- advanced search/retrieval
- advanced dashboards and metrics
- full production-grade report suite
- broad enforcement/follow-up workflow
- unnecessary microservices
- speculative infrastructure
- unrelated feature requests
- any feature that materially expands the MVP without approval

Deferred features remain part of the broader target direction where appropriate.

---

# 9. Locked Result Vocabulary

The project uses:

```text
PASS
POTENTIAL_NON_COMPLIANCE
REQUIRES_REVIEW
NOT_APPLICABLE
INCOMPLETE
PROCESSING_FAILED
```

Important semantics:

```text
NOT_APPLICABLE ≠ PASS
INCOMPLETE ≠ POTENTIAL_NON_COMPLIANCE
PROCESSING_FAILED ≠ NON_COMPLIANCE
NOT_OBSERVED ≠ MISSING
UNREADABLE ≠ MISSING
CONFLICTING → REQUIRES_REVIEW
```

No technical failure or uncertainty may be converted into a legal conclusion.

---

# 10. AI / OCR Decisions

## OCR

**Selected:** PaddleOCR

Responsibilities:

- text detection
- text recognition
- bounding boxes
- OCR confidence
- source-image association

OCR does not determine compliance.

## AI Model

**Selected:** Gemini 2.5 Flash

Responsibilities:

- declaration extraction
- semantic interpretation
- normalization
- context mapping
- conflict detection
- uncertainty preservation

AI must not:

- invent declarations
- silently resolve conflicting values
- make final legal decisions
- modify original evidence
- modify controlled rules
- finalize inspections
- alter finalized history

## Puter Decision

Puter was considered as an AI option and is currently:

> **SET ASIDE**

It must not be introduced into the current architecture unless the human explicitly reopens the decision.

---

# 11. AI Reliability Contract

The system treats AI output as structured observation data rather than legal truth.

Accepted declarations should retain:

- value
- normalized representation where applicable
- observation status
- AI extraction confidence
- source OCR region(s)
- source evidence reference(s)

Allowed observation statuses:

```text
OBSERVED
NOT_OBSERVED
UNCERTAIN
UNREADABLE
CONFLICTING
```

Rules:

1. No accepted AI fact without evidence/source provenance.
2. No unsupported declaration may be invented.
3. Conflicting values are preserved.
4. Ambiguous interpretation becomes `UNCERTAIN`.
5. Unreadable is distinct from not observed.
6. Low-confidence OCR does not become certainty without validation.
7. Malformed AI output is a processing error.
8. AI API failure is `PROCESSING_FAILED`.
9. Original evidence remains unchanged.
10. AI never finalizes the inspection.

Confidence dimensions remain separate:

```text
OCR Confidence
      ≠
AI Extraction Confidence
      ≠
Evidence Sufficiency
      ≠
Compliance Result
```

---

# 12. Applicability Decision

The project has adopted:

> **Applicability First**

The system should determine whether a supported requirement applies before evaluating it.

Conceptually:

```text
Product / Inspection Context
            ↓
       Applicability
            ↓
       ┌────┴────┐
       │         │
      YES        NO
       │         │
   Validate   NOT_APPLICABLE
```

The MVP does not claim universal coverage of every exception or category-specific condition in the Rules.

---

# 13. Evidence Decision

Evidence is a first-class part of the product.

Evidence categories:

### Primary Evidence

Original package images captured for the inspection.

### Supplemental Evidence

Additional evidence added later following review or evidence insufficiency.

### Derived Evidence

OCR boxes, crops, highlights, and other generated artifacts.

### Audit / Decision Records

Workflow records and decisions; they are not package evidence.

Original evidence must be immutable.

Each evidence item should have:

- Evidence ID
- inspection association
- metadata
- integrity hash
- provenance
- access controls
- audit event

New evidence receives a new Evidence ID.

---

# 14. Evidence Integrity Decision

SHA-256 hashing is used/expected for tamper-evident integrity where implemented.

Important limitation:

> **A hash detects changes to the hashed artifact; it does not prove that the photograph itself is truthful or authentic.**

The project must not claim otherwise.

Evidence upload should enforce appropriate:

- authentication
- authorization
- MIME/type validation
- size validation
- decode validation
- protected storage
- provenance
- auditability

---

# 15. Adaptive Evidence Decision

There is no arbitrary fixed number of photographs.

Evidence should be sufficient for the relevant fact.

If evidence is insufficient:

```text
Evidence Insufficient
        ↓
Inspector Verification
        ↓
Manual Observation
       OR
Supplemental Evidence
       OR
Unable to Establish
        ↓
Re-analysis if affected
        ↓
Verify
        ↓
Resubmit
```

The system must not force automatic recapture as the only resolution.

---

# 16. Human-in-the-Loop Decision

Operational contract:

> **The Inspector prepares and verifies. The System analyzes and records. The Reviewer independently decides and finalizes.**

## Inspector

Can:

- create inspection
- provide context
- upload evidence
- start analysis
- inspect OCR/declarations/findings
- correct extracted values
- add manual observations
- add supplemental evidence
- verify applicability/compliance
- submit
- view preliminary output

Cannot:

- finalize
- change rules
- modify original evidence
- delete protected evidence
- mutate finalized records
- alter audit history
- approve own final decision

## Reviewer

Can:

- receive submitted inspections
- search/filter/sort review records
- inspect evidence/OCR/declarations/applicability/findings/history
- confirm assessments
- correct/override assessment with reason
- request additional evidence
- finalize

Cannot:

- change controlled rules
- delete finalized historical records
- silently mutate finalized records

---

# 17. Submission Boundary

Before submission:

```text
Inspector
   ↓
Owns working record
```

After submission:

```text
Reviewer
   ↓
Owns review decision
```

If additional evidence is requested:

```text
Reviewer
   ↓
Evidence Request ID
   ↓
Inspector
   ↓
Supplement / Observe / Unable to Establish
   ↓
Re-analysis if required
   ↓
Verify
   ↓
Resubmit
   ↓
Reviewer
```

After finalization, normal workflow mutation is prohibited.

---

# 18. Global State Invariant

Locked lifecycle invariant:

> **Upstream correction → invalidate affected downstream state → recompute → preserve prior state/history → audit transition.**

Example:

```text
Old MRP
  ↓
Inspector correction
  ↓
Affected assessment invalidated
  ↓
Compliance recomputed
  ↓
New result
  ↓
Old + new values preserved
  ↓
Correction audited
```

The system must not leave stale downstream results after upstream corrections.

---

# 19. Finalization Decision

Finalization is Reviewer-controlled.

The backend must validate the finalization operation and create a final snapshot containing/referencing relevant:

- inspection data
- product data
- evidence
- evidence hashes
- OCR
- declaration extraction
- applicability
- assessments
- findings
- corrections
- review decisions
- rule snapshot/version
- provenance
- final decision
- audit references

After finalization:

```text
FINALIZED
    ↓
READ-ONLY THROUGH NORMAL WORKFLOW
```

Report generation should use the final snapshot.

Report failure must not undo finalization.

Historical finalized records must retain their original rule context.

---

# 20. Cloud Deployment Decision

A major project decision is:

> **The deployed MVP must be cloud-deployable from the beginning.**

Therefore:

```text
DEPLOYED MVP
    │
    ├── Persistent cloud-capable relational database
    │
    └── Persistent object/file storage
```

Important:

- Local SQLite is not the production architecture.
- Local filesystem is not the production evidence-storage architecture.
- SQLite may be used for local development/testing if useful.
- Production provider choices remain open.
- Frontend hosting does not determine backend/database/storage architecture.
- Secrets/API keys remain server-side.

The system must not require a redesign merely to become deployable after local development.

---

# 21. Technology Status

The final production technology stack is **not permanently locked**.

Current working decisions:

| Area | Current Decision |
|---|---|
| Frontend concept | React + Vite |
| UI concept | Tailwind |
| Backend concept | Python + FastAPI |
| OCR | PaddleOCR |
| AI model | Gemini 2.5 Flash |
| Production database | Cloud-capable relational DB; provider open |
| Production file storage | Persistent object/file storage; provider open |
| Frontend deployment | Vercel is a possible option |
| AI provider abstraction | Keep implementation practical; avoid unnecessary abstraction |

Technology may be changed when justified by implementation reality, deployment, reliability, cost, or team decision.

A technology change that materially affects architecture or scope requires appropriate approval.

---

# 22. Target Architecture Status

The target architecture remains the established 25-logical-component architecture.

```text
1. Users
2. Web Application
3. FastAPI Application/API Layer
4. Inspection Management
5. Evidence Management
6. Image Processing & Quality
7. OCR Engine
8. Visual Analysis
9. Declaration Extraction & AI Understanding
10. Applicability Engine
11. Evidence Sufficiency & Coverage
12. Controlled Compliance Rules
13. Compliance Engine
14. Findings & Evidence Generation
15. Inspector Verification
16. Reviewer & Final Decision
17. Finalization & Immutable Snapshot
18. Reporting & Export
19. Repository & History
20. Search & Retrieval
21. Dashboard & Metrics
22. Database
23. Persistent Object/File Storage
24. Security / Integrity / Audit
25. Physical ↔ Online Verification
```

These are logical boundaries.

They are not a requirement to create 25 microservices.

The MVP implements only the subset required for the vertical slice.

---

# 23. Physical ↔ Online Verification Status

The broader target system includes Physical ↔ Online Verification.

Its purpose is to compare information between:

```text
Physical Package
      ↕
Online Product Information
```

A mismatch is represented as:

> **Cross-Channel Inconsistency**

It is not automatically a legal violation.

Internet-wide crawling is deferred from the current MVP.

---

# 24. Documentation State

The project documentation has been realigned to distinguish target-system requirements from current MVP execution.

## Control / Current-State Documents

- `MVP_BUILD_SCOPE.md`
- `PROJECT_STATE.md`
- `PHASE.md`
- `AGENT_ENGINEERING_PROTOCOL.md`

## Target / Specialized Documents

- `01_PRD.md`
- `02_TRD.md`
- `03_Architecture.md`
- `04_Design.md`
- `05_Domain_Specification.md`
- `06_Compliance_Rules.md`
- `07_State_Machine.md`
- `08_API_Specification.md`
- `09_Database_Specification.md`
- `10_Error_Handling.md`
- `11_Testing_and_Release_Gate.md`

`README.md` provides project orientation and the high-level contract.

Specialized documents remain authoritative for their own domains.

---

# 25. Documentation / Implementation Separation

The project explicitly rejects the following assumption:

```text
Documented = Implemented
```

Instead:

```text
DOCUMENTED
    ↓
INTENDED

IMPLEMENTED
    ↓
ACTUAL CODE

TESTED
    ↓
EXECUTED EVIDENCE

VERIFIED
    ↓
CONFIRMED BEHAVIOR

DEPLOYED
    ↓
CONFIRMED EXTERNAL ENVIRONMENT
```

`PROJECT_STATE.md` must track the actual state.

---

# 26. Current Implementation Status

At the time this state document is established:

### Scope / Architecture

**Status: DECIDED / LOCKED**

The current MVP boundary and target architecture have been explicitly separated.

### Compliance Scope

**Status: DECIDED / LOCKED**

Six core checks are defined.

### Result Vocabulary

**Status: DECIDED / LOCKED**

Six controlled result states are defined.

### AI/OCR Direction

**Status: DECIDED**

- PaddleOCR selected.
- Gemini 2.5 Flash selected.
- Puter set aside.

### Evidence Model

**Status: DECIDED**

Primary, supplemental, derived, and audit/decision distinctions are defined.

### Human Workflow

**Status: DECIDED**

Inspector prepares/verifies; Reviewer independently decides/finalizes in the target workflow.

### Cloud Deployment Requirement

**Status: DECIDED**

Production MVP requires persistent cloud-capable database and object/file storage.

### Implementation Audit (Phase 0)

**Status: COMPLETE**

Phase 0 audit report generated and verified in `phase0_reconciliation_report.md`. Greenfield repository verified.

### Phase 1 — Foundation & Evidence Management

**Status: COMPLETE & VERIFIED (2026-09-16)**

1. **Repository Setup**: Git initialized, `.gitignore` active, `.env.example` template created.
2. **Shared Domain Package**: `shared/domain/` contracts, lifecycle states, enums, schemas, and error codes created.
3. **Database Foundation**: SQLAlchemy 2.0 async/sync models for `User`, `InspectionCase`, `EvidenceAsset`, and `AuditEvent`.
4. **Backend API (FastAPI)**: JWT Authentication, RBAC role dependencies (`INSPECTOR`, `REVIEWER`), inspection creation, Product Context validation, evidence pipeline (MIME validation, PIL decoding integrity, SHA-256 calculation, storage persistence, draft deletion).
5. **Frontend Application**: React 18 + TypeScript + Vite + Tailwind CSS with dark theme, login flow, inspection repository list, Product Context creation form, and Inspection Workspace with interactive evidence uploader.
6. **Automated Test Suite**: 7/7 pytest automated test cases passing with 100% success rate.
7. **Golden Path Verified**: Login → Create Inspection → Product Context → Upload Evidence → View Inspection.

---

# 27. Current Phase

The current status is:

> **PHASE 1 — COMPLETE**

Next authorized phase:

> **PHASE 2 — Perception (Image Quality, PaddleOCR, Bounding Boxes, Derived Evidence, Canvas Overlay)**

---

# 28. Phase Sequence

The current execution plan is:

```text
PHASE 0
Repository / Implementation Audit
        ↓
Human Checkpoint
        ↓
PHASE 1
Minimal Foundation
        ↓
PHASE 2
Inspection + Image Input
        ↓
PHASE 3
Image Processing + PaddleOCR
        ↓
PHASE 4
Gemini Declaration Extraction
        ↓
PHASE 5
Applicability + Six Rules
        ↓
PHASE 6
Findings + Evidence
        ↓
PHASE 7
Inspector Verification + Result
        ↓
PHASE 8
End-to-End QA + Basic Export
        ↓
PHASE 9
Deployment + Demonstration Readiness
```

---

# 29. Immediate Next Actions

## Action 1 — Run Phase 0 Audit

Inspect:

- repository tree
- frontend
- backend
- configuration
- dependencies
- routes
- database setup
- storage setup
- existing AI/OCR code
- current UI
- tests
- environment configuration

Do not blindly rewrite existing work.

## Action 2 — Establish Actual State

Update this document with:

- actual implemented modules
- actual working flows
- actual failures
- actual blockers
- actual test results

## Action 3 — Human Checkpoint

Present the audit before beginning material implementation if the current state differs from expectations.

## Action 4 — Build the Vertical Slice

Implement only what is necessary for:

```text
Evidence
 → OCR
 → AI Extraction
 → Validation
 → Applicability
 → Six Checks
 → Findings
 → Evidence
 → Inspector Verification
 → Result
 → Persistence
 → Deployment
```

## Action 5 — Verify End-to-End

Use representative package evidence.

## Action 6 — Deploy

Confirm the deployed workflow can persist data and evidence.

---

# 30. P0 Priorities

The following are P0:

- representative evidence input
- image processing
- PaddleOCR
- OCR provenance
- Gemini extraction
- structured declaration schema
- backend validation
- applicability
- six compliance checks
- controlled result states
- findings
- evidence references
- Inspector verification
- correction/recomputation behavior
- persistence
- basic error handling
- deployed demonstration

If time is constrained, protect these first.

---

# 31. P1 Priorities

P1 items may be completed after P0:

- UI polish
- improved evidence visualization
- richer error presentation
- basic export
- basic inspection history
- demonstration refinements
- other low-risk improvements that do not expand the MVP

---

# 32. Known Constraints

The project currently has these important constraints:

1. One-day MVP implementation window.
2. Target documentation is substantially larger than the MVP.
3. Final production technology stack is not completely locked.
4. Production database provider is not yet locked.
5. Production object storage provider is not yet locked.
6. The AI model is currently Gemini 2.5 Flash.
7. OCR is currently PaddleOCR.
8. Puter is set aside.
9. Legal compliance coverage is intentionally bounded.
10. Human decision authority must remain intact.
11. Deployment must be possible without redesign.
12. Evidence provenance and integrity must be preserved.
13. The system must not overclaim legal certainty.

---

# 33. Known Risk Areas

These areas require special attention during implementation:

### AI hallucination

Mitigation:

- strict schema
- source mapping
- uncertainty states
- backend validation
- no unsupported facts

### OCR errors

Mitigation:

- preserve OCR confidence
- preserve regions
- human verification
- do not equate OCR failure with missing declaration

### Legal overclaiming

Mitigation:

- deterministic controlled rules
- applicability-first behavior
- `POTENTIAL_NON_COMPLIANCE`
- human decision authority

### Stale downstream state

Mitigation:

- global state invariant
- invalidation and recomputation
- correction audit

### Evidence tampering / loss

Mitigation:

- immutable original
- Evidence IDs
- hashes
- provenance
- protected storage

### Deployment failure

Mitigation:

- persistent cloud-capable DB
- persistent object storage
- deployment planning from the beginning

### Scope explosion

Mitigation:

- `MVP_BUILD_SCOPE.md`
- phase discipline
- human checkpoints
- this protocol
- P0/P1 prioritization

---

# 34. What the Agent Must Not Do

The implementation agent must not:

- claim undocumented functionality is implemented without checking
- implement the full target architecture during the one-day MVP
- create unnecessary microservices
- introduce Puter without explicit approval
- add Unit Sale Price to the MVP
- add broad category-specific rules without approval
- invent legal rules
- treat AI output as legal truth
- fabricate declarations
- silently resolve conflicting values
- modify original evidence
- treat technical failure as non-compliance
- treat unreadable text as missing without evidence
- silently mutate finalized records
- use client-side authorization as the security boundary
- build a local-only production architecture
- rewrite the project architecture because the MVP is smaller
- create speculative infrastructure
- start another documentation cycle instead of implementing the MVP

---

# 35. Implementation Reporting Standard

At every meaningful phase boundary, the agent should report:

```text
PHASE:
STATUS:

COMPLETED:
- ...

VERIFIED:
- ...

NOT VERIFIED:
- ...

KNOWN ISSUES:
- ...

FILES / COMPONENTS CHANGED:
- ...

TESTS RUN:
- ...

MVP IMPACT:
- ...

NEXT PHASE:
- ...
```

The language must distinguish:

```text
DONE
from
WORKING
from
TESTED
from
DEPLOYED
```

---

# 36. Finalization Integrity

Once an inspection is finalized:

```text
Final Snapshot
      ↓
Historical Record
      ↓
Protected from Normal Mutation
```

No future AI/model/rule update may silently rewrite the historical decision.

Any future reprocessing must be an explicit, controlled operation outside ordinary finalization.

---

# 37. Definition of Current MVP Success

The MVP succeeds when a judge can provide representative packaged-commodity evidence and see:

```text
1. Evidence input
2. Image processing
3. OCR
4. Structured declaration extraction
5. Backend validation
6. Applicability
7. Six supported compliance checks
8. Findings
9. Supporting evidence
10. Inspector verification/correction
11. Clear result
12. Persistent deployed workflow
```

The goal is not to demonstrate every target-system feature.

The goal is to demonstrate the core value of ComplianceScan convincingly and reliably.

---

# 38. Final Current-State Statement

The project has moved from:

```text
Large Target Documentation
        ↓
Risk of Building Everything
```

to:

```text
Large Target System
        ↓
Controlled MVP Boundary
        ↓
One-Day Vertical Slice
        ↓
Actual Repository Audit
        ↓
Focused Implementation
        ↓
End-to-End Verification
        ↓
Deployment
```

The architecture remains ambitious.

The implementation path is intentionally narrow.

This is a deliberate engineering decision, not a reduction in the long-term product vision.

---

```text
┌─────────────────────────────────────────────────────┐
│                    COMPLIANCESCAN                   │
├─────────────────────────────────────────────────────┤
│ Target System                                       │
│ → Broad inspection-assistance platform              │
│ → 25 logical components                             │
│ → Full reviewer/history/evidence architecture       │
├─────────────────────────────────────────────────────┤
│ Current Implementation Status                       │
│ → Phase 1 (Core & Infrastructure): VERIFIED PASSED  │
│ → Phase 2.1 (Image Quality Pipeline): VERIFIED PASSED│
│   - Canonical config (shared/domain/constants.py)   │
│   - Decoupled QualityStatus from ComplianceResult   │
│   - 25/25 backend & migration tests passing          │
│ → Phase 2.2 (PaddleOCR Perception): PLANNED         │
│   - Engine: rapidocr-onnxruntime (PP-OCRv4 ONNX)    │
│   - Verified Python 3.14 environment compatibility  │
│   - Deduplicated DB table ocr_results               │
│ → Phase 2.3 (Gemini 2.5 Flash Extraction): PENDING  │
│ → Phase 2.4 (Applicability & Rule Engine): PENDING  │
│ → Phase 2.5 (Reviewer Triage & Finalize): PENDING   │
└─────────────────────────────────────────────────────┘
```

---

# 40. Governing Principle

> **Build deliberately. Verify honestly. Preserve evidence. Respect uncertainty. Control scope. Keep the architecture coherent. Deliver one complete journey.**

And the product principle remains:

> **AI finds → Evidence proves → Officer decides.**
