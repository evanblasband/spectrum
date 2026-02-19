"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app

# Create transport for ASGI testing
transport = ASGITransport(app=app)


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint returns app info."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Spectrum"
    assert "version" in data
    assert "docs" in data


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_analyze_validation_error():
    """Test analyze endpoint returns validation error for invalid input."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/articles/analyze",
            json={"url": "not-a-valid-url"},
        )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_compare_validation_error():
    """Test compare endpoint returns validation error for too few articles."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/comparisons",
            json={"article_urls": ["https://example.com/article1"]},
        )

    assert response.status_code == 422  # Validation error - need at least 2


@pytest.mark.asyncio
async def test_related_validation_error():
    """Test related endpoint requires at least one search criteria."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/articles/related",
            json={},  # No url, keywords, or topic
        )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_analyze_blocked_source_returns_structured_error():
    """Test blocked source returns structured error response."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/articles/analyze",
            json={"url": "https://www.nytimes.com/some-article"},
        )

    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert data["error"]["code"] == "BLOCKED_SOURCE"
    assert data["error"]["retryable"] is False
    assert "suggestion" in data["error"]
    assert "nytimes" in data["error"]["details"].get("domain", "")


@pytest.mark.asyncio
async def test_analyze_blocked_source_wsj():
    """Test WSJ blocked source returns structured error."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/articles/analyze",
            json={"url": "https://www.wsj.com/articles/some-article"},
        )

    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "BLOCKED_SOURCE"
