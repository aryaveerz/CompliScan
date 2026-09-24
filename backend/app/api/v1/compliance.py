"""
CompliScan LM — Compliance Evaluation API Endpoints.
Provides backend-authoritative endpoints for Applicability and Deterministic Compliance Findings.
"""

from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.user import User
from backend.app.services.inspection_service import InspectionService
from backend.app.services.applicability_service import ApplicabilityService
from backend.app.services.compliance_service import ComplianceEvaluationService
from backend.app.services.analysis_job_service import AnalysisJobService
from backend.app.schemas.compliance import (
    ApplicabilityListResponse,
    ApplicabilityItemResponse,
    ComplianceFindingResponse,
    ComplianceEvaluationSummaryResponse,
)
from backend.app.schemas.image_quality import AnalysisJobResponse
from backend.app.services.rules.rule_definitions import (
    RULE_SET_ID,
    RULE_SET_VERSION,
    EVALUATION_VERSION,
)
from shared.domain.enums import JobType

router = APIRouter(prefix="/inspections", tags=["compliance"])


@router.get(
    "/{inspection_id}/applicability",
    response_model=ApplicabilityListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_inspection_applicability(
    inspection_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve statutory applicability results for an inspection.
    RBAC: Owner inspector or reviewer.
    """
    # 1. Authorize inspection access
    inspection = await InspectionService.get_inspection(db, inspection_id, current_user)

    # 2. Fetch existing or evaluate
    results = await ApplicabilityService.get_inspection_applicability(db, inspection.id)
    if not results:
        results = await ApplicabilityService.evaluate_and_persist(
            db=db,
            inspection_id=inspection.id,
            actor_id=current_user.id,
        )
        await db.commit()

    return ApplicabilityListResponse(
        inspection_id=inspection.id,
        items=[ApplicabilityItemResponse.model_validate(r) for r in results],
        rule_set_id=RULE_SET_ID,
        rule_set_version=RULE_SET_VERSION,
        evaluation_version=EVALUATION_VERSION,
    )


@router.post(
    "/{inspection_id}/evaluate",
    status_code=status.HTTP_200_OK,
)
async def evaluate_compliance(
    inspection_id: str,
    async_job: bool = Query(False, description="Set to true to process asynchronously via worker"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Run deterministic compliance evaluation for all evidence in the inspection.
    If async_job=True, enqueues an EVALUATION job and returns 202 Accepted.
    Otherwise executes deterministically and returns 200 OK with summary findings.
    """
    # 1. Authorize inspection access
    inspection = await InspectionService.get_inspection(db, inspection_id, current_user)

    if async_job:
        job = await AnalysisJobService.enqueue_job(
            db=db,
            inspection_id=inspection.id,
            job_type=JobType.EVALUATION,
            priority=10,
        )
        await db.commit()
        return AnalysisJobResponse.model_validate(job)

    # Synchronous deterministic evaluation
    findings = await ComplianceEvaluationService.evaluate_inspection_compliance(
        db=db,
        inspection_id=inspection.id,
        actor_id=current_user.id,
    )
    await db.commit()

    summary_counts: dict = {}
    for f in findings:
        summary_counts[f.result] = summary_counts.get(f.result, 0) + 1

    return ComplianceEvaluationSummaryResponse(
        inspection_id=inspection.id,
        rule_set_id=RULE_SET_ID,
        rule_set_version=RULE_SET_VERSION,
        evaluation_version=EVALUATION_VERSION,
        findings=[ComplianceFindingResponse.model_validate(f) for f in findings],
        total_findings=len(findings),
        summary_counts=summary_counts,
    )


@router.get(
    "/{inspection_id}/findings",
    response_model=ComplianceEvaluationSummaryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_inspection_findings(
    inspection_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve persisted compliance findings for an inspection.
    RBAC: Owner inspector or reviewer.
    """
    # 1. Authorize inspection access
    inspection = await InspectionService.get_inspection(db, inspection_id, current_user)

    # 2. Fetch findings
    findings = await ComplianceEvaluationService.get_inspection_findings(db, inspection.id)
    if not findings:
        try:
            findings = await ComplianceEvaluationService.evaluate_inspection_compliance(
                db=db,
                inspection_id=inspection.id,
                actor_id=current_user.id,
            )
            await db.commit()
        except Exception:
            pass

    summary_counts: dict = {}
    for f in findings:
        summary_counts[f.result] = summary_counts.get(f.result, 0) + 1

    return ComplianceEvaluationSummaryResponse(
        inspection_id=inspection.id,
        rule_set_id=RULE_SET_ID,
        rule_set_version=RULE_SET_VERSION,
        evaluation_version=EVALUATION_VERSION,
        findings=[ComplianceFindingResponse.model_validate(f) for f in findings],
        total_findings=len(findings),
        summary_counts=summary_counts,
    )
