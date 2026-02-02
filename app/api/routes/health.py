"""Health check endpoints."""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health_check() -> dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "0.1.0",
    }


@router.get("/ready")
async def readiness_check() -> dict[str, Any]:
    """
    Readiness check - verifies all dependencies are available.
    
    For now, just returns healthy. Can be extended to check:
    - AI provider connectivity
    - News API availability
    - Cache connectivity
    """
    return {
        "status": "ready",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "api": "ok",
        },
    }
