"""
CompliScan LM — FastAPI Application Entry Point.
"""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.errors import AppError, app_error_handler
from backend.app.db.session import async_engine
from backend.app.api.v1 import api_v1_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("compliscan")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Schema is managed exclusively by Alembic migrations.
    # Base.metadata.create_all is intentionally absent from production startup.
    logger.info("CompliScan LM starting up — schema managed by Alembic.")
    yield
    # Shutdown: release database connection pool
    await async_engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description="Legal Metrology Packaged Commodities Compliance Scanning System (PS ID 26034)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Error Handlers
app.add_exception_handler(AppError, app_error_handler)

# Mount API v1 router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": "CompliScan LM API is running",
        "api_v1": f"{settings.API_V1_STR}",
        "documentation": "/docs",
    }
