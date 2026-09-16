"""
CompliScan LM — Auth Service.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.user import User
from backend.app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.core.errors import UnauthorizedError, AppError
from shared.domain.constants import ErrorCode
from shared.domain.enums import UserRole


class AuthService:
    @staticmethod
    async def register(db: AsyncSession, request: RegisterRequest) -> TokenResponse:
        """Register a new user account."""
        # Check if email already exists
        stmt = select(User).where(User.email == request.email.lower().strip())
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            raise AppError(
                code=ErrorCode.VALIDATION_ERROR,
                message="User with this email already exists",
                status_code=400,
            )

        user = User(
            email=request.email.lower().strip(),
            hashed_password=get_password_hash(request.password),
            full_name=request.full_name.strip(),
            role=request.role.value if isinstance(request.role, UserRole) else str(request.role),
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        token = create_access_token(subject=user.id, role=user.role)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    async def login(db: AsyncSession, request: LoginRequest) -> TokenResponse:
        """Authenticate user with email and password."""
        stmt = select(User).where(User.email == request.email.lower().strip())
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not verify_password(request.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedError("User account is inactive")

        token = create_access_token(subject=user.id, role=user.role)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> User:
        """Fetch user by ID."""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise UnauthorizedError("User not found")
        return user
