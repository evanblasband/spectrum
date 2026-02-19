"""Pytest fixtures for Spectrum tests."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock

from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.entities.article import Article, ArticleSource
from app.core.entities.analysis import (
    ArticleAnalysis,
    ArticlePoint,
    PoliticalLeaning,
    TopicAnalysis,
)
from app.core.interfaces.ai_provider import AIProviderInterface
from app.core.interfaces.article_fetcher import ArticleFetcherInterface
from app.core.interfaces.cache import CacheInterface


@pytest.fixture
def anyio_backend():
    """Use asyncio for async tests."""
    return "asyncio"


@pytest.fixture
async def client():
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_article():
    """Create a sample article for testing."""
    return Article(
        id="test123",
        url="https://example.com/article",
        title="Test Article About Politics",
        content="This is a test article about political topics. " * 50,
        source=ArticleSource(name="Test Source", domain="example.com"),
        published_at=datetime.utcnow(),
        author="Test Author",
        word_count=500,
        fetched_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_analysis():
    """Create a sample analysis for testing."""
    return ArticleAnalysis(
        article_id="test123",
        article_url="https://example.com/article",
        article_title="Test Article About Politics",
        source_name="Test Source",
        political_leaning=PoliticalLeaning(
            score=0.2,
            confidence=0.8,
            reasoning="Slightly right-leaning based on word choice",
            economic_score=0.3,
            social_score=0.1,
        ),
        topics=TopicAnalysis(
            primary_topic="Politics",
            secondary_topics=["Economy", "Policy"],
            keywords=["government", "policy", "economy", "reform"],
            entities=["Congress", "Senate"],
        ),
        key_points=[
            ArticlePoint(
                id="p1",
                statement="The economy is growing",
                supporting_quote="GDP increased by 3%",
                sentiment="positive",
            ),
            ArticlePoint(
                id="p2",
                statement="New policies are being proposed",
                supporting_quote=None,
                sentiment="neutral",
            ),
        ],
        analyzed_at=datetime.utcnow(),
        ai_provider="groq",
        cached=False,
    )


@pytest.fixture
def mock_ai_provider():
    """Create a mock AI provider."""
    mock = AsyncMock(spec=AIProviderInterface)
    mock.name = "mock"
    mock.supports_streaming = False

    mock.analyze_political_leaning.return_value = PoliticalLeaning(
        score=0.0,
        confidence=0.9,
        reasoning="Balanced coverage",
    )

    mock.extract_topics.return_value = TopicAnalysis(
        primary_topic="Test Topic",
        keywords=["test", "keywords"],
    )

    mock.extract_key_points.return_value = [
        ArticlePoint(
            id="p1",
            statement="Test point",
            sentiment="neutral",
        )
    ]

    mock.compare_points.return_value = []
    mock.health_check.return_value = True

    return mock


@pytest.fixture
def mock_article_fetcher(sample_article):
    """Create a mock article fetcher."""
    mock = AsyncMock(spec=ArticleFetcherInterface)
    mock.fetch.return_value = sample_article
    mock.health_check.return_value = True
    return mock


@pytest.fixture
def mock_cache():
    """Create a mock cache that stores nothing."""
    mock = AsyncMock(spec=CacheInterface)
    mock.get.return_value = None
    mock.exists.return_value = False
    return mock
