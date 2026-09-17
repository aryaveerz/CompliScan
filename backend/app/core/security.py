"""
CompliScan LM — Security & Cryptography Utilities.
Provides Supabase Auth JWT verification and cryptographic hashing.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
import hashlib
import logging
import httpx
from jose import jwt, JWTError
from backend.app.core.config import settings
from backend.app.core.errors import UnauthorizedError

logger = logging.getLogger("compliscan.security")

# In-memory cache for Supabase JWKS public keys
_jwks_cache: Dict[str, Any] = {}
_jwks_last_fetched: Optional[datetime] = None


def get_expected_issuer() -> Optional[str]:
    """Derive expected Supabase GoTrue token issuer."""
    if settings.SUPABASE_URL:
        return f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1"
    return None


def get_jwks(jwks_url: str) -> Dict[str, Any]:
    """Fetch and cache JWKS from Supabase GoTrue."""
    global _jwks_cache, _jwks_last_fetched
    now = datetime.now(timezone.utc)
    if _jwks_cache and _jwks_last_fetched and (now - _jwks_last_fetched).total_seconds() < 3600:
        return _jwks_cache

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(jwks_url)
            if resp.status_code == 200:
                _jwks_cache = resp.json()
                _jwks_last_fetched = now
                return _jwks_cache
            raise UnauthorizedError(f"Failed to fetch Supabase JWKS: HTTP {resp.status_code}")
    except Exception as exc:
        raise UnauthorizedError(f"Failed to connect to Supabase JWKS endpoint: {str(exc)}")


def verify_supabase_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a Supabase Auth JWT.
    Validates:
      - signature (via HS256 secret or asymmetric JWKS)
      - expiration (exp)
      - subject (sub)
      - audience (aud == 'authenticated')
      - issuer (iss == https://<project-ref>.supabase.co/auth/v1 if configured)
    """
    try:
        header = jwt.get_unverified_header(token)
    except Exception as exc:
        raise UnauthorizedError(f"Invalid token header: {str(exc)}")

    alg = header.get("alg", "HS256")
    expected_iss = get_expected_issuer()
    expected_aud = settings.SUPABASE_AUTH_AUDIENCE or "authenticated"

    # Strict claim validation options
    options = {
        "verify_signature": True,
        "verify_aud": True,
        "verify_exp": True,
        "verify_iss": bool(expected_iss),
        "require_sub": True,
        "require_exp": True,
        "require_aud": True,
    }

    try:
        if alg == "HS256":
            # Strictly require SUPABASE_JWT_SECRET for Supabase HS256 verification.
            # Never fall back to the application's generic SECRET_KEY; doing so
            # would silently mix application secrets into the Supabase auth path.
            secret = settings.SUPABASE_JWT_SECRET
            if not secret:
                raise UnauthorizedError(
                    "SUPABASE_JWT_SECRET is not configured — cannot verify Supabase HS256 token"
                )
            payload = jwt.decode(
                token,
                secret,
                algorithms=["HS256"],
                audience=expected_aud,
                issuer=expected_iss,
                options=options,
            )
        elif alg in ("RS256", "ES256"):
            if not settings.SUPABASE_URL:
                raise UnauthorizedError("SUPABASE_URL is required to verify asymmetric JWKS tokens")
            jwks_url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
            jwks = get_jwks(jwks_url)
            kid = header.get("kid")

            key = None
            for k in jwks.get("keys", []):
                if k.get("kid") == kid or not kid:
                    key = k
                    break
            if not key:
                raise UnauthorizedError(f"No matching key found in JWKS for kid '{kid}'")

            payload = jwt.decode(
                token,
                key,
                algorithms=[alg],
                audience=expected_aud,
                issuer=expected_iss,
                options=options,
            )
        else:
            raise UnauthorizedError(f"Unsupported JWT algorithm: {alg}")

        # Strict subject check
        sub = payload.get("sub")
        if not sub or not isinstance(sub, str) or not sub.strip():
            raise UnauthorizedError("Token missing valid 'sub' claim")

        return payload

    except JWTError as e:
        raise UnauthorizedError(f"Could not validate credentials: {str(e)}")


def decode_token(token: str) -> Dict[str, Any]:
    """Authoritative token decode wrapper for FastAPI dependencies."""
    return verify_supabase_token(token)


def compute_sha256(data: bytes) -> str:
    """Compute SHA-256 hash of byte payload."""
    return hashlib.sha256(data).hexdigest()
