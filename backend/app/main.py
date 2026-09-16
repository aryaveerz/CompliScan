"""
CompliScan LM — FastAPI Application Entry Point.
"""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from backend.app.core.config import settings
from backend.app.core.errors import AppError, app_error_handler
from backend.app.db.base import Base
from backend.app.db.session import async_engine, AsyncSessionLocal
from backend.app.api.v1 import api_v1_router
from backend.app.models.user import User
from backend.app.core.security import get_password_hash
from shared.domain.enums import UserRole

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("compliscan")


async def seed_initial_users():
    """Seed initial development test users (Inspector and Reviewer) if not present."""
    async with AsyncSessionLocal() as session:
        # Check Inspector
        stmt_insp = select(User).where(User.email == "inspector@compliscan.gov.in")
        res_insp = await session.execute(stmt_insp)
        if not res_insp.scalar_one_or_none():
            inspector = User(
                email="inspector@compliscan.gov.in",
                hashed_password=get_password_hash("Password123!"),
                full_name="Rajesh Sharma (Inspector)",
                role=UserRole.INSPECTOR.value,
                is_active=True,
            )
            session.add(inspector)

        # Check Reviewer
        stmt_rev = select(User).where(User.email == "reviewer@compliscan.gov.in")
        res_rev = await session.execute(stmt_rev)
        if not res_rev.scalar_one_or_none():
            reviewer = User(
                email="reviewer@compliscan.gov.in",
                hashed_password=get_password_hash("Password123!"),
                full_name="Priya Patel (Reviewing Officer)",
                role=UserRole.REVIEWER.value,
                is_active=True,
            )
            session.add(reviewer)

        await session.commit()
        logger.info("Database initialized with seed users.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_initial_users()
    yield
    # Shutdown
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
