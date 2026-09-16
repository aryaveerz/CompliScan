# 07 — STATE MACHINE

**Project:** ComplianceScan  
**SIH'26 Problem Statement:** 26034  
**Document Version:** 2.0  
**Status:** Target lifecycle specification with controlled one-day MVP subset

---

# 1. Purpose

This document defines the lifecycle and state-transition model for ComplianceScan.

It establishes:

- inspection lifecycle states
- evidence-processing states
- review ownership
- transition rules
- correction behavior
- evidence-request behavior
- finalization behavior
- failure states
- invalidation/recomputation semantics
- target-system lifecycle vs current MVP lifecycle

The state machine is intentionally broader than the one-day MVP.

The target system remains the long-term lifecycle model.

The current MVP implements only the states and transitions required for one complete vertical slice.

---

# 2. Scope Model

ComplianceScan has two lifecycle scopes:

```text
TARGET LIFECYCLE
      │
      │ controlled subset
      ▼
CURRENT ONE-DAY MVP
```

The target lifecycle supports the broader inspection/review/finalization architecture.

The current MVP must not attempt to implement every target state merely because the state exists in this document.

Current implementation scope is controlled by:

> `MVP_BUILD_SCOPE.md`

Actual implementation status is controlled by:

> `PROJECT_STATE.md`

Execution order is controlled by:

> `PHASE.md`

Engineering-agent behavior is controlled by:

> `AGENT_ENGINEERING_PROTOCOL.md`

---

# 3. Core Lifecycle Principle

The operational contract is:

> **The Inspector prepares and verifies. The System analyzes and records. The Reviewer independently decides and finalizes.**

The lifecycle must preserve this separation.

```text
Inspector
   │
   │ prepares / observes / verifies
   ▼
System
   │
   │ analyzes / validates / records
   ▼
Inspector
   │
   │ verifies / corrects
   ▼
Reviewer
   │
   │ independently reviews / decides
   ▼
Finalized Record
```

AI does not own the lifecycle.

AI does not finalize inspections.

---

# 4. Core Lifecycle

The target lifecycle is conceptually:

```text
                    ┌────────────────────┐
                    │ INSPECTION CREATED │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ CONTEXT PROVIDED   │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ EVIDENCE CAPTURED  │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ EVIDENCE VERIFIED  │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ QUALITY CHECK      │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ AI PROCESSING      │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ DECLARATIONS       │
                    │ UNDERSTOOD         │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ APPLICABILITY      │
                    │ DETERMINED         │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ COMPLIANCE         │
                    │ ASSESSED           │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ EVIDENCE / FINDING │
                    │ SUFFICIENCY        │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ INSPECTOR          │
                    │ VERIFICATION       │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ SUBMITTED          │
                    └─────────┬──────────┘
                              │
                       Reviewer receives
                              │
                              ▼
                    ┌────────────────────┐
                    │ UNDER REVIEW       │
                    └─────────┬──────────┘
                              │
                    ┌─────────┴──────────┐
                    │                    │
                    ▼                    ▼
             Evidence Request       Decision
                    │                    │
                    ▼                    ▼
             Inspector Action      FINALIZATION
                    │                    │
                    └───────┐            │
                            │            ▼
                            │      ┌────────────┐
                            │      │ FINALIZED  │
                            │      └────────────┘
                            │
                            └──→ RESUBMIT
```

---

# 5. Current One-Day MVP Lifecycle

The current MVP should implement a smaller path:

```text
DRAFT / INSPECTION CREATED
          ↓
EVIDENCE PROVIDED
          ↓
IMAGE PROCESSING
          ↓
OCR COMPLETED
          ↓
DECLARATION EXTRACTION
          ↓
APPLICABILITY
          ↓
COMPLIANCE ASSESSMENT
          ↓
FINDINGS + EVIDENCE
          ↓
INSPECTOR VERIFICATION
          ↓
MVP RESULT
          ↓
BASIC OUTPUT / PERSISTENCE
```

Where review/finalization infrastructure is included in the current implementation, it must respect the target ownership model rather than inventing a separate lifecycle.

The MVP does not need to implement every target lifecycle branch.

---

# 6. State Categories

The lifecycle can be understood through five categories.

## 6.1 Preparation States

```text
DRAFT
CONTEXT_READY
EVIDENCE_PROVIDED
```

## 6.2 Processing States

```text
IMAGE_PROCESSING
OCR_PROCESSING
DECLARATION_EXTRACTION
APPLICABILITY_EVALUATION
COMPLIANCE_EVALUATION
FINDING_GENERATION
```

## 6.3 Verification States

```text
EVIDENCE_REVIEW
INSPECTOR_VERIFICATION
INCOMPLETE
REQUIRES_REVIEW
```

## 6.4 Review States

```text
SUBMITTED
UNDER_REVIEW
EVIDENCE_REQUESTED
REVIEW_DECISION
```

## 6.5 Terminal / Historical States

```text
FINALIZED
PROCESSING_FAILED
```

The exact persistence representation may differ from the conceptual state names, but lifecycle semantics must remain consistent.

---

# 7. State Definitions

## 7.1 DRAFT

Inspection exists but required initial information is not complete.

Owner:

> Inspector

Allowed actions:

- add context
- add product information
- provide evidence
- save changes

Cannot:

- finalize
- perform final review
- alter rules

---

## 7.2 CONTEXT_READY

Required inspection/product context has been supplied sufficiently to begin evidence processing.

Owner:

> Inspector

Next expected action:

> Evidence input/capture

---

## 7.3 EVIDENCE_PROVIDED

At least one valid evidence item has been accepted.

The evidence should have:

- Evidence ID
- source metadata
- inspection association
- integrity information
- provenance

Evidence is immutable once accepted as original evidence.

---

## 7.4 IMAGE_PROCESSING

The system is preparing analysis copies of the evidence.

Possible operations:

- orientation handling
- resizing
- preprocessing
- quality analysis
- normalization

The original evidence must not be modified.

---

## 7.5 OCR_PROCESSING

PaddleOCR is processing the analysis image.

Expected outputs:

- recognized text
- bounding boxes
- OCR confidence
- source evidence association

---

## 7.6 DECLARATION_EXTRACTION

Gemini 2.5 Flash interprets OCR-derived observations.

Expected outputs include:

- declaration values
- normalized values where applicable
- observation status
- extraction confidence
- source OCR regions
- source evidence references

AI uncertainty must be preserved.

---

## 7.7 APPLICABILITY_EVALUATION

The system determines which supported requirements apply.

This state must precede final compliance evaluation.

Conceptually:

```text
Context
   ↓
Applicability
   ↓
Applicable Requirements
```

A non-applicable requirement becomes:

> `NOT_APPLICABLE`

It must not be treated as a failure.

---

## 7.8 COMPLIANCE_EVALUATION

The deterministic compliance engine evaluates structured observations against the controlled rule set.

Current MVP scope:

1. Manufacturer / Packer / Importer
2. Common / Generic Product Name
3. Net Quantity + Standard Unit
4. Month / Year of Manufacture / Packing / Import
5. MRP inclusive of all taxes
6. Consumer Care Details

Country of Origin is evaluated according to supported applicability.

The compliance engine does not invent legal rules.

---

## 7.9 FINDING_GENERATION

The system converts relevant assessments into explainable findings.

A finding should retain:

- requirement
- assessment
- rule reference
- reason
- supporting evidence
- OCR/source region where applicable
- confidence/uncertainty
- provenance

A finding should not exist as an unexplained red/green label.

---

## 7.10 EVIDENCE_REVIEW

The system determines whether available evidence is sufficient for the relevant assessment.

Possible outcomes include:

```text
SUFFICIENT
INSUFFICIENT
UNCERTAIN
CONFLICTING
```

Evidence insufficiency does not automatically mean non-compliance.

---

## 7.11 INSPECTOR_VERIFICATION

The Inspector reviews system observations.

The Inspector may:

- confirm observed information
- correct extracted information
- add manual observations
- add supplemental evidence
- verify applicability
- verify assessment
- leave unresolved information appropriately marked

The Inspector cannot finalize.

---

## 7.12 INCOMPLETE

The inspection cannot establish a required fact or assessment with available information/evidence.

Examples:

- required area not visible
- image insufficient
- necessary context unavailable
- evidence does not establish the fact

`INCOMPLETE` is not a synonym for non-compliance.

---

## 7.13 REQUIRES_REVIEW

The inspection contains ambiguity, conflict, or a condition requiring human review.

Examples:

- conflicting MRP values
- ambiguous declaration interpretation
- inconsistent observations
- unresolved evidence issue

The system must preserve the underlying observations.

---

## 7.14 SUBMITTED

The Inspector has submitted the inspection for independent review.

Submission creates a lifecycle ownership boundary:

```text
Before submission
    → Inspector controls working record

After submission
    → Reviewer controls review
```

---

## 7.15 UNDER_REVIEW

The Reviewer is independently reviewing the submitted inspection.

The Reviewer can inspect:

- evidence
- OCR
- extracted declarations
- applicability
- findings
- corrections
- audit history

The Reviewer may confirm, correct/override, request evidence, or finalize.

---

## 7.16 EVIDENCE_REQUESTED

The Reviewer has determined that additional evidence or clarification is required.

The request must identify:

- what needs to be established
- why it matters
- Evidence Request ID
- requested scope

Example:

```text
ER-00017
```

The request is not an automatic recapture command.

---

## 7.17 REVIEW_DECISION

The Reviewer has reached an assessment decision.

Possible outcomes include:

- confirmed
- corrected
- overridden
- additional evidence requested
- ready for finalization

Any correction/override should preserve:

- old value
- new value
- actor
- timestamp
- reason
- relevant evidence/provenance

---

## 7.18 FINALIZED

The Reviewer has finalized the inspection.

Finalization creates a protected historical snapshot.

The final snapshot should contain or reference:

- inspection
- product
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

---

## 7.19 PROCESSING_FAILED

A technical processing operation failed.

Examples:

- OCR service unavailable
- AI API unavailable
- malformed model output after controlled retry
- image-processing failure
- unsupported/corrupt input

This state is never equivalent to:

> `POTENTIAL_NON_COMPLIANCE`

---

# 8. Controlled Result Vocabulary

Lifecycle state and compliance result are separate concepts.

The compliance result vocabulary is:

```text
PASS
POTENTIAL_NON_COMPLIANCE
REQUIRES_REVIEW
NOT_APPLICABLE
INCOMPLETE
PROCESSING_FAILED
```

A lifecycle state such as `UNDER_REVIEW` does not itself imply a compliance result.

Likewise:

```text
POTENTIAL_NON_COMPLIANCE
```

does not mean the inspection is finalized.

---

# 9. State vs Result Separation

The system must not confuse:

```text
LIFECYCLE STATE
        with
COMPLIANCE RESULT
```

Example:

```text
UNDER_REVIEW
     +
POTENTIAL_NON_COMPLIANCE
```

is valid.

Likewise:

```text
INSPECTOR_VERIFICATION
     +
REQUIRES_REVIEW
```

is valid.

And:

```text
PROCESSING_FAILED
     +
No compliance conclusion
```

is required.

---

# 10. Transition Rules

Every state transition must satisfy:

1. Current state permits the transition.
2. Actor is authorized.
3. Required data exists.
4. Preconditions are satisfied.
5. Transition is recorded/audited where required.
6. Downstream state is invalidated if upstream data changes.
7. The resulting state is deterministic.

---

# 11. Core Transition Table

| From | Action | To | Actor |
|---|---|---|---|
| DRAFT | provide context | CONTEXT_READY | Inspector |
| CONTEXT_READY | add evidence | EVIDENCE_PROVIDED | Inspector |
| EVIDENCE_PROVIDED | process image | IMAGE_PROCESSING | System |
| IMAGE_PROCESSING | quality accepted | OCR_PROCESSING | System |
| IMAGE_PROCESSING | processing failure | PROCESSING_FAILED | System |
| OCR_PROCESSING | OCR complete | DECLARATION_EXTRACTION | System |
| OCR_PROCESSING | processing failure | PROCESSING_FAILED | System |
| DECLARATION_EXTRACTION | extraction complete | APPLICABILITY_EVALUATION | System |
| DECLARATION_EXTRACTION | malformed/fatal failure | PROCESSING_FAILED | System |
| APPLICABILITY_EVALUATION | applicability complete | COMPLIANCE_EVALUATION | System |
| COMPLIANCE_EVALUATION | evaluation complete | FINDING_GENERATION | System |
| FINDING_GENERATION | findings generated | EVIDENCE_REVIEW | System |
| EVIDENCE_REVIEW | evidence sufficient | INSPECTOR_VERIFICATION | System |
| EVIDENCE_REVIEW | evidence insufficient | INCOMPLETE | System / Inspector workflow |
| EVIDENCE_REVIEW | conflict/ambiguity | REQUIRES_REVIEW | System |
| INSPECTOR_VERIFICATION | verify | SUBMITTED / MVP RESULT | Inspector |
| INSPECTOR_VERIFICATION | correct data | affected processing state | Inspector/System |
| SUBMITTED | accept review | UNDER_REVIEW | System |
| UNDER_REVIEW | confirm/correct | REVIEW_DECISION | Reviewer |
| UNDER_REVIEW | request evidence | EVIDENCE_REQUESTED | Reviewer |
| EVIDENCE_REQUESTED | supplement evidence | INSPECTOR_VERIFICATION | Inspector |
| REVIEW_DECISION | finalize | FINALIZED | Reviewer/System |
| FINALIZED | normal edit | FORBIDDEN | Everyone |
```

The precise implementation may combine internal processing states for simplicity, provided the externally meaningful lifecycle semantics are preserved.

---

# 12. Correction Transition Model

Corrections are not simple field edits.

A material upstream correction must trigger:

```text
CORRECTION
    ↓
IDENTIFY AFFECTED DATA
    ↓
INVALIDATE AFFECTED DOWNSTREAM STATE
    ↓
RECOMPUTE
    ↓
GENERATE NEW RESULT
    ↓
PRESERVE OLD STATE
    ↓
AUDIT TRANSITION
```

This is a global project invariant.

---

# 13. Example: MRP Correction

Suppose the system extracts:

```text
MRP = ₹199
```

The Inspector observes that the package actually shows:

```text
MRP = ₹179
```

The correct transition is:

```text
Extracted MRP ₹199
       ↓
Inspector correction
       ↓
Old MRP retained in history
       ↓
Affected compliance result invalidated
       ↓
Compliance re-evaluated using ₹179
       ↓
New assessment
       ↓
Correction recorded
```

The system must not simply update the displayed number while retaining a stale assessment based on ₹199.

---

# 14. Evidence Addition Transition

If new evidence is added:

```text
New Evidence
     ↓
New Evidence ID
     ↓
Associate with Inspection
     ↓
Determine Affected Observations
     ↓
Invalidate Affected Downstream Results
     ↓
Reprocess if Required
     ↓
Inspector Verification
     ↓
Resubmit if applicable
```

Original evidence remains preserved.

---

# 15. Evidence Request Loop

The target workflow supports:

```text
Reviewer
    ↓
EVIDENCE_REQUESTED
    ↓
Inspector
    ↓
Supplemental Evidence / Manual Observation /
Unable to Establish
    ↓
Re-analysis if affected
    ↓
Inspector Verification
    ↓
SUBMITTED
    ↓
Reviewer
```

The Reviewer request must be specific enough to establish what fact or condition is missing.

---

# 16. Evidence Request Does Not Mean Automatic Recapture

The system must not assume:

```text
Evidence Request
      =
Automatic Camera Recapture
```

Instead:

```text
Evidence Request
      ↓
Inspector determines appropriate response
      ├── Manual observation
      ├── Supplemental evidence
      └── Unable to establish
```

This supports real inspection conditions.

---

# 17. Conflicting Data Transition

If conflicting values are detected:

```text
Multiple Observations
       ↓
CONFLICTING
       ↓
REQUIRES_REVIEW
```

The system must preserve the conflicting values and their sources.

It must not silently select one value merely because:

- it has higher model confidence
- it appears first
- it is more common
- it "looks right"

Human resolution is required when the conflict materially affects the assessment.

---

# 18. Unreadable Data Transition

Unreadable text must remain distinct from missing text.

```text
Visible Area
     ↓
Text Cannot Be Reliably Read
     ↓
UNREADABLE
```

Do not automatically convert:

```text
UNREADABLE
    →
NOT_OBSERVED
    →
POTENTIAL_NON_COMPLIANCE
```

without evidence supporting the stronger conclusion.

---

# 19. Not Observed Transition

If the system does not observe a declaration in the available evidence:

```text
NOT_OBSERVED
```

This does not automatically prove that the declaration is absent from the package.

The result may require:

```text
INSUFFICIENT EVIDENCE
        OR
REQUIRES_REVIEW
        OR
POTENTIAL_NON_COMPLIANCE
```

depending on the controlled rule, evidence coverage, and Inspector verification.

---

# 20. Processing Failure Transition

Technical failure follows:

```text
Processing Step
      ↓
Failure
      ↓
PROCESSING_FAILED
```

Examples:

```text
PaddleOCR unavailable
    → PROCESSING_FAILED

Gemini API unavailable
    → PROCESSING_FAILED

Malformed model response after retry
    → PROCESSING_FAILED

Image cannot be decoded
    → INPUT / PROCESSING ERROR
```

Never:

```text
Technical Failure
      ↓
POTENTIAL_NON_COMPLIANCE
```

---

# 21. Retry Semantics

Retryable technical failures may be retried in a controlled manner.

Example:

```text
AI Request
    ↓
Transient Failure
    ↓
Controlled Retry
    ↓
Success → Continue
    ↓
Failure → PROCESSING_FAILED
```

Retries must not:

- create duplicate findings
- create duplicate evidence
- mutate original evidence
- bypass lifecycle controls
- hide repeated failures

---

# 22. Ownership Model

Lifecycle ownership is explicit.

```text
DRAFT / PRE-SUBMISSION
        ↓
Inspector

SYSTEM PROCESSING
        ↓
System

INSPECTOR VERIFICATION
        ↓
Inspector

SUBMITTED / UNDER REVIEW
        ↓
Reviewer

FINALIZATION
        ↓
Reviewer + Backend validation

FINALIZED
        ↓
Historical record
```

The frontend must not be the authority for ownership.

Backend authorization is authoritative.

---

# 23. Finalization Preconditions

Finalization should require:

- valid lifecycle state
- Reviewer authority
- required inspection data
- valid evidence references
- valid rule snapshot/version
- applicable assessments resolved sufficiently
- required review decisions present
- no blocking processing failures
- audit information available

The exact finalization checklist may be refined in implementation, but finalization must never be an unrestricted client-side action.

---

# 24. Atomic Finalization

Finalization should behave as one logical transaction:

```text
Validate
   ↓
Create Final Snapshot
   ↓
Record Final Decision
   ↓
Record Audit References
   ↓
Mark Finalized
```

The system must avoid partially finalized records.

If finalization fails before the atomic commit, the inspection must remain in its previous valid state.

---

# 25. Report Generation After Finalization

Report generation is downstream from finalization:

```text
Reviewer Final Decision
        ↓
Final Snapshot
        ↓
Report Generation
```

A report-generation failure must not invalidate the final decision.

```text
FINALIZED
   +
REPORT_FAILED
```

is a technical output problem, not a reason to roll back the historical inspection.

---

# 26. Historical State

After finalization:

```text
FINALIZED
    ↓
Historical Record
```

Historical records must retain the context necessary to understand how the decision was produced.

This includes, where implemented:

- rule snapshot/version
- evidence references
- evidence hashes
- OCR
- extraction
- applicability
- findings
- corrections
- review decisions
- provenance
- final decision

Future rule/model/code changes must not silently rewrite historical records.

---

# 27. Forbidden Transitions

The following are forbidden through normal workflow:

```text
FINALIZED → EDIT
FINALIZED → DELETE
FINALIZED → SILENT RECOMPUTE
FINALIZED → RULE MUTATION
FINALIZED → EVIDENCE REPLACEMENT
```

Similarly:

```text
AI → FINALIZED
Inspector → FINALIZED
Client → FINALIZED
```

must not occur without the required Reviewer/backend workflow.

---

# 28. Reopening Finalized Records

Normal workflow does not reopen finalized inspections.

If a future system requires a correction to a finalized historical record, it should use an explicit controlled amendment/reprocessing mechanism with appropriate audit semantics.

That capability is outside the current one-day MVP.

---

# 29. Rule Versioning

Compliance assessments must be associated with the controlled rule snapshot/version used during evaluation.

Conceptually:

```text
Inspection
   ↓
Rule Snapshot V1
   ↓
Assessment
   ↓
Finalized
```

Later:

```text
Rule Snapshot V2
```

must not silently alter the historical V1 assessment.

---

# 30. AI Model Versioning

Where practical, processing provenance should preserve enough information to identify the AI/OCR processing context.

For example:

```text
OCR Engine / Version
AI Model / Version
Processing Timestamp
Prompt / Schema Version where appropriate
```

The purpose is reproducibility and auditability.

The exact implementation detail may be defined in the relevant technical/data specifications.

---

# 31. Current MVP State Subset

The one-day MVP should focus on these meaningful states:

```text
DRAFT / INPUT
      ↓
EVIDENCE_PROVIDED
      ↓
PROCESSING
      ↓
OCR_COMPLETE
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
RESULT
```

If review/finalization is implemented in the MVP, use the target workflow:

```text
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

Do not introduce additional lifecycle complexity merely to reproduce every target state.

---

# 32. MVP Processing State Simplification

Internally, implementation may combine:

```text
IMAGE_PROCESSING
OCR_PROCESSING
DECLARATION_EXTRACTION
APPLICABILITY_EVALUATION
COMPLIANCE_EVALUATION
FINDING_GENERATION
```

into fewer technical processing states if doing so is safer and faster.

However, the system must still preserve enough internal status information to distinguish:

- input errors
- OCR failure
- AI failure
- validation failure
- applicability completion
- compliance completion
- evidence/finding generation

This is an implementation optimization, not a change to the conceptual architecture.

---

# 33. Lifecycle and Compliance Result Independence

A single inspection may contain different requirement-level results.

Example:

```text
Manufacturer       → PASS
Generic Name       → PASS
Net Quantity       → PASS
Date               → REQUIRES_REVIEW
MRP                → POTENTIAL_NON_COMPLIANCE
Consumer Care      → NOT_OBSERVED
```

The inspection-level result must be derived from the controlled aggregation rules.

Do not infer inspection state solely from one field.

---

# 34. Aggregation Safety

The agent must not implement simplistic logic such as:

```text
Any red = illegal
```

or:

```text
All green = legally compliant
```

unless that aggregation behavior is explicitly defined by the applicable product/rule semantics.

The system should preserve requirement-level outcomes and uncertainty.

---

# 35. Applicability and State

Applicability must be resolved before treating a requirement as failed.

Example:

```text
Country of Origin
        ↓
Imported?
   ┌────┼────┐
  YES   NO   UNKNOWN
   │     │      │
   ▼     ▼      ▼
CHECK   N/A   REVIEW
```

`NOT_APPLICABLE` is a legitimate outcome.

It is not a failure and not necessarily a pass.

---

# 36. Evidence Sufficiency and State

Evidence sufficiency may block or qualify a compliance assessment.

Conceptually:

```text
Requirement
     ↓
Evidence Available?
     ├── YES → Evaluate
     ├── NO  → INCOMPLETE / REVIEW
     └── CONFLICTING → REQUIRES_REVIEW
```

The system must not manufacture certainty to force a binary result.

---

# 37. Inspector Correction and Ownership

An Inspector correction before submission remains part of the working record.

Example:

```text
System Extraction
      ↓
Inspector Correction
      ↓
Recompute
      ↓
Inspector Verification
      ↓
Submit
```

The Inspector does not need Reviewer approval for every underlying data correction.

The correction must nevertheless be auditable.

---

# 38. Reviewer Override

A Reviewer may override a system assessment when authorized.

The override must preserve:

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
        +
Evidence / Reference
```

The original system assessment is not erased.

---

# 39. Reviewer Evidence Request

A Reviewer evidence request should contain:

```text
Evidence Request ID
Requirement / Fact
Reason
Requested Evidence or Clarification
Created By
Created At
Status
```

Example:

```text
ER-00017
Requirement: Net Quantity
Reason: Current image does not establish unit clearly
Request: Provide clearer evidence of quantity declaration
```

The Inspector may respond through the supported evidence workflow.

---

# 40. Audit Requirements

Material lifecycle transitions should generate audit records.

Examples:

- inspection created
- evidence added
- evidence processed
- extraction corrected
- assessment changed
- evidence request created
- evidence request resolved
- inspection submitted
- Reviewer decision made
- finalization
- processing failure where operationally relevant

Audit records should capture, as appropriate:

```text
Actor
Timestamp
Action
Old State
New State
Reason
Affected Object
Relevant Evidence / Reference
```

Audit history must not be silently rewritten.

---

# 41. State Idempotency

Repeated requests must not create inconsistent state.

Examples:

```text
Double-click Submit
      ↓
One valid submission

Repeated Finalize Request
      ↓
No duplicate finalization

Retry AI Processing
      ↓
No duplicate evidence/findings
```

The implementation should use appropriate idempotency or state checks for critical transitions.

---

# 42. Concurrent Action Safety

The backend must protect lifecycle transitions against conflicting simultaneous actions.

Example:

```text
Reviewer finalizes
        +
Inspector attempts edit
        ↓
Backend rejects invalid mutation
```

The frontend state alone is not sufficient.

---

# 43. Authorization and State

Authorization is evaluated at the backend.

A valid transition requires both:

```text
Correct Current State
        +
Authorized Actor
        ↓
Transition Allowed
```

For example:

```text
INSPECTOR + FINALIZED
        ↓
DENIED

REVIEWER + FINALIZED
        ↓
Normal edit DENIED
```

---

# 44. State Recovery

If a processing service fails, the inspection must remain recoverable.

The system should preserve enough information to determine:

- last successful stage
- failed stage
- error category
- affected evidence
- whether retry is safe

Do not reset the entire inspection unnecessarily.

---

# 45. State Recovery Example

```text
Evidence Provided
      ↓
Image Processing
      ↓
OCR Complete
      ↓
Gemini Failure
      ↓
PROCESSING_FAILED
      ↓
Retry
      ↓
Declaration Extraction
      ↓
Continue
```

The system should not discard successful OCR results unless they are invalidated by an actual upstream change.

---

# 46. State Invalidation Scope

When a value changes, invalidate only the downstream information that depends on it where practical.

Example:

```text
Consumer Care Number correction
      ↓
Invalidate affected consumer-care assessment
      ↓
Recompute relevant finding
```

Do not unnecessarily invalidate unrelated observations.

However, correctness takes precedence over optimization.

If dependency cannot be safely determined:

> Recompute the broader affected processing scope.

---

# 47. Finalized Immutability

The finalized record is the historical truth of the workflow decision.

Normal application paths must not permit:

- editing
- deleting
- replacing evidence
- changing rules
- changing the final decision
- removing audit history

Any future amendment system must be explicit and separately authorized.

---

# 48. State Machine Invariants

The following invariants are mandatory.

## Invariant 1 — No Finalization Without Reviewer

```text
Only Reviewer-controlled workflow
        ↓
FINALIZED
```

## Invariant 2 — No AI Finalization

```text
AI
  ≠
Final Decision Authority
```

## Invariant 3 — No Technical Failure as Compliance Failure

```text
PROCESSING_FAILED
  ≠
POTENTIAL_NON_COMPLIANCE
```

## Invariant 4 — No Unsupported Fact

```text
No Evidence
   ↓
No Accepted AI Fact
```

## Invariant 5 — No Silent Downstream Staleness

```text
Upstream Correction
   ↓
Affected Downstream State Invalidated
```

## Invariant 6 — Original Evidence Immutable

```text
Original Evidence
   ↓
Never silently replaced
```

## Invariant 7 — Historical Finalization

```text
FINALIZED
   ↓
No normal mutation
```

## Invariant 8 — Applicability Before Assessment

```text
Applicability
   ↓
Compliance Evaluation
```

## Invariant 9 — Uncertainty Preserved

```text
UNKNOWN / UNCERTAIN / UNREADABLE / CONFLICTING
        ↓
Never silently converted to certainty
```

## Invariant 10 — Backend Authority

```text
Client Request
   ↓
Backend validates state + authorization
   ↓
Transition
```

---

# 49. State Transition Validation

Before every important transition:

```text
1. Identify current state
2. Identify actor
3. Validate authorization
4. Validate preconditions
5. Validate data integrity
6. Perform transition atomically where required
7. Record audit event
8. Return resulting state
```

This should be implemented centrally where practical rather than duplicated inconsistently across UI handlers.

---

# 50. State Machine and One-Day Execution

The one-day implementation should not attempt to build the entire target state graph.

The practical execution path is:

```text
PHASE 0
Audit
  ↓
PHASE 1
Foundation
  ↓
PHASE 2
Input
  ↓
PHASE 3
OCR
  ↓
PHASE 4
AI Extraction
  ↓
PHASE 5
Applicability + Rules
  ↓
PHASE 6
Findings + Evidence
  ↓
PHASE 7
Inspector Verification + Result
  ↓
PHASE 8
QA + Basic Output
  ↓
PHASE 9
Deployment
```

The state machine supports this sequence without requiring every target feature to be built.

---

# 51. Relationship to Other Documents

| Document | State-Machine Relationship |
|---|---|
| `MVP_BUILD_SCOPE.md` | Defines which lifecycle subset is currently implemented |
| `PROJECT_STATE.md` | Records actual lifecycle implementation status |
| `PHASE.md` | Defines implementation sequence |
| `AGENT_ENGINEERING_PROTOCOL.md` | Defines implementation discipline |
| `05_Domain_Specification.md` | Defines domain concepts used by states |
| `06_Compliance_Rules.md` | Defines compliance assessment semantics |
| `08_API_Specification.md` | Defines API contracts for transitions |
| `09_Database_Specification.md` | Defines persistence representation |
| `10_Error_Handling.md` | Defines technical failure behavior |
| `11_Testing_and_Release_Gate.md` | Defines transition/workflow validation |

This document is authoritative for lifecycle/state semantics.

---

# 52. Implementation Guidance

The implementation should prefer:

- explicit state transitions
- backend authorization
- centralized transition validation
- transaction-safe critical changes
- auditability
- clear error states
- deterministic downstream invalidation
- immutable original evidence
- clear separation between lifecycle and compliance result

Avoid:

- scattered state mutation
- UI-only state enforcement
- implicit transitions
- hidden side effects
- automatic finalization
- silent recomputation
- destructive updates to historical data

---

# 53. Current MVP State Checklist

For the current one-day MVP, verify that the implemented workflow can answer:

```text
[ ] Can an inspection be created?
[ ] Can evidence be provided?
[ ] Can the evidence be processed?
[ ] Can PaddleOCR produce text and regions?
[ ] Can Gemini produce structured declarations?
[ ] Are AI uncertainties preserved?
[ ] Can applicability be determined?
[ ] Can the six supported checks be evaluated?
[ ] Are findings explainable?
[ ] Are findings linked to evidence?
[ ] Can the Inspector verify/correct information?
[ ] Does correction trigger affected recomputation?
[ ] Can a meaningful result be produced?
[ ] Can the data persist in the deployed environment?
[ ] Can the workflow survive technical failure?
[ ] Can the workflow be demonstrated end-to-end?
```

A checked box must mean the behavior has actually been verified, not merely implemented in code.

---

# 54. Current Status

### Target Lifecycle

**Status:** Defined

The broader inspection lifecycle, evidence-request loop, Reviewer workflow, and finalization model are defined.

### MVP Lifecycle

**Status:** Defined

The current vertical-slice lifecycle is defined as a controlled subset.

### Implementation

**Status:** Must be verified from the actual repository.

This document does not claim that any state transition is already implemented merely because it is specified here.

### Next Required Action

> **Phase 0 repository/implementation audit.**

The agent must establish actual state before claiming implementation completeness.

---

# 55. Final Lifecycle Model

The lifecycle can be summarized as:

```text
PREPARE
  ↓
CAPTURE EVIDENCE
  ↓
PROCESS
  ↓
UNDERSTAND
  ↓
DETERMINE APPLICABILITY
  ↓
ASSESS
  ↓
GENERATE EVIDENCE-BACKED FINDINGS
  ↓
INSPECTOR VERIFIES
  ↓
SUBMIT
  ↓
REVIEWER INDEPENDENTLY REVIEWS
  ↓
REQUEST EVIDENCE / CORRECT / CONFIRM
  ↓
FINALIZE
  ↓
IMMUTABLE HISTORICAL RECORD
```

With the central invariant:

> **Upstream correction → invalidate affected downstream state → recompute → preserve prior state/history → audit transition.**

And the central responsibility boundary:

> **The Inspector prepares and verifies. The System analyzes and records. The Reviewer independently decides and finalizes.**
