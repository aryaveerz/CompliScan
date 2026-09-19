"""
CompliScan LM — Inspection Finalization Service (Async).
Constructs the immutable FinalAuditRecord snapshot and transitions inspection to READ_ONLY.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.inspection import InspectionCase
from backend.app.models.evidence import EvidenceAsset
from backend.app.models.structured_declaration import StructuredDeclarationResult
from backend.app.models.compliance import ApplicabilityResult, ComplianceFinding
from backend.app.models.reviewer import ReviewerDecision
from backend.app.models.evidence_request import EvidenceRequest
from backend.app.models.final_audit import FinalAuditRecord
from backend.app.schemas.reviewer import FinalizeInspectionRequest
from backend.app.services.audit_service import AuditService
from backend.app.core.errors import (
    NotFoundError,
    ForbiddenError,
    ConflictError,
    ValidationError,
)
from shared.domain.states import InspectionLifecycleState, ProcessingState, FinalizationStatus
from shared.domain.enums import AuditEventType, EvidenceRequestStatus, ApplicabilityStatus, UserRole


class FinalizationService:

    @classmethod
    async def finalize_inspection(
        cls,
        db: AsyncSession,
        inspection_id: str,
        reviewer_id: str,
        finalize_in: FinalizeInspectionRequest,
    ) -> FinalAuditRecord:
        stmt_insp = select(InspectionCase).where(InspectionCase.id == inspection_id)
        inspection = (await db.execute(stmt_insp)).scalar_one_or_none()
        if not inspection:
            raise NotFoundError(f"Inspection {inspection_id} not found")

        # Idempotency / Immutability check
        if (
            inspection.finalization_status == FinalizationStatus.READ_ONLY.value
            or inspection.status == InspectionLifecycleState.FINALIZED.value
        ):
            stmt_far = select(FinalAuditRecord).where(FinalAuditRecord.inspection_id == inspection_id)
            existing_far = (await db.execute(stmt_far)).scalar_one_or_none()
            if existing_far:
                raise ConflictError("Inspection is already finalized and immutable (READ_ONLY)")
            raise ConflictError("Inspection is in finalized state")

        # 1. State must be SUBMITTED_FOR_REVIEW
        if inspection.status != InspectionLifecycleState.SUBMITTED_FOR_REVIEW.value:
            raise ConflictError(
                f"Cannot finalize inspection in status '{inspection.status}'. Must be in SUBMITTED_FOR_REVIEW."
            )

        # 2. No active processing
        if inspection.processing_state == ProcessingState.PROCESSING.value:
            raise ConflictError("Cannot finalize while perception or evaluation analysis is processing")

        # 3. No open evidence requests
        stmt_ers = select(EvidenceRequest).where(
            EvidenceRequest.inspection_id == inspection_id,
            EvidenceRequest.status == EvidenceRequestStatus.OPEN.value,
        )
        open_ers = (await db.execute(stmt_ers)).scalars().all()
        if open_ers:
            raise ValidationError(
                f"Cannot finalize: {len(open_ers)} open evidence request(s) must be fulfilled or resolved first"
            )

        # 4. Must have evidence assets
        stmt_ev = select(EvidenceAsset).where(
            EvidenceAsset.inspection_id == inspection_id,
        )
        evidence_assets = (await db.execute(stmt_ev)).scalars().all()
        if not evidence_assets:
            raise ValidationError("Cannot finalize: No accepted visual evidence assets found")

        # 5. Must have applicability evaluation
        stmt_app = select(ApplicabilityResult).where(ApplicabilityResult.inspection_id == inspection_id)
        applicability_rows = (await db.execute(stmt_app)).scalars().all()
        if not applicability_rows:
            raise ValidationError("Cannot finalize: Applicability evaluation has not been performed")

        # 6. Must have compliance findings
        stmt_find = select(ComplianceFinding).where(ComplianceFinding.inspection_id == inspection_id)
        finding_rows = (await db.execute(stmt_find)).scalars().all()
        if not finding_rows:
            raise ValidationError("Cannot finalize: Compliance findings have not been generated")

        # 7. Reviewer decisions must exist for all findings
        stmt_rd = select(ReviewerDecision).where(ReviewerDecision.inspection_id == inspection_id)
        reviewer_decisions = (await db.execute(stmt_rd)).scalars().all()
        adjudicated_requirements = {rd.requirement_name for rd in reviewer_decisions}
        finding_requirements = {f.requirement_name for f in finding_rows}

        missing_decisions = finding_requirements - adjudicated_requirements
        if missing_decisions:
            raise ValidationError(
                f"Cannot finalize: Missing reviewer decisions for requirements: {', '.join(sorted(missing_decisions))}"
            )

        # 8. Declarations
        stmt_decl = select(StructuredDeclarationResult).where(
            StructuredDeclarationResult.inspection_id == inspection_id
        )
        decl_rows = (await db.execute(stmt_decl)).scalars().all()

        now = datetime.now(timezone.utc)

        # Build Immutable JSON Snapshots
        inspection_context_snapshot = {
            "id": inspection.id,
            "case_number": inspection.case_number,
            "product_name": inspection.product_name,
            "origin_status": inspection.origin_status,
            "product_category": inspection.product_category,
            "reference_url": inspection.reference_url,
            "notes": inspection.notes,
            "created_by_id": inspection.created_by_id,
            "created_at": inspection.created_at.isoformat() if inspection.created_at else None,
            "submitted_at": inspection.submitted_at.isoformat() if inspection.submitted_at else None,
        }

        evidence_snapshot = [
            {
                "id": e.id,
                "original_filename": e.original_filename,
                "mime_type": e.mime_type,
                "evidence_type": e.evidence_type,
                "file_size_bytes": e.file_size_bytes,
                "sha256_hash": e.sha256_hash,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in evidence_assets
        ]

        source_evidence_hashes = {e.id: e.sha256_hash for e in evidence_assets}

        declaration_snapshot = {
            d.evidence_id: {
                "id": d.id,
                "raw_declarations": d.raw_declarations,
                "normalized_declarations": d.normalized_declarations,
                "model_name": d.model_name,
                "prompt_version": d.prompt_version,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in decl_rows
        }

        applicability_snapshot = [
            {
                "id": a.id,
                "requirement_name": a.requirement_name,
                "status": a.status,
                "basis": a.basis,
                "rule_citation": a.rule_citation,
                "context_used": a.context_used,
            }
            for a in applicability_rows
        ]

        compliance_findings_snapshot = [
            {
                "id": f.id,
                "evidence_id": f.evidence_id,
                "requirement_name": f.requirement_name,
                "result": f.result,
                "reason": f.reason,
                "applicability_status": f.applicability_status,
                "rule_citation": f.rule_citation,
                "source_token_indices": f.source_token_indices,
            }
            for f in finding_rows
        ]

        reviewer_decisions_snapshot = [
            {
                "id": rd.id,
                "requirement_name": rd.requirement_name,
                "determination": rd.determination,
                "original_result": rd.original_result,
                "adjudicated_result": rd.adjudicated_result,
                "is_override": rd.is_override,
                "rationale": rd.rationale,
                "reviewer_id": rd.reviewer_id,
                "created_at": rd.created_at.isoformat() if rd.created_at else None,
            }
            for rd in reviewer_decisions
        ]

        audit_metadata = {
            "finalized_by": reviewer_id,
            "finalized_at": now.isoformat(),
            "total_evidence_count": len(evidence_assets),
            "total_findings_count": len(finding_rows),
            "total_reviewer_decisions_count": len(reviewer_decisions),
        }

        # Create FinalAuditRecord
        far = FinalAuditRecord(
            inspection_id=inspection_id,
            finalized_by_id=reviewer_id,
            finalized_at=now,
            final_decision=finalize_in.final_decision.value if hasattr(finalize_in.final_decision, "value") else str(finalize_in.final_decision),
            final_rationale=finalize_in.final_rationale,
            inspection_context_snapshot=inspection_context_snapshot,
            evidence_snapshot=evidence_snapshot,
            declaration_snapshot=declaration_snapshot,
            applicability_snapshot=applicability_snapshot,
            compliance_findings_snapshot=compliance_findings_snapshot,
            reviewer_decisions_snapshot=reviewer_decisions_snapshot,
            rule_set_id="LMPC-2011-MVP-RULES",
            rule_set_version="v1.0",
            evaluation_version="v1.0",
            source_evidence_hashes=source_evidence_hashes,
            audit_metadata=audit_metadata,
        )
        db.add(far)

        # Mutate Inspection to FINALIZED + READ_ONLY
        inspection.status = InspectionLifecycleState.FINALIZED.value
        inspection.finalization_status = FinalizationStatus.READ_ONLY.value
        inspection.finalized_at = now
        inspection.reviewer_id = reviewer_id

        # Log Finalized Audit Event
        await AuditService.log_event(
            db=db,
            inspection_id=inspection.id,
            actor_id=reviewer_id,
            actor_role=UserRole.REVIEWER.value,
            event_type=AuditEventType.INSPECTION_FINALIZED,
            details={
                "final_audit_record_id": far.id,
                "final_decision": far.final_decision,
                "final_rationale": far.final_rationale,
                "evidence_count": len(evidence_assets),
                "evaluation_version": "v1.0",
                "rule_set_version": "v1.0",
            },
        )

        await db.commit()
        await db.refresh(far)
        return far

    @classmethod
    async def get_final_record(cls, db: AsyncSession, inspection_id: str) -> FinalAuditRecord:
        stmt = select(FinalAuditRecord).where(FinalAuditRecord.inspection_id == inspection_id)
        far = (await db.execute(stmt)).scalar_one_or_none()
        if not far:
            raise NotFoundError(f"Final audit record for inspection {inspection_id} not found")
        return far
