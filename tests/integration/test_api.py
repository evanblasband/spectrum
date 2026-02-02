"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint returns app info."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Spectrum"
    assert "version" in data
    assert "docs" in data


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_analyze_validation_error():
    """Test analyze endpoint returns validation error for invalid input."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/articles/analyze",
            json={"url": "not-a-valid-url"},
        )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_compare_validation_error():
    """Test compare endpoint returns validation error for too few articles."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/comparisons",
            json={"article_urls": ["https://example.com/article1"]},
        )

    assert response.status_code == 422  # Validation error - need at least 2


@pytest.mark.asyncio
async def test_related_validation_error():
    """Test related endpoint requires at least one search criteria."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/articles/related",
            json={},  # No url, keywords, or topic
        )

    assert response.status_code == 422  # Validation error
