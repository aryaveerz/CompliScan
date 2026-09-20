"""
CompliScan LM — Analysis Job Queue Service.
Manages durable asynchronous job enqueueing, atomic leasing, retry handling, and execution.
"""

from datetime import datetime, timezone, timedelta
import os
import uuid
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from backend.app.core.config import settings
from backend.app.core.errors import NotFoundError, AnalysisError
from backend.app.models.analysis_job import AnalysisJob
from backend.app.models.evidence import EvidenceAsset
from backend.app.models.inspection import InspectionCase
from backend.app.models.image_quality import ImageQualityAssessment
from backend.app.models.ocr import OCRResult
from backend.app.models.structured_declaration import StructuredDeclarationResult
from backend.app.services.image_quality_service import ImageQualityService
from backend.app.services.ocr_service import OCRService
from backend.app.services.extraction_service import ExtractionService
from backend.app.services.audit_service import AuditService
from backend.app.core.security import compute_sha256
from backend.app.services.storage_service import get_storage_service
from shared.domain.constants import ErrorCode
from shared.domain.enums import JobType, JobStatus, AuditEventType, ImageQualityStatus
from shared.domain.states import ProcessingState


class AnalysisJobService:
    """
    Durable PostgreSQL / SQLite backed Analysis Job Service.
    """

    @classmethod
    async def _get_and_verify_evidence_binary(
        cls,
        db: AsyncSession,
        evidence: EvidenceAsset,
        job_id: str,
    ) -> bytes:
        """
        Download evidence binary through StorageService and verify SHA-256 integrity against EvidenceAsset.sha256_hash.
        If SHA-256 mismatches:
            - logs AuditEventType.INTEGRITY_MISMATCH_ERROR
            - raises AnalysisError with code INTEGRITY_MISMATCH_ERROR
        """
        storage_service = get_storage_service()
        bucket = "compliscan-evidence"
        path = evidence.storage_path
        if path.startswith("compliscan-evidence/"):
            path = path[len("compliscan-evidence/"):]

        try:
            content = await storage_service.download_file(bucket=bucket, path=path)
        except NotFoundError:
            if os.path.exists(evidence.storage_path):
                with open(evidence.storage_path, "rb") as f:
                    content = f.read()
            else:
                raise FileNotFoundError(f"Evidence binary missing at storage path: {evidence.storage_path}")

        # Compute SHA-256
        computed_sha256 = compute_sha256(content)

        # Compare with EvidenceAsset.sha256_hash
        if computed_sha256 != evidence.sha256_hash:
            # Audit log security event
            await AuditService.log_event(
                db=db,
                event_type=AuditEventType.INTEGRITY_MISMATCH_ERROR,
                inspection_id=evidence.inspection_id,
                actor_id=job_id,
                actor_role="SYSTEM_WORKER",
                details={
                    "evidence_id": evidence.id,
                    "expected_sha256": evidence.sha256_hash,
                    "computed_sha256": computed_sha256,
                    "message": "CRITICAL: Cryptographic SHA-256 mismatch detected during worker evidence retrieval.",
                },
            )
            raise AnalysisError(
                code=ErrorCode.INTEGRITY_MISMATCH_ERROR,
                message=f"INTEGRITY_MISMATCH_ERROR: Evidence {evidence.id} binary payload corrupted or modified. Expected {evidence.sha256_hash}, computed {computed_sha256}",
                status_code=400,
            )

        return content

    @classmethod
    async def enqueue_job(

        cls,
        db: AsyncSession,
        inspection_id: str,
        job_type: JobType,
        evidence_id: Optional[str] = None,
        payload: Optional[dict] = None,
        priority: int = 0,
    ) -> AnalysisJob:
        """
        Enqueue a new analysis job idempotently.
        If a PENDING or RUNNING job of the same type already exists for the target evidence, returns it.
        """
        now = datetime.now(timezone.utc)
        job_type_val = job_type.value if hasattr(job_type, "value") else str(job_type)

        # Idempotence check: check if an active job of same type already exists
        filter_clauses = [
            AnalysisJob.inspection_id == inspection_id,
            AnalysisJob.job_type == job_type_val,
            AnalysisJob.status.in_([JobStatus.PENDING.value, JobStatus.CLAIMED.value, JobStatus.RUNNING.value]),
        ]
        if evidence_id:
            filter_clauses.append(AnalysisJob.evidence_id == evidence_id)
        else:
            filter_clauses.append(AnalysisJob.evidence_id.is_(None))

        stmt = select(AnalysisJob).where(and_(*filter_clauses))
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            return existing

        job_id = f"JOB-{uuid.uuid4().hex[:12].upper()}"
        job = AnalysisJob(
            id=job_id,
            inspection_id=inspection_id,
            evidence_id=evidence_id,
            job_type=job_type_val,
            status=JobStatus.PENDING.value,
            priority=priority,
            max_attempts=settings.WORKER_MAX_JOB_ATTEMPTS,
            payload=payload,
            created_at=now,
            updated_at=now,
        )
        db.add(job)
        await db.flush()
        return job

    @classmethod
    async def claim_next_job(
        cls,
        db: AsyncSession,
        worker_id: str,
        lease_seconds: Optional[int] = None,
    ) -> Optional[AnalysisJob]:
        """
        Atomically claim the next eligible job.
        Considers PENDING jobs and expired lease jobs (FAILED/RUNNING where lease expired and attempts < max_attempts).
        """
        lease_sec = lease_seconds or settings.WORKER_LEASE_SECONDS
        now = datetime.now(timezone.utc)
        lease_cutoff = now

        # Find eligible job:
        # 1. PENDING jobs
        # 2. RUNNING / CLAIMED jobs where lease_expires_at has passed and attempts < max_attempts
        stmt = (
            select(AnalysisJob)
            .where(
                or_(
                    AnalysisJob.status == JobStatus.PENDING.value,
                    and_(
                        AnalysisJob.status.in_([JobStatus.CLAIMED.value, JobStatus.RUNNING.value]),
                        AnalysisJob.lease_expires_at < lease_cutoff,
                        AnalysisJob.attempts < AnalysisJob.max_attempts,
                    ),
                )
            )
            .order_by(AnalysisJob.priority.desc(), AnalysisJob.created_at.asc())
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        result = await db.execute(stmt)
        job = result.scalar_one_or_none()

        if not job:
            return None

        # Atomically claim
        job.status = JobStatus.RUNNING.value
        job.worker_id = worker_id
        job.lease_expires_at = now + timedelta(seconds=lease_sec)
        job.attempts += 1
        job.started_at = now
        job.updated_at = now

        await db.flush()
        return job

    @classmethod
    async def execute_job(
        cls,
        db: AsyncSession,
        job: AnalysisJob,
    ) -> None:
        """
        Execute a claimed analysis job with full failure isolation and idempotence.
        """
        now = datetime.now(timezone.utc)
        try:
            if job.job_type == JobType.IMAGE_QUALITY.value:
                await cls._execute_image_quality(db, job)
            elif job.job_type == JobType.PERCEPTION.value:
                await cls._execute_ocr(db, job)
            elif job.job_type == JobType.EXTRACTION.value:
                await cls._execute_extraction(db, job)
            elif job.job_type == JobType.EVALUATION.value:
                await cls._execute_compliance_evaluation(db, job)
            else:
                raise NotImplementedError(f"Job type {job.job_type} not implemented")

            job.status = JobStatus.COMPLETED.value
            job.completed_at = datetime.now(timezone.utc)
            job.error_message = None
            job.updated_at = datetime.now(timezone.utc)

        except Exception as e:
            job.updated_at = datetime.now(timezone.utc)
            job.error_message = str(e)
            if job.attempts >= job.max_attempts:
                job.status = JobStatus.FAILED.value
            else:
                # Release for retry
                job.status = JobStatus.PENDING.value
                job.lease_expires_at = None

        await db.flush()


    @classmethod
    async def _execute_image_quality(
        cls,
        db: AsyncSession,
        job: AnalysisJob,
    ) -> None:
        """
        Execute Image Quality Assessment for an evidence asset.
        If quality passes as USABLE, auto-enqueues downstream PERCEPTION job idempotently.
        """
        if not job.evidence_id:
            raise ValueError(f"Job {job.id} missing required evidence_id")

        stmt = select(EvidenceAsset).where(EvidenceAsset.id == job.evidence_id)
        evidence = (await db.execute(stmt)).scalar_one_or_none()

        if not evidence:
            raise NotFoundError(f"Evidence asset {job.evidence_id} not found")

        # Read original evidence binary with SHA-256 integrity verification
        content = await cls._get_and_verify_evidence_binary(db, evidence, job.id)


        # Perform deterministic assessment
        result = ImageQualityService.assess_image_bytes(
            content=content,
            mime_type=evidence.mime_type,
        )

        # Persist quality assessment idempotently
        assessment = await ImageQualityService.persist_assessment(
            db=db,
            evidence=evidence,
            result=result,
        )

        # Log audit event upon successful completion
        await AuditService.log_event(
            db=db,
            event_type=AuditEventType.IMAGE_QUALITY_ASSESSED,
            inspection_id=job.inspection_id,
            actor_id=job.worker_id or "SYSTEM_WORKER",
            actor_role="SYSTEM",
            details={
                "evidence_id": evidence.id,
                "quality_status": assessment.quality_status,
                "assessment_version": assessment.assessment_version,
                "reason_codes": assessment.reason_codes,
                "width": assessment.width,
                "height": assessment.height,
                "sharpness_score": assessment.sharpness_score,
            },
        )

        # Auto-enqueue PERCEPTION job if quality is USABLE
        if assessment.quality_status == ImageQualityStatus.USABLE.value:
            await cls.enqueue_job(
                db=db,
                inspection_id=job.inspection_id,
                job_type=JobType.PERCEPTION,
                evidence_id=evidence.id,
                priority=job.priority,
            )

    @classmethod
    async def _execute_ocr(
        cls,
        db: AsyncSession,
        job: AnalysisJob,
    ) -> None:
        """
        Execute PaddleOCR PP-OCRv4 perception pipeline for an evidence asset.
        Gated by ImageQualityAssessment suitability screening.
        """
        if not job.evidence_id:
            raise ValueError(f"Job {job.id} missing required evidence_id")

        stmt = select(EvidenceAsset).where(EvidenceAsset.id == job.evidence_id)
        evidence = (await db.execute(stmt)).scalar_one_or_none()

        if not evidence:
            raise NotFoundError(f"Evidence asset {job.evidence_id} not found")

        # 1. Image Quality Gating Check
        stmt_qual = select(ImageQualityAssessment).where(ImageQualityAssessment.evidence_id == evidence.id)
        quality = (await db.execute(stmt_qual)).scalar_one_or_none()

        if not quality or quality.quality_status != ImageQualityStatus.USABLE.value:
            block_reason = quality.quality_status if quality else "QUALITY_ASSESSMENT_MISSING"
            ocr_record = await OCRService.persist_blocked_result(
                db=db,
                evidence=evidence,
                block_reason=block_reason,
            )
            await AuditService.log_event(
                db=db,
                event_type=AuditEventType.OCR_PROCESSED,
                inspection_id=job.inspection_id,
                actor_id=job.worker_id or "SYSTEM_WORKER",
                actor_role="SYSTEM",
                details={
                    "evidence_id": evidence.id,
                    "status": "BLOCKED",
                    "block_reason": block_reason,
                    "ocr_engine": ocr_record.ocr_engine,
                    "ocr_engine_version": ocr_record.ocr_engine_version,
                },
            )
            # Enqueue extraction to propagate blocked perception state deterministically
            await cls.enqueue_job(
                db=db,
                inspection_id=job.inspection_id,
                job_type=JobType.EXTRACTION,
                evidence_id=evidence.id,
                priority=job.priority,
            )
            return

        # 2. Read original evidence binary with SHA-256 integrity verification
        content = await cls._get_and_verify_evidence_binary(db, evidence, job.id)


        # 3. Execute OCR perception pipeline
        raw_result = OCRService.process_image_bytes(
            content=content,
            mime_type=evidence.mime_type,
        )

        # 4. Persist OCR tokens idempotently
        ocr_record = await OCRService.persist_ocr_result(
            db=db,
            evidence=evidence,
            raw_result=raw_result,
        )

        # 5. Log audit event
        await AuditService.log_event(
            db=db,
            event_type=AuditEventType.OCR_PROCESSED,
            inspection_id=job.inspection_id,
            actor_id=job.worker_id or "SYSTEM_WORKER",
            actor_role="SYSTEM",
            details={
                "evidence_id": evidence.id,
                "status": "COMPLETED",
                "total_tokens": ocr_record.total_tokens,
                "ocr_engine": ocr_record.ocr_engine,
                "ocr_engine_version": ocr_record.ocr_engine_version,
                "processing_version": ocr_record.processing_version,
            },
        )

        # 6. Auto-enqueue semantic extraction job
        await cls.enqueue_job(
            db=db,
            inspection_id=job.inspection_id,
            job_type=JobType.EXTRACTION,
            evidence_id=evidence.id,
            priority=job.priority,
        )

    @classmethod
    async def _execute_extraction(
        cls,
        db: AsyncSession,
        job: AnalysisJob,
    ) -> None:
        """
        Execute Gemini 2.5 Flash semantic extraction of packaged-commodity declarations.
        Gated by upstream OCR token presence (zero-token OCR results bypass LLM and persist BLOCKED).
        """
        if not job.evidence_id:
            raise ValueError(f"Job {job.id} missing required evidence_id")

        stmt = select(EvidenceAsset).where(EvidenceAsset.id == job.evidence_id)
        evidence = (await db.execute(stmt)).scalar_one_or_none()

        if not evidence:
            raise NotFoundError(f"Evidence asset {job.evidence_id} not found")

        # 1. Fetch latest OCR result for evidence
        stmt_ocr = select(OCRResult).where(OCRResult.evidence_id == evidence.id)
        ocr_result = (await db.execute(stmt_ocr)).scalar_one_or_none()

        # 2. Check for zero-token or blocked OCR conditions
        if not ocr_result or ocr_result.processing_blocked or ocr_result.total_tokens == 0:
            block_reason = "NO_OCR_TOKENS_OBSERVED" if (ocr_result and ocr_result.total_tokens == 0) else (
                ocr_result.block_reason if ocr_result else "OCR_RESULT_MISSING"
            )
            decl_record = await ExtractionService.persist_blocked_result(
                db=db,
                evidence=evidence,
                ocr_result=ocr_result if ocr_result else OCRResult(id="NONE"),
                block_reason=block_reason,
            )
            await AuditService.log_event(
                db=db,
                event_type=AuditEventType.DECLARATIONS_EXTRACTED,
                inspection_id=job.inspection_id,
                actor_id=job.worker_id or "SYSTEM_WORKER",
                actor_role="SYSTEM",
                details={
                    "evidence_id": evidence.id,
                    "status": "BLOCKED",
                    "block_reason": block_reason,
                    "model_name": decl_record.model_name,
                    "prompt_version": decl_record.prompt_version,
                    "extraction_version": decl_record.extraction_version,
                },
            )
            return

        # 3. Call Gemini extraction service
        declarations = ExtractionService.call_gemini_extraction(
            tokens=ocr_result.tokens or [],
        )

        # 4. Persist structured declaration record idempotently
        decl_record = await ExtractionService.persist_declaration_result(
            db=db,
            evidence=evidence,
            ocr_result=ocr_result,
            declarations=declarations,
        )

        # 5. Log audit event
        await AuditService.log_event(
            db=db,
            event_type=AuditEventType.DECLARATIONS_EXTRACTED,
            inspection_id=job.inspection_id,
            actor_id=job.worker_id or "SYSTEM_WORKER",
            actor_role="SYSTEM",
            details={
                "evidence_id": evidence.id,
                "status": "COMPLETED",
                "ocr_result_id": ocr_result.id,
                "model_name": decl_record.model_name,
                "prompt_version": decl_record.prompt_version,
                "extraction_version": decl_record.extraction_version,
            },
        )

    @classmethod
    async def _execute_compliance_evaluation(
        cls,
        db: AsyncSession,
        job: AnalysisJob,
    ) -> None:
        """
        Executes Phase 3 deterministic compliance evaluation for an inspection case.
        """
        from backend.app.services.compliance_service import ComplianceEvaluationService
        await ComplianceEvaluationService.evaluate_inspection_compliance(
            db=db,
            inspection_id=job.inspection_id,
            actor_id=job.worker_id or "SYSTEM_WORKER",
        )

    @classmethod
    async def run_pending_jobs_inline(
        cls,
        db: AsyncSession,
        worker_id: str = "inline-test-worker",
    ) -> int:
        """
        Helper method to process all pending jobs synchronously.
        Useful for automated tests and single-worker flush passes.
        """
        count = 0
        while True:
            job = await cls.claim_next_job(db, worker_id=worker_id)
            if not job:
                break
            await cls.execute_job(db, job)
            await db.commit()
            count += 1
        return count
