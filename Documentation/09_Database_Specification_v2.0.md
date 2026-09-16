# 09 — DATABASE SPECIFICATION

**Project:** ComplianceScan  
**SIH'26 Problem Statement:** 26034  
**Document Version:** 2.0  
**Status:** Target persistence specification with controlled one-day MVP subset

---

# 1. Purpose

This document defines the persistence model for ComplianceScan.

It specifies:

- persistence responsibilities
- core entities
- relationships
- lifecycle persistence
- evidence metadata
- OCR observations
- AI extraction
- applicability
- compliance assessments
- findings
- Inspector corrections
- Reviewer decisions
- evidence requests
- finalization snapshots
- audit history
- rule/model provenance
- deployment storage requirements
- current one-day MVP persistence subset

The database must preserve the distinction between:

```text
Observed Data
System Analysis
Human Verification
Reviewer Decision
Historical Final State
```

The database is not merely a place to store the latest UI values.

It must preserve enough information to explain how an inspection reached its result.

---

# 2. Scope Model

This specification describes the broader target persistence architecture.

The current one-day MVP uses only the subset required for the vertical slice.

```text
TARGET DATA MODEL
       │
       │ controlled subset
       ▼
CURRENT MVP DATA MODEL
```

Current implementation boundary:

> `MVP_BUILD_SCOPE.md`

Actual implementation status:

> `PROJECT_STATE.md`

Execution sequence:

> `PHASE.md`

Engineering-agent behavior:

> `AGENT_ENGINEERING_PROTOCOL.md`

This document is authoritative for persistence/data-model semantics.

---

# 3. Persistence Principle

The core persistence principle is:

> **Store facts, observations, decisions, provenance, and history separately enough that they can be understood and audited.**

The system must not collapse:

```text
OCR Value
     =
AI Value
     =
Inspector Value
     =
Reviewer Decision
```

These are different layers.

---

# 4. Deployment Requirement

The deployed MVP must use persistent storage.

Required production architecture:

```text
Application
    │
    ├───────────────► Persistent Cloud-Capable Relational Database
    │
    └───────────────► Persistent Object/File Storage
```

Important decisions:

- Local-only SQLite is not the production architecture.
- Local filesystem is not the production evidence-storage architecture.
- SQLite may be used for local development/testing if useful.
- The production relational database provider is not yet locked.
- The production object/file storage provider is not yet locked.
- The application must not depend on process-local memory for persistent inspection state.
- Evidence binaries should be stored in persistent object/file storage rather than unnecessarily inside relational rows.

The exact provider/technology may be selected during implementation/team discussion.

---

# 5. Logical Data Architecture

```text
                    ┌──────────────────┐
                    │      USERS       │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   INSPECTIONS    │
                    └────────┬─────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
      PRODUCT           EVIDENCE          CONTEXT
          │                  │
          │                  ├────► OCR
          │                  │
          │                  └────► Derived Artifacts
          │
          ▼
    DECLARATIONS
          │
          ▼
    APPLICABILITY
          │
          ▼
    ASSESSMENTS
          │
          ▼
      FINDINGS
          │
          ▼
    VERIFICATION
          │
          ▼
       REVIEWS
          │
          ├────► EVIDENCE REQUESTS
          │
          ▼
     FINAL SNAPSHOT
          │
          ▼
        REPORT
```

Cross-cutting:

```text
AUDIT
PROVENANCE
RULE VERSION
AI/OCR PROCESSING CONTEXT
INTEGRITY HASHES
```

---

# 6. Core Entity Set

The target data model contains these logical entities:

1. User
2. Role / Permission
3. Inspection
4. Product Context
5. Evidence
6. Evidence Metadata
7. OCR Run
8. OCR Region
9. AI Processing Run
10. Declaration
11. Declaration Source
12. Applicability Decision
13. Compliance Assessment
14. Finding
15. Finding Evidence
16. Inspector Verification
17. Correction
18. Evidence Request
19. Reviewer Decision
20. Final Snapshot
21. Audit Event
22. Rule Snapshot
23. Processing/Provenance Record
24. Report
25. Physical/Online Comparison (target)
26. Dashboard/aggregation data (target, derived)

The one-day MVP may consolidate some of these into fewer physical tables if doing so preserves the semantics and auditability.

---

# 7. Entity 1 — User

Represents an authenticated system user.

Conceptual fields:

```text
user_id
name
email / login identifier
role
status
created_at
updated_at
```

Target operational roles:

```text
INSPECTOR
REVIEWER
```

A technical administrator may exist separately for deployment/security administration but is not an operational inspection role.

---

# 8. User Security

Passwords/credentials should not be stored in plaintext.

Authentication implementation is not permanently locked.

The database must store only the information required by the chosen authentication mechanism.

Sensitive secrets such as:

- Gemini API keys
- storage credentials
- database credentials
- signing secrets

must not be stored as ordinary user data.

---

# 9. Entity 2 — Inspection

The Inspection is the primary aggregate/root record.

Conceptual fields:

```text
inspection_id
status
created_by
reviewer_id
created_at
updated_at
submitted_at
finalized_at
current_result
rule_snapshot_id
created_version
```

The inspection owns or references the majority of the workflow data.

---

# 10. Inspection Ownership

The inspection should identify:

```text
created_by → Inspector
reviewer_id → Reviewer when assigned/available
```

Ownership must be enforced by the backend.

The database must support lifecycle checks such as:

```text
DRAFT
EVIDENCE_PROVIDED
PROCESSING
INSPECTOR_VERIFICATION
SUBMITTED
UNDER_REVIEW
FINALIZED
```

---

# 11. Inspection Status

The persisted lifecycle must align with `07_State_Machine.md`.

Conceptual states include:

```text
DRAFT
CONTEXT_READY
EVIDENCE_PROVIDED
IMAGE_PROCESSING
OCR_PROCESSING
DECLARATION_EXTRACTION
APPLICABILITY_EVALUATION
COMPLIANCE_EVALUATION
FINDING_GENERATION
EVIDENCE_REVIEW
INSPECTOR_VERIFICATION
INCOMPLETE
REQUIRES_REVIEW
SUBMITTED
UNDER_REVIEW
EVIDENCE_REQUESTED
REVIEW_DECISION
FINALIZED
PROCESSING_FAILED
```

The physical implementation may consolidate technical processing states.

It must not lose the semantic distinction between processing, verification, review, and finalization.

---

# 12. Entity 3 — Product Context

Stores product/inspection information relevant to applicability and analysis.

Conceptual fields:

```text
product_context_id
inspection_id
product_name
generic_name
imported_status
manufacturer
packer
importer
category
source_context
created_at
updated_at
```

The exact field separation may differ because some declarations are system-observed rather than user-provided.

The database must preserve the distinction between:

```text
Initial context
AI-extracted declaration
Inspector-corrected declaration
Reviewer decision
```

---

# 13. Imported Status

Country of Origin applicability depends on supported imported status.

Represent:

```text
YES
NO
UNKNOWN
```

Do not collapse `UNKNOWN` into `NO`.

Conceptually:

```text
YES
 ↓
COO APPLICABLE

NO
 ↓
NOT_APPLICABLE

UNKNOWN
 ↓
REVIEW / BLOCK AS APPROPRIATE
```

---

# 14. Entity 4 — Evidence

Evidence is a first-class persisted entity.

Conceptual fields:

```text
evidence_id
inspection_id
evidence_type
storage_reference
original_filename
mime_type
size
sha256
captured_at
uploaded_at
created_by
source
provenance
immutable
evidence_request_id
```

Evidence types:

```text
PRIMARY
SUPPLEMENTAL
DERIVED
```

Audit/decision records are not evidence.

---

# 15. Evidence Storage

The relational database should store evidence metadata and relationships.

The original binary should normally be stored in persistent object/file storage.

Conceptually:

```text
Database
  ├── Evidence ID
  ├── Storage reference
  ├── SHA-256
  ├── Metadata
  └── Provenance

Object Storage
  └── Original Image
```

The application must not depend on a local process filesystem for production evidence persistence.

---

# 16. Evidence Immutability

Original evidence is immutable.

The database must prevent ordinary update/delete operations that would silently replace or remove protected evidence.

If a new image is supplied:

```text
New Image
   ↓
New Evidence ID
```

The old evidence remains preserved.

---

# 17. Evidence Integrity

The server should calculate the authoritative SHA-256 hash.

Conceptually:

```text
Uploaded Bytes
      ↓
Server
      ↓
SHA-256
      ↓
Evidence.sha256
```

The hash provides:

> **Tamper-evident integrity/change detection.**

It does not prove:

- truthfulness
- source authenticity
- absence of manipulation before upload

The database documentation and UI must not overclaim what hashing establishes.

---

# 18. Evidence Provenance

Evidence should preserve enough provenance to determine:

- who added it
- when it was added
- which inspection it belongs to
- whether it is primary or supplemental
- whether it responds to an Evidence Request
- what processing was derived from it

Example:

```text
Evidence
  ├── Inspection
  ├── Actor
  ├── Timestamp
  ├── Type
  ├── Request ID
  └── Processing References
```

---

# 19. Entity 5 — OCR Run

Represents one OCR processing operation.

Conceptual fields:

```text
ocr_run_id
inspection_id
evidence_id
engine
engine_version
status
started_at
completed_at
error_code
```

Current selected OCR:

> PaddleOCR

OCR output must remain associated with its source evidence.

---

# 20. Entity 6 — OCR Region

Stores text detected in an image region.

Conceptual fields:

```text
ocr_region_id
ocr_run_id
evidence_id
text
x
y
width
height
confidence
sequence
```

The bounding box should use a documented coordinate convention.

The OCR region is derived evidence, not original evidence.

---

# 21. OCR Confidence

OCR confidence is stored separately from AI extraction confidence.

```text
OCR confidence
      ≠
AI extraction confidence
```

Do not use one database field to represent both.

---

# 22. Entity 7 — AI Processing Run

Represents a model invocation/processing attempt.

Conceptual fields:

```text
ai_run_id
inspection_id
model_provider
model_name
model_version
schema_version
status
started_at
completed_at
error_code
request_reference
```

Current selected model:

> Gemini 2.5 Flash

The exact provider implementation may be abstracted internally, but the processing provenance should remain available.

---

# 23. AI Processing Output

AI output should be persisted as structured observations.

It should preserve:

- extracted values
- observation statuses
- confidence
- source regions
- evidence references
- AI run reference

Do not store only the final flattened value.

---

# 24. Entity 8 — Declaration

Represents a structured declaration observation.

Current supported declarations include:

```text
MANUFACTURER_PACKER_IMPORTER
GENERIC_PRODUCT_NAME
NET_QUANTITY
MANUFACTURE_PACKING_IMPORT_DATE
MRP
CONSUMER_CARE
COUNTRY_OF_ORIGIN
```

Country of Origin is applicability-driven.

Conceptual fields:

```text
declaration_id
inspection_id
field_name
value
normalized_value
observation_status
ai_confidence
ai_run_id
current_version
created_at
updated_at
```

---

# 25. Declaration Observation Status

Allowed statuses:

```text
OBSERVED
NOT_OBSERVED
UNCERTAIN
UNREADABLE
CONFLICTING
```

These states must remain distinguishable in persistence.

---

# 26. Declaration Versioning

A declaration correction must not destroy the original observation.

Preferred logical model:

```text
Original AI Observation
        ↓
Inspector Correction
        ↓
Current Verified Value
```

Historical values should remain auditable.

The physical implementation may use:

- version rows
- correction records
- append-only history
- snapshot references

The chosen mechanism must preserve old/new values and actor/time.

---

# 27. Entity 9 — Declaration Source

Maps a declaration to the evidence/region that supports it.

Conceptual fields:

```text
declaration_source_id
declaration_id
evidence_id
ocr_region_id
source_type
confidence
created_at
```

This enables:

```text
Declaration
   ↓
OCR Region
   ↓
Evidence
```

---

# 28. No Unsupported AI Fact

Database constraints and application validation must prevent an AI declaration from being accepted as a supported observation without appropriate provenance.

Conceptually:

```text
Accepted Declaration
      ↓
Must have source/provenance
```

If no source exists, the system should preserve the output as unaccepted/unresolved processing information rather than silently treating it as fact.

---

# 29. Entity 10 — Applicability Decision

Stores whether a requirement applies.

Conceptual fields:

```text
applicability_id
inspection_id
requirement_code
applicable
status
reason
source
created_at
updated_at
```

Possible statuses may include:

```text
APPLICABLE
NOT_APPLICABLE
UNKNOWN
REQUIRES_REVIEW
```

The exact status representation may be simplified.

---

# 30. Applicability First

The persistence model must support:

```text
Applicability
      ↓
Compliance Assessment
```

A requirement that is not applicable should not be persisted as an ordinary failure.

Example:

```text
Country of Origin
    ↓
Imported = NO
    ↓
NOT_APPLICABLE
```

---

# 31. Entity 11 — Compliance Assessment

Represents deterministic evaluation of one supported requirement.

Conceptual fields:

```text
assessment_id
inspection_id
requirement_code
result
reason
rule_snapshot_id
source_declaration_refs
evidence_refs
created_at
updated_at
```

Current result vocabulary:

```text
PASS
POTENTIAL_NON_COMPLIANCE
REQUIRES_REVIEW
NOT_APPLICABLE
INCOMPLETE
PROCESSING_FAILED
```

---

# 32. Assessment Source Separation

The assessment should preserve what it was based on.

Conceptually:

```text
Assessment
 ├── Declaration references
 ├── Applicability reference
 ├── Rule snapshot
 ├── Evidence references
 └── Processing provenance
```

This makes the assessment explainable.

---

# 33. Assessment History

When an assessment changes:

```text
Old Assessment
      ↓
New Assessment
```

The old assessment should remain recoverable through history/audit/snapshot semantics.

The database must not silently overwrite a historical final decision.

---

# 34. Entity 12 — Finding

A Finding is an evidence-backed explanation of a potential issue or relevant observation.

Conceptual fields:

```text
finding_id
inspection_id
assessment_id
requirement_code
result
reason
rule_reference
confidence
status
created_at
```

---

# 35. Entity 13 — Finding Evidence

Associates findings with supporting evidence.

Conceptual fields:

```text
finding_evidence_id
finding_id
evidence_id
ocr_region_id
relationship_type
created_at
```

This enables:

```text
Finding
   ↓
Evidence
   ↓
Image Region
```

---

# 36. Evidence-Backed Finding Requirement

Important findings should be traceable.

The data model should make it possible to answer:

```text
What requirement?
What rule?
What was observed?
What evidence supports it?
Where in the image?
What confidence?
What decision followed?
```

A finding without supporting evidence should remain explicitly unresolved/insufficient where appropriate.

---

# 37. Entity 14 — Inspector Verification

Stores Inspector verification actions.

Conceptual fields:

```text
verification_id
inspection_id
actor_id
action
reason
created_at
```

Possible actions:

```text
CONFIRM
CORRECT
ADD_OBSERVATION
ADD_EVIDENCE
LEAVE_UNRESOLVED
```

Verification must not be represented as Reviewer finalization.

---

# 38. Entity 15 — Correction

A correction records a change to an underlying value.

Conceptual fields:

```text
correction_id
inspection_id
entity_type
entity_id
field
old_value
new_value
actor_id
reason
source_evidence_id
created_at
```

This is important for:

```text
Old Value
+
New Value
+
Actor
+
Time
+
Reason
```

---

# 39. Correction Semantics

A correction is not just:

```text
UPDATE field
```

It is:

```text
UPDATE
+
HISTORY
+
INVALIDATION
+
RECOMPUTATION
+
AUDIT
```

The database must support this semantic.

---

# 40. Entity 16 — Evidence Request

Represents a Reviewer request for additional evidence or clarification.

Conceptual fields:

```text
evidence_request_id
inspection_id
reviewer_id
requirement_code
reason
requested_information
status
created_at
responded_at
resolved_at
```

Example:

```text
ER-00017
```

---

# 41. Evidence Request Status

Conceptual statuses:

```text
OPEN
RESPONDED
RESOLVED
UNRESOLVED
CANCELLED
```

The one-day MVP may simplify this if necessary.

---

# 42. Evidence Request Relationship

Supplemental evidence should be traceable to the request that caused it when applicable.

```text
Evidence Request
       ↓
Supplemental Evidence
       ↓
Re-analysis
       ↓
Inspector Verification
       ↓
Resubmission
```

---

# 43. Entity 17 — Reviewer Decision

Stores an independent Reviewer decision.

Conceptual fields:

```text
review_id
inspection_id
reviewer_id
action
requirement_code
result
reason
created_at
```

Actions:

```text
CONFIRM
CORRECT
OVERRIDE
REQUEST_EVIDENCE
```

The original system assessment must remain available.

---

# 44. Reviewer Override Persistence

If the Reviewer overrides an assessment:

```text
System Assessment
       +
Reviewer Override
       +
Reason
       +
Reviewer
       +
Timestamp
```

Do not replace the original system assessment with only the final value.

---

# 45. Entity 18 — Final Snapshot

The final snapshot represents the historical state at finalization.

Conceptual fields:

```text
snapshot_id
inspection_id
snapshot_version
created_at
finalized_by
final_result
rule_snapshot_id
content/reference
integrity_hash where appropriate
```

The snapshot must capture or reference the complete decision context.

---

# 46. Final Snapshot Contents

The final snapshot should contain or reference:

```text
Inspection
Product / Context
Evidence
Evidence Hashes
OCR
Declarations
Applicability
Assessments
Findings
Corrections
Inspector Verification
Reviewer Decisions
Rule Snapshot
AI/OCR Provenance
Final Decision
Audit References
```

This creates a stable historical representation.

---

# 47. Final Snapshot Immutability

After finalization:

```text
Final Snapshot
      ↓
Immutable Historical Record
```

Normal application APIs must not mutate it.

Any future amendment/reprocessing workflow must be explicit and separately controlled.

---

# 48. Entity 19 — Audit Event

Stores important lifecycle and data-change history.

Conceptual fields:

```text
audit_event_id
inspection_id
actor_id
action
entity_type
entity_id
old_state
new_state
old_value
new_value
reason
created_at
metadata
```

Not every read operation needs an audit event.

Material changes should be auditable.

---

# 49. Audit Events

Examples:

```text
INSPECTION_CREATED
EVIDENCE_ADDED
PROCESSING_STARTED
PROCESSING_FAILED
OCR_COMPLETED
DECLARATION_EXTRACTED
DECLARATION_CORRECTED
APPLICABILITY_CHANGED
ASSESSMENT_UPDATED
FINDING_CREATED
INSPECTOR_VERIFIED
INSPECTION_SUBMITTED
REVIEW_STARTED
EVIDENCE_REQUESTED
EVIDENCE_RESPONDED
REVIEW_DECISION
INSPECTION_FINALIZED
```

The exact event list may evolve, but important transitions must remain traceable.

---

# 50. Audit Immutability

Audit history must not be silently rewritten.

Preferred model:

```text
Append Event
     ↓
Never mutate historical event
```

If an error is discovered, record a correcting event rather than silently changing the old event.

---

# 51. Entity 20 — Rule Snapshot

Represents the exact controlled compliance rule context used for an assessment.

Conceptual fields:

```text
rule_snapshot_id
version
name
created_at
rule_definition_reference
active
```

The current MVP uses a controlled rule snapshot for the supported six-check scope.

---

# 52. Rule Snapshot Preservation

Historical inspections must retain the rule snapshot/version used.

Example:

```text
Inspection A
    ↓
Rule Snapshot LM-MVP-1.0
    ↓
Assessment
    ↓
Finalized
```

Later:

```text
Rule Snapshot LM-MVP-2.0
```

must not silently recalculate Inspection A.

---

# 53. Entity 21 — Processing / Provenance Record

A generalized provenance record may link:

```text
Inspection
Evidence
OCR Run
AI Run
Rule Snapshot
Application Version
Timestamp
```

This supports reproducibility and diagnosis.

The physical implementation may use dedicated OCR/AI tables rather than one generalized table.

---

# 54. Entity 22 — Report

Represents generated inspection output.

Conceptual fields:

```text
report_id
inspection_id
snapshot_id
format
storage_reference
status
created_at
generated_by
```

For finalized inspections:

```text
Final Snapshot
      ↓
Report
```

Report generation must not mutate the final snapshot.

---

# 55. Report Failure

If report generation fails:

```text
FINALIZED
+
REPORT_FAILED
```

The database must preserve the finalized inspection.

Report failure must not roll back finalization.

---

# 56. Target Physical ↔ Online Comparison

The broader target system may persist:

```text
comparison_id
inspection_id
physical_field
online_field
physical_value
online_value
comparison_result
source
created_at
```

A mismatch should be represented as:

> Cross-Channel Inconsistency

It is not automatically stored as a legal violation.

This capability is deferred from the current one-day MVP.

---

# 57. Target Dashboard Data

Dashboard metrics should normally be derived from authoritative inspection records rather than manually maintained counters.

Possible metrics:

- inspection count
- result distribution
- review backlog
- processing failures
- finding distribution
- completion time

The MVP may calculate simple metrics directly from persisted records.

Do not introduce a separate analytics warehouse for the one-day MVP.

---

# 58. Relationships

Core relationships:

```text
User
  │
  └──► Inspection
          │
          ├──► Product Context
          │
          ├──► Evidence
          │      │
          │      ├──► OCR Run
          │      │      └──► OCR Region
          │      │
          │      └──► Derived Evidence
          │
          ├──► AI Processing Run
          │
          ├──► Declaration
          │      └──► Declaration Source
          │
          ├──► Applicability Decision
          │
          ├──► Compliance Assessment
          │      └──► Finding
          │             └──► Finding Evidence
          │
          ├──► Inspector Verification
          │
          ├──► Correction
          │
          ├──► Evidence Request
          │      └──► Supplemental Evidence
          │
          ├──► Reviewer Decision
          │
          ├──► Final Snapshot
          │
          ├──► Report
          │
          └──► Audit Events
```

---

# 59. Inspection as Aggregate Root

The Inspection is the primary workflow aggregate.

Most child entities should be associated with an inspection.

This provides a clear boundary:

```text
Inspection
   ├── Evidence
   ├── Processing
   ├── Declarations
   ├── Applicability
   ├── Assessments
   ├── Findings
   ├── Verification
   ├── Reviews
   ├── Final Snapshot
   └── Audit
```

---

# 60. Referential Integrity

The database should enforce relationships where practical.

Examples:

```text
Evidence.inspection_id
    → valid Inspection

OCR.evidence_id
    → valid Evidence

Declaration.inspection_id
    → valid Inspection

Assessment.inspection_id
    → valid Inspection

Finding.assessment_id
    → valid Assessment

FinalSnapshot.inspection_id
    → valid Inspection
```

Orphaned records should be avoided.

---

# 61. Delete Policy

Deletion must be conservative.

For finalized inspections:

```text
DELETE
    → forbidden through normal workflow
```

For original evidence:

```text
DELETE
    → forbidden after acceptance
```

For audit events:

```text
DELETE
    → forbidden
```

For working records, deletion behavior must be explicitly defined rather than assumed.

Soft-delete may be appropriate for certain administrative resources, but it must not be used to hide historical records.

---

# 62. Finalized Data Protection

Finalized records should be protected by:

```text
Application rules
+
Database constraints where practical
+
Authorization
+
Audit
```

Do not rely on UI hiding buttons.

---

# 63. Transaction Boundaries

The following operations should be transactionally safe:

### Inspection Creation

```text
Create inspection
+
Initial context
```

### Evidence Registration

```text
Evidence metadata
+
Inspection association
+
Integrity information
+
Audit event
```

### Declaration Correction

```text
Correction
+
Invalidation
+
Recomputed assessment
+
Audit event
```

### Reviewer Decision

```text
Decision
+
Affected assessment state
+
Audit event
```

### Finalization

```text
Validate
+
Create final snapshot
+
Record final decision
+
Record audit references
+
Mark finalized
```

---

# 64. Finalization Transaction

Finalization is the strongest transaction boundary.

Conceptually:

```text
BEGIN
  ↓
Validate Reviewer
  ↓
Validate Inspection State
  ↓
Validate Required Data
  ↓
Validate Evidence References
  ↓
Validate Rule Snapshot
  ↓
Create Final Snapshot
  ↓
Record Final Decision
  ↓
Record Audit Event
  ↓
Mark FINALIZED
  ↓
COMMIT
```

If the transaction fails:

```text
No partial finalization
```

---

# 65. Correction Transaction

A correction should behave like:

```text
BEGIN
  ↓
Validate Actor
  ↓
Read Current Value
  ↓
Record Old Value
  ↓
Write New Value
  ↓
Invalidate Affected Results
  ↓
Recompute
  ↓
Record Audit
  ↓
COMMIT
```

The exact transaction boundary may be adapted to asynchronous processing, but the resulting data must never leave an inconsistent state.

---

# 66. Asynchronous Processing Persistence

If OCR/AI processing is asynchronous:

```text
Processing Job
      ↓
Persist Job Status
      ↓
Worker
      ↓
Persist Result
      ↓
Update Inspection State
```

The system must survive process restarts.

Do not keep processing state only in memory.

---

# 67. Processing Job State

Conceptual:

```text
QUEUED
RUNNING
SUCCEEDED
FAILED
RETRYING
```

These are technical job states.

They are distinct from inspection compliance results.

---

# 68. Processing Failure Persistence

If processing fails, persist enough information to identify:

```text
Inspection
Evidence
Processing Stage
Error Code
Attempt
Timestamp
Provider/Engine
```

Do not replace the inspection's compliance result with a misleading failure label.

---

# 69. Idempotency

Critical operations should avoid duplicate records.

Examples:

```text
Repeated evidence upload
Repeated processing start
Repeated submission
Repeated Reviewer decision
Repeated finalization
```

The implementation should use appropriate idempotency keys, unique constraints, lifecycle checks, or transaction controls.

---

# 70. Uniqueness Constraints

Potential uniqueness constraints include:

```text
inspection_id
evidence_id
finding_id
evidence_request_id
snapshot_id
audit_event_id
```

Compound uniqueness may be required for:

```text
inspection + requirement + current assessment
```

The exact constraint design must align with the chosen schema.

---

# 71. Indexing

At minimum, likely indexes include:

```text
Inspection.status
Inspection.created_at
Inspection.created_by
Inspection.reviewer_id

Evidence.inspection_id
Evidence.created_at
Evidence.sha256

OCRRun.inspection_id
OCRRegion.ocr_run_id

Declaration.inspection_id
Declaration.field_name

Applicability.inspection_id
Applicability.requirement_code

Assessment.inspection_id
Assessment.requirement_code
Assessment.result

Finding.inspection_id
Finding.assessment_id

EvidenceRequest.inspection_id
EvidenceRequest.status

Review.inspection_id
Review.reviewer_id

AuditEvent.inspection_id
AuditEvent.created_at
```

Indexing should be driven by actual query patterns.

Do not create indexes for every possible field.

---

# 72. Data Types

Use types appropriate to the selected relational database.

Examples:

```text
UUID / string IDs
VARCHAR / TEXT
BOOLEAN
INTEGER / DECIMAL
TIMESTAMP
JSON / JSONB where appropriate
```

Financial/quantity values that require precision should not rely on floating-point representation when exact decimal storage is required.

The exact physical schema depends on the chosen production database.

---

# 73. Monetary Values

MRP should be stored in a representation that avoids floating-point precision errors.

Prefer:

```text
DECIMAL / NUMERIC
```

where the selected database supports it.

The original observed textual value may also be retained for provenance.

Example:

```text
Observed Text: "MRP ₹179/- incl. all taxes"
Normalized Value: 179.00
```

---

# 74. Quantity Values

Net quantity should preserve:

```text
Original Text
Numeric Value
Unit
Normalized Representation
```

Example:

```text
Original: "500 g"
Value: 500
Unit: g
```

The exact normalization rules belong to the domain/compliance specifications.

---

# 75. Date Values

Manufacture/packing/import date observations should preserve:

- original observed text
- normalized month/year where confidently determined
- observation status
- source evidence

Do not invent a specific day when only month/year is present.

---

# 76. JSON Usage

JSON can be useful for:

- AI raw structured response
- provenance metadata
- flexible evidence metadata
- rule metadata

However, important queryable fields should not be hidden exclusively inside arbitrary JSON.

For example:

```text
inspection.status
assessment.result
evidence.sha256
```

should remain first-class relational fields.

---

# 77. Raw AI Output

Where retention is required for debugging/provenance, raw AI output may be stored separately from normalized declarations.

Example:

```text
AI Run
 ├── Raw Response
 └── Structured Declarations
```

Raw output must not automatically become trusted system truth.

---

# 78. Sensitive Data

The database should minimize unnecessary sensitive information.

Do not persist:

- API keys
- authentication secrets
- unnecessary credentials
- unnecessary personal data

Use access controls and appropriate encryption mechanisms provided by the deployment environment.

---

# 79. Evidence Access Control

Database records must support authorization decisions.

For example:

```text
Inspection
    ↓
User Access
    ↓
Evidence Access
```

Knowing an Evidence ID must not be sufficient to access protected evidence.

The API layer remains authoritative for access decisions.

---

# 80. Audit Retention

Audit records should be retained with the inspection history according to the project's retention policy.

The one-day MVP should not implement arbitrary automatic deletion of audit history.

Retention duration can be defined separately if required.

---

# 81. Migration Discipline

Database migrations must be:

- versioned
- repeatable
- tested
- non-destructive where possible

Do not perform destructive schema changes without understanding existing data.

During MVP development:

```text
Schema Change
    ↓
Migration
    ↓
Test
    ↓
Verify
```

---

# 82. Development Database

SQLite may be used as a local development/testing convenience if practical.

This does not change the production requirement:

```text
Production
    ≠
Local SQLite-only architecture
```

If SQLite is used locally, compatibility-sensitive features should be checked against the intended production relational database.

---

# 83. Production Database Decision

The production database technology/provider is currently:

> **OPEN**

Selection should consider:

- persistence
- reliability
- deployment simplicity
- cost
- relational capability
- team familiarity
- judge accessibility
- migration effort

Do not lock the project to a provider solely because it is convenient for local development.

---

# 84. Object Storage Decision

The production object/file storage provider is currently:

> **OPEN**

It must support persistent evidence storage suitable for the deployed application.

Requirements include:

- durable storage
- controlled access
- appropriate object identifiers
- integration with backend authorization
- evidence integrity metadata
- sufficient capacity for demonstration

The exact provider remains a team implementation decision.

---

# 85. Backup / Recovery

The deployed system should rely on the persistence provider's appropriate durability/backup capabilities.

At minimum, the architecture must avoid making the local development machine the only copy of inspection evidence.

Detailed disaster-recovery architecture is target-system scope and not a one-day MVP priority unless required by deployment.

---

# 86. Data Consistency

Important consistency rules:

```text
Evidence belongs to an Inspection
Declaration belongs to an Inspection
Assessment belongs to an Inspection
Finding references valid Assessment
Finding references valid Evidence
Final Snapshot references valid historical data
Audit Event references valid affected resources
```

Broken relationships should be treated as data-integrity failures.

---

# 87. State Consistency

The database must support:

```text
Lifecycle State
+
Processing State
+
Compliance Result
+
Review State
```

without confusing them.

Example:

```text
Inspection Status = UNDER_REVIEW
MRP Result = POTENTIAL_NON_COMPLIANCE
Consumer Care Result = PASS
```

This is valid.

---

# 88. State Invalidation

When upstream data changes:

```text
Upstream Data
      ↓
Affected Assessment
      ↓
Affected Finding
      ↓
Invalidate
      ↓
Recompute
```

The database must not leave stale results marked as current.

---

# 89. Current vs Historical Values

The model should distinguish:

```text
CURRENT VERIFIED VALUE
        from
HISTORICAL VALUE
```

For example:

```text
AI extracted MRP = ₹199
Inspector corrected MRP = ₹179
```

Both are historically relevant.

The current verified value can be ₹179 while the old observation remains available in history.

---

# 90. Finalized Historical Values

After finalization:

```text
Final Snapshot
      ↓
Historical Value Set
```

Future changes to the working system must not modify the snapshot.

---

# 91. Rule/Model Provenance

A final record should be explainable in terms of:

```text
Rule Snapshot
OCR Engine / Version
AI Model / Version
Processing Time
Evidence References
```

The exact prompt retention strategy may be determined during implementation.

---

# 92. Database and AI Boundary

The database stores AI observations.

It does not decide whether the AI output is legally correct.

The architecture remains:

```text
AI Output
   ↓
Validation
   ↓
Database Observation
   ↓
Applicability
   ↓
Rule Evaluation
```

Do not encode legal conclusions directly into AI storage tables.

---

# 93. Database and Compliance Rule Boundary

The database stores:

```text
Rule Snapshot
Assessment
Rule Reference
```

The rule logic itself should remain controlled application/domain logic or an explicitly versioned rule representation.

Do not make compliance behavior depend on arbitrary user-editable database fields.

---

# 94. Database and Reviewer Boundary

Reviewer decisions are stored separately from system assessments.

Conceptually:

```text
System Assessment
        ↓
Reviewer Decision
        ↓
Final Snapshot
```

The database must preserve the distinction.

---

# 95. Database and Inspector Boundary

Inspector corrections should be stored as human verification/correction data.

Do not overwrite the AI provenance.

```text
AI Observation
      +
Inspector Correction
      ↓
Verified Current Value
```

---

# 96. Finalization Read Model

The final snapshot should provide a stable read model for:

- final report
- historical inspection view
- audit review
- future retrieval

This reduces dependence on mutable working-state tables after finalization.

---

# 97. Report Relationship

```text
Inspection
    ↓
Final Snapshot
    ↓
Report
```

For preliminary output, a report may reference the current working state if explicitly supported.

For final reports, the source should be the final snapshot.

---

# 98. Target Repository / Search

The relational model should support future retrieval by:

```text
inspection_id
date
status
result
product
inspector
reviewer
```

Authorization must still be applied.

The one-day MVP may expose only minimal history.

---

# 99. Current MVP Data Model

The minimum practical persisted model should support:

```text
User / Actor
      ↓
Inspection
      ├── Product / Context
      ├── Evidence
      ├── OCR
      ├── Declarations
      ├── Applicability
      ├── Assessments
      ├── Findings
      ├── Corrections / Verification
      └── Basic Audit
```

If Reviewer/finalization is implemented in the MVP:

```text
      ├── Submission
      ├── Review
      ├── Evidence Requests
      └── Final Snapshot
```

The physical schema may be smaller than the full target model if the semantics remain intact.

---

# 100. Current MVP Persistence Definition of Done

The database/storage layer is sufficient when the deployed MVP can reliably:

```text
1. Create an inspection
2. Persist inspection context
3. Persist original evidence
4. Preserve evidence hash/provenance
5. Persist OCR observations
6. Persist AI declaration observations
7. Persist source references
8. Persist applicability
9. Persist six compliance assessments
10. Persist findings
11. Persist Inspector corrections
12. Preserve correction history
13. Recompute affected downstream state
14. Persist final/current result
15. Survive application restart
16. Support deployed persistent storage
```

If Reviewer workflow is implemented:

```text
17. Persist submission
18. Persist Reviewer decision
19. Persist evidence requests
20. Persist final snapshot
21. Protect finalized historical state
22. Generate report from final state
```

---

# 101. Database Testing Priorities

P0 tests:

```text
Create inspection
Persist evidence
Retrieve evidence metadata
Verify hash
Persist OCR
Persist declarations
Persist provenance
Persist applicability
Persist assessments
Persist findings
Correct declaration
Verify downstream invalidation
Verify recomputation
Persist result
Restart application
Verify data still exists
```

Reviewer/finalization tests:

```text
Submit
Review
Request evidence
Respond
Decision
Finalize
Retrieve final snapshot
Attempt forbidden mutation
```

---

# 102. Data Integrity Tests

The following must be tested:

### Evidence

```text
Original evidence remains unchanged
Hash remains consistent
New evidence receives new ID
```

### Corrections

```text
Old value preserved
New value stored
Affected result recomputed
```

### Finalization

```text
Snapshot created
Finalized state persisted
Mutation rejected
```

### Rules

```text
Rule snapshot preserved
Historical inspection not silently recalculated
```

---

# 103. Performance Considerations

For the one-day MVP, optimize for:

- correctness
- persistence reliability
- simple queries
- clear relationships
- deployment stability

Do not prematurely optimize for:

- millions of inspections
- massive analytical workloads
- distributed databases
- sharding
- data warehouses
- complex event sourcing

The target architecture can evolve later.

---

# 104. Avoid Unnecessary Microservices

The database architecture must not force a microservice architecture.

A practical MVP may use:

```text
One backend application
        ↓
Relational Database
        +
Object Storage
```

with logical modules inside the backend.

The 25 logical architecture components do not require 25 databases or services.

---

# 105. Transaction and Concurrency Safety

Where two actors could change the same record:

```text
Read Current State
      ↓
Validate Version / State
      ↓
Write
      ↓
Commit
```

Optimistic locking/version fields may be used where appropriate.

The exact implementation remains open.

---

# 106. Soft vs Hard Delete

Use deletion conservatively.

For protected historical resources:

```text
No normal deletion
```

For temporary development data, deletion may be allowed under controlled environments.

Do not use deletion to hide errors or audit history.

---

# 107. Data Privacy Principle

Store only what the workflow needs.

Minimize:

- personal information
- unnecessary metadata
- unnecessary raw AI data
- credentials
- secrets

Access to inspection/evidence records should be role- and resource-aware.

---

# 108. Data Export

Exports should be generated from authoritative current/final data.

For finalized reports:

```text
Final Snapshot
     ↓
Export
```

Do not build final reports from mutable UI state.

---

# 109. Schema Evolution

The schema must allow future expansion without requiring the one-day MVP to implement the future.

Examples:

```text
New compliance requirement
New evidence type
New rule version
New review capability
Physical ↔ Online comparison
```

Future extensibility should not justify speculative tables or infrastructure today.

---

# 110. Database Documentation Authority

This document is authoritative for:

- persistence entities
- persistence relationships
- historical-data semantics
- evidence metadata
- snapshot semantics
- database integrity requirements

Other documents may reference these definitions but should not silently redefine them.

---

# 111. Relationship to Other Documents

| Document | Relationship |
|---|---|
| `MVP_BUILD_SCOPE.md` | Defines current persisted MVP subset |
| `PROJECT_STATE.md` | Records actual persistence implementation state |
| `PHASE.md` | Defines when persistence capabilities are implemented |
| `AGENT_ENGINEERING_PROTOCOL.md` | Controls database implementation decisions |
| `05_Domain_Specification.md` | Defines domain meanings |
| `06_Compliance_Rules.md` | Defines rule semantics |
| `07_State_Machine.md` | Defines lifecycle states/transitions |
| `08_API_Specification.md` | Defines API access to persisted data |
| `10_Error_Handling.md` | Defines persistence/processing failure behavior |
| `11_Testing_and_Release_Gate.md` | Defines persistence validation |

---

# 112. Implementation Rules

The implementation agent must:

1. Inspect the current database before changing it.
2. Reuse working schema where safe.
3. Avoid destructive migrations without approval.
4. Preserve evidence provenance.
5. Preserve correction history.
6. Preserve final snapshots.
7. Keep lifecycle state authoritative.
8. Keep API authorization authoritative.
9. Keep rules controlled.
10. Test migrations.
11. Test persistence after application restart.
12. Verify production storage behavior.
13. Avoid local-only production assumptions.
14. Record material schema decisions in project state.

---

# 113. Current Technology Status

The final production database is:

> **NOT LOCKED**

The final object storage provider is:

> **NOT LOCKED**

The implementation may choose a suitable cloud-capable relational database and persistent object storage based on:

- reliability
- simplicity
- deployment
- cost
- team familiarity
- judge accessibility

The choice should not expand the MVP scope unnecessarily.

---

# 114. Current Project State

### Persistence Architecture

**Status: DECIDED**

Production requires:

```text
Persistent relational DB
+
Persistent object/file storage
```

### Local SQLite

**Status: DEVELOPMENT/TEST ONLY**

SQLite is not the deployed production source of truth.

### Evidence Storage

**Status: DECIDED**

Original evidence requires persistent protected storage and integrity metadata.

### Historical Data

**Status: DECIDED**

Finalized records are protected historical snapshots.

### Rule Versioning

**Status: DECIDED**

Historical assessments retain the rule snapshot/version used.

### Exact Provider

**Status: OPEN**

Production database/storage provider remains a team implementation decision.

### Actual Implementation

**Status: MUST BE VERIFIED**

This document defines intended persistence behavior. It does not prove that the repository currently implements it.

---

# 115. Final Database Mental Model

The persistence system can be remembered as:

```text
INSPECTION
   │
   ├── CONTEXT
   ├── EVIDENCE
   │     └── HASH + PROVENANCE
   ├── OCR
   ├── AI OBSERVATIONS
   ├── APPLICABILITY
   ├── ASSESSMENTS
   ├── FINDINGS
   ├── INSPECTOR CORRECTIONS
   ├── REVIEWER DECISIONS
   ├── AUDIT HISTORY
   └── FINAL SNAPSHOT
             │
             ▼
          REPORT
```

The database should preserve the chain:

```text
Evidence
   ↓
Observation
   ↓
Applicability
   ↓
Assessment
   ↓
Finding
   ↓
Verification
   ↓
Review
   ↓
Final Snapshot
```

---

# 116. Final Persistence Principles

The database implementation must preserve these principles:

> **Evidence is immutable.**

> **Observations are not legal conclusions.**

> **AI output is not automatically trusted.**

> **Applicability precedes compliance assessment.**

> **Corrections preserve history and invalidate affected downstream state.**

> **Reviewer decisions remain distinct from system assessments.**

> **Finalized inspections are historical snapshots.**

> **Technical failures are not compliance failures.**

> **Historical rule context is preserved.**

> **Production persistence is cloud-capable from the beginning.**

> **The MVP stores only what is necessary to complete one reliable inspection journey.**

---

# 117. Final Contract

The database exists to make the ComplianceScan workflow:

```text
PERSISTENT
TRACEABLE
AUDITABLE
EVIDENCE-BACKED
STATE-SAFE
DEPLOYABLE
```

while avoiding unnecessary complexity.

The governing implementation principle is:

> **Store enough to explain what happened, preserve what was observed, protect what was finalized, and keep the one-day MVP simple enough to finish.**
