# Phase 7 Forensic Root Cause Report: Synthetic Mock Data Contamination in Inspection Workspace

**Document ID:** `CR-2026-LM-001`  
**Date:** September 20, 2026  
**Status:** REMEDIATED & VERIFIED  
**Severity:** High (Data Integrity & Regulatory Surface Contamination)  
**Target Scope:** `frontend/src/pages/InspectionWorkspacePage.tsx`

---

## 1. Executive Summary

During an end-to-end audit of CompliScan LM on inspection record `INSP-VAL-4A1FCC` (a Real Fruit Juice pack sample), the frontend Inspection Workspace displayed manufacturer declarations for *"Apex Consumer Goods Pvt. Ltd."* and *"Refined Sunflower Oil (1L)"* with contact *"apexcare@apexconsumer.in"*, PKD *"08/2026"*, and MRP *"185.00"*.

These hardcoded values originated from a development mock fixture in `frontend/src/pages/InspectionWorkspacePage.tsx`. The mock data was unconditionally surfaced in the Universal Declarations Matrix whenever any evidence asset was attached to an inspection, regardless of the actual product type or backend compliance state.

This report documents the forensic investigation, root cause identification, dynamic remediation architecture, zero-synthetic audit results, and regression prevention rules.

---

## 2. Root Cause Analysis

### 2.1 File & Function Identification
- **File:** `frontend/src/pages/InspectionWorkspacePage.tsx`
- **Functions:**
  - `buildUniversalDeclarations(primaryEvidenceId?: string): ExtractedDeclarationItem[]`
  - `buildConditionalCOO(originStatus?: string, primaryEvidenceId?: string): ExtractedDeclarationItem | null`

### 2.2 Mechanism of Failure
The legacy builder functions checked if `primaryEvidenceId` was truthy. When true (i.e. any evidence asset existed for the inspection), the functions returned hardcoded static records:
- **Rule 6(1)(a) Name & Address:** Pre-populated with *"Apex Consumer Goods Pvt. Ltd., Plot 42, Industrial Area Phase II, Bengaluru - 560058"*.
- **Rule 6(1)(b) Generic Name:** Pre-populated with *"Refined Sunflower Oil"*.
- **Rule 6(1)(c) Net Quantity:** Pre-populated with *"910 g (1 Litre at 30 °C)"*.
- **Rule 6(1)(d) Date of Pkg/Import:** Pre-populated with *"PKD: 08/2026"*.
- **Rule 6(1)(da) Best Before:** Pre-populated with *"Best Before 9 Months from PKD"*.
- **Rule 6(1)(e) Retail Sale Price (MRP):** Pre-populated with *"₹ 185.00 (Inclusive of all taxes)"*.
- **Rule 6(1)(g) Consumer Care:** Pre-populated with *"Consumer Care Cell: apexcare@apexconsumer.in, 1800-425-0199"*.

Because the UI maintained `universalDeclarations` and `cooDeclaration` as static `useState` instances seeded by these functions during initial fetch, file upload, and context save, any inspection displaying evidence inherited the Sunflower Oil mock record.

### 2.3 Backend Engine Scope Verification
A forensic review of `backend/` and database repositories confirmed that the backend compliance engine (`rule_engine.py`, `compliance_service.py`, `models/compliance.py`) was entirely free of this contamination. The backend was correctly processing and storing inspection-scoped evidence; the contamination was strictly isolated to frontend presentation builder routines.

---

## 3. Remediation Architecture

### 3.1 Dynamic Declarations Resolver
The hardcoded mock builders were replaced with a declarative mapping system backed by a dynamic resolver context:

```typescript
interface BuildDeclarationsContext {
  primaryEvidenceId?: string;
  findings: ComplianceFinding[];
  structuredDeclarations: StructuredDeclaration[];
  corrections: Record<string, InspectorCorrection>;
  adjudications: Record<string, ReviewerAdjudication>;
  activeAssetId?: string;
}
```

### 3.2 Evaluation Priority Hierarchy
For each statutory rule, the UI evaluates declarations in a strict, deterministic priority order:
1. **Compliance Finding:** Checks `findings.find(f => f.rule_id === ruleId || f.rule_code === ruleId)`. Reads `finding.extracted_value`, `finding.status`, `finding.bounding_box`, and `finding.confidence`.
2. **Structured Declarations:** If no finding is present, scans `structuredDeclarations` for matching declaration keys (e.g. `manufacturer_address`, `mrp`, `net_quantity`).
3. **Inspector Adjudications / Corrections:** Merges verified corrections and overrides from the active review session.
4. **Pending / Not Observed Fallback:** If no data exists in the database or active session, outputs:
   - Extracted Value: `""`
   - Adjudication State: `NOT RECORDED` / `PENDING`
   - Confidence: `0.0`
   - Visual Badge: `INCOMPLETE` / `Awaiting compliance evaluation`

### 3.3 Reactive State Derivation
- Removed `universalDeclarations: useState` and `cooDeclaration: useState`.
- Replaced with computed `useMemo` hooks driven by `[declarationContext, inspection.origin_status]`.
- Adjudication changes are managed via `declarationOverrides: useState<Record<string, Partial<ExtractedDeclarationItem>>>({})` which are layered over computed state without overwriting underlying source truths.

---

## 4. Verification & Audit Results

### 4.1 TypeScript Compilation
Executed `npx tsc --noEmit` in `frontend/`:
- **Result:** Exit code `0` (Zero compiler errors or type mismatches).

### 4.2 Synthetic String Audit
A comprehensive regex audit was executed across the entire repository for legacy test tokens:
| Token / Pattern | Search Target | Matches Found |
|---|---|---|
| `Apex Consumer Goods` | Entire codebase | 0 |
| `Refined Sunflower` | Entire codebase | 0 |
| `apexcare@` | Entire codebase | 0 |
| `1800-425-0199` | Entire codebase | 0 |
| `910 g (1 Litre` | Entire codebase | 0 |
| `PKD: 08/2026` | Entire codebase | 0 |
| `185.00` (MRP mock) | Entire codebase | 0 |
| `Country of Origin: Vietnam` | Entire codebase | 0 |

---

## 5. Architectural Guardrails & Standards

To ensure zero recurrence of mock/synthetic contamination across CompliScan LM:

1. **Strict Data Grounding:** The UI must never display data from a different inspection, test fixture, fallback object, or stale validation record.
2. **Deterministic Unobserved State:** If the database contains no value for a field, the UI must explicitly state `NOT RECORDED`, `NOT OBSERVED`, `NOT AVAILABLE`, or `PENDING`.
3. **No Stateful Duplication of Backend Models:** UI components must derive views reactively from backend API responses via `useMemo` rather than cloning data into disconnected `useState` registers.
4. **CI Static Checks:** Any future PR containing hardcoded manufacturer or product names in UI builder modules will be flagged by static lint / regex policies.
