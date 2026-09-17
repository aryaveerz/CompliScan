"""
CompliScan LM — Supabase Auth (GoTrue) REST Client.
Communicates directly with Supabase GoTrue Auth API via httpx.
"""

from typing import Any, Dict, Optional
import httpx
from backend.app.core.config import settings
from backend.app.core.errors import UnauthorizedError, AppError
from shared.domain.constants import ErrorCode


class SupabaseAuthClient:
    """Async client for Supabase GoTrue Auth REST endpoints."""

    def __init__(self, base_url: Optional[str] = None, anon_key: Optional[str] = None, service_role_key: Optional[str] = None):
        self.base_url = (base_url or settings.SUPABASE_URL).rstrip("/")
        self.anon_key = anon_key or settings.SUPABASE_ANON_KEY
        self.service_role_key = service_role_key or settings.SUPABASE_SERVICE_ROLE_KEY

    def _get_auth_url(self, path: str) -> str:
        return f"{self.base_url}/auth/v1{path}"

    async def sign_in_with_password(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate with email and password via GoTrue token endpoint."""
        url = self._get_auth_url("/token?grant_type=password")
        headers = {
            "apikey": self.anon_key,
            "Content-Type": "application/json",
        }
        payload = {
            "email": email,
            "password": password,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
            except Exception as exc:
                raise AppError(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=f"Failed to communicate with Supabase Auth service: {str(exc)}",
                    status_code=503,
                )

        if response.status_code != 200:
            error_data = response.json() if response.content else {}
            error_msg = error_data.get("msg") or error_data.get("error_description") or "Invalid email or password"
            raise UnauthorizedError(error_msg)

        return response.json()

    async def sign_up(self, email: str, password: str, user_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Normal user sign-up via GoTrue /signup endpoint.
        Respects the project's configured email confirmation policy.
        """
        url = self._get_auth_url("/signup")
        headers = {
            "apikey": self.anon_key,
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "email": email,
            "password": password,
        }
        if user_metadata:
            payload["data"] = user_metadata

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
            except Exception as exc:
                raise AppError(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=f"Failed to communicate with Supabase Auth service: {str(exc)}",
                    status_code=503,
                )

        if response.status_code not in (200, 201):
            error_data = response.json() if response.content else {}
            error_msg = error_data.get("msg") or error_data.get("error_description") or "Registration failed"
            raise AppError(
                code=ErrorCode.VALIDATION_ERROR,
                message=error_msg,
                status_code=400,
            )

        return response.json()

    async def admin_create_user(
        self,
        email: str,
        password: str,
        user_metadata: Optional[Dict[str, Any]] = None,
        email_confirm: bool = True,
    ) -> Dict[str, Any]:
        """
        Administrative user creation via GoTrue /admin/users endpoint.
        Requires SUPABASE_SERVICE_ROLE_KEY. Strictly for admin scripts & seed users.
        """
        if not self.service_role_key:
            raise AppError(
                code=ErrorCode.INTERNAL_ERROR,
                message="SUPABASE_SERVICE_ROLE_KEY is required for administrative user creation",
                status_code=500,
            )

        url = self._get_auth_url("/admin/users")
        headers = {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "email": email,
            "password": password,
            "email_confirm": email_confirm,
        }
        if user_metadata:
            payload["user_metadata"] = user_metadata

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
            except Exception as exc:
                raise AppError(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=f"Failed to communicate with Supabase Auth admin service: {str(exc)}",
                    status_code=503,
                )

        if response.status_code not in (200, 201):
            error_data = response.json() if response.content else {}
            error_msg = error_data.get("msg") or error_data.get("error_description") or "Admin user creation failed"
            raise AppError(
                code=ErrorCode.VALIDATION_ERROR,
                message=error_msg,
                status_code=response.status_code,
            )

        return response.json()

    async def get_user(self, access_token: str) -> Dict[str, Any]:
        """Retrieve user identity data from GoTrue using their access token."""
        url = self._get_auth_url("/user")
        headers = {
            "apikey": self.anon_key,
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, headers=headers)
            except Exception as exc:
                raise AppError(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=f"Failed to verify user with Supabase Auth: {str(exc)}",
                    status_code=503,
                )

        if response.status_code != 200:
            raise UnauthorizedError("Invalid or expired session token")

        return response.json()

    async def delete_user(self, user_id: str) -> None:
        """
        Delete a Supabase Auth user by UUID via the Admin API.
        Requires SUPABASE_SERVICE_ROLE_KEY.
        Used for best-effort cleanup of orphaned identities when local DB commit fails.
        """
        if not self.service_role_key:
            raise AppError(
                code=ErrorCode.INTERNAL_ERROR,
                message="SUPABASE_SERVICE_ROLE_KEY is required to delete Auth users",
                status_code=500,
            )

        url = self._get_auth_url(f"/admin/users/{user_id}")
        headers = {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.delete(url, headers=headers)
            except Exception as exc:
                raise AppError(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=f"Failed to communicate with Supabase Auth admin service: {str(exc)}",
                    status_code=503,
                )

        # 200 or 404 (already gone) are both acceptable outcomes for cleanup
        if response.status_code not in (200, 204, 404):
            error_data = response.json() if response.content else {}
            error_msg = error_data.get("msg") or error_data.get("error_description") or "Cleanup failed"
            raise AppError(
                code=ErrorCode.INTERNAL_ERROR,
                message=f"Supabase Auth user deletion failed: {error_msg}",
                status_code=response.status_code,
            )


supabase_auth_client = SupabaseAuthClient()
