"""
CompliScan LM — Auth Service.
Delegates identity and password authentication to Supabase Auth.
Authoritative for application user profiles and domain RBAC mapping.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.user import User
from backend.app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from backend.app.core.errors import UnauthorizedError, AppError
from backend.app.services.supabase_auth_client import supabase_auth_client
from shared.domain.constants import ErrorCode
from shared.domain.enums import UserRole

logger = logging.getLogger("compliscan.auth_service")


class AuthService:
    @staticmethod
    async def register(db: AsyncSession, request: RegisterRequest) -> TokenResponse:
        """
        Register a new user identity via Supabase Auth and provision matching application User record.
        Respects project email confirmation settings.
        """
        email_clean = request.email.lower().strip()
        role_str = request.role.value if isinstance(request.role, UserRole) else str(request.role)

        # 1. Check if email already exists in local application registry
        stmt = select(User).where(User.email == email_clean)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise AppError(
                code=ErrorCode.VALIDATION_ERROR,
                message="User with this email already exists",
                status_code=400,
            )

        # 2. Delegate identity registration to Supabase Auth
        supabase_res = await supabase_auth_client.sign_up(
            email=email_clean,
            password=request.password,
            user_metadata={
                "full_name": request.full_name.strip(),
                "role": role_str,
            },
        )

        auth_user = supabase_res.get("user") or supabase_res
        auth_user_id = auth_user.get("id")
        if not auth_user_id:
            raise AppError(
                code=ErrorCode.INTERNAL_ERROR,
                message="Supabase Auth registration did not return a valid user identity ID",
                status_code=502,
            )

        session = supabase_res.get("session") or {}
        access_token = session.get("access_token") or supabase_res.get("access_token") or ""

        # 3. Create application User record with 1:1 mapped UUID primary key.
        # hashed_password is NULL — Supabase Auth owns all credentials.
        user = User(
            id=str(auth_user_id),
            email=email_clean,
            hashed_password=None,
            full_name=request.full_name.strip(),
            role=role_str,
            is_active=True,
        )
        db.add(user)
        try:
            await db.commit()
            await db.refresh(user)
        except Exception as db_exc:
            # REGISTRATION CONSISTENCY (Correction 3):
            # The Supabase Auth identity was created but the local profile transaction failed.
            # Attempt best-effort cleanup of the orphaned Supabase identity so the email
            # address is not permanently locked in auth.users without a matching profile.
            # If this cleanup call also fails, a provisioning orphan exists:
            #   auth.users row present, public.users row absent.
            # Operations staff can resolve it by deleting the orphaned auth.users entry
            # via the Supabase Admin API or dashboard.
            logger.error(
                "Registration DB commit failed for auth_user_id=%s email=%s; "
                "attempting Supabase Auth identity cleanup.",
                auth_user_id,
                email_clean,
            )
            try:
                await supabase_auth_client.delete_user(auth_user_id)
                logger.info(
                    "Supabase Auth identity cleanup succeeded for auth_user_id=%s.",
                    auth_user_id,
                )
            except Exception as cleanup_exc:
                # Cleanup failed — document the orphan condition explicitly.
                logger.error(
                    "PROVISIONING ORPHAN: Supabase Auth identity auth_user_id=%s email=%s "
                    "could not be cleaned up after local DB failure. "
                    "Manual remediation required. cleanup_error=%s",
                    auth_user_id,
                    email_clean,
                    str(cleanup_exc),
                )
            raise AppError(
                code=ErrorCode.INTERNAL_ERROR,
                message="Registration failed: user profile could not be created. Please try again.",
                status_code=500,
            ) from db_exc

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    async def login(db: AsyncSession, request: LoginRequest) -> TokenResponse:
        """
        Authenticate user identity against Supabase Auth, then resolve authoritative application User.
        """
        email_clean = request.email.lower().strip()

        # 1. Authenticate against Supabase GoTrue
        auth_res = await supabase_auth_client.sign_in_with_password(
            email=email_clean,
            password=request.password,
        )

        session = auth_res.get("session") or auth_res
        access_token = session.get("access_token") or auth_res.get("access_token")
        auth_user = auth_res.get("user") or session.get("user") or {}
        auth_user_id = auth_user.get("id")

        if not access_token or not auth_user_id:
            raise UnauthorizedError("Supabase Auth returned incomplete session credentials")

        # 2. Authoritative resolution: JWT.sub -> public.users.id
        # Invariant: public.users.id == auth.users.id (UUID, set at registration).
        # Email-based identity reconciliation is NOT performed here — doing so
        # could silently mutate public.users.id, breaking foreign-key integrity
        # for created_by_id, reviewer_id, and uploaded_by_id references.
        stmt = select(User).where(User.id == str(auth_user_id))
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise UnauthorizedError(
                "Authenticated identity has no matching application profile. "
                "User may need to complete registration."
            )

        if not user.is_active:
            raise UnauthorizedError("User account is inactive")

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> User:
        """Authoritatively fetch application user by ID (mapped to Supabase Auth UUID)."""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise UnauthorizedError("User not found in application registry")
        return user
