# 10 — ERROR HANDLING & RECOVERY SPECIFICATION

**Project:** ComplianceScan  
**SIH'26 Problem Statement:** 26034  
**Document Version:** 2.0  
**Status:** Target error/recovery model with controlled one-day MVP boundary

---

# 1. Purpose

This document defines how ComplianceScan detects, represents, contains, communicates, logs, and recovers from failures.

The primary objective is safe failure.

The system must never turn:

- technical failure into compliance failure
- uncertainty into certainty
- insufficient evidence into proven non-compliance
- stale data into a current result
- unauthorized action into a valid state transition

The governing principle is:

> **A failure must remain a failure of the layer where it occurred.**

---

# 2. Error-Handling Philosophy

ComplianceScan follows:

```text
Detect
  ↓
Classify
  ↓
Preserve Context
  ↓
Contain
  ↓
Recover if Possible
  ↓
Reprocess / Retry / Human Action
  ↓
Audit
```

The system must not hide failures behind a generic PASS/FAIL result.

---

# 3. Core Safety Principle

The most important invariant is:

> **Technical processing failure ≠ Compliance failure.**

Examples:

```text
Gemini unavailable
      ↓
PROCESSING_FAILED

Not:
POTENTIAL_NON_COMPLIANCE
```

```text
Database unavailable
      ↓
STORAGE_ERROR

Not:
NON-COMPLIANCE
```

```text
Unreadable image
      ↓
UNREADABLE / INCOMPLETE

Not automatically:
POTENTIAL_NON_COMPLIANCE
```

---

# 4. Error Scope Model

The target system has several failure layers:

```text
Client
  ↓
API
  ↓
Authentication / Authorization
  ↓
Evidence
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
Compliance Rules
  ↓
Persistence
  ↓
Reporting
```

A failure must be classified at the appropriate layer.

---

# 5. MVP Error Scope

The one-day MVP must safely handle at least:

```text
Invalid input
Evidence upload failure
Invalid image
Image processing failure
OCR failure
AI/provider failure
Malformed AI output
Validation failure
Applicability uncertainty
Rule evaluation failure
Persistence failure
Invalid lifecycle transition
Authorization failure
Correction/recalculation failure
```

Reviewer/finalization-specific errors apply if those capabilities are implemented.

---

# 6. Error Taxonomy

The technical error taxonomy is:

```text
VALIDATION_ERROR
AUTHENTICATION_ERROR
AUTHORIZATION_ERROR
NOT_FOUND
CONFLICT
INVALID_STATE
EVIDENCE_ERROR
IMAGE_PROCESSING_ERROR
OCR_ERROR
AI_ERROR
PROCESSING_FAILED
APPLICABILITY_ERROR
RULE_EVALUATION_ERROR
STORAGE_ERROR
REPORT_ERROR
INTERNAL_ERROR
```

These are technical/application errors.

They are separate from compliance result vocabulary.

---

# 7. Compliance Result Vocabulary

The domain result vocabulary remains:

```text
PASS
POTENTIAL_NON_COMPLIANCE
REQUIRES_REVIEW
NOT_APPLICABLE
INCOMPLETE
PROCESSING_FAILED
```

The UI/API must not collapse technical errors and domain outcomes into one generic status.

---

# 8. Error vs Domain Result

Example:

```text
Technical Error:
AI_ERROR

Domain consequence:
PROCESSING_FAILED
```

Example:

```text
Technical Error:
OCR_ERROR

Domain consequence:
INCOMPLETE or PROCESSING_FAILED
depending on whether useful processing can continue
```

Example:

```text
Domain observation:
CONFLICTING

Domain consequence:
REQUIRES_REVIEW
```

The exact mapping must preserve the distinction between cause and resulting state.

---

# 9. Error Object Requirements

A structured API error should contain, where appropriate:

```text
error code
human-readable message
request/correlation ID
field/resource reference
retryability
next action
```

Example:

```json
{
  "code": "AI_ERROR",
  "message": "Declaration analysis could not be completed.",
  "request_id": "REQ-7F42",
  "retryable": true
}
```

The exact API schema is defined in `08_API_Specification.md`.

---

# 10. User-Facing Error Principles

User-facing messages should:

1. explain what happened
2. avoid unnecessary technical detail
3. state whether the issue affects compliance assessment
4. provide a recovery action where possible

Example:

> “The analysis service could not complete. No compliance conclusion was generated from this failed step.”

---

# 11. No False Compliance

The system must never produce:

```text
PROCESSING FAILURE
      ↓
POTENTIAL NON-COMPLIANCE
```

unless a separate valid compliance assessment independently establishes the result.

---

# 12. No Silent Recovery

Automatic recovery must not silently change material inspection meaning.

Examples:

```text
AI retry
```

is acceptable.

But:

```text
AI conflict
→ silently choose value
```

is not acceptable.

---

# 13. Error Correlation

Requests and processing operations should have correlation identifiers where practical.

Example:

```text
Request ID: REQ-7F42
Processing ID: JOB-00214
OCR Run: OCR-00112
AI Run: AI-00087
Inspection: INS-00124
```

This allows failures to be traced across the processing pipeline.

---

# 14. Error Logging

Logs should capture enough information to diagnose failures.

Useful fields:

- timestamp
- severity
- error code
- request/correlation ID
- inspection ID where appropriate
- processing/job ID
- component
- operation
- retry count
- safe diagnostic detail

Logs must not expose:

- API keys
- passwords
- authentication tokens
- unnecessary private evidence
- storage secrets

---

# 15. Error Severity

Suggested severity levels:

```text
INFO
WARNING
ERROR
CRITICAL
```

Examples:

```text
INFO
Successful OCR run

WARNING
Low OCR confidence

ERROR
AI provider failure

CRITICAL
Persistent database unavailable
```

Severity is operational metadata, not a compliance result.

---

# 16. Validation Errors

Validation errors occur when input violates an expected contract.

Examples:

- missing required field
- invalid enum
- malformed identifier
- unsupported value
- invalid request body

Result:

```text
VALIDATION_ERROR
```

The request should not mutate domain state.

---

# 17. Authentication Errors

If a user cannot be authenticated:

```text
AUTHENTICATION_ERROR
```

Do not reveal unnecessary details about whether a specific account exists.

---

# 18. Authorization Errors

If the authenticated user lacks permission:

```text
AUTHORIZATION_ERROR
```

Examples:

```text
Inspector attempts finalization
Reviewer-only operation
        ↓
AUTHORIZATION_ERROR
```

or:

```text
User requests another inspection's evidence
        ↓
AUTHORIZATION_ERROR / NOT_FOUND
```

depending on the security design.

---

# 19. Not Found Errors

If a requested resource does not exist or is not visible:

```text
NOT_FOUND
```

The API should avoid leaking protected resource existence where inappropriate.

---

# 20. Conflict Errors

A conflict occurs when the requested operation conflicts with current state/version.

Examples:

```text
Inspection already finalized
        ↓
CONFLICT / INVALID_STATE
```

```text
Stale update
        ↓
CONFLICT
```

The client should refresh/reload current state rather than blindly retrying the mutation.

---

# 21. Invalid State Errors

An operation is invalid for the current lifecycle state.

Example:

```text
FINALIZED
   ↓
Inspector tries to edit
   ↓
INVALID_STATE
```

Lifecycle rules are authoritative in:

> `07_State_Machine.md`

---

# 22. Evidence Errors

Evidence errors include:

- unsupported file
- invalid MIME type
- oversized file
- corrupted image
- failed decode
- unauthorized evidence access
- storage failure during evidence persistence

These must be distinguished from compliance results.

---

# 23. Evidence Upload Failure

Flow:

```text
Upload
  ↓
Validation
  ├── Fail → EVIDENCE_ERROR
  │
  └── Pass
        ↓
     Storage
        ├── Fail → STORAGE_ERROR
        └── Success
```

A failed upload must not create a phantom evidence item.

---

# 24. Original Evidence Preservation on Failure

If storage fails before successful persistence:

```text
Evidence accepted?
NO
```

The system must not claim that the original evidence was securely stored when it was not.

If evidence was persisted successfully and later processing fails:

```text
Evidence
   ↓
Remains available
   ↓
Processing can retry
```

---

# 25. Image Processing Errors

Examples:

- unsupported image
- decoder failure
- memory/resource limitation
- preprocessing exception
- invalid image dimensions

Result:

```text
IMAGE_PROCESSING_ERROR
```

The original evidence must remain preserved.

---

# 26. Image Processing Recovery

Where possible:

```text
Image Processing Failure
        ↓
Retry
        OR
Use alternate safe preprocessing
        OR
Human action / supplemental evidence
```

Do not modify the original evidence to recover.

---

# 27. OCR Errors

OCR errors include:

- OCR engine unavailable
- OCR process crash
- invalid input
- OCR timeout
- no usable text

The system should distinguish:

```text
OCR technical failure
```

from:

```text
No readable declaration established
```

---

# 28. OCR Technical Failure

If PaddleOCR cannot execute:

```text
OCR_ERROR
      ↓
PROCESSING_FAILED
```

No compliance conclusion should be inferred from the failure.

---

# 29. No Readable Text

If OCR executes successfully but cannot establish useful text:

```text
OCR completed
      ↓
No usable text
      ↓
NOT_OBSERVED / UNREADABLE
```

The exact domain consequence depends on evidence/context.

This is not automatically a technical failure.

---

# 30. Low OCR Confidence

Low OCR confidence should be preserved.

Example:

```text
OCR:
"MRP ₹1?9"
Confidence:
Low
```

Downstream interpretation should preserve uncertainty.

Do not silently normalize to:

```text
₹199
```

unless valid evidence supports it.

---

# 31. AI Errors

AI errors include:

- provider unavailable
- timeout
- rate limit
- authentication/configuration failure
- malformed output
- schema mismatch
- unexpected provider response

These should be classified as:

```text
AI_ERROR
```

with an appropriate domain processing state.

---

# 32. AI Provider Failure

Example:

```text
Gemini request
      ↓
Provider unavailable
      ↓
AI_ERROR
      ↓
PROCESSING_FAILED
```

The system should offer retry when the failure is transient.

---

# 33. AI Retry

Retry only where appropriate.

Good retry candidates:

- transient network error
- provider timeout
- temporary service unavailability
- rate limiting where retry-after semantics permit

Do not endlessly retry:

- malformed request
- unsupported schema
- invalid local configuration
- deterministic validation failure

---

# 34. Controlled Retry

A retry should preserve:

- original AI run
- failure
- retry attempt
- new AI run
- final outcome

Example:

```text
AI-00087
FAILED

Retry
↓
AI-00088
SUCCESS
```

The first failure remains auditable.

---

# 35. Malformed AI Output

If the provider returns malformed output:

```text
AI Output
   ↓
Schema Validation
   ↓
FAIL
   ↓
Controlled Retry
```

If the retry also fails:

```text
PROCESSING_FAILED
```

The malformed output must not be accepted as domain data.

---

# 36. AI Hallucination Prevention

The system should reject/flag output that:

- lacks source evidence
- invents unsupported values
- violates the expected schema
- contradicts preserved observations without explanation
- provides unsupported legal conclusions

AI output must be treated as untrusted input.

---

# 37. AI Source Requirement

No declaration should be accepted as an AI-established fact without appropriate source evidence.

Conceptually:

```text
AI Value
  +
Source OCR / Evidence
  ↓
Eligible for validation

AI Value
  +
No source
  ↓
Reject / UNCERTAIN
```

---

# 38. Validation of AI Output

AI output should pass:

```text
Schema Validation
      ↓
Type Validation
      ↓
Domain Validation
      ↓
Source/Provenance Validation
      ↓
Accepted Observation
```

Failure at any stage prevents invalid data from becoming trusted domain state.

---

# 39. Conflict Errors

A conflict is not necessarily a technical error.

Example:

```text
MRP
₹199
₹179
```

Domain result:

```text
CONFLICTING
```

Potential assessment:

```text
REQUIRES_REVIEW
```

The system must preserve both observations.

---

# 40. Applicability Errors

Applicability may fail because:

- required context is missing
- import status is unknown
- supported condition cannot be evaluated
- configuration/rule data is unavailable

The system should distinguish:

```text
Unknown applicability
```

from:

```text
Applicability engine technical failure
```

---

# 41. Applicability Uncertainty

Example:

```text
Import Status
UNKNOWN

Country of Origin
Applicability
REQUIRES REVIEW / INCOMPLETE
```

Do not assume:

```text
UNKNOWN → NOT_APPLICABLE
```

or:

```text
UNKNOWN → NON_COMPLIANCE
```

---

# 42. Rule Evaluation Errors

A rule evaluation error is a technical/domain execution problem such as:

- invalid rule configuration
- missing required rule parameter
- unexpected evaluator exception
- inconsistent rule data

Result:

```text
RULE_EVALUATION_ERROR
```

The system must not fabricate a PASS or non-compliance result.

---

# 43. Rule Failure Recovery

If rule evaluation fails:

```text
Rule Evaluation
      ↓
Failure
      ↓
REQUIRES_REVIEW / PROCESSING_FAILED
```

depending on the failure semantics.

The exact mapping must be defined by the rule/state implementation.

---

# 44. Persistence Errors

Persistence errors include:

- database unavailable
- transaction failure
- constraint violation
- object storage unavailable
- network/storage timeout

These are:

```text
STORAGE_ERROR
```

or a more specific persistence error.

---

# 45. Persistence Failure Safety

If a material operation cannot be persisted:

```text
Do not claim success
```

Example:

```text
Inspector correction
      ↓
Database failure
      ↓
Correction NOT confirmed
```

The UI should not display:

> Saved successfully

unless the backend confirms persistence.

---

# 46. Transaction Failure

If a transaction fails:

```text
Transaction
  ├── Change
  ├── Invalidation
  └── Audit
       ↓
Failure
       ↓
Rollback / safe recovery
```

The system must not leave known inconsistent partial state.

---

# 47. Correction Failure

A correction should not be considered complete until:

```text
New value
+
Affected invalidation/recalculation
+
Required audit
```

are persisted according to the implementation's transaction boundary.

If recomputation fails:

```text
Correction cannot be represented as fully current
```

The system should surface the condition and prevent stale output from being treated as final.

---

# 48. Stale Data Protection

A key invariant:

> **Upstream correction → invalidate affected downstream state → recompute → preserve prior state/history → audit transition.**

If recomputation fails:

```text
Affected result
      ↓
STALE / INVALIDATED
      ↓
Do not present as current final assessment
```

---

# 49. Submission Errors

If submission fails:

```text
SUBMIT request
      ↓
Validation
      ↓
State/permission checks
      ↓
Persistence
```

If any required operation fails:

```text
Submission not completed
```

The Inspector must receive a clear recovery path.

---

# 50. Submission Retry

A failed submission may be retried after resolving the underlying problem.

The system must prevent duplicate submission events.

---

# 51. Reviewer Errors

Where Reviewer workflow exists, errors may include:

- unauthorized review
- stale inspection
- invalid decision
- missing override reason
- evidence request conflict
- finalization precondition failure

These must not silently change inspection state.

---

# 52. Override Validation

If a Reviewer overrides an assessment:

```text
Reviewer authorized?
      ↓
Yes
      ↓
Reason provided?
      ↓
Yes
      ↓
Persist decision
```

Missing reason:

```text
VALIDATION_ERROR
```

---

# 53. Evidence Request Errors

An Evidence Request must not be created if:

- Reviewer is unauthorized
- inspection is not reviewable
- request data is invalid
- inspection is finalized

The operation must fail without corrupting inspection state.

---

# 54. Finalization Errors

Finalization is high impact.

Before finalization validate:

- Reviewer authorization
- lifecycle state
- required review actions
- blocking unresolved conditions
- rule snapshot
- evidence references
- decision
- reason where required
- snapshot integrity

If validation fails:

```text
FINALIZATION FAILED
```

The inspection remains non-finalized.

---

# 55. Atomic Finalization Failure

The system should ensure:

```text
Final Decision
+
Final Snapshot
+
Finalization State
+
Audit
```

are committed consistently.

If the transaction fails:

```text
Inspection ≠ FINALIZED
```

unless the implementation can prove the finalization transaction completed.

---

# 56. Finalized Mutation Error

Attempt:

```text
FINALIZED
   ↓
Edit
```

must produce:

```text
INVALID_STATE
```

or equivalent conflict.

The historical record remains unchanged.

---

# 57. Report Errors

Report errors include:

- generation failure
- rendering failure
- storage failure
- template failure
- export failure

Result:

```text
REPORT_ERROR
```

---

# 58. Report Failure Isolation

Critical invariant:

```text
Finalization
      ↓
SUCCESS

Report
      ↓
FAILURE
```

must result in:

```text
Inspection = FINALIZED
Report = RETRYABLE ERROR
```

Report failure must not roll back finalization.

---

# 59. Network Errors

Transient network failures should be handled differently from deterministic errors.

```text
Network timeout
      ↓
Retry candidate

Invalid request
      ↓
No blind retry
```

The UI should avoid duplicate actions caused by impatient repeated clicks.

---

# 60. Timeout Handling

Long-running operations should have controlled timeouts.

Possible operations:

- upload
- OCR
- AI
- storage
- report generation

Timeout should produce an explicit failure state rather than indefinite waiting.

---

# 61. Duplicate Requests

The system should protect material operations from accidental duplicate requests.

Examples:

```text
Double-click Submit
```

must not create:

```text
Two submissions
```

Likewise, duplicate processing initiation should be controlled.

---

# 62. Idempotency

Where appropriate, use idempotency or equivalent deduplication for:

- processing initiation
- evidence operations
- submission
- finalization
- report generation

The exact API contract is defined in `08_API_Specification.md`.

---

# 63. Concurrent Mutation

If two actors attempt conflicting mutations:

```text
Inspector update
+
Reviewer action
```

the backend must detect invalid/stale state.

Possible response:

```text
CONFLICT
```

The user should refresh current state before retrying.

---

# 64. Lifecycle Error Handling

All lifecycle transitions must be validated server-side.

Example:

```text
DRAFT
 ↓
FINALIZE
```

must be rejected.

The UI may prevent the action, but backend validation is mandatory.

---

# 65. Error Handling Across the Pipeline

Full processing:

```text
Evidence
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
Rules
   ↓
Findings
```

If a stage fails:

```text
Stop dependent processing
      ↓
Record failure
      ↓
Preserve prior valid artifacts
      ↓
Expose recovery path
```

Do not continue with fabricated inputs.

---

# 66. Partial Success

The system may preserve valid prior artifacts.

Example:

```text
Evidence ✓
Image Processing ✓
OCR ✓
AI ✗
```

Then:

```text
Evidence remains valid
OCR remains available
AI-dependent results are unavailable
Inspection is not marked compliant/non-compliant solely from AI failure
```

---

# 67. Dependency Invalidation

If an upstream artifact becomes invalid:

```text
Upstream Failure
      ↓
Identify dependents
      ↓
Invalidate affected outputs
      ↓
Preserve historical attempts
      ↓
Reprocess
```

Example:

```text
Corrected Declaration
      ↓
Affected Assessment invalidated
      ↓
Finding recalculated
```

---

# 68. Error Recovery Matrix

| Error | Safe Result | Retry | Human Action |
|---|---|---:|---:|
| Invalid input | Validation error | No | Correct input |
| Invalid image | Evidence/image error | Usually no | Upload valid image |
| Storage outage | Storage error | Yes | Retry |
| OCR timeout | Processing failure | Yes | Retry |
| No readable text | Unreadable / incomplete | Sometimes | Review/add evidence |
| AI timeout | Processing failure | Yes | Retry |
| AI malformed output | Processing failure after controlled retry | Yes | Review if persistent |
| AI conflict | Requires Review | No blind retry | Verify |
| Applicability unknown | Review/incomplete | Sometimes | Establish context |
| Rule execution error | Review/processing error | Controlled | Engineering/admin action |
| DB failure | Storage error | Yes | Retry |
| Invalid state | Invalid State | No blind retry | Refresh/current workflow |
| Unauthorized action | Authorization error | No | Use permitted role |
| Finalization failure | Not finalized | Controlled | Resolve blocker |
| Report failure | Report error | Yes | Retry report |

---

# 69. Error Recovery Priority

When several failures occur, prioritize:

```text
1. Data integrity
2. Evidence preservation
3. State consistency
4. Security
5. Recoverability
6. User convenience
```

Never sacrifice integrity for a smoother UI.

---

# 70. Error Recovery and Human Workflow

When automation cannot establish a fact:

```text
Automation Failure / Uncertainty
          ↓
Human Verification
```

The system may route the user to:

- inspect evidence
- correct extraction
- add manual observation
- add supplemental evidence
- request review
- retry processing

---

# 71. Inspector Recovery

The Inspector may recover from:

```text
OCR uncertainty
AI extraction error
Insufficient evidence
Incorrect extraction
```

through:

```text
Review
Correct
Supplement
Retry
Verify
```

---

# 72. Reviewer Recovery

The Reviewer may recover from unresolved inspection conditions by:

```text
Request Evidence
      ↓
Inspector Response
      ↓
Reprocess if required
      ↓
Review Again
```

or:

```text
Record decision based on available evidence
```

according to the supported workflow.

---

# 73. Unable to Establish

The system should support the outcome:

> Unable to Establish

where evidence is insufficient.

This may lead to:

```text
INCOMPLETE
```

or:

```text
REQUIRES_REVIEW
```

depending on lifecycle/rule semantics.

It must not force a fabricated PASS or non-compliance result.

---

# 74. UI Error Communication

The UI should communicate:

```text
What happened?
Why does it matter?
What can I do?
```

Example:

```text
PROCESSING FAILED

Declaration analysis could not be completed.

This is a technical processing failure and does not
indicate product non-compliance.

[Retry Analysis]
```

---

# 75. Error Messaging Anti-Patterns

Avoid:

```text
Something went wrong.
```

without recovery information.

Avoid:

```text
AI says invalid.
```

Avoid:

```text
FAILED → NON-COMPLIANT
```

Avoid exposing:

```text
Stack traces
API keys
provider internals
database credentials
```

to normal users.

---

# 76. Technical Error vs User Error

Example:

```text
Unsupported image
→ User/input problem

Gemini unavailable
→ External technical problem

Database unavailable
→ Infrastructure problem

Reviewer lacks permission
→ Authorization problem
```

The UI should communicate the appropriate action.

---

# 77. Retry Policy

Retries should be:

- bounded
- intentional
- observable
- safe

Do not create infinite retry loops.

Example:

```text
Attempt 1
   ↓
Attempt 2
   ↓
Attempt 3
   ↓
PROCESSING_FAILED
```

The exact retry count may be implementation-specific.

---

# 78. Backoff

Transient external failures may use increasing delay.

Conceptually:

```text
Retry 1 → short delay
Retry 2 → longer delay
Retry 3 → longer delay
```

The exact strategy is implementation-defined.

---

# 79. External Provider Failure Isolation

Gemini/PaddleOCR/storage failures should not corrupt unrelated inspection data.

For example:

```text
AI Provider Down
```

must not affect:

- existing finalized records
- unrelated inspections
- original evidence
- rule definitions

---

# 80. Error Boundaries

Each major component should have an error boundary:

```text
Frontend
Backend
Evidence
Image Processing
OCR
AI
Rules
Persistence
Reporting
```

An error should be contained as close as practical to its source.

---

# 81. Error Boundary Example

```text
Gemini Failure
      ↓
AI Integration Boundary
      ↓
AI_ERROR
      ↓
Processing State
```

Do not allow an exception to propagate into an unexplained global application failure.

---

# 82. Data Preservation During Errors

When an error occurs:

```text
Preserve:
Original Evidence
Successful OCR
Previous Valid Declarations
Prior Audit Events
Previous Assessment History
```

Do not delete valid historical artifacts merely because a later processing step failed.

---

# 83. Error and Audit Relationship

Material failures should be auditable.

Examples:

```text
Processing started
Processing failed
Retry started
Processing succeeded
Declaration corrected
Assessment recalculated
Finalization failed
```

The audit trail should allow reconstruction of what happened.

---

# 84. Error and Provenance Relationship

Each processing attempt should be distinguishable.

Example:

```text
OCR Run 001 → FAILED
OCR Run 002 → SUCCESS

AI Run 001 → FAILED
AI Run 002 → SUCCESS
```

The successful result must not erase evidence that earlier attempts failed.

---

# 85. Error and Historical Integrity

Finalized history must not be changed because a later technical failure occurs.

Example:

```text
Finalized Inspection
      ↓
Later report generation failure
      ↓
Historical inspection remains FINALIZED
```

---

# 86. Security Error Handling

Security failures must fail closed where appropriate.

Examples:

```text
Missing authorization
      ↓
Reject

Invalid evidence access
      ↓
Reject

Invalid finalization request
      ↓
Reject
```

Do not grant fallback permissions to “make the workflow work.”

---

# 87. File Security Errors

Reject files that:

- exceed size limits
- have unsupported types
- cannot be decoded
- violate storage rules
- attempt unsafe paths/names

Do not trust client-provided filenames or MIME declarations alone.

---

# 88. Secret/Configuration Errors

If required secrets/configuration are missing:

```text
Service startup/configuration error
```

The system should fail clearly rather than making requests with invalid credentials.

Secrets must never appear in error messages.

---

# 89. Database Configuration Errors

If the database cannot initialize:

```text
Application unavailable / controlled startup failure
```

Do not silently fall back to an unintended local database in a deployed environment.

---

# 90. Storage Configuration Errors

If production object storage is unavailable:

```text
Evidence operations fail safely
```

Do not silently fall back to local filesystem storage as the deployed source of truth.

---

# 91. Deployment Error Handling

Deployment should verify:

```text
Frontend reachable
Backend reachable
Database reachable
Object storage reachable
AI configuration valid
OCR available
```

A deployment smoke test should catch missing dependencies before demonstration.

---

# 92. Monitoring Requirements

The deployed system should monitor:

- application errors
- processing failures
- OCR failures
- AI failures
- storage failures
- database failures
- authorization failures
- report failures

The exact monitoring platform is not locked.

---

# 93. User Feedback Timing

The UI should acknowledge actions promptly.

Example:

```text
Upload
  ↓
Uploading...
  ↓
Uploaded
  ↓
Processing...
```

Avoid making the user unsure whether an action was received.

---

# 94. Preventing Double Actions

Disable or otherwise guard high-impact actions while pending.

Examples:

```text
[Submitting...]
```

instead of allowing repeated submission.

Likewise:

```text
[Finalizing...]
```

should prevent duplicate finalization attempts.

---

# 95. Offline/Disconnected Conditions

If the browser loses connectivity:

```text
Connection lost
```

The UI should not falsely claim that changes were saved.

For critical actions:

```text
Action not confirmed by server.
```

The user should be able to retry safely.

---

# 96. Error State Recovery Navigation

An error screen should return the user to the last valid workflow point where possible.

Example:

```text
AI Failed
 ↓
Back to Analysis
 ↓
Retry
```

Do not force users to restart an entire inspection unnecessarily.

---

# 97. Recovery Without Data Loss

Recovery must preserve:

```text
Inspection ID
Evidence
Successful OCR
Prior corrections
Audit history
```

unless a specific operation intentionally creates a new version/artifact.

---

# 98. Target Error State Model

Processing state may use:

```text
QUEUED
PROCESSING
COMPLETED
FAILED
RETRYING
```

Domain inspection state may use:

```text
DRAFT
EVIDENCE_READY
PROCESSING
ANALYSIS_READY
VERIFICATION
SUBMITTED
REVIEW
FINALIZED
```

The two state systems must not be conflated.

---

# 99. Error Handling and State Machine

Error handling must respect lifecycle rules.

Example:

```text
PROCESSING
    ↓
AI Failure
    ↓
PROCESSING_FAILED
    ↓
Retry
    ↓
PROCESSING
```

A failed processing attempt does not automatically terminate the inspection permanently.

Exact transitions are authoritative in `07_State_Machine.md`.

---

# 100. MVP Error-Handling Definition of Done

The one-day MVP is error-ready when:

```text
[ ] Invalid input is rejected
[ ] Invalid evidence is rejected
[ ] Original evidence is preserved
[ ] OCR failure is explicit
[ ] AI failure is explicit
[ ] Malformed AI output is rejected
[ ] Uncertainty is preserved
[ ] Conflicts are preserved
[ ] Applicability uncertainty is represented
[ ] Rule failure is not converted to non-compliance
[ ] Persistence failure is visible
[ ] Invalid lifecycle transitions are rejected
[ ] Unauthorized actions are rejected
[ ] Corrections do not leave known stale results
[ ] Report failure cannot undo finalization
[ ] Finalized records cannot be normally mutated
[ ] Recovery actions are clear
[ ] Errors are auditable where material
[ ] Deployment smoke test validates dependencies
```

---

# 101. Error-Handling Anti-Patterns

Do not implement:

## Error as Compliance

```text
API failure → NON-COMPLIANCE
```

## Silent Fallback

```text
Cloud storage fails → silently use local filesystem
```

## Silent AI Guess

```text
Ambiguous OCR → invented value
```

## Infinite Retry

```text
while failure:
    retry forever
```

## Error Suppression

```text
catch Exception:
    return PASS
```

## Partial Finalization

```text
Decision saved
Snapshot failed
State says FINALIZED
```

## UI-Only Recovery

Showing “retry” while backend state is inconsistent.

---

# 102. Error Handling Priority for the Coding Agent

When implementing error behavior, the agent should prioritize:

```text
1. Preserve original evidence
2. Preserve valid persisted data
3. Maintain state consistency
4. Prevent false compliance conclusions
5. Preserve audit/provenance
6. Provide recovery
7. Improve user messaging
```

---

# 103. Relationship to Other Documents

| Document | Relationship |
|---|---|
| `01_PRD.md` | Product-level error expectations |
| `02_TRD.md` | Technical failure constraints |
| `03_Architecture.md` | Component/error boundaries |
| `04_Design.md` | Error presentation |
| `05_Domain_Specification.md` | Domain state/result semantics |
| `06_Compliance_Rules.md` | Rule evaluation behavior |
| `07_State_Machine.md` | Lifecycle transitions |
| `08_API_Specification.md` | Error/API contracts |
| `09_Database_Specification.md` | Persistence failure/integrity |
| `10_Error_Handling.md` | Error/recovery authority |
| `11_Testing_and_Release_Gate.md` | Error validation |

---

# 104. Final Error-Handling Principle

ComplianceScan must fail safely.

The most important distinctions are:

```text
Technical Failure
      ≠
Compliance Result

Uncertainty
      ≠
Non-Compliance

Unreadable
      ≠
Missing

Insufficient Evidence
      ≠
Proven Violation

Hash Integrity
      ≠
Truth / Authenticity
```

The recovery chain is:

```text
Detect
  ↓
Classify
  ↓
Preserve
  ↓
Contain
  ↓
Retry / Correct / Supplement
  ↓
Reprocess
  ↓
Verify
  ↓
Audit
```

The governing principle is:

> **Never manufacture certainty from failure.**

And the system-wide safety rule remains:

> **AI finds → Evidence supports → Backend validates → Inspector verifies → Reviewer decides.**
