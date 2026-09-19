# 04 — UI/UX DESIGN SPECIFICATION

**Project:** ComplianceScan
**SIH'26 Problem Statement:** 26034
**Document Version:** 2.0
**Status:** Target design with controlled one-day MVP boundary

---

# 1. Purpose

This document defines the user-interface and user-experience design for ComplianceScan.

It describes:

- design principles
- user roles
- navigation
- inspection workflow
- evidence interaction
- OCR/AI presentation
- applicability presentation
- compliance-result presentation
- Inspector Verification
- Reviewer workflow
- evidence requests
- finalization
- reports/history/dashboard target experiences
- responsive behavior
- error states
- accessibility
- MVP design boundary

The design must make the system understandable as an inspection-assistance tool rather than an autonomous legal decision engine.

---

# 2. Design Vision

ComplianceScan should feel like a professional inspection workspace.

The interface should communicate:

```text
Evidence
   ↓
Observation
   ↓
Understanding
   ↓
Applicability
   ↓
Assessment
   ↓
Verification
   ↓
Decision
```

The central UX principle is:

> **AI finds → Evidence supports → Inspector verifies → Reviewer decides.**

The interface must never visually imply that an AI model independently establishes a final legal violation.

---

# 3. Design Goals

The UI should optimize for:

1. clarity
2. traceability
3. evidence visibility
4. low cognitive load
5. safe human verification
6. explicit uncertainty
7. clear lifecycle state
8. predictable navigation
9. deployable demonstration quality
10. mobile-friendly evidence capture where practical

---

# 4. MVP Design Principle

The one-day MVP must prioritize:

> **ONE COMPLETE USER JOURNEY > MANY PARTIAL SCREENS**

The minimum useful experience is:

```text
Create Inspection
      ↓
Add Evidence
      ↓
Process
      ↓
View OCR / AI Extraction
      ↓
View Applicability
      ↓
View Six Checks
      ↓
Inspect Evidence-Backed Findings
      ↓
Verify / Correct
      ↓
Submit / Complete
```

Every screen in the MVP should support this journey.

Target screens that do not contribute to this journey should be deferred unless explicitly approved.

---

# 5. Target User Roles

## 5.1 Inspector

Primary working user.

The Inspector can:

- create inspections
- provide context
- add evidence
- start analysis
- inspect OCR
- inspect extracted declarations
- correct extracted information
- verify applicability
- review findings
- add manual observations
- add supplemental evidence where supported
- submit for review

The Inspector does not finalize the inspection.

---

## 5.2 Reviewer

Independent decision-making user.

The Reviewer can:

- view submitted inspections
- inspect evidence
- inspect OCR/declarations
- inspect applicability
- inspect findings
- inspect audit/history
- confirm assessments
- correct/override with reason
- request additional evidence
- finalize

The Reviewer should have a dedicated review/audit workspace.

---

# 6. Information Architecture

Target navigation:

```text
ComplianceScan
│
├── Dashboard
│
├── Inspections
│   ├── All
│   ├── Draft
│   ├── Processing
│   ├── Verification
│   ├── Submitted
│   ├── Review
│   └── Finalized
│
├── New Inspection
│
├── Review Queue          [Reviewer]
│
├── Repository / History
│
└── Account
```

The one-day MVP may reduce navigation to:

```text
ComplianceScan
│
├── Inspections
├── New Inspection
└── Inspection Detail
```

Reviewer/History/Dashboard navigation is included only if those capabilities are implemented.

---

# 7. Global Layout

Recommended desktop structure:

```text
┌──────────────────────────────────────────────────────────┐
│ ComplianceScan                 User / Role / Account     │
├───────────────┬──────────────────────────────────────────┤
│ Navigation    │                                          │
│               │              Main Workspace              │
│ Inspections   │                                          │
│ New           │                                          │
│ History       │                                          │
│ Review        │                                          │
│ Dashboard     │                                          │
│               │                                          │
└───────────────┴──────────────────────────────────────────┘
```

The main workspace should remain focused on the current task.

---

# 8. Visual Hierarchy

The interface should distinguish:

### Primary

- current inspection state
- primary action
- compliance result
- evidence

### Secondary

- extraction details
- confidence
- processing metadata
- audit details

### Tertiary

- technical identifiers
- timestamps
- provenance details

Avoid overwhelming the user with implementation details during the primary inspection flow.

---

# 9. Status Vocabulary

Use the canonical product vocabulary:

```text
PASS
POTENTIAL NON-COMPLIANCE
REQUIRES REVIEW
NOT APPLICABLE
INCOMPLETE
PROCESSING FAILED
```

Do not replace these with ambiguous labels such as:

- “Bad”
- “AI failed”
- “Illegal”
- “Probably wrong”

---

# 10. Status Presentation

Suggested semantic treatment:

```text
PASS
      Clear positive result

POTENTIAL NON-COMPLIANCE
      Evidence-backed potential issue requiring attention

REQUIRES REVIEW
      Conflict/uncertainty/decision requiring human attention

NOT APPLICABLE
      Requirement does not apply

INCOMPLETE
      Required information/evidence is insufficient

PROCESSING FAILED
      Technical processing did not complete
```

The UI should clearly distinguish technical states from compliance outcomes.

---

# 11. Inspection Creation Screen

The Inspector should be able to start an inspection with minimal friction.

Suggested structure:

```text
NEW INSPECTION

Inspection Context
────────────────────────
Inspection reference
Date/time
Location/context
Inspector

Product Context
────────────────────────
Product name
Product type/category where supported
Imported?  Yes / No / Unknown

[Continue]
```

Only information required by the supported workflow should be requested.

Avoid unnecessary forms in the MVP.

---

# 12. Evidence Capture Screen

Evidence is a primary workflow element.

Suggested layout:

```text
EVIDENCE

┌──────────────────────────────────────┐
│                                      │
│        Add / Capture Evidence        │
│                                      │
│       [ Upload Image ]               │
│       [ Capture Image ]              │
│                                      │
└──────────────────────────────────────┘

Evidence Items
────────────────────────────
EVD-000001   Front Label
EVD-000002   Back Label

[Continue to Analysis]
```

The exact capture mechanism depends on deployment/device capabilities.

---

# 13. Evidence Guidance

The UI should guide the Inspector toward useful evidence without imposing an arbitrary fixed photo count.

Example guidance:

> Capture enough of the package to establish the required declarations clearly.

If evidence coverage is insufficient:

> Additional evidence may be required.

The UI should not automatically demand a fixed number of photos for every package.

---

# 14. Evidence Card

Each evidence item may display:

```text
┌─────────────────────────────┐
│ Image Preview               │
│                             │
├─────────────────────────────┤
│ EVD-000001                  │
│ Primary Evidence            │
│ Captured: 10:32             │
│ Integrity: Verified         │
│                             │
│ [View] [Details]            │
└─────────────────────────────┘
```

Do not expose unnecessary storage paths.

---

# 15. Evidence Detail View

Target detail:

```text
Evidence
─────────────────────────────
Image

Evidence ID: EVD-000001
Type: PRIMARY
Captured/received: ...
Hash: ...
Source: ...
Inspection: ...

Derived Artifacts
- OCR regions
- highlights
- crops
```

The original image must remain visually distinguishable from derived artifacts.

---

# 16. Evidence Integrity Presentation

The UI may show:

```text
Integrity
✓ Original preserved
✓ SHA-256 recorded
```

Avoid implying:

> “Verified image is truthful.”

Hash verification indicates integrity/change detection, not truth or authenticity.

---

# 17. Image Quality Screen

Before analysis, the system may show:

```text
IMAGE QUALITY

Evidence EVD-000001

Readability       Good
Blur              Acceptable
Contrast          Good
Coverage          Partial

[Continue]
```

If severe problems exist:

```text
Review recommended:
This image may not provide sufficient visibility for some declarations.
```

This is a quality observation, not a legal finding.

---

# 18. Processing Screen

The processing UI should make system activity understandable.

Example:

```text
ANALYZING INSPECTION

✓ Evidence received
✓ Image processed
✓ Text detected
● Understanding declarations
○ Applicability
○ Compliance checks

Please wait...
```

If processing fails:

```text
PROCESSING FAILED

The analysis could not be completed.

Reason:
AI processing service unavailable.

This does not indicate product non-compliance.

[Retry]
```

---

# 19. OCR Review Screen

The Inspector should be able to inspect OCR results where useful.

Suggested layout:

```text
OCR OBSERVATIONS

┌──────────────────────┬──────────────────────────────┐
│ Package Image       │ Detected Text                │
│                      │                              │
│ [Image + boxes]     │ MRP ₹199                     │
│                      │ Manufacturer: ABC Foods      │
│                      │ Net Qty: 500 g               │
│                      │                              │
│                      │ Confidence / source regions │
└──────────────────────┴──────────────────────────────┘
```

OCR confidence should be presented as an observation-quality signal, not a legal score.

---

# 20. Declaration Understanding Screen

The UI should show extracted declarations as structured observations.

Example:

```text
DECLARATIONS

Manufacturer / Packer / Importer
Observed
ABC Foods Pvt. Ltd.
Source: EVD-000001 / Region 04
AI confidence: High

Common / Generic Product Name
Observed
Packaged Food Product
Source: EVD-000001 / Region 02

MRP
Observed
₹199
Source: EVD-000002 / Region 03
```

---

# 21. Observation State Presentation

Use explicit states:

```text
OBSERVED
NOT OBSERVED
UNCERTAIN
UNREADABLE
CONFLICTING
```

Example:

```text
MRP
CONFLICTING

Observed values:
₹199 — Front label
₹179 — Side label

Review required.
```

Never hide conflicting observations behind a single selected value.

---

# 22. Declaration Correction UI

Inspector correction should be explicit.

Example:

```text
MRP

System observed:
₹199

Inspector correction:
₹179

Source:
EVD-000002 / Region 03

Reason / note:
Visible package value differs from OCR extraction.

[Save Correction]
```

The interface should make clear that the underlying observation is being corrected.

---

# 23. Correction Warning

When a correction affects downstream results:

```text
This correction will cause affected compliance assessments
to be recalculated.

Previous assessment will remain in history.
```

The system should not silently leave stale results visible.

---

# 24. Applicability Screen

Applicability should be visible before compliance results.

Example:

```text
APPLICABILITY

Country of Origin
────────────────────────
Import status: YES
Requirement: APPLICABLE

Consumer Care
────────────────────────
Requirement: APPLICABLE

Other supported requirement
────────────────────────
NOT APPLICABLE
```

The user should understand why a requirement is being evaluated.

---

# 25. Applicability Uncertainty

If import status is unknown:

```text
Import Status
UNKNOWN

Country of Origin applicability
REQUIRES REVIEW

Reason:
Import status could not be established from available information.
```

Do not convert uncertainty into a definitive applicability decision.

---

# 26. Compliance Summary Screen

The central inspection result should be easy to scan.

Example:

```text
INSPECTION RESULT

┌────────────────────────────────────────────────┐
│ Overall Assessment                             │
│                                                │
│        REQUIRES REVIEW                         │
│                                                │
│  6 supported requirements evaluated            │
│  4 PASS                                        │
│  1 POTENTIAL NON-COMPLIANCE                    │
│  1 REQUIRES REVIEW                             │
└────────────────────────────────────────────────┘
```

The UI must avoid presenting a single “AI compliance score.”

---

# 27. Requirement Checklist

Use a requirement-level view:

```text
REQUIREMENT CHECKS

✓ Manufacturer / Packer / Importer
  PASS

✓ Common / Generic Product Name
  PASS

! Net Quantity + Standard Unit
  REQUIRES REVIEW

! Month / Year
  POTENTIAL NON-COMPLIANCE

✓ MRP Inclusive of All Taxes
  PASS

✓ Consumer Care Details
  PASS
```

Each item should be expandable.

---

# 28. Finding Detail

Finding detail should answer four questions:

```text
What requirement?
What was observed?
Why is it a potential issue?
What evidence supports it?
```

Example:

```text
POTENTIAL NON-COMPLIANCE

Requirement
Month / Year of Manufacture / Packing / Import

Observation
No sufficiently readable date declaration was established.

Reason
Required declaration could not be established from available evidence.

Evidence
EVD-000001
Region 08

[View Evidence]
```

Avoid unsupported legal claims.

---

# 29. Evidence-Linked Finding View

Selecting evidence should open the relevant source region.

```text
Finding
   ↓
Evidence
   ↓
Highlighted Region
   ↓
Original Image
```

The Inspector should be able to verify the finding visually.

---

# 30. Evidence Insufficiency UI

When evidence is insufficient:

```text
INCOMPLETE

Evidence is insufficient to establish:
Consumer Care Details

Available evidence:
EVD-000001

Suggested action:
Provide clearer/supplemental evidence or record
that the information could not be established.

[Add Evidence]
[Record Observation]
```

This must not be displayed as a non-compliance verdict.

---

# 31. Inspector Verification Screen

This is the key human-in-the-loop screen.

Suggested structure:

```text
INSPECTOR VERIFICATION

Declarations
[Review]

Applicability
[Review]

Compliance Checks
[Review]

Evidence
[Review]

Manual Observations
[Add]

────────────────────────────
Verification Status
○ Not reviewed
● Reviewed

[Verify Inspection]
```

---

# 32. Verification Checklist

The Inspector should have a clear checklist:

```text
INSPECTOR VERIFICATION

[✓] Evidence reviewed
[✓] Extracted declarations reviewed
[✓] Applicability reviewed
[✓] Findings reviewed
[ ] Additional observation required

[Submit for Review]
```

If a required item is unresolved, submission should be blocked or clearly marked according to the state machine.

---

# 33. Manual Observation UI

The Inspector may record a manual observation.

Example:

```text
MANUAL OBSERVATION

Requirement
Net Quantity + Standard Unit

Observation
Quantity text is visible on the side panel.

Evidence
EVD-000002

Notes
Readable under normal inspection conditions.

[Save Observation]
```

Manual observations must remain distinguishable from AI-generated observations.

---

# 34. Submission UI

Before submission:

```text
READY FOR REVIEW

Evidence
✓ Available

Analysis
✓ Complete

Applicability
✓ Verified

Requirements
✓ Reviewed

Corrections
✓ Recalculated

[Submit for Review]
```

After submission:

```text
SUBMITTED

This inspection is now with the Reviewer.
The Inspector can no longer modify the working record
unless additional evidence is requested.
```

---

# 35. Submission Boundary UX

The interface must visibly communicate ownership.

Before submission:

```text
Inspector — Editing
```

After submission:

```text
Reviewer — Review in progress
Inspector — View only
```

This prevents confusion about who controls the record.

---

# 36. Reviewer Queue

Target Reviewer workspace:

```text
REVIEW QUEUE

Filter: [All] [Needs Review] [Evidence Requested]

Inspection     Result              Submitted
INS-00124      REQUIRES REVIEW     10:42
INS-00125      POTENTIAL ISSUE     10:37
INS-00126      INCOMPLETE          10:31

[Open Inspection]
```

The queue should prioritize actionable records.

---

# 37. Reviewer Inspection Workspace

Recommended layout:

```text
┌─────────────────────────────────────────────────────────┐
│ Inspection INS-00124              SUBMITTED             │
├───────────────────┬─────────────────────────────────────┤
│ Evidence          │ Findings                            │
│                   │                                     │
│ [Image]           │ Requirement                         │
│                   │ Assessment                          │
│                   │ Evidence                            │
├───────────────────┼─────────────────────────────────────┤
│ Declarations      │ Audit Timeline                      │
│                   │                                     │
│ Values / Sources  │ Events / Corrections / Decisions    │
└───────────────────┴─────────────────────────────────────┘
```

The Reviewer should be able to understand the entire decision chain without navigating through unrelated screens.

---

# 38. Reviewer Decision UI

Possible actions:

```text
REVIEW DECISION

[Confirm Assessment]

[Override Assessment]
Reason: ______________________

[Request Additional Evidence]

[Finalize]
```

Override must require a reason.

---

# 39. Reviewer Override Presentation

When an override exists:

```text
SYSTEM ASSESSMENT
POTENTIAL NON-COMPLIANCE

REVIEWER DECISION
PASS

Reason
Reviewer verified the declaration against additional evidence.

Reviewer
Reviewer-001
Time
10:58
```

The system assessment remains visible in history.

---

# 40. Evidence Request UI

Example:

```text
REQUEST ADDITIONAL EVIDENCE

Evidence Request ID: ER-00017

What needs to be established?
Consumer care details on package side panel.

Reason:
Current evidence does not clearly establish the declaration.

[Send Request]
```

The Reviewer should not be forced to request a specific number of images.

---

# 41. Inspector Evidence Request Response

```text
EVIDENCE REQUEST
ER-00017

Requested:
Consumer care details

Response

[Add Supplemental Evidence]
[Add Manual Observation]
[Unable to Establish]

Notes:
________________________

[Resubmit]
```

If new evidence changes analysis, the affected information should be reprocessed.

---

# 42. Finalization UI

Before finalization:

```text
FINALIZE INSPECTION

Reviewer Decision:
PASS

Checks:
✓ All required review actions complete
✓ Evidence available
✓ Decision reason recorded
✓ Rule snapshot recorded
✓ Audit information available

Finalization will make this inspection read-only.

[Finalize Inspection]
```

---

# 43. Finalized State UI

After finalization:

```text
FINALIZED

This inspection is a historical record.
Normal editing is disabled.

Final Decision: PASS
Finalized by: Reviewer
Finalized: 11:04

[View Evidence]
[View Audit]
[Generate / View Report]
```

No normal edit controls should be shown.

---

# 44. Audit Timeline UI

Target timeline:

```text
AUDIT TIMELINE

10:12  Inspection created
10:14  Evidence EVD-000001 added
10:15  Evidence hash recorded
10:17  OCR completed
10:18  AI extraction completed
10:20  Inspector corrected MRP
10:20  Assessment recalculated
10:27  Inspector verified
10:29  Submitted
10:48  Reviewer opened
10:55  Reviewer decision recorded
11:04  Finalized
```

The timeline should be chronological and easy to inspect.

---

# 45. History / Repository UI

Target:

```text
INSPECTION HISTORY

Search [Inspection ID / Product]

Filters:
Date
Status
Result
Inspector
Reviewer

Inspection   Product       Result             State
INS-00124    Product A     PASS               FINALIZED
INS-00125    Product B     REVIEW             REVIEW
```

The MVP may implement a minimal history view if needed.

---

# 46. Dashboard UI

Target dashboard:

```text
DASHBOARD

Inspections
───────────
124

Potential Issues
───────────────
31

Requires Review
───────────────
12

Processing Failures
───────────────────
3

Recent Inspections
───────────────────
...
```

Metrics should be derived from persisted inspection data.

Dashboard is secondary to the inspection workflow for the one-day MVP.

---

# 47. Report UI

The report action should be explicit:

```text
REPORT

Inspection: INS-00124
Status: FINALIZED

[View Report]
[Export PDF]
[Export Editable]
```

Final reports should represent the finalized inspection snapshot.

---

# 48. Report Failure UI

If report generation fails:

```text
REPORT GENERATION FAILED

The inspection remains finalized.

Report generation can be retried.

[Retry]
```

Do not show the inspection as unfinalized because report generation failed.

---

# 49. Loading States

Every network/processing action should have a visible state.

Examples:

```text
Uploading...
Processing...
Loading inspection...
Saving correction...
Recalculating...
Submitting...
Finalizing...
```

Avoid ambiguous indefinite spinners.

Where possible, provide meaningful progress stages.

---

# 50. Empty States

Example:

```text
NO INSPECTIONS YET

Create your first inspection to begin.

[New Inspection]
```

Reviewer queue:

```text
NO INSPECTIONS NEED REVIEW

All submitted inspections are up to date.
```

---

# 51. Error States

Errors should be actionable.

Example:

```text
UPLOAD FAILED

The image could not be accepted.

Possible reasons:
- unsupported format
- file too large
- corrupted image

[Try Again]
```

Technical failures must not be shown as compliance failures.

---

# 52. AI Failure UX

```text
AI PROCESSING FAILED

The declaration-understanding service could not complete.

No compliance conclusion was generated from this failed step.

[Retry Analysis]
```

This wording protects against the dangerous interpretation:

> AI failed = product failed compliance.

---

# 53. OCR Failure UX

```text
TEXT EXTRACTION INCOMPLETE

Some text could not be reliably extracted.

You may:
- review the image
- provide clearer evidence
- manually verify the declaration

[Continue to Verification]
```

---

# 54. Conflict UX

```text
CONFLICTING INFORMATION

MRP values observed:
₹199 — EVD-000001
₹179 — EVD-000002

The system did not automatically select one.

Reviewer verification is required.
```

This should be visually prominent.

---

# 55. Unreadable UX

```text
UNREADABLE

The relevant text is present/expected in this area,
but it cannot be reliably read from the available evidence.

This is not the same as a confirmed missing declaration.
```

---

# 56. Not Observed UX

```text
NOT OBSERVED

The supported declaration was not established
from the available evidence.

This does not by itself establish a legal violation.
```

This distinction is important for trustworthy UX.

---

# 57. Not Applicable UX

```text
NOT APPLICABLE

Country of Origin

Reason:
Inspection context indicates the product is not imported.

This requirement was not evaluated as a compliance failure.
```

Do not visually treat NOT_APPLICABLE as a normal PASS.

---

# 58. Incomplete UX

```text
INCOMPLETE

The available information/evidence is insufficient
to complete this assessment.

Required action:
Provide evidence or resolve the uncertainty.
```

---

# 59. Result Detail Drawer

A requirement result can open a detail panel:

```text
┌───────────────────────────────────────────────┐
│ MRP Inclusive of All Taxes                    │
│                                               │
│ Result: PASS                                  │
│                                               │
│ Observed: ₹199                                │
│ Source: EVD-000001 / Region 03               │
│                                               │
│ Rule: LM-MVP-MRP-001                          │
│                                               │
│ [View Evidence]                               │
└───────────────────────────────────────────────┘
```

This provides explainability without leaving the main workflow.

---

# 60. Evidence Viewer UX

The viewer should support:

- zoom
- pan
- image navigation
- OCR region highlighting
- finding-region highlighting
- source identification

Example:

```text
[Original Image]

       ┌───────────────┐
       │ MRP ₹199      │ ← selected finding
       └───────────────┘

Source: EVD-000001
Region: OCR-004
```

The original image remains identifiable.

---

# 61. Mobile / Small-Screen Design

Evidence capture may occur on phones.

The MVP should therefore support responsive layouts.

Mobile priority:

```text
Evidence Capture
      ↓
Evidence Preview
      ↓
Processing Status
      ↓
Key Findings
      ↓
Verification
```

Complex Reviewer audit layouts may be optimized primarily for desktop.

---

# 62. Responsive Behavior

Desktop:

```text
Two-column evidence/review layouts
```

Tablet:

```text
Reduced side navigation
Stacked detail sections
```

Mobile:

```text
Single-column workflow
Expandable sections
Sticky primary action
```

---

# 63. Accessibility

The UI should support:

- keyboard navigation
- readable text
- meaningful labels
- sufficient visual distinction
- semantic controls
- visible focus states
- accessible error messages
- non-color-only status communication

Compliance status should never rely only on color.

---

# 64. Typography

Typography should prioritize:

- legibility
- clear hierarchy
- dense but readable inspection tables
- strong headings
- compact metadata

Do not use excessively decorative typography.

The product should feel operational and professional.

---

# 65. Color Semantics

Color may reinforce status but must not be the only signal.

Conceptually:

```text
PASS
Positive semantic treatment

POTENTIAL NON-COMPLIANCE
Attention semantic treatment

REQUIRES REVIEW
Review semantic treatment

NOT APPLICABLE
Neutral semantic treatment

INCOMPLETE
Incomplete semantic treatment

PROCESSING FAILED
Error semantic treatment
```

Exact visual palette is an implementation/design-system decision.

---

# 66. Icons

Icons should reinforce meaning:

```text
Evidence       → image/document icon
Processing     → progress/status icon
Review         → inspection/search icon
Warning        → attention icon
Finalized      → lock/record icon
Audit          → timeline/history icon
```

Icons should have accessible labels/tooltips where necessary.

---

# 67. Notifications

Use notifications for:

- upload completion
- processing completion
- processing failure
- successful correction
- submission
- evidence request
- finalization

Avoid excessive notification noise.

---

# 68. Confirmation Dialogs

Confirmation should be required for high-impact actions:

- submit
- reviewer override
- finalization

Example:

```text
Finalize Inspection?

After finalization, the inspection becomes read-only.

[Cancel] [Finalize]
```

Low-risk navigation should not be unnecessarily blocked by confirmation dialogs.

---

# 69. Security UX

The UI should reflect backend permissions.

Examples:

Inspector:

```text
[Verify]
[Submit]
```

Reviewer:

```text
[Review]
[Override]
[Request Evidence]
[Finalize]
```

But hiding a button is not the security control.

The backend remains authoritative.

---

# 70. Role Visibility

Display the active role clearly:

```text
Inspector
```

or:

```text
Reviewer
```

This reduces accidental workflow confusion.

---

# 71. Ownership Messaging

Example:

```text
You are editing this inspection as Inspector.
```

After submission:

```text
This inspection is under Reviewer control.
```

After evidence request:

```text
Reviewer requested additional evidence.
```

After finalization:

```text
This is a finalized historical record.
```

---

# 72. Design for Trust

The UI should avoid exaggerated AI language.

Avoid:

```text
AI says product is illegal
```

Prefer:

```text
Potential Non-Compliance
Supported by:
- observation
- rule
- evidence
```

Avoid:

```text
AI confidence: 99% legal violation
```

Prefer:

```text
AI extraction confidence: High
Evidence: EVD-000001 / Region 03
```

---

# 73. AI Transparency

Where useful, the UI can disclose:

```text
Source:
PaddleOCR + Gemini extraction

Verified by:
Inspector
```

This makes the processing chain understandable.

---

# 74. Provenance UX

A user should be able to trace:

```text
Finding
  ↓
Assessment
  ↓
Declaration
  ↓
OCR Region
  ↓
Evidence
```

This can be implemented through expandable source links.

---

# 75. Correction History UX

When a value was corrected:

```text
MRP

Current:
₹179

Previous system observation:
₹199

Corrected by:
Inspector
Time:
10:20

Reason:
Visible package value differs from OCR extraction.

Assessment:
Recalculated
```

This preserves trust.

---

# 76. Reviewer Audit UX

The Reviewer should have access to:

```text
Evidence
Declarations
Corrections
Applicability
Assessments
Findings
Submission
Evidence Requests
Reviewer Decisions
Finalization
```

The audit view should be chronological and searchable where practical.

---

# 77. Final Record UX

A finalized inspection should present a stable summary:

```text
FINAL INSPECTION RECORD

Inspection
INS-00124

Final Decision
PASS

Evidence
3 items

Supported Checks
6

Reviewer
Reviewer-001

Rule Snapshot
MVP-2026-01

Finalized
15 Sep 2026, 11:04
```

The exact date/time is populated dynamically.

---

# 78. Target Design for Physical ↔ Online Verification

Future design:

```text
PHYSICAL ↔ ONLINE

Physical Evidence
        │
        ▼
Identity Match
        │
        ▼
Field Comparison
        │
        ▼
Comparison Results

Manufacturer     MATCH
MRP              MISMATCH
Net Quantity     MATCH
Consumer Care    MATCH
```

Use:

> Cross-Channel Inconsistency

for mismatches.

Do not label the mismatch as an automatic legal violation.

---

# 79. Target Dashboard Design

Dashboard should support operational awareness rather than decorative analytics.

Useful sections:

```text
Current Workload
Review Queue
Inspection Results
Processing Health
Common Findings
Recent Activity
```

---

# 80. Target Repository Design

The repository should make historical inspections discoverable.

Useful controls:

```text
Search
Filter
Sort
Open
View Evidence
View Audit
View Report
```

The repository must not provide ordinary mutation controls for finalized records.

---

# 81. Design State Model

UI state should reflect backend lifecycle.

Conceptually:

```text
DRAFT
  ↓
EVIDENCE READY
  ↓
PROCESSING
  ↓
ANALYSIS READY
  ↓
VERIFICATION
  ↓
SUBMITTED
  ↓
REVIEW
  ↓
FINALIZED
```

Special states:

```text
PROCESSING FAILED
INCOMPLETE
EVIDENCE REQUESTED
```

Exact lifecycle semantics are authoritative in:

> `07_State_Machine.md`

---

# 82. UI State vs Domain State

The UI may have temporary states such as:

```text
Saving...
Uploading...
Refreshing...
```

These must not be confused with domain states.

Example:

```text
UI:
Saving correction...

Backend:
VERIFICATION
```

After save:

```text
Backend:
VERIFICATION
Assessment recalculated
```

---

# 83. Unsaved Changes

Where forms permit multiple edits, clearly indicate unsaved changes.

Example:

```text
Unsaved changes
[Save] [Discard]
```

High-impact navigation should warn before discarding material edits.

---

# 84. Error Recovery UX

Every recoverable failure should provide a clear next action.

Examples:

```text
Upload failed
→ Retry

AI failed
→ Retry analysis

Evidence insufficient
→ Add evidence / record observation

Conflict
→ Review values

Authorization failure
→ Return to permitted workspace
```

---

# 85. Progressive Disclosure

The UI should reveal complexity only when necessary.

Primary:

```text
Result
Reason
Evidence
Action
```

Expandable:

```text
OCR details
AI metadata
Rule reference
Audit metadata
Technical processing information
```

This keeps the inspection workflow understandable.

---

# 86. MVP Screen Set

The one-day MVP should aim for the smallest useful screen set:

```text
1. Inspection List / Landing
2. New Inspection
3. Evidence Upload/Capture
4. Processing Status
5. Analysis / Declaration Review
6. Applicability + Compliance Results
7. Finding / Evidence Detail
8. Inspector Verification
9. Result / Submission
```

If Reviewer workflow is safely included:

```text
10. Reviewer Queue
11. Reviewer Inspection Detail
12. Evidence Request
13. Finalization
```

Do not add dashboards, advanced repository screens, or secondary workflows before these are functional.

---

# 87. MVP Navigation Flow

```text
Landing
   ↓
New Inspection
   ↓
Evidence
   ↓
Analyze
   ↓
Declarations
   ↓
Applicability
   ↓
Compliance
   ↓
Findings
   ↓
Verification
   ↓
Submit / Result
```

The user should always know:

```text
Where am I?
What happened?
What needs attention?
What can I do next?
```

---

# 88. Primary Action Rule

Each screen should have one dominant next action.

Examples:

```text
New Inspection
→ Continue

Evidence
→ Analyze

Processing
→ Wait / Retry

Analysis
→ Verify Findings

Verification
→ Submit

Reviewer
→ Decide / Finalize
```

Avoid multiple competing primary buttons.

---

# 89. No Dead-End Screens

Every non-terminal screen should provide a meaningful next action.

For example:

```text
PROCESSING FAILED
```

must provide:

```text
Retry
```

or a clear recovery path.

---

# 90. Design QA Requirements

Before release, verify:

- no dead-end workflow
- no ambiguous result labels
- no hidden critical evidence
- no accidental edit of finalized records
- clear Inspector/Reviewer ownership
- clear processing failures
- clear uncertainty
- clear evidence source
- responsive evidence workflow
- accessible status presentation

---

# 91. MVP Design Acceptance Criteria

The MVP UI is acceptable when a representative user can:

```text
[ ] Create an inspection
[ ] Add evidence
[ ] Understand processing state
[ ] View extracted declarations
[ ] Identify uncertainty/conflicts
[ ] Understand applicability
[ ] Understand all six checks
[ ] Open supporting evidence
[ ] Correct extracted information
[ ] See affected results recomputed
[ ] Verify the inspection
[ ] Submit the inspection
[ ] Understand the resulting state
```

Where Reviewer workflow is implemented:

```text
[ ] Reviewer can inspect submitted record
[ ] Reviewer can see audit/history
[ ] Reviewer can request evidence
[ ] Reviewer can override with reason
[ ] Reviewer can finalize
[ ] Finalized record is clearly read-only
```

---

# 92. Design Anti-Patterns

Do not build:

### Anti-pattern 1 — AI Score Dashboard

A large “AI compliance score” that hides the underlying evidence.

### Anti-pattern 2 — Red Everything

Making every uncertainty look like a legal violation.

### Anti-pattern 3 — Hidden Evidence

Showing findings without allowing the user to inspect supporting evidence.

### Anti-pattern 4 — False Certainty

Showing:

> “Violation detected”

when the system only has uncertain or insufficient evidence.

### Anti-pattern 5 — Finalization by UI Only

Disabling an edit button without backend enforcement.

### Anti-pattern 6 — Form Explosion

Requiring dozens of fields before the user can reach the core inspection flow.

### Anti-pattern 7 — Feature Dashboard First

Building analytics before the inspection journey works.

---

# 93. Design System Direction

The UI should use a consistent design system for:

- spacing
- typography
- cards
- buttons
- forms
- status badges
- tables
- dialogs
- evidence viewers
- alerts
- navigation

The exact component library remains an implementation choice.

---

# 94. Technical Design Boundary

The design does not lock:

- a specific component library
- exact color palette
- exact icon library
- exact responsive breakpoints
- exact CSS architecture

These can be selected during implementation while preserving the UX requirements.

---

# 95. Design Relationship to Architecture

The design maps to the architecture as follows:

```text
Web Application
      ↓
Inspection UI
      ↓
Evidence UI
      ↓
Analysis UI
      ↓
Verification UI
      ↓
Reviewer UI
```

The UI communicates with the FastAPI backend.

It does not directly control:

- database
- compliance rules
- evidence integrity
- lifecycle
- finalization

---

# 96. Design Relationship to Domain

The UI must use domain terminology consistently.

Important terms:

```text
Evidence
Observation
Applicability
Assessment
Finding
Verification
Review
Finalization
```

Avoid replacing domain concepts with generic AI terminology.

---

# 97. Design Relationship to Compliance Rules

The UI should expose rule references where they improve explainability.

Example:

```text
Requirement:
MRP Inclusive of All Taxes

Rule:
LM-MVP-MRP-001

Result:
PASS

Evidence:
EVD-000001 / Region 03
```

The detailed legal text need not overwhelm the main workflow.

---

# 98. Design Relationship to Error Handling

Technical error behavior is defined in:

> `10_Error_Handling.md`

The UI must surface the user-relevant consequence and recovery path without exposing unnecessary internal details.

---

# 99. Design Relationship to State Machine

Lifecycle behavior is defined in:

> `07_State_Machine.md`

The UI must not invent lifecycle transitions.

For example:

```text
FINALIZED
```

must not expose a normal:

```text
Edit
```

operation.

---

# 100. Final Design Principle

ComplianceScan should look and behave like a trustworthy inspection workspace.

The interface must make this chain visible:

```text
Evidence
   ↓
Observation
   ↓
AI Understanding
   ↓
Applicability
   ↓
Rule Evaluation
   ↓
Finding
   ↓
Inspector Verification
   ↓
Reviewer Decision
   ↓
Final Record
```

The user should never have to trust an unexplained AI verdict.

The design must consistently communicate:

> **AI finds → Evidence supports → Inspector verifies → Reviewer decides.**

For the one-day MVP:

> **ONE COMPLETE USER JOURNEY > MANY PARTIAL SCREENS.**
