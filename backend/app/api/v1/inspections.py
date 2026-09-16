"""
CompliScan LM — Inspections Router.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.inspection import (
    InspectionCreateRequest,
    InspectionUpdateRequest,
    InspectionResponse,
    InspectionListResponse,
)
from backend.app.services.inspection_service import InspectionService
from backend.app.api.deps import get_current_user, require_role
from shared.domain.enums import UserRole

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
