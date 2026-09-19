"""
CompliScan LM — API v1 Router Aggregator.
"""

from fastapi import APIRouter
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.inspections import router as inspections_router
from backend.app.api.v1.evidence import router as evidence_router
from backend.app.api.v1.compliance import router as compliance_router
from backend.app.api.v1.verification import router as verification_router
from backend.app.api.v1.reviews import router as reviews_router
from backend.app.api.v1.dashboard import router as dashboard_router
from backend.app.api.v1.health import router as health_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(inspections_router)
api_v1_router.include_router(evidence_router)
api_v1_router.include_router(compliance_router)
api_v1_router.include_router(verification_router)
api_v1_router.include_router(reviews_router)
api_v1_router.include_router(dashboard_router)
