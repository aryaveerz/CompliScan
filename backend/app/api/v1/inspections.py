"""
CompliScan LM — Inspections Router.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.inspection import (
    InspectionCreateRequest,
    InspectionUpdateRequest,
    InspectionResponse,
    InspectionListResponse,
    InspectionSearchResponse,
)
from backend.app.schemas.audit import AuditEventResponse
from backend.app.services.inspection_service import InspectionService
from backend.app.services.finalization_service import FinalizationService
from backend.app.services.docx_report_service import DOCXReportService
from backend.app.services.pdf_report_service import PDFReportService
from backend.app.services.audit_service import AuditService
from backend.app.api.deps import get_current_user, require_role
from backend.app.core.errors import ValidationError
from shared.domain.enums import UserRole, AuditEventType

router = APIRouter(prefix="/inspections", tags=["Inspections"])


@router.post("", response_model=InspectionResponse, status_code=status.HTTP_201_CREATED)
async def create_inspection(
    request: InspectionCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.INSPECTOR)),
):
    """
    Create a new InspectionCase.
    Enforces RBAC: Only an INSPECTOR may create an inspection case.
    """
    inspection = await InspectionService.create_inspection(db, request, current_user)
    return InspectionResponse.model_validate(inspection)


@router.get("", response_model=InspectionListResponse)
async def list_inspections(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List inspection cases.
    - Inspectors see only their own cases.
    - Reviewers see accessible cases.
    """
    items = await InspectionService.list_inspections(db, current_user)
    return InspectionListResponse(
        items=[InspectionResponse.model_validate(item) for item in items],
        total=len(items),
    )


@router.get("/search", response_model=InspectionSearchResponse)
async def search_inspections(
    q: Optional[str] = Query(default=None, description="Search term for case number, product name, or category"),
    category: Optional[str] = Query(default=None, description="Filter by product category"),
    status: Optional[str] = Query(default=None, description="Filter by lifecycle status"),
    compliance: Optional[str] = Query(default=None, description="Filter by final compliance decision"),
    origin: Optional[str] = Query(default=None, description="Filter by origin status (DOMESTIC, IMPORTED, UNKNOWN)"),
    start_date: Optional[datetime] = Query(default=None, description="Filter created_at >= start_date"),
    end_date: Optional[datetime] = Query(default=None, description="Filter created_at <= end_date"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query(default="created_at", description="Field to sort by"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc|ASC|DESC)$", description="Sort direction"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Server-side search & filtering for the Inspection Repository.
    Supports multi-field filtering, pagination, and SQL-injection safe sorting.
    RBAC: Enforced strictly by user role.
    """
    return await InspectionService.search_inspections(
        db=db,
        current_user=current_user,
        q=q,
        category=category,
        status=status,
        compliance=compliance,
        origin=origin,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/{inspection_id}", response_model=InspectionResponse)
async def get_inspection(
    inspection_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get detailed inspection case including Product Context and evidence assets.
    """
    inspection = await InspectionService.get_inspection(db, inspection_id, current_user)
    return InspectionResponse.model_validate(inspection)


@router.patch("/{inspection_id}", response_model=InspectionResponse)
async def update_inspection_context(
    inspection_id: str,
    request: InspectionUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update Product Context metadata for a working inspection.
    """
    inspection = await InspectionService.update_inspection_context(db, inspection_id, request, current_user)
    return InspectionResponse.model_validate(inspection)


@router.get("/{inspection_id}/audit-trail", response_model=List[AuditEventResponse])
async def get_audit_trail(
    inspection_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve the complete, chronological chain-of-custody audit trail for an inspection.
    RBAC: Owner Inspector, Reviewer, Admin.
    """
    return await InspectionService.get_audit_trail(db, inspection_id, current_user)


@router.get("/{inspection_id}/report/docx")
async def download_docx_report(
    inspection_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Download official editable Legal Metrology inspection DOCX report generated strictly from FinalAuditRecord.
    RBAC: Owner inspector or Reviewer.
    """
    inspection = await InspectionService.get_inspection(db, inspection_id, current_user)
    far = await FinalizationService.get_final_record(db, inspection_id)

    docx_bytes = DOCXReportService.generate_docx_report(far)

    # Log REPORT_DOWNLOADED audit event
    await AuditService.log_event(
        db=db,
        event_type=AuditEventType.REPORT_DOWNLOADED,
        inspection_id=inspection.id,
        actor_id=current_user.id,
        actor_role=current_user.role,
        details={
            "format": "docx",
            "case_number": inspection.case_number,
            "final_record_id": far.id,
        },
    )
    await db.commit()

    filename = f"CompliScan_Report_{inspection.case_number}.docx"
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Inspection-Id": inspection_id,
            "X-Final-Audit-Record-Id": far.id,
        },
    )


@router.get("/{inspection_id}/report/pdf")
async def download_pdf_report(
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
        },
    )
