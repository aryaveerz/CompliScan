# ComplianceScan — Architecture Decision Review Package for Antigravity

**Project:** ComplianceScan  
**SIH PS:** 26034  
**Purpose:** Give Antigravity the current architecture decisions for an independent technical review.

> ## IMPORTANT — THIS IS NOT THE FINAL IMPLEMENTATION SPECIFICATION
>
> These decisions are the current human-approved architecture baseline, but this document is being sent to Antigravity specifically to obtain its technical critique, optimization ideas, risks, contradictions, and better implementation approaches.
>
> **DO NOT START IMPLEMENTATION.**
>
> **DO NOT CREATE CODE, DATABASE SCHEMA, API CONTRACTS, UI, migrations, or deployment files.**
>
> First review the decisions and provide your technical assessment. If you believe something should change, explain why, identify the affected decision(s), and show the trade-offs and concrete alternative. Wait for human approval before treating any proposed change as architecture.
>
> Workflow:
>
> `Human Architecture → Antigravity Review → Human Evaluation → Possible Revision → Implementation Baseline → Implementation`
>
> Antigravity must not silently reinterpret, merge, remove, or replace decisions.

---

# 1. Project Intent

ComplianceScan is an inspection-assistance system for checking packaged commodities under the Legal Metrology (Packaged Commodities) Rules, 2011 and the approved project/legal scope.

Core philosophy:

> **AI finds → Evidence proves → Officer decides.**

```text
PRODUCT INPUT
     ↓
AI-POWERED ANALYSIS
     ├── Image Quality
     ├── PaddleOCR
     └── Gemini 2.5 Flash
     ↓
DECLARATION EXTRACTION
     ↓
PRODUCT / PACKAGE CONTEXT
     ↓
APPLICABILITY
     ↓
DETERMINISTIC COMPLIANCE
     ↓
EVIDENCE + FINDINGS
     ↓
INSPECTOR VERIFICATION
     ↓
REVIEWER DECISION
     ↓
FINALIZATION
     ↓
REPORT + HISTORY + SEARCH + DASHBOARD
```

The MVP is an inspection-assistance system, not an autonomous statutory enforcement system.

---

# 2. Locked MVP Compliance Scope

Six core domains:

1. Manufacturer / Packer / Importer identity and address
2. Common / Generic Product Name
3. Net Quantity + Standard Unit
4. Month / Year of Manufacture / Packing / Import
5. MRP Inclusive of All Taxes
6. Consumer Care Details

Country of Origin is applicability-driven:

- Imported = applicable
- Domestic = NOT_APPLICABLE
- Unknown = review/incomplete handling

Country of Origin is **not a seventh universal compliance check**.

USP is excluded from MVP.

Unit Sale Price is excluded from the current MVP.

Broad category-specific rule coverage is excluded from MVP.

Font-size assessment is a visual warning/assessment, not a definitive legal verdict where image scale prevents reliable determination.

Placement is a lightweight visual/evidence assessment, not universal packaging-layout legal verification.

The MVP uses a controlled legal-rule snapshot and does not implement a dynamic regulatory-update pipeline.

---

# 3. Global Invariants

- AI does not make the final legal decision.
- No evidence does not prove a fact.
- `NOT_OBSERVED` is not the same as missing.
- Unreadable is not automatically missing.
- `NOT_APPLICABLE` is not `PASS`.
- `INCOMPLETE` is not `POTENTIAL_NON_COMPLIANCE`.
- `PROCESSING_FAILED` is not non-compliance.
- Conflicting values route to `REQUIRES_REVIEW`.
- Technical processing failure is never a compliance conclusion.
- SHA-256 provides tamper/change detection; it is not proof of factual authenticity or a legal digital signature.

Core correction invariant:

> **Upstream correction → invalidate affected downstream state → recompute → preserve prior state/history → audit transition.**

---

# 4. Decision 01 — Core Product Philosophy

ComplianceScan follows:

```text
Scan
  ↓
Understand
  ↓
Determine Applicability
  ↓
Validate
  ↓
Prove with Evidence
  ↓
Officer Verifies
  ↓
Reviewer Decides
  ↓
Finalize
```

Differentiators:

- Applicability First
- Evidence-Based Findings
- Human-in-the-Loop
- Evidence Integrity / tamper-evident audit
- Physical ↔ Online Verification
- Adaptive Evidence Capture

---

# 5. Decision 02 — Operational Workflow

Eight operational stages:

```text
1. INITIALIZE
       ↓
2. CAPTURE EVIDENCE
       ↓
3. ANALYZE
   ├── Image Quality
   ├── OCR
   └── Structured Extraction
       ↓
4. DETERMINE APPLICABILITY
       ↓
5. EVALUATE COMPLIANCE
       ↓
6. INSPECTOR VERIFICATION
       ↓
7. REVIEWER DECISION
       ↓
8. FINALIZE
```

Reporting, history, search, and dashboard are outputs, not lifecycle stages.

---

# 6. Decision 03 — Roles & Human Workflow

Operational roles:

## Inspector

Can create inspections, capture context, upload evidence, start analysis, inspect OCR/declarations/confidence, correct extracted values, add manual observations, add supplemental evidence, verify applicability/compliance, submit, and view preliminary reports.

Cannot finalize, modify/delete accepted primary evidence, modify legal rules, alter audit history, mutate finalized records, or approve their own final decision.

## Reviewer

Can receive submitted inspections, inspect evidence/OCR/declarations/applicability/findings/history, confirm, correct/override assessments with reason, request additional evidence, and finalize.

Cannot modify controlled legal rules, delete finalized history, mutate finalized records, or finalize an inspection they submitted as Inspector.

Reviewer should not silently edit underlying extracted declarations. If underlying information is wrong, use revision/request or an explicitly recorded determination.

---

# 7. Decision 04 — State Model

## Master lifecycle

```text
DRAFT
EVIDENCE_UPLOADED
EXTRACTED
APPLICABILITY_EVALUATED
EVALUATED
IN_VERIFICATION
SUBMITTED_FOR_REVIEW
REQUIRES_REVISION
FINALIZED
```

## Processing

```text
IDLE
PROCESSING
FAILED
```

## Compliance result

```text
PASS
POTENTIAL_NON_COMPLIANCE
REQUIRES_REVIEW
NOT_APPLICABLE
INCOMPLETE
PROCESSING_FAILED
```

## Finalization

```text
UNFINALIZED
READ_ONLY
```

These dimensions remain separate.

---

# 8. Decision 05 — Evidence Architecture

```text
DRAFT UPLOAD
     ↓
PRIMARY EVIDENCE
     ↓
DERIVED EVIDENCE
     ↓
INSPECTION RECORD
     ↓
IMMUTABLE FINAL SNAPSHOT
```

- Draft uploads can be removed/replaced before acceptance.
- Accepted primary evidence is immutable.
- New evidence receives a new Evidence ID.
- Evidence receives SHA-256.
- Derived OCR/crops/highlights reference source evidence.
- Findings trace to derived evidence and ultimately original evidence.
- Finalized records are immutable.
- SHA-256 is integrity/change detection only.

Evidence categories:

- Primary = original package images
- Supplemental = later additional evidence
- Derived = OCR tokens, crops, highlights

Adaptive evidence capture is used; no arbitrary fixed photo count.

---

# 9. Decision 06 — AI/OCR Boundary

## PaddleOCR

Perception only:

- text
- location/bounding boxes
- OCR confidence

## Gemini 2.5 Flash

Semantic extraction/structuring only.

Gemini cannot decide legal compliance, determine final applicability, finalize, modify evidence/rules, or bypass workflow.

## Backend

Authoritative for schema validation, applicability, deterministic compliance evaluation, lifecycle, authorization, audit, and finalization.

## Human

Inspector verifies before submission; Reviewer independently decides and finalizes.

```text
OCR confidence
≠
AI extraction confidence
≠
Evidence sufficiency
≠
Compliance result
```

AI must not guess absent, unreadable, uncertain, or conflicting information.

---

# 10. Decision 07 — Data Model

Nine conceptual/domain entities:

1. `User`
2. `InspectionCase`
3. `EvidenceAsset`
4. `DerivedOcrToken`
5. `ExtractedDeclaration`
6. `ApplicabilityContext`
7. `ComplianceFinding`
8. `FinalAuditRecord`
9. `AuditEvent`

`InspectionCase` is the root aggregate.

No competing mutable final-result entity.

OCR tokens remain persistent and traceable.

Declarations preserve history/versioning.

Applicability is persisted with rule/version context.

Compliance findings preserve system findings separately from reviewer decisions.

`AuditEvent` is append-only chronological history.

---

# 11. Decision 08 — API Architecture

REST boundary:

```text
/api/v1
```

Logical groups:

```text
/auth
/inspections
/evidence
/analysis
/findings
/verification
/review
/reports
/audit
```

Rules:

- FastAPI is authoritative for auth, authorization, lifecycle, applicability, rules, evidence, review, and finalization.
- Analysis is asynchronous and may return `202 Accepted`.
- Evidence acceptance is explicit.
- Only draft evidence is removable.
- Corrections are audited commands, not silent mutations.
- Corrections invalidate affected downstream state and trigger recomputation.
- Rule evaluation is exposed through inspection operations, not arbitrary public rule CRUD.
- Reviewer decisions are explicit and audited.
- Finalization is a separate atomic operation.
- Finalized records are read-only.
- Reports derive from finalized snapshots.
- Audit is read-only.
- Standardized API errors are required.
- No lifecycle/RBAC bypass.

---

# 12. Decision 09 — UI Architecture

Functional routes:

```text
/dashboard
/inspections
/inspections/new
/inspections/:id
/inspections/:id/verify
/inspections/:id/result
/inspections/:id/history
/review/:id
```

Inspector:

```text
Dashboard → Inspections → Create → Evidence/Analysis → Verification → Submit
```

Reviewer:

```text
Review Queue → Reviewer Workspace → Decision → Finalize
```

After finalization:

```text
Result → PDF + History/Audit
```

Rules:

- backend state drives UI
- frontend is not security boundary
- original evidence distinct from derived/AI material
- AI observations, system findings, and human decisions visually distinct
- corrections preserve original values/history
- finalized records read-only
- reviewer has independent workspace
- avoid enterprise navigation bloat

---

# 13. Decision 10 — Technology / Platform Direction

Supabase is infrastructure, not domain authority.

```text
React → FastAPI → Supabase
```

Frontend does not directly manipulate inspection domain data.

---

# 14. Decision 11 — Final Technology Stack

```text
Frontend: React + TypeScript + Vite + Tailwind CSS
Backend: Python 3.11+ + FastAPI
Database: PostgreSQL
Platform: Supabase
Database hosting: Supabase PostgreSQL
Storage: Supabase Storage
Authentication: Supabase Auth
OCR: PaddleOCR
LLM: Gemini 2.5 Flash
ORM: SQLAlchemy
Migrations: Alembic
Containers: Docker
Processing: Asynchronous Worker
```

Provider-specific domain lock-in should be minimized where practical.

---

# 15. Decision 12 — Deployment Architecture

```text
Users
  ↓
Managed Frontend Hosting
  ↓ HTTPS
FastAPI Container
  ↓
Supabase
 ├── PostgreSQL
 ├── Storage
 └── Auth

FastAPI
  ↓
Background Worker
  ├── PaddleOCR
  └── Gemini
```

Rules:

- Managed frontend hosting.
- Containerized FastAPI.
- Separate asynchronous worker deployment.
- Supabase PostgreSQL, Storage, and Auth.
- Docker Compose for local development.
- Development → Staging → Production separation.
- Private evidence storage.
- Backend-controlled evidence access.
- Secrets server-side.
- Alembic migrations.
- Automated CI/CD.
- No Kubernetes/microservices/service mesh for MVP.
- Other hosting vendors remain replaceable.
- FastAPI remains the authoritative application/security/domain boundary.
- Containers are disposable/stateless.
- Persistent data never lives only inside containers.

Exact cloud providers for frontend/backend/worker/CI are implementation choices.

---

# 16. Decision 13 — Security Architecture

```text
User
 ↓
Supabase Auth
 ↓
FastAPI Identity Validation
 ↓
RBAC
 ↓
Resource Authorization
 ↓
State Validation
 ↓
Domain Operation
```

Rules:

- Server-side RBAC.
- Server-side inspection/resource authorization.
- Private evidence storage.
- No public evidence URLs.
- Server-side upload size/type/decode validation.
- Accepted primary evidence cannot be modified/deleted.
- Secrets are not in Git, frontend bundles, logs, database records, or responses.
- Protected APIs require authentication.
- Backend validates state transitions.
- Important actions generate append-only audit events.
- Audit supports tamper-evident hash chaining.
- Finalization creates immutable final snapshot.
- Finalized inspections are read-only.
- HTTPS is mandatory in deployed environments.
- Frontend security controls are supplementary only.

---

# 17. Decision 14 — Observability, Errors & Reliability

Core principle:

> Technical failure must never silently alter the meaning of an inspection.

Processing:

```text
IDLE
 ↓
PROCESSING
 ├──→ COMPLETED
 └──→ FAILED
```

Requirements:

- durable analysis job identity
- explicit job status
- bounded retries
- idempotency protection where appropriate
- standardized API error structure
- internal details hidden from users
- request IDs
- structured logs
- no secrets/tokens/unnecessary raw evidence in logs
- basic logs, metrics, and error tracking
- health/readiness checks
- external dependency failures cannot become compliance findings
- critical operations use transactions
- finalization is atomic and idempotent
- persistent evidence does not rely on local container storage
- technical failure never becomes a legal/compliance conclusion

---

# 18. Decision 15 — Testing & QA Architecture

Testing layers:

```text
Unit
 ↓
Integration
 ↓
End-to-End
 ↓
CI Quality Gates
```

Coverage:

- deterministic rule engine
- applicability
- state transitions
- RBAC/resource authorization
- evidence lifecycle
- SHA-256 integrity
- AI/OCR contracts and schemas
- API integration
- complete lifecycle
- negative workflows
- regression tests
- legal-rule fixtures
- contract tests
- CI lint/type-check/test/build gates

OCR is tested as perception.

AI confidence is not a legal threshold.

Tests preserve semantic distinctions between all result states.

---

# 19. Decision 16 — Performance & Scalability

Heavy analysis is asynchronous:

```text
Request
 ↓
Validate
 ↓
Create Analysis Job
 ↓
202 Accepted
 ↓
Worker
```

Rules:

- worker concurrency is configurable/bounded
- Gemini concurrency is controlled
- provider rate limits/transient failures are handled
- image size/dimension limits are configurable engineering parameters
- original evidence remains unchanged
- processing uses working/derived copies when needed
- database indexes follow actual query patterns
- large collections use pagination/cursors
- MVP search uses PostgreSQL
- API/worker are stateless and horizontally scalable
- worker can scale based on processing demand/queue depth
- compliance results are not detached generic cache entries
- performance numbers are measured engineering targets, not legal guarantees
- excess jobs are queued rather than silently dropped
- no Kubernetes/Kafka/dedicated search cluster unless measurements justify them

---

# 20. Decision 17 — Data Retention, Privacy & Backup

Data categories:

```text
Evidence
Inspection
Audit
Technical / Operational
```

Rules:

- draft evidence can be replaced/removed
- accepted primary evidence is immutable through normal operations
- supplemental evidence gets new ID + hash
- corrections preserve old/new values, actor, timestamp, reason, evidence context
- finalized inspections are immutable
- audit events are append-only through normal API
- technical logs and audit records can have different retention
- minimize unnecessary personal data
- credentials/tokens are not ordinary inspection data
- managed backup capabilities are used
- containers are never the sole persistent store
- dev/staging/prod data are isolated
- retention periods are configurable/policy-driven
- do not invent statutory retention periods
- recovery must preserve inspection data, evidence, audit history, and finalized snapshots
- normal workflow must not silently destroy historical integrity

---

# 21. Decision 18 — Configuration & Environment Management

Three categories:

```text
Environment Configuration
Application / Engineering Configuration
Controlled Legal Rules
```

Engineering configuration may include image limits, timeouts, retry count, worker concurrency, and pagination limits.

Legal behavior must not be casual environment variables or feature flags.

Rules:

- no secrets in Git
- `.env.example` contains placeholders/documentation only
- deployed secrets use managed secret/environment configuration
- configuration validated at startup
- invalid required configuration causes controlled startup failure
- operational roles cannot change system configuration
- feature flags cannot disable/alter legal rules
- AI model/processing configuration is controlled engineering configuration
- relevant AI/rule provenance is preserved where needed
- material configuration changes should be operationally traceable
- finalized inspections preserve necessary rule/version context
- configuration cannot bypass RBAC, lifecycle, evidence integrity, or controlled legal rules

---

# 22. Decision 19 — AI/OCR Operational Policy

Pipeline:

```text
Primary Evidence
 ↓
Image Quality
 ↓
PaddleOCR
 ↓
OCR Tokens
 ↓
Gemini 2.5 Flash
 ↓
Structured Declarations
 ↓
Backend Schema Validation
 ↓
Applicability
 ↓
Deterministic Compliance
```

Rules:

- PaddleOCR = perception only.
- Gemini = semantic extraction/structuring only.
- Neither produces authoritative legal decisions.
- Gemini output must conform to validated schema.
- Invalid output is rejected/reviewed.
- AI cannot guess unreadable/missing/uncertain values.
- Conflicts remain explicitly represented.
- Extracted declarations retain source/evidence traceability.
- OCR and extraction confidence remain separate.
- Evidence sufficiency remains separate.
- AI confidence is not a legal threshold.
- Model/prompt/OCR provenance is recorded for relevant analysis.
- Prompts are version-controlled artifacts.
- AI calls have bounded timeouts.
- Transient failures use bounded retries.
- Persistent failures become technical failure/review handling.
- Original evidence remains unchanged.
- Reprocessing follows upstream-invalidation invariant.
- Inspector verification remains mandatory before submission.
- Reviewer independently reviews.
- AI credentials remain server-side.
- Only required information should be sent to external AI services where practical.

---

# 23. Decision 20 — Reporting & Export Architecture

Reports are generated from finalized authoritative data:

```text
FinalAuditRecord
      ↓
Report Service
      ↓
PDF Inspection Report
```

The report is not a second mutable source of truth.

It should represent the finalized inspection context, relevant evidence references, findings, decisions, rule context, and finalization information required by the approved reporting specification.

Reports are not generated from merely the current frontend state.

---

# 24. Decision 21 — Search, Dashboard & Metrics

Search:

```text
Frontend
 ↓
FastAPI
 ↓
PostgreSQL
```

No dedicated search engine for MVP.

Search/filter fields can include:

- inspection ID
- product/commodity
- status
- compliance result
- inspector
- reviewer
- created date
- updated date
- finalization date
- import status

Rules:

- search + filters can be combined
- server-side sorting
- pagination/cursors
- reviewer queue is derived from inspection state
- dashboard derives from authoritative inspection data
- metrics are descriptive counts, not ratings/rankings
- active vs finalized data remain distinguishable
- historical finalized results remain stable
- search/dashboard enforce backend authorization
- frontend does not retrieve unrestricted database data for local filtering
- PostgreSQL is sufficient for MVP
- search/dashboard do not modify compliance decisions
- inspection data remains the source of truth

---

# 25. Decision 22 — Legal Rule Versioning & Temporal Evaluation

```text
Legal Sources
 ↓
Approved Legal Specification
 ↓
Controlled Rule Version
 ↓
Effective Date
 ↓
Applicability Resolver
 ↓
Deterministic Evaluation
```

Rules:

- rule sets have controlled versions
- versions have effective-date boundaries
- publication date ≠ effective date
- legal evaluation uses the approved relevant inspection/evaluation date
- backend resolves applicable rule version
- Inspectors cannot manually choose arbitrary rule versions
- Reviewers cannot manually choose arbitrary rule versions
- operational roles cannot modify controlled rules
- historical finalized inspections retain original rule-version context
- later rules do not silently mutate historical results
- re-evaluation, if ever supported, creates a traceable separate evaluation
- rule versions retain provenance to authoritative legal references
- applicability is evaluated before applicable compliance rules
- six MVP domains remain the controlled core
- Country of Origin remains applicability-driven
- rule changes are controlled changes, not ordinary runtime configuration
- each controlled rule version has deterministic tests
- temporal tests cover effective-date transitions
- finalized records retain sufficient rule/applicability context
- current rules are never retroactively imposed merely because software was updated

---

# 26. Decision 23 — Repository & Implementation Boundary

Repository:

```text
CompliScan/
├── frontend/
├── backend/
├── worker/
├── tests/
├── legal_references/
├── docs/
├── scripts/
├── docker/
├── .env.example
├── docker-compose.yml
└── README.md
```

Backend modular monolith:

```text
backend/app/
├── api/
├── auth/
├── inspections/
├── evidence/
├── analysis/
├── declarations/
├── applicability/
├── compliance/
├── verification/
├── review/
├── reports/
├── audit/
├── database/
├── config/
└── main.py
```

Rules:

- API routes remain thin.
- Domain/application services hold business logic.
- State-machine authority is centralized.
- Evidence operations are centralized.
- AI integrations use adapters/interfaces.
- PaddleOCR/Gemini remain replaceable adapters.
- Database access uses repository/data-access boundaries.
- Reports operate from finalized data.
- Audit events are generated by controlled operations.
- Tests mirror unit/integration/E2E architecture.
- Dependency direction is clear.
- No microservice split for MVP.
- Worker shares domain contracts/logic where practical.
- Legal PDFs are provenance/reference material, not automatically runtime rules.
- Antigravity must implement approved architecture rather than silently reinterpret it.
- Genuine architectural conflicts must be surfaced for human decision.

---

# 27. Decision 24 — Final Architecture Freeze

The architecture was frozen after cross-checking the previous decisions.

Final system:

```text
                         USER
                           │
                           ▼
                  React + Vite + TS
                           │
                         HTTPS
                           │
                           ▼
                  ┌─────────────────┐
                  │    FastAPI      │
                  │ Modular Monolith│
                  └────────┬────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
      PostgreSQL         Storage           Auth
      Supabase           Supabase          Supabase
                           │
                           ▼
                    Background Worker
                       │         │
                       ▼         ▼
                   PaddleOCR   Gemini
```

Final authority chain:

```text
PaddleOCR
  ↓ perception
OCR
  ↓
Gemini
  ↓ semantic extraction
Declarations
  ↓
FastAPI
  ├── schema validation
  ├── applicability
  ├── deterministic rules
  ├── lifecycle
  ├── authorization
  └── audit
  ↓
Inspector verification
  ↓
Reviewer decision
  ↓
Immutable finalization
```

Final invariant:

> **AI finds → Evidence proves → Officer decides.**

The architecture is frozen for implementation **unless the human explicitly approves a change after review**.

---

# 28. Pre-Implementation Legal / Architecture Notes

Known items requiring careful implementation:

1. Consumer Care legal citation/numbering should follow the approved legal specification.
2. Country of Origin is applicability-driven, not a seventh universal check.
3. Processing failure and compliance result remain distinct.
4. Draft evidence deletion and accepted-primary immutability remain distinct.
5. SHA-256 is not legal authenticity proof.
6. Engineering thresholds are engineering parameters, not legal thresholds.
7. Applicability must follow the approved legal specification rather than a simplistic shortcut.
8. Legal source PDFs are not automatically runtime rules.
9. Effective dates are first-class.
10. 2025–2026 amendments and future effective dates must not be blindly treated as current universal rules.
11. Historical evaluations require rule/version context.
12. Avoid assuming “official certificate” terminology; use approved inspection/report terminology.
13. USP is outside MVP.
14. Unit Sale Price is outside MVP.
15. Category-specific expansion is outside MVP unless separately approved.

---

# 29. Explicit Scope Boundary

Not authorized by this package:

- Kubernetes
- microservice architecture
- dedicated search cluster
- Kafka/event streaming
- dynamic legal-rule ingestion
- autonomous legal decision-making
- unrestricted rule CRUD
- Rule Manager operational role
- USP compliance
- universal category-specific compliance
- automatic statutory enforcement
- arbitrary historical re-evaluation
- enterprise-scale analytics infrastructure

Any such addition requires explicit human approval.

---

# 30. Antigravity Review Request — REVIEW ONLY

Antigravity must review the complete package and provide:

## A. Architecture critique

Identify:

- contradictions
- hidden coupling
- over-engineering
- under-engineering
- scalability concerns
- security concerns
- data-integrity risks
- reliability gaps
- deployment risks

## B. Optimization opportunities

For every proposed improvement:

1. Current decision
2. Proposed change
3. Why it is better
4. Problem solved
5. Trade-offs
6. Decision(s) affected
7. MVP-critical or optional

## C. Implementation feasibility

Assess feasibility with:

- React + TypeScript + Vite + Tailwind
- FastAPI
- PostgreSQL/Supabase
- Supabase Auth
- Supabase Storage
- SQLAlchemy
- Alembic
- PaddleOCR
- Gemini 2.5 Flash
- Docker
- asynchronous worker

## D. Boundary audit

Pay special attention to:

```text
Frontend ↔ FastAPI
FastAPI ↔ Supabase
FastAPI ↔ Worker
Worker ↔ PaddleOCR
Worker ↔ Gemini
Evidence ↔ Derived Evidence
Extraction ↔ Applicability
Applicability ↔ Compliance
Inspector ↔ Reviewer
Finalization ↔ Reporting
Rules ↔ Historical Inspections
```

## E. Preferred implementation approach

Describe how you would implement this architecture **if approved**, but do not implement it.

## F. Missing decisions

Identify a missing decision only if it is genuinely required for safe implementation.

Do not manufacture additional architecture decisions simply to extend planning.

## G. Proposed changes

If architecture should change, provide precise decision deltas. **Do not silently apply them.**

---

# 31. Required Antigravity Response Format

```text
1. EXECUTIVE ASSESSMENT

2. ARCHITECTURE STRENGTHS

3. CONTRADICTIONS / CONFLICTS

4. SECURITY CONCERNS

5. DATA / STATE / INTEGRITY CONCERNS

6. AI / OCR CONCERNS

7. PERFORMANCE / SCALABILITY CONCERNS

8. DEPLOYMENT CONCERNS

9. IMPLEMENTATION COMPLEXITY CONCERNS

10. OPTIMIZATION OPPORTUNITIES

11. PROPOSED CHANGES
    For each:
    - Decision affected
    - Current approach
    - Proposed approach
    - Reason
    - Trade-offs
    - MVP impact

12. IMPLEMENTATION APPROACH
    High-level only; no code.

13. MISSING DECISIONS
    Only if genuinely necessary.

14. FINAL RECOMMENDATION
    - Keep unchanged
    - Revise specific decisions
    - Major architectural revision required
```

---

# 32. Critical Instruction

**Do not interpret “Final Architecture Freeze” as authorization to code.**

At this stage:

```text
APPROVED HUMAN BASELINE
          ↓
     ANTIGRAVITY REVIEW
          ↓
     HUMAN EVALUATION
          ↓
   POSSIBLE ARCHITECTURE
       REVISION
          ↓
 IMPLEMENTATION BASELINE
          ↓
      CODE BEGINS
```

The current purpose is **review, not implementation**.

---

# 33. Decision Count Clarification

The architecture process contains **24 decisions**, not 25.

There is intentionally **no Decision 25**.

The final architecture decision is:

> **Decision 24 — Final Architecture Freeze**

Any implementation-preparation work after this is a **new phase**, not another architecture decision.
