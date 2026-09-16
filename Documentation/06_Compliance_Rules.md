# ComplianceScan — Compliance Rules Specification

**Document:** `06_Compliance_Rules.md`  
**Version:** 1.0  
**Status:** MVP Controlled Rule Specification  
**Product:** ComplianceScan  
**Problem Statement:** SIH'26 PS 26034  
**Domain:** Legal Metrology (Packaged Commodities) inspection assistance  

---

# 1. Purpose

This document defines the controlled compliance-rule behavior used by ComplianceScan for its MVP.

It establishes:

- the legal and regulatory basis of the MVP rule set;
- the supported declaration requirements;
- applicability behavior;
- validation behavior;
- visual assessment boundaries;
- result semantics;
- evidence requirements;
- uncertainty handling;
- rule versioning;
- rule evaluation behavior;
- human decision boundaries;
- explicit exclusions from MVP coverage.

This document is authoritative for **compliance-rule behavior**.

It does not define:

- database implementation;
- API schemas;
- UI layout;
- deployment infrastructure;
- OCR implementation details;
- AI prompt engineering.

Those concerns belong to the specialized architecture, design, API, database, and technical documents.

---

# 2. Legal Basis and Regulatory Context

ComplianceScan is designed around the Legal Metrology framework governing pre-packaged commodities in India.

The Legal Metrology Act, 2009 establishes the statutory framework for standards of weights and measures and regulates trade and commerce in relevant goods. Section 18 specifically addresses declarations on pre-packaged commodities and provides that a pre-packaged commodity must bear prescribed declarations and particulars in the prescribed manner. citeturn0search12turn0search0

The Legal Metrology (Packaged Commodities) Rules, 2011 provide the detailed packaged-commodity requirements. The official consolidated material published by the Department of Consumer Affairs incorporates amendments and should be treated as the source material for maintaining the controlled rule snapshot. citeturn0search16turn0search14

The rules and amendments have changed over time. Therefore, ComplianceScan must not encode the legal framework as if the 2011 text were permanently unchanged. The application uses a **versioned, controlled MVP rule snapshot**.

## 2.1 Legal Authority Boundary

ComplianceScan is an inspection-assistance system.

It does not replace:

- the Legal Metrology Act;
- the Legal Metrology (Packaged Commodities) Rules;
- applicable amendments;
- notifications;
- orders;
- competent-authority interpretation;
- authorized officer judgment;
- applicable court decisions or enforcement guidance.

The application must present its output as a system assessment and potential issue identification, not as an autonomous legal determination.

Core principle:

> **AI finds → Evidence supports → Inspector verifies → Reviewer decides.**

---

# 3. Regulatory Source Register

The MVP rule set should maintain a source register containing at least:

| Source | Role in ComplianceScan |
|---|---|
| Legal Metrology Act, 2009 | Primary statutory framework |
| Legal Metrology (Packaged Commodities) Rules, 2011 | Packaged-commodity declaration and presentation requirements |
| Official amendments to the Packaged Commodities Rules | Updates to the controlled rule set |
| Department of Consumer Affairs consolidated material | Controlled regulatory reference source |
| Applicable official notifications/advisories | Supporting interpretation where explicitly adopted into the MVP rule snapshot |

The Legal Metrology Act's Section 18 is the statutory anchor for prescribed declarations on pre-packaged commodities. citeturn0search12

The Department of Consumer Affairs maintains the Legal Metrology regulatory materials, including the Packaged Commodities Rules and amendment history. citeturn0search0turn0search16

## 3.1 Controlled Snapshot Requirement

Every compliance evaluation must identify the rule snapshot used.

Conceptually:

```text
Rule Snapshot
├── Rule Set ID
├── Version
├── Effective From
├── Source References
├── Requirement Definitions
├── Applicability Logic
├── Validation Logic
└── Controlled Status
```

A finalized inspection retains the rule snapshot reference used at the time of evaluation.

---

# 4. MVP Rule Philosophy

The MVP intentionally implements a **controlled subset** of packaged-commodity compliance requirements.

The MVP does not claim universal legal coverage.

The MVP focuses on six core declaration areas:

1. Manufacturer / Packer / Importer
2. Common / Generic Product Name
3. Net Quantity + Standard Unit
4. Month / Year of Manufacture / Packing / Import
5. Maximum Retail Price (MRP), inclusive of all taxes
6. Consumer Care Details

Country of Origin is implemented as an **applicability-driven requirement** for imported commodities.

Additional requirements that may apply under the broader regulatory framework are explicitly outside the MVP rule-evaluation scope unless separately implemented and versioned.

---

# 5. Supported Result Vocabulary

The compliance subsystem uses the following result vocabulary:

| Result | Meaning |
|---|---|
| `PASS` | The supported requirement was evaluated and no supported non-compliance condition was identified in the available evidence. |
| `POTENTIAL_NON_COMPLIANCE` | The available evidence indicates a supported requirement may not be satisfied. Human review remains required. |
| `REQUIRES_REVIEW` | The system cannot safely resolve the condition and human review is required. |
| `NOT_APPLICABLE` | The supported requirement does not apply under the established applicability context. |
| `INCOMPLETE` | Required information or evidence is insufficient to complete the supported assessment. |
| `PROCESSING_FAILED` | A technical processing failure prevented reliable evaluation. |

These values are intentionally distinct.

```text
NOT_APPLICABLE ≠ PASS
INCOMPLETE ≠ POTENTIAL_NON_COMPLIANCE
PROCESSING_FAILED ≠ NON_COMPLIANCE
NOT_OBSERVED ≠ PROVEN MISSING
UNREADABLE ≠ PROVEN MISSING
```

---

# 6. Compliance Evaluation Model

Every supported requirement follows this logical sequence:

```text
Evidence
   ↓
Observation
   ↓
Declaration Understanding
   ↓
Applicability
   ↓
Evidence Sufficiency
   ↓
Rule Evaluation
   ↓
System Assessment
   ↓
Inspector Verification
   ↓
Reviewer Decision
```

A rule must not be evaluated solely from a free-form AI response.

The compliance engine consumes validated structured domain data.

---

# 7. Core Rule Object

A controlled rule is conceptually represented as:

```text
ComplianceRule
├── Rule ID
├── Rule Version
├── Requirement ID
├── Name
├── Legal Reference
├── Applicability Condition
├── Required Observation
├── Validation Logic
├── Evidence Expectations
├── Assessment Mapping
├── Human Review Conditions
└── Source Provenance
```

Example:

```text
Rule ID: PCR-MVP-NQ-001
Requirement: Net Quantity
Applicability: Supported packaged commodity scenario
Observation: Net quantity + unit
Validation: Quantity and recognized standard unit must be established
Evidence: Source declaration region
Failure: POTENTIAL_NON_COMPLIANCE or INCOMPLETE depending on evidence state
```

---

# 8. Rule Evaluation Contract

The compliance engine must receive:

```text
Validated Declarations
+
Observation Status
+
Applicability State
+
Evidence Sufficiency
+
Controlled Rule Snapshot
```

It returns:

```text
System Assessment
+
Reason
+
Rule Reference
+
Evidence References
+
Provenance
```

The engine must not receive an instruction such as:

> "Decide whether this package is legally compliant."

Instead it evaluates explicit supported conditions.

---

# 9. Rule Status Model

Each requirement may have an observation state independent from its compliance result.

Observation states:

- `OBSERVED`
- `NOT_OBSERVED`
- `UNCERTAIN`
- `UNREADABLE`
- `CONFLICTING`

These states are not themselves legal conclusions.

Example:

```text
Net Quantity
Observation = UNREADABLE
        ↓
Evidence insufficient
        ↓
Assessment = INCOMPLETE / REQUIRES_REVIEW
```

The system must not transform `UNREADABLE` into `POTENTIAL_NON_COMPLIANCE` without sufficient evidence and a rule-supported reason.

---

# 10. Rule R-01 — Manufacturer / Packer / Importer Declaration

## 10.1 Requirement

The package should identify the applicable responsible entity declaration, such as manufacturer, packer, or importer, according to the regulatory context applicable to the package.

The broader rules prescribe declarations concerning the manufacturer, packer and/or importer. The exact legal wording and applicability must be taken from the controlled rule snapshot in force for the inspection.

## 10.2 MVP Observation

The system attempts to establish:

```text
Entity Type
Entity Name / Address Information
Source Evidence
Observation Status
```

Possible entity types:

- `MANUFACTURER`
- `PACKER`
- `IMPORTER`
- `MANUFACTURER_OR_PACKER`
- `UNKNOWN`

## 10.3 PASS Condition

`PASS` may be produced when:

- the applicable declaration is established from evidence;
- the observed declaration satisfies the controlled MVP validation conditions;
- evidence is sufficient;
- no unresolved conflict exists.

## 10.4 Potential Non-Compliance

`POTENTIAL_NON_COMPLIANCE` may be produced when reliable evidence establishes that an applicable declaration is present but fails a supported validation condition, or when a required declaration is sufficiently established as absent within the defined evidence coverage.

## 10.5 Review Conditions

Use `REQUIRES_REVIEW` when:

- multiple responsible entities create a conflict;
- the package context is ambiguous;
- imported/manufactured/packed status cannot be established;
- declaration wording is legally ambiguous;
- evidence is insufficient to establish absence.

---

# 11. Rule R-02 — Common / Generic Product Name

## 11.1 Requirement

The package should declare the common or generic name of the commodity as required by the controlled rule snapshot.

## 11.2 Observation

The AI understanding layer may identify candidate product-name text from OCR observations.

The application should preserve:

- original OCR text;
- selected declaration value;
- normalized representation if used;
- source region;
- confidence;
- observation status.

## 11.3 Validation

Validation should establish that the observed value functions as the common/generic product description within the supported scenario.

The MVP should not attempt unrestricted semantic classification of every possible commodity category.

## 11.4 Failure Handling

If text is visible but its meaning is ambiguous:

```text
UNCERTAIN
   ↓
REQUIRES_REVIEW
```

If the relevant region is unreadable:

```text
UNREADABLE
   ↓
INCOMPLETE / REQUIRES_REVIEW
```

---

# 12. Rule R-03 — Net Quantity + Standard Unit

## 12.1 Requirement

The package must provide a supported net quantity declaration expressed using the applicable standard unit or number representation.

The Legal Metrology Act prohibits indicating the net quantity of a pre-packaged commodity otherwise than in accordance with standard units of weight, measure or numeration, subject to the Act and applicable rules. citeturn0search17

## 12.2 Observation Model

```text
Net Quantity
├── Numeric Value
├── Unit / Number Representation
├── Normalized Quantity
├── Source Region
├── OCR Confidence
└── Observation Status
```

## 12.3 Supported Validation

The MVP validates:

- quantity is present or sufficiently established;
- numeric value is interpretable;
- unit is present where required;
- unit is within the controlled supported unit set;
- contradictory quantity declarations are not silently resolved.

## 12.4 Conflicting Quantities

Example:

```text
Front: 500 g
Side: 450 g
```

The system must preserve both observations.

Result:

```text
CONFLICTING
   ↓
REQUIRES_REVIEW
```

It must not select one value merely because one has higher AI confidence.

## 12.5 Missing vs Unreadable

If the evidence sufficiently covers the relevant declaration area and no net quantity declaration is observed, a potential missing-declaration condition may be raised.

If the relevant area is blurred, obstructed, cropped, or unreadable, the result should generally be `INCOMPLETE` or `REQUIRES_REVIEW`, not an automatic finding of absence.

---

# 13. Rule R-04 — Month / Year of Manufacture / Packing / Import

## 13.1 Requirement

The package must be evaluated for the applicable month/year declaration concerning manufacture, packing, or import as required by the controlled rule snapshot.

## 13.2 Observation Model

```text
Date Declaration
├── Date Type
│   ├── MANUFACTURE
│   ├── PACKING
│   └── IMPORT
├── Month
├── Year
├── Raw Text
├── Normalized Date
├── Source Evidence
└── Observation Status
```

## 13.3 Validation

The MVP should validate:

- recognizable month/year information;
- plausible date structure;
- applicable date type;
- absence of unresolved contradictions.

The application should not infer a manufacture/packing/import date from unrelated timestamps such as upload time or image metadata.

## 13.4 Ambiguity

If a package shows multiple date-like values and the system cannot reliably classify them:

```text
CONFLICTING / UNCERTAIN
        ↓
REQUIRES_REVIEW
```

---

# 14. Rule R-05 — MRP Inclusive of All Taxes

## 14.1 Requirement

The package must be evaluated for the applicable maximum retail price declaration, including the required tax-inclusive presentation under the controlled rule snapshot.

The Packaged Commodities Rules contain requirements concerning retail sale price and prohibit sale above the applicable retail sale price in the circumstances covered by the rules. citeturn0search14

## 14.2 Observation Model

```text
MRP
├── Numeric Value
├── Currency Marker / Context
├── Tax-Inclusive Indicator / Required Form
├── Source Region
├── OCR Confidence
└── Observation Status
```

## 14.3 Validation

The MVP may establish:

- MRP is observable;
- numeric price is parseable;
- supported currency context is present or otherwise unambiguous;
- required tax-inclusive presentation is consistent with the controlled rule snapshot.

## 14.4 Important Boundary

ComplianceScan must distinguish:

```text
MRP declaration on package
```

from:

```text
Actual selling price charged at point of sale
```

The MVP declaration engine does not claim to verify the actual transaction price unless that data is explicitly provided and the corresponding rule is implemented.

---

# 15. Rule R-06 — Consumer Care Details

## 15.1 Requirement

The package must be evaluated for the applicable consumer-care contact declaration required by the controlled rule snapshot.

## 15.2 Observation Model

```text
Consumer Care
├── Name / Entity if present
├── Address if present
├── Phone / Contact
├── Email / Other supported contact
├── Raw Text
├── Source Region
└── Observation Status
```

## 15.3 Validation

The MVP should establish whether a recognizable consumer-care contact declaration is present and sufficiently readable.

It should not attempt to prove that:

- a phone number is currently reachable;
- an email address is operational;
- a company legally owns the contact;
- the consumer will receive a response.

Those are outside the package-label declaration check.

---

# 16. Country of Origin — Applicability-Driven Rule

Country of Origin is included as an applicability-driven requirement rather than one of the six universal MVP checks.

## 16.1 Imported = YES

```text
Imported = YES
       ↓
Country of Origin
       ↓
APPLICABLE
```

The system evaluates the applicable country-of-origin declaration under the controlled rule snapshot.

## 16.2 Imported = NO

```text
Imported = NO
       ↓
Country of Origin
       ↓
NOT_APPLICABLE
```

## 16.3 Imported = UNKNOWN

```text
Imported = UNKNOWN
       ↓
Cannot safely determine applicability
       ↓
REQUIRES_REVIEW / INCOMPLETE
```

The system must not guess import status from a weak signal.

## 16.4 Evidence Requirement

Country-of-origin assessment must retain the evidence supporting the imported/not-imported context where that context is material to the decision.

---

# 17. Additional Regulatory Requirements Outside Core MVP

The broader Legal Metrology (Packaged Commodities) Rules contain requirements beyond the six core MVP declaration areas.

Examples may include, depending on commodity and circumstances:

- best before / use by declarations where applicable;
- unit sale price requirements where applicable;
- dimensions for relevant commodities;
- standard package-size requirements;
- commodity/category-specific requirements;
- placement/presentation requirements;
- exemptions and special cases;
- promotional/grouped package conditions;
- wholesale-package requirements;
- sector-specific or commodity-specific provisions.

The official regulatory material demonstrates that the rules contain requirements beyond the narrow MVP subset. citeturn0search16turn0search14

These are **not silently treated as universally compliant merely because the six MVP checks pass**.

The product should communicate that the MVP is a controlled subset.

---

# 18. Best Before / Use By Boundary

The broader rules can require date-related declarations where applicable.

The MVP does not implement a universal best-before/use-by legal rule.

Therefore:

```text
Best Before / Use By
        ↓
Not part of core MVP evaluation
```

This must not be represented as:

```text
Best Before / Use By = PASS
```

Instead the UI/report may state that the field is outside the supported MVP rule set where appropriate.

Future support requires:

- applicability logic;
- controlled rule definition;
- evidence semantics;
- validation logic;
- tests;
- versioned legal source.

---

# 19. Unit Sale Price Boundary

Unit Sale Price is deliberately excluded from the current MVP because its applicability and presentation requirements are sensitive to commodity/category and regulatory context.

The system must not silently infer:

```text
Unit Sale Price absent
      ↓
Non-compliant
```

unless a future controlled rule explicitly establishes applicability and validation.

---

# 20. Category-Specific Rules Boundary

The MVP is not a universal commodity-classification engine.

Category-specific requirements are excluded unless explicitly represented in the controlled rule snapshot.

Therefore:

```text
Unknown / unsupported category-specific condition
                 ↓
REQUIRES_REVIEW / OUTSIDE MVP SCOPE
```

The system must not invent a category-specific legal requirement based solely on an AI model's general knowledge.

---

# 21. Placement and Presentation Assessment

The broader regulatory framework includes requirements relating to how declarations are presented and made legible/prominent.

The MVP provides only a bounded visual assessment.

## 21.1 Supported Visual Signals

The system may assess:

- whether text is visible;
- whether text is severely obscured;
- whether the relevant region can be located;
- whether the declaration appears reasonably readable from the supplied evidence;
- whether a potential presentation issue warrants review.

## 21.2 Legal Boundary

A photograph does not necessarily establish physical print dimensions or all package-display conditions.

Therefore the system must not state a definitive legal font-size violation from pixels alone without appropriate scale information.

Preferred wording:

> **Potential readability / presentation issue — reviewer verification required.**

---

# 22. Font Size Assessment

Font-size assessment is a visual warning in the MVP.

It is not a definitive legal measurement unless the evidence contains the required physical scale/calibration and the relevant rule is implemented.

```text
Image Pixels
     ↓
Visual Estimate
     ↓
Potential Warning
     ↓
Human Verification
```

Do not convert an uncalibrated pixel measurement directly into a legal conclusion.

---

# 23. Applicability-First Evaluation

Every requirement should have an applicability decision before compliance evaluation.

```text
Requirement
    ↓
Applicable?
 ┌──┴────────────┐
 │               │
YES              NO
 │               │
 ▼               ▼
Evaluate     NOT_APPLICABLE
```

If applicability cannot be established:

```text
UNKNOWN
   ↓
REQUIRES_REVIEW / INCOMPLETE
```

This prevents false findings caused by applying a requirement to a context where it does not apply.

---

# 24. Evidence Sufficiency Rules

A compliance assessment requires adequate evidence for the proposition being assessed.

## 24.1 Sufficient Evidence

Evidence is sufficient when the relevant declaration or condition can be established with reasonable confidence from the available evidence.

## 24.2 Insufficient Evidence

Evidence is insufficient when:

- relevant package surfaces are missing;
- text is unreadable;
- the relevant area is obstructed;
- image resolution prevents interpretation;
- conflicting evidence cannot be resolved.

## 24.3 Absence Rule

The system must distinguish:

```text
Not observed because area was not captured
```

from:

```text
Not observed despite adequate evidence coverage
```

Only the latter can potentially support a missing-declaration finding, and even then the rule and evidence must support that conclusion.

---

# 25. Evidence-to-Finding Requirement

Every potential non-compliance finding should have a traceable evidence basis.

Minimum conceptual chain:

```text
Finding
  ↓
Rule Reference
  ↓
Observed / Expected Condition
  ↓
Evidence Reference
  ↓
Source Region where available
```

A finding without sufficient provenance should be marked for review rather than presented as a proven fact.

---

# 26. Confidence Separation

ComplianceScan must maintain separate confidence dimensions.

```text
OCR Confidence
       ≠
AI Extraction Confidence
       ≠
Evidence Sufficiency
       ≠
Compliance Result
```

## OCR Confidence

Confidence in text recognition.

## AI Extraction Confidence

Confidence that OCR observations were correctly mapped to a declaration.

## Evidence Sufficiency

Confidence that available evidence is sufficient to establish the relevant condition.

## Compliance Result

The deterministic assessment produced by applying the rule to validated data.

A high confidence value in one layer cannot automatically override uncertainty in another.

---

# 27. Conflict Handling

If multiple values conflict:

```text
Value A
  │
  ├── conflict ──► REQUIRES_REVIEW
  │
Value B
```

The system must:

1. preserve all relevant observations;
2. preserve source evidence;
3. avoid silent selection;
4. identify the conflict;
5. route the condition to human review.

Example:

```text
MRP = ₹199
MRP = ₹249
        ↓
CONFLICTING
        ↓
REQUIRES_REVIEW
```

---

# 28. Unreadable Handling

`UNREADABLE` means that the relevant content may exist, but the available evidence cannot reliably establish its value.

It is not equivalent to absence.

```text
Unreadable declaration
        ↓
Do not guess
        ↓
INCOMPLETE / REQUIRES_REVIEW
```

The Inspector may add supplemental evidence.

---

# 29. Not Observed Handling

`NOT_OBSERVED` means that the system did not identify the declaration in the analyzed evidence.

It does not automatically mean that the declaration is absent from the physical package.

The system should consider evidence coverage.

```text
NOT_OBSERVED
     │
     ├── Coverage insufficient → INCOMPLETE
     │
     └── Coverage sufficient + rule supports absence assessment
                              ↓
                       POTENTIAL_NON_COMPLIANCE
```

---

# 30. Processing Failure Handling

Technical failures must be separated from compliance results.

Examples:

- OCR service failure;
- AI provider timeout;
- malformed AI response;
- image decoder failure;
- object-storage failure;
- processing worker failure.

These produce controlled processing states.

```text
Technical Failure
       ↓
PROCESSING_FAILED
```

Never:

```text
Technical Failure
       ↓
POTENTIAL_NON_COMPLIANCE
```

---

# 31. AI Rule Boundary

AI may assist with:

- OCR interpretation;
- semantic declaration extraction;
- normalization;
- date interpretation;
- conflict identification;
- context mapping;
- uncertainty detection.

AI must not:

- create legal requirements;
- decide applicability from unsupported assumptions;
- invent missing declarations;
- silently resolve conflicts;
- change controlled rules;
- finalize an inspection;
- modify original evidence;
- rewrite historical decisions.

---

# 32. Deterministic Rule Boundary

The compliance engine should use explicit deterministic logic wherever the MVP rule can be represented deterministically.

Example:

```text
IF
    applicable = TRUE
AND quantity_observation.status = OBSERVED
AND quantity.value is valid
AND quantity.unit is supported
AND evidence_sufficient = TRUE
THEN
    PASS
```

Another example:

```text
IF
    applicable = TRUE
AND evidence_sufficient = TRUE
AND required_declaration = NOT_OBSERVED
AND absence_is_established = TRUE
THEN
    POTENTIAL_NON_COMPLIANCE
```

The exact predicates are versioned with the rule.

---

# 33. PASS Semantics

`PASS` means:

> The supported requirement was evaluated using the controlled rule snapshot and available evidence, and no supported non-compliance condition was identified.

It does **not** mean:

- the entire package is legally compliant in every respect;
- every statutory requirement was checked;
- no hidden defect exists;
- the AI guarantees correctness.

This distinction must appear in product/report language where necessary.

---

# 34. POTENTIAL_NON_COMPLIANCE Semantics

`POTENTIAL_NON_COMPLIANCE` means:

> The supported rule evaluation identified a condition that may represent non-compliance, based on the available evidence and the controlled rule snapshot.

It remains subject to human verification and Reviewer decision.

Preferred report wording:

> Potential non-compliance identified — reviewer verification required.

Avoid:

> AI confirmed a legal violation.

---

# 35. REQUIRES_REVIEW Semantics

Use `REQUIRES_REVIEW` when the system identifies an unresolved issue requiring human interpretation.

Examples:

- conflicting declarations;
- ambiguous date type;
- uncertain applicability;
- ambiguous product identity;
- unclear presentation condition;
- uncertain imported status;
- AI uncertainty.

---

# 36. INCOMPLETE Semantics

Use `INCOMPLETE` when the system cannot complete the supported assessment because necessary evidence or structured information is missing.

Examples:

- package side not captured;
- declaration area obstructed;
- unreadable image;
- required context missing.

The Inspector may address the condition with supplemental evidence.

---

# 37. NOT_APPLICABLE Semantics

`NOT_APPLICABLE` means the controlled rule explicitly does not apply to the established context.

Example:

```text
Imported = NO
Country of Origin
      ↓
NOT_APPLICABLE
```

It must not be counted as a successful compliance check in the same way as `PASS`.

---

# 38. Human Decision Boundary

The compliance-rule engine stops at system assessment.

```text
Rules
  ↓
System Assessment
  ↓
Inspector Verification
  ↓
Reviewer Decision
```

The Reviewer may:

- confirm;
- correct/override with reason;
- request additional evidence;
- finalize.

A Reviewer override must preserve:

- previous assessment;
- new decision;
- actor;
- timestamp;
- reason;
- supporting evidence where applicable.

---

# 39. Inspector Correction Rules

An Inspector may correct extracted values when the evidence supports the correction.

Example:

```text
AI extracted:
5000 ml

Inspector correction:
500 ml

Reason:
OCR decimal/character interpretation error
```

The system must preserve:

```text
Original AI Value
        ↓
Correction
        ↓
Corrected Value
        ↓
Actor + Time + Reason
```

Affected compliance state must be recomputed.

---

# 40. Reviewer Override Rules

A Reviewer may override a system assessment when the Reviewer has sufficient basis.

The override must capture:

- previous result;
- final Reviewer result;
- reason;
- Reviewer identity;
- timestamp;
- evidence references where appropriate.

Example:

```text
System:
POTENTIAL_NON_COMPLIANCE

Reviewer:
PASS

Reason:
Declaration was present on the reverse panel captured in supplemental evidence.
```

The original system assessment remains part of the audit history.

---

# 41. Evidence Request Rules

A Reviewer may request additional evidence when the current evidence is insufficient.

Each request receives a stable Evidence Request ID.

```text
ER-00017
```

The request should identify:

- what condition must be established;
- why current evidence is insufficient;
- requested evidence type if relevant;
- requesting Reviewer;
- timestamp;
- status.

The Inspector may respond with:

1. supplemental evidence;
2. manual observation;
3. an explanation that the condition cannot be established.

The request must not imply that a particular result is expected.

---

# 42. Recalculation Rules

If an upstream value changes, all affected downstream compliance assessments must be invalidated and recomputed.

```text
Declaration Change
       ↓
Affected Applicability
       ↓
Affected Compliance
       ↓
Affected Findings
```

Unrelated assessments should remain unchanged.

The system must preserve the previous state in the audit history.

---

# 43. Rule Versioning

Every rule must be versioned.

Example:

```text
PCR-MVP-NQ-001
Version: 1.0
```

If the legal requirement changes:

```text
PCR-MVP-NQ-001 v1.0
        ↓
PCR-MVP-NQ-001 v2.0
```

Historical inspections retain the earlier rule snapshot.

Future inspections use the applicable current controlled snapshot.

---

# 44. Rule Change Governance

A rule change should not be made by changing application code silently.

A controlled rule update should include:

1. source reference;
2. effective date;
3. requirement affected;
4. old behavior;
5. new behavior;
6. applicability impact;
7. test cases;
8. reviewer/approval metadata;
9. new rule version.

The MVP may maintain this as a controlled configuration/repository process rather than a full Rule Manager UI.

---

# 45. Rule Snapshot and Finalization

At finalization, the system must preserve the rule context used for the final assessment.

```text
Inspection
   ↓
Rule Snapshot vX
   ↓
Assessment
   ↓
Reviewer Decision
   ↓
Final Snapshot
```

A future rule update must not mutate the historical final record.

---

# 46. Evidence Integrity and Legal Truth

SHA-256 provides integrity/change detection for stored evidence bytes.

It does not prove:

- that the photograph is authentic;
- that the package was photographed at the claimed location;
- that the package itself is genuine;
- that the depicted declaration is legally sufficient;
- that the observed condition existed outside the evidence capture context.

Therefore:

```text
Hash Integrity
      ≠
Truth / Authenticity
```

---

# 47. Physical ↔ Online Rule Boundary

If the optional physical-to-online verification feature is used, the comparison engine may identify:

- product identity mismatch;
- declaration mismatch;
- quantity mismatch;
- MRP mismatch;
- other explicitly supported field inconsistencies.

The output is:

> `CROSS_CHANNEL_INCONSISTENCY`

This is not automatically equivalent to legal non-compliance.

The Reviewer must interpret the significance.

---

# 48. Rule Evaluation Example — Compliant Scenario

```text
Evidence
  ↓
Manufacturer declaration observed
  ↓
Generic name observed
  ↓
500 g observed
  ↓
Month/year observed
  ↓
MRP observed
  ↓
Consumer care observed
  ↓
Imported = NO
  ↓
Country of Origin = NOT_APPLICABLE
  ↓
All supported validations pass
  ↓
System Assessment
```

Result may be:

```text
PASS
```

This means the supported MVP checks passed, not that every possible statutory condition has been established.

---

# 49. Rule Evaluation Example — Missing Declaration

```text
Evidence coverage sufficient
        ↓
Relevant declaration area inspected
        ↓
Required declaration not observed
        ↓
Absence sufficiently established
        ↓
Rule supports missing-declaration assessment
        ↓
POTENTIAL_NON_COMPLIANCE
```

Evidence and rule references must be attached to the finding.

---

# 50. Rule Evaluation Example — Unreadable Evidence

```text
Package image
   ↓
Relevant area severely blurred
   ↓
Declaration cannot be established
   ↓
UNREADABLE
   ↓
INCOMPLETE / REQUIRES_REVIEW
```

Do not produce:

```text
UNREADABLE → Missing → Non-compliant
```

---

# 51. Rule Evaluation Example — Conflict

```text
Image A → MRP ₹199
Image B → MRP ₹249
       ↓
CONFLICTING
       ↓
REQUIRES_REVIEW
       ↓
Reviewer resolves using evidence
```

No silent winner selection is permitted.

---

# 52. Rule Evaluation Example — Processing Failure

```text
Image
 ↓
PaddleOCR unavailable
 ↓
OCR processing fails
 ↓
PROCESSING_FAILED
```

The system must not conclude that declarations are absent merely because OCR failed.

---

# 53. Rule Evaluation Example — Imported Product

```text
Import context established = YES
            ↓
Country of Origin applicable
            ↓
Country declaration observed
            ↓
Validation succeeds
            ↓
PASS
```

If the country declaration cannot be established:

```text
Import = YES
     ↓
Country of Origin applicable
     ↓
Evidence insufficient
     ↓
INCOMPLETE / REQUIRES_REVIEW
```

---

# 54. Rule Evaluation Example — Non-Imported Product

```text
Import context = NO
       ↓
Country of Origin
       ↓
NOT_APPLICABLE
```

The system must not generate a missing-country-of-origin finding solely because the package lacks a country-of-origin declaration when the controlled applicability condition says it is not applicable.

---

# 55. Rule Evaluation Example — AI API Failure

```text
OCR
 ↓
Gemini API request
 ↓
Timeout
 ↓
Retry according to technical policy
 ↓
Still failed
 ↓
PROCESSING_FAILED
```

The inspection may remain incomplete until processing succeeds or the human workflow provides an alternative supported path.

---

# 56. Rule Evaluation Example — Inspector Correction

```text
AI:
MRP = ₹199

Inspector sees evidence:
MRP = ₹199.00

Correction:
Normalize representation

↓
Revalidate
↓
Recompute affected state
```

The correction does not alter the original OCR output.

---

# 57. Rule Evaluation Example — Reviewer Override

```text
System:
POTENTIAL_NON_COMPLIANCE

Reviewer examines supplemental evidence
        ↓
Evidence establishes declaration
        ↓
Reviewer decision:
PASS
        ↓
Override reason recorded
```

The previous system assessment remains auditable.

---

# 58. Reporting Rules

Reports should distinguish:

### Supported Pass

> Supported MVP requirements evaluated without an identified issue.

### Potential Non-Compliance

> A supported MVP rule condition may not be satisfied based on available evidence; human decision required.

### Requires Review

> The system could not safely resolve the condition.

### Incomplete

> Required information/evidence was insufficient.

### Not Applicable

> The supported requirement does not apply under the established context.

### Processing Failed

> Technical processing prevented reliable assessment.

Reports must not collapse all six states into a binary compliant/non-compliant label.

---

# 59. Prohibited Rule Behaviors

The implementation must not:

1. invent a legal requirement;
2. silently apply an inapplicable requirement;
3. treat OCR failure as missing declaration;
4. treat unreadable as absent without evidence support;
5. silently choose between conflicting values;
6. let AI modify rule definitions;
7. let AI finalize an inspection;
8. mutate finalized rule snapshots;
9. use a future rule version to rewrite historical assessments;
10. represent a limited MVP PASS as universal legal compliance;
11. claim a definitive font-size violation from an uncalibrated image;
12. treat an online/physical mismatch as automatically unlawful;
13. treat a hash as proof of authenticity;
14. turn technical failure into legal non-compliance.

---

# 60. MVP Rule Coverage Matrix

| Rule Area | MVP Status | Applicability | Primary Evidence | System Result |
|---|---|---|---|---|
| Manufacturer / Packer / Importer | Supported | Context-dependent | Package declaration | Supported assessment |
| Common / Generic Name | Supported | Supported generic scenario | Product label | Supported assessment |
| Net Quantity + Unit | Supported | Supported packaged commodity | Quantity declaration | Supported assessment |
| Month / Year | Supported | Applicable package context | Date declaration | Supported assessment |
| MRP inclusive of taxes | Supported | Applicable retail package context | Price declaration | Supported assessment |
| Consumer Care | Supported | Supported package context | Contact declaration | Supported assessment |
| Country of Origin | Supported as applicability-driven | Imported products | Origin declaration + import context | Supported assessment |
| Best Before / Use By | Outside core MVP | Where applicable | Date declaration | Not universally evaluated |
| Unit Sale Price | Outside core MVP | Context-dependent | Price declarations | Not evaluated |
| Category-specific rules | Outside core MVP | Commodity-dependent | Context-specific | Not universally evaluated |
| Universal font-size legal verdict | Outside core MVP | Context-dependent | Calibrated physical evidence required | Visual warning only |
| Universal placement legality | Outside core MVP | Context-dependent | Full package context required | Bounded visual assessment |

---

# 61. Minimum Evidence Expectations by Rule

| Requirement | Minimum conceptual evidence |
|---|---|
| Manufacturer/Packer/Importer | Clear declaration region + context establishing applicable entity type |
| Generic Name | Clear product-name region |
| Net Quantity | Clear quantity + unit region |
| Month/Year | Clear date region + enough context to identify date type |
| MRP | Clear price declaration region |
| Consumer Care | Clear contact declaration region |
| Country of Origin | Import applicability evidence + origin declaration region |

The actual number of photographs is not fixed.

The system should use adaptive evidence capture based on coverage.

---

# 62. Evidence Coverage Principle

The system should ask:

> **Do we have enough evidence to establish this particular condition?**

It should not ask only:

> **How many photos were uploaded?**

Therefore, there is no universal fixed requirement such as "three photos per package".

---

# 63. Rule Testability

Every implemented rule should have test cases covering at least:

1. clear compliant observation;
2. clear potential non-compliance;
3. missing evidence;
4. unreadable evidence;
5. conflicting observations;
6. non-applicable condition;
7. unknown applicability;
8. malformed structured data;
9. processing failure;
10. corrected observation;
11. Reviewer override;
12. rule-version change.

---

# 64. Rule Determinism Requirement

Given identical:

- validated domain inputs;
- applicability state;
- rule snapshot;
- evidence sufficiency state;

an evaluation should produce the same deterministic system assessment.

AI may be used upstream to generate observations, but the final rule evaluation itself should not depend on uncontrolled free-form model reasoning.

---

# 65. Rule Provenance Requirement

Each compliance assessment must be traceable to:

```text
Assessment
  ↓
Rule ID + Version
  ↓
Applicability State
  ↓
Observed Values
  ↓
Evidence References
  ↓
Processing / Correction History
```

This makes the result explainable and auditable.

---

# 66. Legal Source Maintenance

The rule source register must be reviewed whenever the controlled MVP rules are changed.

The Department of Consumer Affairs publishes Legal Metrology material and amendment records, including the Packaged Commodities Rules and later amendments. citeturn0search0turn0search16

Because the rules have been amended repeatedly, implementation must use an explicit version and effective date rather than assuming that an old rule text is permanently current. citeturn0search1turn0search16

The project should perform a legal-source review before any public deployment intended for operational use.

---

# 67. Controlled Rule Snapshot Example

```text
Rule Set
──────────────
ID: PCR-MVP
Version: 1.0
Status: CONTROLLED
Effective From: <controlled release date>

Requirements
──────────────
R-01 Manufacturer/Packer/Importer
R-02 Common/Generic Name
R-03 Net Quantity + Unit
R-04 Month/Year
R-05 MRP Inclusive of Taxes
R-06 Consumer Care
R-07 Country of Origin (applicability-driven)
```

The actual release should record the approved effective date and source references.

---

# 68. Rule Execution Pseudocode

```text
for requirement in controlled_rule_snapshot:

    applicability = evaluate_applicability(requirement, context)

    if applicability == NOT_APPLICABLE:
        result = NOT_APPLICABLE
        continue

    if applicability == UNKNOWN:
        result = REQUIRES_REVIEW
        continue

    observation = get_validated_observation(requirement)

    evidence = evaluate_evidence_sufficiency(requirement, observation)

    if evidence == INSUFFICIENT:
        result = INCOMPLETE
        continue

    if observation.status == CONFLICTING:
        result = REQUIRES_REVIEW
        continue

    if observation.status == UNREADABLE:
        result = INCOMPLETE
        continue

    result = deterministic_rule_evaluation(
        requirement,
        applicability,
        observation,
        evidence
    )

    create_finding_if_required(result)
```

The exact implementation belongs in the compliance-engine code and must remain consistent with this contract.

---

# 69. Relationship to Domain Specification

`05_Domain_Specification.md` defines domain concepts such as:

- Observation Status;
- Declaration;
- Applicability;
- Finding;
- Review;
- Final Snapshot.

This document defines how those concepts are used for compliance-rule evaluation.

If a domain-semantic conflict is discovered, the domain specification and this rule specification must be reconciled explicitly rather than silently diverging.

---

# 70. Relationship to State Machine

`07_State_Machine.md` defines lifecycle transitions.

This document defines assessment semantics inside those lifecycle states.

For example:

```text
Processing
   ↓
System Assessment
   ↓
Inspector Verification
   ↓
Submitted
   ↓
Reviewer Decision
   ↓
Finalized
```

A rule result does not itself authorize a lifecycle transition.

---

# 71. Relationship to API Specification

`08_API_Specification.md` should expose rule results using the exact controlled result vocabulary defined here.

API consumers must not reinterpret:

```text
PROCESSING_FAILED
```

as:

```text
POTENTIAL_NON_COMPLIANCE
```

The backend remains the authoritative source of assessment semantics.

---

# 72. Relationship to Database Specification

`09_Database_Specification.md` should persist enough information to reconstruct the compliance assessment, including:

- rule ID;
- rule version/snapshot;
- applicability;
- observed values;
- result;
- evidence references;
- provenance;
- correction history;
- Reviewer decision.

---

# 73. Relationship to Error Handling

`10_Error_Handling.md` defines technical failure behavior.

The compliance-rule specification establishes the critical semantic distinction:

```text
Technical Error ≠ Compliance Failure
```

A failed OCR/AI/storage operation must remain a technical state until sufficient evidence and processing exist for rule evaluation.

---

# 74. Rule Governance Checklist

Before a rule is activated:

- [ ] Legal source identified.
- [ ] Source version/date recorded.
- [ ] Applicability defined.
- [ ] Expected observation defined.
- [ ] Validation logic defined.
- [ ] Evidence expectations defined.
- [ ] PASS semantics defined.
- [ ] Potential non-compliance semantics defined.
- [ ] Review conditions defined.
- [ ] Incomplete conditions defined.
- [ ] Conflict behavior defined.
- [ ] Test cases created.
- [ ] Rule version assigned.
- [ ] Historical snapshot behavior verified.

---

# 75. MVP Compliance Definition

For the purposes of the ComplianceScan MVP:

> **Compliance assessment means deterministic evaluation of a controlled subset of supported Legal Metrology packaged-commodity requirements against validated observations, explicit applicability, and sufficient evidence, followed by human verification and independent Reviewer decision.**

It does not mean:

> automated determination that an entire package is legally compliant in every respect.

---

# 76. Final Compliance Rule Statement

ComplianceScan shall implement compliance checking as a controlled, versioned, evidence-backed evaluation pipeline:

```text
Controlled Legal Source
        ↓
Versioned MVP Rule
        ↓
Applicability
        ↓
Validated Observation
        ↓
Evidence Sufficiency
        ↓
Deterministic Evaluation
        ↓
System Assessment
        ↓
Inspector Verification
        ↓
Reviewer Decision
        ↓
Immutable Final Record
```

The governing principle is:

> **The system evaluates supported rules; it does not replace the legal decision-maker.**

---

# 77. Official Reference Sources

The implementation team should use official sources when maintaining the controlled rule snapshot.

1. **India Code — Legal Metrology Act, 2009**  
   https://www.indiacode.nic.in/handle/123456789/15676

2. **India Code — Legal Metrology Act, 2009, statutory text**  
   https://www.indiacode.nic.in/bitstream/123456789/4892/1/legalmetrology_act_2009.pdf

3. **India Code — Legal Metrology (Packaged Commodities) Rules, 2011**  
   https://upload.indiacode.nic.in/showfile?actid=AC_CH_60_1205_00002_00002_1560405527490&filename=9_the_legal_metrology_%28package_commodities%29_rules%2C_2011.pdf&type=rule

4. **Department of Consumer Affairs — consolidated Legal Metrology Packaged Commodities material**  
   https://consumeraffairs.nic.in/sites/default/files/file-uploads/latestnews/LM_PCR_All_Amendements.pdf

These references are provided for regulatory traceability. The project must verify the applicable legal position and amendment status before treating a rule snapshot as current for operational use.

---

# 78. Final Authority Note

This document defines the **software's controlled MVP rule behavior**.

It is not legal advice and does not itself establish the authoritative legal interpretation of any package, commodity, declaration, or enforcement action.

Where the legal framework, official notification, competent-authority interpretation, or applicable facts are uncertain, ComplianceScan must preserve that uncertainty and route the matter to human review.

