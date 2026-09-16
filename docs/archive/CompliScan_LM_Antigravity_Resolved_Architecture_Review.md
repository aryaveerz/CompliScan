# ComplianceScan / CompliScan LM

## Architecture Review --- Resolved Antigravity Items

**Purpose:** Obtain an independent Antigravity review of the
architecture decisions that were proposed during the previous
architecture review and have now been approved/locked.

**Review status:** Human-approved decisions are FINAL for the current
MVP unless a genuine contradiction, implementation blocker, security
issue, or critical omission is identified.

**Important instruction to Antigravity:**\
This document is a review package, not an invitation to redesign the
project. Do not silently change or implement anything. Review the
decisions as a coherent set, identify contradictions or risks, and
propose changes only if genuinely necessary. Do not introduce feature
creep.

------------------------------------------------------------------------

# 1. Project Context

## Project

**CompliScan LM / ComplianceScan**

A software system intended to assist inspection of packaged commodities
under the Legal Metrology (Packaged Commodities) Rules, 2011 within the
defined MVP scope.

The system is intended to:

-   capture product/package evidence;
-   extract visible declarations from package images;
-   structure those observations;
-   determine which requirements apply;
-   evaluate predefined requirements;
-   generate evidence-linked findings;
-   keep an Inspector and Reviewer in the workflow;
-   preserve an auditable inspection history;
-   produce a finalized inspection record and report.

The system is an **inspection-assistance system**, not an autonomous
statutory enforcement authority.

## Core philosophy

> **AI finds → Evidence proves → Officer decides.**

Primary workflow:

``` text
PRODUCT INPUT
Physical Package / Online Listing
        ↓
AI-POWERED ANALYSIS
Image Quality + OCR + Semantic Extraction
        ↓
DECLARATION EXTRACTION
Manufacturer / Packer / Importer
Net Quantity
MRP
Dates
Consumer Care
Other applicable information
        ↓
PRODUCT & PACKAGE CONTEXT
        ↓
APPLICABILITY ENGINE
Determine which requirements apply
        ↓
COMPLIANCE ANALYSIS
Deterministic Rule Engine
        ↓
COMPLIANCE RESULT
PASS / POTENTIAL_NON_COMPLIANCE /
REQUIRES_REVIEW / NOT_APPLICABLE /
INCOMPLETE / PROCESSING_FAILED
        ↓
EVIDENCE GENERATION
Rule + Reason + Highlighted Evidence + Confidence
        ↓
INSPECTOR VERIFICATION
        ↓
REVIEWER DECISION
        ↓
FINALIZE
        ↓
REPORT + HISTORY + AUDIT + DASHBOARD
```

------------------------------------------------------------------------

# 2. Locked Safety / Decision Principles

## AI/legal boundary

1.  PaddleOCR is a perception layer.
2.  PaddleOCR extracts visible text, locations and OCR confidence.
3.  Gemini performs semantic extraction/structuring.
4.  Gemini does not make the legal compliance decision.
5.  Backend schema validation, applicability logic and deterministic
    compliance rules are authoritative.
6.  Inspector verification is mandatory before submission.
7.  Reviewer makes the independent final decision.
8.  AI uncertainty must not be converted into a legal conclusion.
9.  Confidence thresholds are engineering parameters, not legal
    thresholds.
10. OCR confidence, AI extraction confidence, evidence sufficiency and
    compliance result are separate concepts.

## No guessing

The system must distinguish:

-   not observed;
-   unreadable;
-   absent;
-   uncertain;
-   conflicting;
-   processing failed.

In particular:

-   NOT_OBSERVED is not automatically missing.
-   Unreadable is not automatically missing.
-   Conflicting values go to review.
-   Lack of evidence does not prove a fact.
-   Processing failure is not non-compliance.

## Locked result vocabulary

``` text
PASS
POTENTIAL_NON_COMPLIANCE
REQUIRES_REVIEW
NOT_APPLICABLE
INCOMPLETE
PROCESSING_FAILED
```

Important distinctions:

-   NOT_APPLICABLE ≠ PASS
-   INCOMPLETE ≠ POTENTIAL_NON_COMPLIANCE
-   PROCESSING_FAILED ≠ NON_COMPLIANCE

------------------------------------------------------------------------

# 3. MVP Compliance Scope

Six core compliance domains are locked:

1.  Manufacturer / Packer / Importer identity and address
2.  Common / generic commodity name
3.  Net quantity + standard unit
4.  Month / year of manufacture / packing / import
5.  MRP inclusive of all taxes
6.  Consumer care details

## Country of Origin

Country of Origin is applicability-driven and is not treated as a
seventh universal compliance check.

Conceptual handling:

``` text
Imported = YES
    → Country of Origin applicable

Imported = NO
    → NOT_APPLICABLE

Imported = UNKNOWN
    → REVIEW / INCOMPLETE / block submission as appropriate
```

## Deliberately excluded from current MVP

-   Unit Sale Price
-   USP / User-facing USP declaration
-   broad category-specific rules
-   universal legal font-size verdict
-   universal packaging-placement legal verdict
-   dynamic automatic regulatory-update pipeline
-   universal coverage of every packaged-commodity category

Font size and placement may be assessed as visual/evidence observations,
but the MVP does not claim definitive legal judgement from ordinary
photographs.

------------------------------------------------------------------------

# 4. Locked Operational Workflow

``` text
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

``` text
FINALIZED
   ├──→ PDF REPORT
   ├──→ HISTORY / AUDIT
   ├──→ SEARCH
   └──→ DASHBOARD / METRICS
```

Reports and history are outputs, not additional lifecycle stages.

------------------------------------------------------------------------

# 5. Locked Lifecycle / State Model

## Master lifecycle

``` text
DRAFT
EVIDENCE_UPLOADED
EXTRACTED
APPLICABILITY_EVALUATED
EVALUATED
IN_VERIFICATION
SUBMITTED_FOR_REVIEW
REQUIRES_REVISION
FINALIZED
```

## Processing state

``` text
IDLE
PROCESSING
FAILED
```

## Compliance result

``` text
PASS
POTENTIAL_NON_COMPLIANCE
REQUIRES_REVIEW
NOT_APPLICABLE
INCOMPLETE
PROCESSING_FAILED
```

## Finalization

``` text
UNFINALIZED
READ_ONLY
```

These dimensions remain conceptually separate. Individual finding states
must not overwrite the master inspection lifecycle.

------------------------------------------------------------------------

# 6. Locked Roles

## Inspector

The Inspector can:

-   create inspections;
-   capture evidence;
-   start analysis;
-   view OCR and extracted declarations;
-   correct extracted values;
-   add manual observations;
-   provide supplemental evidence;
-   verify applicability/compliance observations;
-   submit for review;
-   respond to evidence/revision requests.

The Inspector cannot:

-   finalize;
-   act as the final independent Reviewer for the same inspection;
-   modify controlled legal rules;
-   modify or delete accepted primary evidence;
-   silently alter audit history;
-   mutate finalized records.

## Reviewer

The Reviewer can:

-   inspect submitted cases;
-   inspect evidence, OCR, declarations, applicability and findings;
-   confirm findings;
-   make explicit determinations/overrides;
-   request revision;
-   request supplemental evidence;
-   finalize the inspection.

The Reviewer cannot:

-   silently edit underlying extracted declarations;
-   modify controlled legal rules;
-   delete finalized history;
-   mutate finalized records.

## Separation principle

``` text
UNDERLYING DATA
    → Inspector

ASSESSMENT / DECISION
    → Reviewer
```

Reviewer and submitting Inspector must be different people for the same
inspection.

------------------------------------------------------------------------

# 7. Locked Evidence Model

``` text
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

## Evidence rules

-   Draft uploads can be removed/replaced before acceptance.
-   Accepted Primary Evidence is immutable.
-   New evidence receives a new Evidence ID.
-   Every accepted evidence asset has a SHA-256 hash.
-   Original evidence is preserved.
-   Derived evidence references source primary evidence.
-   Findings trace to derived evidence and ultimately to original
    evidence.
-   Supplemental evidence is separate from primary evidence.
-   Evidence requests specify the fact/condition that needs to be
    established.
-   Evidence Request IDs may look like `ER-00017`.

## Hashing limitation

SHA-256 provides integrity/change detection for the stored file. It does
not by itself prove factual authenticity of the photograph or its
contents.

------------------------------------------------------------------------

# 8. Locked Data Model

Nine conceptual/domain entities:

1.  User
2.  InspectionCase
3.  EvidenceAsset
4.  DerivedOcrToken
5.  ExtractedDeclaration
6.  ApplicabilityContext
7.  ComplianceFinding
8.  FinalAuditRecord
9.  AuditEvent

## Root aggregate

`InspectionCase` is the root aggregate.

## Important principles

-   OCR tokens remain persistent and traceable.
-   Declarations preserve history/versioning.
-   Applicability is persisted with rule/version context.
-   System compliance findings remain separate from reviewer
    determinations.
-   AuditEvent is append-only chronological history.
-   FinalAuditRecord is the immutable point-in-time finalized snapshot.
-   There is no competing mutable final-result source of truth.

------------------------------------------------------------------------

# 9. Locked Architecture

The system is a modular FastAPI backend rather than a microservice
architecture.

## Eight logical components

``` text
1. Frontend Web Client

2. API Gateway & Authentication

3. Inspection Orchestrator & State Machine

4. Evidence Store

5. Perception Engine
   ├── Image Quality
   └── PaddleOCR

6. Structured Extractor
   └── Gemini 2.5 Flash

7. Applicability & Deterministic Rule Engine
   ├── Applicability
   └── Six deterministic compliance evaluators

8. Report & Audit Store
   ├── Audit
   ├── Finalization
   └── PDF Reporting
```

Target architecture documents may contain larger reference component
counts, but the implementation architecture is the eight logical
components above.

------------------------------------------------------------------------

# 10. Locked Technology Stack

``` text
Frontend:
React + TypeScript + Vite + Tailwind CSS

Backend:
Python 3.11+ + FastAPI

Database:
PostgreSQL

Platform:
Supabase

Database Platform:
Supabase PostgreSQL

Storage:
Supabase Storage

Authentication:
Supabase Auth

OCR:
PaddleOCR

LLM:
Gemini 2.5 Flash

ORM:
SQLAlchemy

Migrations:
Alembic

Containers:
Docker

Processing:
Asynchronous Worker
```

## Critical boundary

``` text
React → FastAPI → Supabase
```

The frontend does not directly manipulate inspection/domain data.

FastAPI remains authoritative for:

-   RBAC
-   lifecycle
-   evidence operations
-   applicability
-   compliance rules
-   verification
-   review
-   finalization

Supabase is infrastructure, not the business authority.

------------------------------------------------------------------------

# 11. M-01 --- PostgreSQL-Backed Durable Analysis Queue

## STATUS: FINAL / APPROVED

### Decision

Use a PostgreSQL-backed durable analysis job queue using Supabase
PostgreSQL.

``` text
FastAPI
   ↓
Supabase PostgreSQL
   ↓
analysis_jobs
   ↓
Cloud Worker
   ├── PaddleOCR
   └── Gemini
```

### Locked requirements

-   durable job IDs;
-   explicit job status;
-   atomic worker claim;
-   multiple workers cannot claim the same job simultaneously;
-   bounded retries;
-   stale/abandoned job recovery using timeout/lease;
-   idempotent processing where required;
-   queue/backpressure;
-   FastAPI does not perform heavy OCR/LLM synchronously;
-   FastAPI BackgroundTasks are not the durable processing mechanism;
-   worker is separately deployable;
-   PostgreSQL stores durable job state;
-   Redis/ARQ is not required for MVP;
-   a dedicated queue may be introduced later if measured scale requires
    it.

### Production interpretation

The local development PC is not required to remain on for production
processing.

FastAPI, Supabase PostgreSQL, worker, PaddleOCR and Gemini can run in
deployed/cloud infrastructure.

------------------------------------------------------------------------

# 12. M-02 --- Inspector vs Reviewer Correction Boundary

## STATUS: FINAL / APPROVED

### Core separation

``` text
Inspection
  ├── Underlying Data → Inspector
  └── Assessment → Reviewer
```

### Inspector correction

Inspector answers:

> "What does the package actually show?"

Example domain command:

``` text
CorrectDeclaration
├── inspection_id
├── declaration_id
├── old_value
├── new_value
├── reason
├── source_evidence_id
└── actor
```

### Correction flow

``` text
Inspector Correction
 → validate permission
 → record old/new
 → record reason/actor/time/evidence
 → invalidate affected downstream state
 → recompute
 → audit transition
```

### Conservative invalidation

``` text
Evidence
 ↓
OCR
 ↓
Declarations
 ↓
Applicability
 ↓
Compliance Findings
 ↓
Verification
 ↓
Review
 ↓
Finalization
```

For MVP, if a declaration correction could affect downstream evaluation,
conservatively invalidate applicability/evaluation and require
re-verification where appropriate rather than implementing a
sophisticated field-level dependency graph.

### Reviewer determination

``` text
ReviewerDetermination
├── finding_id
├── decision
├── reason
├── evidence_reference
├── actor
└── timestamp
```

Reviewer actions include:

-   CONFIRM
-   OVERRIDE
-   REQUEST_REVISION
-   REQUEST_EVIDENCE

### Locked principles

-   Reviewer does not silently edit underlying declarations.
-   Reviewer may request revision when underlying data needs correction.
-   Reviewer may request supplemental evidence.
-   Evidence requests have Evidence Request IDs.
-   Reviewer overrides require reasons.
-   System findings remain preserved alongside reviewer determinations.
-   If an Inspector changes a declaration after verification and the
    change affects the verified result, verification becomes stale.
-   Inspector re-verifies before submission.
-   Finalized inspections cannot use normal correction/determination
    operations.
-   Audit events capture corrections, determinations, revisions,
    evidence requests and finalization.
-   Human-entered corrections must never appear as though they were part
    of the original AI extraction.

------------------------------------------------------------------------

# 13. P-01 --- Shared Domain Package Between Backend and Worker

## STATUS: FINAL / APPROVED

### Problem

FastAPI and the separately deployed Worker could independently define
states, schemas and domain terminology, causing drift.

Example:

``` text
Backend:
"EVALUATED"

Worker:
"evaluation_complete"
```

### Decision

Create a shared internal domain package consumed by both Backend and
Worker.

Conceptually:

``` text
ComplianceScan/
│
├── backend/
│
├── worker/
│
└── shared/
    └── domain/
        ├── states
        ├── enums
        ├── schemas
        ├── domain types
        └── constants
```

### Shared package contains

-   inspection lifecycle states;
-   processing/job states;
-   compliance result vocabulary;
-   shared schemas/contracts;
-   domain identifiers/types;
-   controlled constants;
-   common validation contracts.

### Shared package does NOT contain

Backend-specific:

-   FastAPI routes;
-   authentication implementation;
-   RBAC enforcement;
-   SQLAlchemy repositories;
-   HTTP handlers;
-   middleware.

Worker-specific:

-   PaddleOCR execution;
-   Gemini API calls;
-   image processing implementation;
-   queue polling/claiming;
-   retry runtime.

Infrastructure-specific:

-   Supabase client configuration;
-   Docker runtime configuration;
-   deployment configuration.

### Critical principle

> Shared package contains contracts, not duplicated business authority.

The worker must not become a second legal-rule authority.

Backend remains authoritative for applicability and compliance
evaluation.

### Locked requirements

1.  Backend and Worker use a shared internal domain package.
2.  Shared package is canonical for shared domain
    enums/states/contracts/types.
3.  Shared schemas are version-controlled with the application.
4.  Backend and Worker may deploy independently while consuming the same
    domain contract.
5.  Contract changes require coordinated backend/worker compatibility
    review.
6.  No duplicated handwritten definitions of shared domain
    states/contracts.
7.  Shared package must not become a dumping ground for unrelated
    implementation code.

------------------------------------------------------------------------

# 14. P-02 --- Worker Queue / Communication Mechanism

## STATUS: FINAL / APPROVED

### Decision

Use the PostgreSQL-backed analysis queue from M-01 and define safe
worker claiming/execution behavior.

### Conceptual flow

``` text
Inspector
   ↓
FastAPI
   ↓
Create Analysis Job
   ↓
Supabase PostgreSQL
   ↓
Worker claims job
   ↓
PaddleOCR + Gemini
   ↓
Save results
   ↓
PostgreSQL
   ↓
FastAPI
   ↓
Inspector
```

### Locked job lifecycle

``` text
QUEUED
   ↓
PROCESSING
   ↓
COMPLETED
```

Failure path:

``` text
QUEUED
   ↓
PROCESSING
   ↓
FAILED
```

Retry path:

``` text
FAILED
   ↓
RETRY
   ↓
QUEUED
   ↓
PROCESSING
```

Retries must be bounded.

### Locked requirements

1.  Worker looks for eligible queued jobs.
2.  Worker atomically claims a job.
3.  Claimed job becomes PROCESSING.
4.  Multiple workers cannot simultaneously own the same job.
5.  Successful processing stores output and marks job COMPLETED.
6.  Failure is explicitly recorded.
7.  Eligible failures may be retried within a bounded limit.
8.  Lease/timeout permits recovery of abandoned jobs.
9.  Duplicate execution is handled safely where required.
10. Job state is durable in PostgreSQL.
11. FastAPI does not perform heavy OCR/LLM processing synchronously.

------------------------------------------------------------------------

# 15. P-03 --- Explicit Correction Command Model

## STATUS: FINAL / APPROVED

### Core principle

> **Don't overwrite an inspection. Record the correction to the
> inspection.**

Inspection-relevant corrections are explicit domain commands rather than
unrestricted generic mutations.

### Example

``` text
Original observation:
MRP = ₹20

Correction:
MRP = ₹120

Reason:
OCR misread the printed value.

Evidence:
IMG-00042

Corrected by:
Inspector

Timestamp:
Recorded by system
```

### Correction flow

``` text
CorrectDeclaration
        ↓
Check permission
        ↓
Record old + new value
        ↓
Record reason
        ↓
Record evidence
        ↓
Record actor + timestamp
        ↓
Invalidate affected evaluation
        ↓
Recompute
        ↓
Re-verify if required
        ↓
Audit
```

### Important distinction

Temporary editing while an inspection is still an unaccepted draft may
remain normal UI interaction.

Once an inspection-relevant observation is accepted, its correction must
use the explicit correction model.

### Locked requirements

-   No unrestricted generic mutation/PATCH for inspection observations.
-   Old and new values are preserved.
-   Reason is mandatory for inspection-relevant correction.
-   Actor and timestamp are recorded.
-   Evidence can support the correction.
-   Original OCR output is preserved.
-   Corrections do not modify historical OCR output.
-   Affected downstream state is invalidated.
-   Applicability/compliance is recomputed where affected.
-   Verification becomes stale where appropriate.
-   Inspector re-verifies affected information before submission.
-   Correction generates an audit event.
-   Finalized inspections cannot be normally corrected.
-   Reviewer does not silently modify underlying extracted declarations.

------------------------------------------------------------------------

# 16. P-04 --- FinalAuditRecord as Immutable Point-in-Time Snapshot

## STATUS: FINAL / APPROVED

### Problem

A working inspection changes over time. A finalized inspection must
represent exactly what was finalized at a particular point in time.

### Decision

`FinalAuditRecord` is an immutable point-in-time snapshot created during
finalization.

Conceptual flow:

``` text
Inspection
   ↓
Reviewer finalizes
   ↓
FinalAuditRecord
   ↓
READ-ONLY
```

### Snapshot contains / references

-   finalized evidence references;
-   final declarations;
-   applicability;
-   compliance findings;
-   reviewer determinations;
-   final outcome;
-   finalizing reviewer;
-   finalization timestamp;
-   information necessary to reproduce the finalized inspection result.

### Relationship with AuditEvent

``` text
AuditEvent
   ↓
"What happened over time?"

FinalAuditRecord
   ↓
"What was final at finalization?"
```

Simple mental model:

> AuditEvent = the movie\
> FinalAuditRecord = the final photograph

### Locked requirements

1.  FinalAuditRecord represents the final point-in-time state.
2.  It is created during finalization.
3.  It is immutable after creation.
4.  It references evidence used by the final inspection.
5.  It preserves final applicability, findings and reviewer
    determinations.
6.  It records reviewer and timestamp.
7.  Reports are generated from the finalized snapshot.
8.  AuditEvent remains the chronological history.
9.  FinalAuditRecord does not replace AuditEvent.
10. No mutable working record can silently alter the finalized snapshot.
11. Future exceptional re-evaluation must preserve the original
    finalized record.
12. There must be no competing mutable "final result" source of truth.

------------------------------------------------------------------------

# 17. P-05 --- Field-Level Gemini Output Validation

## STATUS: FINAL / APPROVED

### Problem

Gemini output is probabilistic. It must not be passed blindly into the
compliance engine.

Example expected output:

``` text
MRP
  value = 120
  currency = INR

Net Quantity
  value = 500
  unit = g

Packing Date
  month = 08
  year = 2026
```

Potential malformed output:

``` text
MRP = "probably 120 rupees"
Quantity = "about half kilogram"
Date = "August-ish 2026"
```

### Decision

Validate Gemini output at the field level before it enters compliance
evaluation.

### Validation includes

1.  expected structure;
2.  required fields where applicable;
3.  data types;
4.  controlled formats/representations;
5.  source/traceability information where required;
6.  missing/malformed/unsupported values;
7.  uncertainty/conflict handling.

### No guessing

If evidence says:

``` text
MRP ₹1?0
```

Gemini must not silently turn that into:

``` text
MRP ₹120
```

Uncertain/conflicting information remains uncertain/conflicting and can
require review.

### Critical distinction

``` text
QUESTION 1
Is the AI response structurally valid?
        ↓
Field-level validation

QUESTION 2
Does the value satisfy the applicable rule?
        ↓
Deterministic rule engine

QUESTION 3
Does the package actually show this?
        ↓
Inspector verification
```

### Locked requirements

-   Gemini output conforms to predefined structured schemas.
-   Field-level validation occurs before compliance evaluation.
-   Expected types/formats are validated.
-   Source traceability is retained where required.
-   AI must not invent values to satisfy schema requirements.
-   Validation failure is a data/analysis quality issue, not
    automatically a compliance violation.
-   Validated AI output remains an observation.
-   Deterministic backend rules remain responsible for compliance
    evaluation.
-   Inspector verification remains mandatory.
-   Original OCR output remains preserved.
-   Validation rules are deterministic and version-controlled.
-   MVP validation remains lightweight and does not become a second AI
    reasoning system.

------------------------------------------------------------------------

# 18. Combined AI / Compliance Boundary

The complete pipeline is:

``` text
ORIGINAL IMAGE
      ↓
IMAGE QUALITY
      ↓
PADDLEOCR
      ↓
OCR OBSERVATIONS
      ↓
GEMINI
      ↓
STRUCTURED EXTRACTION
      ↓
FIELD-LEVEL VALIDATION
      ↓
VALIDATED OBSERVATIONS
      ↓
APPLICABILITY
      ↓
DETERMINISTIC RULE ENGINE
      ↓
FINDINGS
      ↓
INSPECTOR VERIFICATION
      ↓
REVIEWER DECISION
      ↓
FINALIZATION
```

This boundary is intentional.

The AI is not the legal authority.

------------------------------------------------------------------------

# 19. Global Invariant

The following invariant applies across the architecture:

> **Upstream correction → invalidate affected downstream state →
> recompute → preserve prior state/history → audit transition.**

Example:

``` text
Evidence
  ↓
OCR
  ↓
Declaration
  ↓
Applicability
  ↓
Compliance
  ↓
Verification
  ↓
Review
  ↓
Finalization
```

If an upstream accepted observation changes, affected downstream state
must not remain falsely valid.

------------------------------------------------------------------------

# 20. API Boundary

Base path:

``` text
/api/v1
```

Logical groups:

``` text
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

### Locked API principles

-   Backend authoritative for authentication, authorization, lifecycle,
    applicability, rules and finalization.
-   Analysis is asynchronous and may return 202.
-   Evidence acceptance is explicit.
-   Only draft evidence is removable.
-   Corrections are audited commands rather than silent mutations.
-   Rule evaluation is exposed through inspection operations rather than
    arbitrary public rule CRUD.
-   Reviewer decisions are explicit and audited.
-   Finalization is a separate atomic operation.
-   Finalized records are read-only.
-   Reports derive from finalized snapshots.
-   Audit is read-only.
-   API errors are standardized.
-   No lifecycle or RBAC bypass is permitted.

------------------------------------------------------------------------

# 21. Locked UI Views

``` text
/dashboard
/inspections
/inspections/new
/inspections/:id
/inspections/:id/verify
/inspections/:id/result
/inspections/:id/history
/review/:id
```

## Inspector flow

``` text
Dashboard
   ↓
Inspections
   ↓
Create
   ↓
Evidence / Analysis
   ↓
Verification
   ↓
Submit
```

## Reviewer flow

``` text
Review Queue
   ↓
Reviewer Workspace
   ↓
Decision
   ↓
Finalize
```

After finalization:

``` text
Result
   ├── PDF
   └── History
```

------------------------------------------------------------------------

# 22. Security / Integrity Principles

-   Backend is authoritative for RBAC.
-   Original accepted evidence is immutable.
-   Accepted evidence is stored outside a directly exposed web root
    where applicable.
-   Evidence upload is authenticated and authorized.
-   MIME, size and decoding validation are performed.
-   Evidence receives a server-generated ID.
-   SHA-256 is recorded.
-   Audit events are append-only.
-   Finalized records are immutable.
-   Reviewer overrides require a reason.
-   Inspector and Reviewer separation is enforced.
-   Controlled legal rules cannot be changed through normal operational
    roles.
-   Technical administration is separate from operational inspection
    workflow.

------------------------------------------------------------------------

# 23. Legal Research Basis

The project research uses official sources as the primary basis:

-   Legal Metrology Act, 2009
-   Legal Metrology (Packaged Commodities) Rules, 2011
-   Relevant amendment notifications
-   Department of Consumer Affairs Legal Metrology material
-   Supporting official guidance / FAQs

Research principle:

> Primary legislation and official notifications are the authoritative
> basis; explanatory material is supporting evidence.

The project does not treat AI output or general web content as legal
authority.

------------------------------------------------------------------------

# 24. Known Architectural Constraints

The following are deliberate MVP boundaries:

-   Modular monolith rather than microservices.
-   PostgreSQL-backed queue rather than Redis/ARQ.
-   Controlled legal rule snapshot rather than automatic regulatory
    ingestion.
-   Two operational roles: Inspector and Reviewer.
-   Six core compliance domains.
-   Adaptive evidence capture rather than fixed image count.
-   Human verification before submission.
-   Independent Reviewer finalization.
-   No autonomous legal enforcement decision.
-   No universal category-specific legal coverage.
-   No unsupported quantitative claims about cost savings, accuracy or
    environmental impact.

------------------------------------------------------------------------

# 25. Antigravity Review Request

Please review the **seven resolved items**:

``` text
M-01  PostgreSQL-backed durable analysis queue
M-02  Inspector vs Reviewer correction boundary
P-01  Shared Domain Package
P-02  Worker Queue / Communication Mechanism
P-03  Explicit Correction Command Model
P-04  Immutable FinalAuditRecord snapshot
P-05  Field-Level Gemini Output Validation
```

All are currently **FINAL / APPROVED** by the human project owner.

## Review questions

### A. Consistency

Do any of these decisions contradict each other?

Pay particular attention to:

-   M-01 + P-02
-   M-02 + P-03
-   P-01 + P-05
-   P-03 + P-04
-   finalization + evidence immutability
-   lifecycle states + processing states + compliance results

### B. Completeness

Is there any genuinely necessary architectural decision missing that
would prevent safe implementation?

Do not invent decisions merely because they could theoretically be
useful.

### C. Implementation risks

Are there implementation-level risks that could invalidate any of these
decisions?

Identify concrete risks, not generic warnings.

### D. Security / integrity

Does the combined model contain a path that could allow:

-   unauthorized correction;
-   evidence replacement;
-   duplicate job execution causing inconsistent results;
-   reviewer/inspector separation bypass;
-   finalized record mutation;
-   audit history manipulation;
-   AI output to bypass validation;
-   compliance logic to be bypassed by malformed data?

### E. MVP scope

Does anything in the seven decisions introduce unnecessary MVP
complexity?

If yes, identify the specific item and why.

### F. Worker/backend contract

Does P-01 define an adequate boundary between the shared domain contract
and actual business authority?

### G. Finalization

Does P-04 provide a sufficient point-in-time representation for
reporting and historical review without creating a competing source of
truth?

------------------------------------------------------------------------

# 26. Required Review Output

Please do NOT rewrite the architecture.

Return a structured review:

## 1. Overall Assessment

One concise assessment of whether the seven decisions form a coherent
implementation foundation.

## 2. Contradictions

List only real contradictions.

For each:

-   Decision(s)
-   Problem
-   Severity
-   Proposed resolution

## 3. Missing Decisions

List only decisions that are genuinely required before implementation.

For each:

-   Missing decision
-   Why it matters
-   Whether it blocks implementation
-   Minimal recommended resolution

## 4. Implementation Risks

List concrete risks and mitigations.

## 5. MVP Complexity Check

Identify any approved item that appears unnecessarily complex for MVP.

## 6. Security / Integrity Check

Check the correction, evidence, queue, audit, AI-validation and
finalization paths.

## 7. Final Verdict

State whether:

``` text
READY FOR IMPLEMENTATION
```

or

``` text
REQUIRES SPECIFIC CHANGES BEFORE IMPLEMENTATION
```

If changes are proposed, do not silently treat them as approved. The
human project owner will decide whether to accept them.

------------------------------------------------------------------------

# 27. Important Instruction to Antigravity

Do NOT:

-   write code;
-   create database migrations;
-   create API files;
-   create UI files;
-   create deployment files;
-   modify the architecture;
-   silently add features;
-   introduce microservices;
-   introduce Redis merely because it is common;
-   add a Rule Manager role;
-   add USP checks;
-   add dynamic legal scraping;
-   turn Gemini into a legal decision-maker;
-   replace PostgreSQL queue without evidence;
-   create another "final result" authority;
-   treat AI confidence as a legal threshold.

This review is strictly for **architecture validation and identification
of genuine gaps**.

------------------------------------------------------------------------

# 28. Current Approval Table

``` text
┌────────────────────────────────────────────────────────────┐
│          ANTIGRAVITY REVIEW — RESOLVED ITEMS               │
├────────────────────────────────────────────────────────────┤
│ M-01  PostgreSQL-backed durable analysis queue       ✓ FINAL│
│ M-02  Inspector vs Reviewer correction boundary      ✓ FINAL│
│ P-01  Shared Domain Package                          ✓ FINAL│
│ P-02  Worker Queue / Communication Mechanism         ✓ FINAL│
│ P-03  Explicit Correction Command Model              ✓ FINAL│
│ P-04  Immutable FinalAuditRecord snapshot            ✓ FINAL│
│ P-05  Field-Level Gemini Output Validation           ✓ FINAL│
└────────────────────────────────────────────────────────────┘
```

------------------------------------------------------------------------

# 29. Current Architecture Philosophy

The architecture should remain understandable as:

``` text
CAPTURE
   ↓
UNDERSTAND
   ↓
DETERMINE APPLICABILITY
   ↓
EVALUATE
   ↓
VERIFY
   ↓
REVIEW
   ↓
FINALIZE
   ↓
PRESERVE
```

With responsibility separated:

``` text
PaddleOCR
   → Reads

Gemini
   → Structures

Validation
   → Checks structure

Rule Engine
   → Evaluates requirements

Inspector
   → Verifies observations

Reviewer
   → Decides and finalizes

FinalAuditRecord
   → Preserves the finalized state

AuditEvent
   → Preserves what happened over time
```

The objective is a system that is **buildable, explainable, auditable
and defensible**, without claiming that AI independently determines
legal compliance.
