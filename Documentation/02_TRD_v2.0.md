# 02 — TECHNICAL REQUIREMENTS DOCUMENT (TRD)

**Project:** ComplianceScan  
**SIH'26 Problem Statement:** 26034  
**Document Version:** 2.0  
**Status:** Target technical requirements with controlled one-day MVP boundary

---

# 1. Purpose

This Technical Requirements Document defines the technical constraints, implementation requirements, technology responsibilities, deployment requirements, integration boundaries, reliability expectations, and engineering constraints for ComplianceScan.

It translates the product requirements in `01_PRD.md` into technical requirements without prematurely locking every production technology choice.

The technical design follows:

> **One complete, reliable, deployable vertical slice before broad subsystem coverage.**

---

# 2. Technical Objective

The one-day MVP must demonstrate a working path from packaged-commodity evidence to a human-verifiable compliance result.

```text
Evidence
   ↓
Image Processing
   ↓
PaddleOCR
   ↓
Gemini 2.5 Flash
   ↓
Structured Declarations
   ↓
Backend Validation
   ↓
Applicability
   ↓
Deterministic Rules
   ↓
Findings + Evidence
   ↓
Inspector Verification
   ↓
Persistent Result
```

The implementation must prioritize correctness, traceability, safe failure, and deployment readiness over feature quantity.

---

# 3. Technical Scope Model

This document distinguishes:

## 3.1 Target Technical System

The target system supports the full architecture described in:

- `03_Architecture.md`
- `08_API_Specification.md`
- `09_Database_Specification.md`
- `07_State_Machine.md`

## 3.2 Current One-Day MVP

The current MVP implements only the technical components required for the complete vertical slice.

The MVP boundary is authoritative in:

> `MVP_BUILD_SCOPE.md`

Actual implementation status is authoritative in:

> `PROJECT_STATE.md`

Target requirements must not automatically become MVP implementation requirements.

---

# 4. Core Engineering Principle

The system must follow:

> **AI finds → Backend validates → Applicability determines relevance → Rules evaluate → Evidence supports → Inspector verifies → Reviewer decides.**

No technical component may bypass this responsibility boundary merely for implementation convenience.

---

# 5. Technology Decision Status

The final production technology stack is intentionally **not fully locked**.

The implementation team may choose practical technologies that satisfy the requirements.

Current selected technologies:

| Area | Current Selection / Constraint |
|---|---|
| Frontend | React + Vite + Tailwind |
| Backend | Python + FastAPI |
| OCR | PaddleOCR |
| AI model | Gemini 2.5 Flash |
| Image/CV | OpenCV or equivalent practical CV tooling |
| Database | Persistent cloud-capable relational database required |
| File storage | Persistent object/file storage required |
| Frontend deployment | Vercel is a possible target |
| Backend deployment | Appropriate hosted backend platform |
| AI provider | Provider abstraction around Gemini |
| Local database | SQLite may be used for local development/testing only |
| Local filesystem | Local development/testing only; not deployed source of truth |

The exact database provider, object-storage provider, backend host, and final production configuration remain open until implementation/team discussion.

---

# 6. Frontend Requirements

## 6.1 Framework

The current frontend direction is:

> React + Vite + Tailwind

The frontend is responsible for:

- presentation
- user interaction
- evidence selection/upload initiation
- inspection views
- OCR/declaration visualization
- applicability/results presentation
- Inspector verification
- Reviewer workflow where implemented
- report/download actions
- status/error presentation

The frontend is not the authority for:

- authorization
- compliance decisions
- state transitions
- evidence integrity
- finalization
- persistence correctness

---

# 7. Backend Requirements

The current backend direction is:

> Python + FastAPI

The backend is authoritative for:

- authentication
- authorization
- input validation
- lifecycle transitions
- inspection ownership
- evidence management
- processing orchestration
- OCR/AI integration
- declaration validation
- applicability
- compliance evaluation
- findings
- corrections
- reviewer decisions
- finalization
- persistence
- audit events
- report generation orchestration

The backend must not rely on frontend controls for security or workflow enforcement.

---

# 8. Logical Architecture

The target system contains 25 logical components:

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
15. Inspector Review & Correction / Inspector Verification
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

These are logical responsibilities, not a requirement to deploy 25 separate services.

---

# 9. MVP Technical Architecture

The one-day implementation should concentrate on:

```text
┌───────────────────────────────┐
│ React + Vite + Tailwind       │
│ Web Application               │
└───────────────┬───────────────┘
                │ HTTPS/API
                ▼
┌───────────────────────────────┐
│ FastAPI Backend               │
│ Auth / Validation / Lifecycle │
│ Processing Orchestration      │
└───────────────┬───────────────┘
                │
       ┌────────┴─────────┐
       ▼                  ▼
 Evidence             Inspection
 Management           Management
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
 Deterministic Compliance Engine
       │
       ▼
 Findings + Evidence
       │
       ▼
 Inspector Verification
       │
       ▼
 Persistent Database + Object Storage
```

---

# 10. Responsibility Boundaries

## 10.1 Frontend

Does:

- display
- collect
- request
- render
- present state

Does not:

- decide compliance
- authorize users
- finalize records
- calculate authoritative hashes
- mutate database directly

## 10.2 Backend

Does:

- validate
- authorize
- orchestrate
- persist
- enforce lifecycle
- calculate authoritative state

## 10.3 OCR

Does:

- read text
- locate text
- report confidence

Does not:

- interpret legal meaning
- determine applicability
- determine compliance

## 10.4 AI

Does:

- interpret OCR observations
- extract declarations
- normalize values
- identify conflicts/uncertainty

Does not:

- make final legal decisions
- invent values
- alter rules
- finalize inspections

## 10.5 Rules

Do:

- evaluate structured facts
- apply controlled requirements
- return deterministic system assessments

Do not:

- infer unsupported facts
- bypass applicability
- erase evidence uncertainty

## 10.6 Inspector

Does:

- verify
- correct
- supplement
- submit

## 10.7 Reviewer

Does:

- independently review
- confirm/correct/override
- request evidence
- finalize

---

# 11. Cloud Deployment Requirement

The deployed MVP must not depend on a developer's local machine.

Required:

```text
Hosted Frontend
       ↓
Hosted Backend
       ↓
Persistent Database
       +
Persistent Object/File Storage
       +
External AI/OCR dependencies as required
```

A local SQLite database or local filesystem may be used for development/testing but must not be treated as the deployed source of truth.

---

# 12. Persistence Requirements

The deployed system must persist:

- users
- inspections
- product/context data
- evidence metadata
- evidence storage references
- evidence hashes
- OCR results
- AI processing records
- declarations
- applicability results
- assessments
- findings
- Inspector corrections
- audit events
- reviewer decisions where implemented
- final snapshots where implemented
- report metadata

Persistence must survive:

- backend restart
- frontend redeployment
- normal application lifecycle events

---

# 13. Database Requirements

A persistent relational database is required for the deployed MVP.

Requirements:

- stable primary keys
- referential integrity
- transaction support
- concurrent access appropriate for demonstration/deployment
- migration capability
- indexed inspection/retrieval fields
- audit/event persistence
- historical record protection

The exact database engine/provider remains open.

SQLite is acceptable only as a local development/test option where appropriate.

---

# 14. Object/File Storage Requirements

Original package evidence must be stored in persistent storage appropriate for deployment.

Requirements:

- persistent storage
- protected access
- non-public-by-default evidence
- stable object references
- Evidence IDs
- metadata
- SHA-256 integrity hash
- separation of original and derived artifacts
- access authorization

Local filesystem storage is not sufficient as the deployed evidence source of truth.

---

# 15. Evidence Upload Requirements

The backend must validate:

- authenticated requester
- authorization
- file size
- MIME/type
- decodability
- supported image format
- inspection association

The server should generate the Evidence ID.

Example:

```text
EVD-000042
```

The original evidence should not be silently overwritten.

A new image is a new evidence item.

---

# 16. Evidence Integrity

For each accepted original evidence item:

```text
Original Image
      ↓
Server Validation
      ↓
SHA-256
      ↓
Evidence ID
      ↓
Persistent Storage
      ↓
Metadata + Audit
```

Hashing provides tamper-evident integrity/change detection.

It does not prove that the image is truthful or authentic.

---

# 17. Image Processing Requirements

Image processing may perform:

- orientation correction
- resizing
- preprocessing
- brightness/contrast adjustment
- denoising
- crop generation
- quality assessment

Important rule:

> Processing must not overwrite the original evidence.

Use:

```text
Original Evidence
      ↓
Analysis Copy
      ↓
OCR / CV
```

The original remains preserved.

---

# 18. Image Quality Requirements

The system should detect relevant quality problems such as:

- severe blur
- poor contrast
- extreme brightness/darkness
- unreadable orientation
- insufficient visible coverage

Quality problems should be surfaced as observations or processing conditions.

They must not automatically become legal non-compliance findings.

---

# 19. OCR Requirements

Selected MVP OCR:

> **PaddleOCR**

The OCR layer should produce:

- recognized text
- bounding boxes
- OCR confidence
- source evidence reference
- OCR run identifier

Example conceptual result:

```json
{
  "text": "MRP ₹199",
  "confidence": 0.94,
  "bbox": [120, 420, 350, 475],
  "evidence_id": "EVD-000042"
}
```

The exact schema is defined by the API/domain specifications.

---

# 20. OCR Failure Requirements

OCR failure must be explicit.

Examples:

```text
OCR service unavailable
→ PROCESSING_FAILED

No readable text
→ observation may be NOT_OBSERVED / UNREADABLE

Low-confidence text
→ preserve confidence and uncertainty
```

OCR failure must never automatically produce:

> POTENTIAL_NON_COMPLIANCE

---

# 21. AI Integration Requirements

Selected MVP model:

> **Gemini 2.5 Flash**

The backend should use a provider abstraction where practical.

Conceptually:

```text
AI Provider Interface
       │
       └── Gemini 2.5 Flash
```

This prevents business logic from being tightly coupled to a provider-specific implementation.

---

# 22. AI Input Contract

The AI should primarily receive controlled observations such as:

- OCR text
- bounding boxes
- OCR confidence
- evidence/source references
- supported declaration schema
- controlled instructions

The system should avoid treating arbitrary model output as trusted application data.

---

# 23. AI Output Contract

AI output must be:

- structured
- schema validated
- source-linked
- uncertainty-aware
- domain validated

Each accepted declaration should preserve, as applicable:

- field
- value
- normalized value
- observation status
- AI extraction confidence
- source OCR regions
- source evidence references

---

# 24. AI Observation Status

Supported states:

```text
OBSERVED
NOT_OBSERVED
UNCERTAIN
UNREADABLE
CONFLICTING
```

The application must not collapse these into a single boolean such as:

```text
found = true/false
```

---

# 25. Confidence Requirements

The system must keep distinct:

```text
OCR Confidence
AI Extraction Confidence
Evidence Sufficiency
Compliance Result
```

No single confidence score should be presented as a universal “legal confidence.”

Thresholds should be calibrated empirically rather than introducing arbitrary universal cutoffs without validation.

---

# 26. AI No-Guessing Requirement

The model must not:

- fabricate declarations
- fill missing values from assumptions
- silently choose between conflicting values
- convert uncertainty into certainty

Example:

```text
OCR:
"MRP 1?9"

AI:
UNCERTAIN

Not:
MRP = 199
```

---

# 27. AI Failure Handling

The backend must distinguish:

### Provider unavailable

```text
PROCESSING_FAILED
```

### Malformed response

```text
Controlled retry
       ↓
If still invalid
       ↓
PROCESSING_FAILED
```

### Conflicting declarations

```text
Preserve values
       ↓
CONFLICTING
       ↓
REQUIRES_REVIEW
```

### Ambiguous interpretation

```text
UNCERTAIN
       ↓
Human verification
```

---

# 28. Applicability Engine Requirements

Applicability must run before compliance evaluation.

```text
Structured Facts
      ↓
Applicability
      ↓
Applicable Requirements
      ↓
Compliance Engine
```

The MVP supports explicit applicability logic for the supported scope.

It is not a universal statutory exception engine.

---

# 29. Compliance Rule Requirements

The MVP uses a controlled rule snapshot covering six checks:

1. Manufacturer / Packer / Importer
2. Common / Generic Product Name
3. Net Quantity + Standard Unit
4. Month / Year of Manufacture / Packing / Import
5. MRP Inclusive of All Taxes
6. Consumer Care Details

Country of Origin is applicability-driven.

The exact legal rule definitions belong in:

> `06_Compliance_Rules.md`

---

# 30. Deterministic Compliance Engine

The compliance engine must evaluate structured facts against controlled rules.

Conceptually:

```text
Facts
 +
Applicability
 +
Rule Snapshot
      ↓
Deterministic Evaluation
      ↓
System Assessment
```

The engine must not use an LLM as the authoritative legal rule evaluator.

---

# 31. Result Requirements

The system supports:

```text
PASS
POTENTIAL_NON_COMPLIANCE
REQUIRES_REVIEW
NOT_APPLICABLE
INCOMPLETE
PROCESSING_FAILED
```

Required distinctions:

```text
NOT_APPLICABLE ≠ PASS
INCOMPLETE ≠ NON_COMPLIANCE
PROCESSING_FAILED ≠ NON_COMPLIANCE
UNREADABLE ≠ MISSING
NOT_OBSERVED ≠ PROVEN ABSENT
```

---

# 32. Findings Requirements

Each material finding should preserve:

- finding identifier
- requirement
- assessment
- reason
- rule reference
- evidence references
- source region/crop where available
- provenance
- relevant observation
- processing/rule version information

The finding must be explainable.

---

# 33. Evidence Generation

The system may generate:

- highlighted image regions
- crops
- OCR-region references
- finding evidence links

Derived evidence must remain traceable to original evidence.

Example:

```text
Original Evidence
       ↓
OCR Region
       ↓
Highlight/Crop
       ↓
Finding
```

---

# 34. Visual Analysis Requirements

Visual analysis may assist with:

- readability
- visibility
- placement/evidence coverage
- font-size warnings
- image quality

It must not claim universal legal certainty from insufficient visual information.

For example:

```text
Estimated font-size warning
        ≠
Definitive statutory violation
```

---

# 35. Inspector Verification Requirements

The Inspector interface must support:

- reviewing extracted declarations
- correcting incorrect extraction
- recording manual observations
- verifying applicability
- reviewing findings
- supplementing evidence where supported
- submitting the inspection

The Inspector's correction is a change to underlying observed data, not merely a cosmetic UI edit.

---

# 36. Correction Invalidation Requirement

The system must implement:

> **Upstream correction → invalidate affected downstream state → recompute → preserve prior state/history → audit transition.**

Example:

```text
Declaration corrected
      ↓
Affected applicability invalidated
      ↓
Affected assessment invalidated
      ↓
Affected finding recalculated
      ↓
New result persisted
      ↓
Correction audited
```

The exact dependency graph may be implemented incrementally, but stale downstream results must not be presented as current.

---

# 37. Submission Boundary

Before submission:

```text
Inspector-owned working state
```

After submission:

```text
Reviewer-owned review state
```

If Reviewer requests evidence:

```text
Reviewer
   ↓
Evidence Request
   ↓
Inspector
   ↓
Supplement / Correct / Unable to Establish
   ↓
Reprocess if required
   ↓
Resubmit
```

After finalization:

```text
Read-only
```

---

# 38. Reviewer Requirements

Where Reviewer workflow is implemented, the backend must support:

- Reviewer authorization
- submitted-inspection access
- evidence review
- declaration review
- applicability review
- findings review
- audit/history review
- confirmation
- correction/override
- evidence requests
- finalization

Reviewer overrides must require a reason.

---

# 39. Role Separation

The operational roles are:

```text
Inspector
Reviewer
```

An Inspector should not finalize their own inspection.

The Reviewer should independently review the submitted inspection.

Technical administration, if required, is separate from the operational inspection workflow.

---

# 40. State Machine Requirements

Lifecycle transitions must be backend-controlled.

The system must reject invalid transitions even if a malicious client calls the API directly.

Examples:

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

The exact state model is authoritative in:

> `07_State_Machine.md`

The MVP may use a controlled subset.

---

# 41. Audit Requirements

Material actions should produce auditable events.

Examples:

- inspection created
- evidence added
- processing started
- processing failed
- declaration corrected
- applicability changed
- assessment recalculated
- evidence requested
- review decision recorded
- finalization performed

Audit entries should preserve:

- actor
- action
- timestamp
- affected object
- previous state/value where applicable
- new state/value where applicable
- reason/source where applicable

---

# 42. Finalization Requirements

Finalization should be atomic.

Conceptually:

```text
Validate
   ↓
Build Final Snapshot
   ↓
Persist Snapshot + Final Decision
   ↓
Audit
   ↓
FINALIZED
```

The finalized snapshot should preserve/refer to all information required to reconstruct the final inspection state.

---

# 43. Finalized Record Protection

After finalization:

- normal editing is disabled
- backend mutation is rejected
- original evidence remains immutable
- historical audit remains intact
- reports derive from the final snapshot

No UI-only lock is sufficient.

---

# 44. Rule Versioning Requirements

A historical inspection must retain the rule snapshot/version used for its assessment.

Future rule changes must not silently recalculate finalized historical inspections.

Conceptually:

```text
Inspection A
   ↓
Rule Snapshot v1
   ↓
Finalized

Later:
Rule Snapshot v2

Inspection A remains based on v1
```

---

# 45. Report Requirements

The target system supports:

- preliminary report
- final report
- PDF output
- editable output where required

Reports should be generated from the corresponding inspection state/snapshot.

A report-generation failure must not corrupt or roll back an already finalized inspection.

---

# 46. Search and Repository Requirements

The target system should support retrieval by:

- inspection ID
- date
- state
- result
- product information
- relevant filters

The one-day MVP should implement only retrieval needed for its deployed demonstration.

---

# 47. Dashboard Requirements

Target metrics may include:

- inspection count
- result distribution
- review backlog
- processing failures
- common findings
- completion metrics

Dashboard implementation is secondary to the core inspection journey in the one-day MVP.

---

# 48. Physical ↔ Online Verification

This is a target capability, not a one-day MVP dependency.

The technical design may compare:

```text
Physical Evidence
      ↕
Online Product Information
```

Potential comparison fields include:

- product identity
- manufacturer
- quantity
- MRP
- consumer care
- other supported declarations

A mismatch is represented as:

> Cross-Channel Inconsistency

It must not automatically become a legal violation.

No internet-wide crawling is required for the MVP.

---

# 49. API Requirements

The API must provide authoritative backend operations for the implemented MVP.

Minimum conceptual API areas:

```text
Authentication
Inspection
Evidence
Processing
OCR
Declaration Extraction
Applicability
Assessment
Findings
Inspector Verification
Result
```

If Reviewer functionality is implemented:

```text
Review Queue
Reviewer Decision
Evidence Requests
Finalization
Reports
```

API details belong in:

> `08_API_Specification.md`

---

# 50. API Security

Every protected API must enforce:

- authentication
- authorization
- object ownership/access checks
- lifecycle-state checks
- input validation
- safe error responses

The API must not trust:

- frontend role labels
- client-provided ownership
- client-provided finalization state
- client-provided evidence hashes as authoritative values

---

# 51. API Idempotency

Operations that can be retried should be designed to avoid unintended duplication.

Particularly:

- evidence upload/finalization where applicable
- processing initiation
- report generation
- reviewer decision submission

Exact idempotency contracts belong in `08_API_Specification.md`.

---

# 52. Concurrency

The backend should prevent conflicting state mutations.

Examples:

```text
Reviewer finalizes
      +
Inspector attempts mutation
      ↓
Backend rejects stale/invalid operation
```

Optimistic versioning, transaction checks, or equivalent controls may be used.

The exact mechanism remains an implementation choice.

---

# 53. Authentication Requirements

The target operational system requires authenticated users.

Authentication must establish:

- user identity
- active status
- role/permissions

Authentication implementation technology is not locked by this document.

---

# 54. Authorization Requirements

Authorization is backend-enforced.

Minimum operational roles:

```text
INSPECTOR
REVIEWER
```

Permission examples:

| Operation | Inspector | Reviewer |
|---|---:|---:|
| Create inspection | Yes | As authorized |
| Add evidence | Yes | As authorized |
| Start analysis | Yes | As authorized |
| Correct extraction | Yes | Review context |
| Submit | Yes | No |
| Review submitted record | No | Yes |
| Override assessment | No | Yes |
| Request evidence | No | Yes |
| Finalize | No | Yes |

Exact permissions are authoritative in the API/domain specifications.

---

# 55. Secret Management

Secrets must remain server-side.

Examples:

- Gemini API key
- database credentials
- storage credentials
- signing/secrets
- authentication secrets

Never expose provider credentials in:

- frontend source
- browser bundles
- client-side environment variables intended for public exposure
- logs
- reports

---

# 56. File Security

Uploaded files must be treated as untrusted input.

The backend should:

- validate MIME/type
- validate file size
- decode safely
- reject unsupported content
- generate storage names/IDs
- avoid path traversal
- prevent public exposure by default
- store outside executable web paths where applicable

---

# 57. Error Taxonomy

The technical system should distinguish:

```text
VALIDATION_ERROR
AUTHENTICATION_ERROR
AUTHORIZATION_ERROR
NOT_FOUND
CONFLICT
INVALID_STATE
EVIDENCE_ERROR
OCR_ERROR
AI_ERROR
PROCESSING_FAILED
APPLICABILITY_ERROR
RULE_EVALUATION_ERROR
STORAGE_ERROR
REPORT_ERROR
INTERNAL_ERROR
```

These technical errors must remain distinct from compliance results.

---

# 58. Safe Error Mapping

Example:

```text
Gemini API unavailable
        ↓
AI_ERROR / PROCESSING_FAILED
        ↓
Inspection cannot be falsely marked non-compliant
```

Similarly:

```text
Database unavailable
        ↓
STORAGE_ERROR
        ↓
No fabricated compliance result
```

---

# 59. Observability Requirements

The deployed MVP should provide enough logging to diagnose:

- request failures
- processing failures
- OCR failures
- AI failures
- storage failures
- invalid lifecycle transitions
- finalization failures

Logs must avoid exposing:

- API keys
- credentials
- unnecessary sensitive evidence
- private tokens

---

# 60. Processing Architecture

Long-running processing should be separated conceptually from synchronous request handling where required.

Target flow:

```text
User Request
    ↓
Create Processing Job
    ↓
Worker / Processing Layer
    ↓
Image Processing
    ↓
OCR
    ↓
AI
    ↓
Validation
    ↓
Applicability
    ↓
Compliance
    ↓
Findings
    ↓
Persist
```

The exact worker/queue technology is not locked for the one-day MVP.

For a small deployment, a simpler implementation may be acceptable if it remains reliable.

---

# 61. Processing State Requirements

The system should distinguish states such as:

```text
QUEUED
PROCESSING
COMPLETED
FAILED
RETRYING
```

Processing failure must not be converted into a compliance failure.

---

# 62. Retry Requirements

Retries must be controlled.

Appropriate retry candidates:

- transient AI provider failures
- transient storage failures
- temporary network failures

Do not blindly retry:

- malformed user input
- invalid files
- invalid state transitions
- deterministic rule errors

Repeated failures should become explicit failure state.

---

# 63. Data Model Requirements

The target relational model should represent at least:

```text
User
Role
Inspection
Product / Context
Evidence
Evidence Hash / Provenance
OCR Run
OCR Region
AI Run
Declaration
Declaration Source
Applicability
Assessment
Finding
Inspector Correction
Evidence Request
Reviewer Decision
Final Snapshot
Audit Event
Rule Snapshot
Report
```

The exact schema is authoritative in:

> `09_Database_Specification.md`

---

# 64. Data Provenance

Material extracted information should be traceable through:

```text
Declaration
   ↓
OCR Region(s)
   ↓
Evidence
```

Findings should be traceable through:

```text
Finding
   ↓
Assessment
   ↓
Declaration / Observation
   ↓
Evidence
```

This provenance chain is a core technical requirement.

---

# 65. Original-vs-Derived Data

The system must distinguish:

```text
Original
- package image
- original uploaded evidence

Derived
- resized analysis image
- OCR output
- crop
- highlight
- AI interpretation
```

Derived artifacts must never silently replace original evidence.

---

# 66. Data Deletion Requirements

Original evidence and finalized records must be protected from ordinary deletion.

The target deletion policy should consider:

- inspection state
- evidence dependency
- audit requirements
- legal/history requirements
- authorization

A normal user operation must not destroy finalized historical integrity.

---

# 67. Deployment Topology

A practical deployed MVP can follow:

```text
                 Internet
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
          ┌──────▼─┐ ┌─▼─────────────┐
          │Cloud DB│ │Object Storage │
          └────────┘ └───────────────┘
                 │
                 ▼
          External AI Provider
          Gemini 2.5 Flash
```

OCR execution may be colocated with the backend or handled through an appropriate processing environment.

The architecture must remain deployable rather than assuming localhost-only services.

---

# 68. Environment Separation

At minimum, distinguish:

```text
Development
Testing
Deployment/Demo
```

Environment-specific:

- credentials
- API endpoints
- database connection
- storage connection
- AI configuration

must not be hard-coded.

---

# 69. Configuration Requirements

Configuration should be environment-driven.

Examples:

```text
DATABASE_URL
STORAGE_CONFIGURATION
GEMINI_API_KEY
APPLICATION_SECRET
CORS_ALLOWED_ORIGINS
```

Names are illustrative; exact configuration is implementation-defined.

Secrets must not be committed to source control.

---

# 70. CORS / Network Security

The backend should explicitly configure allowed frontend origins.

Do not use unrestricted production CORS unless justified.

All production communication should use HTTPS.

---

# 71. API Documentation

FastAPI's generated API documentation may be used during development.

However, generated documentation does not replace:

> `08_API_Specification.md`

The specification remains the contract for intended behavior.

---

# 72. Testing Requirements

The MVP must test the complete journey.

Priority:

## P0

- inspection creation
- evidence upload
- image processing
- OCR
- AI extraction
- applicability
- six compliance checks
- findings
- Inspector verification
- persistence
- deployment

## P1

- malformed files
- OCR failure
- AI failure
- conflicting extraction
- unreadable evidence
- invalid transitions
- authorization
- correction/recomputation
- reviewer/finalization where implemented

The release gate is authoritative in:

> `11_Testing_and_Release_Gate.md`

---

# 73. Representative Evidence Testing

Representative package images must be used to validate:

- OCR quality
- declaration extraction
- source mapping
- applicability
- rule evaluation
- evidence generation
- UI presentation

Technology selection is considered validated through implementation testing, not assumption.

---

# 74. AI Testing

AI tests should include:

- normal readable declaration
- missing declaration
- ambiguous declaration
- conflicting declarations
- OCR noise
- unsupported text
- malformed provider output
- provider failure

Expected behavior must emphasize preservation of uncertainty.

---

# 75. Rule Testing

Each supported MVP rule should have deterministic tests for:

```text
PASS
POTENTIAL_NON_COMPLIANCE
REQUIRES_REVIEW
NOT_APPLICABLE
INCOMPLETE
```

where applicable.

Technical processing failures must be tested separately.

---

# 76. Security Testing

Minimum MVP security checks:

- unauthorized API access
- wrong-role access
- cross-inspection evidence access
- invalid state mutation
- path traversal/file upload issues
- secret exposure
- finalized-record mutation
- malformed AI response
- malicious/invalid upload

---

# 77. Performance Expectations

No large-scale performance SLA is required for the one-day MVP.

The MVP should nevertheless:

- avoid unnecessary repeated AI calls
- avoid blocking the UI without status feedback
- prevent duplicate processing where possible
- store processing state
- provide useful progress/failure feedback

Optimization beyond the demonstration workload is deferred.

---

# 78. Scalability Direction

The target architecture should permit future scaling of:

- API
- OCR processing
- AI calls
- background jobs
- object storage
- database workloads

But the MVP should not introduce distributed infrastructure unless required.

Do not build microservices solely because the target architecture contains multiple logical components.

---

# 79. Availability Expectations

The demonstration deployment should be sufficiently stable for judge access.

A formal production SLA is outside the one-day MVP.

The system should fail visibly and safely rather than silently losing data.

---

# 80. Dependency Management

External dependencies must be:

- explicitly declared
- versioned/pinned where practical
- tested
- replaceable where appropriate

Critical dependencies include:

- OCR engine
- AI provider
- database driver
- object storage SDK
- image processing libraries

---

# 81. Provider Abstraction

Where a third-party provider creates strong coupling, use a small abstraction layer.

Most important candidates:

```text
AI Provider
Storage Provider
```

The abstraction must remain lightweight.

Do not create abstraction layers that provide no practical value within the MVP.

---

# 82. Frontend State Requirements

The UI should distinguish:

```text
Loading
Processing
Ready
Needs Verification
Error
Submitted
Review
Finalized
```

The displayed state must come from authoritative backend data.

---

# 83. Backend State Authority

The backend is the source of truth for:

- inspection state
- ownership
- processing state
- applicability
- assessment
- finalization
- permissions

The frontend may cache/display state but cannot authoritatively define it.

---

# 84. Data Consistency

Material operations should be transactional where appropriate.

For example:

```text
Correction
 +
Invalidation
 +
Audit Event
```

should not leave the database in a state where the correction exists but stale dependent results are presented as final.

---

# 85. Atomic Finalization

If Reviewer finalization is implemented, finalization should ensure:

```text
Decision
+
Snapshot
+
Audit
```

are committed consistently.

If the transaction cannot be completed, the inspection must not appear finalized.

---

# 86. Report Failure Isolation

If:

```text
Finalize = SUCCESS
Report = FAILURE
```

then:

```text
Inspection = FINALIZED
Report = RETRYABLE ERROR
```

Report generation must not corrupt the inspection lifecycle.

---

# 87. Historical Reproducibility

A historical inspection should retain enough provenance to explain:

- what evidence was used
- what extraction occurred
- what corrections occurred
- what rule snapshot was used
- what assessment was generated
- what Reviewer decision was made
- what final state was stored

---

# 88. Legal-Rule Update Boundary

The MVP uses a controlled rule snapshot.

It does not require:

- automated legal website monitoring
- automatic rule ingestion
- automatic legal interpretation
- live statutory crawling

A future rule-management system may be introduced separately.

---

# 89. Technical Non-Goals

The one-day implementation must not become:

- a general-purpose OCR platform
- an autonomous legal decision engine
- a full enterprise case-management platform
- an internet crawler
- a universal packaging-layout analyzer
- a universal statutory-rule engine
- a multi-service distributed platform without need
- a large analytics platform

---

# 90. Engineering Judgment Rules

When implementation choices are unspecified:

1. Prefer the simplest reliable option.
2. Preserve cloud deployability.
3. Preserve persistent data.
4. Preserve evidence provenance.
5. Preserve human authority.
6. Avoid irreversible design decisions unless necessary.
7. Avoid feature creep.
8. Prefer a complete tested path over isolated sophistication.

---

# 91. Agent Implementation Constraint

Antigravity or another coding agent must not infer that every target component must be implemented during the one-day MVP.

Before coding, the agent must:

- read the control documents
- inspect the repository
- inspect actual implementation state
- compare current state against MVP scope
- identify blockers
- report proposed implementation plan
- wait for the required human checkpoint

Engineering-agent behavior is governed by:

> `AGENT_ENGINEERING_PROTOCOL.md`

---

# 92. Phase 0 Requirement

Phase 0 is an audit, not a coding phase.

The agent should establish:

```text
What exists?
What works?
What is missing?
What is broken?
What is required for the vertical slice?
What can be deferred?
```

The agent must not perform broad refactoring before the implementation state is understood.

---

# 93. Phase Sequence

The technical execution sequence is:

```text
PHASE 0 — Audit
        ↓
PHASE 1 — Foundation
        ↓
PHASE 2 — Inspection + Evidence
        ↓
PHASE 3 — Image Processing + PaddleOCR
        ↓
PHASE 4 — Gemini Extraction
        ↓
PHASE 5 — Applicability + Six Rules
        ↓
PHASE 6 — Findings + Evidence
        ↓
PHASE 7 — Inspector Verification + Result
        ↓
PHASE 8 — End-to-End QA + Output
        ↓
PHASE 9 — Deployment + Demonstration
```

---

# 94. Definition of Technical Readiness

The MVP is technically ready when:

```text
[ ] Frontend is deployed
[ ] Backend is deployed
[ ] Persistent database is connected
[ ] Persistent object/file storage is connected
[ ] Evidence upload works
[ ] Original evidence remains preserved
[ ] OCR works on representative evidence
[ ] Gemini extraction is schema validated
[ ] Applicability works
[ ] Six rules work
[ ] Findings contain evidence provenance
[ ] Inspector verification works
[ ] Corrections do not leave stale results
[ ] Technical failures are distinguished from compliance results
[ ] Security checks pass
[ ] End-to-end test passes
[ ] Judge demonstration works
```

These are release gates only after actual verification.

---

# 95. Technical Definition of Done

A feature is not considered complete merely because:

```text
UI exists
```

or:

```text
API returns 200
```

A complete vertical-slice feature requires:

```text
UI
 +
Backend Contract
 +
Validation
 +
Persistence
 +
Failure Handling
 +
Relevant Test
 +
Evidence/Provenance where applicable
```

---

# 96. Final Technical Principle

ComplianceScan should be engineered as a trustworthy inspection-assistance system, not as an AI demo.

The core technical chain is:

```text
Evidence
  ↓
OCR
  ↓
AI Understanding
  ↓
Validated Structured Data
  ↓
Applicability
  ↓
Deterministic Rules
  ↓
Evidence-Backed Findings
  ↓
Human Verification
  ↓
Independent Review
  ↓
Immutable Historical Record
```

The current one-day engineering priority is:

> **Build the smallest system that can execute this chain reliably and persistently in a deployed environment.**

The governing implementation principle is:

> **ONE COMPLETE USER JOURNEY > MANY PARTIAL SUBSYSTEMS.**
