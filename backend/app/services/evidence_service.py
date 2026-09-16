"""
CompliScan LM — Evidence Service.
Handles evidence validation, SHA-256 calculation, image decoding integrity,
storage persistence, and lifecycle transitions.
"""

import io
import os
import uuid
from typing import List, Optional
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import UploadFile
from backend.app.models.evidence import EvidenceAsset
from backend.app.models.inspection import InspectionCase
from backend.app.models.user import User
from backend.app.core.config import settings
from backend.app.core.errors import EvidenceError, NotFoundError, ForbiddenError, InvalidStateError
from backend.app.core.security import compute_sha256
from backend.app.services.audit_service import AuditService
from shared.domain.constants import (
    MAX_EVIDENCE_SIZE_BYTES,
    ALLOWED_MIME_TYPES,
    ErrorCode,
)
from shared.domain.enums import EvidenceType, AuditEventType, UserRole
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
        """Process and persist an evidence asset upload."""
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

        # 9. Update inspection lifecycle state if it was in DRAFT
        if inspection.status == InspectionLifecycleState.DRAFT.value:
            inspection.status = InspectionLifecycleState.EVIDENCE_UPLOADED.value
            await AuditService.log_event(
                db=db,
                event_type=AuditEventType.STATUS_TRANSITION,
                inspection_id=inspection_id,
                actor_id=current_user.id,
                actor_role=current_user.role,
                details={"from": InspectionLifecycleState.DRAFT.value, "to": InspectionLifecycleState.EVIDENCE_UPLOADED.value},
            )

        # 10. Audit log
        await AuditService.log_event(
            db=db,
            event_type=AuditEventType.EVIDENCE_UPLOADED,
            inspection_id=inspection_id,
            actor_id=current_user.id,
            actor_role=current_user.role,
            details={
                "evidence_id": evidence_id,
                "filename": file.filename,
                "sha256_hash": sha256_hash,
                "size_bytes": file_size,
                "mime_type": file.content_type,
            },
        )

        await db.commit()
        await db.refresh(asset)
        return asset

    @staticmethod
    async def get_evidence_by_id(db: AsyncSession, evidence_id: str) -> EvidenceAsset:
        """Retrieve evidence asset by ID."""
        stmt = select(EvidenceAsset).where(EvidenceAsset.id == evidence_id)
        result = await db.execute(stmt)
        asset = result.scalar_one_or_none()
        if not asset:
            raise NotFoundError(f"Evidence {evidence_id} not found")
        return asset

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
