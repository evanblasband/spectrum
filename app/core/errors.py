"""Centralized error definitions for Spectrum."""

from enum import Enum


class ErrorCode(str, Enum):
    """Error codes for structured error responses."""

    BLOCKED_SOURCE = "BLOCKED_SOURCE"
    NETWORK_ERROR = "NETWORK_ERROR"
    CONTENT_EXTRACTION = "CONTENT_EXTRACTION"
    NOT_FOUND = "NOT_FOUND"
    RATE_LIMITED = "RATE_LIMITED"
    AI_ERROR = "AI_ERROR"
    VALIDATION = "VALIDATION"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# HTTP status codes for each error type
ERROR_STATUS_CODES: dict[ErrorCode, int] = {
    ErrorCode.BLOCKED_SOURCE: 422,
    ErrorCode.NETWORK_ERROR: 503,
    ErrorCode.CONTENT_EXTRACTION: 422,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.RATE_LIMITED: 429,
    ErrorCode.AI_ERROR: 503,
    ErrorCode.VALIDATION: 400,
    ErrorCode.INTERNAL_ERROR: 500,
}

# User-friendly suggestions for recovery
ERROR_SUGGESTIONS: dict[ErrorCode, str] = {
    ErrorCode.BLOCKED_SOURCE: "Try using a different news source. Check the supported sources list.",
    ErrorCode.NETWORK_ERROR: "Check your connection and try again in a moment.",
    ErrorCode.CONTENT_EXTRACTION: "This article's format may not be supported. Try a different article.",
    ErrorCode.NOT_FOUND: "The article may have been removed. Verify the URL is correct.",
    ErrorCode.RATE_LIMITED: "Too many requests. Please wait a moment and try again.",
    ErrorCode.AI_ERROR: "Our AI service is temporarily unavailable. Please try again shortly.",
    ErrorCode.VALIDATION: "Please check your input and try again.",
    ErrorCode.INTERNAL_ERROR: "Something went wrong on our end. Please try again.",
}

# Errors that may succeed on retry
RETRYABLE_ERRORS: set[ErrorCode] = {
    ErrorCode.NETWORK_ERROR,
    ErrorCode.RATE_LIMITED,
    ErrorCode.AI_ERROR,
}
