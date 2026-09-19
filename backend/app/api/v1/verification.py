"""
CompliScan LM — Inspector Verification Endpoints.
Provides backend-authoritative endpoints for declaration corrections, manual observations,
verification state inspection, and submission for reviewer governance.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.user import User
from backend.app.services.inspection_service import InspectionService
from backend.app.services.verification_service import VerificationService
from backend.app.schemas.verification import (
    DeclarationCorrectionCreate,
    DeclarationCorrectionResponse,
    ManualObservationCreate,
    ManualObservationResponse,
    VerificationSubmitRequest,
    VerificationStateResponse,
)
from backend.app.schemas.inspection import InspectionResponse
from backend.app.core.errors import ForbiddenError
from shared.domain.enums import UserRole

router = APIRouter(prefix="/inspections", tags=["verification"])


@router.post(
    "/{inspection_id}/corrections",
    response_model=DeclarationCorrectionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_declaration_correction(
    inspection_id: str,
    correction_in: DeclarationCorrectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Record an inspector correction to extracted declaration values.
    RBAC: Inspector (owner).
    """
    # Authorize case access
    await InspectionService.get_inspection(db, inspection_id, current_user)

    correction = await VerificationService.add_declaration_correction(
        db=db,
        inspection_id=inspection_id,
        inspector_id=current_user.id,
        correction_in=correction_in,
    )
    return correction


@router.post(
    "/{inspection_id}/manual-observations",
    response_model=ManualObservationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_manual_observation(
    inspection_id: str,
    observation_in: ManualObservationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Record an inspector manual observation where automated perception is insufficient.
    RBAC: Inspector (owner).
    """
    await InspectionService.get_inspection(db, inspection_id, current_user)

    observation = await VerificationService.add_manual_observation(
        db=db,
        inspection_id=inspection_id,
        inspector_id=current_user.id,
        observation_in=observation_in,
    )
    return observation


@router.get(
    "/{inspection_id}/verification-state",
    response_model=VerificationStateResponse,
    status_code=status.HTTP_200_OK,
)
async def get_verification_state(
    inspection_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get current verification status, corrections, manual observations, and submission readiness.
    RBAC: Inspector (owner) or Reviewer.
    """
    await InspectionService.get_inspection(db, inspection_id, current_user)
    return await VerificationService.get_verification_state(db, inspection_id)


@router.post(
    "/{inspection_id}/submit-for-review",
    response_model=InspectionResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_inspection_for_review(
    inspection_id: str,
    submit_in: VerificationSubmitRequest = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit verified inspection case for Reviewer governance.
    RBAC: Inspector (owner).
    """
    inspection = await InspectionService.get_inspection(db, inspection_id, current_user)
    if current_user.role == UserRole.INSPECTOR.value and inspection.created_by_id != current_user.id:
        raise ForbiddenError("You can only submit your own inspection cases")

    updated_inspection = await VerificationService.submit_for_review(
        db=db,
        inspection_id=inspection_id,
        inspector_id=current_user.id,
        submit_in=submit_in,
    )
    return updated_inspection
