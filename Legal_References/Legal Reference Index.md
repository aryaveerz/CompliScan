# Legal Reference Index

## ComplianceScan — Legal Metrology (Packaged Commodities) Rules, 2011

**Project:** ComplianceScan
**Reference Collection:** Legal Metrology (Packaged Commodities) Rules, 2011
**Source Authority:** Department of Consumer Affairs, Ministry of Consumer Affairs, Food & Public Distribution, Government of India
**Archive Scope:** 2011–2026
**Total Source Files:** 40
**Status:** Legal Source Archive / Provenance Reference
**Last Audit Date:** September 2026 (Phase 0 Reconciliation Audit — Controlled Correction Pass)

---

## 1. Purpose

This directory contains the legal and regulatory source documents collected for the ComplianceScan project in relation to the **Legal Metrology (Packaged Commodities) Rules, 2011** (LMPC Rules, 2011).

The collection contains:
- The principal Packaged Commodities Rules, 2011 (G.S.R. 202(E), 7 March 2011);
- Subsequent formal amendment notifications (2011–2026);
- Official corrigenda;
- Implementation guidelines and standard operating procedures (SOPs);
- Ministerial advisories and clarification orders;
- Specialized commodity relaxation / extension orders; and
- Recent 2025–2026 amendments (including e-commerce COO filters, AEO bonded warehousing, and medical device dereferencing).

The purpose of this archive is to preserve the **legal provenance** used during the specification, validation, and testing of ComplianceScan.

These documents are **source references**. They are not directly executed by runtime application code, and an LLM is strictly prohibited from directly deciding compliance from raw legal PDFs.

---

## 2. Critical Separation: Source Archive vs Runtime Rules

The legal PDFs stored in this archive must never be treated as directly executable code or parsed dynamically at runtime.

ComplianceScan follows strict separation of legal authority, formal specification, and execution:

```text
Official Legal Sources (PDF Archive: 40 Documents)
        ↓
Controlled Legal Audit (Phase 0 Reconciliation Report)
        ↓
Approved Legal Specification (Documentation/06_Compliance_Rules.md)
        ↓
Versioned Deterministic Rule Representation (TypeScript / JSON Ruleset)
        ↓
Runtime Rule Engine (Deterministic Pure Functions)
```

1. **Official Legal Sources**: Authoritative gazette notifications and administrative orders issued by the Government of India.
2. **Controlled Legal Audit**: Cross-referenced reconciliation identifying enforceable requirements, effective dates, applicability constraints, and exemptions.
3. **Approved Legal Specification**: Versioned, reviewed engineering documents (`05_Domain_Specification_v2.0.md`, `06_Compliance_Rules.md`) approved by human decision-makers.
4. **Versioned Deterministic Rule Representation**: Explicit machine-readable rule models with version identifiers.
5. **Runtime Rule Engine**: Pure deterministic functions validating structured declaration data against rule models. AI models (Gemini / PaddleOCR) are strictly confined to perception and structure extraction; they never make final compliance or legal determinations.

---

## 3. Archive Summary Statistics

| Metric | Value | Details |
|---|---|---|
| **Total Archive Documents** | 40 | 12 year directories (2011–2026) |
| **Year Distribution** | 2011 (7), 2012 (2), 2013 (1), 2014 (2), 2015 (1), 2016 (2), 2017 (2), 2021 (1), 2022 (5), 2023 (12), 2025 (2), 2026 (3) | Concentrated around 2022–2023 major rule overhauls |
| **Machine-Readable Text PDFs** | 26 | Digital text layer extracted via PyMuPDF |
| **Scanned Image / Bitmap PDFs** | 14 | Scanned gazette prints; verified via official notification registry and gazette numbers |
| **Current Target Checks (MVP)** | Six MVP Compliance Checks | 1. Manufacturer/Packer/Importer; 2. Commodity Name; 3. Net Quantity; 4. Month/Year; 5. MRP; 6. Consumer Care (Rule 6(1)(da) Country of Origin is applicability-driven) |
| **Deferred Statutory Capabilities** | 13 Cataloged Provisions | Regulatory backlog / awareness catalog; cataloging does NOT constitute committed product roadmap features |

---

## 4. Complete 40-Document Legal Source Catalog

The following table catalogs all 40 legal source documents in the repository, organized chronologically by folder and filename. Document categories distinguish statutory rules, amendments, corrigenda, guidelines, advisories, SOPs, historical transition extensions, and future-effective provisions.

| # | Year | Filename | Official Notification / Title | Gazette / Ref No. & Date | Core Subject / Legal Nature | Readability | Regulatory & System Classification |
|---|---|---|---|---|---|---|---|
| 1 | 2011 | `8(i)_0_1732860957.pdf` | Legal Metrology (Packaged Commodities) (Amendment) Rules, 2011 | G.S.R. 427(E) dt. 03-06-2011 | Amendment to principal 2011 rules prior to commencement | Scanned | Historical Amendment |
| 2 | 2011 | `8(ii)_0_1732860982.pdf` | Legal Metrology (Packaged Commodities) (Second Amendment) Rules, 2011 | G.S.R. 784(E) dt. 24-10-2011 | Second amendment extending implementation date to 01-04-2012 | Scanned | Historical Transition |
| 3 | 2011 | `8(iii)_0_1732861046.pdf` | Legal Metrology (Packaged Commodities) Rules, 2011 (Hindi Gazette Copy) | G.S.R. 202(E) dt. 07-03-2011 | Principal LMPC Rules, 2011 notification text in Hindi | Scanned | Historical Reference |
| 4 | 2011 | `8_1732871406.pdf` | Legal Metrology (Packaged Commodities) Rules, 2011 (Bilingual Official Gazette) | G.S.R. 202(E) dt. 07-03-2011 (effective 01-04-2011 / 01-04-2012) | **Foundational Principal Rules**. Establishes Chapter II, Rule 6 declarations, Second Schedule, Fifth Schedule | Scanned | **Principal Statutory Authority** |
| 5 | 2011 | `advisory_pcr(1)_0 (1)_1732860898.pdf` | Advisory on Implementation of PCR, 2011 | Advisory WM-10(5)/2011 dt. 2011 | Administrative guidance on transition from Standards of Weights & Measures (PC) Rules, 1977 | Scanned | Administrative Advisory |
| 6 | 2011 | `corrigendum_PCR_0_0_1732860695.pdf` | Corrigendum to G.S.R. 202(E) | Corrigendum dt. 2011 | Typographical and numerical corrections to the principal 2011 rules | Scanned | Statutory Corrigendum |
| 7 | 2011 | `guidelines dt 30_9_2011 for PCR(1)_0 (1)_1732860774.pdf` | Enforcement Guidelines under PCR, 2011 | Order No. WM-10(5)/2011 dt. 30-09-2011 | Guidelines to State Controllers on dual labelling transition and standard sizes | Scanned | Administrative Guideline |
| 8 | 2012 | `8(v)_0_1732861119.pdf` | Legal Metrology (Packaged Commodities) (Amendment) Rules, 2012 | G.S.R. dt. 2012 | Provisions on non-standard packaging and Second Schedule additions | Scanned | Statutory Amendment |
| 9 | 2012 | `8(vi)_0_1732861153.pdf` | Legal Metrology (Packaged Commodities) (Second Amendment) Rules, 2012 | G.S.R. dt. 2012 | Clarifications on net quantity tolerances and font height tables | Scanned | Statutory Amendment |
| 10 | 2013 | `8(vii)_0_1732861181.pdf` | Legal Metrology (Packaged Commodities) (Amendment) Rules, 2013 | G.S.R. dt. 2013 | Amendments regarding industrial/institutional consumer definitions | Scanned | Statutory Amendment |
| 11 | 2014 | `8(viii)_0 (1)_1732870622.pdf` | Legal Metrology (Packaged Commodities) (Amendment) Rules, 2014 | G.S.R. dt. 2014 | Provisions regarding retail dealer liabilities and manufacturer declarations | Scanned | Statutory Amendment |
| 12 | 2014 | `8(ix)_0_1732870718.pdf` | Legal Metrology (Packaged Commodities) (Second Amendment) Rules, 2014 | G.S.R. dt. 2014 | Updates to Second Schedule commodities | Scanned | Statutory Amendment |
| 13 | 2015 | `8(x)_0_1732870750.pdf` | Legal Metrology (Packaged Commodities) (Amendment) Rules, 2015 | G.S.R. dt. 2015 | Specific commodity net quantity exemptions and retail display rules | Scanned | Statutory Amendment |
| 14 | 2016 | `8(xi)_0_1732871315.pdf` | Legal Metrology (Packaged Commodities) (Amendment) Rules, 2016 | G.S.R. dt. 2016 | Amendments regarding font size standards and area of principal display panel | Scanned | Statutory Amendment |
| 15 | 2016 | `LM_Advisory_for_Readymade_Garments_0_1732710356.pdf` | Advisory on Readymade Garments | Advisory WM-10(28)/2016 dt. 2016 | Declarations applicable to readymade garments sold in loose / hung form | Scanned | Administrative Advisory |
| 16 | 2017 | `8(xii)_0_1732871346.pdf` | Legal Metrology (Packaged Commodities) (Amendment) Rules, 2017 | G.S.R. 629(E) dt. 23-06-2017 (effective 01-01-2018) | **Major Amendment**: Inserted Rule 6(10) mandating e-commerce platforms display all mandatory declarations; inserted Rule 6(1)(da) COO | Text | **Core Statutory Authority** |
| 17 | 2017 | `8(xiii)_0_1732871373.pdf` | Legal Metrology (Packaged Commodities) (Second Amendment) Rules, 2017 | G.S.R. dt. 2017 | Barcode, QR code, and consumer care electronic contact details guidelines | Text | Administrative Guideline |
| 18 | 2021 | `230946_1732871433.pdf` | Legal Metrology (Packaged Commodities) (Second Amendment) Rules, 2021 | G.S.R. 779(E) dt. 02-11-2021 (effective 01-01-2023) | **Landmark Reform**: (1) Inserted Rule 6(1)(f) Unit Sale Price; (2) Simplified date to month/year; (3) Revised MRP format | Text | **Core Statutory Authority** (USP is Documented Gap; Implementation TBD) |
| 19 | 2022 | `GSR226_1732871458.pdf` | Legal Metrology (Packaged Commodities) (Amendment) Rules, 2022 | G.S.R. 226(E) dt. 28-03-2022 | Amended G.S.R. 779(E) timelines and modified Unit Sale Price rounding rules | Text | Statutory Amendment |
| 20 | 2022 | `Notification -  Legal Metrology (QR Code)_1732871487.pdf` | Legal Metrology (Packaged Commodities) (Second Amendment) Rules, 2022 | G.S.R. 542(E) dt. 14-07-2022 | Allowed electronic products to declare details through QR code for 1 year | Text | Temporary Exemption (Historical) |
| 21 | 2022 | `PCR_1732871549.pdf` | Extension Notification for G.S.R. 779(E) | G.S.R. 709(E) dt. 22-09-2022 | Extended enforcement date of G.S.R. 779(E) from 01-10-2022 to 01-12-2022 | Text | Historical Transition |
| 22 | 2022 | `2022 3rd amendment in PCR Garments_1733228786.pdf` | Legal Metrology (Packaged Commodities) (Third Amendment) Rules, 2022 | G.S.R. 858(E) dt. 29-11-2022 | Specialized labelling relaxations for readymade garments and hosiery | Text | Specialized Statutory Rule |
| 23 | 2022 | `eGazette_30_nov_22_1732871630_1746006280.pdf` | Final Extension Notification for G.S.R. 779(E) | G.S.R. 862(E) dt. 30-11-2022 | Final extension establishing G.S.R. 779(E) in-force date as 01-01-2023 | Text | In-Force Milestone Notification |
| 24 | 2023 | `2023.01.27 amendment in amendment of 2023 PCR_1732871665.pdf` | Amendment in Amendment Rules | G.S.R. dt. 27-01-2023 | Transition relaxation for existing packaging inventory post-January 2023 | Text | Administrative Advisory |
| 25 | 2023 | `PCR_Amendment_24March2023_1732871698.pdf` | Extension Notification | G.S.R. dt. 24-03-2023 | Extension of relaxation for packaging material inventory to 30-06-2023 | Text | Administrative Advisory |
| 26 | 2023 | `2023.3.6 Fuel capacity vehicle tank_1732871722.pdf` | Vehicle Tank Fuel Capacity Order | Notification dt. 06-03-2023 | Exemption and standard calibration rules for motor vehicle fuel tanks | Text | Specialized Exemption (Out of Scope) |
| 27 | 2023 | `2023.3.6 farm produce upto 50 kg as per PCR_1732871747.pdf` | Exemption for Agricultural Produce up to 50 kg | G.S.R. dt. 06-03-2023 | Rule 26 amendment regarding wholesale/retail packages of farm produce up to 50 kg | Text | Statutory Exemption Rule |
| 28 | 2023 | `2023.06.5 amendment in amendment of PCR ext till 30.6.2023_1732871791.pdf` | Advisory on Inventory Clearance | Advisory dt. 05-06-2023 | Clarification on non-prosecution during inventory depletion window | Text | Administrative Advisory |
| 29 | 2023 | `2023.6.23 QR Code PCR amendment_1732871827.pdf` | Legal Metrology (Packaged Commodities) (Amendment) Rules, 2023 | G.S.R. 456(E) dt. 23-06-2023 | Permanent provision allowing electronic products to declare details via QR code (Rule 6(4)) | Text | Statutory Provision (Deferred Capability) |
| 30 | 2023 | `2023.6.28 amendment in amendment of PCR ext till 31.8.2023_1733228263.pdf` | Extension of Transition Period | G.S.R. dt. 28-06-2023 | Extension of inventory transition window to 31-08-2023 | Text | Historical Transition |
| 31 | 2023 | `2023.7.10 Medical Devices revision of prices_1733228304.pdf` | Advisory on Medical Devices Price Revision | Order dt. 10-07-2023 | Pricing stickers and compliance guidelines under NPPA / LMPC for medical devices | Text | Administrative Advisory |
| 32 | 2023 | `248432_1732871904.pdf` | Clarification on Packaging Rules | Advisory dt. 2023 | Administrative advisory on net quantity verification and compounding procedures | Text | Administrative Advisory |
| 33 | 2023 | `Amendment of PCR ext till 31.12.2023 (1)_1732871950.pdf` | Extension to 31-12-2023 | G.S.R. dt. 2023 | Final transition extension for pre-printed packaging inventory | Text | Historical Transition |
| 34 | 2023 | `2023.10.6 amendment in PCR_1732871982.pdf` | Legal Metrology (Packaged Commodities) (Second Amendment) Rules, 2023 | G.S.R. 722(E) dt. 06-10-2023 (effective 01-01-2024) | Definitions Inserted: Combination Package (Rule 2(aa)), Group Package (Rule 2(da)), Multi-Piece Package (Rule 2(hc)) | Text | Statutory Definitions (Deferred Capability) |
| 35 | 2023 | `2023.12.29 Standard Operating Procedure for Edible oil & Fats Net Quantity Measurement signed copy_1732872010.pdf` | Standard Operating Procedure (SOP) for Edible Oils and Fats | SOP dt. 29-12-2023 | Standardized protocol for net quantity measurement of edible oils at specified temperature | Text | Standard Operating Procedure |
| 36 | 2025 | `267107_1761404707.pdf` | Legal Metrology (Packaged Commodities) (Amendment) Rules, 2025 | G.S.R. 778(E) dt. 23-10-2025 | Medical Devices exclusion: Rule 26 amended to defer to Medical Devices Rules, 2017 | Text | Statutory Exemption Rule |
| 37 | 2025 | `2nd PCR Pan Masala_1764736734.pdf` | Legal Metrology (Packaged Commodities) (Second Amendment) Rules, 2025 | G.S.R. 881(E) dt. 02-12-2025 (effective 01-02-2026) | Exemption of Pan Masala packages from Rule 26(a) standard packaging constraints | Text | Statutory Exemption Rule |
| 38 | 2026 | `2026.02.13 PCR 1st COO Filter on e-commerce websites_1771231030.pdf` | Legal Metrology (Packaged Commodities) (Amendment) Rules, 2026 | G.S.R. 128(E) dt. 13-02-2026 (effective 01-07-2026) | Inserts Rule 6(10A) requiring e-commerce platforms selling imported items to provide sortable/searchable COO filter | Text | Digital Marketplace Mandate (Deferred Capability) |
| 39 | 2026 | `2026.4.27 PCR 2nd COO from 1.7.2027_1777348487.pdf` | Legal Metrology (Packaged Commodities) (Second Amendment) Rules, 2026 | G.S.R. 312(E) dt. 27-04-2026 (effective 01-07-2027) | Substitutes Rule 6(10A) with identical terms, shifting long-term e-commerce COO compliance milestone to 01-07-2027 | Text | Future Law Milestone (Informational) |
| 40 | 2026 | `PCR_3rd_29May2026_1780376045.pdf` | Legal Metrology (Packaged Commodities) (Third Amendment) Rules, 2026 | G.S.R. 418(E) dt. 29-05-2026 | Labelling relaxations for AEO Tier-2 & Tier-3 bonded warehouses; importer portal updates with COO | Text | Customs Logistics Provision (Deferred Capability) |

---

## 5. Temporal Mapping & Legal Lineage

The 40 documents establish a statutory lineage spanning 15 years:

1. **2011 Inception**: Promulgation of the Legal Metrology (Packaged Commodities) Rules, 2011 under Section 52 of the Legal Metrology Act, 2009, repealing the 1977 rules.
2. **2017 Digital Marketplace Expansion**: G.S.R. 629(E) extended Rule 6 declarations to e-commerce marketplaces and digital platforms, and introduced Rule 6(1)(da) Country of Origin for imported commodities.
3. **2021–2022 Pricing & Metric Reform**: G.S.R. 779(E) introduced Unit Sale Price (USP) under Rule 6(1)(f) and simplified date of manufacture, taking full effect 01-01-2023.
4. **2023 Packaging Structural Clarifications**: G.S.R. 456(E) codified QR codes for electronics; G.S.R. 722(E) codified multi-piece, combination, and group packaging definitions.
5. **2025 Regulatory Coordination**: G.S.R. 778(E) harmonized medical device packaging with CDSCO Medical Device Rules, 2017.
6. **2026 Provenance & Trade Facilitation**: G.S.R. 128(E) and G.S.R. 418(E) introduced e-commerce marketplace COO filter mandates and AEO customs warehouse labelling flexibilities.

---

## 6. Document Governance and Usage Rules

- **Engineering Prohibition**: Developers and engineers MUST NOT write runtime logic directly from these PDFs without an approved specification update in `Documentation/06_Compliance_Rules.md`.
- **Integrity Guarantee**: All source PDFs in this archive are permanent, uneditable legal artifacts.
- **Traceability Requirement**: Every rule in the deterministic engine must trace back to a specific Rule subclause documented in an approved legal specification.
- **No Scope Expansion**: Cataloging an advisory, SOP, or statutory amendment in this index does NOT automatically authorize or commit software implementation.

