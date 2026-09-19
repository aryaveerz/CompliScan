"""
CompliScan LM — Dashboard Router.
Provides real-time operational and compliance metrics.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.api.deps import get_current_user
from backend.app.schemas.dashboard import DashboardMetricsResponse
from backend.app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/metrics",
    response_model=DashboardMetricsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_dashboard_metrics(
    date_range: str = Query(default="30d", pattern="^(7d|30d|90d|all)$"),
    category: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve aggregated operational, statutory compliance, and governance metrics.
    RBAC: Authenticated Inspectors, Reviewers, Admins.
    """
    return await DashboardService.get_metrics(
        db=db,
        current_user=current_user,
        date_range=date_range,
        category=category,
    )
