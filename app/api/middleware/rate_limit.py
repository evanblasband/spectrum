"""Rate limiting middleware using slowapi."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse

from app.config import get_settings

settings = get_settings()

# Create limiter instance
# Uses client IP address as the key for rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_requests}/minute"],
    storage_uri="memory://",  # In-memory storage, suitable for single instance
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom handler for rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests. Please slow down.",
                "suggestion": "Wait a minute before trying again.",
                "retryable": True,
                "details": {
                    "limit": str(exc.detail),
                    "retry_after": getattr(exc, "retry_after", 60),
                },
            },
        },
    )


# Rate limit decorators for different endpoint types
# These can be used as: @limiter.limit("5/minute")

# Expensive endpoints (AI analysis) - stricter limits
ANALYZE_LIMIT = "10/minute"  # AI analysis is expensive
COMPARE_LIMIT = "5/minute"   # Comparison analyzes multiple articles

# Standard endpoints - more lenient
RELATED_LIMIT = "20/minute"  # NewsAPI has its own limits
DOCS_LIMIT = "60/minute"     # Documentation is cheap
HEALTH_LIMIT = "120/minute"  # Health checks should be fast
