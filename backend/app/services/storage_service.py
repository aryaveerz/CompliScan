"""
CompliScan LM — Unified Storage Service Abstraction.

Provides clean, backend-agnostic interfaces for object storage operations across:
  - LocalStorageService (development, offline testing, CI/CD)
  - SupabaseStorageService (production cloud object storage on Supabase Storage)

Buckets:
  - compliscan-evidence  (Original raw packaging photos and PDFs)
  - compliscan-derived   (Cropped token bounding boxes, token masks, canvas overlays)
  - compliscan-reports   (Finalized PDF and DOCX statutory audit dossiers)
  - compliscan-audit     (Daily cryptographic audit ledger manifests)
"""

import abc
import os
import shutil
from pathlib import Path
from typing import Optional
import httpx

from backend.app.core.config import settings
from backend.app.core.errors import NotFoundError, EvidenceError
from shared.domain.constants import ErrorCode


class BaseStorageService(abc.ABC):
    """Abstract Base Class defining authoritative Storage Service contract."""

    @abc.abstractmethod
    async def upload_file(
        self,
        bucket: str,
        path: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload binary content to storage. Returns canonical storage path."""
        pass

    @abc.abstractmethod
    async def download_file(self, bucket: str, path: str) -> bytes:
        """Download binary content from storage."""
        pass

    @abc.abstractmethod
    async def generate_signed_url(self, bucket: str, path: str, expires_in: int = 300) -> str:
        """Generate short-lived signed URL for client download access."""
        pass

    @abc.abstractmethod
    async def delete_file(self, bucket: str, path: str) -> bool:
        """Delete object from storage."""
        pass

    @abc.abstractmethod
    async def file_exists(self, bucket: str, path: str) -> bool:
        """Check if object exists in storage."""
        pass


class LocalStorageService(BaseStorageService):
    """Local filesystem storage implementation for offline development and testing."""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or settings.LOCAL_STORAGE_DIR).resolve()

    def _get_full_path(self, bucket: str, path: str) -> Path:
        # Strip leading slashes to avoid path traversal
        clean_path = path.lstrip("/\\")
        clean_bucket = bucket.lstrip("/\\")
        full_path = (self.base_dir / clean_bucket / clean_path).resolve()
        
        # Ensure path stays within base_dir
        if not str(full_path).startswith(str(self.base_dir)):
            raise EvidenceError(
                code=ErrorCode.VALIDATION_ERROR,
                message="Invalid storage path traversal attempt",
                status_code=400,
            )
        return full_path

    async def upload_file(
        self,
        bucket: str,
        path: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        full_path = self._get_full_path(bucket, path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(content)
        # Return canonical bucket-relative path
        return f"{bucket}/{path.lstrip('/')}"

    async def download_file(self, bucket: str, path: str) -> bytes:
        full_path = self._get_full_path(bucket, path)
        if not full_path.exists() or not full_path.is_file():
            # Fallback: check if path includes bucket prefix already
            if str(path).startswith(bucket):
                stripped_path = str(path)[len(bucket):].lstrip("/\\")
                full_path = self._get_full_path(bucket, stripped_path)

        if not full_path.exists() or not full_path.is_file():
            raise NotFoundError(f"Storage object not found: {bucket}/{path}")

        with open(full_path, "rb") as f:
            return f.read()

    async def generate_signed_url(self, bucket: str, path: str, expires_in: int = 300) -> str:
        # For local development, return local API download endpoint URL
        clean_path = path.lstrip("/")
        return f"/api/v1/evidence/download?bucket={bucket}&path={clean_path}"

    async def delete_file(self, bucket: str, path: str) -> bool:
        try:
            full_path = self._get_full_path(bucket, path)
            if full_path.exists() and full_path.is_file():
                os.remove(full_path)
                return True
            return False
        except Exception:
            return False

    async def file_exists(self, bucket: str, path: str) -> bool:
        try:
            full_path = self._get_full_path(bucket, path)
            return full_path.exists() and full_path.is_file()
        except Exception:
            return False


class SupabaseStorageService(BaseStorageService):
    """Production Supabase Storage REST API implementation."""

    def __init__(self, supabase_url: Optional[str] = None, service_role_key: Optional[str] = None):
        self.supabase_url = (supabase_url or settings.SUPABASE_URL).rstrip("/")
        self.service_role_key = service_role_key or settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY

    def _get_headers(self, content_type: str = "application/octet-stream") -> dict:
        return {
            "Authorization": f"Bearer {self.service_role_key}",
            "apikey": self.service_role_key,
            "Content-Type": content_type,
            "x-upsert": "true",
        }

    async def upload_file(
        self,
        bucket: str,
        path: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        if not self.supabase_url or not self.service_role_key:
            raise EvidenceError(
                code=ErrorCode.INTERNAL_SERVER_ERROR,
                message="Supabase Storage URL or key not configured",
                status_code=500,
            )

        clean_path = path.lstrip("/")
        url = f"{self.supabase_url}/storage/v1/object/{bucket}/{clean_path}"
        headers = self._get_headers(content_type)

        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, content=content, headers=headers)
            if res.status_code not in (200, 201):
                raise EvidenceError(
                    code=ErrorCode.INTERNAL_SERVER_ERROR,
                    message=f"Supabase Storage upload failed: HTTP {res.status_code} - {res.text}",
                    status_code=500,
                )
        return f"{bucket}/{clean_path}"

    async def download_file(self, bucket: str, path: str) -> bytes:
        if not self.supabase_url or not self.service_role_key:
            raise EvidenceError(
                code=ErrorCode.INTERNAL_SERVER_ERROR,
                message="Supabase Storage URL or key not configured",
                status_code=500,
            )

        clean_path = path.lstrip("/")
        # If path starts with bucket name, strip it
        if clean_path.startswith(f"{bucket}/"):
            clean_path = clean_path[len(f"{bucket}/"):]

        url = f"{self.supabase_url}/storage/v1/object/{bucket}/{clean_path}"
        headers = {
            "Authorization": f"Bearer {self.service_role_key}",
            "apikey": self.service_role_key,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.get(url, headers=headers)
            if res.status_code == 404:
                raise NotFoundError(f"Supabase Storage object not found: {bucket}/{clean_path}")
            if res.status_code != 200:
                raise EvidenceError(
                    code=ErrorCode.INTERNAL_SERVER_ERROR,
                    message=f"Supabase Storage download failed: HTTP {res.status_code}",
                    status_code=500,
                )
            return res.content

    async def generate_signed_url(self, bucket: str, path: str, expires_in: int = 300) -> str:
        if not self.supabase_url or not self.service_role_key:
            raise EvidenceError(
                code=ErrorCode.INTERNAL_SERVER_ERROR,
                message="Supabase Storage URL or key not configured",
                status_code=500,
            )

        clean_path = path.lstrip("/")
        if clean_path.startswith(f"{bucket}/"):
            clean_path = clean_path[len(f"{bucket}/"):]

        url = f"{self.supabase_url}/storage/v1/object/sign/{bucket}/{clean_path}"
        headers = {
            "Authorization": f"Bearer {self.service_role_key}",
            "apikey": self.service_role_key,
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, json={"expiresIn": expires_in}, headers=headers)
            if res.status_code != 200:
                raise EvidenceError(
                    code=ErrorCode.INTERNAL_SERVER_ERROR,
                    message=f"Supabase Storage signed URL generation failed: HTTP {res.status_code}",
                    status_code=500,
                )
            data = res.json()
            signed_path = data.get("signedURL") or data.get("signedUrl")
            if signed_path and signed_path.startswith("http"):
                return signed_path
            return f"{self.supabase_url}/storage/v1{signed_path}"

    async def delete_file(self, bucket: str, path: str) -> bool:
        if not self.supabase_url or not self.service_role_key:
            return False

        clean_path = path.lstrip("/")
        if clean_path.startswith(f"{bucket}/"):
            clean_path = clean_path[len(f"{bucket}/"):]

        url = f"{self.supabase_url}/storage/v1/object/{bucket}/{clean_path}"
        headers = {
            "Authorization": f"Bearer {self.service_role_key}",
            "apikey": self.service_role_key,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.delete(url, headers=headers)
            return res.status_code in (200, 204)

    async def file_exists(self, bucket: str, path: str) -> bool:
        try:
            await self.download_file(bucket, path)
            return True
        except Exception:
            return False


# Singleton instances
_local_storage_instance: Optional[LocalStorageService] = None
_supabase_storage_instance: Optional[SupabaseStorageService] = None


def get_storage_service(backend_type: Optional[str] = None) -> BaseStorageService:
    """
    Factory function returning the configured StorageService instance.
    Uses LocalStorageService for development/testing, SupabaseStorageService for production.
    """
    global _local_storage_instance, _supabase_storage_instance

    target_backend = backend_type or settings.STORAGE_BACKEND
    if settings.ENVIRONMENT == "production" and not backend_type:
        target_backend = "supabase"

    if target_backend == "supabase":
        if _supabase_storage_instance is None:
            _supabase_storage_instance = SupabaseStorageService()
        return _supabase_storage_instance
    else:
        if _local_storage_instance is None:
            _local_storage_instance = LocalStorageService()
        return _local_storage_instance
