"""
CompliScan LM — Focused Supabase Auth Migration Test Suite.
Verifies Supabase identity delegation, 1:1 UUID mapping, null password storage,
strict JWT claim validation, and database-authoritative RBAC resolution.
"""

from datetime import datetime, timedelta, timezone
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from jose import jwt
from sqlalchemy import select
from backend.app.main import app
from backend.app.core.config import settings
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.user import User
from backend.tests.conftest import create_test_supabase_token
from shared.domain.enums import UserRole


@pytest.mark.asyncio
async def test_supabase_registration_stores_null_password_and_1to1_uuid():
    """Verify registration delegates to Supabase Auth and stores hashed_password as NULL."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/v1/auth/register", json={
            "email": "new_inspector@compliscan.gov.in",
            "password": "SecurePassword123!",
            "full_name": "New Inspector",
            "role": "INSPECTOR",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        user_id = data["user"]["id"]
        assert data["user"]["email"] == "new_inspector@compliscan.gov.in"
        assert data["user"]["role"] == "INSPECTOR"

        # Direct database inspection
        async with AsyncSessionLocal() as session:
            stmt = select(User).where(User.id == user_id)
            res = await session.execute(stmt)
            db_user = res.scalar_one_or_none()
            assert db_user is not None
            assert db_user.id == user_id
            # Verify hashed_password is NULL in database (no passwords stored in public.users)
            assert db_user.hashed_password is None
            assert db_user.role == UserRole.INSPECTOR.value
            assert db_user.is_active is True


@pytest.mark.asyncio
async def test_supabase_login_success_and_failure():
    """Verify login delegates credential check to Supabase Auth."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register user
        reg_resp = await client.post("/api/v1/auth/register", json={
            "email": "login_test@compliscan.gov.in",
            "password": "CorrectPassword123!",
            "full_name": "Login Test User",
            "role": "INSPECTOR",
        })
        assert reg_resp.status_code == 201

        # Successful login
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "login_test@compliscan.gov.in",
            "password": "CorrectPassword123!",
        })
        assert login_resp.status_code == 200
        assert "access_token" in login_resp.json()

        # Failed login with incorrect password
        bad_login = await client.post("/api/v1/auth/login", json={
            "email": "login_test@compliscan.gov.in",
            "password": "WrongPassword!",
        })
        assert bad_login.status_code == 401


@pytest.mark.asyncio
async def test_jwt_claim_validation_enforcement():
    """Verify token signature, expiration, audience, and subject requirements."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create user in db
        user_id = str(uuid.uuid4())
        async with AsyncSessionLocal() as session:
            user = User(
                id=user_id,
                email="claim_test@compliscan.gov.in",
                hashed_password=None,
                full_name="Claim Test User",
                role=UserRole.INSPECTOR.value,
                is_active=True,
            )
            session.add(user)
            await session.commit()

        # 1. Valid Token -> 200 OK
        valid_token = create_test_supabase_token(user_id=user_id, email="claim_test@compliscan.gov.in")
        res_valid = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {valid_token}"})
        assert res_valid.status_code == 200
        assert res_valid.json()["id"] == user_id

        # 2. Tampered Signature -> 401
        # Use test SUPABASE_JWT_SECRET — same key the verifier will use.
        # SECRET_KEY is deliberately NOT used; that fallback has been removed.
        secret = settings.SUPABASE_JWT_SECRET
        tampered_token = jwt.encode(
            {"sub": user_id, "aud": "authenticated", "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())},
            "wrong_signature_secret",
            algorithm="HS256",
        )
        res_tampered = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tampered_token}"})
        assert res_tampered.status_code == 401

        # 3. Expired Token -> 401
        expired_token = jwt.encode(
            {"sub": user_id, "aud": "authenticated", "exp": int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp())},
            secret,  # same secret — expired, not tampered
            algorithm="HS256",
        )
        res_expired = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
        assert res_expired.status_code == 401

        # 4. Invalid Audience -> 401
        bad_aud_token = jwt.encode(
            {"sub": user_id, "aud": "wrong_audience", "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())},
            secret,
            algorithm="HS256",
        )
        res_bad_aud = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {bad_aud_token}"})
        assert res_bad_aud.status_code == 401

        # 5. Missing / Empty Sub -> 401
        no_sub_token = jwt.encode(
            {"sub": "", "aud": "authenticated", "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())},
            secret,
            algorithm="HS256",
        )
        res_no_sub = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {no_sub_token}"})
        assert res_no_sub.status_code == 401


@pytest.mark.asyncio
async def test_rbac_resolved_from_database_never_token_claim():
    """
    CRITICAL QUALITY GATE:
    Verify that an attacker forging a 'role: REVIEWER' claim in their Supabase JWT
    is STILL restricted to their database role (INSPECTOR).
    Authority resides strictly in public.users.role.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create an INSPECTOR in database
        inspector_id = str(uuid.uuid4())
        async with AsyncSessionLocal() as session:
            user = User(
                id=inspector_id,
                email="genuine_inspector@compliscan.gov.in",
                hashed_password=None,
                full_name="Genuine Inspector",
                role=UserRole.INSPECTOR.value,
                is_active=True,
            )
            session.add(user)
            await session.commit()

        # Forge token containing 'role: REVIEWER' in the JWT payload
        now = datetime.now(timezone.utc)
        forged_payload = {
            "sub": inspector_id,
            "email": "genuine_inspector@compliscan.gov.in",
            "role": "REVIEWER",  # Forged role claim
            "aud": "authenticated",
            "iss": f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1" if settings.SUPABASE_URL else None,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=1)).timestamp()),
        }
        # Use test SUPABASE_JWT_SECRET — same key the verifier will use.
        secret = settings.SUPABASE_JWT_SECRET
        forged_token = jwt.encode(forged_payload, secret, algorithm="HS256")

        # 1. /api/v1/auth/me must return genuine database role (INSPECTOR), not forged claim
        res_me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {forged_token}"})
        assert res_me.status_code == 200
        assert res_me.json()["role"] == "INSPECTOR"

        # 2. Inspector CAN create inspection
        payload = {
            "product_name": "Authentic Ghee 1L",
            "origin_status": "DOMESTIC",
            "product_category": "Dairy",
        }
        res_create = await client.post(
            "/api/v1/inspections",
            json=payload,
            headers={"Authorization": f"Bearer {forged_token}"},
        )
        assert res_create.status_code == 201


@pytest.mark.asyncio
async def test_inactive_user_rejected():
    """Verify that an inactive user cannot access endpoints even with a valid token."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        inactive_user_id = str(uuid.uuid4())
        async with AsyncSessionLocal() as session:
            user = User(
                id=inactive_user_id,
                email="inactive@compliscan.gov.in",
                hashed_password=None,
                full_name="Inactive Officer",
                role=UserRole.INSPECTOR.value,
                is_active=False,  # Inactive account
            )
            session.add(user)
            await session.commit()

        token = create_test_supabase_token(user_id=inactive_user_id, email="inactive@compliscan.gov.in")
        res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 401
        assert "inactive" in res.json()["error"]["message"].lower()
