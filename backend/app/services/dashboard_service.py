"""
CompliScan LM — Dashboard Service.
Computes fast, authoritative database aggregations for the Operational & Executive Compliance Dashboard.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, distinct, case
from backend.app.models.inspection import InspectionCase
from backend.app.models.final_audit import FinalAuditRecord
from backend.app.models.compliance import ComplianceFinding
from backend.app.models.audit import AuditEvent
from backend.app.models.user import User
from backend.app.schemas.dashboard import DashboardMetricsResponse, GovernanceMetrics
from shared.domain.states import InspectionLifecycleState, FinalizationStatus
from shared.domain.enums import UserRole, AuditEventType, ComplianceResult, FinalDecision


class DashboardService:
    """
    Computes real-time operational and compliance metrics directly from PostgreSQL.
    """

    @classmethod
    async def get_metrics(
        cls,
        db: AsyncSession,
        current_user: User,
        date_range: str = "30d",
        category: Optional[str] = None,
    ) -> DashboardMetricsResponse:
        now = datetime.now(timezone.utc)
        since_date: Optional[datetime] = None

        if date_range == "7d":
            since_date = now - timedelta(days=7)
        elif date_range == "30d":
            since_date = now - timedelta(days=30)
        elif date_range == "90d":
            since_date = now - timedelta(days=90)
        # "all" leaves since_date as None

        # Build base filters on InspectionCase
        filters = []
        if since_date is not None:
            filters.append(InspectionCase.created_at >= since_date)
        if category and category.strip():
            filters.append(func.lower(InspectionCase.product_category) == category.strip().lower())
        if current_user.role == UserRole.INSPECTOR.value:
            filters.append(InspectionCase.created_by_id == current_user.id)

        base_filter = and_(*filters) if filters else True

        # 1. Total Inspections & Status breakdown
        stmt_status = (
            select(
                InspectionCase.status,
                func.count(InspectionCase.id).label("count")
            )
            .where(base_filter)
            .group_by(InspectionCase.status)
        )
        res_status = await db.execute(stmt_status)
        status_counts: Dict[str, int] = {row[0]: row[1] for row in res_status.all()}

        total_inspections = sum(status_counts.values())

        # Specific status counts
        active_states = {
            InspectionLifecycleState.DRAFT.value,
            InspectionLifecycleState.EVIDENCE_UPLOADED.value,
            InspectionLifecycleState.EXTRACTED.value,
            InspectionLifecycleState.APPLICABILITY_EVALUATED.value,
            InspectionLifecycleState.EVALUATED.value,
        }
        active_inspections = sum(status_counts.get(s, 0) for s in active_states)
        in_verification_count = status_counts.get(InspectionLifecycleState.IN_VERIFICATION.value, 0)
        submitted_for_review_count = status_counts.get(InspectionLifecycleState.SUBMITTED_FOR_REVIEW.value, 0)
        requires_revision_count = status_counts.get(InspectionLifecycleState.REQUIRES_REVISION.value, 0)
        total_finalized = status_counts.get(InspectionLifecycleState.FINALIZED.value, 0)

        # 2. Compliance Distribution (from FinalAuditRecord for finalized inspections in scope)
        stmt_comp = (
            select(
                FinalAuditRecord.final_decision,
                func.count(FinalAuditRecord.id).label("count")
            )
            .join(InspectionCase, FinalAuditRecord.inspection_id == InspectionCase.id)
            .where(base_filter)
            .group_by(FinalAuditRecord.final_decision)
        )
        res_comp = await db.execute(stmt_comp)
        compliance_distribution: Dict[str, int] = {row[0]: row[1] for row in res_comp.all()}

        compliant_count = compliance_distribution.get(FinalDecision.COMPLIANT.value, 0)
        compliance_rate = round((compliant_count / total_finalized * 100), 1) if total_finalized > 0 else 0.0

        # 3. Origin Distribution
        stmt_origin = (
            select(
                InspectionCase.origin_status,
                func.count(InspectionCase.id).label("count")
            )
            .where(base_filter)
            .group_by(InspectionCase.origin_status)
        )
        res_origin = await db.execute(stmt_origin)
        origin_distribution: Dict[str, int] = {row[0]: row[1] for row in res_origin.all()}

        # 4. Rule Non-Compliance / Violation Citations
        # Aggregates from ComplianceFinding where result is POTENTIAL_NON_COMPLIANCE or REQUIRES_REVIEW
        stmt_rules = (
            select(
                ComplianceFinding.rule_citation,
                func.count(ComplianceFinding.id).label("count")
            )
            .join(InspectionCase, ComplianceFinding.inspection_id == InspectionCase.id)
            .where(
                and_(
                    base_filter,
                    ComplianceFinding.result.in_([
                        ComplianceResult.POTENTIAL_NON_COMPLIANCE.value,
                        ComplianceResult.REQUIRES_REVIEW.value,
                    ])
                )
            )
            .group_by(ComplianceFinding.rule_citation)
            .order_by(func.count(ComplianceFinding.id).desc())
        )
        res_rules = await db.execute(stmt_rules)
        rule_violation_counts: Dict[str, int] = {row[0]: row[1] for row in res_rules.all() if row[0]}

        # 5. Governance Metrics (Turnaround, Revision count, Correction count, Override count)
        # Turnaround calculation for finalized cases
        stmt_turnaround = (
            select(InspectionCase.submitted_at, InspectionCase.finalized_at)
            .where(
                and_(
                    base_filter,
                    InspectionCase.status == InspectionLifecycleState.FINALIZED.value,
                    InspectionCase.submitted_at.is_not(None),
                    InspectionCase.finalized_at.is_not(None),
                )
            )
        )
        res_turnaround = await db.execute(stmt_turnaround)
        turnaround_rows = res_turnaround.all()

        if turnaround_rows:
            deltas = [
                (f_at - s_at).total_seconds()
                for s_at, f_at in turnaround_rows
                if f_at and s_at and (f_at >= s_at)
            ]
            avg_turnaround_seconds = round(sum(deltas) / len(deltas), 1) if deltas else None
        else:
            avg_turnaround_seconds = None

        # Audit events in scope
        # Subquery of matching inspection IDs to respect RBAC and date range
        matching_inspections_subq = select(InspectionCase.id).where(base_filter)

        stmt_audit_counts = (
            select(
                AuditEvent.event_type,
                func.count(AuditEvent.id).label("count")
            )
            .where(
                and_(
                    AuditEvent.inspection_id.in_(matching_inspections_subq),
                    AuditEvent.event_type.in_([
                        AuditEventType.REVIEW_REVISION_REQUESTED.value,
                        AuditEventType.DECLARATION_CORRECTED.value,
                        AuditEventType.DECLARATION_MANUALLY_CORRECTED.value,
                        AuditEventType.REVIEWER_OVERRIDE_RECORDED.value,
                    ])
                )
            )
            .group_by(AuditEvent.event_type)
        )
        res_audit = await db.execute(stmt_audit_counts)
        audit_counts_map = {row[0]: row[1] for row in res_audit.all()}

        revision_count = audit_counts_map.get(AuditEventType.REVIEW_REVISION_REQUESTED.value, 0)
        correction_count = (
            audit_counts_map.get(AuditEventType.DECLARATION_CORRECTED.value, 0) +
            audit_counts_map.get(AuditEventType.DECLARATION_MANUALLY_CORRECTED.value, 0)
        )
        override_count = audit_counts_map.get(AuditEventType.REVIEWER_OVERRIDE_RECORDED.value, 0)

        governance = GovernanceMetrics(
            avg_review_turnaround_seconds=avg_turnaround_seconds,
            revision_count=revision_count,
            correction_count=correction_count,
            override_count=override_count,
        )

        return DashboardMetricsResponse(
            date_range=date_range,
            category=category,
            total_inspections=total_inspections,
            total_finalized=total_finalized,
            active_inspections=active_inspections,
            in_verification_count=in_verification_count,
            submitted_for_review_count=submitted_for_review_count,
            requires_revision_count=requires_revision_count,
            compliance_rate_percent=compliance_rate,
            status_counts=status_counts,
            compliance_distribution=compliance_distribution,
            origin_distribution=origin_distribution,
            rule_violation_counts=rule_violation_counts,
            governance_metrics=governance,
        )
