# 03 — SYSTEM ARCHITECTURE

**Project:** ComplianceScan
**SIH'26 Problem Statement:** 26034
**Document Version:** 2.0
**Status:** Target architecture with controlled one-day MVP implementation boundary

---

# 1. Purpose

This document defines the system architecture for ComplianceScan.

It establishes:

- logical system components
- responsibility boundaries
- data and processing flow
- security boundaries
- evidence provenance
- lifecycle ownership
- AI/OCR integration
- persistence architecture
- deployment architecture
- target-system capabilities
- one-day MVP architecture subset

This document describes architecture, not implementation status.

The actual implementation state is maintained in:

> `PROJECT_STATE.md`

The current MVP boundary is maintained in:

> `MVP_BUILD_SCOPE.md`

---

# 2. Architectural Vision

ComplianceScan is an AI-assisted inspection system for packaged commodities.

Its architecture is built around:

> **AI finds → Evidence supports → Backend validates → Inspector verifies → Reviewer decides.**

The system must preserve a clear separation between:

```text
Observation
    ↓
Interpretation
    ↓
Applicability
    ↓
Rule Evaluation
    ↓
Human Verification
    ↓
Final Decision
```

No AI component is the final legal authority.

---

# 3. Architectural Goals

The architecture must provide:

1. Complete end-to-end inspection flow
2. Evidence traceability
3. Human-in-the-loop control
4. Deterministic compliance evaluation
5. Applicability-first assessment
6. Safe AI/OCR failure handling
7. Persistent cloud deployment
8. Historical integrity
9. Backend-enforced authorization
10. Extensibility without unnecessary complexity

---

# 4. Architectural Principles

## 4.1 Human Authority

The system assists officers; it does not replace statutory decision-making.

```text
AI
 ↓
Observation / Interpretation

System
 ↓
Validation / Rule Evaluation

Inspector
 ↓
Verification

Reviewer
 ↓
Final Decision
```

---

## 4.2 Evidence First

Every important conclusion should be traceable to source evidence where applicable.

```text
Finding
   ↓
Assessment
   ↓
Declaration / Observation
   ↓
OCR Region
   ↓
Evidence
```

---

## 4.3 Applicability First

A requirement must be evaluated for applicability before being treated as a compliance requirement.

```text
Inspection Context
        ↓
Applicability
        ↓
Applicable Requirements
        ↓
Compliance Evaluation
```

---

## 4.4 Deterministic Legal Evaluation

AI interprets observations.

The backend compliance engine evaluates structured facts against controlled rules.

```text
AI
 ↓
Structured Data

Backend
 ↓
Controlled Rules
 ↓
Assessment
```

---

## 4.5 Original Evidence Is Immutable

Original package evidence must never be silently overwritten by:

- image preprocessing
- OCR
- AI output
- Inspector correction
- Reviewer decision

Derived artifacts are separate.

---

## 4.6 Backend Is Authoritative

The frontend is a presentation layer.

The backend is authoritative for:

- authentication
- authorization
- lifecycle
- ownership
- compliance assessment
- evidence integrity
- persistence
- finalization

---

## 4.7 Safe Failure

Technical failure must never silently become compliance failure.

```text
AI Failure
   ↓
PROCESSING_FAILED

Not:
POTENTIAL_NON_COMPLIANCE
```

---

## 4.8 One Complete Journey

For the one-day MVP:

> **ONE COMPLETE USER JOURNEY > MANY PARTIAL SUBSYSTEMS**

Target architecture must not force every target component into the one-day build.

---

# 5. System Context

At the highest level:

```text
             ┌──────────────────────────┐
             │       Inspector          │
             │ Capture / Verify / Submit│
             └────────────┬─────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────┐
│                   ComplianceScan                      │
│                                                       │
│  Web UI → API → Inspection → Evidence → AI/Rules     │
│                                                       │
│  OCR → Extraction → Applicability → Assessment       │
│                                                       │
│  Findings → Verification → Review → Finalization     │
└───────────────┬───────────────────────────┬───────────┘
                │                           │
                ▼                           ▼
       Persistent Database          Object/File Storage
                │
                ▼
       Historical Repository

                ▲
                │
          External AI Provider
          Gemini 2.5 Flash
```

---

# 6. Target Architecture

The target architecture contains 25 logical components.

These are logical responsibilities, not 25 microservices.

```text
01 Users
02 Web Application
03 FastAPI Application/API Layer
04 Inspection Management
05 Evidence Management
06 Image Processing & Quality
07 OCR Engine
08 Visual Analysis
09 Declaration Extraction & AI Understanding
10 Applicability Engine
11 Evidence Sufficiency & Coverage
12 Controlled Compliance Rules
13 Compliance Engine
14 Findings & Evidence Generation
15 Inspector Verification
16 Reviewer & Final Decision
17 Finalization & Immutable Snapshot
18 Reporting & Export
19 Repository & History
20 Search & Retrieval
21 Dashboard & Metrics
22 Database
23 Persistent Object/File Storage
24 Security / Integrity / Audit
25 Physical ↔ Online Verification
```

---

# 7. Logical Component 1 — Users

Represents authenticated operational users.

Primary roles:

```text
Inspector
Reviewer
```

The system may contain technical administration capabilities separately, but they are not part of the core inspection decision workflow.

Responsibilities:

- identity
- authentication context
- role
- account status
- authorization context

---

# 8. Logical Component 2 — Web Application

Current direction:

> React + Vite + Tailwind

Responsibilities:

- inspection UI
- evidence upload interaction
- processing status
- OCR visualization
- declaration review
- applicability display
- findings display
- Inspector verification
- Reviewer workspace where implemented
- report access
- history/search where implemented

The Web Application must not be the security authority.

---

# 9. Logical Component 3 — FastAPI Application/API Layer

Current backend direction:

> Python + FastAPI

This is the main application boundary.

Responsibilities:

- authentication integration
- authorization
- request validation
- lifecycle enforcement
- inspection APIs
- evidence APIs
- processing orchestration
- OCR/AI integration
- declaration validation
- applicability
- compliance evaluation
- findings
- review/finalization
- reporting
- persistence coordination
- audit

The API layer coordinates domain components; it does not replace their logical responsibilities.

---

# 10. Logical Component 4 — Inspection Management

Responsible for the inspection aggregate.

Responsibilities:

- create inspection
- inspection identifier
- product/context
- ownership
- lifecycle state
- submission
- review state
- finalization state

Conceptually:

```text
Inspection
 ├── Context
 ├── Product
 ├── Evidence
 ├── Analysis
 ├── Applicability
 ├── Assessments
 ├── Findings
 ├── Verification
 ├── Review
 └── Final Snapshot
```

---

# 11. Logical Component 5 — Evidence Management

Responsible for evidence lifecycle.

Responsibilities:

- upload
- validation
- Evidence ID
- metadata
- storage reference
- SHA-256
- provenance
- association
- access control
- original/derived distinction

Evidence types:

```text
PRIMARY
SUPPLEMENTAL
DERIVED
```

---

# 12. Logical Component 6 — Image Processing & Quality

Responsible for analysis copies.

Functions may include:

- orientation
- resizing
- preprocessing
- brightness/contrast adjustment
- denoising
- quality analysis

Important boundary:

```text
Original Evidence
      │
      ├── Preserved
      │
      └── Analysis Copy
              ↓
       Image Processing
```

Processing must not replace the original.

---

# 13. Logical Component 7 — OCR Engine

Current MVP selection:

> PaddleOCR

Responsibilities:

- text detection
- text recognition
- bounding boxes
- OCR confidence
- source evidence mapping

Output:

```text
OCR Run
 ├── text
 ├── bounding box
 ├── confidence
 └── evidence reference
```

OCR does not determine compliance.

---

# 14. Logical Component 8 — Visual Analysis

Responsible for visual observations such as:

- readability
- visibility
- image quality
- placement/evidence coverage
- font-size warning/assessment

The component must distinguish:

```text
Visual Observation
      ≠
Legal Conclusion
```

Approximate photo-based font measurements must not be presented as universally definitive where scale is unavailable.

---

# 15. Logical Component 9 — Declaration Extraction & AI Understanding

Current MVP AI:

> Gemini 2.5 Flash

Responsibilities:

- declaration extraction
- semantic interpretation
- normalization
- context mapping
- conflict detection
- uncertainty preservation

Input:

```text
OCR Text
+
OCR Regions
+
OCR Confidence
+
Evidence References
+
Controlled Schema
```

Output:

```text
Structured Declaration Observations
```

AI must not:

- make final legal decisions
- invent values
- silently resolve conflicts
- modify evidence
- change rules
- finalize inspections

---

# 16. Logical Component 10 — Applicability Engine

Determines which supported requirements apply.

Input may include:

- product context
- import status
- package context
- supported applicability conditions

Output:

```text
APPLICABLE
NOT_APPLICABLE
UNKNOWN / REVIEW
```

Applicability must precede compliance evaluation.

This is a controlled MVP applicability engine, not a universal legal exception engine.

---

# 17. Logical Component 11 — Evidence Sufficiency & Coverage

Responsible for determining whether the available evidence sufficiently supports the supported inspection requirements.

It may consider:

- declaration coverage
- image quality
- visibility
- source mapping
- unresolved areas

It must not automatically create a legal violation because evidence is insufficient.

Possible outcomes:

```text
SUFFICIENT
INSUFFICIENT
UNCERTAIN
```

The product may route insufficient evidence to Inspector Verification or Reviewer evidence request workflows.

---

# 18. Logical Component 12 — Controlled Compliance Rules

Contains the controlled rule snapshot for the supported scope.

MVP checks:

1. Manufacturer / Packer / Importer
2. Common / Generic Product Name
3. Net Quantity + Standard Unit
4. Month / Year of Manufacture / Packing / Import
5. MRP Inclusive of All Taxes
6. Consumer Care Details

Country of Origin is applicability-driven.

Rules are controlled and versioned.

There is no dynamic regulatory-update pipeline in the MVP.

---

# 19. Logical Component 13 — Compliance Engine

Evaluates structured data against controlled rules.

```text
Validated Facts
      +
Applicability
      +
Rule Snapshot
      ↓
Deterministic Evaluation
      ↓
System Assessment
```

The compliance engine must not depend on free-form LLM reasoning for the authoritative rule result.

---

# 20. Logical Component 14 — Findings & Evidence Generation

Generates explainable findings.

A finding should preserve:

- finding ID
- requirement
- result
- reason
- rule reference
- evidence references
- source regions
- provenance

Derived evidence may include:

- crop
- highlight
- OCR-region visualization

---

# 21. Logical Component 15 — Inspector Verification

The Inspector verifies the system's output.

Responsibilities:

- inspect OCR
- inspect extracted declarations
- correct underlying data
- verify applicability
- review findings
- add manual observation
- supplement evidence where applicable
- submit

The Inspector does not finalize the inspection.

---

# 22. Logical Component 16 — Reviewer & Final Decision

The Reviewer independently examines submitted inspections.

Responsibilities:

- inspect evidence
- inspect declarations
- inspect applicability
- inspect findings
- inspect audit/history
- confirm assessment
- correct/override with reason
- request evidence
- finalize

Reviewer decisions do not erase prior system assessments.

---

# 23. Logical Component 17 — Finalization & Immutable Snapshot

Finalization creates a protected historical state.

Conceptually:

```text
Submitted
   ↓
Reviewer Decision
   ↓
Backend Validation
   ↓
Atomic Final Snapshot
   ↓
FINALIZED
```

Snapshot should include/refer to:

- inspection context
- evidence references/hashes
- OCR
- declarations
- applicability
- assessments
- findings
- corrections
- review decisions
- rule snapshot
- provenance
- audit references
- final decision

---

# 24. Logical Component 18 — Reporting & Export

Responsible for:

- preliminary reports
- final reports
- PDF
- editable output where required

Final reports must be generated from the finalized snapshot.

If report generation fails:

```text
Inspection = FINALIZED
Report = ERROR / RETRYABLE
```

Report failure must not roll back finalization.

---

# 25. Logical Component 19 — Repository & History

Responsible for persistent inspection history.

Target capabilities:

- inspection history
- finalized record retrieval
- prior findings
- evidence references
- audit history
- review history

Finalized records remain protected.

---

# 26. Logical Component 20 — Search & Retrieval

Target search dimensions:

- inspection ID
- date
- state
- result
- product information
- relevant filters

MVP implementation may be limited to demonstration requirements.

---

# 27. Logical Component 21 — Dashboard & Metrics

Target metrics:

- inspection count
- result distribution
- review backlog
- processing failures
- common findings
- completion metrics

Dashboard is not a prerequisite for the core one-day vertical slice.

---

# 28. Logical Component 22 — Database

The deployed MVP requires a persistent relational database.

Responsibilities:

- structured persistence
- relationships
- transaction boundaries
- state
- audit records
- history
- rule snapshots
- final records

The exact provider/engine is intentionally open.

SQLite may be used for local development/testing but is not the deployed source of truth.

---

# 29. Logical Component 23 — Persistent Object/File Storage

Stores:

- original evidence
- supplemental evidence
- derived evidence where required
- generated reports where applicable

Requirements:

- persistent
- access-controlled
- non-public by default
- stable references
- integrity metadata

Local filesystem storage is not sufficient for the deployed MVP.

---

# 30. Logical Component 24 — Security / Integrity / Audit

Cross-cutting responsibilities:

- authentication
- authorization
- file security
- evidence integrity
- audit
- state protection
- secret management
- finalized-record protection

Security controls must exist at backend boundaries.

---

# 31. Logical Component 25 — Physical ↔ Online Verification

Target capability:

```text
Physical Package
       ↕
Online Listing
```

May compare:

- product identity
- manufacturer
- quantity
- MRP
- consumer care
- supported declarations

Mismatch is represented as:

> Cross-Channel Inconsistency

It is not automatically a legal violation.

Internet-wide crawling is outside the one-day MVP.

---

# 32. End-to-End Data Flow

The primary target flow is:

```text
                  PACKAGE EVIDENCE
                         │
                         ▼
                Evidence Management
                         │
                         ▼
              Image Processing / Quality
                         │
                         ▼
                      PaddleOCR
                         │
                         ▼
             OCR Text + Regions + Confidence
                         │
                         ▼
               Gemini 2.5 Flash
                         │
                         ▼
             Structured Declarations
                         │
                         ▼
                 Backend Validation
                         │
                         ▼
                Applicability Engine
                         │
                         ▼
               Controlled Rule Snapshot
                         │
                         ▼
                Compliance Engine
                         │
                         ▼
                Findings + Evidence
                         │
                         ▼
               Inspector Verification
                         │
                         ▼
                  Reviewer Review
                         │
                         ▼
                    Finalization
                         │
                         ▼
               Final Snapshot / Report
```

---

# 33. MVP Vertical Slice

The one-day MVP narrows the target architecture to:

```text
┌──────────────────────────────┐
│ React Web Application        │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ FastAPI Backend              │
└──────────────┬───────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
 Inspection         Evidence
 Management         Management
       │                │
       └───────┬────────┘
               ▼
       Image Processing
               │
               ▼
           PaddleOCR
               │
               ▼
     Gemini 2.5 Flash
               │
               ▼
    Declaration Validation
               │
               ▼
       Applicability
               │
               ▼
       Six Core Rules
               │
               ▼
     Findings + Evidence
               │
               ▼
     Inspector Verification
               │
               ▼
      Persistent Storage
```

This is the primary implementation path.

---

# 34. MVP vs Target Boundary

| Capability | Target | One-Day MVP |
|---|---:|---:|
| Web application | Yes | Yes |
| Backend/API | Yes | Yes |
| Inspection management | Yes | Yes |
| Evidence management | Yes | Yes |
| Image processing | Yes | Yes |
| PaddleOCR | Yes | Yes |
| Gemini extraction | Yes | Yes |
| Applicability | Yes | Yes |
| Six core checks | Yes | Yes |
| Findings/evidence | Yes | Yes |
| Inspector verification | Yes | Yes |
| Reviewer workflow | Yes | If safely achievable |
| Finalization | Yes | If safely achievable |
| Reports | Yes | Basic output where feasible |
| Repository/history | Yes | Minimum required persistence |
| Search | Yes | Minimal/optional |
| Dashboard | Yes | Deferred/secondary |
| Physical ↔ Online | Yes | Deferred |
| Dynamic rule updates | No MVP | Deferred |
| Full enforcement | No | Outside scope |

---

# 35. Component Communication

Components should communicate through explicit contracts.

Primary contract boundaries:

```text
Frontend
   ↕
API

API
   ↕
Domain Services

Domain Services
   ↕
Persistence

Processing
   ↕
OCR / AI

Compliance
   ↕
Controlled Rules
```

Avoid direct database manipulation from the frontend or arbitrary cross-component state mutation.

---

# 36. AI Provider Boundary

The AI provider should be isolated behind a backend integration boundary.

```text
Declaration Service
        │
        ▼
   AI Provider Interface
        │
        ▼
 Gemini 2.5 Flash
```

This makes provider changes possible without rewriting compliance logic.

The abstraction should remain lightweight.

---

# 37. OCR Provider Boundary

Likewise:

```text
OCR Service
    │
    ▼
PaddleOCR
```

OCR output must be normalized into an application-owned schema before downstream processing.

---

# 38. Rule Provider Boundary

Compliance rules should be represented as controlled application data/configuration.

```text
Rule Snapshot
     ↓
Compliance Engine
```

Rules must not be generated dynamically by an LLM during evaluation.

---

# 39. Evidence Provenance Architecture

The evidence chain should be:

```text
Original Evidence
       │
       ├── SHA-256
       │
       ├── OCR Run
       │      └── OCR Regions
       │
       ├── AI Run
       │      └── Declaration Observations
       │
       └── Derived Evidence
              └── Crops / Highlights

Declaration
       ↓
Assessment
       ↓
Finding
       ↓
Review / Final Snapshot
```

This chain enables explainability and historical reconstruction.

---

# 40. Correction Architecture

A correction is not merely a field update.

```text
Inspector Correction
        ↓
Persist New Value
        ↓
Preserve Previous Value
        ↓
Identify Dependencies
        ↓
Invalidate Affected Results
        ↓
Recompute
        ↓
Persist New Result
        ↓
Audit Transition
```

This follows the global invariant:

> **Upstream correction → invalidate affected downstream state → recompute → preserve prior state/history → audit transition.**

---

# 41. Processing Failure Architecture

Technical failures follow:

```text
Input
 ↓
Processing
 ├── Success → Continue
 │
 └── Failure
       ↓
PROCESSING_FAILED
       ↓
Retry / Correct Input / Human Action
```

The system must never convert a technical processing failure into a compliance result.

---

# 42. Uncertainty Architecture

Uncertainty is preserved through the pipeline.

```text
OCR Uncertainty
      ↓
AI Uncertainty
      ↓
Domain Observation
      ↓
REQUIRES_REVIEW / INCOMPLETE
```

The system should not silently convert:

```text
UNCERTAIN → OBSERVED
```

without human verification or valid evidence.

---

# 43. Conflict Architecture

If multiple values conflict:

```text
Value A
+
Value B
      ↓
CONFLICTING
      ↓
Preserve both
      ↓
REQUIRES_REVIEW
```

AI must not silently choose one.

---

# 44. Evidence Sufficiency Architecture

Evidence coverage is requirement-specific.

```text
Requirement
      ↓
Evidence Coverage
      ↓
Sufficient?
  ├── YES → Evaluate
  └── NO  → Verify / Review
```

Insufficient evidence should not automatically become:

> POTENTIAL_NON_COMPLIANCE

---

# 45. Security Boundaries

The major trust boundaries are:

```text
Browser
   │
   │ Untrusted client
   ▼
Backend
   │
   ├── Authentication
   ├── Authorization
   ├── Validation
   └── Lifecycle
   │
   ▼
Trusted Application Services
   │
   ├── Database
   ├── Object Storage
   └── External Providers
```

The browser is never trusted for authoritative values.

---

# 46. Evidence Access Security

Evidence access should require:

```text
Authenticated User
      ↓
Authorization
      ↓
Inspection Access Check
      ↓
Evidence Access
```

A user must not be able to retrieve arbitrary evidence by changing an ID.

---

# 47. Storage Security

Persistent storage should use:

- private access where supported
- server-mediated authorization
- generated object references
- integrity hashes
- controlled access URLs/mechanisms where appropriate

Storage credentials remain server-side.

---

# 48. Deployment Architecture

The deployed MVP should follow a cloud-compatible topology.

```text
                     INTERNET
                         │
                         ▼
              ┌──────────────────┐
              │ Hosted Frontend  │
              │ React / Vite     │
              └────────┬─────────┘
                       │ HTTPS
                       ▼
              ┌──────────────────┐
              │ Hosted Backend   │
              │ FastAPI          │
              └──────┬─────┬─────┘
                     │     │
             ┌───────▼┐   ┌▼────────────────┐
             │ Cloud  │   │ Object / File   │
             │ DB     │   │ Storage         │
             └────────┘   └─────────────────┘
                     │
                     ▼
             External AI Provider
             Gemini 2.5 Flash
```

PaddleOCR may run within the backend/processing environment or an appropriate processing worker.

---

# 49. Deployment Provider Flexibility

The architecture does not require a specific provider.

Possible deployment patterns include:

```text
Frontend → Vercel
Backend → Hosted Python platform
Database → Managed relational DB
Storage → Managed object storage
```

This is an example, not a locked final deployment stack.

---

# 50. Why Cloud Persistence Is Required

The project is intended for judge/user access after deployment.

Therefore this is insufficient:

```text
Browser
  ↓
Localhost
  ↓
SQLite
  ↓
Local filesystem
```

The deployed architecture requires:

```text
Internet
  ↓
Hosted Application
  ↓
Persistent Database
  +
Persistent Object Storage
```

---

# 51. Runtime Environments

At minimum:

```text
Development
Testing
Demo/Deployment
```

Environment-specific configuration must be separated.

No production secret should be hard-coded.

---

# 52. Secret Boundary

Secrets are server-side only.

Examples:

- Gemini API key
- database credentials
- storage credentials
- application secrets
- authentication secrets

```text
Browser
   X
   │
   │ never receives server secret
   ▼
Backend
   ↓
Provider
```

---

# 53. Network Requirements

Production communication should use HTTPS.

CORS should explicitly allow required frontend origins.

External service calls should use secure transport.

---

# 54. Persistence Architecture

The inspection is the central aggregate.

Conceptually:

```text
Inspection
 ├── Product / Context
 ├── Evidence
 │    ├── Original
 │    ├── Supplemental
 │    └── Derived
 ├── OCR Runs
 ├── AI Runs
 ├── Declarations
 ├── Applicability
 ├── Assessments
 ├── Findings
 ├── Corrections
 ├── Review
 ├── Audit
 └── Final Snapshot
```

---

# 55. Transaction Boundaries

Transactions should protect material state changes.

Examples:

```text
Correction
 + Invalidation
 + Audit
```

and:

```text
Final Decision
 + Final Snapshot
 + Finalization State
 + Audit
```

should be handled consistently.

---

# 56. Asynchronous Processing Direction

Processing may eventually use background workers:

```text
API
 ↓
Processing Job
 ↓
Worker
 ├── Image Processing
 ├── OCR
 ├── AI
 ├── Validation
 ├── Applicability
 └── Compliance
 ↓
Persist Results
```

The one-day MVP may use a simpler approach if it is reliable and testable.

Do not introduce queues solely for architectural appearance.

---

# 57. State and Lifecycle Architecture

The target lifecycle is:

```text
DRAFT
  ↓
EVIDENCE_READY
  ↓
PROCESSING
  ↓
ANALYSIS_READY
  ↓
VERIFICATION
  ↓
SUBMITTED
  ↓
REVIEW
  ↓
FINALIZED
```

Additional states may exist for:

- incomplete evidence
- processing failure
- evidence request
- correction/reprocessing

The authoritative lifecycle is defined in:

> `07_State_Machine.md`

---

# 58. Ownership Model

```text
Working State
     ↓
Inspector

Submitted State
     ↓
Reviewer

Finalized State
     ↓
Protected Historical Record
```

Ownership is enforced by the backend.

---

# 59. Reviewer Evidence Request Architecture

```text
Reviewer
   ↓
Evidence Request
   ↓
Request ID
   ↓
Inspector
   ├── Add supplemental evidence
   ├── Add manual observation
   └── State unable to establish
           ↓
       Reprocess if required
           ↓
        Resubmit
```

The request is not an automatic camera/recapture command.

---

# 60. Finalization Architecture

Finalization sequence:

```text
Reviewer Decision
       ↓
Authorization Check
       ↓
Lifecycle Check
       ↓
Blocking-Condition Check
       ↓
Build Final Snapshot
       ↓
Atomic Persistence
       ↓
Audit Event
       ↓
FINALIZED
```

Once finalized:

```text
Normal Mutation = REJECTED
```

---

# 61. Historical Architecture

Historical inspections must retain the rule snapshot/version used at evaluation.

```text
Inspection
    ↓
Rule Snapshot v1
    ↓
Assessment
    ↓
Finalized

Later:
Rule Snapshot v2

Historical Inspection
    ↓
Still based on v1
```

No silent recalculation of finalized history.

---

# 62. API Architecture

The API should expose domain operations rather than database-shaped endpoints wherever practical.

Conceptual groups:

```text
/auth
/inspections
/evidence
/processing
/ocr
/declarations
/applicability
/assessments
/findings
/verification
/review
/finalization
/reports
/history
/search
/dashboard
```

Only the groups required by the MVP need to be implemented.

Detailed contracts are in:

> `08_API_Specification.md`

---

# 63. Database Architecture

The target data model includes:

```text
Users
Roles
Inspections
Products / Context
Evidence
Evidence Hash / Provenance
OCR Runs
OCR Regions
AI Runs
Declarations
Declaration Sources
Applicability
Assessments
Findings
Corrections
Evidence Requests
Reviewer Decisions
Final Snapshots
Audit Events
Rule Snapshots
Reports
```

Detailed persistence requirements are in:

> `09_Database_Specification.md`

---

# 64. Error Architecture

Error categories must remain separate:

```text
Validation
Authentication
Authorization
Evidence
OCR
AI
Processing
Applicability
Rule Evaluation
Storage
Report
Internal
```

Compliance result vocabulary is separate:

```text
PASS
POTENTIAL_NON_COMPLIANCE
REQUIRES_REVIEW
NOT_APPLICABLE
INCOMPLETE
PROCESSING_FAILED
```

---

# 65. Observability Architecture

The deployed application should make failures diagnosable.

At minimum, capture structured information for:

- request failures
- processing jobs
- OCR failures
- AI failures
- storage failures
- invalid state transitions
- authorization failures
- finalization failures

Sensitive secrets and unnecessary evidence content must not be logged.

---

# 66. Performance Architecture

For the MVP, optimize for:

```text
Reliability
 ↓
Correctness
 ↓
Traceability
 ↓
Demonstration readiness
 ↓
Performance optimization
```

Avoid premature optimization.

Potential future improvements:

- background processing
- caching
- batching
- asynchronous provider calls
- scalable workers

---

# 67. Scalability Architecture

The logical separation allows future scaling without requiring it now.

Potential future scaling:

```text
API instances
      +
Processing workers
      +
OCR workers
      +
AI orchestration
      +
Managed DB
      +
Object storage
```

The MVP does not require microservices.

---

# 68. Target Physical ↔ Online Branch

The future branch is:

```text
                 ┌───────────────┐
                 │ Inspection    │
                 └───────┬───────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
      Physical Evidence       Online Information
              │                     │
              └──────────┬──────────┘
                         ▼
                  Identity Match
                         ↓
                  Field Comparison
                         ↓
             Cross-Channel Inconsistency
```

This remains outside the one-day MVP.

---

# 69. Target Dashboard Branch

The future dashboard consumes derived/aggregated information.

```text
Finalized Inspections
        ↓
Derived Metrics
        ↓
Dashboard
```

It should not mutate source inspection records.

---

# 70. Target Reporting Branch

```text
Inspection State
      ↓
Final Snapshot
      ↓
Report Generator
      ↓
PDF / Editable Output
```

Reports should not become a second source of truth.

---

# 71. Source of Truth Model

The system should maintain a clear hierarchy:

```text
Original Evidence
        ↓
Observed / Extracted Data
        ↓
Applicability
        ↓
System Assessment
        ↓
Inspector Verification
        ↓
Reviewer Decision
        ↓
Final Snapshot
```

The final snapshot is the authoritative historical representation of a finalized inspection.

---

# 72. No Hidden State

Material state must be persisted or deterministically reproducible.

Avoid relying on:

- browser-only state
- temporary memory
- untracked local files
- hidden model context
- undocumented transformations

for authoritative inspection information.

---

# 73. Integrity Model

Integrity controls apply at multiple levels:

```text
Evidence Integrity
    ↓
SHA-256 / immutable original

Data Integrity
    ↓
Transactions / constraints

Lifecycle Integrity
    ↓
State machine

Decision Integrity
    ↓
Reviewer + final snapshot

Audit Integrity
    ↓
Historical events
```

---

# 74. Security Model

Security is layered:

```text
Authentication
      ↓
Authorization
      ↓
Object-Level Access
      ↓
State Validation
      ↓
Input Validation
      ↓
Persistence Controls
      ↓
Audit
```

No single UI control is treated as sufficient.

---

# 75. Architecture Invariants

The following invariants must always hold.

## Invariant 1

AI cannot finalize an inspection.

## Invariant 2

Frontend cannot determine authoritative compliance.

## Invariant 3

Processing failure cannot become compliance failure.

## Invariant 4

Original evidence cannot be overwritten by derived processing.

## Invariant 5

A correction cannot leave known stale downstream results presented as current.

## Invariant 6

Historical finalized records cannot be silently mutated.

## Invariant 7

Applicability precedes rule evaluation.

## Invariant 8

Unsupported information must not be fabricated.

## Invariant 9

Evidence insufficiency does not automatically prove non-compliance.

## Invariant 10

Hash integrity does not prove evidence truth/authenticity.

---

# 76. Architecture Anti-Patterns

Do not implement:

### Anti-pattern 1 — LLM as Legal Judge

```text
Image → LLM → "Illegal"
```

### Anti-pattern 2 — Frontend as Security Layer

```text
Button hidden = authorized
```

### Anti-pattern 3 — Local Deployment Source of Truth

```text
SQLite + local filesystem
```

for the deployed MVP.

### Anti-pattern 4 — Silent AI Guessing

```text
Unclear → guessed value
```

### Anti-pattern 5 — Mutable Finalized History

```text
Finalized → ordinary edit
```

### Anti-pattern 6 — Feature-First Architecture

Building many incomplete subsystems before the core journey works.

### Anti-pattern 7 — Microservice Theater

Creating services merely to match logical boxes.

---

# 77. One-Day MVP Technical Path

Implementation order:

```text
PHASE 0
Audit actual repository
       ↓
PHASE 1
Foundation + persistent deployment setup
       ↓
PHASE 2
Inspection + evidence
       ↓
PHASE 3
Image processing + PaddleOCR
       ↓
PHASE 4
Gemini extraction
       ↓
PHASE 5
Applicability + six rules
       ↓
PHASE 6
Findings + evidence
       ↓
PHASE 7
Inspector verification + result
       ↓
PHASE 8
End-to-end QA
       ↓
PHASE 9
Deployment + demonstration
```

---

# 78. Phase 0 Architecture Rule

The coding agent must inspect before modifying.

Phase 0 must answer:

```text
What architecture exists?
What code exists?
What persistence exists?
What is deployable?
What is missing?
What is broken?
What is the smallest path to the MVP?
```

No broad refactoring should occur before this audit.

---

# 79. Deployment Readiness Architecture

Before demonstration:

```text
Frontend
      ↓
Publicly reachable
      ↓
Backend
      ↓
Publicly reachable through secure API
      ↓
Persistent Database
      +
Persistent Object Storage
      ↓
AI integration configured
      ↓
Representative evidence tested
```

All critical dependencies must work in the deployed environment.

---

# 80. Testing Architecture

Testing should occur across layers:

```text
Unit
 ↓
Domain / Rule
 ↓
API
 ↓
Integration
 ↓
AI/OCR contract
 ↓
End-to-End
 ↓
Deployment smoke test
```

The highest priority is the end-to-end inspection journey.

---

# 81. MVP Release Gate

The architecture is considered implementation-ready for demonstration when:

```text
[ ] Evidence can be submitted
[ ] Original evidence persists
[ ] OCR works
[ ] AI extraction works
[ ] Structured output validates
[ ] Applicability works
[ ] Six checks work
[ ] Findings are evidence-linked
[ ] Inspector can verify/correct
[ ] Corrections recompute affected state
[ ] Technical failures are safe
[ ] Persistent deployment works
[ ] Security baseline passes
[ ] End-to-end test passes
```

Reviewer/finalization gates apply if those target capabilities are included in the MVP.

---

# 82. Technology Flexibility

The architecture locks responsibilities and boundaries more strongly than specific infrastructure products.

This is intentional.

The implementation team may replace:

- database provider
- object storage provider
- backend hosting platform
- worker/queue implementation
- AI provider in the future

provided the architectural contracts remain intact.

Current AI selection remains:

> Gemini 2.5 Flash

Current OCR selection remains:

> PaddleOCR

---

# 83. Architecture Change Control

Changes to the target architecture should be evaluated against:

1. Product requirements
2. MVP scope
3. lifecycle correctness
4. evidence integrity
5. security
6. deployment requirements
7. implementation effort
8. testing burden

A change must not be introduced simply because it appears technically interesting.

---

# 84. Relationship to Other Documents

| Document | Architecture Relationship |
|---|---|
| `01_PRD.md` | Product intent and requirements |
| `02_TRD.md` | Technical constraints |
| `03_Architecture.md` | Architecture authority |
| `04_Design.md` | UI/UX |
| `05_Domain_Specification.md` | Domain semantics |
| `06_Compliance_Rules.md` | Rule behavior |
| `07_State_Machine.md` | Lifecycle |
| `08_API_Specification.md` | API contracts |
| `09_Database_Specification.md` | Persistence |
| `10_Error_Handling.md` | Failure behavior |
| `11_Testing_and_Release_Gate.md` | Validation/release |
| `MVP_BUILD_SCOPE.md` | Current MVP boundary |
| `PROJECT_STATE.md` | Actual implementation state |

---

# 85. Final Architecture Statement

ComplianceScan is architected as a layered, evidence-centered, human-in-the-loop inspection system:

```text
┌────────────────────────────────────────────┐
│              HUMAN USERS                   │
│        Inspector / Reviewer                │
└────────────────────┬───────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────┐
│              WEB APPLICATION               │
└────────────────────┬───────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────┐
│             FASTAPI APPLICATION            │
│       Auth / Lifecycle / Orchestration      │
└──────────┬─────────┬───────────┬───────────┘
           │         │           │
           ▼         ▼           ▼
       Evidence    Processing   Domain
       Management  Pipeline     Services
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
          PaddleOCR          Gemini 2.5 Flash
              │                     │
              └──────────┬──────────┘
                         ▼
                Structured Observations
                         │
                         ▼
                  Applicability
                         │
                         ▼
                Controlled Rules
                         │
                         ▼
              Deterministic Assessment
                         │
                         ▼
                Findings + Evidence
                         │
                         ▼
              Inspector Verification
                         │
                         ▼
                 Reviewer Decision
                         │
                         ▼
              Immutable Final Snapshot
                         │
                ┌────────┴────────┐
                ▼                 ▼
         Persistent DB      Object Storage
```

The architectural goal is not maximum technical complexity.

It is a trustworthy chain from evidence to decision.

> **AI finds → Evidence supports → Backend validates → Inspector verifies → Reviewer decides.**

And for the one-day implementation:

> **ONE COMPLETE USER JOURNEY > MANY PARTIAL SUBSYSTEMS.**
