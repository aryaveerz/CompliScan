# ComplianceScan

**SIH'26 — Problem Statement 26034**

> **Software System to check compliance of Packaged Commodities under Legal Metrology (Packaged Commodities) Rules, 2011 by scanning products, images and labels.**

ComplianceScan is an inspection-assistance system designed to help an inspector analyze packaged-commodity labels, identify relevant mandatory declarations, surface potential compliance issues, preserve supporting evidence, and produce a reviewable inspection record.

The system is designed around one core principle:

> **AI finds → Evidence proves → Officer decides.**

ComplianceScan is **not** intended to replace statutory judgment or automatically declare a legal violation. AI and deterministic rules assist the inspection workflow; the Inspector verifies the observed information, and the Reviewer independently makes the final decision.

---

## 1. Project Status

The project documentation describes a **target/full system**, while the current implementation is intentionally constrained to a **one-day MVP vertical slice**.

This distinction is important:

- The numbered specification documents describe the broader target system and its intended architecture.
- `MVP_BUILD_SCOPE.md` defines what is actually allowed in the current MVP build.
- `PROJECT_STATE.md` records what is actually implemented.
- `PHASE.md` defines the execution order and phase gates.
- `AGENT_ENGINEERING_PROTOCOL.md` controls how implementation agents must work.
- The remaining numbered documents provide detailed domain, technical, architectural, API, database, state, compliance, design, and error-handling specifications.

**The target architecture is not being redesigned. The current MVP is a deliberately smaller implementation slice of that architecture.**

---

## 2. SIH Problem Context

### Organization

**Ministry of Consumer Affairs, Food & Public Distribution**

### Department

**Department of Consumer Affairs (DoCA)**

### Category

**Software**

### Theme

**Miscellaneous**

### Problem Statement

The system should support scanning packaged commodities, images, labels, and product information to identify mandatory declarations and help assess whether those declarations appear complete, correct, appropriately presented, and readable.

The intended solution includes automated extraction and validation, evidence-backed findings, reports, repository/history, dashboards, search/retrieval, security, and role-based workflows.

ComplianceScan implements this problem as an **inspection-assistance workflow**, with human verification and final decision authority retained by officers.

---

# 3. Core Workflow

The target workflow is:

```text
                COMPLIANCESCAN
                     │
                     ▼
              PRODUCT INPUT
        Physical Package / Online Listing
                     │
                     ▼
          AI-POWERED ANALYSIS
            OCR + Computer Vision
                     │
                     ▼
         DECLARATION EXTRACTION
 Manufacturer • Packer • Importer
 Net Quantity • MRP • Dates
 Consumer Care • Other Fields
                     │
                     ▼
      PRODUCT / PACKAGE CLASSIFICATION
                     │
                     ▼
           APPLICABILITY ENGINE
        Category + Context + Exemptions
                     │
                     ▼
         COMPLIANCE ANALYSIS
          Rules + Visual Analysis
                     │
                     ▼
          COMPLIANCE RESULT
 PASS / POTENTIAL NON-COMPLIANCE /
 REQUIRES REVIEW / NOT APPLICABLE /
 INCOMPLETE / PROCESSING FAILED
                     │
                     ▼
          EVIDENCE GENERATION
 Rule + Reason + Highlight + Confidence
                     │
                     ▼
          INSPECTOR VERIFICATION
       Confirm / Correct / Review
                     │
                     ▼
          REVIEWER DECISION
       Confirm / Correct / Override
                     │
                     ▼
          FINAL INSPECTION RECORD
                     │
                     ▼
         REPORT + REPOSITORY +
          DASHBOARD + HISTORY
```

For the **current one-day MVP**, this is reduced to one complete end-to-end vertical slice:

```text
Upload Evidence
      ↓
Image Quality / Processing
      ↓
PaddleOCR
      ↓
Gemini 2.5 Flash
      ↓
Structured Declarations
      ↓
Applicability
      ↓
Six Controlled Compliance Checks
      ↓
Findings + Evidence
      ↓
Inspector Verification
      ↓
Final MVP Result
      ↓
Basic Report / Demonstration Output
```

The MVP must demonstrate a **complete usable journey**, not many disconnected subsystems.

---

# 4. Current One-Day MVP Boundary

The current MVP is intentionally small.

## 4.1 Supported Compliance Checks

The current MVP focuses on six core declaration checks:

1. **Manufacturer / Packer / Importer**
2. **Common / Generic Product Name**
3. **Net Quantity + Standard Unit**
4. **Month / Year of Manufacture / Packing / Import**
5. **MRP inclusive of all taxes**
6. **Consumer Care Details**

### Country of Origin

Country of Origin is **applicability-driven**:

```text
Imported = YES
    → Country of Origin applicable

Imported = NO
    → NOT_APPLICABLE

Imported = UNKNOWN
    → REVIEW / BLOCK AS APPROPRIATE
```

It is not treated as a universal mandatory field for every product.

---

## 4.2 Deliberately Deferred from the One-Day MVP

The following are target-system capabilities or future enhancements and must not be allowed to expand the one-day critical path:

- Full category-specific legal rule coverage
- Unit Sale Price
- Universal exemption handling
- Dynamic regulatory/rule update pipeline
- Universal packaging-layout/legal placement verification
- Definitive legal font-size determination from uncontrolled photographs
- Internet-wide product crawling
- Full Physical ↔ Online Verification workflow
- Advanced repository/search/dashboard capabilities beyond what is necessary for the vertical slice
- Full production-grade reporting suite
- Broad enforcement/follow-up workflow
- Large-scale multi-service architecture
- Unnecessary microservices
- Feature work not required by the current MVP acceptance criteria

**Deferred does not mean rejected.** These remain part of the broader target system where applicable.

---

# 5. Result Vocabulary

ComplianceScan uses explicit result states.

| Result | Meaning |
|---|---|
| `PASS` | The supported requirement is satisfied based on available evidence and rules. |
| `POTENTIAL_NON_COMPLIANCE` | The system found an apparent issue requiring officer verification. |
| `REQUIRES_REVIEW` | The available information is conflicting, ambiguous, or otherwise requires human review. |
| `NOT_APPLICABLE` | The requirement does not apply under the supported applicability conditions. |
| `INCOMPLETE` | There is insufficient information/evidence to establish the required fact or assessment. |
| `PROCESSING_FAILED` | A technical processing step failed; this is not a compliance failure. |

Important distinctions:

```text
NOT_APPLICABLE ≠ PASS
INCOMPLETE ≠ POTENTIAL_NON_COMPLIANCE
PROCESSING_FAILED ≠ NON_COMPLIANCE
NOT_OBSERVED ≠ MISSING
UNREADABLE ≠ MISSING
CONFLICTING → REQUIRES_REVIEW
```

The system must not convert uncertainty or technical failure into a legal conclusion.

---

# 6. AI / OCR Architecture

The current selected OCR engine is **PaddleOCR**.

The current selected AI model is **Gemini 2.5 Flash**.

The implementation flow is:

```text
Package Image
      ↓
Image Processing / CV
      ↓
PaddleOCR
      ↓
OCR Text + Bounding Boxes + Confidence
      ↓
Gemini 2.5 Flash
      ↓
Structured Declaration Data
      ↓
Backend Validation
      ↓
Applicability Engine
      ↓
Deterministic Compliance Rules
      ↓
Findings + Evidence
      ↓
Inspector Verification
      ↓
Reviewer Decision
```

### Responsibility boundaries

**PaddleOCR reads.**

It provides:

- detected text
- recognized text
- bounding boxes
- OCR confidence
- source-image association

**Gemini understands.**

It is used primarily for:

- declaration extraction
- semantic interpretation
- normalization
- context mapping
- conflict detection
- preserving uncertainty

**Backend validates.**

It performs:

- schema validation
- business/domain validation
- state/lifecycle validation
- evidence/reference validation

**Applicability determines relevance.**

It determines whether a supported requirement applies in the inspection context.

**Deterministic rules evaluate.**

The compliance engine evaluates structured information against the controlled rule set.

**Evidence supports.**

Findings retain their rule references and supporting evidence.

**Inspector verifies.**

The Inspector can correct extracted information, add observations, supplement evidence, and verify the working result.

**Reviewer decides.**

The Reviewer independently confirms, corrects/overrides, requests additional evidence, and finalizes.

---

# 7. AI Reliability Rules

AI output is treated as **structured, uncertain observation data**, not as legal truth.

Accepted declarations carry:

- extracted value
- normalized value where applicable
- observation status
- AI extraction confidence
- source OCR region(s)
- source evidence reference(s)

Observation statuses:

```text
OBSERVED
NOT_OBSERVED
UNCERTAIN
UNREADABLE
CONFLICTING
```

Rules:

1. No accepted AI fact without a source/evidence reference.
2. No unsupported declaration may be invented.
3. Conflicting values must be preserved and surfaced.
4. Ambiguous interpretation becomes `UNCERTAIN`.
5. Unreadable information is distinct from information that was not observed.
6. Low-confidence OCR must not silently become high-confidence structured data.
7. Malformed AI output is a processing error, not a compliance failure.
8. AI API failure results in `PROCESSING_FAILED`.
9. The original evidence must never be modified by the AI pipeline.
10. AI must never finalize an inspection or alter finalized history.

Confidence values are deliberately separated:

```text
OCR Confidence
      ≠
AI Extraction Confidence
      ≠
Evidence Sufficiency
      ≠
Compliance Result
```

---

# 8. Applicability-First Design

ComplianceScan does not simply ask:

> "Is this declaration present?"

It first asks:

> **"Does this requirement apply to this inspection context?"**

The intended sequence is:

```text
Product / Package Context
          ↓
Applicability
          ↓
Requirement Relevant?
       ↙       ↘
     YES        NO
      ↓          ↓
    Validate   NOT_APPLICABLE
```

This prevents the system from treating every possible declaration as universally mandatory.

The MVP only implements the explicitly supported applicability conditions. It does **not** claim universal coverage of every exemption or product category under the Rules.

---

# 9. Evidence-First Design

A compliance finding must be explainable and reviewable.

The system should be able to answer:

- What requirement was evaluated?
- What was observed?
- What rule/reference was used?
- Why was the result produced?
- Which evidence supports the observation?
- Where in the image was the relevant information found?
- What confidence/uncertainty exists?
- What did the Inspector verify?
- What did the Reviewer decide?

Conceptually:

```text
Finding
 ├── Requirement
 ├── Rule Reference
 ├── Reason
 ├── Assessment
 ├── Confidence / Uncertainty
 ├── Evidence Reference
 ├── OCR Region
 └── Derived Highlight / Crop
```

The principle is:

> **A finding without traceable evidence is incomplete.**

---

# 10. Evidence Integrity

The original package evidence is treated as immutable.

Evidence categories:

- **Primary Evidence** — original package images captured for the inspection
- **Supplemental Evidence** — later evidence added after a request/review
- **Derived Evidence** — OCR boxes, crops, highlights, and other generated artifacts
- **Audit/Decision Records** — workflow records, not package evidence

Each evidence item should have:

- server-generated Evidence ID
- inspection association
- metadata
- integrity hash
- provenance
- access controls
- audit event

SHA-256 hashing provides **tamper-evident integrity/change detection**.

It does not prove that the photograph itself is truthful or authentic.

New evidence receives a new Evidence ID. Original evidence is not silently replaced.

Evidence capture is adaptive: the system should request or support additional evidence when needed, rather than imposing an arbitrary fixed number of photographs.

---

# 11. Human-in-the-Loop Workflow

The operational contract is:

> **The Inspector prepares and verifies. The System analyzes and records. The Reviewer independently decides and finalizes.**

### Inspector

The Inspector can:

- create an inspection
- provide inspection/product context
- upload evidence
- start analysis
- inspect OCR/declarations/findings
- correct extracted values
- add manual observations
- add supplemental evidence
- verify applicability/compliance
- submit for review
- view a preliminary result/report

The Inspector cannot:

- finalize an inspection
- change compliance rules
- modify original evidence
- delete protected evidence
- mutate finalized records
- alter audit history
- approve their own final decision

### Reviewer

The Reviewer can:

- receive submitted inspections
- search/filter/sort review records
- inspect evidence, OCR, declarations, applicability, findings, and history
- confirm an assessment
- correct or override an assessment with a reason
- request additional evidence
- finalize the inspection

The Reviewer cannot:

- change the rule set
- delete finalized historical records
- silently mutate finalized records

Inspector and Reviewer responsibilities are deliberately separated:

```text
Inspector → corrects observed/extracted data
Reviewer  → reviews assessment and makes final decision
```

---

# 12. Finalization and History

Finalization is a controlled workflow.

At finalization:

1. Reviewer initiates finalization.
2. Backend validates the inspection state.
3. A final snapshot is created atomically.
4. The snapshot references the relevant:
   - inspection/product information
   - evidence and hashes
   - OCR results
   - extracted declarations
   - applicability decisions
   - compliance assessments
   - findings
   - corrections
   - review decisions
   - rule snapshot/version
   - provenance
   - audit references
5. The finalized record becomes read-only through the normal workflow.
6. The report is generated from the final snapshot.
7. Report-generation failure does not roll back the finalized decision.

Historical inspections retain the rule snapshot/version under which they were evaluated. Future rule changes must not silently recalculate finalized historical inspections.

Enforcement/follow-up is outside the current MVP.

---

# 13. Global State Invariant

The system follows one important lifecycle rule:

> **Upstream correction → invalidate affected downstream state → recompute → preserve prior state/history → audit transition.**

Example:

```text
Inspector corrects extracted MRP
          ↓
Affected compliance assessment invalidated
          ↓
Compliance re-evaluated
          ↓
New finding/result generated
          ↓
Old value + new value preserved
          ↓
Correction audited
```

The system must never allow a correction to silently leave stale downstream results.

---

# 14. Target System Architecture

The broader architecture consists of logical components, not mandatory microservices.

```text
                    ┌─────────────────────┐
                    │      Users          │
                    │ Inspector / Reviewer│
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Web Application   │
                    │ React + Vite + UI   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   FastAPI / API     │
                    │ Lifecycle + Security│
                    └──────────┬──────────┘
                               │
       ┌───────────────────────┼────────────────────────┐
       │                       │                        │
       ▼                       ▼                        ▼
 Inspection              Evidence                Processing
 Management              Management              Pipeline
       │                       │                        │
       │               ┌───────┴────────┐       ┌──────┴──────┐
       │               │                │       │             │
       │               ▼                ▼       ▼             ▼
       │          Object Storage      Hash   Image/CV      OCR
       │                                      │             │
       │                                      └──────┬──────┘
       │                                             ▼
       │                                      Gemini 2.5 Flash
       │                                             │
       └──────────────────────┬──────────────────────┘
                              ▼
                    Declaration Understanding
                              │
                              ▼
                    Applicability Engine
                              │
                              ▼
                    Controlled Compliance Rules
                              │
                              ▼
                    Compliance Engine
                              │
                              ▼
                    Findings + Evidence
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
       Inspector Verification       Reviewer / Final Decision
                 │                         │
                 └────────────┬────────────┘
                              ▼
                    Finalization / Snapshot
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
       Reports            Repository          Dashboard
```

The target architecture includes these logical areas:

1. Users
2. Web Application
3. FastAPI Application/API Layer
4. Inspection Management
5. Evidence Management
6. Image Processing & Quality
7. OCR Engine
8. Visual Analysis
9. Declaration Extraction & AI Understanding
10. Applicability Engine
11. Evidence Sufficiency & Coverage
12. Controlled Compliance Rules
13. Compliance Engine
14. Findings & Evidence Generation
15. Inspector Verification
16. Reviewer & Final Decision
17. Finalization & Immutable Snapshot
18. Reporting & Export
19. Repository & History
20. Search & Retrieval
21. Dashboard & Metrics
22. Database
23. Persistent Object/File Storage
24. Security / Integrity / Audit
25. Physical ↔ Online Verification

These are **logical boundaries**. They do not imply that every box must become a separate service.

---

# 15. Cloud-Deployable from the Beginning

The MVP must be deployable for external demonstration and judging.

Therefore:

- A local-only database is **not** the deployed architecture.
- A local filesystem is **not** the deployed evidence-storage architecture.
- The deployed MVP requires a **persistent cloud-capable relational database**.
- The deployed MVP requires **persistent object/file storage** for evidence.
- The exact database, storage provider, and backend hosting technology remain open until implementation/team discussion.
- SQLite may be used as a local development/test convenience where appropriate, but it is not the production source of truth.
- A frontend platform such as Vercel may be used, but frontend hosting does not determine the backend/database/storage architecture.
- Secrets and API keys must remain server-side.

The architectural requirement is:

> **Build the MVP so that deployment is a normal deployment step, not a redesign after local development.**

---

# 16. Current Technology Decisions

The final production stack has **not** been permanently locked.

Technology choices should be made pragmatically during implementation based on:

- speed of development
- reliability
- deployment suitability
- team familiarity
- cost
- judge/demo accessibility
- maintainability

Current selected AI/OCR choices:

| Component | Current Choice |
|---|---|
| OCR | PaddleOCR |
| AI Model | Gemini 2.5 Flash |
| Backend concept | Python / FastAPI |
| Frontend concept | React + Vite |
| UI concept | Tailwind |
| Production database | Cloud-capable relational DB; provider open |
| Production evidence storage | Persistent object/file storage; provider open |
| Frontend deployment | Vercel is a possible option, not a mandatory final decision |

These choices may be refined during implementation where the change is justified and does not expand MVP scope.

---

# 17. Physical ↔ Online Verification

The broader target system includes a **Physical ↔ Online Verification** capability.

It is intended to compare:

```text
Physical Package
      ↕
Online Product Information
```

Possible comparisons include:

- product identity
- manufacturer/packer/importer
- net quantity
- MRP
- other supported declarations

A mismatch should be represented as a **Cross-Channel Inconsistency**.

It is **not automatically treated as a legal violation**.

Internet-wide crawling is outside the MVP.

---

# 18. Project Documentation Structure

The repository is organized around clear document authority.

```text
ComplianceScan/
│
├── README.md
├── MVP_BUILD_SCOPE.md
├── PROJECT_STATE.md
├── PHASE.md
├── AGENT_ENGINEERING_PROTOCOL.md
│
├── 01_PRD.md
├── 02_TRD.md
├── 03_Architecture.md
├── 04_Design.md
├── 05_Domain_Specification.md
├── 06_Compliance_Rules.md
├── 07_State_Machine.md
├── 08_API_Specification.md
├── 09_Database_Specification.md
├── 10_Error_Handling.md
├── 11_Testing_and_Release_Gate.md
│
└── .agents/
    └── skills/
        └── compliance-engineering/
            └── SKILL.md
```

## Document authority

| Document | Primary Purpose |
|---|---|
| `README.md` | Project orientation and high-level contract |
| `MVP_BUILD_SCOPE.md` | **Current implementation boundary** |
| `PROJECT_STATE.md` | **Actual implementation state** |
| `PHASE.md` | Execution sequence and phase gates |
| `AGENT_ENGINEERING_PROTOCOL.md` | Engineering-agent behavior and decision controls |
| `01_PRD.md` | Product requirements and intent |
| `02_TRD.md` | Technical requirements and constraints |
| `03_Architecture.md` | Target system structure and boundaries |
| `04_Design.md` | UI/UX and interaction design |
| `05_Domain_Specification.md` | Domain semantics and terminology |
| `06_Compliance_Rules.md` | Compliance-rule behavior |
| `07_State_Machine.md` | Lifecycle/state semantics |
| `08_API_Specification.md` | Frontend/backend contracts |
| `09_Database_Specification.md` | Persistence model |
| `10_Error_Handling.md` | Failure and recovery semantics |
| `11_Testing_and_Release_Gate.md` | Testing, quality, and release criteria |

A specialized document is authoritative for its own domain. Other documents should reference it rather than independently redefining the same behavior.

---

# 19. Implementation Control

The project has two distinct layers:

```text
TARGET SYSTEM
     │
     │ reference architecture / future capabilities
     ▼
CURRENT MVP
     │
     │ controlled implementation subset
     ▼
ACTUAL PROJECT STATE
```

The agent must not infer the MVP from the largest specification document.

Instead:

1. Read `MVP_BUILD_SCOPE.md`.
2. Read `PROJECT_STATE.md`.
3. Read `PHASE.md`.
4. Follow `AGENT_ENGINEERING_PROTOCOL.md`.
5. Consult the numbered specifications as authoritative reference documents.
6. Inspect the actual repository before making implementation claims.
7. Implement only the current phase and approved scope.
8. Stop at human checkpoints when required.

---

# 20. Phase Execution

The current execution plan is defined by `PHASE.md`.

The high-level sequence is:

```text
PHASE 0 [VERIFIED PASSED]
Repository / Implementation Audit
        ↓
PHASE 1 [VERIFIED PASSED]
Core DB, Auth, Storage, RBAC & Core Entities
        ↓
PHASE 2.1 [VERIFIED PASSED]
Image Quality Assessment Pipeline (QualityStatus)
        ↓
PHASE 2.2 [IN PROGRESS / PLANNED]
PaddleOCR Perception Pipeline (rapidocr-onnxruntime PP-OCRv4)
        ↓
PHASE 2.3 [PENDING]
Gemini 2.5 Flash Declaration Extraction
        ↓
PHASE 2.4 [PENDING]
Applicability + Rule Evaluation Engine
        ↓
PHASE 2.5 [PENDING]
Inspector Verification & Reviewer Triage
        ↓
PHASE 3 [PENDING]
Report & History Persistence
        ↓
PHASE 4 [PENDING]
Deployment + Demonstration Readiness
```

The first agent activity is **Phase 0**, not unrestricted coding.

Phase 0 must establish:

- what exists
- what works
- what is broken
- what is missing
- what can be reused
- what must be implemented
- what the shortest safe path to the vertical slice is

The agent then reports and waits for the required human checkpoint.

---

# 21. Engineering Agent Rules

The implementation agent must follow these principles:

### Scope control

> **MVP_BUILD_SCOPE.md outranks feature temptation.**

Do not:

- add features because they seem useful
- build deferred target-system functionality prematurely
- redesign the architecture unnecessarily
- create speculative abstractions
- expand the MVP because a target document is larger

### Anti-hallucination

The agent must never claim that something is implemented without checking the repository.

Statements such as:

```text
"already implemented"
"working"
"connected"
"deployed"
"tested"
```

must be backed by actual inspection or execution.

### Proposal before material scope change

If implementation reveals a genuine need for a change that affects:

- architecture
- MVP boundary
- data model
- API contract
- compliance semantics
- security/integrity behavior
- lifecycle/state behavior
- deployment assumptions

the agent must explain the issue, propose the smallest viable change, and obtain human approval where required.

### One complete user journey

The primary success criterion is:

> **ONE COMPLETE USER JOURNEY > MANY PARTIAL SUBSYSTEMS**

---

# 22. Testing and Release Philosophy

The MVP is not complete because individual components exist.

The release gate must validate the complete journey:

```text
Input
  ↓
Processing
  ↓
OCR
  ↓
AI extraction
  ↓
Validation
  ↓
Applicability
  ↓
Compliance checks
  ↓
Findings
  ↓
Evidence
  ↓
Inspector verification
  ↓
Result
  ↓
Basic output
  ↓
Deployment / demonstration
```

Critical failures include:

- wrong declaration extraction that changes the result
- unsupported legal claims
- fabricated AI values
- missing evidence provenance
- stale downstream results after correction
- processing failure reported as non-compliance
- inability to persist inspection data in the deployed environment
- inability to demonstrate the complete workflow

Target-system testing may be broader, but the one-day release gate is focused on the current vertical slice.

---

# 23. Security and Integrity Principles

Security is not an optional post-MVP decoration.

The system should enforce:

- authenticated access where required
- backend-authoritative authorization
- server-side validation
- controlled evidence upload
- MIME/type/size/decode validation
- protected evidence storage
- immutable original evidence
- SHA-256 integrity hashes
- audit events for important transitions
- protected finalized records
- server-side secrets
- no client-side trust for security-sensitive decisions

The frontend is a presentation layer. Security-sensitive authorization and lifecycle decisions belong to the backend.

---

# 24. What ComplianceScan Is — and Is Not

## ComplianceScan is:

- an inspection-assistance system
- an OCR and AI-assisted declaration extraction system
- an applicability-aware rule evaluation system
- an evidence-backed finding system
- a human-in-the-loop verification workflow
- a reviewable inspection record system
- a foundation for broader Legal Metrology compliance workflows

## ComplianceScan is not:

- an autonomous legal authority
- an automatic enforcement decision-maker
- a replacement for an authorized officer
- a universal implementation of every Legal Metrology exception/rule
- a system that treats AI confidence as legal certainty
- a system that treats technical processing failure as non-compliance
- an internet-wide product crawler in the MVP
- a justification for unnecessary microservices or feature expansion

---

# 25. Current MVP Success Definition

The one-day MVP is successful if a judge can take a representative packaged commodity image and observe a coherent flow:

```text
1. Upload / provide product evidence
2. System processes the image
3. PaddleOCR extracts observable text
4. Gemini 2.5 Flash structures declarations
5. Backend validates the extracted data
6. Applicability is evaluated
7. Six supported compliance checks are evaluated
8. Findings explain potential issues
9. Findings point to supporting evidence
10. Inspector can verify/correct the result
11. A clear final MVP result is produced
12. The inspection can be demonstrated as a persistent, deployable workflow
```

The demo should make the value obvious:

> **Instead of manually reading every declaration and assembling an inspection assessment from scratch, the officer receives structured observations, applicability-aware checks, evidence-backed findings, and a controlled verification workflow.**

---

# 26. Key Design Principles

The project is governed by these principles:

### 1. Applicability First

Determine whether a requirement applies before evaluating it.

### 2. Evidence Before Conclusions

Every meaningful finding should be traceable to supporting evidence.

### 3. AI Assists, Officers Decide

AI does not replace legal judgment.

### 4. Preserve Uncertainty

Unknown, unreadable, conflicting, and technically failed states remain distinct.

### 5. Immutable Evidence

Original evidence is preserved and integrity-protected.

### 6. Deterministic Compliance Evaluation

The backend rule engine evaluates structured data against controlled rules.

### 7. Human-in-the-Loop

Inspector verification and independent Reviewer decision are part of the target workflow.

### 8. Auditability

Important corrections and decisions preserve who, what, when, and why.

### 9. Cloud-Ready by Design

The deployed MVP must use persistent cloud-capable database and evidence storage.

### 10. One Complete Journey

A working vertical slice is more valuable than a large number of unfinished features.

### 11. No Silent State Corruption

Upstream corrections invalidate and recompute affected downstream state.

### 12. Controlled Scope

The target system can be ambitious without forcing the one-day MVP to implement everything.

---

# 27. The Core Mental Model

The entire project can be remembered as:

```text
SCAN
  ↓
UNDERSTAND
  ↓
DETERMINE APPLICABILITY
  ↓
VALIDATE
  ↓
PROVE WITH EVIDENCE
  ↓
INSPECTOR VERIFIES
  ↓
REVIEWER DECIDES
  ↓
REPORT
```

Or, even shorter:

> **Scan → Understand → Apply → Validate → Prove → Verify → Decide → Report**

That is the core of ComplianceScan.
