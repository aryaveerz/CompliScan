"""
CompliScan LM — Test Configuration and Fixtures.
Provides an explicit mock Supabase Auth provider and local test database isolation.
"""

import os
import sys

# Force local SQLite test databases for automated test suite execution
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./compliscan_test.db"
os.environ["SYNC_DATABASE_URL"] = "sqlite:///./compliscan_test.db"
os.environ["ENVIRONMENT"] = "test"
os.environ["SUPABASE_JWT_SECRET"] = "compliscan_test_secret_key_for_offline_validation_only"

# Rebind settings to ensure environment overrides take effect
from backend.app.core.config import settings
settings.DATABASE_URL = "sqlite+aiosqlite:///./compliscan_test.db"
settings.SYNC_DATABASE_URL = "sqlite:///./compliscan_test.db"
settings.SUPABASE_JWT_SECRET = "compliscan_test_secret_key_for_offline_validation_only"

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.app.db import session as db_session

# Ensure session engines use test SQLite database
test_sync_engine = create_engine(settings.SYNC_DATABASE_URL, echo=False, future=True)
test_async_engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

db_session.sync_engine = test_sync_engine
db_session.async_engine = test_async_engine
db_session.AsyncSessionLocal = async_sessionmaker(
    bind=test_async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

from datetime import datetime, timedelta, timezone
import uuid
from typing import Dict, Any
import pytest
from jose import jwt
from backend.app.services.supabase_auth_client import supabase_auth_client
from backend.app.core.errors import UnauthorizedError, AppError
from shared.domain.constants import ErrorCode
from backend.app.db.base import Base
import backend.app.models  # ensure all models registered on Base.metadata

@pytest.fixture(autouse=True)
def setup_test_database():
    """Create clean isolated schema for every test synchronously."""
    Base.metadata.drop_all(bind=test_sync_engine)
    Base.metadata.create_all(bind=test_sync_engine)
    yield
    Base.metadata.drop_all(bind=test_sync_engine)


def create_test_supabase_token(user_id: str, email: str = "test@example.com") -> str:
    """
    Generate a valid signed Supabase-format JWT for OFFLINE MOCKED tests using the
    test SUPABASE_JWT_SECRET set at the top of this conftest.

    Offline vs smoke test boundary
    --------------------------------
    - Tests in this file / test_supabase_auth.py are OFFLINE tests: they never
      contact a real Supabase project and use the mock fixtures below.
    - Real-Supabase smoke tests (to be added later) must live in a separate
      file (e.g. tests/smoke/test_supabase_smoke.py) and be gated by an
      explicit SUPABASE_SMOKE env variable so CI never depends on live auth.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "aud": settings.SUPABASE_AUTH_AUDIENCE or "authenticated",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=1)).timestamp()),
    }
    if settings.SUPABASE_URL:
        payload["iss"] = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1"

    # Strictly use SUPABASE_JWT_SECRET — same rule as production verification.
    # The test secret is set at the top of this file to an explicit offline value.
    secret = settings.SUPABASE_JWT_SECRET
    if not secret:
        raise RuntimeError(
            "SUPABASE_JWT_SECRET must be set for test token generation. "
            "Check conftest.py environment setup."
        )
    return jwt.encode(payload, secret, algorithm="HS256")


@pytest.fixture(autouse=True)
def mock_supabase_auth(monkeypatch):
    """
    Explicit mock Supabase Auth provider for local offline test suite.
    Decouples test execution from external cloud network calls while testing the full
    FastAPI registration, login, token resolution, and RBAC authorization flow.
    """
    mock_users: Dict[str, Dict[str, Any]] = {}

    async def mock_sign_up(email: str, password: str, user_metadata=None):
        email_clean = email.lower().strip()
        if email_clean in mock_users:
            raise AppError(code=ErrorCode.VALIDATION_ERROR, message="User already registered", status_code=400)

        user_id = str(uuid.uuid4())
        mock_users[email_clean] = {
            "id": user_id,
            "email": email_clean,
            "password": password,
            "user_metadata": user_metadata or {},
        }
        token = create_test_supabase_token(user_id=user_id, email=email_clean)
        return {
            "user": {"id": user_id, "email": email_clean, "user_metadata": user_metadata},
            "session": {"access_token": token, "token_type": "bearer"},
        }

    async def mock_sign_in(email: str, password: str):
        email_clean = email.lower().strip()
        user = mock_users.get(email_clean)
        if not user or user["password"] != password:
            raise UnauthorizedError("Invalid email or password")

        token = create_test_supabase_token(user_id=user["id"], email=email_clean)
        return {
            "access_token": token,
            "user": {"id": user["id"], "email": email_clean},
            "session": {"access_token": token, "token_type": "bearer"},
        }

    async def mock_admin_create_user(email: str, password: str, user_metadata=None, email_confirm=True):
        email_clean = email.lower().strip()
        user_id = str(uuid.uuid4())
        mock_users[email_clean] = {
            "id": user_id,
            "email": email_clean,
            "password": password,
            "user_metadata": user_metadata or {},
        }
        return {
            "user": {"id": user_id, "email": email_clean, "user_metadata": user_metadata},
        }

    async def mock_delete_user(user_id: str) -> None:
        """Stub delete_user — removes identity from the in-memory mock registry if present."""
        # Find and remove by user_id value
        to_remove = [email for email, u in mock_users.items() if u["id"] == str(user_id)]
        for email in to_remove:
            del mock_users[email]

    monkeypatch.setattr(supabase_auth_client, "sign_up", mock_sign_up)
    monkeypatch.setattr(supabase_auth_client, "sign_in_with_password", mock_sign_in)
    monkeypatch.setattr(supabase_auth_client, "admin_create_user", mock_admin_create_user)
    monkeypatch.setattr(supabase_auth_client, "delete_user", mock_delete_user)
