"""
CompliScan LM — Reviewer Governance Service (Async).
Handles reviewer queues, adjudications/overrides (separate from system findings),
revision requests, and evidence requests (ER-xxxxx).
"""

from datetime import datetime, timezone
import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.app.models.inspection import InspectionCase
from backend.app.models.compliance import ComplianceFinding
from backend.app.models.reviewer import ReviewerDecision
from backend.app.models.evidence_request import EvidenceRequest
from backend.app.models.evidence import EvidenceAsset
from backend.app.models.user import User
from backend.app.schemas.reviewer import (
    ReviewerDecisionCreate,
    ReviewRevisionRequest,
    EvidenceRequestCreate,
    EvidenceRequestFulfillRequest,
    ReviewQueueItemResponse,
)
from backend.app.services.audit_service import AuditService
from backend.app.core.errors import (
    NotFoundError,
    ForbiddenError,
    ConflictError,
    ValidationError,
)
from shared.domain.states import InspectionLifecycleState, ProcessingState, FinalizationStatus
from shared.domain.enums import (
    AuditEventType,
    ReviewerDeterminationType,
    ComplianceResult,
    EvidenceRequestStatus,
    UserRole,
)


class ReviewerService:

    @staticmethod
    def check_editable(inspection: InspectionCase) -> None:
        if inspection.finalization_status == FinalizationStatus.READ_ONLY.value or inspection.status == InspectionLifecycleState.FINALIZED.value:
            raise ConflictError("Inspection is finalized and immutable (READ_ONLY)")

    @classmethod
    async def get_review_queue(cls, db: AsyncSession) -> List[ReviewQueueItemResponse]:
        stmt = (
            select(InspectionCase)
            .where(InspectionCase.status.in_([
                InspectionLifecycleState.SUBMITTED_FOR_REVIEW.value,
                InspectionLifecycleState.IN_VERIFICATION.value,
                InspectionLifecycleState.REQUIRES_REVISION.value,
            ]))
            .order_by(InspectionCase.submitted_at.desc().nullslast(), InspectionCase.created_at.desc())
        )
        inspections = (await db.execute(stmt)).scalars().all()

        results = []
        for insp in inspections:
            stmt_f = select(ComplianceFinding).where(ComplianceFinding.inspection_id == insp.id)
            findings = (await db.execute(stmt_f)).scalars().all()
            pot_violations = sum(1 for f in findings if f.result == ComplianceResult.POTENTIAL_NON_COMPLIANCE.value)

            stmt_er = select(func.count(EvidenceRequest.id)).where(
                EvidenceRequest.inspection_id == insp.id,
                EvidenceRequest.status == EvidenceRequestStatus.OPEN.value,
            )
            open_ers = (await db.execute(stmt_er)).scalar() or 0

            inspector = (await db.execute(select(User).where(User.id == insp.created_by_id))).scalar_one_or_none()
            inspector_name = inspector.full_name or inspector.email if inspector else "Unknown"

            results.append(ReviewQueueItemResponse(
                id=insp.id,
                case_number=insp.case_number,
                product_name=insp.product_name,
                origin_status=insp.origin_status,
                status=insp.status,
                created_by_id=insp.created_by_id,
                inspector_name=inspector_name,
                submitted_at=insp.submitted_at,
                findings_count=len(findings),
                potential_violations_count=pot_violations,
                open_evidence_requests_count=open_ers,
            ))
        return results

    @classmethod
    async def record_reviewer_decision(
        cls,
        db: AsyncSession,
        inspection_id: str,
        reviewer_id: str,
        decision_in: ReviewerDecisionCreate,
    ) -> ReviewerDecision:
        stmt = select(InspectionCase).where(InspectionCase.id == inspection_id)
        inspection = (await db.execute(stmt)).scalar_one_or_none()
        if not inspection:
            raise NotFoundError(f"Inspection {inspection_id} not found")

        cls.check_editable(inspection)

        if inspection.status != InspectionLifecycleState.SUBMITTED_FOR_REVIEW.value:
            raise ConflictError(f"Cannot record reviewer decision when inspection status is {inspection.status}")

        if not decision_in.rationale or len(decision_in.rationale.strip()) < 5:
            raise ValidationError("A mandatory rationale (minimum 5 characters) is required for reviewer decisions")

        # Find finding if available
        finding = None
        if decision_in.finding_id:
            finding = (await db.execute(select(ComplianceFinding).where(ComplianceFinding.id == decision_in.finding_id))).scalar_one_or_none()
        else:
            finding = (await db.execute(
                select(ComplianceFinding).where(
                    ComplianceFinding.inspection_id == inspection_id,
                    ComplianceFinding.requirement_name == decision_in.requirement_name,
                )
            )).scalars().first()

        original_result = finding.result if finding else None

        # Determine override
        is_override = (
            decision_in.determination == ReviewerDeterminationType.OVERRIDDEN or
            decision_in.determination == ReviewerDeterminationType.OVERRIDDEN.value or
            (
                original_result is not None
                and decision_in.determination not in (ReviewerDeterminationType.CONFIRMED, ReviewerDeterminationType.CONFIRMED.value)
                and (
                    decision_in.adjudicated_result.value != original_result
                    if hasattr(decision_in.adjudicated_result, "value")
                    else decision_in.adjudicated_result != original_result
                )
            )
        )

        # Upsert decision
        stmt_dec = select(ReviewerDecision).where(
            ReviewerDecision.inspection_id == inspection_id,
            ReviewerDecision.requirement_name == decision_in.requirement_name,
        )
        existing_decision = (await db.execute(stmt_dec)).scalar_one_or_none()

        if existing_decision:
            existing_decision.determination = decision_in.determination.value
            existing_decision.adjudicated_result = decision_in.adjudicated_result.value
            existing_decision.original_result = original_result
            existing_decision.is_override = is_override
            existing_decision.rationale = decision_in.rationale
            existing_decision.reviewer_id = reviewer_id
            decision = existing_decision
        else:
            decision = ReviewerDecision(
                inspection_id=inspection_id,
                finding_id=finding.id if finding else None,
                requirement_name=decision_in.requirement_name,
                reviewer_id=reviewer_id,
                determination=decision_in.determination.value,
                original_result=original_result,
                adjudicated_result=decision_in.adjudicated_result.value,
                is_override=is_override,
                rationale=decision_in.rationale,
            )
            db.add(decision)

        await db.flush()

        # Audit Event
        event_type = (
            AuditEventType.REVIEWER_OVERRIDE_RECORDED
            if is_override
            else AuditEventType.REVIEWER_DECISION_RECORDED
        )

        await AuditService.log_event(
            db=db,
            inspection_id=inspection.id,
            actor_id=reviewer_id,
            actor_role=UserRole.REVIEWER.value,
            event_type=event_type,
            details={
                "decision_id": decision.id,
                "requirement_name": decision.requirement_name,
                "determination": decision.determination,
                "original_result": original_result,
                "adjudicated_result": decision.adjudicated_result,
                "is_override": is_override,
                "rationale": decision.rationale,
            },
        )
        await db.commit()
        await db.refresh(decision)
        return decision

    @classmethod
    async def request_revision(
        cls,
        db: AsyncSession,
        inspection_id: str,
        reviewer_id: str,
        revision_in: ReviewRevisionRequest,
    ) -> InspectionCase:
        stmt = select(InspectionCase).where(InspectionCase.id == inspection_id)
        inspection = (await db.execute(stmt)).scalar_one_or_none()
        if not inspection:
            raise NotFoundError(f"Inspection {inspection_id} not found")

        cls.check_editable(inspection)

        if inspection.status != InspectionLifecycleState.SUBMITTED_FOR_REVIEW.value:
            raise ConflictError(f"Cannot request revision from status {inspection.status}")

        if not revision_in.reason or len(revision_in.reason.strip()) < 5:
            raise ValidationError("Mandatory revision reason (minimum 5 characters) required")

        # Transition state
        inspection.status = InspectionLifecycleState.REQUIRES_REVISION.value

        await AuditService.log_event(
            db=db,
            inspection_id=inspection.id,
            actor_id=reviewer_id,
            actor_role=UserRole.REVIEWER.value,
            event_type=AuditEventType.REVIEW_REVISION_REQUESTED,
            details={
                "reason": revision_in.reason,
                "requested_changes": revision_in.requested_changes,
            },
        )
        await db.commit()
        await db.refresh(inspection)
        return inspection

    @classmethod
    async def create_evidence_request(
        cls,
        db: AsyncSession,
        inspection_id: str,
        reviewer_id: str,
        er_in: EvidenceRequestCreate,
    ) -> EvidenceRequest:
        stmt = select(InspectionCase).where(InspectionCase.id == inspection_id)
        inspection = (await db.execute(stmt)).scalar_one_or_none()
        if not inspection:
            raise NotFoundError(f"Inspection {inspection_id} not found")

        cls.check_editable(inspection)

        if not er_in.request_reason or len(er_in.request_reason.strip()) < 5:
            raise ValidationError("Evidence request reason is mandatory (min 5 chars)")
        if not er_in.requested_condition or len(er_in.requested_condition.strip()) < 5:
            raise ValidationError("Requested condition/fact is mandatory (min 5 chars)")

        er = EvidenceRequest(
            inspection_id=inspection_id,
            reviewer_id=reviewer_id,
            requirement_name=er_in.requirement_name,
            request_reason=er_in.request_reason,
            requested_condition=er_in.requested_condition,
            requested_evidence_type=er_in.requested_evidence_type,
            status=EvidenceRequestStatus.OPEN.value,
        )
        db.add(er)
        await db.flush()

        await AuditService.log_event(
            db=db,
            inspection_id=inspection.id,
            actor_id=reviewer_id,
            actor_role=UserRole.REVIEWER.value,
            event_type=AuditEventType.EVIDENCE_REQUEST_CREATED,
            details={
                "evidence_request_id": er.id,
                "requirement_name": er.requirement_name,
                "request_reason": er.request_reason,
                "requested_condition": er.requested_condition,
            },
        )
        await db.commit()
        await db.refresh(er)
        return er

    @classmethod
    async def fulfill_evidence_request(
        cls,
        db: AsyncSession,
        er_id: str,
        user_id: str,
        fulfill_in: EvidenceRequestFulfillRequest,
    ) -> EvidenceRequest:
        er = (await db.execute(select(EvidenceRequest).where(EvidenceRequest.id == er_id))).scalar_one_or_none()
        if not er:
            raise NotFoundError(f"Evidence request {er_id} not found")

        inspection = (await db.execute(select(InspectionCase).where(InspectionCase.id == er.inspection_id))).scalar_one_or_none()
        if not inspection:
            raise NotFoundError(f"Inspection {er.inspection_id} not found")

        cls.check_editable(inspection)

        evidence = (await db.execute(select(EvidenceAsset).where(EvidenceAsset.id == fulfill_in.evidence_id))).scalar_one_or_none()
        if not evidence or evidence.inspection_id != er.inspection_id:
            raise ValidationError("Supplied evidence asset does not exist or does not belong to this inspection")

        er.response_evidence_id = evidence.id
        er.response_note = fulfill_in.response_note
        er.resolved_by_id = user_id
        er.resolved_at = datetime.now(timezone.utc)
        er.status = EvidenceRequestStatus.FULFILLED.value

        await AuditService.log_event(
            db=db,
            inspection_id=inspection.id,
            actor_id=user_id,
            actor_role=UserRole.INSPECTOR.value,
            event_type=AuditEventType.EVIDENCE_REQUEST_FULFILLED,
            details={
                "evidence_request_id": er.id,
                "response_evidence_id": evidence.id,
                "evidence_sha256": evidence.sha256_hash,
                "response_note": fulfill_in.response_note,
            },
        )
        await db.commit()
        await db.refresh(er)
        return er

    @classmethod
    async def get_reviewer_decisions_for_inspection(cls, db: AsyncSession, inspection_id: str) -> List[ReviewerDecision]:
        stmt = (
            select(ReviewerDecision)
            .where(ReviewerDecision.inspection_id == inspection_id)
            .order_by(ReviewerDecision.created_at.asc())
        )
        return list((await db.execute(stmt)).scalars().all())

    @classmethod
    async def get_evidence_requests_for_inspection(cls, db: AsyncSession, inspection_id: str) -> List[EvidenceRequest]:
        stmt = (
            select(EvidenceRequest)
            .where(EvidenceRequest.inspection_id == inspection_id)
            .order_by(EvidenceRequest.created_at.asc())
        )
        return list((await db.execute(stmt)).scalars().all())
