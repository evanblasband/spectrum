"""Global error handling middleware."""

import logging
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.errors import ErrorCode, ERROR_SUGGESTIONS

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for handling uncaught exceptions."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and handle any uncaught exceptions."""
        try:
            return await call_next(request)
        except Exception as e:
            logger.exception("Unhandled exception occurred")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "code": ErrorCode.INTERNAL_ERROR.value,
                        "message": "Internal server error",
                        "suggestion": ERROR_SUGGESTIONS[ErrorCode.INTERNAL_ERROR],
                        "retryable": False,
                        "details": {"debug": str(e)} if request.app.state.debug else None,
                    },
                },
            )
