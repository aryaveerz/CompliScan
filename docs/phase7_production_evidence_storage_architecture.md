# Phase 7.1 — Production Evidence & Artifact Storage Architecture

**Document ID:** `ARCH-2026-STORE-001`  
**Date:** September 20, 2026  
**Status:** DRAFT (PLANNING ONLY — NO MUTATIONS EXECUTED)  
**Target Infrastructure:** Supabase Storage, Render Ephemeral Worker, Supabase PostgreSQL

---

## 1. Executive Summary

CompliScan LM operates in a statutory legal metrology domain under the Legal Metrology (Packaged Commodities) Rules, 2011. Evidence collected during inspections constitutes regulatory records subject to strict data integrity, audit attribution, and anti-tampering requirements.

In the target cloud deployment:
- **Frontend (Vercel):** Transmits evidence binaries to the backend API or direct-to-storage signed upload endpoints.
- **Backend API & Background Worker (Render):** Execute OCR, Gemini perception, and deterministic compliance analysis. Render local container disks are ephemeral; no persistent evidence may reside on Render local filesystems.
- **Persistent Object Storage (Supabase Storage):** Authoritative, durable store for all raw evidence binaries, derived artifacts, and generated audit reports.
- **Database (Supabase PostgreSQL):** Authoritative store for metadata, cryptographic hashes, OCR tokens, structured declarations, findings, adjudications, and FinalAuditRecords.

---

## 2. Evidence Storage Lifecycle

```
[Inspector Device / Camera]
       │
       ▼ (HTTPS Upload)
[FastAPI /api/v1/evidence/upload] ──► [Compute SHA-256 & Validate MIME/Size]
       │                                              │
       ├──────────────────────────────────────────────┘
       ▼
[Supabase Storage: compliscan-evidence] 
  Path: inspections/{inspection_id}/{evidence_id}/original/{safe_filename}
       │
       ▼ (Database Metadata Insert)
[PostgreSQL: EvidenceAsset Record]
  - id: evidence_id
  - inspection_id: inspection_id
  - storage_path: "inspections/{inspection_id}/{evidence_id}/original/{safe_filename}"
  - sha256_hash: computed_digest
  - status: UPLOADED
       │
       ▼ (Enqueue Analysis Job)
[Worker Node (Render)]
  1. Download binary via Storage Service
  2. Compute SHA-256 & Verify Against Database Record
  3. Execute RapidOCR / Gemini Extraction
  4. Persist OCR Tokens & Structured Declarations in PostgreSQL
  5. Upload Derived Crops/Canvas Overlays to `compliscan-derived`
  6. Clean up temporary local worker scratch disk
       │
       ▼ (Adjudication & Finalization)
[Reviewer Adjudication] ──► [Generate FinalAuditRecord (PostgreSQL)]
                                       │
                                       ▼ (Deterministic Report Generation)
                            [PDFReportService / DOCXReportService]
                                       │
                                       ▼ (Compute Report SHA-256)
                            [Supabase Storage: compliscan-reports]
                              Path: inspections/{inspection_id}/{far_id}/report.pdf
                              Path: inspections/{inspection_id}/{far_id}/report.docx
```

---

## 3. Logical Storage Bucket & Namespace Architecture

All buckets are configured as **PRIVATE** (No public bucket access permitted).

### 3.1 Primary Buckets

| Bucket Name | Purpose | Content Type | Immutability | Access Control |
|---|---|---|---|---|
| `compliscan-evidence` | Original raw packaging photos, PDFs, camera captures | Raw binaries (`image/jpeg`, `image/png`, `application/pdf`) | **IMMUTABLE** (WORM - Write Once, Read Many) | Inspector (Upload own case), Reviewer (Read), Worker (Read) |
| `compliscan-derived` | Cropped bounding boxes, token masks, canvas overlay renders | Image slices, normalized tokens | **IMMUTABLE** (Per analysis job run) | Worker (Write), Inspector/Reviewer (Read) |
| `compliscan-reports` | Generated Final Audit Reports (FAR) in PDF & DOCX | `application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | **IMMUTABLE** (Locked upon FAR finalization) | Reviewer/Inspector (Read via signed URLs) |
| `compliscan-audit` | Cryptographic manifests, daily audit ledger snapshots | JSON, CSV | **APPEND-ONLY** | System / Administrator only |

### 3.2 Canonical Object Path Hierarchy

```
compliscan-evidence/
└── inspections/
    └── {inspection_id}/
        └── {evidence_id}/
            └── original/
                └── {safe_filename}

compliscan-derived/
└── inspections/
    └── {inspection_id}/
        └── {evidence_id}/
            └── jobs/
                └── {job_id}/
                    ├── token_crops/
                    │   ├── token_001.jpg
                    │   └── token_002.jpg
                    └── canvas_overlay.png

compliscan-reports/
└── inspections/
    └── {inspection_id}/
        └── {far_id}/
            ├── report.pdf
            ├── report.docx
            └── manifest.json
```

---

## 4. Evidence Identity & Data Grounding

Every persistent evidence object must maintain a complete provenance tuple in PostgreSQL:

| Property | Database Column | Description |
|---|---|---|
| `evidence_id` | `EvidenceAsset.id` | Global UUID / prefixed ID (e.g. `EV-F4A1FCC01`) |
| `inspection_id` | `EvidenceAsset.inspection_id` | Foreign key to `InspectionCase.id` |
| `original_filename` | `EvidenceAsset.original_filename` | Original client file name (for user display) |
| `safe_filename` | Stored in path | Sanitized ASCII alphanumeric filename |
| `mime_type` | `EvidenceAsset.mime_type` | Validated MIME type (`image/jpeg`, `image/png`, `image/webp`, `application/pdf`) |
| `file_size_bytes` | `EvidenceAsset.file_size_bytes` | Byte size of raw object |
| `sha256_hash` | `EvidenceAsset.sha256_hash` | Lowercase 64-character hex SHA-256 digest of exact uploaded bytes |
| `storage_backend` | Configuration | `supabase_storage` (production) / `local_storage` (development/tests) |
| `storage_path` | `EvidenceAsset.storage_path` | Bucket-relative canonical path |
| `uploaded_by_id` | `EvidenceAsset.uploaded_by_id` | Foreign key to `User.id` (attributing inspector) |
| `created_at` | `EvidenceAsset.created_at` | UTC timestamp of ingestion |

---

## 5. End-to-End Cryptographic Anti-Tampering Chain

CompliScan LM implements a **tamper-evident, integrity-verifiable, provenance-traceable** architecture:

1. **Ingestion Hash:**
   - Raw bytes streamed to SHA-256 hasher during upload.
   - `EvidenceAsset.sha256_hash = HASH(raw_bytes)`.
2. **Pre-Processing Verification:**
   - Worker retrieves object bytes from Supabase Storage.
   - Computes `current_hash = HASH(downloaded_bytes)`.
   - If `current_hash != EvidenceAsset.sha256_hash`, worker immediately marks job `FAILED` with `INTEGRITY_MISMATCH_ERROR`, creates an `AuditEvent`, and aborts execution.
3. **Structured Declaration Linkage:**
   - `StructuredDeclarationResult.evidence_id` links directly to verified `EvidenceAsset`.
   - Source token indices reference exact OCR bounding boxes.
4. **Deterministic Compliance Findings:**
   - `ComplianceFinding.evidence_id` links findings to the specific evidence asset evaluated.
5. **FinalAuditRecord (FAR) Immutability:**
   - `FinalAuditRecord.evidence_summary` embeds the SHA-256 hashes of all constituent evidence assets.
   - `FinalAuditRecord.record_hash` computes a SHA-256 digest over the canonical JSON representation of the entire FAR state.
6. **Report Parity & Audit Trail:**
   - PDF and DOCX reports generated strictly from the immutable FAR data model.
   - The generated PDF SHA-256 and DOCX SHA-256 are logged to the `AuditEvent` ledger upon generation.

> [!IMPORTANT]
> The system claims **tamper-evident** and **integrity-verifiable** guarantees based on SHA-256 hashing and append-only audit trails. It does not claim asymmetric digital non-repudiation unless certified X.509 PKI digital signatures are configured.

---

## 6. Access Control & Security Model

1. **Private Buckets & Signed URLs:**
   - Buckets are never exposed publicly.
   - File downloads occur via short-lived (e.g. 5-minute TTL) Supabase Storage Signed URLs generated on-demand by the backend API.
2. **Role-Based Authorization (RBAC):**
   - **Inspectors:** Can upload evidence only to `InspectionCase` records they own (`created_by_id == current_user.id`). Can download evidence only for their own cases. Cross-case access returns `403 Forbidden`.
   - **Reviewers:** Read-only access to all evidence across all inspection cases submitted for review.
   - **Worker Service:** Backend service account with bucket read/write permissions via `SUPABASE_SERVICE_ROLE_KEY`.
3. **Download IDOR Protection:**
   - Implemented and verified in `backend/app/services/evidence_service.py::get_evidence_by_id()`.

---

## 7. Storage Service Abstraction (Local vs. Cloud)

Production code interacts with storage strictly through an abstract interface:

```python
class BaseStorageService(ABC):
    @abstractmethod
    async def upload_file(self, bucket: str, path: str, content: bytes, content_type: str) -> str: ...
    
    @abstractmethod
    async def download_file(self, bucket: str, path: str) -> bytes: ...
    
    @abstractmethod
    async def generate_signed_url(self, bucket: str, path: str, expires_in: int = 300) -> str: ...
    
    @abstractmethod
    async def delete_file(self, bucket: str, path: str) -> bool: ...
```

- **`LocalStorageService`:** Used in development, CI/CD, and offline test suite (`backend/tests/`). Reads/writes to local mock storage directory (`./storage_test/`).
- **`SupabaseStorageService`:** Used in production on Render. Communicates via HTTP with Supabase Storage REST API using service role credentials.

---

## 8. Retention & Deletion Policy Matrix

| Artifact Category | Lifecycle Phase | Mutable? | Deletable? | Permitted Actor | Trigger / Policy | Audit Event Logged? |
|---|---|---|---|---|---|---|
| **Original Evidence** | Unfinalized (DRAFT) | No | Yes | Owner Inspector | Inspector removes incorrect photo before submission | `EVIDENCE_DELETED` |
| **Original Evidence** | Finalized (FAR Created) | **No** | **No** | None | Immutable statutory legal record | Attempt blocked (403) |
| **Derived OCR Slices** | Unfinalized | Yes (on rerun) | Yes | Background Worker | Re-extraction job overwrites derived cache | `DERIVED_ARTIFACT_UPDATED` |
| **Derived OCR Slices** | Finalized | **No** | **No** | None | Frozen with FAR snapshot | Attempt blocked (403) |
| **Compliance Findings** | Unfinalized | Yes (on rerun) | Yes | Compliance Engine | Re-evaluation updates finding rows | `COMPLIANCE_EVALUATED` |
| **Compliance Findings** | Finalized | **No** | **No** | None | Read-only frozen state | Attempt blocked (403) |
| **FinalAuditRecord (FAR)** | Finalized | **No** | **No** | None | Permanent legal archive | Modification blocked |
| **Generated Reports (PDF/DOCX)** | Finalized | **No** | **No** | None | Immutable output artifacts | `REPORT_DOWNLOADED` |
| **Audit Events** | All Phases | **No** | **No** | None (Append-Only) | Permanent tamper-evident log | N/A |
| **Local Worker Temp Files** | During Processing | Yes | Yes (Auto) | Background Worker | Cleaned up in `finally:` block | No |

---

## 9. Failure Modes & Resilience Engineering

| Failure Scenario | Detection Mechanism | System State | User-Facing Notification | Recovery Procedure |
|---|---|---|---|---|
| **Upload succeeds, DB insert fails** | FastAPI exception handler catches DB error | Storage object orphan | `"Failed to register evidence. Please re-upload."` | Storage cleanup worker deletes unindexed storage objects older than 1 hour |
| **DB insert succeeds, storage fails** | `BaseStorageService` raises `StorageError` | Transaction rolls back | `"Storage upload failed. Please try again."` | No orphan database record created |
| **SHA-256 hash mismatch during retrieval** | Worker computes hash != `sha256_hash` | Job marked `FAILED` | `"Evidence binary integrity error detected."` | Logs critical `SECURITY_ALERT` audit event; flags for manual review |
| **Supabase Storage API outage** | HTTP 503 / timeout | Job remains `PENDING` | `"Storage temporarily unavailable. Retrying..."` | Exponential backoff retry in worker queue (up to 5 attempts) |
| **Render container restart during processing** | Job lease expires (`lease_expires_at < now`) | Job `PENDING` | `"Processing re-enqueued."` | `AnalysisJobService` recovers expired leases automatically |
| **Missing evidence during report generation** | Storage returns 404 | Report builder flags `NOT AVAILABLE` | Section rendered with `"Evidence asset not available"` | Zero substitution of fallback images; integrity status logged |
