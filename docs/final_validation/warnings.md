# CompliScan LM — Validation Warnings & Operational Considerations

**Document Version:** 1.0.0  
**Date:** September 20, 2026  
**Scope:** Automated Validation Campaign

---

## 1. Summary of Operational Warnings

The following operational conditions were observed during the validation campaign across real product packaging. None of these constitute software defects; they represent operational boundaries and physical constraints that human inspectors and deployment operators must recognize.

---

## 2. Detailed Warning Items

### WARN-01: Multi-Image Evidence Requirement for Comprehensive Compliance
- **Description:** Pre-packaged commodities under the Legal Metrology (Packaged Commodities) Rules, 2011 mandate disclosures across various panels (Principal Display Panel, Information Panel, Bottom/Top seals).
- **Operational Reality:** A single photograph rarely captures all 7 statutory fields simultaneously.
- **Guidance:** Inspectors must be trained to capture multi-angle evidence (Front, Back, Bottom) within the same inspection case to ensure full statutory coverage.

### WARN-02: Lighting and Glare on Reflective Foil / Laminated Packaging
- **Description:** Reflective packaging (e.g., silver foil on *Serum* bottles, metallic prints on *Noodles* packets) can cause localized glare when photographed under direct flash or strong sunlight.
- **System Defense:** The Image Quality Assessment (IQA) engine evaluates overexposure and contrast. When glare degrades text readability, IQA returns `NEEDS_REVIEW` or `UNUSABLE`.
- **Guidance:** Camera acquisition guidance in the mobile UI prompts the inspector to avoid direct glare.

### WARN-03: Font Size Physical Measurement Limitation
- **Description:** Legal Metrology Rule 9 defines minimum numeral heights (e.g., 1.0mm to 6.0mm depending on net quantity).
- **System Scope:** In the MVP scope, font height measurement from 2D uncalibrated photographs without a physical calibration target (Fiducial marker) is mathematically indeterminate.
- **Guidance:** Font height compliance is flagged as `REQUIRES_REVIEW` for manual verification by the human inspector with physical calipers if contested.

### WARN-04: Offline Operation vs Gemini Cloud Connectivity
- **Description:** OCR and deterministic rule evaluation execute entirely locally (ONNX Runtime / Python engine). However, semantic structured extraction relies on Google Gemini 2.5 Flash API.
- **Guidance:** In low-connectivity field environments, jobs are queued in PostgreSQL. When internet connectivity is restored, the worker processes structured extraction and notifies the inspector.
