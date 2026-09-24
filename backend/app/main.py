"""
CompliScan LM — FastAPI Application Entry Point.
"""

from contextlib import asynccontextmanager
import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.errors import AppError, app_error_handler
from backend.app.db.session import async_engine, AsyncSessionLocal
from backend.app.api.v1 import api_v1_router
from backend.app.services.analysis_job_service import AnalysisJobService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("compliscan")


async def _embedded_worker_loop():
    """
    Background worker loop embedded within FastAPI application process.
    Automatically claims and processes pending analysis jobs (Quality, Perception/OCR, Extraction).
    """
    logger.info("Embedded background worker loop initialized.")
    while True:
        try:
            async with AsyncSessionLocal() as db:
                processed = await AnalysisJobService.run_pending_jobs_inline(
                    db, worker_id="embedded-api-worker"
                )
                if processed > 0:
                    logger.info(f"[Embedded Worker] Processed {processed} job(s)")
        except asyncio.CancelledError:
            logger.info("Embedded worker task shutting down.")
            break
        except Exception as e:
            logger.error(f"[Embedded Worker] Error during job execution: {e}")

        await asyncio.sleep(settings.WORKER_POLL_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Schema is managed exclusively by Alembic migrations.
    logger.info("CompliScan LM starting up — schema managed by Alembic.")
    worker_task = asyncio.create_task(_embedded_worker_loop())
    try:
        yield
    finally:
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass
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
    allow_origin_regex=r"https://.*\.vercel\.app",
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
