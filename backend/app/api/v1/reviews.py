"""
CompliScan LM — Reviewer Governance & Finalization API Endpoints.
Provides backend-authoritative endpoints for reviewer queues, adjudications/overrides,
evidence requests, revisions, atomic finalization, and PDF report retrieval.
"""

import hashlib
from typing import List
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.user import User
from backend.app.services.inspection_service import InspectionService
from backend.app.services.reviewer_service import ReviewerService
from backend.app.services.finalization_service import FinalizationService
from backend.app.services.pdf_report_service import PDFReportService
from backend.app.services.audit_service import AuditService
from backend.app.schemas.reviewer import (
    ReviewerDecisionCreate,
    ReviewerDecisionResponse,
    ReviewRevisionRequest,
    EvidenceRequestCreate,
    EvidenceRequestResponse,
    EvidenceRequestFulfillRequest,
    FinalizeInspectionRequest,
    FinalAuditRecordResponse,
    ReviewQueueItemResponse,
)
from backend.app.schemas.inspection import InspectionResponse
from backend.app.core.errors import ForbiddenError, NotFoundError
from shared.domain.enums import UserRole, AuditEventType

router = APIRouter(tags=["reviews"])


# 1. Review Queue
@router.get(
    "/reviews/queue",
    response_model=List[ReviewQueueItemResponse],
    status_code=status.HTTP_200_OK,
)
async def get_review_queue(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get queue of inspections awaiting reviewer governance or under review.
    RBAC: Reviewer.
    """
    if current_user.role != UserRole.REVIEWER.value:
        raise ForbiddenError("Only users with the REVIEWER role can access the review queue")

    return await ReviewerService.get_review_queue(db)


# 2. Reviewer Decisions
@router.post(
    "/inspections/{inspection_id}/reviewer-decisions",
    response_model=ReviewerDecisionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def record_reviewer_decision(
    inspection_id: str,
    decision_in: ReviewerDecisionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Record a reviewer determination or override on a statutory requirement.
    RBAC: Reviewer.
    """
    if current_user.role != UserRole.REVIEWER.value:
        raise ForbiddenError("Only users with the REVIEWER role can record reviewer decisions")

    # Authorize case access
    await InspectionService.get_inspection(db, inspection_id, current_user)

    decision = await ReviewerService.record_reviewer_decision(
        db=db,
        inspection_id=inspection_id,
        reviewer_id=current_user.id,
        decision_in=decision_in,
    )
    return decision


@router.get(
    "/inspections/{inspection_id}/reviewer-decisions",
    response_model=List[ReviewerDecisionResponse],
    status_code=status.HTTP_200_OK,
)
async def get_reviewer_decisions(
    inspection_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List reviewer decisions for an inspection.
    RBAC: Owner inspector or Reviewer.
    """
    await InspectionService.get_inspection(db, inspection_id, current_user)
    return await ReviewerService.get_reviewer_decisions_for_inspection(db, inspection_id)


# 3. Revision Workflow
@router.post(
    "/inspections/{inspection_id}/request-revision",
    response_model=InspectionResponse,
    status_code=status.HTTP_200_OK,
)
async def request_revision(
    inspection_id: str,
    revision_in: ReviewRevisionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Reviewer returns inspection to Inspector with required changes (SUBMITTED_FOR_REVIEW -> REQUIRES_REVISION).
    RBAC: Reviewer.
    """
    if current_user.role != UserRole.REVIEWER.value:
        raise ForbiddenError("Only users with the REVIEWER role can request case revision")

    await InspectionService.get_inspection(db, inspection_id, current_user)

    updated_inspection = await ReviewerService.request_revision(
        db=db,
        inspection_id=inspection_id,
        reviewer_id=current_user.id,
        revision_in=revision_in,
    )
    return updated_inspection


# 4. Evidence Requests
@router.post(
    "/inspections/{inspection_id}/evidence-requests",
    response_model=EvidenceRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_evidence_request(
    inspection_id: str,
    er_in: EvidenceRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Reviewer requests supplemental visual evidence establishing a specific fact (creates ER-xxxxx).
    RBAC: Reviewer.
    """
    if current_user.role != UserRole.REVIEWER.value:
        raise ForbiddenError("Only users with the REVIEWER role can create evidence requests")

    await InspectionService.get_inspection(db, inspection_id, current_user)

    er = await ReviewerService.create_evidence_request(
        db=db,
        inspection_id=inspection_id,
        reviewer_id=current_user.id,
        er_in=er_in,
    )
    return er


@router.get(
    "/inspections/{inspection_id}/evidence-requests",
    response_model=List[EvidenceRequestResponse],
    status_code=status.HTTP_200_OK,
)
async def get_evidence_requests(
    inspection_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all evidence requests for an inspection.
    RBAC: Owner inspector or Reviewer.
    """
    await InspectionService.get_inspection(db, inspection_id, current_user)
    return await ReviewerService.get_evidence_requests_for_inspection(db, inspection_id)


@router.post(
    "/evidence-requests/{er_id}/fulfill",
    response_model=EvidenceRequestResponse,
    status_code=status.HTTP_200_OK,
)
async def fulfill_evidence_request(
    er_id: str,
    fulfill_in: EvidenceRequestFulfillRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Inspector fulfills an open evidence request by associating newly uploaded evidence asset.
    RBAC: Inspector (owner) or Reviewer.
    """
    er = await ReviewerService.fulfill_evidence_request(
        db=db,
        er_id=er_id,
        user_id=current_user.id,
        fulfill_in=fulfill_in,
    )
    return er


# 5. Finalization & FinalAuditRecord
@router.post(
    "/inspections/{inspection_id}/finalize",
    response_model=FinalAuditRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
async def finalize_inspection(
    inspection_id: str,
    finalize_in: FinalizeInspectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Reviewer atomically finalizes an inspection, generating immutable FinalAuditRecord and locking case to READ_ONLY.
    RBAC: Reviewer.
    """
    if current_user.role != UserRole.REVIEWER.value:
        raise ForbiddenError("Only authorized users with the REVIEWER role can finalize inspections")

    await InspectionService.get_inspection(db, inspection_id, current_user)

    far = await FinalizationService.finalize_inspection(
        db=db,
        inspection_id=inspection_id,
        reviewer_id=current_user.id,
        finalize_in=finalize_in,
    )
    return far


@router.get(
    "/inspections/{inspection_id}/final-record",
    response_model=FinalAuditRecordResponse,
    status_code=status.HTTP_200_OK,
)
async def get_final_audit_record(
    inspection_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fetch immutable FinalAuditRecord snapshot for a finalized inspection.
    RBAC: Owner inspector or Reviewer.
    """
    await InspectionService.get_inspection(db, inspection_id, current_user)
    return await FinalizationService.get_final_record(db, inspection_id)


# 6. PDF Inspection Report
@router.get(
    "/inspections/{inspection_id}/final-report",
    status_code=status.HTTP_200_OK,
)
async def get_final_pdf_report(
    inspection_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Download official Legal Metrology inspection PDF report generated strictly from FinalAuditRecord.
    RBAC: Owner inspector or Reviewer.
    """
    inspection = await InspectionService.get_inspection(db, inspection_id, current_user)
    far = await FinalizationService.get_final_record(db, inspection_id)

    pdf_bytes = PDFReportService.generate_pdf_report(far)
    report_sha256 = hashlib.sha256(pdf_bytes).hexdigest()

    # Log REPORT_DOWNLOADED audit event
    await AuditService.log_event(
        db=db,
        event_type=AuditEventType.REPORT_DOWNLOADED,
        inspection_id=inspection.id,
        actor_id=current_user.id,
        actor_role=current_user.role,
        details={
            "format": "pdf",
            "case_number": inspection.case_number,
            "final_record_id": far.id,
            "report_sha256": report_sha256,
        },
    )
    await db.commit()

    filename = f"CompliScan_Report_{inspection.case_number}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Inspection-Id": inspection_id,
            "X-Final-Audit-Record-Id": far.id,
            "X-Report-SHA256": report_sha256,
        },
    )
