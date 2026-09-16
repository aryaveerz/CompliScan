# Antigravity Review — CompliScan LM Proposed Requirement-Complete MVP
**Document Reviewed:** `CompliScan_LM_Proposed_Requirement_Complete_MVP.md`  
**Reviewed by:** Antigravity  
**Date:** 2026-09-16  
**Status:** REVIEW ONLY — No implementation started.

---

## VERDICT

```text
APPROVED WITH TARGETED ADJUSTMENTS
```

This proposed MVP is **well-conceived, appropriately scoped, and technically credible**. It correctly identifies the gap between the previous implementation spec (which was workflow-complete but SIH-requirement-narrow) and what an SIH judge needs to observe: a system that visibly and demonstrably addresses every major capability in the problem statement.

The proposal is approvable as the new controlling MVP definition. Four targeted adjustments are recommended — none are blocking, but two are important enough to resolve before implementation begins.

---

## REQUIREMENT COVERAGE

**Assessment: Near-complete. No major SIH requirement is missing.**

| SIH Requirement | Proposed Coverage | Assessment |
|-----------------|-------------------|------------|
| Scan package images | Physical upload + online listing screenshot | ✅ Sufficient |
| Detect mandatory declarations | PaddleOCR + Gemini extraction | ✅ Correct |
| Automated extraction | Structured extraction pipeline | ✅ Correct |
| Correctness checking | 6 deterministic compliance domains | ✅ Correct |
| Completeness checking | Required-field evaluation with evidence-awareness | ✅ Correct |
| Missing declaration detection | Evidence-aware missing-field logic (§16) | ✅ Correct — the NOT_OBSERVED ≠ MISSING logic is strong |
| Placement assessment | OCR bounding-box placement screening | ✅ Scoped appropriately |
| Readability analysis | Image + OCR confidence assessment | ✅ Scoped appropriately |
| Font-size checking | Bounding-box height estimation with honest confidence | ✅ Correctly bounded |
| Non-standard/misleading declarations | Format anomaly + conflict checks | ✅ Scoped correctly |
| Compliance reports | PDF + DOCX | ✅ Both required |
| Violation summary | Findings summary screen | ✅ |
| Product repository | Inspection list with search | ✅ |
| Compliance history | Inspection history + audit trail | ✅ |
| Dashboard | Real stored-data metrics | ✅ |
| Web/mobile-accessible | Responsive web app | ✅ Correct — native mobile not needed |
| RBAC | Inspector / Reviewer with backend enforcement | ✅ |
| Secure authentication | Supabase Auth + FastAPI validation | ✅ |
| Search/retrieval | Filter by ID, product, status, result | ✅ |
| Editable report | DOCX generation | ✅ |
| Rule-based checking | Deterministic backend engine | ✅ |
| Supporting evidence | Original images + evidence references + highlights | ✅ |

**Verdict: Requirement matrix is comprehensive and correctly maps to demonstrable capabilities.**

---

## STRONG POINTS

### SP-01 — Evidence-aware missing-declaration logic (§16)
This is the most important technical distinction in the entire proposal. The three-way split:
```
NOT_OBSERVED ≠ MISSING
UNREADABLE ≠ MISSING  
INSUFFICIENT_EVIDENCE ≠ MISSING
```
is legally correct and technically defensible. Most competing systems would blindly treat OCR failure as a missing declaration. This distinction alone is a meaningful differentiator.

### SP-02 — Font-size screening with honest confidence (§13)
The proposal correctly refuses to claim precise millimetre measurements from arbitrary photographs. Instead it offers:
- Estimated size from bounding-box height
- Explicit `UNABLE TO ESTABLISH PRECISE PHYSICAL SIZE` when scale reference is unavailable
- `REVIEW REQUIRED` rather than a fake measurement

This is technically honest and actually stronger than a system that fabricates a precise number. An SIH judge will respect this.

### SP-03 — SIH Requirement Coverage Matrix (§7)
The explicit mapping table (SIH Requirement → MVP Capability → Demonstration) is excellent. It should become a mandatory implementation tracking artifact, updated after each phase with actual demo status.

### SP-04 — Two input modes (§8)
Mode A (physical package) + Mode B (online product listing screenshot) covers the SIH statement's mention of e-commerce platforms without requiring a web crawler. This is smart scoping: same pipeline, different evidence source.

### SP-05 — Positioning language (§61)
> *"CompliScan LM combines perception, structured extraction, applicability-aware deterministic rules, visual screening, evidence traceability and human review into one inspection workflow."*

This is technically accurate, comprehensive, and differentiated. Use this exact framing for the demo.

### SP-06 — 36-step demo acceptance test (§49)
Expanded from the previous 32-step test. Steps 16–18 (font-size, placement, anomaly assessment) and steps 33–36 (DOCX, history, search, dashboard) are exactly the SIH-required additions. This is the right demo script.

---

## TECHNICAL RISKS

### TR-01 — Font-size estimation: bounding-box method limitations
**Risk:** Character height from bounding boxes gives pixel height, not physical millimetres. Without a physical scale reference (a known-dimension object in frame, or package dimension metadata), conversion to mm is not possible.

**The proposal correctly handles this** (§13: "If physical scale is unavailable, say UNABLE TO ESTABLISH PRECISE PHYSICAL SIZE"). However, the implementation team must be careful:
- Never compute a fake mm estimate by assuming a default DPI.
- The bounding-box pixel height relative to image height is a useful *relative* indicator, not a physical measurement.
- The output must always label itself "screening/estimation" not "measurement."

**Risk level:** Low — the proposal's honest scoping prevents the implementation risk.

---

### TR-02 — DOCX generation library choice
**Risk:** DOCX generation from Python has inconsistent formatting across libraries. Options:
- `python-docx` — reliable, well-maintained, produces valid DOCX from scratch
- `docxtpl` — Jinja2 templates for DOCX (recommended for templated reports)
- LibreOffice conversion — heavyweight, Docker dependency

**Recommendation:** Use `docxtpl` (Jinja2 DOCX templates) for the editable report. Same template approach as WeasyPrint for PDF. Both derive from the `FinalAuditRecord` snapshot. Adds minimal complexity to Phase 5.

**Risk level:** Low.

---

### TR-03 — Placement assessment: what is the "configured expected region"?
**The pipeline in §14** references "Configured Expected Region":
```
Declaration → OCR Bounding Box → Image Region → Configured Expected Region → Assessment
```

For MVP, the "configured expected region" cannot be a deep understanding of packaging layout rules (which vary by commodity category and are not fully specified in the LM Rules for all cases). 

**Implementation guidance:** For MVP, placement assessment means:
- Record the detected bounding-box region (top/bottom/left/right of the image, front/rear face if the Inspector tags it).
- Report whether a declaration was found at all, and in which region.
- Flag declarations found in unexpected regions as `REQUIRES_REVIEW`.
- Do not claim precise legal verification of packaging layout.

The proposal already scopes this correctly in §14: *"The MVP must NOT claim universal understanding of every packaging-placement provision."*

**Risk level:** Low — just needs precise implementation scoping.

---

### TR-04 — Online listing mode (Mode B) scope creep risk
**The proposal says** (§8): Mode B accepts a listing screenshot, product image, or optionally a product URL/reference. The same compliance pipeline is reused.

**Risk:** If "product URL/reference" is interpreted as a web crawler or scraping feature, implementation complexity explodes. The proposal explicitly says *"The MVP does NOT require a web crawler."*

**Implementation guard:** Mode B = Inspector manually uploads a screenshot or product image from an online source. The URL field is metadata/annotation only — it is never fetched or crawled. The pipeline is identical to Mode A.

**Risk level:** Low if clearly implemented as above. Medium if URL-fetching is accidentally added.

---

## OVER-SCOPED ITEMS

### OS-01 — Format anomaly checks (§15) scope should be tightly defined before Phase 3

**Observation:** "Misleading and non-standard declarations" is a broad category. The proposal offers examples:
- malformed MRP representation
- unsupported/ambiguous quantity unit
- malformed date representation
- incomplete consumer-care representation
- suspicious declaration formatting
- ambiguous extracted values
- conflicting declaration values

The last two (suspicious formatting, conflicting values) are already handled by the `REQUIRES_REVIEW` result state. The first five are well-defined and implementable.

**Recommendation:** Before Phase 3 implementation, produce a controlled list of exactly which format anomaly checks are in scope (e.g., MRP not prefixed by ₹ symbol, quantity unit not in a controlled list, date format not MM/YYYY). This prevents the format anomaly module from becoming an open-ended AI reasoning layer.

**MVP impact:** Scoping clarification needed before Phase 3. Not a blocker now.

---

### OS-02 — Technical documentation requirement (§7 matrix, last row)
The SIH requirement matrix includes "Technical documentation → Show architecture/deployment documentation." This is fine and appropriate. However, do not spend implementation time writing exhaustive docs. The existing Phase 0 artifacts (legal reconciliation, architecture decisions, this spec) already constitute strong technical documentation. A `README.md` pointing to these is sufficient for the demo.

---

## UNDER-SCOPED ITEMS

### US-01 — Visual highlighting implementation detail (§22)

The proposal mandates visual highlighting of declarations on package images. This requires:
1. OCR bounding boxes (from PaddleOCR) stored as derived evidence.
2. A backend endpoint that generates a highlighted version of the image (or returns bounding box coordinates).
3. Frontend rendering of bounding boxes overlaid on the original image.

Option A (backend renders highlighted image): Simpler frontend, adds PIL/Pillow dependency to backend.
Option B (frontend renders overlay using canvas): More flexible, no backend image manipulation needed.

**Recommendation:** Option B (frontend canvas overlay). Store bounding boxes as structured data in `DerivedOcrToken`. Frontend renders the overlay using the stored coordinates. Original image is never modified.

This should be explicitly planned in Phase 2 (not Phase 3) because OCR bounding boxes are produced during the PaddleOCR step.

---

### US-02 — Dashboard: Inspector vs. Reviewer visibility

The dashboard metrics in §33 are minimal and correct. One under-specified item: do Inspectors see all inspections or only their own? Do Reviewers see only cases submitted for review?

**Recommendation:** For MVP:
- Inspector sees their own inspections.
- Reviewer sees all inspections in `SUBMITTED_FOR_REVIEW` or `REQUIRES_REVISION` state (review queue).
- Dashboard counts are scoped by role.

This requires a one-sentence RBAC rule, not additional architecture.

---

## MISSING REQUIREMENTS

**Finding: Nothing critically missing from an SIH perspective.**

One item worth noting for completeness:

### MR-01 — No explicit mention of product information input form

The SIH statement mentions "product information." The proposal handles this through inspection metadata (product name, manufacturer observed from extraction). However, a brief structured product context form during inspection creation would allow the Inspector to pre-annotate:
- Product name (if known)
- Import status (imported/domestic/unknown — this directly feeds the Country of Origin applicability check)
- Product category (for future expansion)

**Recommendation:** Add a simple product context form to the `CreateInspection` flow. This is low-effort (3-4 fields) and directly enables the Country of Origin applicability logic without requiring it to be inferred solely from AI extraction.

**MVP impact:** Strongly recommended addition. Low implementation cost. High applicability logic value.

---

## RECOMMENDED CHANGES

### RC-01 — Add product context form to inspection creation (MVP-Critical)

**Why:** The Country of Origin applicability check (imported/domestic/unknown) needs an explicit Inspector input. Relying on Gemini to infer import status from a label image is unreliable.

**Impact:** Adds a 3-4 field form to the `CreateInspection` UI. No architecture change.

**Can be deferred:** No. Needed in Phase 1 to correctly set up the applicability pipeline in Phase 3.

---

### RC-02 — Define controlled format anomaly check list before Phase 3 (MVP-Critical Scoping)

**Why:** Without a controlled list, "format anomaly checks" can expand indefinitely. Define exactly which checks are in scope as a controlled rule artifact before Phase 3 begins.

**Impact:** Zero code impact. Requires a one-page spec defining the controlled anomaly checks.

**Can be deferred:** Until start of Phase 3, but not after.

---

### RC-03 — Add `docxtpl` to the technology stack (DOCX export) (MVP-Required)

**Why:** The proposal requires editable DOCX output (§28). The technology stack (§40) lists "PDF + DOCX" but does not specify the library.

**Recommendation:** Add `python-docx` / `docxtpl` (Jinja2 DOCX templates) to the approved stack for Phase 5.

**Can be deferred:** Until Phase 5. Does not affect Phase 1–4.

---

### RC-04 — Clarify visual highlighting implementation as frontend canvas overlay (Phase 2 scoping)

**Why:** If not specified, developers may implement this as backend image manipulation (adds PIL dependency to all API containers) or skip it entirely.

**Recommendation:** Confirm frontend canvas overlay using stored `DerivedOcrToken` bounding boxes. Note this in Phase 2 acceptance criteria.

**Can be deferred:** Scoping clarification only — no code impact until Phase 2.

---

## MVP COMPLEXITY ASSESSMENT

| Phase | Complexity | Risk | Notes |
|-------|-----------|------|-------|
| Phase 0 (Audit) | Very Low | None | Repository is nearly clean — short audit |
| Phase 1 (Foundation) | Low | Low | Standard FastAPI + React + Supabase setup |
| Phase 2 (OCR + AI) | Medium | Medium | PaddleOCR Docker image, Gemini API, bounding boxes |
| Phase 3 (Compliance + Visual) | Medium-High | Medium | Six rules + readability + font-size + placement + anomaly checks — all need controlled scope |
| Phase 4 (Human Workflow) | Medium | Low | Well-specified in the architecture documents |
| Phase 5 (Reports + Repository) | Medium | Low | WeasyPrint + docxtpl + search + dashboard |
| Phase 6 (Hardening) | Low-Medium | Low | Deferred from core path |

**Total complexity:** This is a **medium-complexity MVP** — significantly more demonstrable than the previous spec but not over-engineered. The additions (readability, font-size, placement, DOCX, search, dashboard) each individually add modest scope. Together they add approximately 30-40% more implementation work compared to the previous MVP spec.

**That is acceptable** given the SIH requirement coverage it unlocks.

---

## DEMO FEASIBILITY

**Assessment: HIGH FEASIBILITY**

The 36-step demo acceptance test (§49) is realistic and achievable. The complete flow from upload to dashboard can be demonstrated in a live session of approximately 10-15 minutes.

The most visually impressive moments for an SIH judge will be:
1. Steps 6-10: OCR bounding boxes overlaid on the package image, then structured Gemini output.
2. Step 16: Font-size estimation with honest confidence display.
3. Steps 19-21: Inspector correction with old/new value preserved + automatic recomputation.
4. Steps 32-36: PDF + DOCX generation, search, dashboard.

These are the moments that demonstrate the system is real, not a mockup.

---

## NEW STRATEGY — HOW THIS CHANGES THE IMPLEMENTATION APPROACH

This document supersedes the previous MVP Implementation Specification (`CompliScan_LM_MVP_Implementation_Specification.md`) in the following ways:

### What stays the same
- All 24 locked architecture decisions remain unchanged.
- All 7 resolved decisions (M-01, M-02, P-01–P-05) remain unchanged.
- The 6-state result vocabulary.
- The 9-entity data model.
- The FastAPI modular monolith architecture.
- The evidence immutability, audit, and finalization invariants.
- The `AI finds → Evidence proves → Officer decides` philosophy.

### What changes (expanded scope)

| Previous Spec | New Proposed Spec | Change |
|---------------|-------------------|--------|
| PDF only | PDF + DOCX | Added DOCX (Phase 5) |
| Basic findings display | Evidence-highlighted findings with bounding boxes | Added visual overlay (Phase 2–3) |
| 6 compliance checks only | 6 compliance checks + readability + font-size + placement + format anomaly | Added 4 visual/format assessments (Phase 3) |
| Physical package only | Physical package + online listing screenshot | Added Mode B input (Phase 1/2) |
| No explicit search UI | Search/filter by multiple fields | Added search (Phase 5) |
| Minimal dashboard | Real metrics dashboard | Added dashboard (Phase 5) |
| 32-step acceptance test | 36-step acceptance test | 4 new observable demo steps |

### Revised Phase 3 scope (most impacted phase)

The previous Phase 3 was: `Validated Observations → Applicability → Six Rules → Findings`

The new Phase 3 is:
```text
Validated Observations
        ↓
Applicability
        ↓
Six Deterministic Compliance Checks
        ↓
Readability Assessment (from OCR confidence + image quality)
        ↓
Font-Size Screening (from bounding-box height + honest confidence)
        ↓
Placement Screening (from bounding-box region + Inspector-tagged face)
        ↓
Format Anomaly Checks (controlled list — define before Phase 3 starts)
        ↓
All Findings with Evidence Links
```

The visual assessments (readability, font-size, placement, anomalies) are **lightweight additions** that reuse already-computed data from Phase 2 (bounding boxes, OCR confidence, image quality). They do not require a new AI model or new external dependency.

---

## FINAL RECOMMENDATION

```text
===========================================================
RECOMMENDATION: APPROVE WITH FOUR TARGETED ADJUSTMENTS
===========================================================

ADJUSTMENTS REQUIRED BEFORE IMPLEMENTATION STARTS:

1. (RC-01) Add product context form to CreateInspection flow.
   → Critical for applicability engine correctness.

2. (RC-02) Define controlled format anomaly check list.
   → Prevents scope creep in Phase 3.

ADJUSTMENTS BEFORE THEIR RESPECTIVE PHASES:

3. (RC-03) Add docxtpl to approved stack.
   → Needed before Phase 5 begins.

4. (RC-04) Confirm frontend canvas overlay approach for
   visual highlighting.
   → Needed before Phase 2 begins.

OVERALL VERDICT:

This proposed MVP is:
✅ Small enough to build within SIH timeframe
✅ Broad enough to visibly satisfy all major SIH requirements
✅ Technically defensible — no overclaims
✅ Differentiated from a generic OCR-label-checker
✅ Honest about AI limitations

The 36-step demo is achievable and impressive.
The requirement coverage matrix is comprehensive.

AUTHORIZE FOR IMPLEMENTATION after RC-01 and RC-02 are confirmed.
===========================================================
```

---

*Review complete. No code, schema, migration, or implementation artifact created.*  
*All four recommended adjustments require human confirmation before they are treated as approved changes.*
