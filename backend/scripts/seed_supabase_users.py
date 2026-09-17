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
        logger.warning(f"Admin creation returned: {exc}. Checking if user already exists in Supabase...")
        # If user already exists, try signing in to get their auth ID
        try:
            sign_in_res = await supabase_auth_client.sign_in_with_password(email, password)
            auth_user = sign_in_res.get("user") or {}
            auth_id = auth_user.get("id")
            if not auth_id:
                logger.error(f"Could not resolve Supabase ID for {email}")
                return
            logger.info(f"Resolved existing Supabase Auth identity: {auth_id}")
        except Exception as sign_in_exc:
            logger.error(f"Failed to resolve identity for {email}: {sign_in_exc}")
            return

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
