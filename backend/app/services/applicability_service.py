"""
CompliScan LM — Applicability Engine.
Deterministically determines statutory applicability for all Legal Metrology requirements.
"""

from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.inspection import InspectionCase
from backend.app.models.compliance import ApplicabilityResult
from backend.app.models.audit import AuditEvent
from backend.app.services.rules.rule_definitions import (
    RULE_SET_ID,
    RULE_SET_VERSION,
    EVALUATION_VERSION,
    CORE_RULES,
)
from shared.domain.enums import ApplicabilityStatus, OriginStatus, AuditEventType


class ApplicabilityService:
    """
    Deterministic applicability service.
    Evaluates whether statutory declarations are APPLICABLE, NOT_APPLICABLE, or REQUIRES_REVIEW.
    """

    @classmethod
    def evaluate_applicability_context(
        cls,
        inspection: InspectionCase,
    ) -> List[Dict[str, Any]]:
        """
        Pure deterministic computation of applicability for an inspection case.
        Returns list of dictionary payloads for each statutory requirement.
        """
        results = []

        for req_name, rule_meta in CORE_RULES.items():
            if not rule_meta.is_conditional:
                # 6 core domains are unconditionally applicable for packaged commodities
                results.append({
                    "requirement_name": req_name,
                    "status": ApplicabilityStatus.APPLICABLE.value,
                    "basis": (
                        f"Mandatory statutory declaration required for all pre-packaged commodities "
                        f"under Legal Metrology (Packaged Commodities) Rules, 2011, {rule_meta.citation}."
                    ),
                    "rule_citation": rule_meta.citation,
                    "context_used": {
                        "product_name": inspection.product_name,
                        "origin_status": inspection.origin_status,
                        "product_category": inspection.product_category,
                    },
                    "rule_set_id": RULE_SET_ID,
                    "rule_set_version": RULE_SET_VERSION,
                    "evaluation_version": EVALUATION_VERSION,
                })
            else:
                # Conditional requirements (e.g. Country of Origin)
                if req_name == "country_of_origin":
                    origin = inspection.origin_status.upper() if inspection.origin_status else OriginStatus.UNKNOWN.value

                    if origin == OriginStatus.IMPORTED.value:
                        status = ApplicabilityStatus.APPLICABLE.value
                        basis = (
                            "Imported packaged commodity requires mandatory Country of Origin "
                            f"declaration under {rule_meta.citation} (G.S.R. 629(E))."
                        )
                    elif origin == OriginStatus.DOMESTIC.value:
                        status = ApplicabilityStatus.NOT_APPLICABLE.value
                        basis = (
                            "Domestically manufactured/packed commodity is exempt from mandatory "
                            f"Country of Origin declaration under {rule_meta.citation}."
                        )
                    else:  # UNKNOWN
                        status = ApplicabilityStatus.REQUIRES_REVIEW.value
                        basis = (
                            "Commodity origin status is UNKNOWN at inspection context. "
                            f"Officer verification required to determine applicability under {rule_meta.citation}."
                        )

                    results.append({
                        "requirement_name": req_name,
                        "status": status,
                        "basis": basis,
                        "rule_citation": rule_meta.citation,
                        "context_used": {
                            "origin_status": origin,
                            "product_name": inspection.product_name,
                            "product_category": inspection.product_category,
                        },
                        "rule_set_id": RULE_SET_ID,
                        "rule_set_version": RULE_SET_VERSION,
                        "evaluation_version": EVALUATION_VERSION,
                    })

        return results

    @classmethod
    async def evaluate_and_persist(
        cls,
        db: AsyncSession,
        inspection_id: str,
        actor_id: str = "SYSTEM",
    ) -> List[ApplicabilityResult]:
        """
        Evaluates and persists applicability for the given inspection.
        Maintains idempotence via upsert on (inspection_id, requirement_name, evaluation_version).
        """
        # Fetch inspection
        stmt_insp = select(InspectionCase).where(InspectionCase.id == inspection_id)
        inspection = (await db.execute(stmt_insp)).scalar_one_or_none()
        if not inspection:
            raise ValueError(f"Inspection with ID {inspection_id} not found.")

        # Compute applicability
        payloads = cls.evaluate_applicability_context(inspection)

        # Fetch existing records for this inspection and evaluation version
        stmt_existing = select(ApplicabilityResult).where(
            ApplicabilityResult.inspection_id == inspection_id,
            ApplicabilityResult.evaluation_version == EVALUATION_VERSION,
        )
        existing_rows = {row.requirement_name: row for row in (await db.execute(stmt_existing)).scalars().all()}

        persisted_records: List[ApplicabilityResult] = []

        for p in payloads:
            req_name = p["requirement_name"]
            if req_name in existing_rows:
                record = existing_rows[req_name]
                record.status = p["status"]
                record.basis = p["basis"]
                record.rule_citation = p["rule_citation"]
                record.context_used = p["context_used"]
                record.rule_set_id = p["rule_set_id"]
                record.rule_set_version = p["rule_set_version"]
            else:
                record = ApplicabilityResult(
                    inspection_id=inspection_id,
                    requirement_name=req_name,
                    status=p["status"],
                    basis=p["basis"],
                    rule_citation=p["rule_citation"],
                    context_used=p["context_used"],
                    rule_set_id=p["rule_set_id"],
                    rule_set_version=p["rule_set_version"],
                    evaluation_version=p["evaluation_version"],
                )
                db.add(record)
            persisted_records.append(record)

        await db.flush()

        # Emit audit event
        audit = AuditEvent(
            inspection_id=inspection_id,
            event_type=AuditEventType.APPLICABILITY_EVALUATED.value,
            actor_id=actor_id,
            details={
                "rule_set_id": RULE_SET_ID,
                "rule_set_version": RULE_SET_VERSION,
                "evaluation_version": EVALUATION_VERSION,
                "total_requirements": len(persisted_records),
                "applicable_count": sum(1 for r in persisted_records if r.status == ApplicabilityStatus.APPLICABLE.value),
                "not_applicable_count": sum(1 for r in persisted_records if r.status == ApplicabilityStatus.NOT_APPLICABLE.value),
                "requires_review_count": sum(1 for r in persisted_records if r.status == ApplicabilityStatus.REQUIRES_REVIEW.value),
            },
        )
        db.add(audit)
        await db.flush()

        return persisted_records

    @classmethod
    async def get_inspection_applicability(
        cls,
        db: AsyncSession,
        inspection_id: str,
    ) -> List[ApplicabilityResult]:
        """
        Retrieves persisted applicability results for an inspection.
        """
        stmt = (
            select(ApplicabilityResult)
            .where(
                ApplicabilityResult.inspection_id == inspection_id,
                ApplicabilityResult.evaluation_version == EVALUATION_VERSION,
            )
            .order_by(ApplicabilityResult.requirement_name)
        )
        return list((await db.execute(stmt)).scalars().all())
