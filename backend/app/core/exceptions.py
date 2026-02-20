"""Core exceptions module for custom exception handling."""

from typing import Any


from fastapi import HTTPException


class AppException(HTTPException):
    """Base exception for application-specific errors that returns HTTP responses.
    
    Attributes:
        status_code: HTTP status code to return.
        detail: Human-readable error message.
        code: Machine-readable error code.
    """

    code: str = "internal_error"

    def __init__(
        self,
        detail: str | None = None,
        status_code: int | None = None,
        code: str | None = None,
        **kwargs: Any,
    ):
        """Initialize exception with optional custom detail and code."""
        if status_code is not None:
            self.status_code = status_code
        if detail is not None:
            self.detail = detail
        if code is not None:
            self.code = code
        super().__init__(status_code=self.status_code, detail=self.detail)


class NotFoundException(AppException):
    """Exception raised when a resource is not found.

    Returns HTTP 404 status code.
    """

    status_code = 404
    detail = "Resource not found"
    code = "not_found"


class UnauthorizedException(AppException):
    """Exception raised when authentication is required or invalid.

    Returns HTTP 401 status code.
    """

    status_code = 401
    detail = "Not authenticated"
    code = "unauthorized"


class ForbiddenException(AppException):
    """Exception raised when user lacks permission for an action.

    Returns HTTP 403 status code.
    """

    status_code = 403
    detail = "Access denied"
    code = "forbidden"


class ValidationException(AppException):
    """Exception raised when input validation fails.

    Returns HTTP 400 status code.
    """

    status_code = 400
    detail = "Validation error"
    code = "validation_error"


class ConflictException(AppException):
    """Exception raised when there's a resource conflict.

    Returns HTTP 409 status code.
    """

    status_code = 409
    detail = "Resource conflict"
    code = "conflict"
