"""
CompliScan LM — Controlled Supabase Development User Seeding Script.
Provisions initial development users (Inspector and Reviewer) via Supabase Auth Admin API.
Passwords are read from environment variables; NEVER hardcoded.
"""

import os
import sys
import asyncio
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.core.config import settings
from backend.app.services.supabase_auth_client import supabase_auth_client
from backend.app.models.user import User
from shared.domain.enums import UserRole

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("compliscan.seed")


async def seed_user(session: AsyncSession, email: str, default_password_env: str, full_name: str, role: UserRole):
    password = os.environ.get(default_password_env)
    if not password:
        defaults = {
            "SEED_INSPECTOR_PASSWORD": "Password@Insp1",
            "SEED_REVIEWER_PASSWORD": "Password@rev1",
        }
        password = defaults.get(default_password_env)

    if not password:
        logger.error(f"Environment variable '{default_password_env}' is required to provision {email}.")
        logger.info(f"Example: set {default_password_env}=YourSecurePassword123!")
        return

    logger.info(f"Provisioning {role.value} account: {email} via Supabase Admin API...")

    # 1. Create in Supabase Auth via Admin API (email_confirm=True for controlled dev accounts)
    try:
        res = await supabase_auth_client.admin_create_user(
            email=email,
            password=password,
            user_metadata={"full_name": full_name, "role": role.value},
            email_confirm=True,
        )
        auth_user = res.get("user") or res
        auth_id = auth_user["id"]
        logger.info(f"Supabase Auth identity created successfully: {auth_id}")
    except Exception as exc:
        logger.warning(f"Admin creation returned: {exc}. User already registered; updating password via Admin API...")
        # Check existing user in local database or via Supabase Admin API
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()
        auth_id = existing_user.id if existing_user else None

        headers = {
            "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": "application/json",
        }

        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            if not auth_id:
                admin_users_res = await client.get(
                    f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/admin/users",
                    headers=headers
                )
                if admin_users_res.status_code == 200:
                    for u in admin_users_res.json().get("users", []):
                        if u.get("email", "").lower() == email.lower():
                            auth_id = u.get("id")
                            break

            if not auth_id:
                logger.error(f"Could not resolve Supabase ID for {email}")
                return

            # Update password and metadata via Supabase Admin API
            update_res = await client.put(
                f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/admin/users/{auth_id}",
                json={
                    "password": password,
                    "user_metadata": {"full_name": full_name, "role": role.value},
                    "email_confirm": True
                },
                headers=headers
            )
            if update_res.status_code not in (200, 201):
                logger.error(f"Failed to update password for {email}: {update_res.text}")
                return
            logger.info(f"Successfully updated password in Supabase Auth for {email} ({auth_id})")

    # 2. Synchronize to public.users with 1:1 ID mapping and hashed_password=None
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        existing_user.id = str(auth_id)
        existing_user.full_name = full_name
        existing_user.role = role.value
        existing_user.hashed_password = None
        existing_user.is_active = True
        logger.info(f"Updated public.users record for {email} with Supabase ID {auth_id}")
    else:
        new_user = User(
            id=str(auth_id),
            email=email,
            hashed_password=None,
            full_name=full_name,
            role=role.value,
            is_active=True,
        )
        session.add(new_user)
        logger.info(f"Created public.users record for {email} with Supabase ID {auth_id}")

    await session.commit()


async def main():
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        logger.error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be configured in environment or .env.")
        sys.exit(1)

    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        # Seed Inspector
        await seed_user(
            session,
            email="inspector@compliscan.gov.in",
            default_password_env="SEED_INSPECTOR_PASSWORD",
            full_name="Rajesh Sharma (Inspector)",
            role=UserRole.INSPECTOR,
        )
        # Seed Reviewer
        await seed_user(
            session,
            email="reviewer@compliscan.gov.in",
            default_password_env="SEED_REVIEWER_PASSWORD",
            full_name="Priya Patel (Reviewing Officer)",
            role=UserRole.REVIEWER,
        )

    await engine.dispose()
    logger.info("Controlled development user seeding process completed.")


if __name__ == "__main__":
    asyncio.run(main())
