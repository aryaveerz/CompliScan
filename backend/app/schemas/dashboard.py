"""
CompliScan LM — Dashboard Metrics Schemas.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, ConfigDict


class GovernanceMetrics(BaseModel):
    avg_review_turnaround_seconds: Optional[float] = None
    revision_count: int = 0
    correction_count: int = 0
    override_count: int = 0


class DashboardMetricsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date_range: str
    category: Optional[str] = None
    total_inspections: int
    total_finalized: int
    active_inspections: int
    in_verification_count: int
    submitted_for_review_count: int
    requires_revision_count: int
    compliance_rate_percent: float
    status_counts: Dict[str, int]
    compliance_distribution: Dict[str, int]
    origin_distribution: Dict[str, int]
    rule_violation_counts: Dict[str, int]
    governance_metrics: GovernanceMetrics
