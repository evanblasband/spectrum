"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.errors import StructuredHTTPException
from app.api.middleware.error_handler import ErrorHandlerMiddleware
from app.api.middleware.logging import LoggingMiddleware
from app.api.routes import articles, comparisons, docs, health
from app.config import get_settings
from app.core.errors import ERROR_SUGGESTIONS, RETRYABLE_ERRORS

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    logger.info(
        "Starting application",
        extra={"version": settings.app_version, "debug": settings.debug},
    )
    # Store debug flag in app state for error handler
    app.state.debug = settings.debug
    yield
    logger.info("Shutting down application")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Political spectrum analyzer for news articles",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware (order matters - last added is first executed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlerMiddleware)

# Exception handler for structured errors
@app.exception_handler(StructuredHTTPException)
async def structured_exception_handler(
    request: Request, exc: StructuredHTTPException
) -> JSONResponse:
    """Convert StructuredHTTPException to JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code.value,
                "message": exc.error_message,
                "suggestion": ERROR_SUGGESTIONS.get(exc.code, "Please try again."),
                "retryable": exc.code in RETRYABLE_ERRORS,
                "details": exc.details,
            },
        },
    )


# Routes
app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(articles.router, prefix=settings.api_prefix)
app.include_router(comparisons.router, prefix=settings.api_prefix)
app.include_router(docs.router, prefix=settings.api_prefix)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": f"{settings.api_prefix}/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
