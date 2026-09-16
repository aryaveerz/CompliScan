"""
CompliScan LM — Evidence Router.
"""

import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.evidence import EvidenceResponse
from backend.app.services.evidence_service import EvidenceService
from backend.app.api.deps import get_current_user, require_role
from backend.app.core.errors import NotFoundError
from shared.domain.enums import EvidenceType, UserRole

router = APIRouter(tags=["Evidence"])


@router.post("/inspections/{inspection_id}/evidence", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    inspection_id: str,
    file: UploadFile = File(...),
    evidence_type: EvidenceType = Form(EvidenceType.PRIMARY),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.INSPECTOR)),
):
    """
    Upload evidence artifact (package photograph / label image).
    Performs MIME validation, file size checks, image decoding integrity,
    SHA-256 computation, and updates inspection lifecycle state.
    """
    asset = await EvidenceService.upload_evidence(
        db=db,
        inspection_id=inspection_id,
        file=file,
        evidence_type=evidence_type,
        current_user=current_user,
    )
    return EvidenceResponse.model_validate(asset)


@router.delete("/inspections/{inspection_id}/evidence/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evidence(
    inspection_id: str,
    evidence_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.INSPECTOR)),
):
    """
    Delete draft evidence asset before immutable finalization.
    """
    await EvidenceService.delete_draft_evidence(
        db=db,
        inspection_id=inspection_id,
        evidence_id=evidence_id,
        current_user=current_user,
    )
    return None


@router.get("/evidence/{evidence_id}/download")
async def download_evidence(
    evidence_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Download / view the stored original evidence file.
    """
    asset = await EvidenceService.get_evidence_by_id(db, evidence_id)
    if not os.path.exists(asset.storage_path):
        raise NotFoundError("Evidence binary file not found on storage")

    return FileResponse(
        path=asset.storage_path,
        media_type=asset.mime_type,
        filename=asset.original_filename,
    )
