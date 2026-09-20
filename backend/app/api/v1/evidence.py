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
from backend.app.schemas.image_quality import ImageQualityAssessmentResponse, AnalysisJobResponse
from backend.app.schemas.ocr import OCRResultResponse
from backend.app.schemas.structured_declaration import StructuredDeclarationResponse
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
    SHA-256 computation, updates inspection lifecycle state, and auto-enqueues
    asynchronous Image Quality Assessment.
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


from fastapi.responses import Response

@router.get("/evidence/{evidence_id}/download")
async def download_evidence(
    evidence_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Download / view the stored original evidence file.
    Enforces authorization check against owning inspection case.
    """
    content, asset = await EvidenceService.get_evidence_binary(db, evidence_id, current_user=current_user)

    return Response(
        content=content,
        media_type=asset.mime_type,
        headers={
            "Content-Disposition": f'inline; filename="{asset.original_filename}"'
        },
    )



@router.get("/evidence/{evidence_id}/quality", response_model=ImageQualityAssessmentResponse)
async def get_evidence_quality(
    evidence_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve the Image Quality Assessment for a specific evidence asset.
    """
    assessment = await EvidenceService.get_evidence_quality(db, evidence_id)
    return ImageQualityAssessmentResponse.model_validate(assessment)


@router.post(
    "/evidence/{evidence_id}/assess-quality",
    response_model=AnalysisJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_quality_reassessment(
    evidence_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.INSPECTOR)),
):
    """
    Manually enqueue an asynchronous Image Quality Assessment job.
    Returns 202 Accepted with job metadata without executing synchronous processing.
    """
    job = await EvidenceService.enqueue_quality_reassessment(
        db=db,
        evidence_id=evidence_id,
        current_user=current_user,
    )
    return AnalysisJobResponse.model_validate(job)


@router.get("/evidence/{evidence_id}/ocr", response_model=OCRResultResponse)
async def get_evidence_ocr(
    evidence_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve OCR perception result for a specific evidence asset.
    """
    ocr_result = await EvidenceService.get_evidence_ocr(db, evidence_id, current_user)
    return OCRResultResponse.model_validate(ocr_result)


@router.post(
    "/evidence/{evidence_id}/process-ocr",
    response_model=AnalysisJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_ocr_processing(
    evidence_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.INSPECTOR)),
):
    """
    Manually enqueue an asynchronous OCR perception job.
    Returns 202 Accepted with job metadata without executing synchronous processing.
    """
    job = await EvidenceService.enqueue_ocr_processing(
        db=db,
        evidence_id=evidence_id,
        current_user=current_user,
    )
    return AnalysisJobResponse.model_validate(job)


@router.get("/evidence/{evidence_id}/declarations", response_model=StructuredDeclarationResponse)
async def get_evidence_declarations(
    evidence_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve structured declaration extraction result for a specific evidence asset.
    """
    decl_result = await EvidenceService.get_evidence_declarations(db, evidence_id, current_user)
    return StructuredDeclarationResponse.model_validate(decl_result)


@router.post(
    "/evidence/{evidence_id}/extract-declarations",
    response_model=AnalysisJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_declaration_extraction(
    evidence_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.INSPECTOR)),
):
    """
    Manually enqueue an asynchronous semantic extraction job.
    Returns 202 Accepted with job metadata without executing synchronous processing.
    """
    job = await EvidenceService.enqueue_declaration_extraction(
        db=db,
        evidence_id=evidence_id,
        current_user=current_user,
    )
    return AnalysisJobResponse.model_validate(job)
