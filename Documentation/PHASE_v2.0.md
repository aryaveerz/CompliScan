# PHASE — COMPLIANCESCAN IMPLEMENTATION ROADMAP

**Project:** ComplianceScan
**SIH'26 Problem Statement:** 26034
**Document Version:** 2.0
**Status:** Current execution-control document

---

# 1. Purpose

This document defines the implementation sequence for ComplianceScan.

It converts the current MVP scope into executable phases while preserving the broader target architecture for future expansion.

The governing strategy is:

> **ONE COMPLETE USER JOURNEY > MANY PARTIAL SUBSYSTEMS**

The one-day implementation must prioritize a working, deployable, trustworthy vertical slice.

---

# 2. Phase Authority

This document defines:

- execution order
- phase gates
- implementation priorities
- stop conditions
- validation checkpoints

`MVP_BUILD_SCOPE.md` defines what belongs in the MVP.

`PROJECT_STATE.md` defines what is actually implemented.

`AGENT_ENGINEERING_PROTOCOL.md` defines how the coding agent must operate.

Together:

```text
MVP_BUILD_SCOPE
      ↓
WHAT to build

PHASE
      ↓
WHEN / in what order to build

PROJECT_STATE
      ↓
WHAT is actually built

AGENT_ENGINEERING_PROTOCOL
      ↓
HOW the agent operates
```

---

# 3. Target System vs MVP Execution

The full ComplianceScan target system is larger than the one-day MVP.

Therefore:

```text
TARGET ARCHITECTURE
       ↓
Select required vertical slice
       ↓
Build MVP
       ↓
Validate + deploy
       ↓
Future expansion
```

The existence of a target component, API, database table, role, screen, or workflow does not automatically make it an MVP task.

---

# 4. One-Day Strategy

The implementation should follow this priority:

```text
RUNNABLE
   ↓
PERSISTENT
   ↓
END-TO-END
   ↓
TRUSTWORTHY
   ↓
DEPLOYED
   ↓
POLISHED
```

Do not reverse the order.

For example:

```text
Beautiful dashboard
```

is less important than:

```text
Evidence → OCR → AI → Rules → Verification → Result
```

---

# 5. Phase Overview

The current execution roadmap is:

```text
PHASE 0 — Reconnaissance & Reality Check
PHASE 1 — Foundation & Deployable Persistence
PHASE 2 — Inspection + Evidence
PHASE 3 — Image Processing + OCR
PHASE 4 — AI Declaration Understanding
PHASE 5 — Applicability + Compliance Engine
PHASE 6 — Findings + Inspector Verification
PHASE 7 — Report + Retrieval
PHASE 8 — Deployment + Quality Gate
PHASE 9 — Demo Hardening & Stop
```

Reviewer workflow, advanced repository/search, dashboard expansion, physical-online verification, and other target capabilities are staged after the critical path unless they are already stable and inexpensive.

---

# 6. PHASE 0 — Reconnaissance & Reality Check

## Objective

Understand the repository and establish actual implementation state before changing code.

## Required actions

The agent must:

1. read the control documents
2. read `MVP_BUILD_SCOPE.md`
3. read relevant numbered specifications
4. inspect the repository
5. identify existing frontend/backend/database/storage structure
6. identify existing integrations
7. identify existing tests
8. identify missing dependencies
9. compare implementation reality with MVP scope
10. update/produce `PROJECT_STATE.md` as appropriate

## Must NOT

- start feature implementation blindly
- redesign the architecture
- create a second MVP architecture
- add features because target docs contain them
- begin a documentation-expansion loop

## Gate

The agent produces a concise implementation report:

```text
CURRENT STATE
MISSING FOR MVP
BLOCKERS
RECOMMENDED NEXT STEP
```

Then stops for human confirmation before material implementation.

---

# 7. PHASE 1 — Foundation & Deployable Persistence

## Objective

Create the minimum stable foundation required for the vertical slice.

## Scope

Establish:

- runnable frontend
- runnable backend/API
- environment configuration
- API connectivity
- persistent relational database
- persistent object/file storage
- basic application structure
- safe server-side secrets
- basic health checks

## Deployment principle

The deployed MVP must not depend on local-only persistence.

```text
Frontend
   ↓
Backend
   ↓
Cloud-capable relational DB
   +
Persistent object storage
```

SQLite may be used for local development/testing but is not the deployed source of truth.

## Gate

Verify:

```text
Frontend starts
Backend starts
Frontend ↔ Backend works
Backend ↔ Database works
Backend ↔ Object Storage works
Secrets are server-side
Health check works
```

Do not proceed if the basic foundation is fundamentally broken.

---

# 8. PHASE 2 — Inspection + Evidence

## Objective

Create the inspection record and securely establish original evidence.

## Scope

Implement the minimum:

```text
Create Inspection
      ↓
Product / Context
      ↓
Evidence Upload
      ↓
Evidence Validation
      ↓
Persistent Storage
      ↓
Evidence ID
      ↓
Hash / Provenance
```

## Evidence requirements

Where implemented, preserve:

- original image
- Evidence ID
- inspection association
- metadata
- SHA-256
- provenance
- storage reference

The original image must not be modified by downstream processing.

## Gate

A user must be able to:

```text
Create inspection
→ upload image
→ persist image
→ retrieve image
```

Failure must be explicit and must not create phantom evidence.

---

# 9. PHASE 3 — Image Processing + OCR

## Objective

Turn evidence into usable textual observations.

## Scope

Implement:

- safe image preprocessing
- analysis copy
- basic quality handling
- PaddleOCR
- text
- bounding boxes
- OCR confidence
- source evidence association

Pipeline:

```text
Original Evidence
      ↓
Analysis Copy
      ↓
Image Processing
      ↓
PaddleOCR
      ↓
OCR Text + Boxes + Confidence
```

## Critical rule

PaddleOCR reads.

It does not determine compliance.

## Failure handling

```text
OCR unavailable
      ↓
PROCESSING_FAILED

OCR completes but text is unreadable
      ↓
UNREADABLE / NOT_OBSERVED
```

Do not convert OCR failure into non-compliance.

## Gate

A representative image must produce usable OCR output with traceable evidence association.

---

# 10. PHASE 4 — AI Declaration Understanding

## Objective

Convert OCR observations into structured declaration data.

## AI

MVP model:

> Gemini 2.5 Flash

## Pipeline

```text
OCR Text
+
Bounding Boxes
+
OCR Confidence
+
Evidence References
      ↓
Gemini 2.5 Flash
      ↓
Structured Declaration Data
      ↓
Schema Validation
      ↓
Domain Validation
```

## AI responsibilities

The AI may perform:

- declaration extraction
- semantic interpretation
- normalization
- context mapping
- conflict detection
- uncertainty preservation

## AI must NOT

- make final legal decisions
- invent unsupported declarations
- silently resolve conflicts
- modify original evidence
- modify rules
- finalize inspections
- mutate finalized history

## Declaration statuses

```text
OBSERVED
NOT_OBSERVED
UNCERTAIN
UNREADABLE
CONFLICTING
```

## Critical invariant

```text
AI confidence
      ≠
Compliance result
```

## Gate

Representative inputs must produce structured, validated declaration data with source references.

---

# 11. PHASE 5 — Applicability + Compliance Engine

## Objective

Determine which supported requirements apply and evaluate them deterministically.

## Applicability first

```text
Structured Data
      ↓
Context
      ↓
Applicability
      ↓
Relevant Requirements
      ↓
Controlled Rules
      ↓
Compliance Assessment
```

## Supported MVP checks

1. Manufacturer / Packer / Importer
2. Common / Generic Product Name
3. Net Quantity + Standard Unit
4. Month / Year of Manufacture / Packing / Import
5. MRP inclusive of all taxes
6. Consumer Care Details

Country of Origin is applicability-driven.

## Rule model

Use a controlled rule snapshot.

Do not build a dynamic legal-rule update platform in the one-day MVP.

## Results

```text
PASS
POTENTIAL_NON_COMPLIANCE
REQUIRES_REVIEW
NOT_APPLICABLE
INCOMPLETE
PROCESSING_FAILED
```

## Critical rules

```text
NOT_APPLICABLE ≠ PASS
INCOMPLETE ≠ NON-COMPLIANCE
PROCESSING_FAILED ≠ NON-COMPLIANCE
CONFLICTING → REQUIRES_REVIEW
```

## Gate

At least one representative compliant case and one representative potential-non-compliance case must pass through the complete rule pipeline.

---

# 12. PHASE 6 — Findings + Inspector Verification

## Objective

Make automated output explainable and human-verifiable.

## Findings

Each material finding should expose:

- requirement
- assessment
- reason
- rule reference
- evidence reference
- source/derived evidence where useful
- uncertainty/confidence context

## Inspector Verification

The Inspector can:

- review extracted declarations
- correct extracted values
- add manual observations
- supplement evidence where supported
- verify applicability
- verify assessment
- submit

## Correction invariant

```text
Upstream correction
      ↓
Invalidate affected downstream state
      ↓
Recompute
      ↓
Preserve previous state/history
      ↓
Audit transition
```

## No silent correction

The system must not silently overwrite historical extraction or assessment context.

## Gate

An Inspector must be able to detect and correct an extraction problem and obtain a consistent recalculated result.

---

# 13. PHASE 7 — Report + Retrieval

## Objective

Turn the completed inspection into a useful persistent output.

## Scope

Implement the smallest useful:

- inspection detail
- result summary
- evidence references
- declaration summary
- applicability
- findings
- reasons
- verification information
- report/export where feasible
- retrieval of completed inspection

## Priority

```text
Correct result
      >
Reliable record
      >
Useful report
      >
Advanced formatting
```

PDF is preferred if practical.

Editable export is target functionality and must not block the primary journey.

## Gate

A completed inspection can be retrieved and its result/report can be understood without relying on transient UI state.

---

# 14. PHASE 8 — Deployment + Quality Gate

## Objective

Prove that the MVP works outside the developer's local environment.

## Deployment requirements

Verify:

```text
Frontend reachable
Backend reachable
Database persistent
Object storage persistent
OCR available
Gemini configured
Secrets protected
API routes functional
```

## Functional tests

At minimum:

```text
Happy path
Invalid input
Invalid/poor evidence
OCR failure
AI failure
Malformed AI output
Conflict
Uncertainty
Correction
Retrieval
```

## Integrity tests

Verify:

```text
Original evidence preserved
Evidence hash stable
Derived artifacts separated
No false compliance from processing failure
No known stale result after correction
```

## Security tests

Verify:

```text
Unauthorized action rejected
Secrets not exposed
Unsafe file input rejected
Evidence access controlled
```

## Gate

No known P0 blocker may remain in the primary inspection journey.

---

# 15. PHASE 9 — Demo Hardening & Stop

## Objective

Make the working MVP stable enough for demonstration.

## Work allowed

- fix bugs
- improve loading/error states
- improve evidence presentation
- improve result readability
- improve report presentation
- improve deployment reliability
- improve test coverage
- prepare representative demo cases
- prepare fallback demo data

## Work NOT allowed

Do not begin unrelated feature development.

Examples:

```text
New rule-management portal
Advanced analytics
Universal category engine
Complete mobile app
Internet-wide crawler
Enterprise notification system
```

## Stop condition

When:

```text
Primary journey works
+
Release gates pass
+
Deployment is stable
+
Demo cases are reliable
```

then:

> **STOP BUILDING NEW FEATURES.**

Use remaining time for reliability and presentation.

---

# 16. Critical Path

The one-day critical path is:

```text
PHASE 0
Reconnaissance
   ↓
PHASE 1
Foundation + Persistent Cloud-Capable Storage
   ↓
PHASE 2
Inspection + Evidence
   ↓
PHASE 3
Image Processing + PaddleOCR
   ↓
PHASE 4
Gemini Declaration Extraction
   ↓
PHASE 5
Applicability + Six Checks
   ↓
PHASE 6
Findings + Inspector Verification
   ↓
PHASE 7
Report + Retrieval
   ↓
PHASE 8
Deployment + Quality
   ↓
PHASE 9
Demo Hardening + STOP
```

This path is more important than implementing every target subsystem.

---

# 17. Priority Model

Use:

```text
P0 = Required for primary journey
P1 = Valuable if P0 is stable
P2 = Target/future
```

## P0

- runnable application
- persistent deployed storage
- inspection creation
- evidence
- image processing
- PaddleOCR
- Gemini extraction
- schema/domain validation
- applicability
- six core checks
- findings
- Inspector verification
- result
- retrieval
- deployment
- critical failure handling

## P1

- stronger report presentation
- richer repository/search
- basic dashboard
- Reviewer workflow if P0 is stable
- adaptive evidence improvements
- richer visual analysis
- additional UX polish

## P2

- full Reviewer platform
- advanced repository
- complete audit/history workspace
- physical-online verification
- universal rule coverage
- dynamic rule management
- advanced analytics
- mobile application
- enforcement/follow-up workflows
- enterprise governance

---

# 18. Reviewer Staging Rule

Reviewer is part of the target operational model.

However, the one-day build must not sacrifice the complete primary inspection journey merely to implement a large review subsystem.

Priority:

```text
Inspector end-to-end journey
        >
Full Reviewer subsystem
```

If Reviewer is implemented, preserve:

```text
Inspector prepares/verifies
Reviewer independently decides/finalizes
```

If not implemented in the one-day build, do not fake the workflow.

---

# 19. Authentication / RBAC Staging

The target system includes RBAC.

For the one-day MVP:

```text
Security boundary is required.
Full enterprise RBAC administration is not.
```

Implement the smallest safe authorization model necessary for the deployed workflow.

Do not spend the critical-path window on:

- role administration UI
- complex permission matrices
- enterprise identity integration

unless explicitly approved and already required by deployment.

---

# 20. Dashboard Staging

Dashboard is not on the primary critical path.

Build only after:

```text
Inspection
→ Analysis
→ Verification
→ Result
```

works reliably.

A basic dashboard may show:

- inspections processed
- pass
- potential non-compliance
- review/incomplete
- processing failures

Advanced analytics are deferred.

---

# 21. Search / Repository Staging

Basic retrieval is part of the useful MVP.

Advanced search is not.

Minimum:

```text
Inspection ID
→ Retrieve inspection
```

Optional after P0:

```text
Date
Result
Status
Product
```

Do not build enterprise search before the primary journey works.

---

# 22. Physical ↔ Online Staging

Physical-online verification is P1/P2 depending on implementation progress.

If implemented:

```text
Physical identity
      ↓
Online listing
      ↓
Field comparison
      ↓
Cross-Channel Inconsistency
```

Never interpret a mismatch automatically as legal non-compliance.

No internet-wide crawler is required.

---

# 23. Error-Handling Gate

Every phase involving processing must preserve:

```text
Technical Failure
      ≠
Compliance Failure
```

Examples:

```text
OCR failure → PROCESSING_FAILED

AI failure → PROCESSING_FAILED

Unreadable → UNREADABLE / INCOMPLETE

Conflict → REQUIRES_REVIEW

Unknown applicability → REVIEW / INCOMPLETE
```

Never:

```text
Exception → NON-COMPLIANCE
```

---

# 24. Evidence Integrity Gate

At every phase:

```text
Original Evidence
      ↓
Never modified
```

Derived artifacts may include:

```text
OCR boxes
crops
highlights
preprocessed copies
AI observations
```

These must remain distinguishable from original evidence.

---

# 25. State Consistency Gate

Every material correction must follow:

```text
Correction
   ↓
Affected downstream state invalidated
   ↓
Recomputation
   ↓
Current result
```

If recomputation fails:

```text
Do not present stale output as current.
```

The detailed lifecycle is authoritative in `07_State_Machine.md`.

---

# 26. No-Guessing Gate

The AI pipeline must never silently guess.

If information is:

```text
Ambiguous
Unreadable
Conflicting
Unsupported
Missing source evidence
```

preserve the uncertainty and route to appropriate verification/review.

---

# 27. Deployment-First Principle

Because the MVP will be demonstrated to judges/users after implementation:

> **Deployment is part of the MVP, not a post-MVP activity.**

Do not leave deployment until the final minutes without testing.

A basic deployed environment should exist as early as practical after Phase 1.

---

# 28. Cloud Persistence Principle

The architecture must remain cloud-deployable from the beginning.

Required:

```text
Persistent relational DB
+
Persistent object/file storage
```

The exact provider is open.

Local-only persistence is acceptable only for development/testing.

---

# 29. Technology Flexibility

The final production tech stack is not locked by this phase plan.

The team may choose practical technologies.

The agent should optimize for:

- speed
- reliability
- deployment
- maintainability
- security
- team familiarity
- integration simplicity

Do not introduce technology merely because it appears in an older document.

---

# 30. Phase Gate Discipline

A phase is complete only when its output is actually usable by the next phase.

Bad:

```text
OCR UI exists
```

Good:

```text
OCR service produces validated text,
boxes, confidence and evidence references
that the AI stage can consume.
```

Every phase must produce a usable contract.

---

# 31. Gate Failure Policy

If a phase gate fails:

```text
STOP
 ↓
Identify blocker
 ↓
Fix blocker
 ↓
Re-run gate
 ↓
Continue
```

Do not work around a foundational failure by silently degrading the architecture.

---

# 32. Scope Expansion Policy

If an implementation discovery suggests a missing feature:

```text
Identify requirement
      ↓
Explain why it blocks the current phase
      ↓
Estimate smallest viable change
      ↓
Human approval
      ↓
Implement
```

Do not silently expand scope.

---

# 33. Architecture Change Policy

Do not create a new architecture to make the MVP easier.

Instead:

```text
Target architecture
      ↓
MVP subset
      ↓
Implementation
```

If a genuine contradiction is discovered:

1. identify the authoritative document
2. document the contradiction
3. propose the smallest correction
4. obtain human approval
5. update affected contract
6. implement

---

# 34. Documentation Freeze

The project has enough planning documentation to begin implementation.

Therefore:

> **Do not continue creating documentation instead of building.**

Documentation changes are allowed only when implementation reveals:

- a contradiction
- a missing contract
- a material security issue
- a necessary scope clarification
- a state/data/API inconsistency

Do not create documents simply to make the project appear more complete.

---

# 35. Agent Operating Checkpoint

Before coding:

```text
PHASE 0
   ↓
Human confirmation
```

After that:

```text
Build phase
   ↓
Run gate
   ↓
Update PROJECT_STATE
   ↓
Continue
```

For material scope changes:

```text
STOP
   ↓
Ask for approval
```

---

# 36. PROJECT_STATE Update Rule

After each meaningful phase, update:

```text
Implemented
Partially Implemented
Not Implemented
Blocked
Deferred
```

Include:

- actual files/components
- actual integrations
- known failures
- next phase
- deviations from planned scope

Do not mark a feature complete because its code exists if it is not integrated/tested.

---

# 37. Phase Evidence

Each phase should leave evidence that it passed.

Examples:

```text
Phase 1
Health check + DB/storage verification

Phase 2
Stored image + retrieval

Phase 3
OCR output with boxes

Phase 4
Validated structured declarations

Phase 5
Rule evaluation results

Phase 6
Correction/recalculation demonstration

Phase 7
Retrieved report

Phase 8
Deployed smoke test

Phase 9
Stable demo run
```

This makes the project state auditable.

---

# 38. Recommended Work Allocation

When time is limited:

```text
Highest priority
Core pipeline

Next
Reliability + deployment

Next
Verification + evidence presentation

Next
Report

Last
Dashboard / advanced UI / optional features
```

Do not allocate equal time to all components.

---

# 39. If Time Runs Short

If the one-day window becomes constrained:

## Keep

```text
Evidence
OCR
AI extraction
Applicability
Six checks
Findings
Inspector verification
Result
Deployment
```

## Simplify

```text
Dashboard
Search
Report styling
Advanced visual analysis
Reviewer UI
```

## Defer

```text
Full Reviewer platform
Physical-online verification
Dynamic rules
Universal exemptions
Advanced analytics
Mobile
Enforcement
```

The core journey must survive.

---

# 40. If AI Integration Is Blocked

Do not replace the architecture with an unrelated AI mechanism without approval.

First:

```text
Diagnose
 ↓
Retry/fix integration
 ↓
Use controlled test fixture if necessary for development
 ↓
Preserve AI contract
```

A fixture may support development/testing, but must not be presented as live AI analysis in the final demo.

---

# 41. If OCR Is Blocked

Preserve the OCR contract:

```text
text
boxes
confidence
evidence reference
```

A temporary test fixture may unblock downstream development.

Do not silently claim real OCR capability if it is not working.

---

# 42. If Cloud Persistence Is Blocked

Do not quietly turn local storage into the deployed architecture.

Instead:

```text
Identify provider/configuration issue
 ↓
Fix deployment
```

Local storage may be used temporarily during local development only.

---

# 43. If Reporting Is Blocked

Do not delay the complete analysis journey for advanced report formatting.

Minimum fallback:

```text
Persistent inspection detail
+
structured result
+
evidence references
```

Then implement the simplest useful report.

---

# 44. If Reviewer Is Blocked

Do not fake independent review.

Keep:

```text
Inspector verification
```

and clearly preserve Reviewer as target scope.

If Reviewer is later implemented:

```text
Inspector
   ↓
Submit
   ↓
Reviewer
   ↓
Final Decision
```

---

# 45. Demonstration Path

The preferred final demo should be:

```text
1. Open deployed application
2. Create inspection
3. Enter/select product context
4. Upload package image
5. Show evidence stored
6. Start analysis
7. Show OCR observations
8. Show structured declarations
9. Show applicability
10. Show six compliance checks
11. Show evidence-backed findings
12. Correct/verify where appropriate
13. Show final inspection result
14. Retrieve inspection/report
15. Demonstrate one safe failure/review case if time permits
```

The demo should tell one coherent story.

---

# 46. Demo Language

Use:

> “AI finds → Evidence supports → Backend validates → Inspector verifies.”

Avoid:

> “AI decides whether the product is legal.”

Use:

> “Potential Non-Compliance”

rather than:

> “AI detected an illegal product.”

---

# 47. Final MVP Phase Gate

```text
[x] Phase 0 completed (Reconciliation & Audit)
[x] Phase 1 foundation works (DB, Auth, Storage, RBAC, Core Entities)
[x] Phase 2.1 Image Quality Assessment works (QualityStatus, canonical config, 25/25 tests passing)
[/] Phase 2.2 PaddleOCR Perception (rapidocr-onnxruntime PP-OCRv4, deduplicated DB persistence - IN PROGRESS)
[ ] Phase 2.3 Gemini 2.5 Flash extraction works
[ ] Phase 2.4 Applicability + rule evaluation engine works
[ ] Phase 2.5 Reviewer triage & finalization works
[ ] Phase 3 Verification & UI Triage works
[ ] Phase 4 Report & History works
[ ] Phase 5 Deployment & Demo Hardening complete
```

Most importantly:

```text
Create
 ↓
Capture
 ↓
Read
 ↓
Understand
 ↓
Determine Applicability
 ↓
Validate
 ↓
Explain
 ↓
Verify
 ↓
Report
```

must work as one continuous journey.

---

# 48. Post-MVP Expansion

After the one-day MVP is stable, future work may expand toward the target architecture:

```text
Reviewer Workspace
      ↓
Advanced Audit & History
      ↓
Advanced Search / Repository
      ↓
Dashboard
      ↓
Physical ↔ Online Verification
      ↓
Broader Rule Coverage
      ↓
Dynamic Rule Management
      ↓
Advanced Evidence Planning
      ↓
Mobile Application
      ↓
Enforcement / Follow-up Integration
```

These are future stages, not reasons to delay the current vertical slice.

---

# 49. Final Operating Principle

The implementation order is not:

```text
Build everything
→ test later
→ deploy later
```

It is:

```text
Build a small complete slice
        ↓
Prove it
        ↓
Deploy it
        ↓
Harden it
        ↓
Expand later
```

The most important rule is:

> **A smaller working ComplianceScan is more valuable than a larger unfinished ComplianceScan.**

And the final stopping rule is:

> **Once the complete primary journey works reliably and the release gates pass, stop adding features.**
