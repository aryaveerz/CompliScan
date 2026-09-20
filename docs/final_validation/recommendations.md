# CompliScan LM — Engineering & Operational Recommendations

**Document Version:** 1.0.0  
**Date:** September 20, 2026  
**Target:** Staging Deployment, Manual Field Validation & SIH Demonstration

---

## 1. Immediate Pre-Demonstration Recommendations

### Rec 1: Use Multi-Image Sample Packaging in Demonstrations
- When demonstrating the complete pipeline to SIH evaluators or regulatory stakeholders, submit 2 to 3 photos per product (e.g., Front label for commodity/brand, Back label for MRP/net qty/manufacturer/consumer care).
- This showcases the system's multi-evidence aggregation, cross-panel OCR synchronization, and unified compliance rollup.

### Rec 2: Highlight Deterministic Explainability & Provenance Chains
- In presentations, emphasize that **AI never makes the legal compliance decision**. Show how the UI draws bounding boxes from extracted text back to the original image pixels, and how Rule Citations (e.g., Rule 6(1)(a), Rule 6(1)(d)) link deterministically to statutory criteria.

### Rec 3: Demonstrate Reviewer Adjudication & Override Workflow
- Walk through a sample case where an inspector flags a field as `REQUIRES_REVIEW` and a senior reviewer adjudicates the final regulatory determination with an immutable audit rationale.

---

## 2. Post-MVP Roadmap Recommendations (Phase 7+)

1. **Physical Measurement Calibration Target (AR Marker):**  
   Introduce a standardized 10mm fiducial sticker on packaging to allow sub-millimeter font height measurement in compliance with Rule 9.

2. **Multilingual Regional Language OCR:**  
   Expand RapidOCR model weights to support Devanagari (Hindi), Tamil, Telugu, and Bengali scripts for regional pre-packaged commodities.

3. **Background Worker Deployment via Redis/Celery:**  
   Transition from PostgreSQL table-based job polling (`claim_next_job`) to dedicated Celery/Redis workers for high-scale enterprise deployments (>10,000 inspections/day).

4. **WebPush / In-App Notification Engine:**  
   Enable live push notifications to inspectors when background OCR and extraction jobs complete.
