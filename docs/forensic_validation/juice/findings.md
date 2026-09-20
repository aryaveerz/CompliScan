# COMPLISCAN LM — DETAILED FORENSIC AUDIT FINDINGS
**Target Dataset**: Packaged Commodity — B Natural Guava Juice 1L (`G:\CompliScan\Test_Images\Juice`)  
**Product**: B Natural Guava Juice 1L TetraPak  

---

## 1. EVIDENCE ASSET ANALYSIS MATRIX

| Field | Image 1 (`IMG_20260920_040854.jpg`) | Image 2 (`IMG_20260920_040900.jpg`) | Image 3 (`IMG_20260920_040906.jpg`) | Image 4 (`IMG_20260920_040922.jpg`) |
|-------|------------------------------------|------------------------------------|------------------------------------|------------------------------------|
| **File Size** | 1,306,214 bytes | 1,199,889 bytes | 1,300,647 bytes | 1,261,675 bytes |
| **Dimensions** | 1080 x 1920 px | 1080 x 1920 px | 1080 x 1920 px | 1080 x 1920 px |
| **SHA-256** | `7987f3a2fcc2...` | `d0891ea5c2d1...` | `95db45287da0...` | `919b9530ea24...` |
| **IQA Sharpness** | 407.89 (USABLE) | 209.32 (USABLE) | 238.54 (USABLE) | 252.30 (USABLE) |
| **IQA Brightness**| 112.48 (USABLE) | 85.67 (USABLE) | 110.24 (USABLE) | 97.63 (USABLE) |
| **OCR Tokens** | 34 tokens | 4 tokens | 70 tokens | 8 tokens |
| **Primary Panel Content** | Ingredients & FSC Board details | Brand tagline ("Natural Source of Vit C") | Nutritional Information Table | Batch, MRP & Date Stamps (Top Seam) |
| **Gemini Status** | LIVE CALL SUCCESS | LIVE CALL SUCCESS | LIVE CALL SUCCESS | LIVE CALL SUCCESS |
| **Gemini Model** | `gemini-3.6-flash` | `gemini-3.6-flash` | `gemini-3.6-flash` | `gemini-3.6-flash` |
| **Prompt Tokens** | 4,378 tokens | 4,028 tokens | 4,747 tokens | 4,097 tokens |
| **Candidate Tokens** | 522 tokens | 505 tokens | 686 tokens | 812 tokens |
| **Thinking Tokens** | 1,699 tokens | 986 tokens | 3,594 tokens | 3,928 tokens |

---

## 2. STATUTORY COMPLIANCE FINDINGS (LEGAL METROLOGY RULES, 2011)

The system evaluated 7 statutory requirement domains across the 4 evidence assets, generating 28 total findings:

1. **Rule 6(1)(a) — Manufacturer Identity & Address**:
   - Extracted from Image 1 & 3: ITC Limited, Packaging & Manufactured details verified.
   - Result: `REQUIRES_REVIEW` (Inspector/Reviewer Adjudicated `PASS`).

2. **Rule 6(1)(b) — Commodity Name**:
   - Extracted from Image 1 & 2: "Guava Beverage / Packaged Fruit Juice".
   - Result: `REQUIRES_REVIEW` (Inspector/Reviewer Adjudicated `PASS`).

3. **Rule 6(1)(c) — Net Quantity**:
   - Extracted from Image 1 & 3: "1 L / 1000 ml".
   - Result: `REQUIRES_REVIEW` (Inspector/Reviewer Adjudicated `PASS`).

4. **Rule 6(1)(d) — Date of Manufacture / Packing**:
   - Extracted from Image 4 (Top Seam Stamp): `22/07/26` (Mfg Date) & `21/04/27` (Expiry Date).
   - OCR raw string: `9G1220726_146.00`.
   - Result: `REQUIRES_REVIEW` (Inspector/Reviewer Adjudicated `PASS`).

5. **Rule 6(1)(e) — Maximum Retail Price (MRP)**:
   - Extracted from Image 4 (Top Seam Stamp): `₹146.00` (Incl. of all taxes).
   - Result: `REQUIRES_REVIEW` (Inspector/Reviewer Adjudicated `PASS` after Inspector correction).

6. **Rule 6(1)(f) — Consumer Care Details**:
   - Extracted from Image 1: Phone & Email helpline verified.
   - Result: `PASS`.

7. **Rule 6(1)(da) — Country of Origin**:
   - Evaluated for Domestic Product Docket.
   - Result: `NOT_APPLICABLE`.
