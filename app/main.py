"""FastAPI application entry point."""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware import error_handler_middleware, logging_middleware
from app.api.routes import articles, comparisons, health
from app.config import get_settings
from app.dependencies import cleanup_resources

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    logger.info(
        "application_starting",
        version=settings.app_version,
        debug=settings.debug,
        ai_provider=settings.default_ai_provider,
    )
    yield

    # Shutdown
    logger.info("application_shutting_down")
    await cleanup_resources()
    logger.info("application_stopped")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Spectrum - Political News Analyzer API

    Analyze the political leaning of news articles on a -1 (far left) to 1 (far right) spectrum.

    Features:
    - Analyze single articles for political bias
    - Extract topics, keywords, and key points
    - Find related articles on the same topic
    - Compare multiple articles to identify agreements and disagreements
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.middleware("http")(logging_middleware)
app.middleware("http")(error_handler_middleware)

# Include routers
app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(articles.router, prefix=settings.api_prefix)
app.include_router(comparisons.router, prefix=settings.api_prefix)


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint redirects to docs."""
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
