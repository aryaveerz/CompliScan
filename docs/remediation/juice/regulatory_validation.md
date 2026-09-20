# CompliScan LM — Statutory Regulatory Scope & Rule Evaluation Audit

## 1. Statutory Regulatory Scope (Gate 7)
CompliScan LM strictly enforces the statutory requirements of **Rule 6(1)** of the **Legal Metrology (Packaged Commodities) Rules, 2011**.
The pipeline operates strictly within this legal boundary without regulatory scope expansion.

---

## 2. Rule-by-Rule Evaluation Logic

### Rule 6(1)(a) — Manufacturer / Packer / Importer Identity & Address
- **Statutory Mandate**: Every package must display the name and complete address of the manufacturer, packer, or importer.
- **Rule Logic**: Requires non-empty name and address. If address lacks locality, pin code, or city, flags `POTENTIAL_NON_COMPLIANCE`. If both name and full address are present $\rightarrow$ `PASS`.
- **Juice Golden Path Finding**: `PASS` (Dabur India Limited, 8/3, Asaf Ali Road, New Delhi 110002).

### Rule 6(1)(b) — Common or Generic Name of Commodity
- **Statutory Mandate**: The package must clearly declare the common or generic name of the commodity contained therein.
- **Rule Logic**: If `observation_status == CONFLICTING` $\rightarrow$ `REQUIRES_REVIEW`. If observed $\rightarrow$ `PASS`.
- **Juice Golden Path Finding**: `REQUIRES_REVIEW` (Flagged due to `"Real Fruit Power Mixed Fruit Juice"` vs `"Mixed Fruit Beverage"` across panels). Adjudicated and reconciled by Reviewer as `PASS` per FSSAI category standard.

### Rule 6(1)(c) — Net Quantity in Standard Legal Units
- **Statutory Mandate**: Net quantity must be declared in terms of standard metric units ($g, kg, ml, l, m, N, U$).
- **Rule Logic**: Validates numeric quantity value $> 0$ and unit $\in \{\text{standard legal units}\}$. Non-standard symbols (e.g. `gms`, `GM`, `Kgs`) trigger `POTENTIAL_NON_COMPLIANCE`.
- **Juice Golden Path Finding**: `PASS` ($1000.0\text{ ml}$ with standard unit).

### Rule 6(1)(d) — Month and Year of Manufacture / Packing
- **Statutory Mandate**: The month and year in which the commodity is manufactured or packed must be declared.
- **Rule Logic**: Verifies $1 \le \text{month} \le 12$ and valid 4-digit $\text{year}$. Missing date triggers `POTENTIAL_NON_COMPLIANCE`.
- **Juice Golden Path Finding**: `PASS` ($07/2026$).

### Rule 6(1)(e) — Maximum Retail Price (MRP)
- **Statutory Mandate**: Retail sale price must be declared as Maximum Retail Price (MRP) with the mandatory phrase "inclusive of all taxes" or "incl. of all taxes".
- **Rule Logic**: Validates positive currency amount and boolean `includes_all_taxes_stated == True`. Missing tax wording triggers `POTENTIAL_NON_COMPLIANCE`.
- **Juice Golden Path Finding**: `PASS` ($\text{Rs. } 146.00\text{ (Incl. of all taxes)}$).

### Rule 6(1)(f) — Consumer Care Grievance Redressal
- **Statutory Mandate**: Name, address, telephone number, and email address of the person or office to contact in case of consumer complaints.
- **Rule Logic**: Verifies presence of at least one telephone channel and one electronic (email/address) channel.
- **Juice Golden Path Finding**: `PASS` (Consumer Cell, Toll-Free: 1800-103-1644, Email: `daburcares@feedback.dabur`, Address: Sahibabad, Ghaziabad 201010).

### Rule 6(1)(da) — Country of Origin (Conditional Rule)
- **Statutory Mandate**: Country of origin must be declared for packages containing imported commodities.
- **Rule Logic**:
  - If `origin_status == DOMESTIC` $\rightarrow$ `NOT_APPLICABLE` (Exempt from mandatory declaration under Rule 6(1)(da)).
  - If `origin_status == IMPORTED` and country is observed $\rightarrow$ `PASS`.
  - If `origin_status == IMPORTED` and country is not observed $\rightarrow$ `POTENTIAL_NON_COMPLIANCE`.
- **Juice Golden Path Finding**: `NOT_APPLICABLE` (Domestically manufactured package; exempt from mandatory country of origin requirement under Rule 6(1)(da)).

---

## 3. Statutory Finding Summary Table

| Requirement Name | Statutory Citation | Automated Finding | Reviewer Determination | Adjudicated Result | Final Compliance Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `manufacturer_identity` | Rule 6(1)(a) | `PASS` | `CONFIRMED` | `PASS` | **COMPLIANT** |
| `commodity_name` | Rule 6(1)(b) | `REQUIRES_REVIEW` | `OVERRIDDEN` | `PASS` | **COMPLIANT** |
| `net_quantity` | Rule 6(1)(c) | `PASS` | `CONFIRMED` | `PASS` | **COMPLIANT** |
| `manufacture_packing_date` | Rule 6(1)(d) | `PASS` | `CONFIRMED` | `PASS` | **COMPLIANT** |
| `mrp` | Rule 6(1)(e) | `PASS` | `CONFIRMED` | `PASS` | **COMPLIANT** |
| `consumer_care` | Rule 6(1)(f) | `PASS` | `CONFIRMED` | `PASS` | **COMPLIANT** |
| `country_of_origin` | Rule 6(1)(da) | `NOT_APPLICABLE` | `CONFIRMED` | `PASS` | **COMPLIANT (EXEMPT)** |
