"""
CompliScan LM — Inspector Verification Service (Async).
Handles inspector declaration corrections, manual observations, and submission for review.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.inspection import InspectionCase
from backend.app.models.evidence import EvidenceAsset
from backend.app.models.verification import DeclarationCorrection, ManualObservation
from backend.app.models.compliance import ComplianceFinding
from backend.app.models.evidence_request import EvidenceRequest
from backend.app.schemas.verification import (
    DeclarationCorrectionCreate,
    ManualObservationCreate,
    VerificationSubmitRequest,
    VerificationStateResponse,
    DeclarationCorrectionResponse,
    ManualObservationResponse,
)
from backend.app.services.audit_service import AuditService
from backend.app.core.errors import (
    NotFoundError,
    ForbiddenError,
    ConflictError,
    ValidationError,
)
from shared.domain.states import InspectionLifecycleState, ProcessingState, FinalizationStatus
from shared.domain.enums import AuditEventType, UserRole, EvidenceRequestStatus


class VerificationService:

    @staticmethod
    def check_editable(inspection: InspectionCase) -> None:
        if inspection.finalization_status == FinalizationStatus.READ_ONLY.value or inspection.status == InspectionLifecycleState.FINALIZED.value:
            raise ConflictError("Inspection is finalized and immutable (READ_ONLY)")

    @classmethod
    async def add_declaration_correction(
        cls,
        db: AsyncSession,
        inspection_id: str,
        inspector_id: str,
        correction_in: DeclarationCorrectionCreate,
    ) -> DeclarationCorrection:
        stmt = select(InspectionCase).where(InspectionCase.id == inspection_id)
        inspection = (await db.execute(stmt)).scalar_one_or_none()
        if not inspection:
            raise NotFoundError(f"Inspection {inspection_id} not found")

        cls.check_editable(inspection)

        # Ensure valid lifecycle state
        if inspection.status in (InspectionLifecycleState.DRAFT.value, InspectionLifecycleState.EVIDENCE_UPLOADED.value, InspectionLifecycleState.EVALUATED.value):
            inspection.status = InspectionLifecycleState.IN_VERIFICATION.value
        elif inspection.status not in (
            InspectionLifecycleState.IN_VERIFICATION.value,
            InspectionLifecycleState.REQUIRES_REVISION.value,
        ):
            raise ConflictError(f"Cannot correct declarations when inspection is in status {inspection.status}")

        correction = DeclarationCorrection(
            inspection_id=inspection.id,
            evidence_id=correction_in.evidence_id,
            requirement_name=correction_in.requirement_name,
            field_name=correction_in.field_name,
            previous_value=correction_in.previous_value,
            corrected_value=correction_in.corrected_value,
            reason=correction_in.reason,
            inspector_id=inspector_id,
        )
        db.add(correction)
        await db.flush()

        # Audit Event
        await AuditService.log_event(
            db=db,
            inspection_id=inspection.id,
            actor_id=inspector_id,
            actor_role=UserRole.INSPECTOR.value,
            event_type=AuditEventType.DECLARATION_MANUALLY_CORRECTED,
            details={
                "correction_id": correction.id,
                "requirement_name": correction.requirement_name,
                "field_name": correction.field_name,
                "reason": correction.reason,
            },
        )
        await db.commit()
        await db.refresh(correction)
        return correction

    @classmethod
    async def add_manual_observation(
        cls,
        db: AsyncSession,
        inspection_id: str,
        inspector_id: str,
        observation_in: ManualObservationCreate,
    ) -> ManualObservation:
        stmt = select(InspectionCase).where(InspectionCase.id == inspection_id)
        inspection = (await db.execute(stmt)).scalar_one_or_none()
        if not inspection:
            raise NotFoundError(f"Inspection {inspection_id} not found")

        cls.check_editable(inspection)

        # Ensure valid lifecycle state
        if inspection.status in (InspectionLifecycleState.DRAFT.value, InspectionLifecycleState.EVIDENCE_UPLOADED.value, InspectionLifecycleState.EVALUATED.value):
            inspection.status = InspectionLifecycleState.IN_VERIFICATION.value
        elif inspection.status not in (
            InspectionLifecycleState.IN_VERIFICATION.value,
            InspectionLifecycleState.REQUIRES_REVISION.value,
        ):
            raise ConflictError(f"Cannot add observations when inspection is in status {inspection.status}")

        obs = ManualObservation(
            inspection_id=inspection.id,
            requirement_name=observation_in.requirement_name,
            observation_text=observation_in.observation_text,
            inspector_id=inspector_id,
        )
        db.add(obs)
        await db.flush()

        # Audit Event
        await AuditService.log_event(
            db=db,
            inspection_id=inspection.id,
            actor_id=inspector_id,
            actor_role=UserRole.INSPECTOR.value,
            event_type=AuditEventType.MANUAL_OBSERVATION_RECORDED,
            details={
                "observation_id": obs.id,
                "requirement_name": obs.requirement_name,
                "text": obs.observation_text[:200],
            },
        )
        await db.commit()
        await db.refresh(obs)
        return obs

    @classmethod
    async def get_verification_state(cls, db: AsyncSession, inspection_id: str) -> VerificationStateResponse:
        stmt_insp = select(InspectionCase).where(InspectionCase.id == inspection_id)
        inspection = (await db.execute(stmt_insp)).scalar_one_or_none()
        if not inspection:
            raise NotFoundError(f"Inspection {inspection_id} not found")

        stmt_cor = (
            select(DeclarationCorrection)
            .where(DeclarationCorrection.inspection_id == inspection_id)
            .order_by(DeclarationCorrection.created_at.desc())
        )
        corrections = (await db.execute(stmt_cor)).scalars().all()

        stmt_obs = (
            select(ManualObservation)
            .where(ManualObservation.inspection_id == inspection_id)
            .order_by(ManualObservation.created_at.desc())
        )
        observations = (await db.execute(stmt_obs)).scalars().all()

        blocking_reasons: List[str] = []
        if inspection.processing_state == ProcessingState.PROCESSING.value:
            blocking_reasons.append("Inspection perception analysis is actively running")

        # Check evidence
        stmt_ev = select(EvidenceAsset).where(
            EvidenceAsset.inspection_id == inspection_id,
        )
        accepted_evidence = (await db.execute(stmt_ev)).scalars().all()
        if not accepted_evidence:
            blocking_reasons.append("No accepted visual evidence assets uploaded")

        # Check findings
        stmt_f = select(ComplianceFinding).where(ComplianceFinding.inspection_id == inspection_id)
        findings = (await db.execute(stmt_f)).scalars().all()
        if not findings:
            blocking_reasons.append("Deterministic compliance evaluation has not been performed")

        # Check open evidence requests
        stmt_er = select(EvidenceRequest).where(
            EvidenceRequest.inspection_id == inspection_id,
            EvidenceRequest.status == EvidenceRequestStatus.OPEN.value,
        )
        open_ers = (await db.execute(stmt_er)).scalars().all()
        if open_ers:
            blocking_reasons.append(f"{len(open_ers)} open evidence request(s) must be fulfilled before submission")

        is_ready = len(blocking_reasons) == 0 and inspection.status in (
            InspectionLifecycleState.DRAFT.value,
            InspectionLifecycleState.EVIDENCE_UPLOADED.value,
            InspectionLifecycleState.IN_VERIFICATION.value,
            InspectionLifecycleState.REQUIRES_REVISION.value,
            InspectionLifecycleState.EVALUATED.value,
        )

        return VerificationStateResponse(
            inspection_id=inspection.id,
            status=inspection.status,
            is_ready_for_submission=is_ready,
            blocking_reasons=blocking_reasons,
            corrections=[DeclarationCorrectionResponse.model_validate(c) for c in corrections],
            observations=[ManualObservationResponse.model_validate(o) for o in observations],
        )

    @classmethod
    async def submit_for_review(
        cls,
        db: AsyncSession,
        inspection_id: str,
        inspector_id: str,
        submit_in: Optional[VerificationSubmitRequest] = None,
    ) -> InspectionCase:
        stmt = select(InspectionCase).where(InspectionCase.id == inspection_id)
        inspection = (await db.execute(stmt)).scalar_one_or_none()
        if not inspection:
            raise NotFoundError(f"Inspection {inspection_id} not found")

        cls.check_editable(inspection)

        # Preconditions check
        vstate = await cls.get_verification_state(db, inspection_id)
        if not vstate.is_ready_for_submission:
            raise ValidationError(
                f"Inspection cannot be submitted for review: {'; '.join(vstate.blocking_reasons)}"
            )

        if inspection.status not in (
            InspectionLifecycleState.DRAFT.value,
            InspectionLifecycleState.EVIDENCE_UPLOADED.value,
            InspectionLifecycleState.IN_VERIFICATION.value,
            InspectionLifecycleState.REQUIRES_REVISION.value,
            InspectionLifecycleState.EVALUATED.value,
        ):
            raise ConflictError(f"Cannot submit for review from status {inspection.status}")

        # Transition state
        inspection.status = InspectionLifecycleState.SUBMITTED_FOR_REVIEW.value
        inspection.submitted_at = datetime.now(timezone.utc)
        if submit_in and submit_in.notes:
            inspection.notes = f"{inspection.notes or ''}\n[Submission Note]: {submit_in.notes}".strip()

        # Audit Event
        await AuditService.log_event(
            db=db,
            inspection_id=inspection.id,
            actor_id=inspector_id,
            actor_role=UserRole.INSPECTOR.value,
            event_type=AuditEventType.INSPECTION_SUBMITTED_FOR_REVIEW,
            details={
                "case_number": inspection.case_number,
                "rule_set_id": "LMPC-2011-MVP-RULES",
                "rule_set_version": "v1.0",
                "evaluation_version": "v1.0",
                "notes": submit_in.notes if submit_in else None,
            },
        )
        await db.commit()
        await db.refresh(inspection)
        return inspection
