"""Dependency injection for API routes."""

from functools import lru_cache
from typing import Optional

from fastapi import Depends

from app.config import Settings, get_settings
from app.core.interfaces.ai_provider import AIProviderInterface
from app.core.interfaces.cache import CacheInterface
from app.core.interfaces.news_aggregator import NewsAggregatorInterface
from app.core.use_cases.analyze_article import AnalyzeArticleUseCase
from app.core.use_cases.find_related import FindRelatedUseCase
from app.services.aggregators.newsapi import NewsAPIAggregator
from app.services.ai.factory import AIProviderFactory
from app.services.cache.memory_cache import MemoryCache
from app.services.fetchers.web_scraper import WebScraper

# Singleton instances
_cache_instance: Optional[CacheInterface] = None
_ai_provider_instance: Optional[AIProviderInterface] = None
_news_aggregator_instance: Optional[NewsAggregatorInterface] = None


def get_cache(settings: Settings = Depends(get_settings)) -> CacheInterface:
    """Get or create cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = MemoryCache(maxsize=settings.cache_max_size)
    return _cache_instance


def get_ai_provider(settings: Settings = Depends(get_settings)) -> AIProviderInterface:
    """Get or create AI provider instance."""
    global _ai_provider_instance
    if _ai_provider_instance is None:
        _ai_provider_instance = AIProviderFactory.get_default(settings)
    return _ai_provider_instance


def get_article_fetcher(settings: Settings = Depends(get_settings)) -> WebScraper:
    """Get article fetcher instance."""
    return WebScraper(
        timeout=settings.scraper_timeout_seconds,
        user_agent=settings.scraper_user_agent,
    )


def get_analyze_use_case(
    ai_provider: AIProviderInterface = Depends(get_ai_provider),
    fetcher: WebScraper = Depends(get_article_fetcher),
    cache: CacheInterface = Depends(get_cache),
) -> AnalyzeArticleUseCase:
    """Assemble analyze article use case with dependencies."""
    return AnalyzeArticleUseCase(
        ai_provider=ai_provider,
        article_fetcher=fetcher,
        cache=cache,
    )


def get_news_aggregator(
    settings: Settings = Depends(get_settings),
) -> Optional[NewsAggregatorInterface]:
    """Get or create news aggregator instance."""
    global _news_aggregator_instance
    if _news_aggregator_instance is None and settings.newsapi_key:
        _news_aggregator_instance = NewsAPIAggregator(api_key=settings.newsapi_key)
    return _news_aggregator_instance


def get_find_related_use_case(
    aggregator: Optional[NewsAggregatorInterface] = Depends(get_news_aggregator),
    ai_provider: AIProviderInterface = Depends(get_ai_provider),
    fetcher: WebScraper = Depends(get_article_fetcher),
    cache: CacheInterface = Depends(get_cache),
) -> Optional[FindRelatedUseCase]:
    """Assemble find related use case with dependencies."""
    if aggregator is None:
        return None
    return FindRelatedUseCase(
        news_aggregator=aggregator,
        ai_provider=ai_provider,
        article_fetcher=fetcher,
        cache=cache,
    )
