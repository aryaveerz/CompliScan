# CompliScan LM — MVP Implementation Specification

**Project:** CompliScan LM  
**SIH Problem Statement:** PS ID 26034  
**Title:** Software System to check compliance of Packaged Commodities under Legal Metrology (Packaged Commodities) Rules, 2011 by scanning products, images and labels.  
**Document Type:** MVP Implementation Specification  
**Status:** APPROVED — IMPLEMENTATION SOURCE OF TRUTH FOR MVP  
**Date:** 2026-09-16

---

## 1. PURPOSE OF THIS DOCUMENT

This document defines exactly what Antigravity should build for the **first real, demonstrable version of CompliScan LM**.

This document is intentionally more detailed than a normal feature list. It explains:

- what the product is,
- who uses it,
- what happens during a real inspection,
- what information moves through the system,
- where AI is used,
- where deterministic rules are used,
- where humans make decisions,
- what the MVP must contain,
- what the MVP must not contain,
- what may be simplified,
- what must never be compromised,
- how the implementation should be developed,
- and how completion will be verified.

The immediate objective is NOT to build the complete long-term CompliScan LM platform.

The immediate objective is:

> **Build a small but real end-to-end inspection system that can demonstrate the complete core workflow from package image to reviewed and finalized compliance report.**

A working, coherent MVP is more valuable than a partially implemented enterprise architecture.

---

# 2. THE PRODUCT IN ONE SENTENCE

CompliScan LM is an inspection-assistance system that uses package images, OCR, structured AI extraction, applicability logic, and deterministic compliance rules to help an Inspector identify potentially relevant declaration issues, verify the observations, and submit the inspection to an independent Reviewer for final decision and reporting.

---

# 3. THE CORE PRINCIPLE

The system follows:

> **AI finds → Evidence proves → Officer decides.**

This means:

- AI assists observation and extraction.
- Evidence provides the basis for inspection findings.
- Deterministic rules evaluate defined requirements.
- The Inspector verifies what the system observed.
- The Reviewer independently makes the final decision.
- The system records the process and produces the final report.

The AI must never be presented as an autonomous legal authority.

---

# 4. WHAT THE MVP MUST DEMONSTRATE

The MVP must tell one complete story:

```text
                    COMPLISCAN LM MVP

                         INSPECTOR
                             │
                             ▼
                    CREATE INSPECTION
                             │
                             ▼
                     CAPTURE EVIDENCE
                             │
                             ▼
                       PACKAGE IMAGE
                             │
                             ▼
                       IMAGE QUALITY
                             │
                             ▼
                          PADDLEOCR
                             │
                             ▼
                      OCR OBSERVATIONS
                             │
                             ▼
                    GEMINI 2.5 FLASH
                             │
                             ▼
                  STRUCTURED EXTRACTION
                             │
                             ▼
                  FIELD-LEVEL VALIDATION
                             │
                             ▼
                      APPLICABILITY
                             │
                             ▼
                 DETERMINISTIC RULE ENGINE
                             │
                             ▼
                        FINDINGS
                             │
                             ▼
                 INSPECTOR VERIFICATION
                             │
                             ▼
                     SUBMIT FOR REVIEW
                             │
                             ▼
                         REVIEWER
                             │
             ┌───────────────┼────────────────┐
             ▼               ▼                ▼
          CONFIRM         OVERRIDE       REQUEST REVISION/
                                            EVIDENCE
             │               │                │
             └───────────────┴────────────────┘
                             │
                             ▼
                         FINALIZE
                             │
                             ▼
                    FINAL SNAPSHOT
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
              PDF REPORT              HISTORY
```

If this complete path works, the MVP has achieved its primary purpose.

---

# 5. WHAT THIS MVP IS NOT

The MVP is NOT intended to be:

- a universal Legal Metrology compliance engine,
- an autonomous legal enforcement system,
- a replacement for an authorized officer,
- a complete implementation of every Packaged Commodities rule,
- a complete category-specific regulatory platform,
- a dynamic legal-regulation update platform,
- a generic AI chatbot,
- an enterprise analytics platform,
- a multi-service distributed system,
- a mobile-native application,
- a production-scale national inspection platform.

These may be future directions.

They are not reasons to delay the first working MVP.

---

# 6. IMPLEMENTATION STRATEGY

The implementation should be incremental.

Do not build everything at once.

Use this progression:

```text
PHASE 0
Repository Understanding
        │
        ▼
PHASE 1
Foundation + Inspection + Evidence
        │
        ▼
PHASE 2
Real OCR + AI Extraction
        │
        ▼
PHASE 3
Applicability + Compliance Engine
        │
        ▼
PHASE 4
Inspector Verification + Reviewer
        │
        ▼
PHASE 5
Finalization + PDF + History
        │
        ▼
PHASE 6
Hardening
```

The critical rule is:

> **Do not spend substantial time hardening infrastructure before the core inspection pipeline works.**

---

# 7. MVP PRIORITY LEVELS

## TIER 1 — DEMONSTRATION CRITICAL

These must work:

- authentication,
- Inspector role,
- Reviewer role,
- inspection creation,
- evidence upload,
- package image display,
- OCR,
- Gemini extraction,
- field validation,
- applicability,
- six compliance checks,
- findings,
- Inspector verification,
- Inspector correction,
- Reviewer workflow,
- final decision,
- finalization,
- PDF report,
- basic history.

## TIER 2 — INTEGRITY AND SECURITY

Implement where practical without blocking Tier 1:

- SHA-256 evidence hash,
- stronger evidence immutability,
- append-only audit,
- immutable final snapshot,
- backend state-transition protection,
- stronger access control,
- robust validation.

## TIER 3 — PRODUCTION HARDENING

These may be implemented after the complete workflow works:

- advanced PostgreSQL queue recovery,
- sophisticated lease management,
- advanced idempotency,
- extensive worker recovery,
- database-level immutability triggers,
- extensive observability,
- load testing,
- advanced deployment hardening.

The existence of Tier 3 does not mean Tier 1 should wait for it.

---

# 8. APPROVED TECHNOLOGY STACK

Use:

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS

### Backend

- Python 3.11+
- FastAPI

### Database

- PostgreSQL
- Supabase PostgreSQL

### Platform

- Supabase

Supabase provides:

- PostgreSQL,
- Storage,
- Authentication.

FastAPI remains authoritative for the application domain.

### ORM

- SQLAlchemy

### Migrations

- Alembic

### OCR

- PaddleOCR

### LLM

- Gemini 2.5 Flash

### Processing

- asynchronous processing where practical

### Containerization

- Docker

---

# 9. LONG-TERM ARCHITECTURE VS MVP IMPLEMENTATION

The approved long-term architecture is:

```text
React
  ↓
FastAPI
  ↓
Supabase PostgreSQL
  ↑
Worker
  ├── PaddleOCR
  └── Gemini
```

The logical components are:

1. Frontend Web Client
2. API Gateway & Authentication
3. Inspection Orchestrator & State Machine
4. Evidence Store
5. Perception Engine
6. Structured Extractor
7. Applicability & Deterministic Rule Engine
8. Report & Audit Store

The MVP should remain compatible with this architecture.

However, implementation should not become blocked by production-level infrastructure.

The architecture is the target.

The MVP is the first working implementation of the target.

---

# 10. REPOSITORY-FIRST RULE

Before writing significant code, inspect the existing repository.

Determine:

- existing project structure,
- existing frontend,
- existing backend,
- existing database code,
- existing OCR implementation,
- existing Gemini integration,
- existing legal references,
- existing tests,
- existing Docker configuration,
- existing environment configuration,
- existing documentation.

Classify existing work:

```text
A — Correct and reusable
B — Correct but requires adaptation
C — Conflicts with approved design
D — Dead/unused
E — Unknown
```

Do not delete working code merely to create a cleaner-looking structure.

Reuse compatible work.

---

# 11. USERS AND REAL-WORLD SCENARIO

The MVP models two operational actors.

## Inspector

The Inspector performs the preliminary inspection.

The Inspector:

1. logs in,
2. creates an inspection,
3. captures/uploads package evidence,
4. starts analysis,
5. reviews OCR and extracted information,
6. corrects extraction errors,
7. reviews applicability,
8. reviews findings,
9. verifies the observations,
10. submits the inspection for independent review.

## Reviewer

The Reviewer performs independent review.

The Reviewer:

1. opens submitted inspection,
2. examines original evidence,
3. examines OCR/extracted declarations,
4. checks applicability,
5. reviews system findings,
6. confirms or overrides findings,
7. requests additional evidence or revision if necessary,
8. finalizes the inspection.

The Inspector and Reviewer must be different users for the same inspection.

---

# 12. COMPLETE REAL-WORLD SCENARIO

The following scenario is the mental model Antigravity should use while implementing the system.

## Step 1 — Inspector starts an inspection

An Inspector encounters a packaged commodity that needs to be inspected.

They log into CompliScan LM.

They create:

```text
Inspection:
INS-00001
```

The system records:

- inspection ID,
- Inspector,
- creation timestamp,
- initial status.

The inspection is initially:

```text
DRAFT
```

---

## Step 2 — Inspector captures package evidence

The Inspector photographs or uploads the package label.

The original image is stored as evidence.

Example:

```text
Evidence ID:
IMG-00042
```

The image is associated with:

```text
INS-00001
```

The system must preserve the original image.

The original image is not modified by OCR or AI.

---

## Step 3 — Evidence is checked

The system verifies:

- image can be decoded,
- supported file type,
- reasonable file size,
- image is usable.

The system may report:

```text
Image Quality:
ACCEPTABLE
```

or:

```text
DEGRADED
```

or:

```text
UNUSABLE
```

A poor image is NOT automatically a legal violation.

If the image is unusable, the workflow should guide the Inspector toward better evidence or an incomplete/review state.

---

# 13. OCR STAGE

Once evidence is accepted, CompliScan LM processes the image using PaddleOCR.

PaddleOCR extracts visible text.

Example OCR observations:

```text
"ABC Foods Pvt. Ltd."
"Premium Rice"
"Net Qty 5 kg"
"MRP ₹450"
"Packed: 08/2026"
"Customer Care: 1800-XXX-XXXX"
```

Each observation should retain:

- text,
- OCR confidence,
- bounding box,
- source Evidence ID.

Example:

```text
OCR Token:
"MRP ₹450"

Confidence:
0.94

Bounding Box:
(x1, y1, x2, y2)

Evidence:
IMG-00042
```

OCR does not determine compliance.

---

# 14. GEMINI EXTRACTION STAGE

Gemini receives the OCR observations and relevant evidence context.

Its task is to structure the information.

For example:

```text
Manufacturer:
ABC Foods Pvt. Ltd.

Product Name:
Premium Rice

Net Quantity:
5

Unit:
kg

Packing Month:
08

Packing Year:
2026

MRP:
450

Currency:
INR

Consumer Care:
1800-XXX-XXXX
```

Gemini is performing semantic extraction.

It is NOT performing legal evaluation.

---

# 15. FIELD VALIDATION

The backend validates Gemini's output.

Example:

```text
MRP:
{
    value: 450,
    currency: INR
}
```

The backend checks:

- structure,
- types,
- valid representations,
- source references,
- uncertainty,
- conflicts.

If Gemini produces something unsupported:

```text
MRP = "probably 450"
```

the system should not blindly accept it as a verified number.

If OCR is:

```text
₹4?0
```

and Gemini says:

```text
450
```

the system should preserve uncertainty unless evidence supports the value.

No guessing.

---

# 16. STRUCTURED OBSERVATIONS ARE NOT LEGAL FINDINGS

This distinction is mandatory.

```text
OCR observation
        ↓
AI structured observation
        ↓
validated observation
        ↓
applicability
        ↓
deterministic rule evaluation
        ↓
finding
```

Do not collapse these layers.

---

# 17. APPLICABILITY STAGE

Before checking compliance, determine which requirements apply.

The system considers available context such as:

- imported/non-imported status,
- product context,
- relevant evidence,
- other MVP applicability information.

Example:

```text
Imported = YES

Therefore:
Country of Origin requirement = APPLICABLE
```

If:

```text
Imported = NO

Country of Origin requirement = NOT_APPLICABLE
```

If:

```text
Imported = UNKNOWN
```

the system should not guess.

It may require review or remain incomplete depending on available evidence and workflow.

Important:

```text
NOT_APPLICABLE ≠ PASS
```

---

# 18. COMPLIANCE EVALUATION

The deterministic rule engine evaluates the applicable requirements.

The MVP checks six core domains.

---

# 19. CHECK 1 — MANUFACTURER / PACKER / IMPORTER

The system evaluates whether the applicable identity/address declaration is sufficiently observed.

The finding should indicate:

- what was observed,
- which identity field it relates to,
- whether the applicable requirement appears satisfied,
- supporting evidence.

Do not make an unsupported legal conclusion from an uncertain OCR result.

---

# 20. CHECK 2 — COMMON / GENERIC PRODUCT NAME

The system evaluates whether the common/generic commodity name is observed.

Example:

```text
Product:
"Premium Rice"
```

The rule engine evaluates the observation against the controlled MVP requirement.

---

# 21. CHECK 3 — NET QUANTITY + STANDARD UNIT

The system evaluates:

- quantity,
- unit,
- expected representation.

Example:

```text
5 kg
```

The rule engine should use structured values rather than attempting to reason from raw text.

---

# 22. CHECK 4 — MONTH / YEAR

The system evaluates relevant manufacture/packing/import month/year information.

Example:

```text
Packed:
08/2026
```

The system should preserve the source evidence.

---

# 23. CHECK 5 — MRP INCLUSIVE OF ALL TAXES

The system evaluates the MRP declaration using the controlled MVP rule representation.

Example:

```text
MRP:
₹450
```

The system must not invent a value.

---

# 24. CHECK 6 — CONSUMER CARE DETAILS

The system evaluates the required consumer-care information using the controlled MVP rule representation.

Example:

```text
Customer Care:
1800-XXX-XXXX
```

The exact legal interpretation must come from the controlled project rule snapshot.

Do not invent legal requirements.

---

# 25. COUNTRY OF ORIGIN

Country of Origin is NOT a universal seventh compliance check.

It is represented through applicability.

For imported goods:

```text
COO:
APPLICABLE
```

For non-imported goods:

```text
COO:
NOT_APPLICABLE
```

For unknown context:

```text
REQUIRES_REVIEW / INCOMPLETE
```

depending on the available information and workflow.

---

# 26. USP

USP is completely excluded from this MVP.

Do not implement:

- USP UI,
- USP database field,
- USP API,
- USP rule,
- USP finding,
- USP test.

---

# 27. FINDING MODEL

A finding should answer:

```text
WHAT?
WHY?
WHERE?
BASED ON WHAT?
```

Example:

```text
Finding:
FND-00012

Check:
MRP

Result:
POTENTIAL_NON_COMPLIANCE

Reason:
Observed declaration does not satisfy the controlled MVP
requirement.

Evidence:
IMG-00042

Source:
OCR/Declaration reference
```

The exact wording can vary, but traceability must remain.

---

# 28. RESULT VOCABULARY

Use exactly:

```text
PASS
POTENTIAL_NON_COMPLIANCE
REQUIRES_REVIEW
NOT_APPLICABLE
INCOMPLETE
PROCESSING_FAILED
```

Semantics:

### PASS

The applicable requirement appears satisfied based on available verified information.

### POTENTIAL_NON_COMPLIANCE

Available evidence supports a possible failure of an applicable requirement.

Use "potential" because the system assists the authorized human decision process.

### REQUIRES_REVIEW

Information is uncertain, conflicting, ambiguous, or insufficient for a reliable determination.

### NOT_APPLICABLE

The requirement does not apply.

### INCOMPLETE

Evidence/information is insufficient to complete the assessment.

### PROCESSING_FAILED

Technical processing failed.

Critical distinctions:

```text
PROCESSING_FAILED
    ≠
POTENTIAL_NON_COMPLIANCE

INCOMPLETE
    ≠
POTENTIAL_NON_COMPLIANCE

NOT_APPLICABLE
    ≠
PASS
```

---

# 29. INSPECTOR VERIFICATION

The system presents the analysis to the Inspector.

The Inspector can see:

- original image,
- OCR,
- extracted declarations,
- applicability,
- findings,
- evidence references,
- uncertainty.

The Inspector can correct observations.

Example:

System extracted:

```text
MRP = ₹20
```

Inspector sees the package image and recognizes:

```text
MRP = ₹120
```

The Inspector corrects it.

The correction must preserve:

```text
OLD:
₹20

NEW:
₹120

REASON:
OCR misread printed value.

EVIDENCE:
IMG-00042

ACTOR:
Inspector

TIMESTAMP:
System recorded
```

The original observation must remain recoverable.

---

# 30. CORRECTION AND RECOMPUTATION

A correction must not silently leave stale findings.

Flow:

```text
Inspector Correction
        ↓
Validate Permission
        ↓
Record Old Value
        ↓
Record New Value
        ↓
Record Reason
        ↓
Record Evidence
        ↓
Invalidate Affected Evaluation
        ↓
Recompute
        ↓
Require Re-verification
```

Conservative invalidation is acceptable for MVP.

Do not build an unnecessarily sophisticated dependency engine.

---

# 31. INSPECTOR SUBMISSION

After reviewing and verifying the inspection, the Inspector submits it.

The state becomes:

```text
SUBMITTED_FOR_REVIEW
```

The Inspector can no longer behave as the final decision-maker.

---

# 32. REVIEWER WORKFLOW

The Reviewer logs in separately.

The Reviewer opens the submitted inspection.

The Reviewer can independently examine:

```text
Original Evidence
       ↓
OCR
       ↓
Declarations
       ↓
Applicability
       ↓
System Findings
       ↓
Inspector Corrections
       ↓
History
```

The Reviewer then decides how to proceed.

---

# 33. REVIEWER ACTIONS

The Reviewer can:

### CONFIRM

Accept the system finding.

### OVERRIDE

Change the assessment based on review.

An override requires a reason.

### REQUEST_REVISION

Send the inspection back to the Inspector.

### REQUEST_EVIDENCE

Request additional evidence for a specific unresolved fact.

The original system finding remains preserved.

---

# 34. REVIEWER DETERMINATION

Example:

```text
System Finding:

POTENTIAL_NON_COMPLIANCE

Reviewer:

OVERRIDE

Reason:

The declaration is visibly present in the original evidence.
OCR failed to detect the declaration.

Evidence:

IMG-00042
```

The system should preserve both:

```text
System Finding
+
Reviewer Determination
```

Do not overwrite history.

---

# 35. EVIDENCE REQUEST

A Reviewer may request additional evidence.

Example:

```text
Evidence Request ID:
ER-00017

Requested fact:
Provide a clearer image of the rear label showing
consumer-care information.

Requested by:
Reviewer

Timestamp:
...

Status:
OPEN
```

The Inspector can respond by:

- uploading supplemental evidence,
- adding a manual observation,
- stating that the fact could not be established.

The system should then reprocess affected information where required.

---

# 36. FINALIZATION

Only the Reviewer can finalize.

Before finalization, the backend verifies prerequisites.

At finalization:

```text
Working Inspection
       ↓
FinalAuditRecord
       ↓
FINALIZED
       ↓
READ ONLY
```

The final record represents the state that was actually decided.

---

# 37. FINAL AUDIT SNAPSHOT

The MVP should create a final snapshot containing/referencing:

- final declarations,
- applicability,
- findings,
- reviewer decisions,
- final outcome,
- evidence references,
- rule/version context,
- reviewer,
- timestamp.

This is the point-in-time representation of the final inspection.

---

# 38. FINALIZED RECORD BEHAVIOR

After finalization:

The inspection becomes read-only.

Normal operations must NOT be able to:

- modify declarations,
- modify findings,
- delete evidence,
- change applicability,
- change reviewer decision,
- change final outcome.

The UI must reflect this.

The backend must enforce it.

---

# 39. PDF REPORT

The MVP must generate a professional PDF.

The report should contain:

```text
COMPLISCAN LM
INSPECTION REPORT

Inspection ID
Inspection Date
Inspector
Reviewer

Product Information

Evidence References

Extracted Declarations

Applicability

Compliance Findings

Reviewer Determinations

Final Outcome

Rule/Version Reference

Audit/Finalization Timestamp
```

The report must be generated from the finalized result/snapshot.

Do not generate the final report from arbitrary mutable UI state.

---

# 40. HISTORY

The inspection should have a history view.

Example:

```text
18:02  Inspection Created
18:04  Evidence Uploaded
18:05  Evidence Accepted
18:06  Analysis Started
18:08  OCR Completed
18:09  Extraction Completed
18:09  Applicability Evaluated
18:10  Compliance Evaluated
18:12  Declaration Corrected
18:13  Verification Completed
18:14  Submitted for Review
18:17  Reviewer Override
18:18  Finalized
```

At minimum show:

- event,
- actor,
- timestamp.

---

# 41. AUDIT PRINCIPLE

Audit answers:

> “What happened?”

FinalAuditRecord answers:

> “What was final?”

These are different concepts.

Do not merge them into one confusing structure.

---

# 42. EVIDENCE MODEL

Use:

```text
DRAFT UPLOAD
      ↓
PRIMARY EVIDENCE
      ↓
DERIVED EVIDENCE
      ↓
INSPECTION RECORD
      ↓
FINAL SNAPSHOT
```

Accepted primary evidence should be treated as immutable.

New evidence gets a new Evidence ID.

Derived evidence references its source evidence.

Example:

```text
IMG-00042
    ↓
OCR-00087
    ↓
DECL-00021
    ↓
FND-00012
```

This creates traceability.

---

# 43. SHA-256

SHA-256 is useful for evidence integrity/change detection.

Example:

```text
Evidence:
IMG-00042

SHA-256:
<hash>
```

Important:

SHA-256 proves that the stored bytes can be compared for changes.

It does NOT prove that the image itself is factually authentic.

Do not describe hashing as proof of authenticity.

---

# 44. AI / HUMAN BOUNDARY

The system must maintain this separation:

```text
PaddleOCR
    ↓
"What text is visible?"

Gemini
    ↓
"What structured declaration does this text represent?"

Field Validation
    ↓
"Is the AI output structurally valid?"

Applicability
    ↓
"Which requirements apply?"

Rule Engine
    ↓
"Does the observed information satisfy the controlled requirement?"

Inspector
    ↓
"Does the observation actually match the package evidence?"

Reviewer
    ↓
"What is the final inspection determination?"
```

This separation is central to the project.

---

# 45. STATE MODEL

Use these master lifecycle states:

```text
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

Processing state is separate:

```text
IDLE
PROCESSING
FAILED
```

Compliance result is separate:

```text
PASS
POTENTIAL_NON_COMPLIANCE
REQUIRES_REVIEW
NOT_APPLICABLE
INCOMPLETE
PROCESSING_FAILED
```

Do not use individual finding status to replace the master inspection lifecycle.

---

# 46. MINIMUM DATA MODEL

Conceptual domain entities:

1. User
2. InspectionCase
3. EvidenceAsset
4. DerivedOcrToken
5. ExtractedDeclaration
6. ApplicabilityContext
7. ComplianceFinding
8. FinalAuditRecord
9. AuditEvent

Infrastructure may include:

- analysis_jobs,
- job attempts,
- sessions,
- other technical tables where required.

Do not create unnecessary domain entities merely to make the schema larger.

---

# 47. API

Use:

```text
/api/v1
```

Logical groups:

```text
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

Use explicit domain operations.

Avoid unrestricted mutation such as:

```text
PATCH /inspection/{id}
```

when it could bypass workflow rules.

Prefer operations such as:

```text
CreateInspection
AcceptEvidence
StartAnalysis
CorrectDeclaration
VerifyInspection
SubmitForReview
ReviewerDetermination
RequestEvidence
RequestRevision
FinalizeInspection
```

---

# 48. FRONTEND ROUTES

Use:

```text
/dashboard

/inspections

/inspections/new

/inspections/:id

/inspections/:id/verify

/inspections/:id/result

/inspections/:id/history

/review/:id
```

Do not create unnecessary screens.

---

# 49. MAIN INSPECTION WORKSPACE

The main inspection view should allow the Inspector to understand:

```text
┌──────────────────────────────────────────────┐
│ INSPECTION STATUS                            │
├──────────────────────┬───────────────────────┤
│                      │                       │
│ ORIGINAL EVIDENCE    │ OCR / EXTRACTION      │
│                      │                       │
├──────────────────────┴───────────────────────┤
│ DECLARATIONS                                  │
├──────────────────────────────────────────────┤
│ APPLICABILITY                                 │
├──────────────────────────────────────────────┤
│ COMPLIANCE FINDINGS                           │
├──────────────────────────────────────────────┤
│ EVIDENCE / REASONS / TRACEABILITY              │
└──────────────────────────────────────────────┘
```

The exact design may vary.

The information hierarchy must remain clear.

---

# 50. VISUAL SEMANTICS

The UI should clearly distinguish:

```text
AI OBSERVATION
SYSTEM FINDING
INSPECTOR CORRECTION
INSPECTOR VERIFICATION
REVIEWER DECISION
FINAL RESULT
```

A user should never have to guess whether a statement came from:

- OCR,
- AI,
- rule engine,
- Inspector,
- Reviewer.

---

# 51. AUTHENTICATION AND RBAC

Use Supabase Auth where practical.

Backend must enforce:

- authentication,
- role,
- inspection access,
- Inspector permissions,
- Reviewer permissions,
- reviewer/Inspector separation,
- finalized read-only behavior.

Frontend controls are for usability.

Backend controls are for security.

---

# 52. SECURITY MINIMUM

MVP security must include:

- authentication,
- authorization,
- backend role checks,
- input validation,
- file validation,
- private evidence storage,
- protected evidence retrieval,
- secret management,
- no hardcoded API keys,
- protection against arbitrary state transitions,
- protection against finalized-record mutation.

Do not expose private evidence publicly merely to simplify frontend implementation.

---

# 53. DURABLE QUEUE AND WORKER

The long-term architecture uses:

```text
FastAPI
   ↓
PostgreSQL
   ↓
analysis_jobs
   ↓
Worker
   ├── PaddleOCR
   └── Gemini
```

This is the preferred architecture.

However:

> **The queue must not become the reason the core demo does not work.**

If the PostgreSQL worker queue can be implemented cleanly during MVP development, implement it.

If infrastructure complexity begins blocking the primary workflow, prioritize a reliable implementation path and document the deferred production-hardening mechanism.

Do not create a fake asynchronous architecture.

Do not claim durable processing if it is not actually durable.

Do not use FastAPI BackgroundTasks and call it a production queue.

---

# 54. WORKER RESPONSIBILITIES

Worker handles:

- analysis jobs,
- image quality,
- PaddleOCR,
- Gemini,
- field validation,
- result persistence.

Worker does NOT handle:

- final legal decision,
- reviewer approval,
- finalization,
- RBAC authority,
- arbitrary lifecycle changes.

---

# 55. FAILURE SEMANTICS

Examples:

OCR service failure:

```text
PROCESSING_FAILED
```

Gemini API timeout:

```text
processing failure
```

Malformed Gemini response:

```text
validation/processing failure
```

Image unusable:

```text
INCOMPLETE
or
REQUIRES_REVIEW
```

Missing declaration with sufficient evidence:

```text
POTENTIAL_NON_COMPLIANCE
```

Conflicting evidence:

```text
REQUIRES_REVIEW
```

Do not convert technical failure into legal non-compliance.

---

# 56. LEGAL SCOPE

The MVP uses a controlled Legal Metrology rule snapshot based on the project's approved legal research.

The legal reference repository is source material.

Do not automatically turn every document into executable runtime logic.

Do not claim:

> “CompliScan implements every Legal Metrology rule.”

Instead the MVP should be described as:

> “A controlled MVP implementation for defined packaged-commodity declaration checks.”

Where the legal material is ambiguous:

DO NOT INVENT A RULE.

Flag the ambiguity.

---

# 57. RULE VERSIONING

Every compliance evaluation should be traceable to the controlled rule/version context.

Do not scatter unexplained legal constants across arbitrary source files.

Keep rule definitions centralized and understandable.

The MVP does not require a dynamic regulatory update pipeline.

---

# 58. TEST DATA AND DEMONSTRATION

Prepare at least one reliable demonstration fixture.

The preferred demo package should contain enough visible information to demonstrate:

- OCR,
- structured extraction,
- applicability,
- multiple compliance checks,
- evidence linking,
- Inspector correction,
- Reviewer decision.

Demo fixtures may be used for testing.

But the system must not be a hardcoded mock.

The demo should exercise real:

- OCR,
- extraction,
- validation,
- rule evaluation,
- workflow.

---

# 59. ACCEPTANCE TEST — PRIMARY DEMO

The following sequence must work:

```text
1. Inspector logs in.

2. Inspector creates inspection.

3. Inspector uploads package image.

4. Evidence is stored.

5. Analysis is started.

6. Image quality runs.

7. PaddleOCR extracts text.

8. OCR observations are persisted.

9. Gemini structures declarations.

10. Field validation validates the AI output.

11. Applicability is evaluated.

12. Six compliance domains are evaluated.

13. Findings appear.

14. Findings reference evidence.

15. Inspector reviews observations.

16. Inspector corrects at least one extracted value.

17. Old and new values remain traceable.

18. Affected evaluation is recomputed.

19. Inspector verifies the result.

20. Inspector submits for review.

21. Reviewer logs in separately.

22. Reviewer opens the inspection.

23. Reviewer reviews original evidence.

24. Reviewer reviews findings.

25. Reviewer confirms or overrides a finding.

26. Override contains a reason.

27. Reviewer finalizes.

28. Final snapshot is created.

29. Inspection becomes read-only.

30. PDF report is generated.

31. History displays the workflow.

32. Unauthorized mutation after finalization is rejected.
```

This is the principal MVP acceptance test.

---

# 60. SECURITY ACCEPTANCE TESTS

At minimum verify:

```text
Inspector cannot finalize.

Reviewer cannot finalize their own submitted inspection.

Unauthenticated users cannot access protected inspection data.

Unauthorized users cannot access another inspection's private evidence.

Accepted evidence cannot be silently replaced.

Finalized inspection cannot be modified through normal API calls.

Audit history cannot be edited through ordinary API operations.

AI output cannot directly create a final legal decision.
```

---

# 61. DATA INTEGRITY ACCEPTANCE TESTS

Verify:

```text
Original OCR remains available.

Declaration corrections preserve old values.

Correction records contain reason.

Correction records contain actor.

Correction records contain timestamp.

Correction can reference evidence.

System findings remain preserved after Reviewer override.

Final snapshot remains stable after finalization.

Final report represents finalized state.
```

---

# 62. IMPLEMENTATION PHASE 0

## Repository Audit

Before significant coding:

Inspect:

- files,
- directories,
- package managers,
- backend,
- frontend,
- database,
- legal references,
- OCR,
- AI,
- Docker,
- tests,
- configuration.

Output:

```text
CURRENT STATE
REUSABLE COMPONENTS
MISSING COMPONENTS
CONFLICTING COMPONENTS
RISKS
MVP IMPLEMENTATION PLAN
```

Do not begin a massive rewrite.

---

# 63. IMPLEMENTATION PHASE 1

## Foundation + Inspection + Evidence

Build:

- React application,
- FastAPI application,
- database connection,
- Supabase integration,
- authentication,
- roles,
- inspection creation,
- evidence upload,
- evidence display.

Acceptance:

```text
Inspector login
→ create inspection
→ upload image
→ view image
```

must work.

Do not proceed while this basic path is fundamentally broken.

---

# 64. IMPLEMENTATION PHASE 2

## OCR + AI

Build:

```text
Evidence
 ↓
Image Quality
 ↓
PaddleOCR
 ↓
Gemini
 ↓
Field Validation
```

Acceptance:

An actual package image produces actual structured declaration observations.

---

# 65. IMPLEMENTATION PHASE 3

## Applicability + Compliance

Build:

```text
Validated Observations
 ↓
Applicability
 ↓
Six Rules
 ↓
Findings
```

Acceptance:

Actual findings are produced from actual structured observations and deterministic rules.

---

# 66. IMPLEMENTATION PHASE 4

## Human Workflow

Build:

```text
Inspector
 ↓
Correction
 ↓
Recompute
 ↓
Verification
 ↓
Submission
 ↓
Reviewer
 ↓
Decision
```

Acceptance:

An inspection can successfully move from analysis to independent review.

---

# 67. IMPLEMENTATION PHASE 5

## Finalization + Reporting

Build:

```text
Reviewer
 ↓
Finalize
 ↓
Final Snapshot
 ↓
PDF
 ↓
History
```

Acceptance:

A finalized inspection becomes read-only and generates a report.

---

# 68. IMPLEMENTATION PHASE 6

## Hardening

Only after the end-to-end workflow works, improve:

- durable queue,
- worker retry,
- worker recovery,
- SHA-256,
- stronger evidence immutability,
- append-only audit enforcement,
- database constraints,
- security testing,
- observability,
- deployment.

---

# 69. DO NOT OVERENGINEER THE MVP

Do NOT add:

- RAG,
- vector database,
- autonomous agents,
- blockchain,
- generic chatbot,
- dynamic regulation engine,
- microservice architecture,
- multi-tenant enterprise platform,
- advanced analytics,
- unnecessary notification systems,
- mobile-native application,
- USP compliance,
- complete category-specific legal coverage.

If a feature does not help demonstrate the core inspection workflow, it should probably be deferred.

---

# 70. NO FEATURE CREEP PROTOCOL

Whenever a new feature is considered, classify it:

```text
MVP REQUIRED
MVP OPTIONAL
POST-MVP
OUT OF SCOPE
```

Only MVP REQUIRED items should block the current phase.

Do not implement POST-MVP features during critical-path development.

---

# 71. IMPLEMENTATION QUALITY RULES

Use:

- typed models,
- explicit schemas,
- clear service boundaries,
- transactions where necessary,
- database constraints,
- testable functions,
- centralized rules,
- meaningful errors,
- clear naming.

Avoid:

- magic strings,
- duplicated state definitions,
- duplicated rule logic,
- hidden mutation,
- unrestricted PATCH operations,
- frontend-only security,
- AI legal decisions,
- fake functionality.

---

# 72. ENVIRONMENT AND SECRETS

Use environment variables.

Provide:

```text
.env.example
```

Potential variables include:

```text
DATABASE_URL
SUPABASE_URL
SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY
GEMINI_API_KEY
```

Never commit real credentials.

Never place API keys in frontend source code.

---

# 73. DOCKER

Docker support should be provided where practical.

Long-term components:

```text
frontend
backend
worker
```

PaddleOCR dependencies should be handled so the worker does not unexpectedly depend on a developer's local environment.

Do not make the demo dependent on an individual developer machine beyond normal development requirements.

---

# 74. DOCUMENTATION

Documentation should reflect actual implementation.

At minimum maintain:

```text
README.md
docs/architecture.md
docs/development.md
docs/api.md
docs/security.md
docs/testing.md
docs/deployment.md
```

Do not spend more time documenting a feature than implementing and testing it.

---

# 75. ANTI-HALLUCINATION RULE FOR IMPLEMENTATION

Never say:

“implemented”

unless the code exists.

Never say:

“tested”

unless the test was actually executed.

Never say:

“secure”

without appropriate testing.

Never say:

“legally compliant”

because an AI model said so.

Never say:

“production-ready”

unless implementation and validation justify the statement.

Always distinguish:

```text
IMPLEMENTED
TESTED
UNTESTED
DEFERRED
BLOCKED
KNOWN LIMITATION
```

---

# 76. ARCHITECTURE DEVIATION RULE

If implementation encounters a genuine technical blocker:

STOP before silently changing the architecture.

Report:

```text
BLOCKER

Affected decision:
...

Why current design fails:
...

Evidence:
...

Minimum proposed change:
...

Alternatives:
...

Impact:
...
```

Do not redesign merely because another approach is more convenient.

However, do not block the MVP over theoretical future requirements.

---

# 77. CHECKPOINT FORMAT

At the end of every implementation phase, report:

```text
PHASE:
<name>

STATUS:
COMPLETED / PARTIALLY COMPLETED / BLOCKED

IMPLEMENTED:
- ...

FILES CREATED:
- ...

FILES MODIFIED:
- ...

DATABASE CHANGES:
- ...

TESTS:
- Passed:
- Failed:

DEMO STATUS:
- ...

KNOWN LIMITATIONS:
- ...

DEFERRED ITEMS:
- ...

ARCHITECTURE DEVIATIONS:
NONE
or
<explicit deviation>

NEXT PHASE:
<name>
```

---

# 78. DEFINITION OF “WORKING MVP”

The MVP is working when a judge can observe:

```text
REAL USER
   ↓
REAL LOGIN
   ↓
REAL INSPECTION
   ↓
REAL PACKAGE IMAGE
   ↓
REAL OCR
   ↓
REAL AI EXTRACTION
   ↓
REAL VALIDATION
   ↓
REAL APPLICABILITY
   ↓
REAL DETERMINISTIC RULES
   ↓
REAL FINDINGS
   ↓
REAL INSPECTOR VERIFICATION
   ↓
REAL REVIEWER DECISION
   ↓
REAL FINALIZATION
   ↓
REAL PDF
   ↓
REAL HISTORY
```

The exact visual styling can evolve.

The underlying workflow must work.

---

# 79. WHAT THE JUDGE SHOULD UNDERSTAND FROM THE DEMO

The demonstration should communicate five things:

## 1. The system can understand package information.

OCR + structured extraction.

## 2. The system does not blindly apply every rule.

Applicability comes before compliance evaluation.

## 3. AI does not make the final legal decision.

AI extracts.

Rules evaluate.

Humans verify and decide.

## 4. Findings are evidence-linked.

The system can show where an observation came from.

## 5. The inspection is traceable.

Corrections, reviewer decisions, and finalization are recorded.

---

# 80. EXPECTED MVP DEMONSTRATION SCRIPT

A concise demonstration should look like:

```text
“An Inspector starts a new inspection and uploads a package image.

CompliScan stores the original evidence and analyzes it.

PaddleOCR identifies the visible text.

Gemini structures the detected declarations into fields such as
manufacturer, product name, quantity, packing date, MRP and
consumer-care details.

The backend validates that structured output.

The system then determines which requirements apply before running
the compliance checks.

The deterministic rule engine generates findings and links them to
the underlying evidence.

The Inspector reviews the observations. If OCR made a mistake,
the Inspector can correct it, with the original value and reason
preserved.

The Inspector verifies the inspection and submits it.

A different Reviewer independently examines the evidence and
findings and can confirm, override, or request additional evidence.

Once satisfied, the Reviewer finalizes the inspection.

The final result becomes read-only and a PDF report is generated
from the finalized record.

The history shows how the inspection reached that final state.”
```

This is the story the product must support.

---

# 81. LONG-TERM EXPANSION PATH

After MVP stability, the system can expand into:

```text
MVP
 │
 ├── More packaged commodity categories
 ├── More applicability rules
 ├── More declaration checks
 ├── Better visual/layout analysis
 ├── Stronger evidence integrity
 ├── Advanced queue/recovery
 ├── Broader legal rule coverage
 ├── Better analytics
 ├── Mobile capture
 └── Production deployment hardening
```

These are expansion paths.

They must not contaminate the first implementation.

---

# 82. FINAL INSTRUCTION TO ANTIGRAVITY

Treat this document as the authoritative definition of the CURRENT MVP implementation scope.

The previously approved architecture remains the long-term architectural baseline.

Do not confuse:

```text
TARGET ARCHITECTURE
```

with:

```text
IMMEDIATE MVP SCOPE
```

The immediate goal is:

> **BUILD A REAL, SMALL, END-TO-END COMPLISCAN LM MVP THAT CAN BE DEMONSTRATED.**

Do not chase completeness before functionality.

Do not chase enterprise features before the inspection pipeline works.

Do not build fake functionality.

Do not silently redesign.

Do not invent legal requirements.

Do not let AI make autonomous legal decisions.

Do not let production-hardening tasks block the core workflow unless they are required for correctness or security.

Start with:

```text
PHASE 0 — REPOSITORY AUDIT
```

Then implement the MVP incrementally.

The success condition is not the number of files created.

The success condition is:

```text
PACKAGE IMAGE
     ↓
UNDERSTAND
     ↓
APPLICABILITY
     ↓
DETERMINISTIC CHECKS
     ↓
EVIDENCE
     ↓
INSPECTOR VERIFICATION
     ↓
REVIEWER DECISION
     ↓
FINAL REPORT
```

Build that first.
