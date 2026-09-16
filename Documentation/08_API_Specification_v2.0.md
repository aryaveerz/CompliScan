# 08 — API SPECIFICATION

**Project:** ComplianceScan  
**SIH'26 Problem Statement:** 26034  
**Document Version:** 2.0  
**Status:** Target API contract with controlled one-day MVP subset

---

# 1. Purpose

This document defines the backend API contract for ComplianceScan.

It describes:

- API responsibilities
- authentication and authorization boundaries
- inspection lifecycle APIs
- evidence APIs
- processing APIs
- OCR and AI processing contracts
- declaration extraction
- applicability
- compliance assessment
- findings
- Inspector verification
- Reviewer workflow
- evidence requests
- finalization
- reporting
- repository/history
- search/dashboard interfaces
- error handling
- state-transition rules
- current one-day MVP API subset

The API is designed around:

> **AI finds → Evidence proves → Officer decides.**

The backend is authoritative for security, lifecycle, compliance evaluation, evidence integrity, and finalization.

---

# 2. Scope Model

The API specification describes the broader target system.

The current one-day MVP implements only the subset required for the complete vertical slice.

```text
TARGET API
    │
    │ controlled subset
    ▼
CURRENT MVP API
```

The current implementation boundary is defined by:

> `MVP_BUILD_SCOPE.md`

Actual implementation status is defined by:

> `PROJECT_STATE.md`

Execution order is defined by:

> `PHASE.md`

Agent behavior is defined by:

> `AGENT_ENGINEERING_PROTOCOL.md`

This document is authoritative for API contract semantics.

---

# 3. API Design Principles

The API must follow these principles:

1. Backend authorization is authoritative.
2. Lifecycle transitions are validated server-side.
3. Client input is never trusted blindly.
4. Original evidence is immutable.
5. AI output is treated as uncertain observation data.
6. Compliance evaluation is deterministic and controlled.
7. Applicability precedes compliance assessment.
8. Important findings retain evidence provenance.
9. Upstream corrections invalidate affected downstream state.
10. Finalization is Reviewer-controlled.
11. Finalized records are protected from normal mutation.
12. Technical failures are distinct from compliance outcomes.
13. APIs must return explicit state/result information.
14. Critical transitions should be auditable.
15. The deployed API must work with persistent cloud-capable storage.

---

# 4. Base API Structure

A versioned API is recommended:

```text
/api/v1
```

Example:

```text
/api/v1/inspections
/api/v1/evidence
/api/v1/processing
/api/v1/findings
/api/v1/reviews
```

The exact public deployment prefix may vary by hosting configuration, but the logical API contract should remain stable.

---

# 5. Authentication

Authentication establishes the identity of the caller.

The API must not rely on frontend state to establish identity.

Conceptually:

```text
Client
  ↓
Authentication
  ↓
Authenticated Identity
  ↓
Backend Authorization
  ↓
API Operation
```

The exact authentication technology remains open until implementation/team discussion.

The implementation must not expose secrets or AI provider credentials to the browser.

---

# 6. Authorization

Authorization is backend-authoritative.

Every protected operation should evaluate:

```text
Authenticated User
       +
Role
       +
Resource Ownership / Access
       +
Current Lifecycle State
       ↓
Allowed / Denied
```

Target operational roles:

- Inspector
- Reviewer

A technical administrator may exist separately if required by deployment, but it is not part of the operational inspection workflow.

---

# 7. Role Permissions

## Inspector

Allowed operations include:

- create inspection
- update working inspection
- provide product/context information
- upload evidence
- initiate analysis
- inspect OCR/declarations/findings
- correct extracted values
- add manual observations
- add supplemental evidence
- verify applicability
- verify assessment
- submit for review
- view preliminary results

Inspector cannot:

- change compliance rules
- finalize
- modify original evidence
- delete protected evidence
- alter audit history
- mutate finalized records
- approve their own final decision

## Reviewer

Allowed operations include:

- view submitted inspections
- search/filter/sort review records
- inspect evidence/OCR/declarations/applicability/findings/history
- confirm assessment
- correct/override assessment with reason
- request additional evidence
- finalize

Reviewer cannot:

- modify the controlled rule set through ordinary review workflow
- delete finalized historical records
- silently mutate finalized records

---

# 8. Common Resource Identifiers

Resources should use server-generated identifiers.

Examples:

```text
inspection_id
evidence_id
finding_id
evidence_request_id
review_id
audit_event_id
report_id
```

Identifiers must not be predictable in a way that bypasses authorization.

Example Evidence Request ID:

```text
ER-00017
```

The exact identifier format may be implemented differently, but references must remain unique and traceable.

---

# 9. Inspection Resource

An inspection represents a single inspection workflow.

Conceptual fields include:

```text
inspection_id
status
product_context
created_by
assigned_reviewer
created_at
updated_at
submitted_at
finalized_at
current_result
rule_snapshot_version
provenance
```

The exact persistence representation is defined in `09_Database_Specification.md`.

---

# 10. Inspection Lifecycle

The target lifecycle is:

```text
DRAFT
  ↓
CONTEXT_READY
  ↓
EVIDENCE_PROVIDED
  ↓
PROCESSING
  ↓
DECLARATIONS_READY
  ↓
APPLICABILITY_READY
  ↓
ASSESSMENT_READY
  ↓
FINDINGS_READY
  ↓
INSPECTOR_VERIFICATION
  ↓
SUBMITTED
  ↓
UNDER_REVIEW
  ↓
REVIEW_DECISION
  ↓
FINALIZED
```

Additional states include:

```text
INCOMPLETE
REQUIRES_REVIEW
PROCESSING_FAILED
EVIDENCE_REQUESTED
```

The implementation may combine internal technical processing states where appropriate, but externally meaningful lifecycle semantics must remain consistent.

---

# 11. Create Inspection

### Endpoint

```http
POST /api/v1/inspections
```

### Actor

Inspector

### Purpose

Create a new inspection working record.

### Request

Conceptual:

```json
{
  "product_name": "Example Product",
  "inspection_context": {
    "imported": "unknown"
  }
}
```

The request schema must be validated server-side.

### Response

```json
{
  "inspection_id": "INS-...",
  "status": "DRAFT",
  "created_at": "..."
}
```

---

# 12. Get Inspection

### Endpoint

```http
GET /api/v1/inspections/{inspection_id}
```

### Actor

Authorized user

### Purpose

Return the inspection and its currently available information.

The response may include:

- lifecycle state
- product/context
- evidence references
- processing status
- declarations
- applicability
- assessments
- findings
- verification information
- review status
- finalization information where authorized

---

# 13. Update Inspection Context

### Endpoint

```http
PATCH /api/v1/inspections/{inspection_id}
```

### Actor

Inspector, while permitted by lifecycle state

### Purpose

Update working inspection/context information.

The backend must:

1. validate actor
2. validate current state
3. validate fields
4. identify downstream dependencies
5. invalidate affected downstream results
6. recompute where required
7. record material changes

A finalized inspection cannot be updated through this endpoint.

---

# 14. Evidence API

Evidence is a first-class resource.

### Primary endpoint

```http
POST /api/v1/inspections/{inspection_id}/evidence
```

### Actor

Inspector, where lifecycle permits

### Purpose

Upload and register evidence.

The backend must perform:

- authentication
- authorization
- MIME/type validation
- size validation
- image decode validation where applicable
- server-generated Evidence ID
- persistent storage
- integrity hash
- provenance
- inspection association
- audit event

---

# 15. Evidence Response

Conceptual response:

```json
{
  "evidence_id": "EVD-...",
  "inspection_id": "INS-...",
  "type": "PRIMARY",
  "sha256": "...",
  "created_at": "...",
  "immutable": true
}
```

The API must not expose internal storage paths unnecessarily.

---

# 16. Get Evidence Metadata

### Endpoint

```http
GET /api/v1/evidence/{evidence_id}
```

### Actor

Authorized user

### Purpose

Return evidence metadata and provenance.

The endpoint must enforce authorization before returning protected evidence information.

---

# 17. Access Evidence

### Endpoint

```http
GET /api/v1/evidence/{evidence_id}/content
```

### Actor

Authorized user

### Purpose

Retrieve the evidence content or an appropriately protected access mechanism.

The exact delivery method may be:

- authenticated streaming
- short-lived signed URL
- controlled backend proxy

The implementation choice remains open.

Evidence must not become publicly accessible merely because the identifier is known.

---

# 18. Evidence Immutability

The original evidence cannot be modified through normal API operations.

Forbidden:

```http
PUT /evidence/{id}
```

for replacing original evidence.

If a new image is supplied:

```text
New Image
   ↓
New Evidence ID
```

The old evidence remains preserved.

---

# 19. Add Supplemental Evidence

### Endpoint

```http
POST /api/v1/inspections/{inspection_id}/evidence
```

with evidence type:

```text
SUPPLEMENTAL
```

Supplemental evidence follows the same integrity and authorization requirements as primary evidence.

It must be traceable to the inspection and, where applicable, the Evidence Request ID that caused its addition.

---

# 20. Start Processing

### Endpoint

```http
POST /api/v1/inspections/{inspection_id}/processing
```

### Actor

Inspector, where lifecycle permits

### Purpose

Start the analysis pipeline.

Conceptually:

```text
Evidence
  ↓
Image Processing
  ↓
PaddleOCR
  ↓
Gemini
  ↓
Validation
  ↓
Applicability
  ↓
Compliance
  ↓
Findings
```

The endpoint must not directly perform every operation inside the HTTP request if asynchronous processing is required for deployment. The exact execution model remains implementation-dependent.

---

# 21. Processing Status

### Endpoint

```http
GET /api/v1/inspections/{inspection_id}/processing
```

### Response

Conceptual:

```json
{
  "inspection_id": "INS-...",
  "status": "PROCESSING",
  "stage": "OCR",
  "progress": null,
  "error": null
}
```

Progress should not be fabricated if the backend cannot reliably measure it.

---

# 22. Processing Stages

Conceptual processing stages:

```text
IMAGE_PROCESSING
OCR
DECLARATION_EXTRACTION
VALIDATION
APPLICABILITY
COMPLIANCE
FINDINGS
```

The API may expose fewer technical stages, but failure provenance should remain sufficient to determine where processing failed.

---

# 23. OCR Result API

### Endpoint

```http
GET /api/v1/inspections/{inspection_id}/ocr
```

### Purpose

Return OCR observations.

Conceptual structure:

```json
{
  "evidence_id": "EVD-...",
  "text": "...",
  "regions": [
    {
      "text": "MRP Rs. 179",
      "bbox": [100, 200, 300, 250],
      "confidence": 0.96
    }
  ]
}
```

OCR confidence is not a compliance result.

---

# 24. Declaration Extraction API

### Endpoint

```http
GET /api/v1/inspections/{inspection_id}/declarations
```

### Purpose

Return structured declaration observations.

Conceptual:

```json
{
  "manufacturer": {
    "value": "Example Pvt Ltd",
    "status": "OBSERVED",
    "confidence": 0.94,
    "source": [
      {
        "evidence_id": "EVD-...",
        "ocr_region_id": "OCR-..."
      }
    ]
  }
}
```

---

# 25. Declaration Status Values

Allowed observation statuses:

```text
OBSERVED
NOT_OBSERVED
UNCERTAIN
UNREADABLE
CONFLICTING
```

The API must not invent additional semantic states that collapse these distinctions without a documented reason.

---

# 26. Declaration Correction

### Endpoint

```http
PATCH /api/v1/inspections/{inspection_id}/declarations/{field}
```

### Actor

Inspector, before finalization and where lifecycle permits

### Purpose

Correct an extracted/normalized value based on human verification.

Example:

```json
{
  "value": "₹179",
  "reason": "Inspector verified package image"
}
```

The backend must:

1. authorize the Inspector
2. preserve the original value
3. record the new value
4. identify affected downstream data
5. invalidate affected assessments/findings
6. recompute affected results
7. audit the transition

---

# 27. Manual Observation API

### Endpoint

```http
POST /api/v1/inspections/{inspection_id}/observations
```

### Actor

Inspector

### Purpose

Record an observation that cannot or should not be represented solely by AI extraction.

The observation should identify:

- field/fact
- observation
- reason
- optional evidence reference
- actor
- timestamp

Manual observation does not silently overwrite the original AI output.

---

# 28. Applicability API

### Endpoint

```http
GET /api/v1/inspections/{inspection_id}/applicability
```

### Purpose

Return applicability decisions for supported requirements.

Conceptual:

```json
{
  "country_of_origin": {
    "applicable": true,
    "status": "APPLICABLE",
    "reason": "Imported product"
  }
}
```

The exact schema may represent `NOT_APPLICABLE` directly.

Applicability must precede compliance evaluation.

---

# 29. Applicability Update

Where Inspector verification can change applicability:

```http
PATCH /api/v1/inspections/{inspection_id}/applicability
```

The backend must invalidate affected compliance assessments when applicability changes.

Example:

```text
Imported = NO
    ↓
Country of Origin
    ↓
NOT_APPLICABLE
```

If the Inspector changes the context:

```text
Imported = YES
    ↓
Country of Origin
    ↓
Re-evaluate requirement
```

---

# 30. Compliance Assessment API

### Endpoint

```http
GET /api/v1/inspections/{inspection_id}/assessments
```

### Purpose

Return requirement-level compliance assessments.

Current MVP requirements:

1. Manufacturer / Packer / Importer
2. Common / Generic Product Name
3. Net Quantity + Standard Unit
4. Month / Year of Manufacture / Packing / Import
5. MRP inclusive of all taxes
6. Consumer Care Details

Country of Origin is applicability-driven.

---

# 31. Compliance Assessment Structure

Conceptual:

```json
{
  "requirement": "MRP",
  "result": "POTENTIAL_NON_COMPLIANCE",
  "reason": "...",
  "rule_reference": "...",
  "evidence": [
    "EVD-..."
  ],
  "source_regions": [
    "OCR-..."
  ]
}
```

The API should expose system assessment separately from Reviewer decision where both exist.

---

# 32. Result Vocabulary

Allowed compliance results:

```text
PASS
POTENTIAL_NON_COMPLIANCE
REQUIRES_REVIEW
NOT_APPLICABLE
INCOMPLETE
PROCESSING_FAILED
```

The API must preserve these distinctions.

---

# 33. Findings API

### Endpoint

```http
GET /api/v1/inspections/{inspection_id}/findings
```

### Purpose

Return evidence-backed findings.

A finding should include:

```text
finding_id
requirement
result
reason
rule_reference
evidence_refs
source_regions
confidence/uncertainty
created_at
status
```

---

# 34. Finding Evidence

A finding must be traceable.

Conceptually:

```text
Finding
  ↓
Requirement
  ↓
Rule Reference
  ↓
Observation
  ↓
Evidence
  ↓
Image Region
```

The API should make these relationships navigable.

---

# 35. Inspector Verification API

### Endpoint

```http
POST /api/v1/inspections/{inspection_id}/verify
```

### Actor

Inspector

### Purpose

Record Inspector verification of the working assessment.

Possible actions:

```text
CONFIRM
CORRECT
ADD_OBSERVATION
ADD_EVIDENCE
LEAVE_UNRESOLVED
```

The exact request schema should ensure that unresolved uncertainty is not accidentally represented as confirmation.

---

# 36. Inspector Verification Rules

The backend must ensure:

- inspection belongs/is accessible to Inspector
- inspection is in a verifiable state
- required processing has completed or appropriate manual workflow exists
- corrections are validated
- downstream results are recomputed
- material actions are auditable

Inspector verification does not finalize the inspection.

---

# 37. Submit for Review

### Endpoint

```http
POST /api/v1/inspections/{inspection_id}/submit
```

### Actor

Inspector

### Purpose

Submit a prepared and verified inspection for independent review.

The backend must validate:

- current state
- Inspector authorization
- required information
- applicable assessments
- evidence requirements
- absence of blocking processing errors

On success:

```text
INSPECTOR_VERIFICATION
        ↓
SUBMITTED
```

---

# 38. Submission Boundary

After successful submission:

```text
Inspector
    ↓
No longer controls review decision

Reviewer
    ↓
Controls review
```

The backend must enforce this boundary.

The Inspector cannot use ordinary edit APIs to mutate a submitted inspection in a way that bypasses the review workflow.

---

# 39. Reviewer Queue API

### Endpoint

```http
GET /api/v1/reviews
```

### Actor

Reviewer

### Purpose

Return inspections available for review.

Supported capabilities may include:

- filtering
- sorting
- status filtering
- search
- pagination

Advanced repository/search behavior remains part of the broader target system.

---

# 40. Reviewer Inspection API

### Endpoint

```http
GET /api/v1/reviews/{inspection_id}
```

### Actor

Reviewer

### Purpose

Return a review-oriented inspection view including:

- inspection context
- evidence
- OCR
- declarations
- applicability
- assessments
- findings
- Inspector corrections
- audit/history
- processing provenance

---

# 41. Reviewer Decision API

### Endpoint

```http
POST /api/v1/reviews/{inspection_id}/decision
```

### Actor

Reviewer

### Purpose

Record the independent Reviewer decision.

Possible actions:

```text
CONFIRM
CORRECT
OVERRIDE
REQUEST_EVIDENCE
```

A correction or override requires an appropriate reason.

---

# 42. Reviewer Correction / Override

Conceptual request:

```json
{
  "action": "OVERRIDE",
  "requirement": "MRP",
  "result": "PASS",
  "reason": "Reviewer verified supporting evidence"
}
```

The API must preserve:

```text
Original System Assessment
        +
Reviewer Decision
        +
Reason
        +
Actor
        +
Timestamp
```

The original system assessment must not be erased.

---

# 43. Evidence Request API

### Endpoint

```http
POST /api/v1/reviews/{inspection_id}/evidence-requests
```

### Actor

Reviewer

### Purpose

Request additional evidence or clarification.

Conceptual request:

```json
{
  "requirement": "NET_QUANTITY",
  "reason": "Unit is not sufficiently visible",
  "requested_evidence": "Clear evidence of quantity and unit"
}
```

Response:

```json
{
  "evidence_request_id": "ER-00017",
  "status": "OPEN"
}
```

---

# 44. Evidence Request Lifecycle

```text
UNDER_REVIEW
      ↓
EVIDENCE_REQUESTED
      ↓
Inspector response
      ↓
Supplemental evidence / manual observation /
unable to establish
      ↓
Re-analysis if affected
      ↓
Inspector verification
      ↓
SUBMITTED
      ↓
UNDER_REVIEW
```

The request must not automatically force a camera recapture.

---

# 45. Evidence Request Status

Conceptual statuses:

```text
OPEN
RESPONDED
RESOLVED
UNRESOLVED
CANCELLED
```

The exact status model may be simplified for the MVP.

---

# 46. Audit API

### Endpoint

```http
GET /api/v1/inspections/{inspection_id}/audit
```

### Actor

Authorized Reviewer and other permitted roles

### Purpose

Return relevant lifecycle and material-change history.

Events may include:

- creation
- evidence addition
- processing
- correction
- applicability change
- assessment change
- evidence request
- submission
- Reviewer decision
- finalization
- relevant failure/recovery

Audit records must not be silently altered.

---

# 47. Finalization API

### Endpoint

```http
POST /api/v1/reviews/{inspection_id}/finalize
```

### Actor

Reviewer

### Purpose

Finalize the inspection.

The backend must validate:

```text
Reviewer authorization
        +
Correct lifecycle state
        +
Required data
        +
Valid evidence
        +
Valid rule snapshot
        +
Resolved blocking issues
        ↓
Atomic finalization
```

---

# 48. Finalization Response

Conceptual:

```json
{
  "inspection_id": "INS-...",
  "status": "FINALIZED",
  "final_result": "PASS",
  "finalized_at": "...",
  "snapshot_id": "SNAP-..."
}
```

The exact final-result aggregation logic must remain aligned with the compliance rules.

---

# 49. Finalization Immutability

After finalization, normal mutation APIs must reject changes.

Examples:

```text
PATCH finalized inspection
    → 409 / lifecycle conflict

DELETE finalized evidence
    → 403 / 409

Change rule version
    → forbidden

Modify final decision
    → forbidden
```

The exact HTTP status depends on the implementation's error conventions.

---

# 50. Final Snapshot API

### Endpoint

```http
GET /api/v1/inspections/{inspection_id}/final
```

### Actor

Authorized user

### Purpose

Return the historical finalized representation.

It should include or reference:

- inspection
- product/context
- evidence
- hashes
- OCR
- declarations
- applicability
- assessments
- findings
- corrections
- reviews
- rule snapshot/version
- provenance
- final decision
- audit references

---

# 51. Report API

### Endpoint

```http
POST /api/v1/inspections/{inspection_id}/reports
```

### Actor

Authorized user, subject to lifecycle rules

### Purpose

Generate a report from the final/preliminary inspection state as permitted.

For finalized inspections:

```text
Final Snapshot
      ↓
Report
```

Report generation must not mutate the finalized decision.

---

# 52. Retrieve Report

### Endpoint

```http
GET /api/v1/reports/{report_id}
```

### Actor

Authorized user

The report may be:

- PDF
- editable format
- other approved export

The exact format set may be reduced for the one-day MVP.

---

# 53. Report Failure

If report generation fails:

```text
FINALIZED
     +
REPORT GENERATION FAILED
```

The finalized inspection remains finalized.

Report failure must not roll back the final decision.

---

# 54. Repository / History API

Target endpoints may include:

```http
GET /api/v1/inspections/history
GET /api/v1/inspections/search
```

Capabilities:

- search
- filtering
- sorting
- pagination
- date/status filters
- reviewer/inspector filters where authorized

Advanced repository behavior is target-system scope and may be deferred from the one-day MVP.

---

# 55. Dashboard API

Target endpoints may include:

```http
GET /api/v1/dashboard/summary
GET /api/v1/dashboard/metrics
```

Possible metrics:

- inspection counts
- result distribution
- processing failures
- review backlog
- completion time
- common findings

Dashboard implementation is not required for the core one-day vertical slice unless needed for demonstration.

---

# 56. Current MVP API Subset

The minimum useful API surface should focus on:

```text
POST   /inspections
GET    /inspections/{id}
PATCH  /inspections/{id}

POST   /inspections/{id}/evidence
GET    /evidence/{id}
GET    /evidence/{id}/content

POST   /inspections/{id}/processing
GET    /inspections/{id}/processing

GET    /inspections/{id}/ocr
GET    /inspections/{id}/declarations

GET    /inspections/{id}/applicability
GET    /inspections/{id}/assessments
GET    /inspections/{id}/findings

PATCH  /inspections/{id}/declarations/{field}
POST   /inspections/{id}/observations
POST   /inspections/{id}/verify
POST   /inspections/{id}/submit
```

If Reviewer/finalization is included in the current MVP:

```text
GET    /reviews
GET    /reviews/{id}
POST   /reviews/{id}/decision
POST   /reviews/{id}/evidence-requests
POST   /reviews/{id}/finalize
GET    /inspections/{id}/final
```

The exact endpoint count should not be treated as a goal.

> **The smallest API that safely supports the complete vertical slice is preferred.**

---

# 57. Request Validation

All request bodies must be validated.

Validation should occur at multiple levels:

```text
HTTP / Schema Validation
        ↓
Domain Validation
        ↓
Lifecycle Validation
        ↓
Authorization
        ↓
Business Rules
```

Invalid requests must return structured errors.

---

# 58. Response Consistency

Responses should provide enough information for the frontend to understand:

- operation result
- current lifecycle state
- compliance result where applicable
- resource identifiers
- errors/warnings where relevant

The frontend should not have to infer backend state from UI behavior.

---

# 59. Error Response Model

A consistent error envelope is recommended:

```json
{
  "error": {
    "code": "INVALID_STATE",
    "message": "Inspection cannot be submitted in its current state.",
    "details": {},
    "request_id": "REQ-..."
  }
}
```

The exact field names may be adjusted during implementation.

Do not expose stack traces or secrets to clients.

---

# 60. Error Categories

Useful API error categories include:

```text
AUTHENTICATION_ERROR
AUTHORIZATION_ERROR
VALIDATION_ERROR
RESOURCE_NOT_FOUND
INVALID_STATE
CONFLICT
EVIDENCE_ERROR
PROCESSING_ERROR
AI_ERROR
RULE_ERROR
FINALIZATION_ERROR
STORAGE_ERROR
INTERNAL_ERROR
```

Technical error categories must remain distinct from compliance results.

---

# 61. HTTP Semantics

Recommended mappings:

```text
200 OK
201 Created
202 Accepted
204 No Content
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Unprocessable Entity
429 Too Many Requests
500 Internal Server Error
502/503 Upstream or Service Failure
```

The exact mapping may be standardized during implementation.

---

# 62. Idempotency

Critical state-changing operations should be protected against duplicate execution.

Especially:

```text
Submit
Finalize
Evidence creation
Processing start
Reviewer decision
```

Repeated requests must not:

- duplicate evidence
- duplicate finalization
- duplicate decisions
- corrupt lifecycle state
- create duplicate findings

---

# 63. Concurrency

The backend must protect lifecycle transitions from race conditions.

Example:

```text
Reviewer Finalize
        +
Inspector Edit
        ↓
Backend state validation
        ↓
One operation succeeds
Invalid concurrent mutation is rejected
```

The frontend is not sufficient to prevent concurrency conflicts.

---

# 64. Correction Invalidation

Any API that changes upstream information must identify affected downstream state.

Example:

```text
PATCH declaration
       ↓
Invalidate affected assessment
       ↓
Recompute
       ↓
Update findings
       ↓
Audit
```

This rule applies to:

- declaration correction
- context changes
- applicability changes
- supplemental evidence
- relevant manual observations

---

# 65. Evidence Provenance Contract

Every AI-derived declaration should be traceable through the API to:

```text
Declaration
   ↓
OCR Region
   ↓
Evidence ID
   ↓
Original Evidence
```

A finding should additionally be traceable to:

```text
Finding
   ↓
Requirement
   ↓
Rule Reference
   ↓
Assessment
   ↓
Evidence
```

---

# 66. AI Processing Contract

The backend must treat Gemini output as untrusted external input.

Processing sequence:

```text
Gemini Response
      ↓
Parse
      ↓
Schema Validate
      ↓
Domain Validate
      ↓
Source Validation
      ↓
Store Structured Observation
```

Malformed output must not be accepted as valid compliance data.

---

# 67. AI Failure Contract

If Gemini is unavailable:

```text
AI Failure
    ↓
PROCESSING_FAILED
```

If a controlled retry succeeds:

```text
Retry
  ↓
Continue
```

If retry fails:

```text
PROCESSING_FAILED
```

Never:

```text
AI Failure
    ↓
POTENTIAL_NON_COMPLIANCE
```

---

# 68. OCR Failure Contract

If PaddleOCR fails:

```text
OCR Failure
    ↓
PROCESSING_FAILED
```

The system must not claim that declarations are absent merely because OCR failed.

Where possible, the Inspector may use a manual observation/evidence workflow.

---

# 69. Rule API Boundary

Compliance rules are controlled backend logic.

The normal operational API must not allow Inspectors or Reviewers to modify rules.

Target rule-management interfaces, if required in a future system, are outside the current operational MVP roles.

---

# 70. Rule Snapshot

Every compliance evaluation should be associated with the rule snapshot/version used.

Conceptually:

```json
{
  "rule_snapshot_version": "LM-MVP-1.0"
}
```

The exact identifier may differ.

Historical finalized inspections retain the rule snapshot under which they were evaluated.

---

# 71. No Silent Historical Recalculation

An API request such as:

```text
GET historical finalized inspection
```

must not trigger:

```text
Current rules
     ↓
Recalculate old inspection
     ↓
Change historical result
```

Historical data remains historically consistent.

---

# 72. Authorization Examples

### Inspector accessing own draft

```text
Allowed
```

### Inspector accessing another user's protected inspection

```text
Denied unless explicitly authorized
```

### Inspector finalizing

```text
Denied
```

### Reviewer finalizing a valid submitted inspection

```text
Allowed
```

### Client directly changing final result

```text
Denied
```

### Client changing rule set

```text
Denied
```

---

# 73. API and Lifecycle Invariants

The following are mandatory.

## Invariant 1

```text
No valid transition without backend state validation.
```

## Invariant 2

```text
No protected operation without backend authorization.
```

## Invariant 3

```text
No accepted AI fact without source provenance.
```

## Invariant 4

```text
No technical failure represented as compliance failure.
```

## Invariant 5

```text
No upstream correction without affected downstream invalidation.
```

## Invariant 6

```text
No normal mutation of finalized records.
```

## Invariant 7

```text
No original evidence replacement.
```

## Invariant 8

```text
Applicability precedes compliance evaluation.
```

## Invariant 9

```text
Reviewer controls finalization.
```

## Invariant 10

```text
Historical rule context is preserved.
```

---

# 74. Security Requirements

The API must enforce:

- authenticated access where required
- server-side authorization
- input validation
- protected evidence access
- safe file upload
- secret protection
- rate limiting where appropriate
- auditability of sensitive transitions
- safe error responses
- protected finalization

API keys for Gemini or other providers must never be exposed to the frontend.

---

# 75. Cloud Deployment Requirements

The API must be compatible with:

```text
Frontend
    ↓
Hosted Backend API
    ↓
Persistent Cloud Database
    +
Persistent Object/File Storage
    +
External AI/OCR dependencies
```

Do not assume:

```text
API process local disk
    =
Permanent evidence storage
```

The production deployment must use persistent storage.

---

# 76. Storage Boundary

The API should not make database rows responsible for storing large original image binaries unless that is an explicit implementation decision.

A typical logical separation is:

```text
Database
    ↓
Metadata / relationships / states / hashes

Object Storage
    ↓
Original images / derived artifacts / reports
```

The exact provider remains open.

---

# 77. API and Evidence Hashing

The upload operation should calculate/store the integrity hash server-side.

Do not trust a client-supplied hash as the authoritative integrity value.

Conceptually:

```text
Uploaded Bytes
      ↓
Backend
      ↓
SHA-256
      ↓
Stored Hash
```

---

# 78. Audit and API Actions

Material API operations should generate audit events.

Examples:

```text
CREATE_INSPECTION
ADD_EVIDENCE
START_PROCESSING
CORRECT_DECLARATION
CHANGE_APPLICABILITY
ADD_OBSERVATION
SUBMIT_INSPECTION
REVIEW_DECISION
REQUEST_EVIDENCE
FINALIZE_INSPECTION
```

The audit record should capture appropriate actor, time, action, object, and transition context.

---

# 79. Pagination

Collection APIs should support pagination where the result set can grow.

Example:

```http
GET /api/v1/reviews?page=1&page_size=20
```

The exact pagination mechanism can be cursor- or page-based.

The one-day MVP should not over-engineer pagination if only small datasets are expected, but APIs should not assume an infinite unbounded response.

---

# 80. Search and Filtering

Target repository APIs may support:

```text
status
date
inspector
reviewer
result
product
inspection_id
```

The MVP may implement only the filters required for demonstration.

Search must always respect backend authorization.

---

# 81. API Observability

The API should produce enough operational information to diagnose failures.

Where appropriate:

```text
request_id
inspection_id
processing_stage
actor_id
error_code
timestamp
```

Do not log:

- API keys
- authentication secrets
- unnecessary sensitive data
- unrestricted raw credentials

---

# 82. API Versioning

Breaking API changes should not silently replace a deployed contract.

Use explicit versioning where necessary:

```text
/api/v1
```

A new incompatible contract should use an appropriate new version or controlled migration.

---

# 83. Backward Compatibility

During MVP development, backward compatibility is secondary to correctness, but breaking changes must be identified.

When changing an API used by the frontend:

```text
Change Contract
      ↓
Update Backend
      ↓
Update Frontend
      ↓
Run Integration Test
```

Do not leave half-updated contracts.

---

# 84. API Testing Priorities

P0 tests:

```text
Create inspection
Upload evidence
Start processing
Receive OCR
Receive declarations
Validate declarations
Determine applicability
Evaluate six checks
Generate findings
Correct declaration
Recompute affected result
Verify
Submit
Persist
```

If Reviewer workflow is part of the current MVP:

```text
Reviewer receives
Review
Request evidence
Respond
Decision
Finalize
Retrieve final snapshot
```

---

# 85. API End-to-End Test

A representative API workflow should prove:

```text
POST inspection
       ↓
POST evidence
       ↓
POST processing
       ↓
GET processing
       ↓
GET OCR
       ↓
GET declarations
       ↓
GET applicability
       ↓
GET assessments
       ↓
GET findings
       ↓
PATCH declaration
       ↓
Verify recomputation
       ↓
POST verify
       ↓
POST submit
       ↓
Reviewer workflow where implemented
       ↓
Final result
```

A passing unit test is not proof that this entire workflow works.

---

# 86. Current MVP API Definition of Done

The API layer is sufficient for the one-day MVP when it can reliably support:

```text
1. Create inspection
2. Provide evidence
3. Persist evidence
4. Process evidence
5. Obtain PaddleOCR observations
6. Obtain Gemini structured declarations
7. Validate structured data
8. Determine applicability
9. Evaluate six supported checks
10. Generate evidence-backed findings
11. Allow Inspector verification/correction
12. Recompute affected downstream state
13. Produce a meaningful result
14. Persist the workflow
15. Support deployed demonstration
```

If Reviewer/finalization is included:

```text
16. Submit
17. Reviewer review
18. Evidence request where needed
19. Reviewer decision
20. Finalize
21. Retrieve immutable final snapshot
```

---

# 87. Deferred Target API Capabilities

The following are not required for the current one-day API implementation unless explicitly approved:

- full rule-management API
- broad category-specific rule APIs
- universal exemption configuration APIs
- advanced dashboard APIs
- full repository/search APIs
- internet-wide crawling APIs
- Physical ↔ Online Verification APIs
- advanced reporting/export APIs
- broad enforcement/follow-up APIs
- unnecessary administrative APIs
- microservice-to-microservice contracts that do not serve the MVP

---

# 88. API Implementation Guidance

Prefer:

```text
Simple
Explicit
Validated
State-aware
Authorization-aware
Evidence-aware
Auditable
Deployable
```

Avoid:

```text
Over-generalized
Speculative
Client-authoritative
State-ambiguous
Evidence-blind
Over-engineered
```

The number of endpoints is not a success metric.

A smaller, reliable API is preferred.

---

# 89. Relationship to Other Documents

| Document | API Relationship |
|---|---|
| `MVP_BUILD_SCOPE.md` | Defines current API subset |
| `PROJECT_STATE.md` | Records actual API implementation state |
| `PHASE.md` | Defines implementation sequence |
| `AGENT_ENGINEERING_PROTOCOL.md` | Defines implementation behavior |
| `05_Domain_Specification.md` | Defines domain semantics |
| `06_Compliance_Rules.md` | Defines compliance evaluation |
| `07_State_Machine.md` | Defines lifecycle transitions |
| `09_Database_Specification.md` | Defines persistence model |
| `10_Error_Handling.md` | Defines error/recovery semantics |
| `11_Testing_and_Release_Gate.md` | Defines API/workflow verification |

This document is authoritative for API contract semantics.

---

# 90. Final API Mental Model

The API can be remembered as:

```text
CREATE
  ↓
CAPTURE
  ↓
PROCESS
  ↓
READ
  ↓
UNDERSTAND
  ↓
APPLY
  ↓
ASSESS
  ↓
PROVE
  ↓
VERIFY
  ↓
SUBMIT
  ↓
REVIEW
  ↓
DECIDE
  ↓
FINALIZE
```

The backend remains the authority at every security-sensitive boundary.

---

# 91. Final Contract

The API must preserve the project's core principles:

> **PaddleOCR reads. Gemini understands. Backend validates. Applicability determines relevance. Rules evaluate. Evidence supports. Inspector verifies. Reviewer decides.**

And the lifecycle invariant:

> **Upstream correction → invalidate affected downstream state → recompute → preserve prior state/history → audit transition.**

And the deployment requirement:

> **The MVP must be deployable with persistent cloud-capable database and object/file storage from the beginning.**

And the scope principle:

> **The API should implement the smallest reliable contract necessary to demonstrate one complete user journey.**
