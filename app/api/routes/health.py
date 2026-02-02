"""Health check endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.dependencies import get_ai_provider, get_article_fetcher
from app.schemas.responses import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    """Basic health check endpoint.

    Returns immediately without checking dependencies.
    Use /health/ready for full readiness check.
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.utcnow(),
        services={},
    )


@router.get("/health/ready", response_model=HealthResponse)
async def readiness_check(
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    """Readiness check endpoint.

    Checks all dependencies are available:
    - AI provider (API key valid, service responding)
    - Article fetcher (can make HTTP requests)
    - News aggregator (API key valid, if configured)

    Returns degraded status if any non-critical service is down.
    Returns unhealthy if critical services are down.
    """
    services = {}

    # Check AI provider
    try:
        ai_provider = get_ai_provider()
        services["ai_provider"] = await ai_provider.health_check()
    except Exception:
        services["ai_provider"] = False

    # Check article fetcher
    try:
        fetcher = get_article_fetcher()
        services["article_fetcher"] = await fetcher.health_check()
    except Exception:
        services["article_fetcher"] = False

    # Check news aggregator (optional)
    try:
        from app.dependencies import get_news_aggregator
        aggregator = get_news_aggregator()
        services["news_aggregator"] = await aggregator.health_check()
    except ValueError:
        # No news API configured - not critical
        services["news_aggregator"] = None
    except Exception:
        services["news_aggregator"] = False

    # Determine overall status
    critical_services = ["ai_provider", "article_fetcher"]
    critical_healthy = all(services.get(s) for s in critical_services)

    optional_services = ["news_aggregator"]
    optional_healthy = all(
        services.get(s) in (True, None) for s in optional_services
    )

    if critical_healthy and optional_healthy:
        status = "healthy"
    elif critical_healthy:
        status = "degraded"
    else:
        status = "unhealthy"

    return HealthResponse(
        status=status,
        version=settings.app_version,
        timestamp=datetime.utcnow(),
        services={k: v for k, v in services.items() if v is not None},
    )
