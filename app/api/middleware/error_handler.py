"""Global error handling middleware."""

import structlog
from fastapi import Request, status
from fastapi.responses import JSONResponse

logger = structlog.get_logger()


async def error_handler_middleware(request: Request, call_next):
    """Global error handler that catches unhandled exceptions.

    Logs errors and returns consistent error response format.
    """
    try:
        return await call_next(request)

    except Exception as e:
        # Log the error
        logger.error(
            "unhandled_exception",
            path=request.url.path,
            method=request.method,
            error=str(e),
            exc_info=True,
        )

        # Return error response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "An unexpected error occurred",
                "error_code": "INTERNAL_ERROR",
            },
        )
