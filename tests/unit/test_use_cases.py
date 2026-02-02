"""Unit tests for use cases."""

import pytest
from unittest.mock import AsyncMock

from app.core.use_cases.analyze_article import AnalyzeArticleUseCase
from app.core.entities.analysis import PoliticalLeaning, TopicAnalysis, ArticlePoint


@pytest.mark.asyncio
async def test_analyze_article_success(
    mock_ai_provider,
    mock_article_fetcher,
    mock_cache,
    sample_article,
):
    """Test successful article analysis."""
    # Setup
    use_case = AnalyzeArticleUseCase(
        ai_provider=mock_ai_provider,
        article_fetcher=mock_article_fetcher,
        cache=mock_cache,
    )

    # Execute
    result = await use_case.execute(
        url="https://example.com/article",
        include_points=True,
    )

    # Verify
    assert result.article_id == sample_article.id
    assert result.political_leaning.score == 0.0
    assert result.ai_provider == "mock"

    # Verify services were called
    mock_article_fetcher.fetch.assert_called_once()
    mock_ai_provider.analyze_political_leaning.assert_called_once()
    mock_ai_provider.extract_topics.assert_called_once()
    mock_ai_provider.extract_key_points.assert_called_once()
    mock_cache.set.assert_called()


@pytest.mark.asyncio
async def test_analyze_article_cached(
    mock_ai_provider,
    mock_article_fetcher,
    mock_cache,
    sample_analysis,
):
    """Test that cached results are returned."""
    # Setup - cache returns existing analysis
    mock_cache.get.return_value = sample_analysis

    use_case = AnalyzeArticleUseCase(
        ai_provider=mock_ai_provider,
        article_fetcher=mock_article_fetcher,
        cache=mock_cache,
    )

    # Execute
    result = await use_case.execute(
        url="https://example.com/article",
    )

    # Verify cache was checked
    mock_cache.get.assert_called()

    # Verify AI provider was NOT called (cached result used)
    mock_ai_provider.analyze_political_leaning.assert_not_called()

    # Verify result is marked as cached
    assert result.cached is True


@pytest.mark.asyncio
async def test_analyze_article_force_refresh(
    mock_ai_provider,
    mock_article_fetcher,
    mock_cache,
    sample_analysis,
):
    """Test that force_refresh bypasses cache."""
    # Setup - cache has data but we want fresh
    mock_cache.get.return_value = sample_analysis

    use_case = AnalyzeArticleUseCase(
        ai_provider=mock_ai_provider,
        article_fetcher=mock_article_fetcher,
        cache=mock_cache,
    )

    # Execute with force_refresh
    result = await use_case.execute(
        url="https://example.com/article",
        force_refresh=True,
    )

    # Verify AI provider WAS called (cache bypassed)
    mock_ai_provider.analyze_political_leaning.assert_called_once()

    # Verify result is NOT marked as cached
    assert result.cached is False


@pytest.mark.asyncio
async def test_analyze_article_without_points(
    mock_ai_provider,
    mock_article_fetcher,
    mock_cache,
):
    """Test analysis without key point extraction."""
    use_case = AnalyzeArticleUseCase(
        ai_provider=mock_ai_provider,
        article_fetcher=mock_article_fetcher,
        cache=mock_cache,
    )

    # Execute without points
    result = await use_case.execute(
        url="https://example.com/article",
        include_points=False,
    )

    # Verify key points were NOT extracted
    mock_ai_provider.extract_key_points.assert_not_called()
    assert result.key_points == []
