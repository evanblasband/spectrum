"""Request/response logging middleware."""

import time
import uuid
from typing import Callable

import structlog
from fastapi import Request, Response

logger = structlog.get_logger()


async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """Log all requests and responses with timing.

    Adds a request ID for correlation and logs:
    - Request method, path, and query params
    - Response status code
    - Processing time
    """
    # Generate request ID for correlation
    request_id = str(uuid.uuid4())[:8]

    # Bind request context to logger
    log = logger.bind(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    )

    # Log request
    log.info(
        "request_started",
        query=str(request.query_params) if request.query_params else None,
    )

    # Process request
    start_time = time.perf_counter()

    try:
        response = await call_next(request)

        # Calculate processing time
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)

        # Log response
        log.info(
            "request_completed",
            status_code=response.status_code,
            processing_time_ms=processing_time_ms,
        )

        # Add request ID to response headers for debugging
        response.headers["X-Request-ID"] = request_id

        return response

    except Exception as e:
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)

        log.error(
            "request_failed",
            error=str(e),
            processing_time_ms=processing_time_ms,
        )

        raise
