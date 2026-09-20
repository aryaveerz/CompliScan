# MVP BUILD SCOPE

**Project:** ComplianceScan
**SIH'26 Problem Statement:** 26034
**Document Version:** 2.0
**Status:** Current build-control document
**Purpose:** Defines exactly what the one-day MVP will and will not build.

---

# 1. Document Authority

This document is the **current implementation boundary** for the MVP.

The numbered architecture and specification documents describe the broader target system. They are reference architecture and future-system contracts unless a capability is explicitly included in this document.

When a target-system feature is not listed in this MVP scope:

> **It is not an MVP requirement.**

The coding agent must not infer MVP scope from the size of the target documentation set.

---

# 2. Why This Document Exists

The complete ComplianceScan target system is substantially larger than a one-day implementation.

The MVP therefore follows a strict vertical-slice strategy:

> **ONE COMPLETE USER JOURNEY > MANY PARTIAL SUBSYSTEMS**

The goal is to demonstrate one coherent, trustworthy inspection workflow rather than superficially implementing every planned subsystem.

---

# 3. MVP Goal

The one-day MVP must demonstrate:

```text
Create Inspection
      ↓
Provide Product / Context
      ↓
Capture / Upload Evidence
      ↓
Validate Evidence
      ↓
Image Processing
      ↓
PaddleOCR
      ↓
Gemini 2.5 Flash
      ↓
Structured Declaration Extraction
      ↓
Applicability
      ↓
Deterministic Compliance Checks
      ↓
Findings + Evidence
      ↓
Inspector Verification
      ↓
Result
      ↓
Report / Inspection Record
```

The MVP should make this journey demonstrable end-to-end.

---

# 4. Core Product Message

The MVP must communicate:

> **Scan → Understand → Determine Applicability → Validate → Prove with Evidence → Inspector Verifies → Report**

The safety principle is:

> **AI finds → Evidence supports → Backend validates → Inspector verifies.**

The MVP must not present AI output as an autonomous legal determination.

---

# 5. MVP Product Boundary

The MVP is an **inspection-assistance prototype for a supported packaged-commodity scenario**.

It is not:

- a complete Legal Metrology enforcement platform
- universal coverage of all packaged commodities
- a complete statutory rule-management system
- an internet-wide product crawler
- an automated enforcement decision-maker
- a replacement for an authorized officer
- a complete production governance platform

---

# 6. MVP Supported Compliance Scope

The MVP implements six core declaration checks:

## 6.1 Manufacturer / Packer / Importer

Check whether the applicable identity declaration is observed and usable.

---

## 6.2 Common / Generic Product Name

Check whether the product's common/generic name is established.

---

## 6.3 Net Quantity + Standard Unit

Check:

- net quantity
- associated unit
- expected/usable representation

---

## 6.4 Month / Year of Manufacture / Packing / Import

Check the applicable date declaration for the supported scenario.

---

## 6.5 MRP Inclusive of All Taxes

Check whether the applicable MRP declaration is observed in the supported format/context.

---

## 6.6 Consumer Care Details

Check whether consumer-care information is observed and usable.

---

# 7. Country of Origin

Country of Origin is included only through applicability logic.

```text
Imported = YES
      ↓
COO applicable

Imported = NO
      ↓
COO = NOT_APPLICABLE

Imported = UNKNOWN
      ↓
REQUIRES_REVIEW / INCOMPLETE
```

The MVP must not assume Country of Origin is universally applicable.

---

# 8. Explicitly Deferred Compliance Scope

The following are intentionally outside the one-day MVP unless separately approved:

- Unit Sale Price
- broad category-specific rules
- universal exemptions
- complete amendment-aware legal rule coverage
- dynamic legal-regulation update pipeline
- universal font-size legal verification
- universal placement verification
- full statutory enforcement workflows
- penalty/enforcement management

---

# 9. Applicability First

Applicability is a required stage before compliance assessment where the requirement depends on context.

Conceptually:

```text
Evidence
  ↓
Declaration
  ↓
Context
  ↓
Applicability
  ↓
Requirement Relevant?
  ↓
Compliance Assessment
```

The system must not evaluate an irrelevant declaration as though it were universally mandatory.

---

# 10. Controlled Rule Snapshot

The MVP uses a **controlled Legal Metrology rule snapshot** for its supported checks.

The MVP does not implement a dynamic legal-rule management/update pipeline.

Rules must be:

- explicit
- versionable
- reviewable
- deterministic where applicable
- traceable to their controlled rule reference

Historical results should retain the rule context used for the assessment.

---

# 11. Result Vocabulary

The MVP uses:

```text
PASS
POTENTIAL_NON_COMPLIANCE
REQUIRES_REVIEW
NOT_APPLICABLE
INCOMPLETE
PROCESSING_FAILED
```

These states must not be collapsed into a generic PASS/FAIL.

---

# 12. Critical Result Distinctions

The implementation must preserve:

```text
NOT_APPLICABLE ≠ PASS

INCOMPLETE ≠ POTENTIAL_NON_COMPLIANCE

PROCESSING_FAILED ≠ POTENTIAL_NON_COMPLIANCE

NOT_OBSERVED ≠ proven missing

UNREADABLE ≠ NOT_OBSERVED

CONFLICTING → REQUIRES_REVIEW
```

A technical failure must never become a compliance failure.

---

# 13. Evidence Model

The MVP must treat original evidence as first-class inspection data.

Evidence categories:

```text
PRIMARY EVIDENCE
    Original package/product images

SUPPLEMENTAL EVIDENCE
    Additional images/observations added later

DERIVED EVIDENCE
    OCR boxes
    crops
    highlights
    analysis artifacts
```

The audit/decision record is not itself package evidence.

---

# 14. Adaptive Evidence Capture

The MVP must not enforce an arbitrary fixed number of photos.

Evidence should be sufficient to establish the supported requirements.

Conceptually:

```text
Requirement
   ↓
Evidence coverage
   ↓
Sufficient?
   ├── YES → continue
   └── NO → Inspector Verification / supplemental evidence
```

The MVP may use a practical/simple coverage mechanism rather than implementing a sophisticated universal evidence-planning engine.

---

# 15. Evidence Integrity

Where evidence persistence is implemented, the MVP should establish:

- authenticated upload
- backend validation
- server-generated Evidence ID
- safe persistent storage
- SHA-256 hash
- source association
- provenance
- audit event where material

The hash provides:

> **tamper-evident integrity/change detection**

It does not prove:

- that the image is truthful
- that the image depicts the claimed product
- that the image is legally authentic

---

# 16. Original Evidence Immutability

Original evidence must not be modified by:

- OCR
- image preprocessing
- AI
- compliance evaluation
- highlighting
- cropping

Analysis must operate on derived/working copies.

If new evidence is added:

```text
New Image
   ↓
New Evidence ID
```

Do not overwrite the original evidence artifact.

---

# 17. Image Processing Scope

The MVP may perform practical preprocessing such as:

- orientation correction
- resizing
- safe preprocessing
- brightness/contrast adjustment where useful
- analysis-copy preparation
- basic quality assessment

The original image remains preserved.

---

# 18. OCR Selection

The MVP OCR engine is:

> **PaddleOCR**

PaddleOCR is responsible for:

- text detection
- text recognition
- bounding boxes
- OCR confidence
- source-image association

PaddleOCR does not determine compliance.

---

# 19. AI Selection

The MVP model is:

> **Gemini 2.5 Flash**

The model is used primarily for:

- declaration extraction
- semantic interpretation
- normalization
- context mapping
- conflict detection
- preserving uncertainty

The backend remains authoritative.

---

# 20. AI Responsibility Boundary

The AI must not:

- make the final legal decision
- invent declarations
- silently resolve conflicts
- modify original evidence
- modify compliance rules
- finalize an inspection
- alter finalized history

The pipeline is:

```text
PaddleOCR reads.
Gemini understands.
Backend validates.
Applicability determines relevance.
Rules evaluate.
Evidence supports.
Inspector verifies.
```

---

# 21. Structured AI Contract

AI output must be constrained to the supported declaration schema.

Each accepted declaration should preserve, where applicable:

- value
- normalized value
- observation status
- extraction confidence
- source OCR region(s)
- source evidence reference(s)

Observation statuses:

```text
OBSERVED
NOT_OBSERVED
UNCERTAIN
UNREADABLE
CONFLICTING
```

No source evidence means the system must not treat an AI-generated value as an accepted fact.

---

# 22. Confidence Separation

The MVP must not treat all confidence values as equivalent.

```text
OCR Confidence
      ≠
AI Extraction Confidence
      ≠
Evidence Sufficiency
      ≠
Compliance Result
```

Low confidence should preserve uncertainty rather than trigger an arbitrary legal conclusion.

---

# 23. OCR Confidence Policy

No universal hard-coded OCR confidence threshold is treated as a legal boundary.

The implementation may use technical thresholds for processing/routing, but these are engineering thresholds, not legal standards.

Representative-image testing should be used to calibrate practical behavior.

---

# 24. Conflict Handling

If multiple credible values are found:

```text
Value A
+
Value B
+
Conflict
      ↓
CONFLICTING
      ↓
REQUIRES_REVIEW
```

The system must preserve the conflicting observations.

It must not silently choose one.

---

# 25. Unreadable vs Missing

The MVP must distinguish:

```text
NOT_OBSERVED
UNREADABLE
UNCERTAIN
```

For example:

```text
Declaration cannot be read
      ↓
UNREADABLE

Not found with sufficient evidence
      ↓
NOT_OBSERVED
```

The system must not claim a declaration is legally missing solely because OCR failed.

---

# 26. Processing Failure

If OCR/AI or another required technical stage fails:

```text
PROCESSING_FAILED
```

The system must not convert that failure into:

```text
POTENTIAL_NON_COMPLIANCE
```

Example:

```text
Gemini unavailable
      ↓
PROCESSING_FAILED
```

---

# 27. AI Failure Recovery

Transient failures may be retried.

Examples:

- timeout
- temporary provider outage
- transient network failure
- rate limiting where safe

Malformed output should undergo controlled validation/retry.

If the failure remains unresolved:

```text
PROCESSING_FAILED
```

The original failed attempt should remain traceable.

---

# 28. Deterministic Compliance Engine

The compliance decision for the supported checks must be produced by backend-controlled logic/rules.

Conceptually:

```text
Structured Declaration Data
        ↓
Applicability
        ↓
Controlled Rules
        ↓
Deterministic Evaluation
        ↓
Assessment
```

AI is not the compliance engine.

---

# 29. Findings

A finding should provide, where applicable:

- requirement
- result
- reason
- controlled rule reference
- evidence reference
- source/derived evidence
- confidence/uncertainty context
- verification state

The goal is:

> **Every material finding should be explainable from recorded evidence and rule logic.**

---

# 30. Evidence-Based Findings

Bad:

```text
AI says MRP is wrong.
```

Good:

```text
Requirement: MRP
Observation: ₹179
Expected/validated condition: ...
Evidence: IMG-001, OCR region ...
Assessment: POTENTIAL_NON_COMPLIANCE
Reason: ...
```

The MVP should make the evidence trail visible.

---

# 31. Visual Analysis Scope

The MVP may provide:

- readability assessment
- visibility indication
- placement/evidence-context observation
- basic font-size warning/assessment
- evidence coverage assistance

These are visual assistance functions.

They are not universal definitive legal verdicts.

---

# 32. Font Size

The MVP may flag apparent font-size concerns.

However, camera/image scale limitations mean:

> **Font-size analysis is an assessment/warning, not a definitive legal measurement unless reliable scale evidence exists.**

Do not present an approximate visual estimate as an exact statutory measurement.

---

# 33. Placement

The MVP may support lightweight placement/evidence assessment.

It does not attempt universal legal verification of every packaging-layout placement requirement.

---

# 34. Inspector Role

The operational MVP role is:

> **Inspector**

The Inspector can:

- create inspection
- provide product/context
- upload evidence
- initiate analysis
- inspect OCR/declarations
- review confidence/uncertainty
- correct extracted values
- add manual observations
- add supplemental evidence where supported
- verify applicability
- verify compliance assessment
- submit the inspection

The Inspector does not:

- modify controlled rules
- modify original evidence
- delete historical evidence
- finalize the inspection
- alter audit history

---

# 35. Reviewer Role

The target system includes:

> **Reviewer**

Where the Reviewer workflow is included in the current MVP build, the Reviewer can:

- receive submitted inspections
- inspect evidence
- inspect OCR/declarations
- inspect applicability
- inspect findings
- inspect audit/history
- confirm
- correct/override assessment with reason
- request additional evidence
- finalize

The Reviewer does not:

- modify controlled rules
- delete historical finalized inspections
- mutate finalized records

If time constraints prevent full Reviewer implementation in the one-day build, Reviewer remains a target-system capability and the MVP must not fake final-review functionality.

---

# 36. Inspector vs Reviewer Correction Boundary

The distinction is mandatory:

```text
Inspector
  ↓
Correct underlying extracted data / observation

Reviewer
  ↓
Correct or override assessment / decision
```

A Reviewer override requires an appropriate reason.

---

# 37. Human-in-the-Loop Principle

The MVP must demonstrate that:

> **AI assists; a human verifies.**

The system should expose enough evidence and uncertainty for the Inspector to correct or challenge automated extraction.

---

# 38. Submission Boundary

The conceptual ownership boundary is:

```text
WORKING
Inspector controls

SUBMITTED
Reviewer controls

FINALIZED
Read-only
```

Before submission, the Inspector owns the working record.

After submission, normal Inspector editing is restricted according to the lifecycle.

---

# 39. Evidence Request Loop

If Reviewer functionality is implemented:

```text
Reviewer
   ↓
Evidence Request
   ↓
Inspector
   ↓
Supplement / Manual Verification / Unable to Establish
   ↓
Reprocess if required
   ↓
Inspector verifies
   ↓
Resubmit
   ↓
Reviewer
```

An Evidence Request should identify what fact/condition needs to be established.

---

# 40. Finalization

Finalization is a target-system capability and may be simplified or deferred in the one-day MVP if it would compromise the complete primary journey.

Where implemented:

```text
Reviewer
   ↓
Validate Preconditions
   ↓
Atomic Finalization
   ↓
Immutable Snapshot
   ↓
FINALIZED
```

A finalized inspection is read-only through normal workflow.

---

# 41. Historical Integrity

Historical records must preserve the context of their assessment.

This includes, where implemented:

- rule snapshot/version
- evidence references
- evidence hashes
- OCR runs
- AI runs
- extracted declarations
- corrections
- assessments
- findings
- review decisions
- final decision
- audit references

Future rule changes must not silently recalculate historical finalized records.

---

# 42. Report Scope

The MVP should provide a useful inspection report when feasible.

Report content should include:

- inspection identity
- product/context
- evidence references
- observed declarations
- applicability
- assessments
- findings
- reasons
- evidence references
- verification/decision information where implemented

PDF/export may be implemented as the primary demonstration output.

Editable export is target functionality and is not allowed to block the one-day core journey.

---

# 43. Repository / History Scope

The MVP should persist inspection records sufficiently to demonstrate:

```text
Create
→ Analyze
→ Verify
→ Retrieve
```

A full enterprise repository/search/history platform is target scope.

Do not spend the one-day build on advanced filtering or analytics at the expense of the core inspection journey.

---

# 44. Dashboard Scope

A basic dashboard may show useful aggregate metrics if inexpensive after the core journey is complete.

Examples:

- inspections processed
- pass count
- potential non-compliance count
- review/incomplete count
- processing failures

Advanced analytics are deferred.

---

# 45. Physical ↔ Online Verification

This is a **P1 target capability**.

If included, the MVP should keep it narrow:

```text
Physical Product
      ↓
Online Listing
      ↓
Identity Match
      ↓
Field Comparison
      ↓
Cross-Channel Inconsistency
```

A mismatch is:

> **Cross-Channel Inconsistency**

not automatically a legal violation.

The MVP does not implement internet-wide crawling.

---

# 46. Deployment Boundary

The MVP is intended for deployment and external demonstration.

Therefore:

> **The deployed MVP must not depend on local-only persistence.**

Required deployed architecture characteristics:

- cloud-deployable backend
- persistent cloud-capable relational database
- persistent object/file storage for evidence
- server-side secrets
- deployable frontend
- externally accessible demonstration environment

The exact providers are not locked.

---

# 47. Database Boundary

The production/deployed MVP requires a persistent relational database capable of cloud deployment.

SQLite may be used for:

- local development
- isolated testing
- temporary prototyping

SQLite is **not** the deployed source of truth.

The exact production database/provider remains open for team decision.

---

# 48. Object Storage Boundary

Original evidence requires persistent storage in the deployed environment.

The exact object-storage provider remains open.

Do not make the deployed MVP dependent on:

```text
local machine filesystem
```

as its permanent evidence store.

---

# 49. Frontend / Backend Boundary

The MVP may use a practical deployable frontend/backend arrangement.

For example:

```text
Frontend
   ↓
Backend API
   ↓
Database
   ↓
Object Storage
   ↓
OCR / AI Providers
```

The exact framework/provider combination remains an implementation decision.

The target architecture must not be weakened merely to fit a preferred hosting platform.

---

# 50. Technology Decision Policy

The final production tech stack is **not locked by this document**.

The implementation team may select practical technologies based on:

- one-day feasibility
- reliability
- deployment readiness
- integration simplicity
- team familiarity
- cost
- security
- maintainability

The architecture and behavioral contracts must remain stable even if implementation technology changes.

---

# 51. Secrets

Secrets must remain server-side.

Examples:

- Gemini API key
- database credentials
- object-storage credentials
- authentication secrets

Never expose secrets in:

- frontend source
- browser network payloads
- Git repository
- reports
- logs
- screenshots

---

# 52. Security Minimum

The MVP must include reasonable protection for:

- authenticated API operations where authentication is implemented
- backend authorization
- evidence access
- server-side secret handling
- input validation
- file validation
- safe storage paths
- basic auditability of material actions

Do not implement decorative security controls that delay the core journey without reducing a meaningful risk.

---

# 53. What the MVP Must NOT Become

Do not expand the one-day build into:

- microservice architecture
- complete RBAC administration suite
- rule-authoring portal
- full legal knowledge graph
- universal exemption engine
- universal category classifier
- internet crawler
- advanced analytics platform
- complete mobile application
- complex notification system
- enterprise document-management platform
- full enforcement case-management system

These are target/future capabilities unless explicitly approved.

---

# 54. One-Day Critical Path

The preferred implementation order is:

```text
1. Establish runnable project
2. Establish deployable persistence
3. Inspection creation
4. Evidence upload/storage
5. Image processing
6. PaddleOCR
7. Gemini extraction
8. Structured validation
9. Applicability
10. Six compliance checks
11. Findings/evidence
12. Inspector verification
13. Result
14. Report
15. Deployment/demo verification
```

Reviewer, dashboard, advanced repository, and physical-online verification come after the critical path unless already inexpensive and stable.

---

# 55. Vertical Slice Definition

The minimum convincing demonstration is:

```text
User
 ↓
Creates inspection
 ↓
Uploads package image
 ↓
System stores original evidence
 ↓
PaddleOCR extracts text
 ↓
Gemini structures declarations
 ↓
Backend validates
 ↓
Applicability runs
 ↓
Six supported checks run
 ↓
Findings generated with evidence
 ↓
Inspector verifies/corrects
 ↓
Result is produced
 ↓
Inspection/report is retrievable
```

If this journey works reliably, the MVP has achieved its primary objective.

---

# 56. Demo Dataset / Representative Images

Testing should use representative packaged-commodity images that exercise:

- readable declarations
- multiple declaration layouts
- noisy OCR
- ambiguous values
- missing/unclear observations
- imported/non-imported context where applicable
- positive compliance cases
- potential non-compliance cases
- conflict/review cases
- processing failure cases

The exact images are implementation/test assets, not part of the legal rule definition.

---

# 57. Failure-First Demonstration

The MVP should demonstrate not only a successful case but safe failure behavior where feasible.

Examples:

```text
Valid image
→ successful analysis

Poor image
→ uncertainty / review

AI unavailable
→ PROCESSING_FAILED

Conflicting values
→ REQUIRES_REVIEW
```

This demonstrates trustworthiness rather than only happy-path automation.

---

# 58. Quality Bar

A feature is MVP-ready only when it is:

```text
Implemented
+
Integrated
+
Tested
+
Recoverable
+
Consistent with domain rules
+
Deployable
```

A half-built feature is not considered complete merely because its UI exists.

---

# 59. Definition of Done

The MVP is ready for demonstration when:

```text
[ ] Application runs reliably
[ ] Deployed environment is reachable
[ ] Persistent deployed database works
[ ] Persistent evidence storage works
[ ] Inspection can be created
[ ] Evidence can be uploaded
[ ] Original evidence is preserved
[ ] Image processing works
[ ] PaddleOCR works
[ ] Gemini 2.5 Flash integration works
[ ] AI output is schema-validated
[ ] AI cannot silently invent accepted declarations
[ ] Applicability is evaluated for supported context
[ ] Six core checks execute
[ ] Findings have reasons/evidence references
[ ] Inspector can verify/correct results
[ ] Processing failures are explicit
[ ] Conflicts remain reviewable
[ ] Technical failures do not become non-compliance
[ ] Inspection state remains consistent
[ ] Results can be retrieved
[ ] Useful report/output can be produced
[ ] Representative cases have been tested
[ ] Critical failure paths have been tested
[ ] No known blocker remains in the primary journey
```

---

# 60. MVP Release Gate

Before calling the MVP complete, perform:

## Functional Gate

```text
Happy path
Correction path
Uncertainty path
Conflict path
Failure/retry path
Retrieval path
```

## Integrity Gate

Verify:

```text
Original evidence preserved
Hashes stable
Derived artifacts distinguishable
Corrections traceable
No finalized mutation
```

## Compliance Gate

Verify:

```text
Six supported checks
Applicability
Result vocabulary
No false non-compliance from processing failure
```

## Deployment Gate

Verify:

```text
Frontend reachable
Backend reachable
Database reachable
Object storage reachable
AI configuration valid
OCR available
Secrets server-side
```

---

# 61. Current vs Target System

The broader target system remains documented in:

```text
01_PRD.md
02_TRD.md
03_Architecture.md
04_Design.md
05_Domain_Specification.md
06_Compliance_Rules.md
07_State_Machine.md
08_API_Specification.md
09_Database_Specification.md
10_Error_Handling.md
11_Testing_and_Release_Gate.md
```

The distinction is:

```text
Target Documents
      ↓
What the complete system may become

MVP_BUILD_SCOPE.md
      ↓
What we are building now
```

The target architecture is not being discarded.

It is being staged.

---

# 62. Scope-Control Rule for Antigravity

Antigravity must treat this document as the primary scope boundary for the one-day MVP.

Before implementing a feature, determine:

```text
Is it required by this document?
      ├── YES → implement if within current phase
      └── NO
           ↓
Is it necessary to make the primary journey work?
           ├── YES → propose before expanding
           └── NO → defer
```

The agent must not expand scope simply because a target document contains an endpoint, table, role, screen, or component.

---

# 63. Proposal Rule

If implementation reveals a missing capability that appears necessary:

```text
Identify gap
   ↓
Explain why it blocks the primary journey
   ↓
Propose smallest viable addition
   ↓
Human approval
   ↓
Implement
```

Do not silently add material scope.

---

# 64. Anti-Feature-Creep Rule

The following are not valid reasons to expand MVP scope:

- “The architecture document mentions it.”
- “It would be nice to have.”
- “The UI would look better.”
- “A complete product should have it.”
- “The database can support it.”
- “The agent already created the model.”
- “It only takes a few endpoints.”
- “We may need it someday.”

The one-day MVP is judged by a working vertical slice.

---

# 65. Stopping Rule

Once the primary journey is working and release gates pass:

> **STOP BUILDING NEW FEATURES.**

Use remaining time for:

- testing
- bug fixing
- deployment reliability
- evidence correctness
- UX clarity
- demo preparation

Do not spend the final hours adding unrelated functionality.

---

# 66. Architecture Stability Rule

Do not create a second “mini architecture” that contradicts the target architecture.

Instead:

```text
Target Architecture
       ↓
Select MVP subset
       ↓
Implement subset
       ↓
Preserve interfaces/boundaries
       ↓
Expand later
```

The MVP is a vertical slice of the architecture, not a separate product architecture.

---

# 67. Documentation Stability Rule

Documentation work is now considered complete enough for implementation.

Do not enter another documentation-expansion loop unless a real implementation discovery requires a material contract change.

If implementation exposes a contradiction:

```text
Stop
 ↓
Identify authoritative document
 ↓
Determine smallest correction
 ↓
Update relevant document
 ↓
Record change
 ↓
Continue
```

---

# 68. Project State Relationship

`PROJECT_STATE.md` records:

> **What is actually implemented right now.**

This document records:

> **What the current MVP is supposed to contain.**

Therefore:

```text
MVP_BUILD_SCOPE
       ≠
PROJECT_STATE
```

They must not be silently merged.

---

# 69. Phase Relationship

`PHASE.md` defines:

- execution order
- phase gates
- implementation sequence

This document defines:

- scope
- inclusion
- exclusion
- MVP definition of done

Together:

```text
MVP_BUILD_SCOPE
      +
PHASE
      +
PROJECT_STATE
      +
AGENT_ENGINEERING_PROTOCOL
```

form the primary implementation-control layer.

---

# 70. Relationship to Error Handling

`10_Error_Handling.md` defines the detailed failure model.

The MVP must at minimum preserve:

```text
Processing failure
≠
Compliance failure
```

and:

```text
Technical failure
→ explicit recovery state
```

---

# 71. Relationship to State Machine

`07_State_Machine.md` is authoritative for lifecycle transitions.

This scope document identifies the states/capabilities required by the MVP but does not replace the state-machine contract.

---

# 72. Relationship to API and Database Specifications

`08_API_Specification.md` defines the broader API contract.

`09_Database_Specification.md` defines the broader persistence model.

The MVP should implement only the subset needed for the current vertical slice.

Unused target endpoints/tables are not MVP requirements.

---

# 73. Relationship to Compliance Rules

`06_Compliance_Rules.md` is authoritative for the supported compliance checks.

This document defines the scope boundary:

```text
Six core checks
+
Applicability-driven Country of Origin
```

The legal-rule document defines their detailed behavior.

---

# 74. Human Decision Boundary

The MVP must never claim:

> “The AI has legally determined that this product violates the law.”

Preferred language:

> “The system identified potential non-compliance based on the configured rule and recorded evidence; the Inspector verifies the assessment.”

For target Reviewer workflow:

> “The Reviewer makes the independent final decision.”

---

# 75. Evidence Language

Use:

```text
Observed
Not observed
Unreadable
Uncertain
Conflicting
Potential non-compliance
Requires review
Unable to establish
```

Avoid unsupported certainty such as:

```text
Definitely illegal
AI proved violation
Image proves authenticity
Hash proves truth
```

---

# 76. Security / Integrity Language

Correct:

> “SHA-256 provides tamper-evident integrity/change detection.”

Incorrect:

> “SHA-256 proves the evidence is authentic.”

Correct:

> “Backend authorization controls access.”

Incorrect:

> “The frontend hides unauthorized buttons, therefore access is secure.”

---

# 77. MVP Success Definition

The MVP succeeds if a judge can see a realistic inspection scenario and understand:

```text
1. What evidence was captured
2. What the system read
3. What declarations were extracted
4. Which requirements were applicable
5. How each supported check was evaluated
6. Why a finding exists
7. What evidence supports it
8. What the Inspector verified/corrected
9. What result was produced
10. That technical uncertainty/failure is handled safely
```

---

# 78. Final Scope Statement

The one-day ComplianceScan MVP is a **cloud-deployable, evidence-centered, AI-assisted packaged-commodity inspection vertical slice**.

Its core capability is:

```text
Evidence
  ↓
PaddleOCR
  ↓
Gemini 2.5 Flash
  ↓
Structured Declarations
  ↓
Applicability
  ↓
Six Controlled Compliance Checks
  ↓
Evidence-Based Findings
  ↓
Inspector Verification
  ↓
Inspection Result
  ↓
Persistent Record / Report
```

Its most important constraints are:

```text
No universal legal coverage.
No autonomous legal decision.
No invented facts.
No silent conflict resolution.
No false non-compliance from technical failure.
No local-only deployed persistence.
No uncontrolled scope expansion.
No mutation of original evidence.
No mutation of finalized history.
```

The governing principle is:

> **Build one trustworthy complete journey before expanding the system.**
