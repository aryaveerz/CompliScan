# CompliScan LM — Proposed Requirement-Complete MVP Specification

**Project:** CompliScan LM  
**SIH Problem Statement:** PS ID 26034  
**Purpose:** Define the smallest REAL MVP that demonstrates the major functional requirements of the SIH problem statement while preserving the approved long-term architecture.  
**Status:** PROPOSED — FOR ANTIGRAVITY REVIEW  
**Date:** 2026-09-16  
**Important:** This document is a proposal for review. It is NOT yet the final implementation specification.

---

# 1. WHY THIS DOCUMENT EXISTS

The project has already gone through substantial legal, workflow, and architecture design.

The previous MVP specification successfully defined a complete inspection workflow, but we identified an important gap:

> The MVP must not only demonstrate a technically sound OCR → AI → rules → human workflow. It must also visibly address the major capabilities explicitly requested by the SIH problem statement.

The SIH statement asks for capabilities including:

- scanning packaged commodity images,
- detecting mandatory declarations,
- checking correctness and completeness,
- checking placement,
- identifying missing/non-compliant declarations,
- readability and font-size analysis,
- reports and violation summaries,
- product repository and compliance history,
- dashboards,
- search/retrieval,
- secure role-based access,
- PDF and editable reports,
- product images/product information,
- rule-based compliance checking.

Therefore this document proposes a **Requirement-Complete Demonstration MVP**.

The objective is NOT to build every possible legal rule or production-hardening feature.

The objective is:

> **Build a small, real, demonstrable system that visibly addresses the major SIH requirements from input to final report.**

---

# 2. IMPORTANT DISTINCTION

There are three different things in this project:

```text
LONG-TERM ARCHITECTURE
        ↓
What the complete system can eventually become

MVP IMPLEMENTATION
        ↓
What we build now for the SIH demonstration

POST-MVP EXPANSION
        ↓
What can be added if time remains
```

Do not confuse them.

The MVP is intentionally smaller than the long-term platform.

However, the MVP must still demonstrate the core capabilities described in the SIH problem statement.

---

# 3. SIH PROBLEM STATEMENT

The background describes packaged commodities being sold through:

- retail stores,
- supermarkets,
- e-commerce platforms.

The problem concerns mandatory declarations under the Legal Metrology Act, 2009 and Legal Metrology (Packaged Commodities) Rules, 2011.

The proposed software should scan:

- product labels,
- package images,
- product information.

The system should help identify:

- missing declarations,
- incorrect declarations,
- non-compliant declarations,
- placement issues,
- readability issues,
- font-size issues,
- other defined declaration problems.

The system should also provide:

- reports,
- violation summaries,
- repository/history,
- dashboards,
- search/retrieval,
- secure role-based access.

This MVP must visibly address these requirements within a controlled and clearly defined scope.

---

# 4. CORE MVP PROMISE

The MVP should demonstrate:

> **Scan → Understand → Determine Applicability → Validate → Check → Prove with Evidence → Inspector Verifies → Reviewer Decides → Report**

The system is an inspection-assistance tool.

It is NOT an autonomous legal enforcement system.

The core principle remains:

> **AI finds → Evidence proves → Officer decides.**

---

# 5. THE COMPLETE MVP SCENARIO

The MVP should support the following real-world scenario.

```text
Inspector encounters a packaged commodity
                 ↓
Captures package evidence
                 ↓
Creates inspection
                 ↓
Uploads package image
                 ↓
System checks image quality/readability
                 ↓
PaddleOCR detects visible text
                 ↓
Gemini structures declarations
                 ↓
Backend validates AI output
                 ↓
System determines applicability
                 ↓
Deterministic compliance checks
                 ↓
Visual screening:
  - readability
  - font-size estimation
  - placement
  - declaration-format anomalies
                 ↓
Evidence-linked findings
                 ↓
Inspector reviews observations
                 ↓
Inspector corrects/verifies information
                 ↓
Inspector submits inspection
                 ↓
Independent Reviewer reviews
                 ↓
Reviewer confirms/overrides/requests evidence/revision
                 ↓
Reviewer finalizes
                 ↓
Final inspection snapshot
                 ↓
PDF + editable DOCX
                 ↓
Searchable repository/history
                 ↓
Dashboard metrics
```

This is the primary MVP story.

---

# 6. REQUIREMENT-COVERAGE PRINCIPLE

Every major SIH requirement should map to:

```text
SIH REQUIREMENT
      ↓
MVP CAPABILITY
      ↓
IMPLEMENTATION
      ↓
DEMO ACTION
      ↓
VISIBLE RESULT
```

The MVP should not merely claim that a requirement is supported.

The feature should be demonstrable.

---

# 7. REQUIREMENT COVERAGE MATRIX

| SIH Requirement | MVP Capability | Demonstration |
|---|---|---|
| Scan packaged commodity images | Image upload and analysis | Upload package image |
| Detect mandatory declarations | OCR + structured extraction | Show detected fields |
| Automated extraction | PaddleOCR + Gemini | Show extracted declarations |
| Correctness checking | Deterministic rule checks | Show finding/reason |
| Completeness checking | Required-field evaluation | Show missing/not-observed/review state |
| Placement checking | Basic visual placement assessment | Show declaration location/highlight |
| Missing declaration detection | Evidence-aware missing-field assessment | Show potential missing declaration |
| Non-compliant declaration detection | Six deterministic compliance domains | Show findings |
| Readability checking | Image/OCR readability assessment | Show readability status |
| Font-size checking | Visual font-size screening/estimation | Show estimate + confidence/review state |
| Misleading/non-standard declarations | Defined format/anomaly checks | Show anomaly/review finding |
| Compliance reports | PDF | Generate report |
| Violation summaries | Findings summary | Show result summary |
| Product repository | Inspection repository | Browse previous inspections |
| Compliance history | Inspection history/audit | Open history |
| Dashboard | Real metrics | Dashboard counts |
| Web/mobile application | Responsive web application | Browser demonstration |
| Product information | Structured inspection metadata + optional listing input | Create inspection |
| Rule-based checking | Deterministic backend rule engine | Explain finding |
| Supporting evidence | Original images + evidence references | Open evidence |
| RBAC | Inspector/Reviewer | Login with different roles |
| Secure authentication | Authenticated backend | Login |
| Search/retrieval | Search/filter | Find previous inspection |
| PDF export | PDF generation | Download/view PDF |
| Editable export | DOCX generation | Generate editable report |
| Technical documentation | Project docs | Show architecture/deployment documentation |

This matrix is a REQUIRED implementation tracking artifact.

---

# 8. MVP INPUT MODES

The MVP should support two related input modes where practical.

## MODE A — PHYSICAL PACKAGE

Inspector uploads:

- package photograph,
- label photograph,
- multiple package images if needed.

Primary use:

```text
Physical package
→ evidence image
→ OCR
→ extraction
→ compliance
```

## MODE B — ONLINE PRODUCT LISTING

The MVP should support product information from an online context through:

- listing screenshot,
- product image,
- optionally a product URL/reference.

The MVP does NOT require a web crawler.

The purpose is to demonstrate that the system can accept and analyze product information beyond a single physical-package workflow.

The same compliance pipeline should be reused.

---

# 9. EVIDENCE TYPES

Support:

### Primary Evidence

Original package/listing image supplied by Inspector.

### Supplemental Evidence

Additional image supplied later.

### Derived Evidence

- OCR region,
- bounding box,
- crop,
- highlight,
- visual analysis region.

Every derived observation should reference its source evidence.

---

# 10. CORE PIPELINE

The central processing pipeline is:

```text
INPUT
 ↓
IMAGE QUALITY
 ↓
PADDLEOCR
 ↓
OCR OBSERVATIONS
 ↓
GEMINI
 ↓
STRUCTURED DECLARATIONS
 ↓
FIELD VALIDATION
 ↓
APPLICABILITY
 ↓
DETERMINISTIC COMPLIANCE
 ↓
VISUAL ASSESSMENT
 ↓
FINDINGS
 ↓
HUMAN VERIFICATION
```

The stages must remain logically distinguishable.

---

# 11. IMAGE QUALITY

The system should identify obvious image-quality problems.

Examples:

- invalid image,
- very low resolution,
- severe blur,
- insufficient OCR quality,
- unusable evidence.

Possible output:

```text
ACCEPTABLE
DEGRADED
UNUSABLE
```

Poor image quality does NOT equal legal non-compliance.

If the evidence cannot establish a fact:

```text
INCOMPLETE
or
REQUIRES_REVIEW
```

may be appropriate.

---

# 12. READABILITY ANALYSIS

Readability is an explicit SIH requirement and therefore must be visible in the MVP.

The system should assess whether relevant declaration regions are sufficiently readable for analysis.

Possible outcomes:

```text
READABLE
PARTIALLY_READABLE
POORLY_READABLE
UNUSABLE
```

Inputs may include:

- OCR confidence,
- image resolution,
- image quality,
- character visibility,
- region quality.

Example:

```text
Consumer Care

Readability:
POORLY_READABLE

OCR Confidence:
0.41

Assessment:
REQUIRES_REVIEW
```

Important:

```text
Poor readability ≠ Missing declaration
```

The system should distinguish the two.

---

# 13. FONT-SIZE ANALYSIS

The SIH requirement explicitly includes font-size checking.

The MVP must therefore include a **font-size screening/estimation capability**.

It must NOT pretend to provide universally precise statutory measurement from arbitrary photographs.

The pipeline may be:

```text
Declaration Region
      ↓
Text Bounding Box
      ↓
Character Height
      ↓
Available Scale Information
      ↓
Estimated Physical Size
      ↓
Assessment
```

Possible outputs:

```text
Estimated font size:
~3.2 mm

Assessment:
REVIEW REQUIRED

Reason:
Insufficient physical scale reference.
```

Where reliable scale/reference information is available:

```text
Estimated:
4.1 mm

Assessment:
APPEARS TO SATISFY CONFIGURED SCREENING THRESHOLD
```

The system should clearly label such output as:

> **Font-size screening / estimation**

not:

> **Definitive legal measurement**

If physical scale is unavailable, the system should not invent millimetres.

It should say:

```text
UNABLE TO ESTABLISH PRECISE PHYSICAL SIZE
```

and flag for manual review.

---

# 14. PLACEMENT ANALYSIS

Placement is explicitly requested by the SIH statement.

The MVP should therefore provide a basic visual placement assessment.

The purpose is to determine:

> Where was the declaration observed on the supplied package/label image?

Pipeline:

```text
Declaration
    ↓
OCR Bounding Box
    ↓
Image / Label Region
    ↓
Configured Expected Region
    ↓
Placement Assessment
```

Possible output:

```text
MRP

Detected Region:
Front Label

Placement:
OBSERVED

Evidence:
IMG-00042
```

or:

```text
Consumer Care

Detected Region:
Rear Label

Assessment:
REQUIRES_REVIEW
```

The MVP must NOT claim universal understanding of every packaging-placement provision.

Placement analysis is a controlled visual screening capability.

---

# 15. DECLARATION-FORMAT / NON-STANDARD ANALYSIS

The SIH statement mentions misleading and non-standard declarations.

The MVP should address this through defined checks rather than broad AI claims.

Examples of checks:

- malformed MRP representation,
- unsupported/ambiguous quantity unit,
- malformed date representation,
- incomplete consumer-care representation,
- suspicious declaration formatting,
- ambiguous extracted values,
- conflicting declaration values.

Possible outcome:

```text
STANDARD
NON_STANDARD / ANOMALOUS
REQUIRES_REVIEW
```

Do NOT claim:

> “AI can detect every misleading declaration.”

Instead claim:

> “The MVP detects defined declaration-format anomalies within its controlled rule scope and flags ambiguous cases for review.”

---

# 16. MISSING DECLARATION LOGIC

Missing declaration detection must be evidence-aware.

Do NOT implement:

```text
OCR didn't find field
→ field is missing
```

Instead:

```text
Required field
      ↓
Was evidence sufficient?
      │
      ├── NO
      │    ↓
      │  INCOMPLETE / REVIEW
      │
      └── YES
           ↓
      Was declaration observed?
           │
           ├── YES → evaluate value
           │
           └── NO → potential missing declaration
```

Important distinction:

```text
NOT_OBSERVED ≠ MISSING
UNREADABLE ≠ MISSING
INSUFFICIENT_EVIDENCE ≠ MISSING
```

This is critical to avoid false conclusions.

---

# 17. APPROVED SIX CORE COMPLIANCE DOMAINS

The MVP's deterministic compliance engine must implement:

## 1. Manufacturer / Packer / Importer

Identity and address information.

## 2. Common / Generic Product Name

Required commodity identification.

## 3. Net Quantity + Standard Unit

Quantity and applicable unit representation.

## 4. Month / Year

Manufacture/packing/import date information as applicable.

## 5. MRP Inclusive of All Taxes

MRP declaration.

## 6. Consumer Care Details

Consumer-care information.

These six are the core universal MVP compliance domains.

---

# 18. COUNTRY OF ORIGIN

Country of Origin is applicability-driven.

It is NOT a universal seventh compliance check.

Example:

```text
Imported:
YES
→ COO applicable
```

```text
Imported:
NO
→ COO not applicable
```

```text
Imported:
UNKNOWN
→ REVIEW / INCOMPLETE
```

Do not guess.

---

# 19. USP

USP is excluded.

Do not create:

- USP UI,
- USP API,
- USP database field,
- USP rule,
- USP finding,
- USP test.

---

# 20. RESULT VOCABULARY

Use:

```text
PASS
POTENTIAL_NON_COMPLIANCE
REQUIRES_REVIEW
NOT_APPLICABLE
INCOMPLETE
PROCESSING_FAILED
```

Definitions:

### PASS

The applicable requirement appears satisfied based on available verified information.

### POTENTIAL_NON_COMPLIANCE

Available evidence supports a possible failure of an applicable requirement.

### REQUIRES_REVIEW

Information is uncertain, conflicting, ambiguous, or insufficient for automatic determination.

### NOT_APPLICABLE

Requirement does not apply.

### INCOMPLETE

Evidence/information is insufficient to complete the assessment.

### PROCESSING_FAILED

Technical processing failed.

Never convert:

```text
PROCESSING_FAILED → NON_COMPLIANCE
```

or:

```text
INCOMPLETE → NON_COMPLIANCE
```

or:

```text
NOT_APPLICABLE → PASS
```

---

# 21. EVIDENCE-LINKED FINDINGS

Every important finding must be traceable.

Preferred chain:

```text
Finding
  ↓
Compliance Check
  ↓
Declaration
  ↓
OCR Observation
  ↓
Bounding Box
  ↓
Original Evidence
```

Example:

```text
FND-00012
   ↓
MRP Check
   ↓
DECL-00021
   ↓
OCR-00087
   ↓
IMG-00042
```

The UI should allow the Inspector/Reviewer to move from finding to evidence.

---

# 22. VISUAL HIGHLIGHTING

Where technically practical, findings should show a highlighted image region.

Example:

```text
Original Package Image

+---------------------------------------+
|                                       |
|       PRODUCT NAME                    |
|                                       |
|       Net Qty: 5 kg                   |
|                                       |
|       [ MRP ₹450 ]  ← highlighted    |
|                                       |
+---------------------------------------+
```

The purpose is evidence comprehension.

Do not modify the original evidence image.

Highlights are derived evidence.

---

# 23. INSPECTOR CORRECTION

Inspector can correct extracted observations.

Example:

```text
SYSTEM:
MRP = ₹20

INSPECTOR:
MRP = ₹120

REASON:
OCR misread printed value.

EVIDENCE:
IMG-00042
```

The old value must remain traceable.

Correction should trigger affected downstream recomputation.

---

# 24. CORRECTION PRINCIPLE

Use:

```text
Original Observation
       ↓
Correction Command
       ↓
Old Value + New Value
       ↓
Reason + Actor + Time + Evidence
       ↓
Invalidate affected evaluation
       ↓
Recompute
       ↓
Re-verify
```

Do not silently overwrite inspection history.

---

# 25. REVIEWER WORKFLOW

Reviewer is independent from Inspector.

Reviewer can:

- inspect evidence,
- inspect OCR,
- inspect declarations,
- inspect visual assessments,
- inspect applicability,
- inspect findings,
- inspect correction history,
- confirm,
- override,
- request evidence,
- request revision,
- finalize.

Reviewer cannot be the Inspector who submitted the inspection.

Backend must enforce this.

---

# 26. REVIEWER OVERRIDE

System finding remains preserved.

Example:

```text
SYSTEM:
POTENTIAL_NON_COMPLIANCE

REVIEWER:
OVERRIDE

REASON:
Declaration manually verified in original evidence.

EVIDENCE:
IMG-00042
```

Do not replace the original system finding with only the reviewer result.

---

# 27. FINALIZATION

Only Reviewer can finalize.

At finalization:

```text
Working Inspection
       ↓
Final Snapshot
       ↓
FINALIZED
       ↓
READ ONLY
```

The final snapshot should contain/refer to:

- final declarations,
- final applicability,
- final findings,
- reviewer decisions,
- final outcome,
- evidence,
- rule/version context,
- reviewer,
- timestamp.

---

# 28. REPORTING

The MVP must support:

## PDF

Required.

## Editable report

Required.

Use DOCX as the editable format.

Both should derive from the finalized inspection state.

```text
Final Snapshot
      │
      ├── PDF
      │
      └── DOCX
```

---

# 29. REPORT CONTENT

Include:

- CompliScan LM title,
- inspection ID,
- date,
- product information,
- Inspector,
- Reviewer,
- evidence references,
- extracted declarations,
- applicability,
- compliance findings,
- visual assessments,
- reviewer determinations,
- final outcome,
- rule/version reference,
- finalization timestamp.

The report should be professional and readable.

Do not over-invest in decorative styling.

---

# 30. VIOLATION / FINDING SUMMARY

The result screen should summarize findings.

Example:

```text
INSPECTION SUMMARY

Checks Evaluated: 6

PASS:                     4
POTENTIAL NON-COMPLIANCE: 1
REQUIRES REVIEW:           1
NOT APPLICABLE:             1
```

The exact counts should be derived from actual data.

Do not hard-code metrics.

---

# 31. PRODUCT REPOSITORY

The MVP must maintain a repository of previous inspections/products.

Minimum capabilities:

- list inspections,
- open inspection,
- view result,
- view evidence,
- view report,
- view history.

---

# 32. SEARCH AND RETRIEVAL

Implement actual search/filter functionality.

Searchable fields may include:

- inspection ID,
- product name,
- manufacturer,
- date,
- status,
- result.

Example:

```text
Search:
"ABC Foods"

Results:

INS-00042
ABC Foods Premium Rice
FINALIZED

INS-00051
ABC Foods Wheat Flour
REQUIRES_REVIEW
```

This directly addresses the SIH search/retrieval requirement.

---

# 33. DASHBOARD

Dashboard must use real stored data.

Minimum metrics:

```text
TOTAL INSPECTIONS
PENDING REVIEW
REQUIRES REVISION
FINALIZED
POTENTIAL NON-COMPLIANCE
REQUIRES REVIEW
```

Optional:

- recent inspections,
- recent findings,
- status distribution.

Do not build complex analytics.

---

# 34. WEB APPLICATION

The MVP will be a responsive web application.

A separate native mobile application is NOT required for MVP.

The web application should support:

- desktop,
- reasonable tablet/mobile responsiveness.

The core demonstration will use the web application.

---

# 35. AUTHENTICATION

Use authenticated users.

Operational roles:

```text
INSPECTOR
REVIEWER
```

Inspector and Reviewer must have different permissions.

Backend is authoritative.

---

# 36. MINIMUM DATA MODEL

Core entities:

```text
User
InspectionCase
EvidenceAsset
DerivedOcrToken
ExtractedDeclaration
ApplicabilityContext
ComplianceFinding
FinalAuditRecord
AuditEvent
```

Infrastructure entities may include:

```text
analysis_jobs
```

if the asynchronous queue is implemented.

Do not create unnecessary domain entities.

---

# 37. API

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

Prefer explicit domain operations.

Examples:

```text
CreateInspection
UploadEvidence
AcceptEvidence
StartAnalysis
CorrectDeclaration
VerifyInspection
SubmitForReview
ReviewerDetermination
RequestEvidence
RequestRevision
FinalizeInspection
GenerateReport
```

Avoid unrestricted mutations that can bypass lifecycle.

---

# 38. FRONTEND ROUTES

Required:

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

Search can be integrated into `/inspections`.

---

# 39. LONG-TERM ASYNC ARCHITECTURE

The approved target architecture includes:

```text
FastAPI
   ↓
Supabase PostgreSQL
   ↓
analysis_jobs
   ↓
Worker
   ├── PaddleOCR
   └── Gemini
```

However:

> The durable queue must NOT block the first working compliance pipeline.

For the first MVP implementation, synchronous processing through a clean service boundary is acceptable if it allows the real pipeline to work quickly.

After the vertical slice is stable, the PostgreSQL-backed worker can be implemented.

Do not create fake asynchronous behavior.

Do not claim durable queue semantics unless they actually exist.

---

# 40. TECHNOLOGY STACK

Use:

```text
Frontend:
React + TypeScript + Vite + Tailwind

Backend:
Python 3.11+ + FastAPI

Database:
PostgreSQL / Supabase

Authentication:
Supabase Auth

Storage:
Supabase Storage

OCR:
PaddleOCR

LLM:
Gemini 2.5 Flash

ORM:
SQLAlchemy

Migrations:
Alembic

Reports:
PDF + DOCX

Containerization:
Docker
```

---

# 41. AI RESPONSIBILITY

PaddleOCR:

```text
Text
Coordinates
OCR Confidence
```

Gemini:

```text
Semantic extraction
Structured declaration fields
Normalization
Uncertainty/conflict representation
```

Backend:

```text
Schema validation
Applicability
Compliance rules
Lifecycle
RBAC
Finalization
```

Inspector:

```text
Observation verification
Correction
Submission
```

Reviewer:

```text
Independent decision
Finalization
```

---

# 42. NO AI LEGAL VERDICT

Never implement:

```text
Gemini
 ↓
"LEGAL VIOLATION"
```

Implement:

```text
Gemini
 ↓
Structured Observation
 ↓
Validation
 ↓
Applicability
 ↓
Deterministic Rule
 ↓
Potential Finding
 ↓
Inspector
 ↓
Reviewer
```

---

# 43. FIELD-LEVEL AI VALIDATION

Validate:

- schema,
- type,
- format,
- missing values,
- uncertainty,
- conflicts,
- source traceability.

No guessing.

Example:

```text
OCR:
₹1?0

Gemini:
₹120
```

Do not blindly accept.

The system should preserve uncertainty unless evidence supports the interpretation.

---

# 44. EVIDENCE INTEGRITY

At minimum:

- original evidence preserved,
- evidence ID,
- private storage,
- authorization,
- file validation.

SHA-256 should be implemented if it does not delay the critical path.

Hash meaning:

```text
Integrity/change detection
```

Not:

```text
Proof of factual authenticity
```

---

# 45. BASIC SECURITY

Required:

- authentication,
- backend authorization,
- role checks,
- evidence access control,
- file validation,
- secret management,
- protected APIs,
- finalized record protection.

Never put API keys in frontend code.

Never rely solely on frontend RBAC.

---

# 46. AUDIT

The MVP should record important workflow events.

At minimum:

```text
Inspection Created
Evidence Uploaded
Analysis Started
Analysis Completed
Declaration Corrected
Verification Completed
Submitted
Reviewer Decision
Finalized
```

Each should contain:

- event,
- actor,
- timestamp.

---

# 47. MVP STATE MODEL

Master lifecycle:

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

Processing:

```text
IDLE
PROCESSING
FAILED
```

Compliance result:

```text
PASS
POTENTIAL_NON_COMPLIANCE
REQUIRES_REVIEW
NOT_APPLICABLE
INCOMPLETE
PROCESSING_FAILED
```

Do not merge these concepts.

---

# 48. MVP PHASE PLAN

## PHASE 0 — REPOSITORY AUDIT

Inspect repository.

Do not blindly rewrite.

Confirm:

- current state,
- reusable components,
- dependencies,
- existing documentation,
- missing implementation.

---

## PHASE 1 — WORKING FOUNDATION

Implement:

- frontend,
- backend,
- Supabase,
- authentication,
- roles,
- inspection creation,
- evidence upload,
- evidence display.

Acceptance:

```text
Inspector login
→ Create inspection
→ Upload image
→ View image
```

---

## PHASE 2 — REAL AI PIPELINE

Implement:

```text
Image
 ↓
Quality
 ↓
PaddleOCR
 ↓
Gemini
 ↓
Validation
```

Acceptance:

Real package image produces real structured declarations.

---

## PHASE 3 — REAL COMPLIANCE + VISUAL ASSESSMENT

Implement:

```text
Declarations
 ↓
Applicability
 ↓
Six Rules
 ↓
Readability
 ↓
Font-size screening
 ↓
Placement screening
 ↓
Format anomaly checks
 ↓
Findings
```

Acceptance:

The system visibly addresses the main detection/validation requirements of the SIH statement.

---

## PHASE 4 — HUMAN WORKFLOW

Implement:

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
```

Acceptance:

Independent reviewer workflow works.

---

## PHASE 5 — REPORTING + REPOSITORY

Implement:

- finalization,
- final snapshot,
- PDF,
- DOCX,
- history,
- search,
- dashboard.

Acceptance:

A complete inspection can be finalized, retrieved, searched and reported.

---

## PHASE 6 — HARDENING

If time remains:

- PostgreSQL durable queue,
- worker,
- retry/recovery,
- stronger evidence integrity,
- SHA-256 if deferred,
- database immutability,
- advanced audit protection,
- observability,
- deployment hardening.

---

# 49. PRIMARY DEMO ACCEPTANCE TEST

The complete demonstration should be:

```text
1. Login as Inspector.

2. Create inspection.

3. Upload package image.

4. Show original evidence.

5. Run analysis.

6. Show image-quality/readability assessment.

7. Show PaddleOCR output.

8. Show OCR bounding boxes.

9. Show Gemini structured declarations.

10. Show field-level validation.

11. Show applicability.

12. Run six compliance checks.

13. Show findings.

14. Open a finding.

15. Show evidence highlight/source.

16. Show font-size assessment.

17. Show placement assessment.

18. Show any format/anomaly assessment.

19. Inspector corrects an extracted declaration.

20. Show old and new value.

21. Show recomputation.

22. Inspector verifies.

23. Inspector submits.

24. Login as different Reviewer.

25. Reviewer opens inspection.

26. Reviewer examines evidence and findings.

27. Reviewer confirms or overrides a finding.

28. Reviewer records reason.

29. Reviewer finalizes.

30. Final snapshot is created.

31. Inspection becomes read-only.

32. Generate PDF.

33. Generate editable DOCX.

34. Open history.

35. Search for the inspection.

36. Show dashboard metrics.
```

This is the main MVP demonstration.

---

# 50. REQUIREMENT-COMPLETENESS TEST

Before calling the MVP complete, verify:

```text
[ ] Image scanning
[ ] Declaration detection
[ ] Declaration extraction
[ ] Correctness checking
[ ] Completeness checking
[ ] Missing declaration handling
[ ] Placement assessment
[ ] Readability assessment
[ ] Font-size screening
[ ] Defined non-standard/format anomaly checks
[ ] Evidence attachment
[ ] Evidence-linked findings
[ ] Compliance report
[ ] Violation/finding summary
[ ] Product/inspection repository
[ ] History
[ ] Search
[ ] Dashboard
[ ] Authentication
[ ] RBAC
[ ] Inspector verification
[ ] Reviewer workflow
[ ] PDF export
[ ] Editable DOCX export
[ ] Technical documentation
```

Every checked item must be demonstrable.

---

# 51. LEGAL HONESTY REQUIREMENT

Do not overclaim.

The MVP is a controlled inspection-assistance system.

Use phrases such as:

> “preliminary compliance assessment”

> “potential non-compliance”

> “visual screening”

> “font-size estimation”

> “requires manual review”

> “within the controlled MVP rule scope”

Avoid:

> “100% legal compliance”

> “AI legally determines violations”

> “fully autonomous enforcement”

> “detects every violation”

> “exact font-size measurement from every photograph”

> “complete Legal Metrology coverage”

---

# 52. KNOWN LIMITATIONS THAT SHOULD BE VISIBLE

The MVP may have limitations such as:

- poor image quality,
- insufficient physical scale for precise font-size measurement,
- unusual packaging layouts,
- ambiguous declarations,
- conflicting evidence,
- OCR errors,
- AI extraction uncertainty,
- product-specific rules outside MVP scope,
- regulatory changes outside the controlled rule snapshot.

The system should respond to these with:

```text
REQUIRES_REVIEW
INCOMPLETE
or
PROCESSING_FAILED
```

rather than fabricated certainty.

---

# 53. POST-MVP EXPANSION

After the MVP works, the system can expand to:

```text
More commodities
      ↓
More applicability rules
      ↓
More legal requirements
      ↓
Better font-size measurement
      ↓
Advanced placement analysis
      ↓
More sophisticated anomaly detection
      ↓
Physical ↔ online comparison
      ↓
Durable worker architecture
      ↓
Advanced audit integrity
      ↓
Production deployment
```

Do not implement these before the core MVP works.

---

# 54. NO FEATURE CREEP

Any proposed feature must be classified:

```text
MVP REQUIRED
MVP OPTIONAL
POST-MVP
OUT OF SCOPE
```

Only MVP REQUIRED items should block MVP completion.

Do not add features because they sound impressive.

---

# 55. IMPLEMENTATION DISCIPLINE

Antigravity must:

- inspect before changing,
- reuse compatible code,
- make small coherent changes,
- test continuously,
- report actual status,
- avoid fake implementations,
- avoid hardcoded final results,
- avoid silent architectural changes,
- avoid invented legal requirements.

---

# 56. ANTI-HALLUCINATION RULE

Never claim:

“implemented”

unless the feature exists.

Never claim:

“tested”

unless tests were run.

Never claim:

“secure”

without security validation.

Never claim:

“legally compliant”

because an AI model produced a result.

Always distinguish:

```text
IMPLEMENTED
TESTED
PARTIALLY IMPLEMENTED
DEFERRED
BLOCKED
KNOWN LIMITATION
```

---

# 57. ARCHITECTURE DEVIATION RULE

If a genuine technical blocker appears:

STOP.

Report:

```text
BLOCKER

Affected decision:
...

Problem:
...

Evidence:
...

Minimum proposed change:
...

Alternative:
...

Impact:
...
```

Do not silently redesign.

However, do not stop the MVP because a future production-hardening feature has not yet been implemented.

---

# 58. PHASE CHECKPOINT FORMAT

At the end of each phase:

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

SIH REQUIREMENTS NOW DEMONSTRABLE:
- ...

DEMO STATUS:
- ...

KNOWN LIMITATIONS:
- ...

DEFERRED:
- ...

ARCHITECTURE DEVIATIONS:
NONE
or
<explicit deviation>

NEXT PHASE:
<name>
```

---

# 59. WHAT SUCCESS LOOKS LIKE

A judge should be able to watch:

```text
PACKAGE
  ↓
SCAN
  ↓
READ
  ↓
UNDERSTAND
  ↓
CHECK APPLICABILITY
  ↓
CHECK DECLARATIONS
  ↓
CHECK VISUAL CONDITIONS
  ↓
SHOW EVIDENCE
  ↓
INSPECTOR VERIFIES
  ↓
REVIEWER DECIDES
  ↓
FINAL REPORT
  ↓
SEARCHABLE HISTORY
  ↓
DASHBOARD
```

and understand the product without requiring a long explanation.

---

# 60. FINAL MVP POSITIONING

The MVP should be positioned as:

> **An evidence-driven, AI-assisted inspection workflow for defined packaged-commodity declaration checks under a controlled Legal Metrology rule scope.**

The differentiators are:

1. Applicability before compliance evaluation.
2. AI extraction separated from legal/rule evaluation.
3. Evidence-linked findings.
4. OCR-to-evidence traceability.
5. Visual screening for readability, font size and placement.
6. Inspector correction with preserved history.
7. Independent Reviewer decision.
8. Finalized inspection snapshot.
9. PDF and editable report generation.
10. Searchable inspection repository and dashboard.
11. Support for both physical package evidence and online product/listing information.

---

# 61. CORE DIFFERENTIATION

The project should NOT be presented as:

> “We use OCR and Gemini to check product labels.”

That is too narrow.

Present it as:

> **“CompliScan LM combines perception, structured extraction, applicability-aware deterministic rules, visual screening, evidence traceability and human review into one inspection workflow.”**

The architecture behind it is:

```text
PERCEPTION
   ↓
UNDERSTANDING
   ↓
APPLICABILITY
   ↓
RULE EVALUATION
   ↓
VISUAL ASSESSMENT
   ↓
EVIDENCE
   ↓
HUMAN VERIFICATION
   ↓
INDEPENDENT REVIEW
   ↓
FINAL REPORT
```

---

# 62. FINAL INSTRUCTION TO ANTIGRAVITY

This document is a PROPOSED MVP scope.

Do NOT implement immediately based only on this document.

First REVIEW it.

Specifically evaluate:

1. Whether every major SIH functional requirement is represented.
2. Whether each proposed feature is realistically implementable as an MVP.
3. Whether any requirement is being overclaimed.
4. Whether font-size screening is technically reasonable.
5. Whether placement assessment is technically reasonable.
6. Whether readability analysis is technically reasonable.
7. Whether non-standard/misleading declaration handling is sufficiently scoped.
8. Whether physical and online input modes are worth including in the MVP.
9. Whether PDF + DOCX is practical.
10. Whether repository/search/dashboard are sufficiently scoped.
11. Whether any proposed feature creates disproportionate implementation complexity.
12. Whether anything important from the SIH statement is still missing.
13. Whether the proposed uniqueness is technically meaningful rather than marketing language.
14. Whether the MVP can realistically demonstrate the complete workflow.

DO NOT rewrite the proposal silently.

DO NOT start implementation during this review.

Return a structured review with:

```text
VERDICT

REQUIREMENT COVERAGE

STRONG POINTS

TECHNICAL RISKS

OVER-SCOPED ITEMS

UNDER-SCOPED ITEMS

MISSING REQUIREMENTS

RECOMMENDED CHANGES

MVP COMPLEXITY ASSESSMENT

DEMO FEASIBILITY

FINAL RECOMMENDATION
```

For every recommended change, explain:

- why,
- impact,
- whether it is MVP-critical,
- whether it can be deferred.

The goal is to determine whether this proposed MVP is:

> **small enough to build, broad enough to satisfy the SIH problem statement, technically defensible, and strong enough to demonstrate genuine differentiation.**

Do not optimize for the number of features.

Optimize for:

> **Requirement coverage + working demonstration + technical credibility + honest scope.**
