"""
CompliScan LM — Evidence Service.
Handles evidence validation, SHA-256 calculation, image decoding integrity,
storage persistence, lifecycle transitions, and asynchronous analysis job enqueueing.
"""

import io
import os
import uuid
from typing import List, Optional
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import UploadFile

from backend.app.models.evidence import EvidenceAsset
from backend.app.models.inspection import InspectionCase
from backend.app.models.image_quality import ImageQualityAssessment
from backend.app.models.ocr import OCRResult
from backend.app.models.structured_declaration import StructuredDeclarationResult
from backend.app.models.analysis_job import AnalysisJob
from backend.app.models.user import User
from backend.app.core.config import settings
from backend.app.core.errors import EvidenceError, NotFoundError, ForbiddenError, InvalidStateError
from backend.app.core.security import compute_sha256
from backend.app.services.audit_service import AuditService
from backend.app.services.analysis_job_service import AnalysisJobService
from shared.domain.constants import (
    MAX_EVIDENCE_SIZE_BYTES,
    ALLOWED_MIME_TYPES,
    ErrorCode,
)
from shared.domain.enums import EvidenceType, AuditEventType, UserRole, JobType
from shared.domain.states import InspectionLifecycleState, FinalizationStatus


class EvidenceService:
    @staticmethod
    def validate_file_metadata(filename: str, content_type: str, file_size: int) -> None:
        """Validate MIME type and file size bounds."""
        if content_type not in ALLOWED_MIME_TYPES:
            raise EvidenceError(
                code=ErrorCode.EVIDENCE_INVALID_MIME,
                message=f"Unsupported image type: {content_type}. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}",
                status_code=415,
            )

        if file_size > MAX_EVIDENCE_SIZE_BYTES:
            raise EvidenceError(
                code=ErrorCode.EVIDENCE_TOO_LARGE,
                message=f"File exceeds maximum allowed size of {MAX_EVIDENCE_SIZE_BYTES // (1024 * 1024)}MB",
                status_code=413,
            )

    @staticmethod
    def validate_image_decode(content: bytes) -> None:
        """Verify binary payload can be decoded as a valid image."""
        try:
            with Image.open(io.BytesIO(content)) as img:
                img.verify()
        except Exception as e:
            raise EvidenceError(
                code=ErrorCode.EVIDENCE_DECODE_FAILED,
                message=f"Invalid or corrupted image payload: {str(e)}",
                status_code=422,
            )

    @staticmethod
    async def save_evidence_file(inspection_id: str, evidence_id: str, filename: str, content: bytes) -> str:
        """Save evidence binary to persistent storage directory."""
        target_dir = os.path.join(settings.LOCAL_STORAGE_DIR, inspection_id)
        os.makedirs(target_dir, exist_ok=True)

        # Sanitize filename
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        storage_path = os.path.join(target_dir, f"{evidence_id}_{safe_filename}")

        with open(storage_path, "wb") as f:
            f.write(content)

        return storage_path

    @classmethod
    async def upload_evidence(
        cls,
        db: AsyncSession,
        inspection_id: str,
        file: UploadFile,
        evidence_type: EvidenceType,
        current_user: User,
    ) -> EvidenceAsset:
        """Process and persist an evidence asset upload, then enqueue asynchronous quality assessment."""
        # 1. Fetch inspection case
        stmt = select(InspectionCase).where(InspectionCase.id == inspection_id)
        result = await db.execute(stmt)
        inspection = result.scalar_one_or_none()

        if not inspection:
            raise NotFoundError(f"Inspection {inspection_id} not found")

        # 2. Authorization check
        if current_user.role == UserRole.INSPECTOR.value and inspection.created_by_id != current_user.id:
            raise ForbiddenError("Cannot upload evidence to another inspector's case")

        if inspection.finalization_status == FinalizationStatus.READ_ONLY.value:
            raise InvalidStateError("Cannot upload evidence to a finalized, read-only inspection")

        # 3. Read content
        content = await file.read()
        file_size = len(content)

        # 4. Validate metadata & decodability
        cls.validate_file_metadata(
            filename=file.filename or "unknown.jpg",
            content_type=file.content_type or "application/octet-stream",
            file_size=file_size,
        )
        cls.validate_image_decode(content)

        # 5. Compute SHA-256 hash for tamper detection
        sha256_hash = compute_sha256(content)

        # 6. Generate server-side Evidence ID
        evidence_id = f"EV-{uuid.uuid4().hex[:12].upper()}"

        # 7. Persist file binary
        storage_path = await cls.save_evidence_file(
            inspection_id=inspection_id,
            evidence_id=evidence_id,
            filename=file.filename or "evidence.jpg",
            content=content,
        )

        # 8. Create DB Asset
        asset = EvidenceAsset(
            id=evidence_id,
            inspection_id=inspection_id,
            evidence_type=evidence_type.value if isinstance(evidence_type, EvidenceType) else str(evidence_type),
            original_filename=file.filename or "evidence.jpg",
            mime_type=file.content_type or "image/jpeg",
            file_size_bytes=file_size,
            sha256_hash=sha256_hash,
            storage_path=storage_path,
            is_immutable=True,
            uploaded_by_id=current_user.id,
        )
        db.add(asset)

        # 9. Auto-enqueue Image Quality Assessment job
        await AnalysisJobService.enqueue_job(
            db=db,
            inspection_id=inspection_id,
            evidence_id=evidence_id,
            job_type=JobType.IMAGE_QUALITY,
        )

        # 10. Update inspection lifecycle state if it was in DRAFT
        if inspection.status == InspectionLifecycleState.DRAFT.value:
            inspection.status = InspectionLifecycleState.EVIDENCE_UPLOADED.value
            await AuditService.log_event(
                db=db,
                event_type=AuditEventType.EVIDENCE_UPLOADED,
                inspection_id=inspection_id,
                actor_id=current_user.id,
                actor_role=current_user.role,
                details={
                    "evidence_id": evidence_id,
                    "evidence_type": str(evidence_type),
                    "original_filename": file.filename,
                    "file_size_bytes": file_size,
                    "sha256_hash": sha256_hash,
                },
            )

        await db.commit()
        await db.refresh(asset)
        return asset

    @staticmethod
    async def get_evidence_by_id(
        db: AsyncSession,
        evidence_id: str,
        current_user: Optional[User] = None,
    ) -> EvidenceAsset:
        """Retrieve an EvidenceAsset by ID with authorization verification."""
        stmt = select(EvidenceAsset).where(EvidenceAsset.id == evidence_id)
        result = await db.execute(stmt)
        asset = result.scalar_one_or_none()
        if not asset:
            raise NotFoundError(f"Evidence {evidence_id} not found")

        if current_user:
            stmt_insp = select(InspectionCase).where(InspectionCase.id == asset.inspection_id)
            res_insp = await db.execute(stmt_insp)
            inspection = res_insp.scalar_one_or_none()
            if not inspection:
                raise NotFoundError(f"Inspection {asset.inspection_id} not found")

            if current_user.role == UserRole.INSPECTOR.value and inspection.created_by_id != current_user.id:
                raise ForbiddenError("Access denied: You are not authorized to download evidence for another inspector's case")

        return asset

    @staticmethod
    async def get_evidence_quality(db: AsyncSession, evidence_id: str) -> ImageQualityAssessment:
        """Retrieve the ImageQualityAssessment for a specific evidence asset."""
        stmt = select(ImageQualityAssessment).where(ImageQualityAssessment.evidence_id == evidence_id)
        result = await db.execute(stmt)
        assessment = result.scalar_one_or_none()
        if not assessment:
            raise NotFoundError(f"Quality assessment for evidence {evidence_id} not found")
        return assessment

    @staticmethod
    async def enqueue_quality_reassessment(
        db: AsyncSession,
        evidence_id: str,
        current_user: User,
    ) -> AnalysisJob:
        """
        Manually re-enqueue an asynchronous Image Quality Assessment job.
        Enforces server-side authentication, RBAC, and access verification.
        """
        stmt = select(EvidenceAsset).where(EvidenceAsset.id == evidence_id)
        result = await db.execute(stmt)
        evidence = result.scalar_one_or_none()
        if not evidence:
            raise NotFoundError(f"Evidence {evidence_id} not found")

        # Verify inspection access
        stmt_insp = select(InspectionCase).where(InspectionCase.id == evidence.inspection_id)
        res_insp = await db.execute(stmt_insp)
        inspection = res_insp.scalar_one_or_none()
        if not inspection:
            raise NotFoundError(f"Inspection {evidence.inspection_id} not found")

        if current_user.role == UserRole.INSPECTOR.value and inspection.created_by_id != current_user.id:
            raise ForbiddenError("Cannot trigger quality assessment for another inspector's case")

        job = await AnalysisJobService.enqueue_job(
            db=db,
            inspection_id=evidence.inspection_id,
            evidence_id=evidence.id,
            job_type=JobType.IMAGE_QUALITY,
            priority=1,  # User-initiated trigger gets higher priority
        )
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def delete_draft_evidence(
        db: AsyncSession,
        inspection_id: str,
        evidence_id: str,
        current_user: User,
    ) -> None:
        """Delete evidence asset if inspection is not finalized and draft rules allow."""
        stmt = select(EvidenceAsset).where(
            EvidenceAsset.id == evidence_id,
            EvidenceAsset.inspection_id == inspection_id,
        )
        result = await db.execute(stmt)
        asset = result.scalar_one_or_none()

        if not asset:
            raise NotFoundError(f"Evidence {evidence_id} not found on inspection {inspection_id}")

        stmt_insp = select(InspectionCase).where(InspectionCase.id == inspection_id)
        res_insp = await db.execute(stmt_insp)
        inspection = res_insp.scalar_one_or_none()

        if inspection and inspection.finalization_status == FinalizationStatus.READ_ONLY.value:
            raise EvidenceError(
                code=ErrorCode.EVIDENCE_IMMUTABLE,
                message="Cannot delete evidence from a finalized inspection record",
                status_code=403,
            )

        if current_user.role == UserRole.INSPECTOR.value and asset.uploaded_by_id != current_user.id:
            raise ForbiddenError("Cannot delete evidence uploaded by another user")

        # Delete physical file if exists
        if os.path.exists(asset.storage_path):
            try:
                os.remove(asset.storage_path)
            except OSError:
                pass

        await db.delete(asset)

        # Audit event
        await AuditService.log_event(
            db=db,
            event_type=AuditEventType.EVIDENCE_DELETED,
            inspection_id=inspection_id,
            actor_id=current_user.id,
            actor_role=current_user.role,
            details={"evidence_id": evidence_id, "original_filename": asset.original_filename},
        )

        await db.commit()

    @staticmethod
    async def get_evidence_ocr(
        db: AsyncSession,
        evidence_id: str,
        current_user: User,
    ) -> OCRResult:
        """
        Retrieve OCR perception result for an evidence asset with RBAC / case authorization check.
        """
        stmt = select(EvidenceAsset).where(EvidenceAsset.id == evidence_id)
        result = await db.execute(stmt)
        evidence = result.scalar_one_or_none()
        if not evidence:
            raise NotFoundError(f"Evidence {evidence_id} not found")

        stmt_insp = select(InspectionCase).where(InspectionCase.id == evidence.inspection_id)
        res_insp = await db.execute(stmt_insp)
        inspection = res_insp.scalar_one_or_none()
        if not inspection:
            raise NotFoundError(f"Inspection {evidence.inspection_id} not found")

        if current_user.role == UserRole.INSPECTOR.value and inspection.created_by_id != current_user.id:
            raise ForbiddenError("Cannot access OCR results for another inspector's case")

        stmt_ocr = select(OCRResult).where(OCRResult.evidence_id == evidence_id)
        res_ocr = await db.execute(stmt_ocr)
        ocr_result = res_ocr.scalar_one_or_none()
        if not ocr_result:
            raise NotFoundError(f"OCR result for evidence {evidence_id} not found")

        return ocr_result

    @staticmethod
    async def enqueue_ocr_processing(
        db: AsyncSession,
        evidence_id: str,
        current_user: User,
    ) -> AnalysisJob:
        """
        Manually enqueue an asynchronous PERCEPTION job for an evidence asset.
        Enforces server-side authentication, RBAC, and inspection state verification.
        """
        stmt = select(EvidenceAsset).where(EvidenceAsset.id == evidence_id)
        result = await db.execute(stmt)
        evidence = result.scalar_one_or_none()
        if not evidence:
            raise NotFoundError(f"Evidence {evidence_id} not found")

        # Verify inspection access
        stmt_insp = select(InspectionCase).where(InspectionCase.id == evidence.inspection_id)
        res_insp = await db.execute(stmt_insp)
        inspection = res_insp.scalar_one_or_none()
        if not inspection:
            raise NotFoundError(f"Inspection {evidence.inspection_id} not found")

        if current_user.role == UserRole.INSPECTOR.value and inspection.created_by_id != current_user.id:
            raise ForbiddenError("Cannot trigger OCR processing for another inspector's case")

        if inspection.finalization_status == FinalizationStatus.READ_ONLY.value:
            raise InvalidStateError("Cannot process evidence for a finalized, read-only inspection")

        job = await AnalysisJobService.enqueue_job(
            db=db,
            inspection_id=evidence.inspection_id,
            evidence_id=evidence.id,
            job_type=JobType.PERCEPTION,
            priority=1,  # User-initiated trigger gets higher priority
        )
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def get_evidence_declarations(
        db: AsyncSession,
        evidence_id: str,
        current_user: User,
    ) -> StructuredDeclarationResult:
        """
        Retrieve structured declaration extraction result for an evidence asset with RBAC / case authorization check.
        """
        stmt = select(EvidenceAsset).where(EvidenceAsset.id == evidence_id)
        result = await db.execute(stmt)
        evidence = result.scalar_one_or_none()
        if not evidence:
            raise NotFoundError(f"Evidence {evidence_id} not found")

        stmt_insp = select(InspectionCase).where(InspectionCase.id == evidence.inspection_id)
        res_insp = await db.execute(stmt_insp)
        inspection = res_insp.scalar_one_or_none()
        if not inspection:
            raise NotFoundError(f"Inspection {evidence.inspection_id} not found")

        if current_user.role == UserRole.INSPECTOR.value and inspection.created_by_id != current_user.id:
            raise ForbiddenError("Cannot access extraction results for another inspector's case")

        stmt_decl = select(StructuredDeclarationResult).where(StructuredDeclarationResult.evidence_id == evidence_id)
        res_decl = await db.execute(stmt_decl)
        decl_result = res_decl.scalar_one_or_none()
        if not decl_result:
            raise NotFoundError(f"Structured declarations for evidence {evidence_id} not found")

        return decl_result

    @staticmethod
    async def enqueue_declaration_extraction(
        db: AsyncSession,
        evidence_id: str,
        current_user: User,
    ) -> AnalysisJob:
        """
        Manually enqueue an asynchronous EXTRACTION job for an evidence asset.
        Enforces server-side authentication, RBAC, and inspection state verification.
        """
        stmt = select(EvidenceAsset).where(EvidenceAsset.id == evidence_id)
        result = await db.execute(stmt)
        evidence = result.scalar_one_or_none()
        if not evidence:
            raise NotFoundError(f"Evidence {evidence_id} not found")

        # Verify inspection access
        stmt_insp = select(InspectionCase).where(InspectionCase.id == evidence.inspection_id)
        res_insp = await db.execute(stmt_insp)
        inspection = res_insp.scalar_one_or_none()
        if not inspection:
            raise NotFoundError(f"Inspection {evidence.inspection_id} not found")

        if current_user.role == UserRole.INSPECTOR.value and inspection.created_by_id != current_user.id:
            raise ForbiddenError("Cannot trigger extraction for another inspector's case")

        if inspection.finalization_status == FinalizationStatus.READ_ONLY.value:
            raise InvalidStateError("Cannot process evidence for a finalized, read-only inspection")

        job = await AnalysisJobService.enqueue_job(
            db=db,
            inspection_id=evidence.inspection_id,
            evidence_id=evidence.id,
            job_type=JobType.EXTRACTION,
            priority=1,  # User-initiated trigger gets higher priority
        )
        await db.commit()
        await db.refresh(job)
        return job
