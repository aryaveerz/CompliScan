"""
CompliScan LM — Error Handling & Exceptions.
Provides standard error envelopes and custom exceptions.
"""

from typing import Any, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from shared.domain.constants import ErrorCode


class AppError(Exception):
    """Base application exception."""
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Any] = None,
        retryable: bool = False,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        self.retryable = retryable


class NotFoundError(AppError):
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            code=ErrorCode.NOT_FOUND,
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            code=ErrorCode.UNAUTHORIZED,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenError(AppError):
    def __init__(self, message: str = "Permission denied for this resource"):
        super().__init__(
            code=ErrorCode.FORBIDDEN,
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ValidationError(AppError):
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            status_code=422,
            details=details,
        )


class InvalidStateError(AppError):
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            code=ErrorCode.INVALID_LIFECYCLE_STATE,
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class EvidenceError(AppError):
    def __init__(self, code: ErrorCode, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, details: Optional[Any] = None):
        super().__init__(
            code=code,
            message=message,
            status_code=status_code,
            details=details,
        )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Standardized error envelope."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code.value if isinstance(exc.code, ErrorCode) else str(exc.code),
                "message": exc.message,
                "details": exc.details,
                "retryable": exc.retryable,
            }
        }
    )
