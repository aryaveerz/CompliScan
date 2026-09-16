# Antigravity Architecture Review — ComplianceScan
**Review of:** ComplianceScan Architecture Decision Review Package (Decisions 01–24)  
**Reviewed by:** Antigravity  
**Date:** 2026-09-16  
**Status:** REVIEW ONLY — No code, schema, API contract, or implementation artifact is produced here.

---

## 1. EXECUTIVE ASSESSMENT

The 24 architecture decisions form a coherent, disciplined baseline for a legal-grade inspection-assistance system. The core philosophy — **AI finds → Evidence proves → Officer decides** — is correctly enforced through role separation, state machines, and evidence immutability. The decision to use a modular monolith (FastAPI) over microservices is correct for MVP scale and team size. Supabase as managed infrastructure (not domain authority) is the right framing.

**Overall verdict:** The architecture is sound and implementable. No major architectural revision is required. A focused set of precision gaps and one structural clarification are identified below. These are genuine implementation risks, not theoretical concerns.

The architecture is ready to proceed to the Implementation Baseline phase after human evaluation of the items flagged in Sections 3, 4, 5, and 13.

---

## 2. ARCHITECTURE STRENGTHS

| # | Strength | Why It Matters |
|---|----------|----------------|
| S-01 | **Applicability-first design** (Decision 02/22) | Prevents incorrect compliance conclusions on inapplicable rules. Country of Origin and category-specific rules are correctly gated. |
| S-02 | **6-state result vocabulary** (Decision 04) | Eliminates the most dangerous ambiguity in compliance systems: `INCOMPLETE ≠ FAIL`, `PROCESSING_FAILED ≠ NON_COMPLIANCE`. Forces explicit handling of every outcome. |
| S-03 | **Evidence immutability with new-ID-on-replacement** (Decision 05) | Prevents silent evidence mutation. New evidence always gets a new hash identity. Legally defensible audit trail. |
| S-04 | **AI boundary is strictly perception + extraction** (Decision 06/19) | AI is never the decision-maker. Gemini cannot determine legal compliance or finalize. Backend is authoritative. Correct. |
| S-05 | **Upstream-correction-invalidates-downstream invariant** (Decision 03) | Prevents stale compliance results silently surviving a corrected extraction. This is a critical correctness invariant for a legal system. |
| S-06 | **`AuditEvent` is append-only** (Decision 07) | Chronological, tamper-evident history is a legal requirement. Correct to make this append-only at the domain level. |
| S-07 | **Inspector cannot self-approve** (Decision 03) | Four-eyes principle correctly enforced at the role level. |
| S-08 | **Technical failure never becomes compliance conclusion** (Decision 14/19) | Prevents false negatives. OCR/Gemini failure routes to `PROCESSING_FAILED`, not `POTENTIAL_NON_COMPLIANCE`. |
| S-09 | **Rule versioning with effective-date boundaries** (Decision 22) | Historical inspections retain original rule context. Future amendments cannot silently retroact. Critical for legal defensibility. |
| S-10 | **Modular monolith, no Kubernetes/microservices for MVP** (Decision 12/16/23) | Correct scoping. Distributed complexity would dwarf compliance logic in implementation effort at this stage. |
| S-11 | **SHA-256 scope is clearly bounded** (Decision 03/05/13) | Explicitly not "legal authenticity proof". Prevents implementers from over-relying on it as a legal instrument. |
| S-12 | **Worker is separate deployment unit** (Decision 12) | Correct. PaddleOCR is resource-heavy (GPU/CPU). Isolating it prevents the web API from being blocked by long-running inference. |

---

## 3. CONTRADICTIONS / CONFLICTS

### C-01 — `worker/` as a separate top-level directory vs. shared domain contracts

**Decision 23** defines `CompliScan/worker/` as a top-level directory, separate from `backend/`. However, Decision 23 also states:

> "Worker shares domain contracts/logic where practical."

**Conflict:** If `worker/` is a separate top-level directory but must share domain contracts (state enums, result states, entity schemas, rule models) from `backend/app/`, the dependency direction is ambiguous. There are two ways to resolve this and the decision does not specify which:

- Option A: Worker is a separate Python package that imports from a shared `backend/` library.
- Option B: Worker lives inside `backend/app/worker/` (or `backend/app/analysis/`), making it a module within the monolith that is deployed separately.

**Risk:** Without clarification, implementers may duplicate domain enums/result states in `worker/`, creating two divergent sources of truth for the 6-state result vocabulary and lifecycle states.

**Proposed resolution:** See Section 11, Proposed Change P-01.

---

### C-02 — "Separate asynchronous worker deployment" vs. "No Kubernetes/microservices"

**Decision 12** requires a "Separate asynchronous worker deployment."  
**Decision 12 and 16** both prohibit Kubernetes/service mesh for MVP.

**Conflict:** The deployment diagram (Decision 24) shows `Background Worker` as a separate box from `FastAPI`, but does not specify the inter-process communication (IPC) mechanism between FastAPI and the worker. Without this, "separate deployment" is undefined at implementation time. Options include:

- Celery + Redis broker (most common FastAPI/Python async worker pattern)
- ARQ (async Redis queue, lighter than Celery)
- Direct in-process `asyncio` background tasks (not truly "separate deployment")
- A task table in PostgreSQL (DB-backed queue, no broker dependency)

**Risk:** An implementer might choose in-process `asyncio.BackgroundTasks` (a FastAPI built-in), which is NOT a separate deployment and does NOT survive container restarts. This would violate the intent of "durable analysis job identity" (Decision 14).

**Proposed resolution:** See Section 11, Proposed Change P-02. This is an MVP-critical missing decision (see also Section 13, M-01).

---

### C-03 — "Corrections are audited commands, not silent mutations" vs. no explicit correction command model

**Decision 08** and **Decision 11** state corrections are "audited commands, not silent mutations." The upstream-correction-invalidates-downstream invariant (Decision 03) defines *what* happens. However, no decision defines *how* corrections are represented:

- Are they a separate `PATCH /inspections/:id/declarations/:field` endpoint?
- Are they a POST to a correction resource (`POST /inspections/:id/corrections`)?
- Does the Declaration entity have a version list, or does `AuditEvent` carry the old/new values?

**Risk:** Without a correction command model decision, implementers will either (a) implement a silent `PUT` mutation (violating the invariant), or (b) make inconsistent ad-hoc choices across declaration, applicability, and finding corrections.

**Proposed resolution:** See Section 11, Proposed Change P-03.

---

## 4. SECURITY CONCERNS

### SEC-01 — Supabase Auth JWT validation: who validates what?

**Decision 13** shows:

```
User → Supabase Auth → FastAPI Identity Validation → RBAC
```

Supabase Auth issues JWTs. FastAPI must validate these JWTs (signature, expiry, issuer). The decision does not specify:

- Whether FastAPI validates the JWT using the Supabase JWT secret or the JWKS endpoint.
- Whether role/permission claims are embedded in the JWT or are resolved by FastAPI from its own database on each request.

**Risk:** If roles are stored only in Supabase Auth custom claims, a Supabase configuration change can silently alter FastAPI's RBAC behaviour. If roles are stored only in the FastAPI database, a user whose Supabase session is revoked may still have a valid JWT that FastAPI accepts until expiry.

**Recommendation (no implementation change required):** The implementation team should decide at implementation-baseline time whether roles live in the JWT claim or in the FastAPI database, and what the revocation model is. This does not require a new architecture decision, but it is a pre-implementation clarification item.

---

### SEC-02 — Evidence access: signed URLs vs. proxied streaming

**Decision 13** requires:
- Private evidence storage (Supabase Storage private bucket).
- No public evidence URLs.
- Backend-controlled evidence access.

Supabase Storage private buckets support **signed URLs** (time-limited, bearer token). An alternative is **FastAPI streaming the file bytes directly** (proxied download).

**Concern:** Signed URLs, even time-limited, are effectively bearer tokens. If a signed URL is leaked (logs, browser history, forwarded request), the evidence is temporarily accessible without FastAPI RBAC re-validation. Proxied streaming always enforces RBAC on every request but adds server-side bandwidth cost.

**For MVP:** Signed URLs with a short TTL (e.g., 5–15 minutes) are acceptable and are the standard Supabase pattern. The implementation team should be aware that signed URL generation must itself be RBAC-gated and the URL must never appear in application logs.

This does not require a new architecture decision, but should be noted in implementation guidance.

---

### SEC-03 — Audit hash chaining: tamper-evident vs. cryptographically proven

**Decision 13** states:
> "Audit supports tamper-evident hash chaining."

SHA-256 hash chaining (each event's hash includes the previous event's hash) makes silent database record modification detectable by any party that retained a prior hash. However:

- It does not prevent a database administrator from re-computing the entire chain after modification.
- It is not a cryptographic proof of non-repudiation (no signing key).

**The decision correctly scopes this** ("tamper-evident", not "cryptographically proven"). This is architecturally correct. The implementation team must not over-represent this as legal-grade non-repudiation in any user-facing language.

No change required. This is a documentation/communication note for implementation.

---

## 5. DATA / STATE / INTEGRITY CONCERNS

### D-01 — `InspectionCase` as root aggregate: aggregate boundary not defined

**Decision 07** names `InspectionCase` as the root aggregate. This is correct Domain-Driven Design (DDD) framing. However, the decisions do not define the **aggregate boundary**:

- Can `EvidenceAsset` exist without an `InspectionCase`? (It should not.)
- Can `ComplianceFinding` be loaded independently of `InspectionCase`? (It should not in the domain layer, but the API groups them separately under `/findings`.)
- Who owns `AuditEvent` — the aggregate or the system?

**Risk:** Without a defined aggregate boundary, database foreign-key cascades, soft-delete behaviour, and orphan-record handling will be implemented inconsistently. This is an implementation-level clarification, not an architecture revision.

---

### D-02 — `FinalAuditRecord` entity: snapshot vs. derived

**Decision 07** includes `FinalAuditRecord` as one of the nine entities. **Decision 20** states reports are generated from `FinalAuditRecord`. The decision does not specify whether `FinalAuditRecord` is:

- A **point-in-time snapshot** (a denormalized copy of all relevant data at finalization time), or
- A **derived view** computed from the normalized entities at report-generation time.

**Risk:** If it is a derived view, a future schema migration could change what the report says about a finalized inspection (violating historical stability). If it is a snapshot, the implementation team must define exactly what data is captured.

**Recommendation:** `FinalAuditRecord` should be a **point-in-time snapshot** stored at finalization. This is consistent with the "finalized records are immutable" invariant. See Section 11, Proposed Change P-04.

---

### D-03 — Re-evaluation after correction: which entities get invalidated?

**Decision 03** states:
> Upstream correction → invalidate affected downstream state → recompute → preserve prior state/history → audit transition.

The decisions do not specify the **invalidation graph**:

- If an `ExtractedDeclaration` is corrected, does `ApplicabilityContext` get invalidated and recomputed?
- If `ApplicabilityContext` changes (e.g., product is re-classified as imported), do all `ComplianceFinding`s get invalidated?
- Does invalidation require a new analysis job, or can it be synchronous?

**Risk:** Without a defined invalidation graph, different developers will implement inconsistent re-computation chains. Some correction paths may leave stale findings.

This is an implementation-baseline clarification item that should be resolved before Phase 1 begins.

---

### D-04 — `DerivedOcrToken` persistence after re-processing

**Decision 07** states "OCR tokens remain persistent and traceable." **Decision 19** allows reprocessing following the upstream-invalidation invariant. If an image is reprocessed (e.g., PaddleOCR is re-run):

- Are old `DerivedOcrToken` records preserved (immutable, versioned) or replaced?
- If preserved, how does the system distinguish current vs. superseded OCR tokens?

**Recommendation:** Old OCR tokens should be preserved and linked to their source evidence and analysis job. A new analysis job generates new tokens. The current/active token set is determined by the current analysis job ID on the `InspectionCase`.

---

## 6. AI / OCR CONCERNS

### AI-01 — Gemini output schema validation: strict vs. partial rejection

**Decision 19** states:
> "Gemini output must conform to validated schema. Invalid output is rejected/reviewed."

"Rejected/reviewed" has two different meanings in this context:

- **Rejected entirely** → entire extraction fails → `PROCESSING_FAILED` or `INCOMPLETE` for all fields.
- **Rejected partially** → invalid fields become `NOT_OBSERVED` or `REQUIRES_REVIEW`, valid fields are accepted.

For an inspection with 6 compliance domains, a Gemini hallucination in one field should not invalidate the entire extraction. Partial acceptance with field-level validation is the more resilient design.

**Recommendation:** Define a field-level schema validation strategy: valid fields are accepted, invalid/unexpected fields are flagged as `REQUIRES_REVIEW` rather than causing full extraction failure. See Section 11, Proposed Change P-05.

---

### AI-02 — PaddleOCR version and model pinning

**Decision 11** specifies PaddleOCR but not a specific model version or language pack. PaddleOCR has significantly different accuracy profiles between versions (PP-OCR v3 vs. v4, multilingual vs. English-only models).

**Risk:** Unpinned OCR model versions can cause non-deterministic test failures. The decision's requirement for "legal-rule fixtures" and "regression tests" (Decision 15) requires deterministic OCR output for testing.

**Recommendation:** Pin the PaddleOCR model version and language pack in implementation. Use a fixed model checkpoint for testing. This is an implementation detail, not an architecture decision, but it must be decided before CI is set up.

---

### AI-03 — Gemini 2.5 Flash: prompt versioning and schema contract

**Decision 19** states: "Prompts are version-controlled artifacts."  
**Decision 11** specifies Gemini 2.5 Flash.

Gemini API model versions (e.g., `gemini-2.5-flash-preview-*`, `gemini-2.5-flash-stable`) have different capability and output-format profiles. The structured output (JSON mode / response schema) feature in Gemini 2.5 Flash is the correct mechanism for enforcing the output schema contract. This should be the mandated integration approach.

**Recommendation:** The implementation should use Gemini's native `response_schema` parameter (not post-hoc regex parsing of free-text output) as the schema enforcement mechanism. Record the exact model version string alongside prompt version in each analysis job record.

---

### AI-04 — Image quality assessment: threshold ownership

**Decision 02** includes "Image Quality" as the first step in ANALYZE. **Decision 19**'s pipeline starts with Image Quality before PaddleOCR. The decisions do not specify:

- Who sets the image quality rejection threshold (blurriness score, resolution minimum)?
- Is a low-quality image a `PROCESSING_FAILED` or an `INCOMPLETE` result?
- Can an Inspector override the quality gate and proceed anyway?

**Risk:** If thresholds are hardcoded, they are not adjustable for different field conditions (bright sunlight, low-light warehouse). If they are environment variables, they are engineering configuration (Decision 18 permits this), but this should be explicit.

**Recommendation:** Image quality thresholds are engineering configuration (Decision 18 category: Application/Engineering Configuration). A low-quality image produces `INCOMPLETE` with a reason, not `PROCESSING_FAILED`. Inspector can add supplemental evidence and re-trigger analysis. This does not require a new architecture decision.

---

## 7. PERFORMANCE / SCALABILITY CONCERNS

### P-PERF-01 — Worker queue depth and backpressure

**Decision 16** states:
> "Excess jobs are queued rather than silently dropped."

This is correct. However, without a queue depth limit or backpressure signal, an unbounded queue can grow indefinitely during an incident (e.g., Gemini API outage), causing:

- Database/broker storage exhaustion.
- Jobs timing out silently at the head of the queue after the issue resolves.

**Recommendation:** The worker queue should have a configurable max-depth. When the queue is full, new analysis requests should receive a `503 Service Unavailable` with a `Retry-After` header rather than being silently queued. This is an implementation detail consistent with Decision 16's bounded-retry requirement.

---

### P-PERF-02 — PostgreSQL full-text search: index strategy

**Decision 21** uses PostgreSQL for MVP search. The searchable fields include product name, inspector name, and commodity type — all potentially variable-length text.

**Risk:** Without `GIN` indexes on `tsvector` columns (or at minimum, `ILIKE` with `pg_trgm` GIN indexes), search queries on large inspection tables will perform full sequential scans.

**Recommendation:** Add PostgreSQL `GIN` index with `pg_trgm` extension for text search fields, and `BTREE` indexes on status, date, and foreign-key filter fields. This is an Alembic migration concern, not an architecture change.

---

### P-PERF-03 — PDF report generation: synchronous or asynchronous?

**Decision 20** generates reports from `FinalAuditRecord`. For inspections with many evidence images and findings, PDF generation (with embedded image thumbnails) can be time-consuming.

**Risk:** If PDF generation is synchronous in the `/reports` API endpoint, it will block the web worker for seconds per request, causing timeouts under concurrent load.

**Recommendation:** PDF report generation should be asynchronous (similar to analysis jobs): `POST /reports/:id/generate` → `202 Accepted` → status polling or webhook notification. If the report has already been generated and cached, `GET /reports/:id` returns it directly.

---

## 8. DEPLOYMENT CONCERNS

### DEP-01 — Docker Compose for local development: worker isolation

**Decision 12** requires Docker Compose for local development. The compose file must include at least:

- `frontend` (React Vite dev server or Nginx)
- `backend` (FastAPI with Uvicorn)
- `worker` (async worker process)
- `broker` (Redis or equivalent, if Celery/ARQ is used)
- Supabase local stack OR environment variables pointing to a cloud Supabase project

**Risk:** PaddleOCR has a significant first-run model download (~1GB). If this is not handled in the Docker image build (not at runtime), the worker container will have a slow and potentially failing cold start in CI environments without network access.

**Recommendation:** PaddleOCR models must be baked into the worker Docker image at build time, not downloaded at runtime. This is a Dockerfile implementation detail, but it must be decided before CI is configured.

---

### DEP-02 — Alembic migrations in CI/CD: migration safety gate

**Decision 12** requires "Automated CI/CD" and "Alembic migrations." The decisions do not specify when migrations run in the deployment pipeline.

**Risk:** If migrations run automatically on every deployment without a dry-run check, a destructive migration (column drop, rename) can reach production before it is caught.

**Recommendation:** CI/CD pipeline should include an Alembic `--sql` dry-run step that outputs the migration SQL for human review before any destructive migration is applied to production. Non-destructive migrations (add column, add index) can be auto-applied.

---

### DEP-03 — Supabase local development stack

Supabase provides `supabase start` (Docker-based local stack) that emulates PostgreSQL + Storage + Auth locally. This is the correct approach for local development, avoiding any dependency on a shared cloud Supabase project for development.

**Risk:** Not all Supabase Storage features (especially signed URL generation) behave identically in the local stack vs. cloud. This can cause test environment discrepancies.

**Recommendation:** Document the Supabase local stack setup in `README.md` and include it in Docker Compose. Integration tests that involve storage should explicitly target the local Supabase stack, not a shared staging bucket.

---

## 9. IMPLEMENTATION COMPLEXITY CONCERNS

### IC-01 — Upstream-correction-invalidates-downstream: implementation complexity

The upstream-correction invariant (Decision 03) is the most complex piece of domain logic in this system. Implementing it correctly requires:

1. A dependency graph of which entities depend on which upstream entities.
2. A mechanism to mark downstream entities as `STALE`/`INVALIDATED`.
3. A re-computation trigger (synchronous or queued, depending on scope).
4. Preservation of the prior state before invalidation (for audit).
5. An atomic transaction that records the correction event, old state, and new state.

This is non-trivial. If implemented incorrectly, it produces one of two failure modes:
- **Silent stale results**: Downstream compliance findings reflect old declarations.
- **Unnecessary cascade**: Entire inspection is re-processed when only one field was corrected.

**Recommendation:** Implement a simple, explicit dependency map as a data structure in the domain layer (not implicit ORM cascade). Each correction operation explicitly identifies which downstream entities are affected. Start with a conservative "invalidate everything downstream" approach for MVP, optimise later if performance requires it.

---

### IC-02 — `AuditEvent` append-only enforcement: application-level vs. database-level

**Decision 07** requires `AuditEvent` to be append-only. This should be enforced at two levels:

1. **Application level:** No `DELETE` or `UPDATE` method in the repository layer.
2. **Database level:** A PostgreSQL rule or trigger that prevents `UPDATE`/`DELETE` on the audit table, or use of row-level security (RLS) to deny mutations.

**Risk:** Application-level enforcement alone can be bypassed by a database administrator or a future developer who adds a "cleanup" migration. Database-level enforcement is stronger.

**Recommendation:** Add a PostgreSQL trigger `BEFORE UPDATE OR DELETE ON audit_events RAISE EXCEPTION` as a defence-in-depth measure. This is an Alembic migration item.

---

### IC-03 — Reviewer "silent edit" prevention: UI + API enforcement

**Decision 03** states:
> "Reviewer should not silently edit underlying extracted declarations. If underlying information is wrong, use revision/request or an explicitly recorded determination."

This requires both:
- API-level: The Reviewer's `PATCH` permissions on declaration fields must be restricted (or absent). Reviewers act through decision/determination endpoints, not declaration mutation endpoints.
- UI-level: The Reviewer workspace must not present editable declaration fields.

**Risk:** If the API does not enforce this distinction and relies only on UI, a raw API call from a Reviewer could silently mutate a declaration.

**Recommendation:** The RBAC layer must explicitly distinguish "correct declaration" (Inspector action, creates audit event) from "reviewer determination" (Reviewer action, creates a separate determination record). These must be separate API operations.

---

## 10. OPTIMIZATION OPPORTUNITIES

### O-01 — Background task status: polling vs. WebSocket/SSE

**Current:** Decision 08 allows `202 Accepted` for analysis. Status is presumably polled by the frontend.

**Proposed change:** Add Server-Sent Events (SSE) as an optional real-time status channel for analysis job progress. FastAPI has native SSE support via `StreamingResponse`. This is an additive feature, not an architecture change.

**Why better:** Polling introduces latency and unnecessary HTTP round-trips. SSE provides real-time feedback (image quality result → OCR progress → extraction complete → compliance evaluated) without WebSocket complexity.

**Trade-offs:** SSE requires the FastAPI server to hold open connections. For MVP scale (low concurrent inspections), this is acceptable. Should not be used if the worker is a separate process without a shared message bus.

**MVP impact:** Optional enhancement. Polling is sufficient for MVP if SSE adds implementation complexity.

---

### O-02 — Structured logging with correlation IDs from request to worker

**Current:** Decision 14 requires request IDs and structured logs.

**Proposed addition:** The `analysis_job_id` should be propagated from the FastAPI request context to the worker job, and both should emit structured logs with the same `inspection_id`, `job_id`, and `request_id`. This enables end-to-end tracing of a single inspection's analysis across two deployment units.

**MVP impact:** Low implementation cost, high operational value. Should be included in the initial implementation.

---

### O-03 — Evidence thumbnail generation at acceptance time

**Current:** Reports and UI presumably load original primary evidence images directly.

**Proposed addition:** Generate fixed-resolution thumbnails of accepted primary evidence at acceptance time (not at display time). Store thumbnails as derived assets in Supabase Storage.

**Why better:** Original evidence images from phone cameras can be 8–20MB. Loading them for dashboard/list views or PDF generation is slow and wasteful.

**Trade-offs:** Adds a thumbnail generation step to evidence acceptance. Thumbnail quality/format is an engineering parameter.

**MVP impact:** Optional but strongly recommended for usability. Can be a background task triggered by evidence acceptance.

---

## 11. PROPOSED CHANGES

### P-01 — Worker/Domain Contract Boundary

**Decision affected:** Decision 23  
**Current approach:** `worker/` is a top-level directory. Domain contracts are shared "where practical" (undefined).  
**Proposed approach:** The worker is a separate top-level directory (`CompliScan/worker/`) that imports from a shared internal package. Create `CompliScan/shared/` (or `CompliScan/backend/app/shared/`) containing:
- Result state enums (`PASS`, `POTENTIAL_NON_COMPLIANCE`, etc.)
- Lifecycle state enums
- Job result schemas (Pydantic models)
- No FastAPI, no HTTP, no database dependencies

The worker imports only from `shared/`. FastAPI imports from `shared/` and its own domain modules.

**Reason:** Prevents result-state enum duplication between two Python packages.  
**Trade-offs:** Adds a shared package; adds a dependency management concern.  
**MVP impact:** MVP-critical. Without this, result state drift between worker and API is a near-certainty.

---

### P-02 — Worker Queue Technology Decision

**Decision affected:** Decision 12 (Deployment Architecture)  
**Current approach:** "Separate asynchronous worker deployment" is specified. IPC mechanism is unspecified.  
**Proposed approach:** Use **ARQ** (Async Redis Queue) as the task broker between FastAPI and the worker for MVP. Rationale:
- Pure Python asyncio, no Celery complexity.
- Redis is a single additional infrastructure dependency (Docker Compose service).
- Supports durable job identity, retry configuration, and job status inspection — matching Decision 14's requirements.
- Simpler than Celery for a single-worker-type system.
- Redis can be replaced by a PostgreSQL-backed queue (e.g., `pg-boss` pattern) if Redis adds operational overhead.

Alternative (if Redis is undesirable): Use a PostgreSQL-backed job table (`analysis_jobs`) polled by the worker. No broker dependency. Less real-time but zero new infrastructure.

**Reason:** "Durable analysis job identity" and "separate deployment" require a real queue, not in-process `asyncio.BackgroundTasks`.  
**Trade-offs:** Adds Redis (or PostgreSQL job table) as a dependency.  
**MVP impact:** MVP-critical. Must be decided before implementation begins.

---

### P-03 — Correction Command Model

**Decision affected:** Decision 08 (API Architecture), Decision 03 (Global Invariants)  
**Current approach:** "Corrections are audited commands, not silent mutations." No correction command model is defined.  
**Proposed approach:** Define a correction as a POST to a correction sub-resource:

```
POST /inspections/:id/declarations/:field/corrections
Body: { new_value, reason, evidence_context }
Response: 201 Created { correction_id, audit_event_id, downstream_invalidation_status }
```

This endpoint:
1. Records old value, new value, actor, timestamp, and reason in `AuditEvent`.
2. Marks affected downstream entities as `INVALIDATED`.
3. Triggers re-computation (synchronous or queued, depending on scope).
4. Returns the correction ID and invalidation status.

**Reason:** Without a defined correction command model, implementers will use silent `PATCH` mutations.  
**Trade-offs:** More complex than a simple `PATCH`. Requires explicit domain event handling.  
**MVP impact:** MVP-critical. Must be designed before the declaration/compliance modules are implemented.

---

### P-04 — `FinalAuditRecord` as Point-in-Time Snapshot

**Decision affected:** Decision 07 (Data Model), Decision 20 (Reporting)  
**Current approach:** `FinalAuditRecord` is listed as an entity. Its nature (snapshot vs. derived view) is unspecified.  
**Proposed approach:** `FinalAuditRecord` is a **serialized JSON snapshot** stored at finalization time, containing:
- Finalized inspection metadata
- Product/package context
- All `ExtractedDeclaration` values (at finalization)
- All `ComplianceFinding` results
- Applicability context and rule version references
- Inspector verification record
- Reviewer decision and rationale
- Finalization actor and timestamp

This JSON blob is stored in the database alongside the normalized relational data. Reports are generated from this blob, not from re-querying normalized tables.

**Reason:** Prevents future schema migrations from silently changing what historical reports say.  
**Trade-offs:** Denormalized storage. JSON blob can grow large for inspections with many findings.  
**MVP impact:** MVP-critical for legal defensibility of historical reports.

---

### P-05 — Field-Level Schema Validation for Gemini Output

**Decision affected:** Decision 19 (AI/OCR Operational Policy)  
**Current approach:** "Invalid output is rejected/reviewed." Scope of rejection (full or partial) is unspecified.  
**Proposed approach:** Field-level validation:
- Each field in the Gemini extraction schema is independently validated.
- Valid fields are accepted as extracted declarations.
- Fields with invalid format/type are set to `status: REQUIRES_REVIEW` with a reason.
- Fields not returned by Gemini (missing) are set to `status: NOT_OBSERVED`.
- Only a complete schema failure (unparseable JSON, wrong top-level structure) triggers `PROCESSING_FAILED`.

**Reason:** A single hallucinated field should not invalidate a full extraction with 5 valid fields.  
**Trade-offs:** More complex validation logic. Requires field-level status tracking in `ExtractedDeclaration`.  
**MVP impact:** MVP-critical for resilience. A single bad Gemini field should not block all compliance evaluation.

---

## 12. IMPLEMENTATION APPROACH

*High-level only. No code.*

### Phase sequence recommendation

**Phase 1A — Foundation (implement first):**
1. Shared domain package: result states, lifecycle states, job schemas.
2. Database schema: all 9 entities, Alembic migration baseline.
3. Supabase Auth integration: JWT validation in FastAPI, RBAC middleware.
4. Evidence acceptance pipeline: upload → hash → store → immutable record.
5. `AuditEvent` append-only infrastructure.
6. Basic inspection lifecycle state machine.

**Phase 1B — Analysis pipeline:**
1. Analysis job queue (ARQ + Redis or PostgreSQL job table).
2. Worker: PaddleOCR perception layer.
3. Worker: Gemini extraction layer with schema validation (field-level).
4. Worker: Declaration persistence with traceability.
5. Applicability resolver.
6. Deterministic compliance rule engine (6 domains).

**Phase 1C — Human workflow:**
1. Inspector verification endpoints.
2. Correction command endpoints with downstream invalidation.
3. Reviewer workspace endpoints.
4. Finalization (atomic, idempotent, snapshot creation).

**Phase 1D — Output layer:**
1. `FinalAuditRecord` snapshot at finalization.
2. PDF report generation (async).
3. Search, filtering, pagination.
4. Dashboard metrics endpoints.

**Phase 1E — Frontend:**
1. Inspector flow: Dashboard → Create → Upload → Analysis status → Verify → Submit.
2. Reviewer flow: Queue → Workspace → Decision → Finalize.
3. Report view and PDF download.
4. History/audit view.

### Technology-specific notes

- **FastAPI:** Use dependency injection (`Depends`) for auth, RBAC, and database sessions. Route handlers are thin; domain logic lives in service classes.
- **SQLAlchemy:** Use 2.0-style async ORM with `AsyncSession`. No raw SQL except for search indexes and the correction command's atomic transaction.
- **Alembic:** All schema changes through migrations. Never `CREATE TABLE` in application startup.
- **PaddleOCR:** Wrap in an adapter class. Pin model version. Load model once at worker startup, not per-request.
- **Gemini:** Use `google-generativeai` SDK with `response_schema` for structured output. Record model version string per analysis job.
- **Supabase Storage:** Use private bucket. Generate signed URLs server-side. Never expose storage credentials to frontend.
- **React + Vite:** TanStack Query for server state. React Router for navigation. Tailwind for styling. Keep frontend stateless with respect to inspection domain; all domain state lives in the backend.

---

## 13. MISSING DECISIONS

Only genuinely required items are listed here.

### M-01 — Worker Queue Technology (MVP-Critical)

**Why required:** "Separate asynchronous worker deployment" and "durable analysis job identity" (Decisions 12 and 14) cannot be implemented without specifying the IPC mechanism. This is not an implementation detail — it determines the infrastructure dependency graph (does Redis exist in the stack?) and the local Docker Compose configuration.

**Question for human decision:** Should the worker use ARQ + Redis, or a PostgreSQL-backed job table (no broker)?

**Recommendation:** ARQ + Redis for simplicity and mature retry semantics. PostgreSQL job table if minimizing infrastructure dependencies is a priority.

---

### M-02 — Correction Command Scope for Reviewer (MVP-Critical)

**Why required:** Decision 03 prohibits Reviewers from silently editing declarations. Decision 03 also allows Reviewers to "correct/override assessments with reason." The exact boundary between an Inspector correction (on extracted data) and a Reviewer determination (on compliance assessment) must be defined before the RBAC layer is implemented.

**Question for human decision:** Can a Reviewer create a `CorrectDeclaration` command on extracted declaration values, or only on compliance findings? Or neither — only a `RequiresRevision` request back to the Inspector?

**Recommendation:** Reviewer creates `ReviewerDetermination` records (separate entity) that override compliance findings. Reviewers cannot directly correct extracted declarations; they send back to Inspector via `REQUIRES_REVISION` lifecycle state.

---

## 14. FINAL RECOMMENDATION

### Verdict: **Revise specific decisions — targeted changes only**

The architecture does not require a major revision. The 24 decisions are coherent, legally grounded, and implementable with the specified technology stack.

**Required before Implementation Baseline is declared:**

| # | Item | Type | Section |
|---|------|------|---------|
| M-01 | Worker queue technology must be specified | Missing Decision | §13 |
| M-02 | Reviewer vs. Inspector correction boundary must be specified | Missing Decision | §13 |
| P-01 | Shared domain package boundary (worker ↔ backend) | Proposed Change | §11 |
| P-02 | Worker queue IPC mechanism | Proposed Change | §11 |
| P-03 | Correction command model for declarations | Proposed Change | §11 |
| P-04 | `FinalAuditRecord` as point-in-time snapshot | Proposed Change | §11 |
| P-05 | Field-Level Gemini schema validation | Proposed Change | §11 |

**Can proceed to Implementation Baseline after:**
- Human evaluation of the five proposed changes (P-01 to P-05).
- Human decisions on the two missing decisions (M-01, M-02).

**The following require no architecture change — they are implementation-level clarifications:**
- Supabase JWT role claim vs. FastAPI database role storage (SEC-01).
- Signed URL TTL and logging policy (SEC-02).
- Image quality threshold ownership (AI-04).
- PaddleOCR model version pinning (AI-02).
- Gemini model version string recording (AI-03).
- PostgreSQL GIN index strategy (P-PERF-02).
- Alembic migration dry-run gate in CI (DEP-02).
- Supabase local stack Docker Compose setup (DEP-03).
- `AuditEvent` database-level trigger (IC-02).
- Reviewer workspace API permission enforcement (IC-03).

**The core architecture — modular FastAPI monolith, 6-state result vocabulary, applicability-first, evidence immutability, human-in-the-loop finalization, and the authority chain — is correct and should remain unchanged.**

---

*This review is complete. No code, schema, API contracts, migrations, or implementation files have been created. All proposed changes require explicit human approval before being treated as architecture.*
