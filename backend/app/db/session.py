"""
CompliScan LM — Database Session Management.
Supports async operations for FastAPI routes and sync engine for migrations/scripts.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings

# Prepare async connect_args (PgBouncer compatibility for Supabase transaction pooler)
async_connect_args = {}
if "postgresql" in settings.DATABASE_URL or "postgres" in settings.DATABASE_URL:
    # Disable prepared statement caches when using PgBouncer transaction pooling (port 6543)
    async_connect_args["statement_cache_size"] = 0
    async_connect_args["prepared_statement_cache_size"] = 0

# Async Engine (for FastAPI routes)
# pool_pre_ping: validates connection before use — catches dead/stale connections
#   immediately and transparently reconnects instead of returning a 500.
# pool_recycle: recycle connections every 300 s (5 min), well under Supabase's
#   ~10 min idle timeout, so we never hand out a connection the server has closed.
# pool_size / max_overflow: bound the number of open connections to Supabase.
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    connect_args=async_connect_args,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# Sync Engine (for Alembic / migrations / synchronous utility scripts)
sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
