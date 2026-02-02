"""Core interfaces (ports) for dependency injection."""

from app.core.interfaces.ai_provider import AIProviderInterface
from app.core.interfaces.article_fetcher import (
    ArticleFetcherInterface,
    FetchError,
    ParseError,
)
from app.core.interfaces.cache import CacheInterface
from app.core.interfaces.news_aggregator import (
    NewsAggregatorInterface,
    NewsArticlePreview,
    NewsSearchResult,
)

__all__ = [
    "AIProviderInterface",
    "ArticleFetcherInterface",
    "FetchError",
    "ParseError",
    "CacheInterface",
    "NewsAggregatorInterface",
    "NewsArticlePreview",
    "NewsSearchResult",
]
