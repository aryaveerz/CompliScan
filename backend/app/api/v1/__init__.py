"""
CompliScan LM — API v1 Router Aggregator.
"""

from fastapi import APIRouter
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.inspections import router as inspections_router
from backend.app.api.v1.evidence import router as evidence_router
from backend.app.api.v1.health import router as health_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(inspections_router)
api_v1_router.include_router(evidence_router)
