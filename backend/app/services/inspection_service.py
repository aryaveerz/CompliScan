"""
CompliScan LM — Inspection Service.
Manages InspectionCase lifecycle, product context, and case authorization.
"""

from datetime import datetime, timezone
import random
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from backend.app.models.inspection import InspectionCase
from backend.app.models.user import User
from backend.app.schemas.inspection import InspectionCreateRequest, InspectionUpdateRequest
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
                selectinload(InspectionCase.evidence_assets),
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
                selectinload(InspectionCase.evidence_assets),
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
                selectinload(InspectionCase.evidence_assets),
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
