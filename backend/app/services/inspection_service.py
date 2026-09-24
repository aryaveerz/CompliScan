"""
CompliScan LM — Inspection Service.
Manages InspectionCase lifecycle, product context, and case authorization.
"""

from datetime import datetime, timezone
import random
import math
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc, func, and_, or_, distinct
from sqlalchemy.orm import selectinload
from backend.app.models.inspection import InspectionCase
from backend.app.models.user import User
from backend.app.models.audit import AuditEvent
from backend.app.models.final_audit import FinalAuditRecord
from backend.app.models.evidence import EvidenceAsset
from backend.app.schemas.inspection import (
    InspectionCreateRequest,
    InspectionUpdateRequest,
    InspectionSearchResponse,
    InspectionSearchResultItem,
)
from backend.app.schemas.audit import AuditEventResponse
from backend.app.core.errors import NotFoundError, ForbiddenError, InvalidStateError, ValidationError
from backend.app.services.audit_service import AuditService
from shared.domain.states import InspectionLifecycleState, ProcessingState, FinalizationStatus
from shared.domain.enums import OriginStatus, AuditEventType, UserRole


class InspectionService:
    @staticmethod
    def _generate_case_number() -> str:
        """Generate human-readable unique case number."""
        year = datetime.now(timezone.utc).year
        random_suffix = random.randint(10000, 99999)
        return f"INSP-{year}-{random_suffix}"

    @classmethod
    async def create_inspection(
        cls,
        db: AsyncSession,
        request: InspectionCreateRequest,
        current_user: User,
    ) -> InspectionCase:
        """Create a new InspectionCase with validated Product Context."""
        if current_user.role != UserRole.INSPECTOR.value:
            raise ForbiddenError("Only users with the INSPECTOR role may create inspection cases")

        if not request.product_name.strip():
            raise ValidationError("Product Name is mandatory and cannot be blank")

        case_number = cls._generate_case_number()

        inspection = InspectionCase(
            case_number=case_number,
            status=InspectionLifecycleState.DRAFT.value,
            processing_state=ProcessingState.IDLE.value,
            finalization_status=FinalizationStatus.UNFINALIZED.value,
            product_name=request.product_name.strip(),
            origin_status=request.origin_status.value if isinstance(request.origin_status, OriginStatus) else str(request.origin_status),
            product_category=request.product_category.strip() if request.product_category else None,
            reference_url=request.reference_url.strip() if request.reference_url else None,
            notes=request.notes.strip() if request.notes else None,
            created_by_id=current_user.id,
        )
        db.add(inspection)
        await db.flush()

        # Audit log
        await AuditService.log_event(
            db=db,
            event_type=AuditEventType.INSPECTION_CREATED,
            inspection_id=inspection.id,
            actor_id=current_user.id,
            actor_role=current_user.role,
            details={
                "case_number": case_number,
                "product_name": inspection.product_name,
                "origin_status": inspection.origin_status,
            },
        )

        await db.commit()
        await db.refresh(inspection, attribute_names=["created_by", "evidence_assets"])
        return inspection

    @staticmethod
    async def get_inspection(
        db: AsyncSession,
        inspection_id: str,
        current_user: User,
    ) -> InspectionCase:
        """Fetch an inspection case with authorization check."""
        stmt = (
            select(InspectionCase)
            .where(InspectionCase.id == inspection_id)
            .options(
                selectinload(InspectionCase.created_by),
                selectinload(InspectionCase.reviewer),
                selectinload(InspectionCase.evidence_assets).options(
                    selectinload(EvidenceAsset.structured_declarations),
                    selectinload(EvidenceAsset.quality_assessment),
                    selectinload(EvidenceAsset.ocr_result),
                ),
                selectinload(InspectionCase.final_audit_record),
            )
        )
        result = await db.execute(stmt)
        inspection = result.scalar_one_or_none()

        if not inspection:
            raise NotFoundError(f"Inspection case {inspection_id} not found")

        # RBAC Check: Inspector can only view own cases; Reviewer can view any
        if current_user.role == UserRole.INSPECTOR.value and inspection.created_by_id != current_user.id:
            raise ForbiddenError("Access denied: You can only view your own inspection cases")

        return inspection

    @staticmethod
    async def list_inspections(
        db: AsyncSession,
        current_user: User,
    ) -> List[InspectionCase]:
        """List inspections based on user role."""
        stmt = (
            select(InspectionCase)
            .options(
                selectinload(InspectionCase.created_by),
                selectinload(InspectionCase.reviewer),
                selectinload(InspectionCase.evidence_assets).options(
                    selectinload(EvidenceAsset.structured_declarations),
                    selectinload(EvidenceAsset.quality_assessment),
                    selectinload(EvidenceAsset.ocr_result),
                ),
                selectinload(InspectionCase.final_audit_record),
            )
            .order_by(desc(InspectionCase.created_at))
        )

        # Filter by role
        if current_user.role == UserRole.INSPECTOR.value:
            stmt = stmt.where(InspectionCase.created_by_id == current_user.id)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_inspection_context(
        db: AsyncSession,
        inspection_id: str,
        request: InspectionUpdateRequest,
        current_user: User,
    ) -> InspectionCase:
        """Update product context metadata."""
        stmt = (
            select(InspectionCase)
            .where(InspectionCase.id == inspection_id)
            .options(
                selectinload(InspectionCase.created_by),
                selectinload(InspectionCase.reviewer),
                selectinload(InspectionCase.evidence_assets).options(
                    selectinload(EvidenceAsset.structured_declarations),
                    selectinload(EvidenceAsset.quality_assessment),
                    selectinload(EvidenceAsset.ocr_result),
                ),
            )
        )
        result = await db.execute(stmt)
        inspection = result.scalar_one_or_none()

        if not inspection:
            raise NotFoundError(f"Inspection case {inspection_id} not found")

        if current_user.role == UserRole.INSPECTOR.value and inspection.created_by_id != current_user.id:
            raise ForbiddenError("Cannot update another inspector's case")

        if inspection.finalization_status == FinalizationStatus.READ_ONLY.value:
            raise InvalidStateError("Cannot modify a finalized inspection case")

        if request.product_name is not None:
            if not request.product_name.strip():
                raise ValidationError("Product name cannot be empty")
            inspection.product_name = request.product_name.strip()

        if request.origin_status is not None:
            inspection.origin_status = request.origin_status.value if isinstance(request.origin_status, OriginStatus) else str(request.origin_status)

        if request.product_category is not None:
            inspection.product_category = request.product_category.strip() or None

        if request.reference_url is not None:
            inspection.reference_url = request.reference_url.strip() or None

        if request.notes is not None:
            inspection.notes = request.notes.strip() or None

        await AuditService.log_event(
            db=db,
            event_type=AuditEventType.PRODUCT_CONTEXT_UPDATED,
            inspection_id=inspection.id,
            actor_id=current_user.id,
            actor_role=current_user.role,
            details={
                "product_name": inspection.product_name,
                "origin_status": inspection.origin_status,
            },
        )

        await db.commit()
        await db.refresh(inspection)
        return inspection

    @classmethod
    async def search_inspections(
        cls,
        db: AsyncSession,
        current_user: User,
        q: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        compliance: Optional[str] = None,
        origin: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> InspectionSearchResponse:
        """
        Multi-field server-side search and filtering for the Inspection Repository.
        Respects RBAC authorization strictly before returning records.
        """
        # Validate pagination
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10
        elif page_size > 100:
            page_size = 100

        # Sort field allowlist to prevent SQL injection
        sort_col_map = {
            "created_at": InspectionCase.created_at,
            "updated_at": InspectionCase.updated_at,
            "case_number": InspectionCase.case_number,
            "product_name": InspectionCase.product_name,
            "status": InspectionCase.status,
            "product_category": InspectionCase.product_category,
            "finalized_at": InspectionCase.finalized_at,
        }
        sort_col = sort_col_map.get(sort_by, InspectionCase.created_at)
        order_clause = desc(sort_col) if sort_order.lower() == "desc" else asc(sort_col)

        # Filters
        filters = []

        # Role-based scoping
        if current_user.role == UserRole.INSPECTOR.value:
            filters.append(InspectionCase.created_by_id == current_user.id)

        # Free-text search on case_number, product_name, category, notes
        if q and q.strip():
            term = f"%{q.strip()}%"
            filters.append(
                or_(
                    InspectionCase.case_number.ilike(term),
                    InspectionCase.product_name.ilike(term),
                    InspectionCase.product_category.ilike(term),
                    InspectionCase.notes.ilike(term),
                )
            )

        if category and category.strip():
            filters.append(func.lower(InspectionCase.product_category) == category.strip().lower())

        if status and status.strip():
            filters.append(InspectionCase.status == status.strip().upper())

        if origin and origin.strip():
            filters.append(InspectionCase.origin_status == origin.strip().upper())

        if start_date is not None:
            filters.append(InspectionCase.created_at >= start_date)

        if end_date is not None:
            filters.append(InspectionCase.created_at <= end_date)

        # Compliance status filter (requires joining FinalAuditRecord)
        if compliance and compliance.strip():
            filters.append(FinalAuditRecord.final_decision == compliance.strip().upper())

        where_clause = and_(*filters) if filters else True

        # Total Count Query
        count_stmt = (
            select(func.count(distinct(InspectionCase.id)))
            .outerjoin(FinalAuditRecord, FinalAuditRecord.inspection_id == InspectionCase.id)
            .where(where_clause)
        )
        count_res = await db.execute(count_stmt)
        total_count = count_res.scalar() or 0
        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1

        # Data Query with Evidence Count
        stmt = (
            select(
                InspectionCase,
                FinalAuditRecord.final_decision.label("final_decision"),
                func.count(EvidenceAsset.id).label("evidence_count"),
            )
            .outerjoin(FinalAuditRecord, FinalAuditRecord.inspection_id == InspectionCase.id)
            .outerjoin(EvidenceAsset, EvidenceAsset.inspection_id == InspectionCase.id)
            .where(where_clause)
            .group_by(InspectionCase.id, FinalAuditRecord.final_decision)
            .order_by(order_clause)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        res = await db.execute(stmt)
        rows = res.all()

        items: List[InspectionSearchResultItem] = []
        for insp, final_dec, ev_cnt in rows:
            items.append(
                InspectionSearchResultItem(
                    id=insp.id,
                    case_number=insp.case_number,
                    status=InspectionLifecycleState(insp.status),
                    processing_state=ProcessingState(insp.processing_state),
                    finalization_status=FinalizationStatus(insp.finalization_status),
                    product_name=insp.product_name,
                    origin_status=OriginStatus(insp.origin_status) if insp.origin_status in OriginStatus.__members__ else OriginStatus.UNKNOWN,
                    product_category=insp.product_category,
                    created_by_id=insp.created_by_id,
                    reviewer_id=insp.reviewer_id,
                    created_at=insp.created_at,
                    updated_at=insp.updated_at,
                    submitted_at=insp.submitted_at,
                    finalized_at=insp.finalized_at,
                    final_decision=final_dec,
                    evidence_count=ev_cnt or 0,
                )
            )

        return InspectionSearchResponse(
            items=items,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @staticmethod
    async def get_audit_trail(
        db: AsyncSession,
        inspection_id: str,
        current_user: User,
    ) -> List[AuditEventResponse]:
        """
        Fetch complete chronological chain of custody audit events for an inspection.
        Enforces authorization check.
        """
        # Authorization check via get_inspection
        await InspectionService.get_inspection(db, inspection_id, current_user)

        stmt = (
            select(AuditEvent)
            .where(AuditEvent.inspection_id == inspection_id)
            .order_by(asc(AuditEvent.created_at))
        )
        res = await db.execute(stmt)
        events = list(res.scalars().all())

        return [AuditEventResponse.model_validate(ev) for ev in events]
