"""Structured error handling for API responses."""

from fastapi import HTTPException
from fastapi.responses import JSONResponse

from app.core.errors import (
    ErrorCode,
    ERROR_STATUS_CODES,
    ERROR_SUGGESTIONS,
    RETRYABLE_ERRORS,
)


class StructuredHTTPException(HTTPException):
    """HTTPException with structured error details."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: dict | None = None,
    ):
        self.code = code
        self.error_message = message
        self.details = details
        status_code = ERROR_STATUS_CODES.get(code, 500)
        super().__init__(status_code=status_code, detail=message)


def raise_structured_error(
    code: ErrorCode,
    message: str,
    details: dict | None = None,
) -> None:
    """
    Raise a structured HTTP error.

    Args:
        code: Error code from ErrorCode enum
        message: Human-readable error message
        details: Optional additional details (e.g., URL, field name)
    """
    raise StructuredHTTPException(code=code, message=message, details=details)


def structured_error_response(
    code: ErrorCode,
    message: str,
    details: dict | None = None,
) -> JSONResponse:
    """
    Create a structured error JSON response.

    Args:
        code: Error code from ErrorCode enum
        message: Human-readable error message
        details: Optional additional details
    """
    status_code = ERROR_STATUS_CODES.get(code, 500)
    suggestion = ERROR_SUGGESTIONS.get(code, "Please try again.")
    retryable = code in RETRYABLE_ERRORS

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": code.value,
                "message": message,
                "suggestion": suggestion,
                "retryable": retryable,
                "details": details,
            },
        },
    )
