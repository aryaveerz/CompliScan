# ComplianceScan — Legal and Project Reconciliation Audit Report
## Phase 0 Controlled Legal Reconciliation Audit (Controlled Correction Pass)

---

## SECTION A: Audit Metadata

- **Project Name:** ComplianceScan
- **Audit Type:** Controlled Legal and Project Reconciliation Audit (Phase 0 Pre-Implementation Gate — Controlled Correction Pass)
- **Primary Legal Framework:** Legal Metrology Act, 2009 & Legal Metrology (Packaged Commodities) Rules, 2011 (as amended through 2026)
- **Source Archive Audited:** `g:\CompliScan\Legal_References\Packaged_Commodities\` (40 PDF files across 12 year folders, 2011–2026)
- **Project Documentation Audited:** `g:\CompliScan\Documentation\` (16 core engineering & domain specification documents)
- **Prior Artifacts Reconciled:** `g:\CompliScan\phase0_reconnaissance_report.md` (lines 1–489), `g:\CompliScan\Legal_References\Legal Reference Index.md`
- **Audit Date:** September 2026
- **Auditor Role:** Antigravity AI Engineering & Legal Reconciliation System
- **Audit Status:** COMPLETE — REVISED ARTIFACT READY FOR HUMAN APPROVAL

---

## SECTION B: Executive Summary

This controlled audit report reconciles the 40 authoritative legal source documents in `g:\CompliScan\Legal_References\Packaged_Commodities\` with the existing specifications in `g:\CompliScan\Documentation\`.

### 1. Three-Layer Separation Model
To prevent confusion between law, software design, and business constraints, this audit strictly enforces three distinct layers across all findings:

```text
LAYER 1 — LEGAL FACT: What the official statutory gazette notification or administrative rule actually states.
        ↓
LAYER 2 — ENGINEERING INTERPRETATION: How ComplianceScan proposes to represent, validate, and test that rule in software.
        ↓
LAYER 3 — PRODUCT / MVP DECISION: What the project explicitly decides to implement now, defer, or exclude from current scope.
```

### 2. Core Architectural Findings
- **Architecture Principle Preservation:** No legal finding identified in this Phase 0 reconciliation currently requires abandonment of the core architectural principles. The system architecture remains subject to later operational workflow and implementation review.
- **Authoritative Six-State Project Result Vocabulary:** The system uses the project's authoritative six-state result vocabulary:
  - `PASS`
  - `POTENTIAL_NON_COMPLIANCE`
  - `REQUIRES_REVIEW`
  - `NOT_APPLICABLE`
  - `INCOMPLETE`
  - `PROCESSING_FAILED`
  *(Note: The older four-state vocabulary `COMPLIANT`, `NON_COMPLIANT`, `MANUAL_REVIEW`, `NOT_APPLICABLE` was an outdated project assumption and is hereby superseded. This is a project state model decision, not a statutory legal determination).*
- **Critical State Distinctions:**
  - `NOT_APPLICABLE != PASS`
  - `INCOMPLETE != POTENTIAL_NON_COMPLIANCE`
  - `PROCESSING_FAILED != POTENTIAL_NON_COMPLIANCE`
  - `NOT_OBSERVED != missing`
  - `UNREADABLE != NOT_OBSERVED`
  - `CONFLICTING evidence/data -> REQUIRES_REVIEW`
  - *Technical processing failure must never be recorded as a legal compliance failure.*
- **AI Boundary & Non-Adjudication:** The system must not claim that AI has legally determined a violation. The system uses "Potential Non-Compliance" to highlight candidate discrepancies for human verification. Final legal/inspection decisions belong exclusively to authorized human officers.
- **Six MVP Compliance Checks:** The product scope targets the **Six MVP compliance checks** (not "six mandatory declarations", as applicability governs individual checks, particularly Country of Origin).
- **Unit Sale Price (USP) Statutory Gap:** G.S.R. 779(E) (effective 1 January 2023) introduced Unit Sale Price under Rule 6(1)(f) for packages measured by weight, volume, or length. In accordance with project decisions, USP is classified as: **"Documented statutory gap; implementation phase TBD."** USP is NOT added to the current MVP, nor is it an automatic Phase 1 commitment.
- **Preservation of Baseline:** No application code has been written, no database schemas created, and no main specification documents modified during Phase 0.

---

## SECTION C: Phase 0 Reconnaissance Reconciliation

The Phase 0 reconnaissance findings recorded in `phase0_reconnaissance_report.md` were reconciled against all 40 legal sources and current project baselines:

| Phase 0 Recon Area | Reconciled Statutory & Project Reality | Layer Separation Analysis | Alignment / Correction Action |
|---|---|---|---|
| **P0-1: Scope of Checks** | Six MVP compliance checks targeted (Rule 6(1)(a)–(e)). USP under Rule 6(1)(f) introduced in 2021 (in force 2023). | **L1:** USP mandatory since 01-01-2023.<br>**L2:** USP requires price-per-unit math engine.<br>**L3:** Retain 6 MVP checks; USP is documented gap (Phase TBD). | Reconciled: 6 MVP compliance checks preserved; USP gap logged without unapproved scope creep. |
| **P0-2: Result Vocabulary** | Project baseline is 6 authoritative states: `PASS`, `POTENTIAL_NON_COMPLIANCE`, `REQUIRES_REVIEW`, `NOT_APPLICABLE`, `INCOMPLETE`, `PROCESSING_FAILED`. | **L1:** Administrative law requires proof of violation.<br>**L2:** Software maps observations to structured states.<br>**L3:** Project adopts 6-state model. | **Corrected:** Older 4-state vocabulary retired as an outdated project assumption. |
| **P0-3: Country of Origin** | Rule 6(1)(da) applies strictly to imported commodities. Domestic packages have no LMPC COO requirement. | **L1:** Mandate conditional on import.<br>**L2:** Applicability engine evaluates import status first.<br>**L3:** Imported = applicable; Domestic = `NOT_APPLICABLE`. | Confirmed: "Applicability First" philosophy preserved. Unknown import status routes to `REQUIRES_REVIEW`/`INCOMPLETE`. |
| **P0-4: Date of Manufacture** | Simplified to "month and year of manufacture" under G.S.R. 779(E). | **L1:** Month and year required.<br>**L2:** Engine should accept valid syntactic representations.<br>**L3:** Do not restrict to narrow MM/YYYY only without approved spec. | Refined: Distinguish mandatory information from syntax; preserve syntax flexibility pending spec approval. |
| **P0-5: Metric Units (Rule 13)** | Third Schedule prescribes legal metric symbols (g, kg, ml, l, m, etc.). Non-standard forms ("gms", "Kgs") are observed discrepancies. | **L1:** Third Schedule specifies legal units.<br>**L2:** OCR flags non-standard strings.<br>**L3:** Flag as `POTENTIAL_NON_COMPLIANCE` / `REQUIRES_REVIEW` (compounding status unconfirmed, LR-004). | Refined: Avoid asserting definitive legal compounding violation; route to human officer verification. |
| **P0-6: Consumer Care** | Rule 6(1)(e) text mandates name, address, telephone, and email. Multi-channel fallback is an engineering interpretation. | **L1:** Statutory text specifies 4 elements.<br>**L2:** Engine checks for at least one active channel.<br>**L3:** Flag multi-channel fallback for legal review (LR-005); do not treat as automatic legal pass. | Refined: Clearly distinguish statutory wording from engineering interpretation. |

---

## SECTION D: Legal Reference Archive Verification

The legal reference archive at `g:\CompliScan\Legal_References\Packaged_Commodities\` was audited across all 40 files:

```text
Packaged_Commodities/
├── 2011/ (7 files)  - G.S.R. 202(E) Principal Rules, Corrigenda, Guidelines, Amendments 1-2
├── 2012/ (2 files)  - Provisions on non-standard packaging, font height tables
├── 2013/ (1 file)   - Industrial/Institutional consumer definitions
├── 2014/ (2 files)  - Retail dealer liability provisions, Second Schedule commodities
├── 2015/ (1 file)   - Specific commodity net quantity exemptions
├── 2016/ (2 files)  - Principal display panel area rules, Readymade garments advisory
├── 2017/ (2 files)  - G.S.R. 629(E) E-Commerce Rule 6(10) & Rule 6(1)(da) COO; Barcodes
├── 2021/ (1 file)   - G.S.R. 779(E) Landmark Reform (USP, simplified date, revised MRP)
├── 2022/ (5 files)  - G.S.R. 226(E), G.S.R. 542(E) QR codes, G.S.R. 858(E), G.S.R. 862(E)
├── 2023/ (12 files) - G.S.R. 456(E) QR codes, G.S.R. 722(E) Package definitions, SOPs
├── 2025/ (2 files)  - G.S.R. 778(E) Medical Devices exclusion, G.S.R. 881(E) Pan Masala
└── 2026/ (3 files)  - G.S.R. 128(E) COO Filter, G.S.R. 312(E) COO 2027, G.S.R. 418(E) AEO
```

- **Archive Count:** 40 PDF files across 12 year directories verified on disk.
- **Readability Breakdown:** 26 digital text PDFs (extracted via PyMuPDF); 14 scanned gazette copies (verified via gazette registries and official notification references).
- **Provenance Principle:** These 40 documents are **provenance references**, not executable runtime code. Neither the runtime engine nor an LLM may dynamically parse or execute raw PDFs.

---

## SECTION E: Temporal Validity and Effective-Date Matrix

Effective dates are first-class legal information. Historical inspection packages must be evaluated against the legal snapshot applicable to their date of manufacture/packing, not retroactively against today's rules.

| Rule Provision | Amending Notification | Issue Date | Stated Commencement | Final In-Force Date | Legal & System Status |
|---|---|---|---|---|---|
| **Principal PCR 2011** | G.S.R. 202(E) | 07-03-2011 | 01-04-2011 | 01-04-2012 | **Principal Statutory Authority** |
| **E-Commerce Rule 6(10)** | G.S.R. 629(E) | 23-06-2017 | 01-01-2018 | 01-01-2018 | **Active Statutory Law** (Core Reference) |
| **Unit Sale Price (USP)** | G.S.R. 779(E) | 02-11-2021 | 01-04-2022 | 01-01-2023 (via G.S.R. 862(E)) | **Active Statutory Law** (Documented Gap; Implementation TBD) |
| **Simplified Date Format** | G.S.R. 779(E) | 02-11-2021 | 01-04-2022 | 01-01-2023 | **Active Statutory Law** (Enforcement standard) |
| **QR Code Electronics** | G.S.R. 456(E) | 23-06-2023 | 23-06-2023 | 23-06-2023 | **Active Statutory Provision** (Deferred Capability) |
| **Package Type Definitions** | G.S.R. 722(E) | 06-10-2023 | 01-01-2024 | 01-01-2024 | **Active Statutory Law** (Deferred Capability) |
| **Medical Devices Deference**| G.S.R. 778(E) | 23-10-2025 | 23-10-2025 | 23-10-2025 | **Active Statutory Exemption** (Applicability Exclusion) |
| **Pan Masala Exemption** | G.S.R. 881(E) | 02-12-2025 | 01-02-2026 | 01-02-2026 | **Active Statutory Exemption** (Commodity Specific) |
| **E-Comm COO Filter** | G.S.R. 128(E) | 13-02-2026 | 01-07-2026 | 01-07-2026 | **Currently In Force** (Digital Marketplace; Deferred Capability) |
| **E-Comm COO Subst.** | G.S.R. 312(E) | 27-04-2026 | 01-07-2027 | 01-07-2027 | **Future Law Milestone** (Informational tracking) |
| **AEO Bonded Warehouses** | G.S.R. 418(E) | 29-05-2026 | 29-05-2026 | 29-05-2026 | **Currently In Force** (Customs Logistics; Deferred Capability) |

---

## SECTION F: Applicability and Exemption Matrix

Statutory compliance requirements depend entirely on package classification. ComplianceScan follows the principle: **"Applicability First"** — determine whether a rule applies before evaluating evidence.

| Commodity / Package Type | Statutory Basis | Exemption / Special Rule | ComplianceScan Handling |
|---|---|---|---|
| **Standard Retail Package** | Rule 3 & Chapter II | Full Rule 6 declarations mandatory | Standard Pipeline (Six MVP Checks) |
| **Imported Commodity** | Rule 6(1)(da) | Country of Origin mandatory; importer details required | Evaluated under Rule 6(1)(da) and 6(1)(a) |
| **Domestic Commodity** | Rule 6(1)(da) | COO declaration NOT mandatory under LMPC | Returns `NOT_APPLICABLE` for COO check |
| **Unknown Import Status** | Rule 6(1)(da) | Cannot safely assume domestic without evidence | Returns `REQUIRES_REVIEW` or `INCOMPLETE` |
| **Small Package (<= 10g/10ml)** | Rule 26(a) | Exempt from certain declarations if on outer display | Flagged for `REQUIRES_REVIEW` / Deferred capability |
| **Package > 25 kg / 25 L** | Rule 3 | Chapter II does not apply (except farm/cement to 50kg) | Flagged as Institutional / Out of Retail Scope |
| **Institutional Consumer** | Rule 3 & 2(p) | Exempt from retail display if marked "Institutional" | Returns `NOT_APPLICABLE` upon marker confirmation |
| **Medical Devices** | G.S.R. 778(E) (2025) | Governed by MDR, 2017; LMPC standard rules deferred | Flagged as Specialized Regulatory Routing |
| **Garments & Hosiery** | G.S.R. 858(E) (2022) | Mandatory declarations on tag: size, net qty, MRP, mfr | Deferred capability (Phase TBD) |

---

## SECTION G: Six MVP Compliance Checks Deep Dive

The Six MVP compliance checks were evaluated through the mandatory 3-layer separation model:

### 1. Check 1: Manufacturer / Packer / Importer Identity & Address (Rule 6(1)(a))
- **Layer 1 (Legal Fact):** Rule 6(1)(a) mandates the name and complete address of the manufacturer, or where manufacturer is not packer, both manufacturer and packer; for imported goods, the name and address of the importer.
- **Layer 2 (Engineering Interpretation):** Validate presence of an identifiable legal entity and a physical address structure (city, state, pincode).
- **Layer 3 (Product/MVP Decision):** Active MVP check. Absence routes to `POTENTIAL_NON_COMPLIANCE`; ambiguous text routes to `REQUIRES_REVIEW`.

### 2. Check 2: Common or Generic Product Name (Rule 6(1)(b))
- **Layer 1 (Legal Fact):** Rule 6(1)(b) requires the common or generic name of the commodity contained in the package.
- **Layer 2 (Engineering Interpretation):** Distinguish proprietary brand name from generic commodity descriptor.
- **Layer 3 (Product/MVP Decision):** Active MVP check. Verified against commodity dictionary or extracted entity description.

### 3. Check 3: Net Quantity + Standard Unit (Rule 6(1)(c) & Rules 11–13)
- **Layer 1 (Legal Fact):** Rule 6(1)(c) and Rules 11–13 require declaration of net quantity in terms of standard metric units (Third Schedule) or number.
- **Layer 2 (Engineering Interpretation):** Parse numerical value and unit symbol. Flag non-standard symbols ("gms", "Kgs", "ltrs") as observed syntax discrepancies.
- **Layer 3 (Product/MVP Decision):** Active MVP check. Because state compounding and enforcement treatment of non-standard symbols varies (see LR-004), the engine shall route detected non-standard symbols to `POTENTIAL_NON_COMPLIANCE` / `REQUIRES_REVIEW` for human verification, rather than asserting a definitive legal breach.

### 4. Check 4: Month and Year of Manufacture / Packing / Import (Rule 6(1)(d))
- **Layer 1 (Legal Fact):** Rule 6(1)(d), as amended by G.S.R. 779(E) (effective 01-01-2023), requires declaration of the month and year of manufacture (or pre-packing / import).
- **Layer 2 (Engineering Interpretation):** Extract month and year. Accepted representations may include numerical formats (MM/YYYY) or textual formats (e.g., "March 2026").
- **Layer 3 (Product/MVP Decision):** Active MVP check. Do not enforce a narrow syntax (such as "MM/YYYY only") unless explicitly required by an approved specification. Missing date routes to `POTENTIAL_NON_COMPLIANCE`.

### 5. Check 5: Maximum Retail Price (MRP), Inclusive of All Taxes (Rule 6(1)(e))
- **Layer 1 (Legal Fact):** Rule 6(1)(e) mandates declaration of the retail sale price in Indian currency inclusive of all taxes in statutory phrases such as "Maximum or Max. Retail Price ₹ ...... incl. of all taxes".
- **Layer 2 (Engineering Interpretation):** Validate numeric price value and verify presence of tax-inclusive phrasing.
- **Layer 3 (Product/MVP Decision):** Active MVP check. Missing price or missing tax phrase routes to `POTENTIAL_NON_COMPLIANCE`.

### 6. Check 6: Consumer Care Details (Rule 6(1)(e))
- **Layer 1 (Legal Fact):** Statutory text states: name, address, telephone number, and e-mail address of the person or office who can be contacted in case of consumer complaints.
- **Layer 2 (Engineering Interpretation):** Check for identifiable consumer complaint point of contact.
- **Layer 3 (Product/MVP Decision):** Active MVP check. *Caution:* An engineering proposal that "any one contact channel is sufficient" is an interpretation, NOT an established statutory exemption (see LR-005). Until formally clarified in an approved legal specification, missing contact channels must route to `REQUIRES_REVIEW` rather than generating an automatic `PASS`.

---

## SECTION H: AI Boundary & Operational Pipeline

ComplianceScan enforces strict separation between perception, extraction, deterministic logic, and human adjudication:

```text
Package Evidence
      ↓
Image Processing / Quality
      ↓
PaddleOCR (Reads raw text, bounding boxes, confidence)
      ↓
Gemini 2.5 Flash (Understands semantics, structures declarations)
      ↓
Backend Validation (Validates structure, types, confidence thresholds)
      ↓
Applicability Engine (Determines statutory relevance per commodity/package)
      ↓
Deterministic Compliance Rules (Evaluates extracted data against rules)
      ↓
Findings + Evidence (Organizes findings with highlighted bounding boxes)
      ↓
Inspector Verification (Human officer inspects evidence and discrepancies)
      ↓
Reviewer Decision (Authorized official records final legal determination)
```

### Core Operating Principle
> **"PaddleOCR reads. Gemini understands. Backend validates. Applicability determines relevance. Rules evaluate. Evidence supports. Inspector verifies. Reviewer decides."**
> **"AI finds → Evidence proves → Officer decides."**

### Prohibitions on AI Behavior
AI components (Gemini / PaddleOCR) must NOT:
1. Make the final legal or compliance decision.
2. Invent or hallucinate missing declarations.
3. Silently resolve conflicting evidence or ambiguous dates.
4. Alter or dynamically rewrite legal rules.
5. Modify or tamper with original image evidence.
6. Finalize an inspection or close an audit case.
7. Alter finalized inspection history.

---

## SECTION I: Country of Origin (COO) Legal Analysis

The Country of Origin declaration was analyzed across statutory gazettes and project applicability rules:

### 1. Statutory Ground Truth (Rule 6(1)(da) via G.S.R. 629(E) 2017)
- Rule 6(1)(da) states: *"for packages containing imported products, the name of the country of origin or manufacture or assembly shall be mentioned on the package."*
- **Applicability:** Mandatory strictly for **imported** commodities.
- **Domestic Commodity Logic:** A domestic product has no statutory obligation under Rule 6(1)(da) to declare Country of Origin on its physical label. ComplianceScan returning `NOT_APPLICABLE` when `is_imported == false` is legally accurate.
- **Unknown Import Status:** When import status is unknown, the system cannot safely assume the package is domestic. The check must route to `REQUIRES_REVIEW` or `INCOMPLETE`.

### 2. E-Commerce Marketplace Obligations (G.S.R. 128(E) 2026 & G.S.R. 312(E) 2026)
- G.S.R. 128(E) inserted Rule 6(10A) (in force 01-07-2026) requiring e-commerce platforms selling imported items to provide a searchable/sortable COO filter.
- G.S.R. 312(E) substitutes Rule 6(10A) effective 01-07-2027.
- **Classification:** Deferred Statutory Capability. Governs digital platform interfaces, not physical retail label verification.

### 3. AEO Customs Bonded Warehouses (G.S.R. 418(E) 2026)
- Grants labelling flexibilities in bonded warehouses for AEO Tier-2/3 importers; mandates importer online registration updates.
- **Classification:** Customs logistics exception; deferred capability.

---

## SECTION J: Project Documentation Change Impact Matrix (Candidate Proposals Only)

The following candidate updates were identified during this audit. **IMPORTANT:** These represent proposed changes for review; **no main specification documents have been modified during Phase 0**.

| Document Path | Current Text / Assumption | Statutory Ground Truth & Reality | Candidate Proposed Change | Action Status |
|---|---|---|---|---|
| `Documentation/06_Compliance_Rules.md` | §3 lists 6 checks without mentioning Unit Sale Price | G.S.R. 779(E) (2021) made USP mandatory under Rule 6(1)(f) since 01-01-2023 | Add informative section: "Rule 6(1)(f) Unit Sale Price: Documented Statutory Gap (Implementation Phase TBD)"; maintain 6 MVP checks | CANDIDATE PROPOSAL (Pending Approval) |
| `Documentation/06_Compliance_Rules.md` | §2 references outdated 4-state vocabulary | Project baseline is the 6-state vocabulary (`PASS`, `POTENTIAL_NON_COMPLIANCE`, etc.) | Align result vocabulary table to the authoritative 6 project states | CANDIDATE PROPOSAL (Pending Approval) |
| `Documentation/05_Domain_Specification_v2.0.md` | Mentions COO as physical check only | G.S.R. 128(E) (2026) created digital e-commerce COO obligations | Add informational reference to Rule 6(10A) as a deferred digital capability | CANDIDATE PROPOSAL (Pending Approval) |
| `MVP_BUILD_SCOPE_v2.0.md` | Lists 6 checks as exhaustive LMPC scope | 6 checks represent prioritized MVP scope; USP is an active statutory mandate deferred | Annotate scope table: "Six MVP compliance checks (USP cataloged as documented gap DELTA-001; phase TBD)" | CANDIDATE PROPOSAL (Pending Approval) |

---

## SECTION K: Legal and Engineering Delta Register

| Delta ID | Affected Rule | Legal Source | Summary of Delta | Classification | System Impact | Proposed Engineering Resolution |
|---|---|---|---|---|---|---|
| **DELTA-001** | Rule 6(1)(f) | G.S.R. 779(E) (2021) | Unit Sale Price mandatory on packages measured by weight/volume/length since 01-01-2023 | STATUTORY_GAP | Scope Awareness | **Document the statutory gap; implementation phase remains TBD unless explicitly approved.** Do not add to current MVP. |
| **DELTA-002** | Rule 6(10A) | G.S.R. 128(E) (2026) | E-commerce platforms must provide sortable/searchable COO filter for imported items (in force 01-07-2026) | DEFERRED_CAPABILITY | Digital Auditing | Catalog as deferred capability. No impact on physical label MVP. |
| **DELTA-003** | Rule 6(10A) | G.S.R. 312(E) (2026) | Long-term substitution of Rule 6(10A) with commencement date 01-07-2027 | INFORMATIONAL | Roadmap Tracking | Track in legal provenance index as future legislative milestone. |
| **DELTA-004** | Rule 26 | G.S.R. 778(E) (2025) | Medical devices packages exempted from LMPC declarations where governed by MDR, 2017 | APPLICABILITY | Routing | Add medical device exclusion rule to domain applicability matrix. |
| **DELTA-005** | Rule 26(a) | G.S.R. 881(E) (2025) | Pan masala packages exempted from Rule 26(a) standard packaging constraints | APPLICABILITY | Domain Specialization | Record in commodity exemptions catalog. |
| **DELTA-006** | Rule 2(aa),(da),(hc) | G.S.R. 722(E) (2023) | Codified definitions for Combination, Group, and Multi-Piece packages (effective 01-01-2024) | DEFERRED_CAPABILITY | Domain Hierarchy | Preserve for future packaging structural models. |
| **DELTA-007** | Rule 6(10) | G.S.R. 629(E) (2017) | E-commerce digital platform mandatory declarations framework | FOUNDATIONAL | Citation Provenance | Update citations in compliance documentation. |
| **DELTA-008** | Rule 6(1)(e) | G.S.R. 779(E) (2021) | Retail price format simplified to Indian currency with inclusive of taxes wording | CLARIFICATION | Syntax Validation | Ensure test suites accommodate standard Indian currency symbols and tax phrasing. |
| **DELTA-009** | Rule 6(4) | G.S.R. 456(E) (2023) | Electronic products permitted to declare mandatory details via QR code | DEFERRED_CAPABILITY | Multi-Modal | Catalog as deferred QR-code extraction capability. |
| **DELTA-010** | Rule 6(1)(a) Proviso | G.S.R. 418(E) (2026) | AEO Tier-2/3 bonded warehouse labelling relaxations and importer annual digital portal updates | REGULATORY_LOGISTICS | Customs Logistics | Document in legal archive register as logistics exception. |

---

## SECTION L: Confirmed Baseline Preservation Register

The following core project components are **preserved as the current project baseline unless superseded by an approved specification change**:

1. **Deterministic Rule Engine Architecture:** Pure rule functions operating on structured declaration data, isolated from non-deterministic OCR/vision extraction.
2. **Authoritative Six-State Result Vocabulary:** `PASS`, `POTENTIAL_NON_COMPLIANCE`, `REQUIRES_REVIEW`, `NOT_APPLICABLE`, `INCOMPLETE`, `PROCESSING_FAILED`.
3. **Six MVP Compliance Checks:** The prioritized product scope targeting Manufacturer, Commodity Name, Net Quantity, Date, MRP, and Consumer Care.
4. **Applicability-First Logic:** Rules are evaluated only after package applicability (retail, domestic vs imported, specialized) is determined.
5. **Zero-Trust Audit Trail:** Tamper-evident, hash-linked execution logs preserving immutable run records.
6. **Human-in-the-Loop Adjudication:** System provides structured observations and candidate findings; authorized human officers make inspection decisions.

---

## SECTION M: Deferred / Future-Scope Legal Capabilities Register

*Note: The following 13 items represent a regulatory reference backlog. Cataloging a statutory provision does NOT constitute an approved product roadmap feature or implementation commitment.*

| Item Code | Regulatory Subject | Statutory Source | Regulatory Category |
|---|---|---|---|
| **FUT-001** | Unit Sale Price (USP) Rule Capability | G.S.R. 779(E) & G.S.R. 226(E) | Deferred Statutory Gap (Phase TBD) |
| **FUT-002** | E-Commerce Sortable COO Filter Verification | G.S.R. 128(E) & G.S.R. 312(E) | Deferred Digital Marketplace Capability |
| **FUT-003** | Electronic Product QR Code Validation | G.S.R. 456(E) (2023) | Deferred Multi-Modal Capability |
| **FUT-004** | Multi-Piece & Combination Package Hierarchy | G.S.R. 722(E) (2023) | Deferred Structural Packaging Model |
| **FUT-005** | Edible Oil Temperature-Specific Density SOP | SOP dt. 29-12-2023 | Deferred Commodity SOP |
| **FUT-006** | Readymade Garment Specific Tag Verification | G.S.R. 858(E) (2022) | Deferred Commodity Standard |
| **FUT-007** | Medical Device MDR 2017 Regulatory Routing | G.S.R. 778(E) (2025) | Deferred Regulatory Routing |
| **FUT-008** | Small Package (<= 10g/ml) Carton Rule Validation | Rule 26(a) | Deferred Threshold Logic |
| **FUT-009** | Institutional / Industrial Package Flagging | Rule 3 & Rule 2(p) | Deferred Threshold Logic |
| **FUT-010** | Dual Labelling Penalty / Barcode Scanning | G.S.R. 629(E) | Deferred Physical Verification |
| **FUT-011** | Wholesale Packages (Chapter III) Validation | Chapter III, PCR 2011 | Deferred Wholesale Scope |
| **FUT-012** | AEO Bonded Warehouse Importer Verification | G.S.R. 418(E) (2026) | Deferred Customs Logistics |
| **FUT-013** | Second Schedule Standard Size Verification | Second Schedule, PCR 2011 | Deferred Standardization Checking |

---

## SECTION N: Ambiguities and External Legal Review Items

The following items represent statutory ambiguities and engineering interpretations flagged for external legal review:

1. **LR-001: Enforcement Status of Unit Sale Price on Pre-Printed Inventory:** While G.S.R. 862(E) set the final effective date as 01-01-2023, multiple administrative advisories permitted inventory depletion. *Question:* How should archival or transition-period packaging manufactured around 2022–2023 be handled during retrospective audits?
2. **LR-002: QR Code Declarations on Electronic Products:** G.S.R. 456(E) allows electronic products to declare certain details via QR code, provided MRP, Net Qty, Consumer Care, and Importer remain physical. *Question:* Does absence of an explicit statement "Scan QR code for other details" invalidate the electronic declaration?
3. **LR-003: Definition of "Imported Package" under AEO Tier-2/3:** G.S.R. 418(E) grants bonded warehouse labelling flexibilities. *Question:* Must digital marketplace listings for AEO-cleared goods verify bonded warehouse credentials prior to final sale?
4. **LR-004: Enforcement Treatment of Non-Standard Metric Symbols:** Rule 13 prescribes standard units (g, kg, etc.). *Question:* Do state enforcement authorities treat informal representations ("gms", "Kgs", "ltrs") as strict compounding offences or remediable clerical defects? *(Current system posture: route to `POTENTIAL_NON_COMPLIANCE` / `REQUIRES_REVIEW` for officer verification).*
5. **LR-005: Consumer Care Multi-Channel Fallback vs Complete Contact Details:** Rule 6(1)(e) text lists name, address, telephone, and email. *Question:* Does absence of one channel (e.g., email present, but phone absent) constitute statutory non-compliance, or is a single functional channel legally sufficient? *(Current system posture: route missing channels to `REQUIRES_REVIEW` rather than an automatic `PASS`).*

---

## SECTION O: Final Recommendations & Phase 0 Gate Scorecard

### Recommendations for Engineering Lead:
1. **Maintain Strict MVP Scope:** Execute the Six MVP compliance checks as the core MVP scope. Do not expand MVP scope to include Unit Sale Price or digital marketplace COO filters.
2. **Preserve Documented Gap:** Keep Unit Sale Price registered as `DELTA-001` (Documented statutory gap; implementation phase TBD).
3. **Obtain Human Approval Prior to Specification Updates:** Do not modify `Documentation/06_Compliance_Rules.md` or other specifications until this reconciliation report is reviewed and formally approved.

### Phase 0 Reconciliation Gate Scorecard

| Gate Item | Target Requirement | Measured Audit Status | Gate Decision |
|---|---|---|---|
| **Legal Source Coverage** | 100% of collected source files audited | 40 of 40 PDF files cataloged, verified, and cross-referenced | **PASS** |
| **Archive Integrity** | All years accounted for (2011–2026) | 12 year folders, 40 documents verified on filesystem | **PASS** |
| **Deltas Identified & Classified** | All statutory discrepancies categorized | 10 deltas registered (`DELTA-001` through `DELTA-010`) | **PASS** |
| **Documentation Impact Formulated** | Specification candidate updates identified | 4 documents analyzed; candidate changes drafted without modifying specs | **PASS** |
| **Result Vocabulary Reconciled** | Authoritative 6-state project model enforced | `PASS`, `POTENTIAL_NON_COMPLIANCE`, `REQUIRES_REVIEW`, `NOT_APPLICABLE`, `INCOMPLETE`, `PROCESSING_FAILED` | **PASS** |
| **Terminology Corrected** | "Six MVP compliance checks" adopted | Differentiated from unconditional declarations; COO applicability isolated | **PASS** |
| **USP Scope Controlled** | Statutory gap documented, not auto-committed | Classed as "Documented gap; phase TBD"; zero MVP creep | **PASS** |
| **Future Scope Controlled** | Cataloged capabilities NOT treated as features | 13 provisions classified as reference backlog (`FUT-001` to `FUT-013`) | **PASS** |
| **Legal Ambiguities Logged** | Uncertain interpretations isolated | 5 specific items logged for legal counsel review (`LR-001` to `LR-005`) | **PASS** |
| **Zero-Code Invariant** | No application code written in Phase 0 | 0 lines of application code, database schemas, or scaffolding created | **PASS** |
| **OVERALL GATE STATUS** | Reconciled audit ready for human sign-off | **PHASE 0 AUDIT ARTIFACT READY FOR HUMAN APPROVAL** | **PASS** |

*(Note: Gate PASS signifies that the Phase 0 Legal Reconciliation Audit is complete, internally consistent, and prepared for human review. It does NOT constitute automatic architecture approval or automatic authorization to begin Phase 1).*

---

## SECTION P: Correction Pass Change Log

| Issue # | Issue Identified | Original Problematic Statement / Concept | Correction Made in This Pass | Reason for Correction | Affects MVP Scope? | Human Review Required? |
|---|---|---|---|---|---|---|
| **CP-01** | Outdated result vocabulary | Asserted that 4-state vocabulary (`COMPLIANT`, `NON_COMPLIANT`, etc.) remains valid | Replaced with authoritative 6-state vocabulary (`PASS`, `POTENTIAL_NON_COMPLIANCE`, `REQUIRES_REVIEW`, `NOT_APPLICABLE`, `INCOMPLETE`, `PROCESSING_FAILED`) | Align with authoritative project state model; preserve distinction between technical failures and non-compliance | No | No (Adopted project baseline) |
| **CP-02** | Unsupported architectural absolute | "Core Architecture Remains 100% Valid" | Replaced with: "No legal finding identified in this Phase 0 reconciliation currently requires abandonment of the core architectural principles." | Avoid overstating validation before operational workflow and implementation review | No | No |
| **CP-03** | Unsupported change-control absolute | "100% sound with zero modifications permitted" | Replaced with: "Preserved as the current project baseline unless superseded by an approved specification change." | Permit disciplined change control without artificial immutability | No | No |
| **CP-04** | Premature USP implementation commitment | "schedule USP for Phase 1" | Replaced with: "Document the statutory gap; implementation phase remains TBD unless explicitly approved." | Prevent unauthorized scope creep; retain strict 6-check MVP scope | No | Yes (Phase roadmap decision) |
| **CP-05** | Future scope framed as committed features | 13 FUT items framed as approved upcoming product features | Reframed section as "Deferred / Future-Scope Legal Capabilities Register"; explicitly noted cataloging does not commit implementation | Prevent regulatory reference catalog from being misconstrued as an engineering roadmap commitment | No | No |
| **CP-06** | Terminology overstatement | "Six mandatory declarations" | Replaced with: "Six MVP compliance checks" | Applicability affects individual checks (especially Country of Origin); declarations are not unconditional | No | No |
| **CP-07** | Consumer care multi-channel assumption | Multi-channel fallback presented as legally confirmed | Clarified that statutory text lists all 4 contact channels; multi-channel fallback is an engineering proposal flagged for review (LR-005) | Maintain honesty regarding statutory ambiguity; avoid turning uncertain interpretations into automatic PASS | No | Yes (Legal counsel confirmation) |
| **CP-08** | Date format over-constraining | Asserted date format must be strictly MM/YYYY | Clarified required info (month + year) vs syntax; noted multiple representations may be valid pending spec approval | Avoid creating overly strict validators without specification backing | No | No |
| **CP-09** | Metric unit enforcement over-certainty | Asserted non-standard symbols ("gms") definitely constitute actionable technical violations | Routed to `POTENTIAL_NON_COMPLIANCE` / `REQUIRES_REVIEW`; flagged compounding/enforcement uncertainty under LR-004 | Avoid asserting unverified legal compounding outcomes; human officer verifies | No | Yes (Legal counsel confirmation) |
| **CP-10** | Premature Phase 1 gate declaration | "READY FOR PHASE 1 IMPLEMENTATION GATE" | Replaced with: "PHASE 0 AUDIT ARTIFACT READY FOR HUMAN APPROVAL" | Phase 0 gate signifies audit readiness for human review, not automatic code authorization | No | Yes (Human gate sign-off) |

---

## SECTION Q: Human-Approval Checklist

- [x] 40 legal source archive preserved and cataloged (`Legal Reference Index.md`)
- [x] Legal source vs runtime logic distinction preserved (no dynamic PDF parsing)
- [x] Effective dates represented correctly across all amendments (2011–2026)
- [x] Six MVP compliance checks preserved as current product scope
- [x] Six-state project result vocabulary restored (`PASS`, `POTENTIAL_NON_COMPLIANCE`, `REQUIRES_REVIEW`, `NOT_APPLICABLE`, `INCOMPLETE`, `PROCESSING_FAILED`)
- [x] Country of Origin remains strictly applicability-driven ("Applicability First")
- [x] Unit Sale Price documented as statutory gap, NOT an automatic Phase 1 commitment
- [x] Deferred legal capabilities cataloged without being treated as committed product features
- [x] Uncertain legal interpretations clearly marked and flagged for external review (`LR-001` to `LR-005`)
- [x] No application code, database schemas, or API endpoints written
- [x] No architecture redesign performed
- [x] No specification changes automatically applied to `Documentation/` or `MVP_BUILD_SCOPE`
- [ ] **Phase 0 Audit Artifact Reviewed and Approved by Human Decision-Maker**

---

## SECTION R: Agent-Proposed Better Approach

No additional agent-proposed approach identified.
