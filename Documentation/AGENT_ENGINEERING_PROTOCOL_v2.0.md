# AGENT ENGINEERING PROTOCOL

**ComplianceScan — SIH'26 Problem Statement 26034**

**Protocol Version:** 2.0
**Purpose:** Control AI/vibe-coded implementation so that the current MVP is built safely, honestly, and without uncontrolled scope expansion.

---

# 1. Purpose

This document defines how an implementation agent must behave while building ComplianceScan.

ComplianceScan has a deliberately ambitious target architecture, but the current implementation is a **one-day MVP vertical slice**.

The central engineering problem is therefore not simply:

> "Build as many documented features as possible."

It is:

> **Build the smallest reliable implementation that demonstrates one complete, deployable, evidence-backed inspection journey without corrupting the target architecture or expanding scope.**

This protocol exists to prevent:

- blind coding
- hallucinated implementation claims
- uncontrolled feature creep
- unnecessary architecture redesign
- premature abstraction
- accidental legal overclaiming
- unsafe AI behavior
- stale downstream state
- loss of evidence provenance
- local-only architecture that cannot be deployed
- endless documentation loops
- building the full target system instead of the current MVP

---

# 2. Authority Hierarchy

When deciding what to implement, use the project documents according to this hierarchy.

```text
1. Explicit Human Decision / Approval
                 ↓
2. MVP_BUILD_SCOPE.md
                 ↓
3. PROJECT_STATE.md
                 ↓
4. PHASE.md
                 ↓
5. AGENT_ENGINEERING_PROTOCOL.md
                 ↓
6. Specialized Numbered Specification
                 ↓
7. Other Project Documentation
                 ↓
8. Agent Inference
```

The hierarchy does **not** mean that lower documents are unimportant.

It means that:

- `MVP_BUILD_SCOPE.md` defines the current implementation boundary.
- `PROJECT_STATE.md` defines what actually exists.
- `PHASE.md` defines execution order.
- This protocol defines engineering behavior.
- Numbered specifications describe the broader target system and provide authoritative domain details for their respective areas.

If two documents appear to conflict:

1. Do not silently choose one.
2. Identify the conflict.
3. Determine whether it affects the current MVP.
4. Follow the higher-authority source.
5. Ask for human approval when the conflict requires a material project decision.

---

# 3. Target System vs Current MVP

The project deliberately maintains two layers.

```text
TARGET SYSTEM
│
├── Full architecture
├── Full lifecycle
├── Reviewer workflow
├── Evidence integrity
├── Repository/history
├── Search/dashboard
├── Physical ↔ Online verification
├── Broader rules
└── Future capabilities
        │
        │ controlled subset
        ▼
CURRENT ONE-DAY MVP
│
├── One complete inspection journey
├── Image evidence
├── Image processing
├── PaddleOCR
├── Gemini 2.5 Flash
├── Structured declarations
├── Applicability
├── Six compliance checks
├── Findings + evidence
├── Inspector verification
├── Result
├── Basic output
└── Deployment/demo readiness
```

The agent must **not** interpret the size of the target documentation as permission to implement all target features.

The target architecture is preserved as the destination.

The MVP is the current road.

---

# 4. Non-Negotiable Core Principle

> **ONE COMPLETE USER JOURNEY > MANY PARTIAL SUBSYSTEMS**

A smaller system that can be demonstrated end-to-end is preferable to a larger system containing disconnected or unreliable components.

The primary question before implementing any feature is:

> **Does this materially contribute to the current vertical slice?**

If not, defer it.

---

# 5. First Action: Phase 0 Audit

The agent must not begin unrestricted feature coding immediately.

The first implementation phase is **Phase 0: Repository / Implementation Audit**.

The agent must:

1. Read the control documents.
2. Read the current MVP scope.
3. Read the current project state.
4. Read the phase plan.
5. Inspect the actual repository.
6. Inspect existing source code.
7. Inspect configuration.
8. Inspect dependency files.
9. Inspect database/storage setup.
10. Inspect current routes/components/modules.
11. Run safe existing tests or checks where possible.
12. Identify what actually works.
13. Identify what is broken.
14. Identify what is missing.
15. Identify reusable implementation.
16. Identify the shortest path to the vertical slice.
17. Produce a concise implementation audit.
18. Stop at the defined human checkpoint.

The agent must not claim a component is implemented merely because:

- a file exists
- documentation mentions it
- an endpoint is declared in a specification
- a UI placeholder exists
- a dependency is installed

Implementation status must be established from the repository and, where appropriate, execution.

---

# 6. Anti-Hallucination Contract

The agent must distinguish between:

```text
DOCUMENTED
IMPLEMENTED
EXECUTED
TESTED
VERIFIED
DEPLOYED
```

These are different states.

For example:

```text
"API documented"
        ≠
"API implemented"

"Component exists"
        ≠
"Component works"

"Code compiles"
        ≠
"Workflow works"

"Local test passes"
        ≠
"Production deployment works"

"AI returned JSON"
        ≠
"AI result is legally correct"
```

Never report a stronger state than the evidence supports.

If uncertain, say:

> "Not verified."

---

# 7. Current MVP Critical Path

The current one-day MVP critical path is:

```text
PHASE 1
Minimal Foundation
       ↓
PHASE 2
Inspection + Image Input
       ↓
PHASE 3
Image Processing + PaddleOCR
       ↓
PHASE 4
Gemini Declaration Extraction
       ↓
PHASE 5
Applicability + Six Rules
       ↓
PHASE 6
Findings + Evidence
       ↓
PHASE 7
Inspector Verification + Result
       ↓
PHASE 8
End-to-End QA + Basic Export
       ↓
PHASE 9
Deployment + Demonstration Readiness
```

Do not jump ahead merely because a later subsystem is interesting.

---

# 8. Phase Discipline

At any point, the agent should know:

```text
CURRENT PHASE
     ↓
CURRENT OBJECTIVE
     ↓
CURRENT ACCEPTANCE CRITERIA
     ↓
IMPLEMENT
     ↓
TEST
     ↓
REPORT
     ↓
NEXT PHASE
```

The agent must not silently combine unrelated phases if doing so increases risk or obscures progress.

Small implementation dependencies are allowed when necessary.

Unrelated feature work is not.

---

# 9. Human Checkpoints

Human approval is required when a change materially affects the project contract.

Examples:

- changing the MVP scope
- adding a new major feature
- removing a required MVP capability
- changing the compliance interpretation
- changing the lifecycle/state model
- changing evidence integrity semantics
- changing role permissions
- changing the architecture boundary
- changing deployment assumptions
- introducing a new AI provider/model with meaningful architectural impact
- changing the persistence model
- changing a documented API contract in a breaking way

The agent should provide:

```text
PROBLEM
WHY IT MATTERS
PROPOSED CHANGE
WHY THIS IS THE SMALLEST SAFE CHANGE
IMPACT
```

Then wait for approval when required.

---

# 10. Scope Control

The agent must actively resist feature creep.

Do not implement a feature merely because:

- it appears in the target architecture
- it appears in a numbered specification
- it would make the product "cooler"
- another AI suggested it
- it seems easy
- it might be useful someday
- the agent has already started designing it
- a dependency happens to support it

A feature belongs in the current build only if it is:

1. required by the current MVP scope,
2. required to make the vertical slice work,
3. required for safety/integrity/security of the vertical slice,
4. or explicitly approved by the human.

Otherwise:

> **DEFER.**

---

# 11. No Architecture Redesign During MVP

The target architecture is already defined.

The agent must not create a second "simplified architecture" merely because the MVP is small.

Instead:

```text
TARGET ARCHITECTURE
       │
       └── implement only required logical subset
```

Logical components do not automatically require separate services.

Do not introduce microservices, queues, orchestration layers, event buses, complex plugin systems, or other infrastructure unless the current implementation genuinely requires them.

Prefer the simplest implementation that respects the target boundaries.

---

# 12. No Premature Abstraction

Avoid speculative abstractions such as:

- generic plugin frameworks
- universal rule engines for rules not in MVP
- unnecessary provider-agnostic infrastructure
- complex event systems
- excessive repository/service layers
- elaborate configuration frameworks
- abstractions for hypothetical future features

Abstraction is justified when it:

- removes actual duplication
- protects an important boundary
- makes the current implementation safer
- is required for deployment
- is required to preserve a documented contract

Do not abstract merely for theoretical extensibility.

---

# 13. Current Compliance Scope

The current MVP evaluates six core declaration checks:

1. Manufacturer / Packer / Importer
2. Common / Generic Product Name
3. Net Quantity + Standard Unit
4. Month / Year of Manufacture / Packing / Import
5. MRP inclusive of all taxes
6. Consumer Care Details

Country of Origin is applicability-driven:

```text
Imported = YES
    → Applicable

Imported = NO
    → NOT_APPLICABLE

Imported = UNKNOWN
    → REVIEW / BLOCK AS APPROPRIATE
```

The agent must not silently add:

- Unit Sale Price
- broad category-specific rules
- universal exemptions
- unapproved regulatory interpretations

The controlled rule set must remain bounded to the current MVP.

---

# 14. Legal Safety

The system is an inspection-assistance tool.

The agent must use careful terminology.

Preferred:

- "Potential Non-Compliance"
- "System Assessment"
- "Requires Review"
- "Observed"
- "Not Observed"
- "Uncertain"
- "Unreadable"
- "Insufficient Evidence"
- "Cross-Channel Inconsistency"

Avoid claims such as:

- "AI has determined a legal violation"
- "AI automatically enforces the law"
- "The product is legally illegal"
- "The model guarantees compliance"

The core principle is:

> **AI finds → Evidence proves → Officer decides.**

---

# 15. Result-State Integrity

Use the controlled result vocabulary:

```text
PASS
POTENTIAL_NON_COMPLIANCE
REQUIRES_REVIEW
NOT_APPLICABLE
INCOMPLETE
PROCESSING_FAILED
```

Never collapse distinct states.

Specifically:

```text
NOT_APPLICABLE ≠ PASS
INCOMPLETE ≠ POTENTIAL_NON_COMPLIANCE
PROCESSING_FAILED ≠ NON_COMPLIANCE
NOT_OBSERVED ≠ MISSING
UNREADABLE ≠ MISSING
CONFLICTING → REQUIRES_REVIEW
```

Technical failure must never become a legal failure.

---

# 16. OCR Boundary

The selected MVP OCR engine is:

> **PaddleOCR**

OCR is responsible for:

- text detection
- text recognition
- bounding boxes
- OCR confidence
- source-image association

OCR does not determine legal compliance.

The agent must preserve OCR provenance so that structured declarations can be traced back to image regions.

---

# 17. AI Boundary

The selected MVP AI model is:

> **Gemini 2.5 Flash**

Gemini is primarily responsible for:

- declaration extraction
- semantic interpretation
- normalization
- context mapping
- conflict detection
- preserving uncertainty

It must not:

- invent declarations
- silently resolve conflicts
- make final legal decisions
- modify original evidence
- modify rules
- finalize inspections
- alter finalized history

The conceptual responsibility split is:

```text
PaddleOCR
   ↓
READS

Gemini
   ↓
UNDERSTANDS

Backend
   ↓
VALIDATES

Applicability Engine
   ↓
DETERMINES RELEVANCE

Compliance Rules
   ↓
EVALUATE

Evidence System
   ↓
SUPPORTS

Inspector
   ↓
VERIFIES

Reviewer
   ↓
DECIDES
```

---

# 18. Structured AI Contract

AI output must be constrained to a controlled schema.

Each accepted declaration should preserve:

- value
- normalized representation where applicable
- observation status
- AI extraction confidence
- source OCR region(s)
- source evidence reference(s)

Allowed observation statuses:

```text
OBSERVED
NOT_OBSERVED
UNCERTAIN
UNREADABLE
CONFLICTING
```

Validation sequence:

```text
AI Response
    ↓
Schema Validation
    ↓
Domain / Business Validation
    ↓
Applicability
    ↓
Deterministic Rules
```

Malformed output must be handled as a controlled processing error.

---

# 19. Uncertainty Rules

The agent must preserve uncertainty instead of guessing.

Examples:

```text
Two different MRP values detected
    → CONFLICTING
    → REQUIRES_REVIEW

Text cannot be read
    → UNREADABLE
    → not "missing"

Declaration not found in available evidence
    → NOT_OBSERVED
    → not automatically "non-compliant"

AI API unavailable
    → PROCESSING_FAILED
    → not "non-compliant"

Evidence insufficient
    → INCOMPLETE / REQUIRES_REVIEW
    → depending on workflow state
```

No unsupported fact may be promoted into structured truth.

---

# 20. Confidence Separation

The agent must never treat all confidence values as interchangeable.

```text
OCR Confidence
      ≠
AI Extraction Confidence
      ≠
Evidence Sufficiency
      ≠
Compliance Result
```

No universal hard-coded OCR threshold should be invented without validation.

Thresholds should be calibrated empirically where required.

---

# 21. Evidence Rules

Evidence is central to the system.

Evidence categories:

```text
PRIMARY EVIDENCE
Original package images

SUPPLEMENTAL EVIDENCE
Additional evidence added later

DERIVED EVIDENCE
OCR regions, crops, highlights, etc.

AUDIT / DECISION RECORD
Workflow history, not package evidence
```

The original evidence must be immutable.

Every evidence item should have:

- server-generated Evidence ID
- inspection association
- metadata
- integrity hash
- provenance
- controlled access
- audit event

New evidence must receive a new Evidence ID.

Never silently overwrite the original evidence.

---

# 22. Evidence Integrity

Use SHA-256 or the approved integrity mechanism defined by the implementation.

Important distinction:

> **A hash provides tamper-evident integrity/change detection. It does not prove the truth or authenticity of the underlying photograph.**

The agent must not overstate what hashing proves.

---

# 23. Evidence Upload Security

Evidence handling must include appropriate:

- authentication
- authorization
- MIME/type validation
- file-size validation
- image decode validation
- safe storage
- server-generated identifiers
- protected access
- provenance
- audit logging

Evidence should not be exposed merely because a client knows a predictable filename or identifier.

Secrets and API keys remain server-side.

---

# 24. Adaptive Evidence

Do not hard-code an arbitrary number of required photographs.

Evidence requirements should be based on whether the available evidence is sufficient to establish the relevant fact.

If evidence is insufficient:

```text
Evidence Insufficient
       ↓
Inspector Verification
       ↓
Manual observation OR
Supplemental evidence OR
Unable to establish
       ↓
Re-analysis if required
       ↓
Resubmit
```

The system must not assume that every case can or must be solved through automatic recapture.

---

# 25. Human-in-the-Loop Boundaries

### Inspector

The Inspector prepares and verifies.

Can:

- create inspection
- provide context
- upload evidence
- start analysis
- inspect OCR/declarations
- correct extracted values
- add observations
- add supplemental evidence
- verify applicability
- verify assessment
- submit

Cannot:

- finalize
- change rules
- modify original evidence
- delete protected evidence
- mutate finalized records
- alter audit history
- approve their own final decision

### Reviewer

The Reviewer independently decides.

Can:

- review submitted inspections
- inspect evidence and history
- confirm assessments
- correct/override assessment with reason
- request additional evidence
- finalize

Cannot:

- modify the controlled rule set
- delete finalized historical records
- silently mutate finalized records

---

# 26. Correction Ownership

Keep these responsibilities distinct:

```text
Inspector
    ↓
Corrects underlying observed/extracted information

Reviewer
    ↓
Corrects / overrides the resulting assessment or decision
```

The Reviewer does not need to approve every Inspector correction individually.

However, all material corrections must remain auditable.

---

# 27. Submission Boundary

The workflow has a deliberate ownership boundary.

```text
WORKING / PRE-SUBMISSION
        ↓
Inspector controls
        ↓
SUBMIT
        ↓
REVIEW
        ↓
Reviewer controls
```

After submission:

- Inspector becomes view-oriented for the submitted record.
- Reviewer owns the review decision.

If additional evidence is requested:

```text
Reviewer
   ↓
Evidence Request ID
   ↓
Inspector
   ↓
Supplemental Evidence / Manual Observation
   ↓
Re-analysis if affected
   ↓
Verification
   ↓
Resubmit
   ↓
Reviewer
```

---

# 28. Global State Invariant

Every upstream correction must follow:

> **Upstream correction → invalidate affected downstream state → recompute → preserve prior state/history → audit transition.**

Example:

```text
Extracted MRP = ₹199
        ↓
Inspector corrects to ₹179
        ↓
Old downstream assessment invalidated
        ↓
Compliance recalculated
        ↓
New result generated
        ↓
Old/new values preserved
        ↓
Correction audited
```

Never allow stale results to survive a material upstream correction.

---

# 29. Finalization

Finalization is a controlled backend operation.

The Reviewer initiates finalization.

The backend must:

1. validate lifecycle state
2. validate required data
3. validate evidence references
4. validate applicable assessments
5. create a final snapshot atomically
6. preserve relevant rule version/snapshot
7. preserve audit references
8. mark the record finalized
9. prevent normal mutation

The final snapshot should contain or reference:

- inspection
- product
- evidence
- evidence hashes
- OCR
- extraction
- applicability
- assessments
- findings
- corrections
- reviews
- rule snapshot/version
- provenance
- final decision
- audit references

Report generation happens from the final snapshot.

A report-generation failure must not undo finalization.

---

# 30. Historical Integrity

Finalized records are historical records.

The agent must not silently recalculate finalized inspections when:

- rules change
- prompts change
- AI models change
- OCR versions change
- code changes

Historical records retain the rule/model/provenance context required by the project specification.

Future rule changes apply to future processing unless an explicit migration/reprocessing workflow is approved.

---

# 31. Database and Storage

The deployed MVP must be cloud-deployable.

Therefore:

```text
Production
    ↓
Persistent Cloud-Capable Relational Database
    +
Persistent Object/File Storage
```

Do not design the deployed MVP around:

- local-only SQLite
- ephemeral local filesystem
- temporary process memory

SQLite may be used for local development/testing if practical, but it is not the production source of truth.

The exact production provider remains open until implementation/team discussion.

Do not lock the architecture to a provider without approval unless the implementation decision is explicitly made.

---

# 32. Deployment Principle

The deployment environment is part of MVP design.

The agent must consider:

- persistent database
- persistent evidence storage
- server-side secrets
- backend hosting
- frontend hosting
- CORS/auth configuration
- production environment variables
- external API availability
- persistent URLs/endpoints
- judge accessibility

A frontend host such as Vercel may be used, but:

> **Frontend deployment does not define the backend/database/storage architecture.**

Do not build a local-only system and postpone deployment compatibility until the end.

---

# 33. API Discipline

API contracts should remain:

- explicit
- validated
- deterministic where possible
- aligned with lifecycle state
- authorization-aware
- provenance-aware

The agent must not expose security-sensitive operations solely because the frontend needs them.

The backend remains authoritative for:

- permissions
- lifecycle transitions
- evidence integrity
- compliance evaluation
- finalization
- audit behavior

If an API change is breaking or materially affects another subsystem, identify it before implementing it.

---

# 34. Frontend Discipline

The frontend is a presentation and interaction layer.

Do not trust the client for:

- authorization
- finalization
- compliance decisions
- evidence ownership
- lifecycle transitions
- integrity controls

The UI should clearly distinguish:

```text
Observed
Not Observed
Uncertain
Unreadable
Potential Non-Compliance
Requires Review
Not Applicable
Incomplete
Processing Failed
```

Avoid misleading green/red indicators that imply legal certainty where the backend only has an uncertain observation.

---

# 35. Testing Discipline

Every meaningful implementation step should have an appropriate verification method.

Possible levels:

```text
Static inspection
     ↓
Unit test
     ↓
Integration test
     ↓
Workflow test
     ↓
End-to-end test
     ↓
Deployment smoke test
```

Do not claim end-to-end correctness from unit tests alone.

For the MVP, the highest priority is the complete representative workflow.

Critical P0 failures include:

- extraction failure that changes the result
- fabricated declarations
- unsupported compliance claims
- missing evidence provenance
- stale results after corrections
- technical failure shown as non-compliance
- inability to persist deployed inspection data
- inability to demonstrate the full journey

---

# 36. Representative Evidence Testing

The AI/OCR implementation must be validated using representative packaged-commodity images.

Testing should verify:

- OCR readability
- bounding boxes
- declaration extraction
- source mapping
- normalization
- conflict handling
- applicability
- six compliance checks
- finding generation
- evidence linking
- correction/recomputation
- final result

Do not select architecture solely from theoretical benchmark claims.

Implementation experience with representative project data is part of engineering validation.

---

# 37. Error Handling

Errors must remain semantically meaningful.

Examples:

```text
Invalid Image
      → INPUT / IMAGE ERROR

OCR unavailable
      → PROCESSING_FAILED

Gemini unavailable
      → PROCESSING_FAILED

Malformed AI response
      → CONTROLLED RETRY → PROCESSING_FAILED

Conflicting declarations
      → REQUIRES_REVIEW

Insufficient evidence
      → INCOMPLETE / REVIEW

Potential rule issue
      → POTENTIAL_NON_COMPLIANCE

Requirement does not apply
      → NOT_APPLICABLE
```

Never use one generic error state for every problem.

---

# 38. Observability

For important processing steps, the system should make it possible to determine:

- which inspection was processed
- which evidence was used
- which processing stage ran
- which OCR result was produced
- which AI extraction was produced
- which rule snapshot was used
- which assessment was generated
- what correction occurred
- who performed it
- when it occurred
- whether processing failed

Do not log secrets, raw API keys, or unnecessary sensitive information.

---

# 39. Security Decision Rules

When choosing between:

```text
FAST BUT UNSAFE
```

and:

```text
SLIGHTLY MORE WORK BUT SAFE
```

choose the safe implementation.

Especially for:

- authentication
- authorization
- file uploads
- evidence access
- secrets
- finalization
- audit records
- database writes

However, security should not be used as an excuse to create unrelated enterprise infrastructure during the one-day MVP.

Implement the security controls necessary for the actual deployed workflow.

---

# 40. Dependency Discipline

Before adding a dependency, determine:

1. Why is it needed?
2. Is it required for the current MVP?
3. Is there already a suitable dependency?
4. Does it complicate deployment?
5. Does it introduce unnecessary licensing/security risk?
6. Can the feature be implemented simply without it?

Avoid dependency accumulation.

---

# 41. AI Provider Discipline

The current model decision is:

> **Gemini 2.5 Flash**

Puter is currently **set aside** and must not be introduced into the architecture unless the human explicitly reopens that decision.

If an alternative model/provider is proposed:

- explain why
- identify the benefit
- identify migration impact
- identify cost/deployment implications
- identify whether the change affects the current critical path
- obtain approval if the change is material

Do not switch providers casually.

---

# 42. Change Management

When modifying code, first determine:

```text
What is changing?
Why?
Which document defines it?
Which current phase requires it?
What existing behavior can it break?
How will it be tested?
```

For small safe changes, proceed.

For material changes, propose before changing.

Every material implementation change should leave the project in a state where `PROJECT_STATE.md` can accurately describe reality.

---

# 43. Documentation Discipline

Documentation exists to support implementation, not replace it.

Do not create documentation merely to postpone coding.

Do not repeatedly rewrite all project documents for minor implementation details.

Update a document when:

- its authoritative behavior changed
- a locked decision changed
- current MVP scope changed
- actual implementation state needs recording
- a contract must remain synchronized

Otherwise, keep moving.

The project explicitly rejects an endless documentation loop.

---

# 44. PROJECT_STATE Discipline

`PROJECT_STATE.md` is the living implementation ledger.

It should reflect:

- current phase
- implemented components
- working components
- known failures
- current blockers
- verified behavior
- pending work
- approved decisions
- deferred work

The agent must not turn `PROJECT_STATE.md` into optimistic marketing prose.

If something is broken:

> Record it as broken.

If something is unverified:

> Record it as unverified.

---

# 45. Phase-Exit Report

At the end of each phase, the agent should report:

```text
PHASE:
STATUS:

COMPLETED:
- ...

VERIFIED:
- ...

NOT VERIFIED:
- ...

KNOWN ISSUES:
- ...

FILES / COMPONENTS CHANGED:
- ...

TESTS RUN:
- ...

MVP IMPACT:
- ...

NEXT PHASE:
- ...
```

If a phase cannot be completed safely, stop and explain why rather than pretending completion.

---

# 46. When to Stop

Stop and ask for human direction when:

- the next implementation choice materially changes architecture
- requirements conflict
- legal semantics are ambiguous
- a required dependency is unavailable
- deployment requires an unapproved provider decision
- a security-sensitive tradeoff is unclear
- a feature would expand MVP scope
- the agent cannot verify a critical behavior
- the repository state differs substantially from the documented state
- a destructive migration is required
- finalization/evidence integrity semantics would be changed

Do not hide uncertainty behind code.

---

# 47. Safe Terminal / Tool Behavior

During discovery and audit:

- prefer read-only commands
- inspect before modifying
- avoid destructive commands
- avoid deleting files without explicit need
- avoid mass rewrites
- avoid irreversible migrations
- avoid exposing secrets

When a command can modify the system substantially, request human review where the environment supports it.

---

# 48. Implementation Priority

When time is limited, prioritize:

```text
P0 — MUST WORK
│
├── Representative image input
├── Image processing
├── PaddleOCR
├── Gemini extraction
├── Structured declarations
├── Applicability
├── Six compliance checks
├── Findings
├── Evidence references
├── Inspector verification
├── Result
├── Persistence
└── Deployable demonstration
```

Then:

```text
P1 — IMPORTANT IF TIME ALLOWS
│
├── Better UI polish
├── Improved evidence visualization
├── Better error presentation
├── Basic export
├── Basic history/repository support
└── Demonstration refinements
```

Target-system features not required for the vertical slice remain deferred.

---

# 49. Definition of Done for the MVP

The MVP is not done when:

- files exist
- pages render
- OCR runs in isolation
- Gemini returns JSON
- database tables exist

The MVP is done when a representative user journey works:

```text
User
 ↓
Provides package evidence
 ↓
System processes evidence
 ↓
OCR reads declarations
 ↓
AI structures declarations
 ↓
Backend validates
 ↓
Applicability evaluated
 ↓
Six checks evaluated
 ↓
Findings generated
 ↓
Evidence attached
 ↓
Inspector verifies/corrects
 ↓
Result produced
 ↓
Data persists
 ↓
Deployment/demo works
```

The journey must be coherent enough for a judge to understand the product's value.

---

# 50. Final Engineering Contract

Every implementation decision should satisfy these questions:

### Scope

> Is this required for the current MVP?

### Correctness

> Does it produce the intended behavior?

### Evidence

> Can important results be traced back to evidence?

### Uncertainty

> Does it preserve ambiguity instead of guessing?

### Lifecycle

> Does it respect the current state and ownership boundaries?

### Security

> Does it protect the actual deployed workflow?

### Deployment

> Will it work outside the developer's local machine?

### Auditability

> Can we explain what happened and why?

### Maintainability

> Is the implementation simple enough to finish and understand?

### Honesty

> Can we prove the claim that this is implemented and working?

If the answer to a critical question is no, do not hide the gap.

---

# 51. Core Rules to Remember

If the agent remembers nothing else, remember these:

```text
1. Read before coding.
2. Inspect the repository before making implementation claims.
3. MVP_BUILD_SCOPE.md defines the current boundary.
4. PROJECT_STATE.md defines actual reality.
5. PHASE.md defines execution order.
6. Do not redesign the target architecture.
7. Do not implement deferred features.
8. One complete user journey beats many partial systems.
9. PaddleOCR reads.
10. Gemini understands.
11. Backend validates.
12. Applicability determines relevance.
13. Deterministic rules evaluate.
14. Evidence supports.
15. Inspector verifies.
16. Reviewer decides.
17. AI never makes the final legal decision.
18. Never invent unsupported facts.
19. Never turn uncertainty into non-compliance.
20. Never turn technical failure into non-compliance.
21. Preserve original evidence.
22. Preserve provenance.
23. Upstream correction invalidates affected downstream state.
24. Finalized records are protected historical records.
25. Production MVP must use persistent cloud-capable storage.
26. Ask before material scope or architecture changes.
27. Test the complete workflow.
28. Never claim what has not been verified.
29. Stop the documentation loop and build.
30. The goal is a reliable, demonstrable MVP — not a perfect future system.
```

---

# 52. Final Principle

ComplianceScan is being built under a simple engineering philosophy:

> **Build deliberately. Verify honestly. Preserve evidence. Respect uncertainty. Control scope. Keep the architecture coherent. Deliver one complete journey.**

And the product philosophy remains:

> **AI finds → Evidence proves → Officer decides.**
