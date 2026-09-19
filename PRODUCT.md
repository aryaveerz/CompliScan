# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Inspectors (Field & Desk Officers):** Conduct and document packaged-commodity inspections across physical retail and e-commerce channels. They capture product/package or online-listing evidence, review OCR and structured declaration extraction, verify which statutory declarations apply, examine compliance findings against applicable rules, correct extracted information when necessary, add manual observations or evidence, and submit inspection cases for independent review.
- **Reviewers (Reviewing Officers):** Independently review submitted inspections. They examine the primary and supplementary evidence, extracted declarations, applicability assessments, findings, and audit history; request additional evidence or clarification when required; confirm or override findings with recorded statutory justifications; and formally finalize the inspection outcome.

## Product Purpose

CompliScan LM is a professional regulatory inspection and compliance-assistance platform for packaged commodities. It exists to provide an evidence-driven, transparent, and legally defensible workspace that streamlines metrology compliance audits under the Legal Metrology Act, 2009 and Legal Metrology (Packaged Commodities) Rules, 2011. Success means accurate declaration verification, indisputable chain-of-custody, and rigorous human-in-the-loop adjudication that withstands regulatory scrutiny.

## Positioning

CompliScan LM is an evidence-driven regulatory inspection workspace, not an autonomous legal-decision system. Its distinct mechanism combines:
1. Evidence capture and cryptographic hashing (SHA-256)
2. OCR and structured declaration extraction
3. Deterministic statutory applicability assessment
4. Rule-based compliance evaluation across mandatory declarations
5. Mandatory inspector verification and manual correction
6. Independent reviewer adjudication with recorded justification

**Core Thesis:** *AI finds → Evidence proves → Officer decides.* AI perceives and structures information; deterministic statutory rules validate requirements; human officers verify facts and make authoritative decisions.

## Operating Context

- **Regulatory Domain:** Legal Metrology Act, 2009 & Legal Metrology (Packaged Commodities) Rules, 2011 (as amended through 2026).
- **Physical & Digital Artifacts:** Retail packaging photographs, commodity label panels, e-commerce listings, gazette notifications, compounding orders, and statutory inspection notices.
- **Environment:** High-accountability government inspection workflows, desk-based reviews, and courtroom/appellate-ready audit files. Ergonomics demand high data density, clear visual split between evidence and findings, zero decorative ambiguity, and rapid keyboard/mouse triage.

## Capabilities and Constraints

- **Authoritative Six-State Assessment Model:** `PASS`, `POTENTIAL_NON_COMPLIANCE`, `REQUIRES_REVIEW`, `NOT_APPLICABLE`, `INCOMPLETE`, `PROCESSING_FAILED`.
- **Cryptographic Evidence Integrity:** Every uploaded evidence asset is validated for MIME/size, parsed for image decoding integrity, and fingerprinted with SHA-256.
- **Strict Role Separation & Invariants:**
  - Inspector: Creates cases, uploads evidence, verifies OCR, submits to review.
  - Reviewer: Adjudicates cases, approves/rejects findings, finalizes inspection.
  - No client-role trust: Roles are enforced exclusively from PostgreSQL `public.users.role`.
  - 1:1 Identity Mapping: Supabase Auth UUID maps strictly to `public.users.id`.
- **Immutable Audit Trail:** All state transitions, corrections, and review decisions are permanently recorded in `audit_events`.
- **No Autonomous Determination:** Software never issues legal penalties or unverified verdicts automatically.

## Brand Commitments

- **Name:** CompliScan LM (Legal Metrology Compliance Scanner).
- **Voice:** Authoritative, precise, objective, regulatory-grade, and transparent.
- **Design Language:** Functional clarity, high information density, evidence visibility, predictable workflows, and government-standard sobriety over consumer trends.

## Evidence on Hand

- **Authoritative Statutory Archive:** 40 official gazette and advisory PDFs (2011–2026) located in `g:\CompliScan\Legal_References\Packaged_Commodities\`.
- **Reconciliation Audit:** Reconciled engineering specifications in `Legal_References/Legal and Project Delta Report.md` and `Legal_References/Legal Reference Index.md`.
- **Active Backend & Database:** FastAPI service, SQLAlchemy async models, PostgreSQL database migrated to Alembic revision `8f4e21a69b12`.

## Product Principles

1. **AI Finds, Evidence Proves, Officer Decides:** Machine intelligence is strictly perceptual and assistive. Authority, verification, and legal liability remain with human officers.
2. **Deterministic Rule Validation:** Compliance evaluations follow hard-coded statutory rules and gazette standards, never stochastic LLM judgment.
3. **Evidence Primacy & Chain of Custody:** Every finding must visibly trace back to specific evidence pixels or text with verifiable cryptographic integrity.
4. **Independent Two-Party Review:** Clear operational separation between field inspection collection and senior officer review/sign-off.
5. **Ergonomic Density Over Novelty:** Prioritize fast verification, scannable compliance matrices, side-by-side evidence inspection, and accessibility over decorative visual exploration.

## Accessibility & Inclusion

- Target standard: WCAG 2.1 AA.
- High-contrast visual presentation for evidentiary label inspection.
- Full keyboard navigation across inspection panels, declaration tables, and modal workflows.
- Clear error states, accessible form labels, and screen-reader-compatible audit records.
