# 01 — PRODUCT REQUIREMENTS DOCUMENT (PRD)

**Project:** ComplianceScan  
**SIH'26 Problem Statement:** 26034  
**Problem Statement Title:** Software System to check compliance of Packaged Commodities under Legal Metrology (Packaged Commodities) Rules, 2011 by scanning products, images and labels.  
**Document Version:** 2.0  
**Status:** Target product requirements with controlled one-day MVP boundary

---

# 1. Purpose

This Product Requirements Document defines the product intent, user problem, scope, functional requirements, workflow, safety boundaries, MVP objective, and future direction for ComplianceScan.

ComplianceScan is an inspection-assistance system intended to help authorized users analyze packaged-commodity labels/product evidence against a controlled subset of Legal Metrology requirements.

The product is designed around:

> **Scan → Understand → Determine Applicability → Validate → Prove with Evidence → Officer Verifies → Reviewer Decides → Report**

The system is not intended to replace statutory authority or human inspection judgment.

The central principle is:

> **AI finds → Evidence proves → Officer decides.**

---

# 2. SIH Problem Context

The SIH'26 problem statement asks for a software system that can check compliance of packaged commodities under the Legal Metrology (Packaged Commodities) Rules, 2011 by scanning products, images, and labels.

The intended solution therefore needs to support:

- product/image/label scanning
- mandatory declaration detection
- completeness and correctness assessment
- placement/readability-related analysis
- violation/finding summaries
- evidence
- reporting
- repository/history
- dashboard/search
- automated extraction and validation
- web/mobile-oriented access

ComplianceScan focuses the initial implementation on a reliable inspection-assistance vertical slice rather than attempting to implement the entire statutory/legal enforcement ecosystem.

---

# 3. Product Vision

ComplianceScan should reduce the manual effort required to inspect packaged-commodity declarations while preserving human authority and evidence traceability.

The desired experience is:

```text
Physical Package / Product Image
              ↓
       Upload / Capture
              ↓
          AI Analysis
              ↓
       Declaration Extraction
              ↓
         Applicability
              ↓
      Deterministic Validation
              ↓
      Evidence-Backed Findings
              ↓
      Inspector Verification
              ↓
       Reviewer Decision
              ↓
       Final Inspection Record
```

The product should make the reasoning chain visible rather than producing unexplained pass/fail labels.

---

# 4. Product Problem

Manual inspection can require an officer to:

- locate mandatory declarations
- read text from packaging
- compare declarations against applicable requirements
- determine whether a requirement applies
- identify potentially non-compliant observations
- collect supporting evidence
- document reasoning
- preserve inspection history

The product aims to assist these activities through automation while avoiding unsafe automation of legal authority.

---

# 5. Primary Product Users

## 5.1 Inspector

The Inspector prepares and verifies an inspection.

Responsibilities:

- create inspection
- provide context
- provide/capture evidence
- initiate analysis
- inspect extracted declarations
- correct extracted values
- add manual observations
- verify applicability
- verify findings
- supplement evidence where required
- submit inspection for independent review

The Inspector does not make the final system-level decision.

---

## 5.2 Reviewer

The Reviewer independently reviews submitted inspections.

Responsibilities:

- inspect evidence
- inspect extracted information
- inspect applicability
- inspect findings
- inspect audit/history
- confirm assessments
- correct/override assessments with reasons
- request additional evidence
- finalize the inspection

The Reviewer is responsible for the final workflow decision.

---

# 6. Human-in-the-Loop Principle

ComplianceScan is not designed around autonomous legal enforcement.

```text
AI
 ↓
Find / Extract / Interpret

System
 ↓
Validate / Apply Rules / Generate Evidence

Inspector
 ↓
Verify / Correct / Supplement

Reviewer
 ↓
Independently Decide / Finalize
```

The system must never represent an AI prediction as an automatically established legal violation.

Use:

> **Potential Non-Compliance**

rather than claiming that AI has conclusively established a statutory violation.

---

# 7. Product Scope Model

The project contains two intentional scopes.

## 7.1 Target System

The target product includes:

- inspection lifecycle
- evidence management
- OCR
- AI declaration understanding
- applicability engine
- compliance rules
- findings/evidence
- Inspector verification
- Reviewer workflow
- finalization
- reports
- repository/history
- search/retrieval
- dashboard
- Physical ↔ Online Verification

## 7.2 Current One-Day MVP

The one-day MVP implements one complete vertical slice:

```text
Input
  ↓
Evidence
  ↓
OCR
  ↓
AI Extraction
  ↓
Applicability
  ↓
Six Supported Checks
  ↓
Findings + Evidence
  ↓
Inspector Verification
  ↓
Result
  ↓
Persistent Deployment
```

Reviewer/finalization may be included where implementation time and stability allow, but must follow the target workflow rather than inventing a second incompatible workflow.

The MVP boundary is authoritative in:

> `MVP_BUILD_SCOPE.md`

---

# 8. MVP Objective

The objective of the one-day MVP is:

> **Demonstrate one reliable, end-to-end packaged-commodity inspection journey from evidence input through AI-assisted extraction, applicability, deterministic compliance assessment, evidence-backed findings, human verification, and persistent deployed output.**

Success is not measured by the number of screens, endpoints, database tables, or AI features.

Success is:

> **One complete journey that works reliably.**

---

# 9. Core MVP Checks

The MVP supports these six core declaration checks:

### 1. Manufacturer / Packer / Importer

Determine whether the applicable responsible-party declaration is observed and adequately represented.

### 2. Common / Generic Product Name

Determine whether the product has the required common/generic identification.

### 3. Net Quantity + Standard Unit

Determine whether quantity and unit are observed in the expected form.

### 4. Month / Year of Manufacture / Packing / Import

Determine whether the relevant date declaration is present and interpretable.

### 5. MRP Inclusive of All Taxes

Determine whether the MRP declaration is observed and whether the supported validation conditions are met.

### 6. Consumer Care Details

Determine whether consumer-care information is observed sufficiently for the supported scope.

---

# 10. Country of Origin

Country of Origin is applicability-driven.

The MVP does not treat it as universally applicable.

Conceptually:

```text
Imported = YES
      ↓
Country of Origin applicable

Imported = NO
      ↓
NOT_APPLICABLE

Imported = UNKNOWN
      ↓
REVIEW / INCOMPLETE as appropriate
```

`NOT_APPLICABLE` is not the same as `PASS`.

---

# 11. Deliberately Deferred MVP Requirements

The following are intentionally outside the one-day core scope unless explicitly approved:

- Unit Sale Price
- broad category-specific rules
- universal exemption handling
- full legal rule management
- dynamic regulatory-update pipeline
- universal font-size legal verdict
- universal packaging-placement legal verification
- internet-wide product crawling
- full Physical ↔ Online Verification
- broad enforcement/follow-up workflow
- complex analytics infrastructure
- unnecessary administrative workflows
- speculative microservices

This is a scope decision, not a claim that these capabilities are unimportant.

---

# 12. Visual Analysis Boundary

The system may provide visual analysis for:

- readability
- visibility
- image quality
- placement/evidence coverage
- font-size warning/assessment

However, the MVP must not present approximate photo-based measurements as definitive universal legal determinations where scale/reference information is insufficient.

The UI should distinguish:

```text
Visual Observation
       ≠
Definitive Legal Conclusion
```

---

# 13. Result Vocabulary

ComplianceScan uses:

```text
PASS
POTENTIAL_NON_COMPLIANCE
REQUIRES_REVIEW
NOT_APPLICABLE
INCOMPLETE
PROCESSING_FAILED
```

These results must remain semantically distinct.

Important rules:

```text
NOT_APPLICABLE ≠ PASS
INCOMPLETE ≠ POTENTIAL_NON_COMPLIANCE
PROCESSING_FAILED ≠ POTENTIAL_NON_COMPLIANCE
NOT_OBSERVED ≠ proven absence
UNREADABLE ≠ missing
CONFLICTING → REQUIRES_REVIEW where material
```

---

# 14. AI/OCR Product Boundary

Current selected OCR:

> **PaddleOCR**

Current selected AI model:

> **Gemini 2.5 Flash**

The architecture is:

```text
Package Image
      ↓
Image Processing / CV
      ↓
PaddleOCR
      ↓
OCR Text + Bounding Boxes + Confidence
      ↓
Gemini 2.5 Flash
      ↓
Structured Declaration Data
      ↓
Backend Validation
      ↓
Applicability Engine
      ↓
Deterministic Compliance Rules
      ↓
Findings + Evidence
      ↓
Inspector Verification
      ↓
Reviewer Decision
```

Puter is explicitly set aside for the current architecture.

---

# 15. OCR Responsibility

PaddleOCR is responsible for:

- text detection
- text recognition
- bounding boxes
- OCR confidence
- source-image association

PaddleOCR does not determine legal compliance.

---

# 16. AI Responsibility

Gemini 2.5 Flash is primarily responsible for:

- declaration extraction
- semantic interpretation
- normalization
- context mapping
- conflict detection
- uncertainty preservation

AI must not:

- make the final legal decision
- invent unsupported declarations
- silently resolve conflicting values
- modify original evidence
- change compliance rules
- finalize inspections
- alter finalized history

---

# 17. AI Observation States

Each accepted declaration should preserve an observation status:

```text
OBSERVED
NOT_OBSERVED
UNCERTAIN
UNREADABLE
CONFLICTING
```

These states allow the product to avoid treating uncertainty as certainty.

---

# 18. Confidence Separation

The product must keep these concepts separate:

```text
OCR Confidence
       ≠
AI Extraction Confidence
       ≠
Evidence Sufficiency
       ≠
Compliance Result
```

A high OCR confidence does not automatically mean a declaration is legally compliant.

---

# 19. No-Guessing Principle

ComplianceScan must not invent missing information.

Examples:

```text
No visible declaration
      ↓
Do not fabricate one

Ambiguous text
      ↓
UNCERTAIN

Conflicting values
      ↓
CONFLICTING / REVIEW

Unreadable region
      ↓
UNREADABLE
```

The system should preserve uncertainty and route the case appropriately.

---

# 20. Applicability-First Product Behavior

The product must determine whether a supported requirement applies before treating it as a compliance failure.

Conceptually:

```text
Inspection Context
       ↓
Applicability
       ↓
Applicable Requirements
       ↓
Compliance Assessment
```

This prevents irrelevant requirements from becoming false findings.

---

# 21. Evidence Model

Evidence is central to the product.

Evidence categories:

```text
PRIMARY
SUPPLEMENTAL
DERIVED
```

### Primary Evidence

Original package images captured/provided for the inspection.

### Supplemental Evidence

Additional evidence supplied after the initial evidence set.

### Derived Evidence

OCR regions, crops, highlights, and similar artifacts generated from original evidence.

Audit/decision records are not package evidence.

---

# 22. Evidence Integrity

Each accepted original evidence item should have:

- Evidence ID
- storage reference
- timestamp
- source/provenance
- SHA-256 hash
- inspection association
- immutable original

Hashing establishes tamper-evident integrity/change detection.

It does not establish truth or authenticity.

---

# 23. Adaptive Evidence

The product should not impose an arbitrary fixed number of images.

Evidence requirements should depend on:

- package complexity
- declaration coverage
- image quality
- evidence sufficiency
- unresolved findings

Conceptually:

```text
Evidence Coverage
      ↓
Sufficient?
   ├── YES → Continue
   └── NO  → Inspector Verification / Evidence Request
```

The MVP may keep this behavior simple while preserving the principle.

---

# 24. Evidence Request Model

In the target workflow, a Reviewer may request additional evidence.

Each request should have an identifier such as:

```text
ER-00017
```

The request identifies:

- fact/condition to establish
- reason
- requested information/evidence

It is not an automatic recapture command.

The Inspector may:

- provide supplemental evidence
- add a manual observation
- state that the fact cannot be established

If new evidence affects analysis, affected information is reprocessed before resubmission.

---

# 25. Inspection Workflow

The target operational workflow is:

```text
1. Inspection Trigger
2. Inspection Context
3. Product/Package Selection
4. Evidence Capture
5. Evidence Integrity
6. Image Quality
7. AI-Assisted Observation
8. Declaration Understanding
9. Applicability
10. Compliance Assessment
11. Evidence Sufficiency
12. Inspector Verification
13. Submit for Review
14. Reviewer Audit & History
15. Inspection Detail + Audit Timeline
16. Reviewer Decision
17. Finalization & Record
18. Final Outputs
19. Authorized Follow-up — outside MVP
```

The one-day MVP uses the controlled subset required for the complete vertical slice.

---

# 26. Inspector Workflow

```text
Create Inspection
      ↓
Provide Context
      ↓
Add Evidence
      ↓
Start Analysis
      ↓
Review OCR / AI Output
      ↓
Correct Information if Required
      ↓
Verify Applicability
      ↓
Review Findings
      ↓
Add Observation/Evidence if Required
      ↓
Verify
      ↓
Submit
```

The Inspector is not the final decision authority.

---

# 27. Reviewer Workflow

```text
Receive Submitted Inspection
          ↓
Inspect Evidence
          ↓
Inspect OCR / Declarations
          ↓
Inspect Applicability
          ↓
Inspect Findings
          ↓
Inspect History
          ↓
Confirm / Correct / Override
          ↓
Request Evidence if Needed
          ↓
Final Decision
          ↓
Finalize
```

Reviewer corrections/overrides require a reason.

---

# 28. Submission Boundary

Before submission:

```text
Inspector controls working record
```

After submission:

```text
Reviewer controls review
```

If the Reviewer requests evidence:

```text
Reviewer
   ↓
Evidence Request
   ↓
Inspector supplements/corrects
   ↓
Resubmit
   ↓
Reviewer
```

After finalization:

```text
Read-only historical record
```

---

# 29. Correction Behavior

The product must preserve the invariant:

> **Upstream correction → invalidate affected downstream state → recompute → preserve prior state/history → audit transition.**

Example:

```text
AI extracts MRP = ₹199
        ↓
Inspector verifies package = ₹179
        ↓
Old value preserved
        ↓
MRP assessment invalidated
        ↓
Recompute using ₹179
        ↓
New finding/result
        ↓
Correction audited
```

The UI must not give the impression that changing a field automatically changes every downstream result unless the backend has actually recomputed it.

---

# 30. Reviewer Override Behavior

A Reviewer may correct/override an assessment.

The system must preserve:

```text
System Assessment
      +
Reviewer Decision
      +
Reason
      +
Actor
      +
Timestamp
```

The Reviewer does not erase the original system assessment.

---

# 31. Finalization

Finalization is controlled by the Reviewer.

The backend validates:

- Reviewer authorization
- lifecycle state
- required data
- evidence references
- rule snapshot
- blocking issues
- audit information

Then it creates an atomic final snapshot.

Conceptually:

```text
Validate
   ↓
Final Snapshot
   ↓
Final Decision
   ↓
Audit
   ↓
FINALIZED
```

---

# 32. Finalized Record

A finalized inspection becomes a protected historical record.

It should preserve/refer to:

- inspection context
- evidence
- evidence hashes
- OCR
- declarations
- applicability
- assessments
- findings
- corrections
- verification
- Reviewer decisions
- rule snapshot/version
- processing provenance
- audit references
- final decision

Normal workflow must not mutate finalized records.

---

# 33. Report Behavior

Final reports should be generated from the finalized snapshot.

```text
Final Snapshot
      ↓
Report
```

If report generation fails:

```text
FINALIZED
+
REPORT FAILURE
```

The inspection remains finalized.

Report generation failure must not roll back the historical decision.

---

# 34. Product Architecture

The target architecture contains 25 logical components:

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

These are logical boundaries.

They do not imply 25 microservices.

---

# 35. Current MVP Architecture Subset

The one-day MVP should focus on:

```text
Web Application
      ↓
Backend/API
      ↓
Inspection Management
      ↓
Evidence Management
      ↓
Image Processing
      ↓
PaddleOCR
      ↓
Gemini 2.5 Flash
      ↓
Declaration Validation
      ↓
Applicability
      ↓
Compliance Rules / Engine
      ↓
Findings + Evidence
      ↓
Inspector Verification
      ↓
Persistent Storage
```

Reviewer/finalization can be included when safely achievable.

---

# 36. Deployment Requirement

The MVP must be deployable for judges/users to access after implementation.

Therefore:

```text
Frontend
    ↓
Hosted Backend
    ↓
Persistent Cloud-Capable Database
    +
Persistent Object/File Storage
    +
AI/OCR Dependencies
```

Local-only storage is not sufficient for the deployed MVP.

The exact providers are intentionally not locked yet.

---

# 37. Non-Functional Requirements

## 37.1 Reliability

The system should fail safely.

Technical failures must not become false compliance findings.

## 37.2 Explainability

Findings should explain:

- what requirement was evaluated
- what was observed
- why the result occurred
- which rule was used
- what evidence supports the finding

## 37.3 Auditability

Material changes should preserve:

- actor
- timestamp
- old/new values
- reason
- state transitions
- evidence references

## 37.4 Security

The backend must enforce:

- authentication
- authorization
- protected evidence access
- safe uploads
- server-side secrets
- protected finalization

## 37.5 Persistence

The deployed system must survive application restarts without losing inspection data or original evidence.

---

# 38. Security Requirements

The product must:

- enforce backend RBAC
- validate all input
- protect evidence access
- validate file type/size/decode
- calculate evidence hashes server-side
- keep provider secrets server-side
- prevent unauthorized state transitions
- protect finalized records
- preserve audit history
- avoid exposing internal storage paths unnecessarily

The frontend is never the security authority.

---

# 39. Performance Requirements

For the one-day MVP, prioritize:

1. end-to-end reliability
2. correct processing
3. persistent deployment
4. clear user feedback
5. reasonable processing time

Do not sacrifice correctness to optimize prematurely for large-scale workloads.

---

# 40. Error Handling Product Requirements

The product must distinguish:

```text
Input Error
Processing Error
OCR Error
AI Error
Validation Error
Applicability Uncertainty
Evidence Insufficiency
Compliance Result
Reviewer Decision
```

Examples:

```text
Gemini unavailable
    → PROCESSING_FAILED

Image unreadable
    → UNREADABLE / INCOMPLETE as appropriate

Conflicting declarations
    → REQUIRES_REVIEW

Potential rule mismatch
    → POTENTIAL_NON_COMPLIANCE
```

---

# 41. Accessibility / Usability

The product should make important status information understandable.

The interface should clearly display:

- processing state
- declaration status
- confidence/uncertainty where useful
- applicable requirements
- findings
- evidence
- Inspector verification state
- Reviewer state
- finalization state

Avoid presenting confidence as a legal probability.

---

# 42. Evidence-Centered UI

For a finding, the user should be able to understand:

```text
Finding
   ↓
Requirement
   ↓
Reason
   ↓
Evidence
   ↓
Relevant image region
```

This should reduce unexplained AI output.

---

# 43. Product State Safety

The product must not allow users to perform operations that are invalid for the current lifecycle state.

Examples:

```text
FINALIZED
   ↓
Edit button hidden/disabled
   +
Backend rejects mutation
```

Both UI and backend should behave consistently.

Backend enforcement is authoritative.

---

# 44. Data Integrity Product Requirements

The product must preserve:

```text
Original Evidence
        ↓
OCR
        ↓
AI Observation
        ↓
Inspector Correction
        ↓
Applicability
        ↓
Assessment
        ↓
Finding
        ↓
Reviewer Decision
        ↓
Final Snapshot
```

This chain should remain traceable.

---

# 45. Target Physical ↔ Online Verification

A future target capability may compare:

```text
Physical Package
      ↕
Online Listing
```

Possible comparisons:

- product identity
- manufacturer
- MRP
- quantity
- consumer care
- other supported declarations

Mismatch should be represented as:

> **Cross-Channel Inconsistency**

not automatically as a legal violation.

Internet-wide crawling is outside the one-day MVP.

---

# 46. Repository and History

The target system should support inspection history.

Users should eventually be able to:

- search inspections
- filter by state/result/date
- inspect prior evidence
- inspect findings
- inspect audit history
- retrieve finalized records

The one-day MVP only needs the minimum persistence/retrieval required for the vertical slice and demonstration.

---

# 47. Dashboard

The target dashboard may provide:

- inspection counts
- result distribution
- review backlog
- processing failures
- common findings
- completion metrics

Dashboard analytics are not a prerequisite for proving the core one-day inspection journey.

---

# 48. Product Success Criteria — One-Day MVP

The MVP is successful when a representative user can:

```text
1. Start an inspection
2. Provide package evidence
3. Process the evidence
4. Obtain OCR
5. Extract declarations with AI
6. Preserve uncertainty
7. Determine applicability
8. Evaluate six supported checks
9. See evidence-backed findings
10. Correct/verify information
11. Produce a meaningful result
12. Persist the inspection in the deployed environment
13. Demonstrate the complete workflow to a judge
```

If Reviewer/finalization is implemented:

```text
14. Submit
15. Review
16. Request evidence when needed
17. Decide
18. Finalize
19. Retrieve final record/report
```

---

# 49. Acceptance Criteria

## AC-01 — Inspection Creation

Given an authorized Inspector, the system can create an inspection with a unique identifier.

## AC-02 — Evidence

Given valid package evidence, the system stores it persistently with an Evidence ID and integrity metadata.

## AC-03 — OCR

Given representative package images, PaddleOCR produces text and source regions where readable.

## AC-04 — AI Extraction

Given OCR observations, Gemini produces schema-valid declaration observations.

## AC-05 — No Guessing

Ambiguous or unsupported information is not silently fabricated.

## AC-06 — Applicability

Supported applicability conditions are evaluated before compliance assessment.

## AC-07 — Six Checks

The system evaluates the six supported declaration requirements.

## AC-08 — Evidence-Backed Findings

Findings retain requirement, reason, rule reference, and evidence provenance.

## AC-09 — Human Verification

Inspector can review and correct extracted information.

## AC-10 — Recalculation

Material upstream corrections invalidate and recompute affected downstream results.

## AC-11 — Safe Failure

Technical processing failures are not reported as compliance failures.

## AC-12 — Persistence

Inspection data remains available after application restart/deployment lifecycle events.

## AC-13 — Reviewer Independence

Where Reviewer workflow is implemented, the Reviewer can independently review and decide.

## AC-14 — Finalization

Where finalization is implemented, only the authorized Reviewer workflow can finalize.

## AC-15 — Historical Integrity

Finalized records cannot be silently modified.

---

# 50. Out of Scope for the One-Day MVP

Explicitly out of scope unless separately approved:

```text
Full statutory enforcement workflow
Universal legal coverage
Dynamic legal-rule ingestion/update system
All category-specific exceptions
Unit Sale Price
Full online marketplace crawling
Universal package-layout compliance verification
Definitive font-size measurement without reliable scale
Advanced analytics platform
Large-scale distributed architecture
Complex administrative RBAC
Full rule-management UI
Broad external integrations
```

---

# 51. Risks

## Risk 1 — AI Hallucination

Mitigation:

- structured schema
- source references
- validation
- uncertainty states
- no-guessing rule
- human verification

## Risk 2 — OCR Errors

Mitigation:

- confidence
- bounding boxes
- image preprocessing
- Inspector correction
- preserved original evidence

## Risk 3 — Legal Overclaiming

Mitigation:

- controlled rules
- applicability-first evaluation
- Potential Non-Compliance terminology
- human final authority

## Risk 4 — Scope Explosion

Mitigation:

- `MVP_BUILD_SCOPE.md`
- vertical-slice principle
- explicit deferred features
- approval before material expansion

## Risk 5 — Local-Only Deployment

Mitigation:

- persistent cloud-capable database
- persistent object/file storage
- deployment validation before release

## Risk 6 — Stale Results After Correction

Mitigation:

- global invalidation/recomputation invariant
- backend-controlled transitions
- correction history

## Risk 7 — Historical Mutation

Mitigation:

- final snapshots
- immutable evidence
- audit events
- protected finalized records

---

# 52. Product Constraints

The one-day MVP is constrained by:

- limited implementation time
- limited testing time
- external AI dependency
- representative-image variability
- legal-rule complexity
- deployment requirements
- need for judge-accessible demonstration

Therefore, the product prioritizes:

```text
Reliability
>
Traceability
>
Correctness
>
Demonstrability
>
Feature Count
```

---

# 53. Scope Governance

No feature should enter the MVP merely because it exists in the target architecture.

A proposed addition should answer:

1. Does it support the complete vertical slice?
2. Is it required by the SIH problem statement for the demonstration?
3. Can it be implemented and tested safely within the available time?
4. Does it introduce new dependencies or failure modes?
5. Has it been explicitly approved?

If not:

> Defer it.

---

# 54. Documentation Authority

The project documentation has specialized authority:

| Document | Authority |
|---|---|
| `README.md` | Project orientation |
| `MVP_BUILD_SCOPE.md` | Current MVP boundary |
| `PROJECT_STATE.md` | Actual implementation state |
| `PHASE.md` | Execution sequence |
| `AGENT_ENGINEERING_PROTOCOL.md` | Engineering-agent behavior |
| `01_PRD.md` | Product requirements and intent |
| `02_TRD.md` | Technical requirements/constraints |
| `03_Architecture.md` | System architecture |
| `04_Design.md` | UI/UX design |
| `05_Domain_Specification.md` | Domain semantics |
| `06_Compliance_Rules.md` | Compliance rules |
| `07_State_Machine.md` | Lifecycle/state semantics |
| `08_API_Specification.md` | API contract |
| `09_Database_Specification.md` | Persistence model |
| `10_Error_Handling.md` | Error/recovery semantics |
| `11_Testing_and_Release_Gate.md` | Quality/release criteria |

A specialized document should not be silently contradicted by a general document.

---

# 55. Current Implementation Status

This PRD defines intended product behavior.

It does not claim that every target requirement has already been implemented.

Actual status must be recorded in:

> `PROJECT_STATE.md`

The next implementation step is:

> **Phase 0 — repository/implementation audit**

The agent must inspect the actual repository before making implementation claims.

---

# 56. Phase Alignment

The product execution sequence is:

```text
PHASE 0
Repository / Implementation Audit
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
End-to-End QA + Basic Output
        ↓
PHASE 9
Deployment + Demonstration Readiness
```

The goal is to reach a complete vertical slice, not to implement every target subsystem.

---

# 57. Product Definition of Done

The one-day MVP is done when:

```text
[✓] Complete user journey exists
[✓] Representative evidence can be processed
[✓] OCR works
[✓] AI extraction works with structured validation
[✓] Applicability works for supported scope
[✓] Six checks work
[✓] Findings are explainable and evidence-linked
[✓] Inspector can verify/correct
[✓] Corrections recompute affected results
[✓] Technical failures are safely represented
[✓] Data persists in deployed environment
[✓] End-to-end QA passes
[✓] Judge demonstration works
```

These checkboxes become release criteria only after actual verification.

---

# 58. Final Product Statement

ComplianceScan is an:

> **AI-assisted packaged-commodity inspection and compliance-assistance system that extracts declarations from package evidence, determines applicability, evaluates a controlled set of Legal Metrology requirements, generates evidence-backed potential findings, and keeps authorized human officers in control of verification and final decisions.**

The current one-day MVP intentionally focuses on:

> **One complete, reliable, deployable inspection journey.**

The governing product principle is:

> **AI finds → Evidence proves → Inspector verifies → Reviewer decides.**

And the governing scope principle is:

> **ONE COMPLETE USER JOURNEY > MANY PARTIAL SUBSYSTEMS.**
