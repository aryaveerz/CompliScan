# COMPLISCAN LM — PHASE 7.0 EVIDENCE STORAGE ARCHITECTURE
## Multi-Node Object Storage, Storage Abstraction, Retention Policy & Cryptographic Grounding

**Audit Date:** 2026-09-20  
**Status:** RECONCILED BLUEPRINT — AUDIT & PLANNING ONLY (ZERO CODE MUTATIONS)

---

## 1. Storage Architecture Overview

In a distributed multi-container cloud deployment (Vercel + Render Web Service + Render Worker), instances must not rely on ephemeral local disks for evidence assets. CompliScan LM introduces a formal `StorageService` abstraction delegating file persistence to **Supabase Storage** in production while retaining `LocalStorageBackend` for offline testing.

```
                    ┌──────────────────────────────────────────┐
                    │              StorageService              │
                    │   upload() | download() | delete()       │
                    └────────────────────┬─────────────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
  ┌─────────────────────────────┐                 ┌─────────────────────────────┐
  │    LocalStorageBackend      │                 │    SupabaseStorageBackend   │
  │  (Used in Dev & Test)       │                 │  (Used in Production)       │
  │  Path: backend/uploads/     │                 │  Bucket: compliscan-evidence│
  │  N-Node Accessible: NO      │                 │  N-Node Accessible: YES     │
  └─────────────────────────────┘                 └─────────────────────────────┘
```

- **`CURRENT — VERIFIED` State:** `EvidenceService` currently saves files directly to local disk `backend/uploads/{inspection_id}/{evidence_id}_{safe_filename}`.
- **`TARGET — PROPOSED` State:** `EvidenceService` delegates to `StorageService` using `SupabaseStorageBackend` when `ENVIRONMENT == "production"` or `STORAGE_BACKEND == "supabase"`.

---

## 2. Object Naming & Path Hierarchy

Production evidence objects in Supabase Storage must be structured strictly around stable system identifiers, never mutable product names or officer names:

```
Bucket: compliscan-evidence
  └── inspections/
        └── {inspection_id}/
              └── {evidence_id}/
                    └── original/
                          └── {safe_filename}
```

- **`{inspection_id}`**: Server-generated inspection UUID (`INS-XXXXXXXXXXXX`).
- **`{evidence_id}`**: Server-generated evidence asset UUID (`EV-XXXXXXXXXXXX`).
- **`{safe_filename}`**: Sanitized original filename containing only `[a-zA-Z0-9._-]`.

---

## 3. Storage Namespace Separation

To maintain strict boundaries between raw physical evidence, derived perception assets, and final statutory reports, three distinct logical storage namespaces are established:

1. **`compliscan-evidence/`** (Private Bucket): Authoritative original photographic evidence binaries ingested from inspectors/devices. Strict append-only post-finalization.
2. **`compliscan-reports/`** (Private Bucket): Canonical generated PDF and DOCX statutory dossiers sealed to a specific `FinalAuditRecord` (`inspections/{id}/{far_id}/report.pdf`).
3. **`compliscan-derived/`** (Private Bucket / Optional): Annotated images, IQA visual crops, and bounding box visualizations (if persisted).

---

## 4. Formal Evidence Deletion & Versioning Policy

| Case Lifecycle State | Evidence Asset Operation | Allowed Actor | System Behavior & Invariants | Audit Event Logged |
|---|---|---|---|---|
| **`DRAFT`** | Delete Draft Evidence | Creating Inspector | File deleted from Supabase Storage; `evidence_assets` DB record removed. Permitted only if case is unfinalized. | `EVIDENCE_DELETED` |
| **`DRAFT`** | Replace / Re-upload | Creating Inspector | Old evidence deleted or re-uploaded as distinct `EvidenceAsset` with fresh UUID and SHA-256. | `EVIDENCE_UPLOADED` |
| **`SUBMITTED_FOR_REVIEW`** | Delete / Mutate Evidence | **NONE** | **BLOCKED (HTTP 409 Conflict)** — Case is under formal review; evidence is locked. | Mutation refusal logged |
| **`FINALIZED` (`READ_ONLY`)** | Delete / Mutate Evidence | **NONE** | **STRICTLY FORBIDDEN (HTTP 403 Forbidden)** — Case is legally sealed; all evidence is permanently immutable. | Mutation refusal logged |
| **Statutory Retention** | Permanent Storage | Compliance Officer | Original evidence retained according to departmental archiving rules. (*Legal duration: POLICY DECISION REQUIRED*). | `EVIDENCE_ARCHIVED` |

---

## 5. Cryptographic Grounding & Anti-Tampering Chain

1. **Ingestion SHA-256:** Computed immediately on incoming binary stream before upload (`EvidenceAsset.sha256_hash`).
2. **Storage Integrity Check:** When the background worker downloads bytes for perception, SHA-256 is re-verified against `EvidenceAsset.sha256_hash`. If a mismatch occurs, the job fails with `INTEGRITY_MISMATCH`.
3. **Sealed Snapshot:** `FinalAuditRecord.evidence_snapshot` permanently records the original filename, size, MIME type, and SHA-256 hash.
4. **FAR Integrity Hash:** Canonical JSON serialization of the FAR is hashed with SHA-256 (`FinalAuditRecord.integrity_hash`).

---

## 6. Truthful Handling of Missing Evidence in Reports

If an evidence asset's binary cannot be retrieved from storage during statutory report generation:
- **Zero Test Folder Fallback:** The report generator will **NEVER** search `Test_Images/Peanut_Butter` or `Test_Images/Juice`.
- **Truthful Statutory Representation:** The report renders:
  ```
  Figure 1 — Evidence Asset ID: EV-58A5A902 (label_front.jpg)
  Expected SHA-256: 7987f3a2fcc2601d82ebb79504ecbaee6f3c5964a31f63607728396fcda45a73 | Size: 1,275 KB
  [Evidence Asset Metadata Available — Binary Retrieval Status: NOT AVAILABLE | Integrity Verification: NOT PERFORMED]
  ```
