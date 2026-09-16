"""
CompliScan LM — FastAPI Dependencies.
Provides database sessions, authenticated current user, and RBAC role guards.
"""

from typing import Callable
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.core.security import decode_token
from backend.app.core.errors import UnauthorizedError, ForbiddenError
from backend.app.services.auth_service import AuthService
from shared.domain.enums import UserRole

# HTTP Bearer scheme
security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate JWT token; return active User entity."""
    if not credentials or not credentials.credentials:
        raise UnauthorizedError("Missing or invalid Authorization header")

    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid token payload")

    user = await AuthService.get_user_by_id(db, user_id=str(user_id))
    if not user.is_active:
        raise UnauthorizedError("User account is inactive")

    return user


def require_role(*allowed_roles: UserRole) -> Callable:
    """RBAC dependency to enforce permitted user roles."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        allowed_values = [r.value if isinstance(r, UserRole) else str(r) for r in allowed_roles]
        if current_user.role not in allowed_values:
            raise ForbiddenError(f"Operation requires one of the following roles: {', '.join(allowed_values)}")
        return current_user

    return role_checker
