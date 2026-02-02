"""Dependency injection setup."""

from typing import Optional

from app.config import Settings, get_settings
from app.core.interfaces.ai_provider import AIProviderInterface
from app.core.interfaces.cache import CacheInterface
from app.core.interfaces.news_aggregator import NewsAggregatorInterface
from app.core.use_cases.analyze_article import AnalyzeArticleUseCase
from app.core.use_cases.compare_articles import CompareArticlesUseCase
from app.core.use_cases.find_related import FindRelatedUseCase
from app.services.ai.factory import AIProviderFactory
from app.services.aggregators.gnews import GNewsAggregator
from app.services.aggregators.newsapi import NewsAPIAggregator
from app.services.cache.memory_cache import MemoryCache
from app.services.fetchers.web_scraper import WebScraper

# Singleton instances (initialized on first use)
_cache_instance: Optional[CacheInterface] = None
_ai_provider_instance: Optional[AIProviderInterface] = None
_news_aggregator_instance: Optional[NewsAggregatorInterface] = None
_article_fetcher_instance: Optional[WebScraper] = None


def get_cache() -> CacheInterface:
    """Get or create cache instance."""
    global _cache_instance
    if _cache_instance is None:
        settings = get_settings()
        # For now, always use memory cache
        # Redis support can be added later
        _cache_instance = MemoryCache(maxsize=settings.cache_max_size)
    return _cache_instance


def get_ai_provider() -> AIProviderInterface:
    """Get or create AI provider instance."""
    global _ai_provider_instance
    if _ai_provider_instance is None:
        settings = get_settings()
        _ai_provider_instance = AIProviderFactory.get_default(settings)
    return _ai_provider_instance


def get_news_aggregator() -> NewsAggregatorInterface:
    """Get or create news aggregator instance."""
    global _news_aggregator_instance
    if _news_aggregator_instance is None:
        settings = get_settings()

        # Prefer NewsAPI, fall back to GNews
        if settings.newsapi_key:
            _news_aggregator_instance = NewsAPIAggregator(settings.newsapi_key)
        elif settings.gnews_api_key:
            _news_aggregator_instance = GNewsAggregator(settings.gnews_api_key)
        else:
            raise ValueError("No news API key configured. Set NEWSAPI_KEY or GNEWS_API_KEY.")

    return _news_aggregator_instance


def get_article_fetcher() -> WebScraper:
    """Get or create article fetcher instance."""
    global _article_fetcher_instance
    if _article_fetcher_instance is None:
        settings = get_settings()
        _article_fetcher_instance = WebScraper(
            timeout=settings.scraper_timeout_seconds,
            user_agent=settings.scraper_user_agent,
        )
    return _article_fetcher_instance


def get_analyze_use_case() -> AnalyzeArticleUseCase:
    """Assemble analyze article use case with dependencies."""
    return AnalyzeArticleUseCase(
        ai_provider=get_ai_provider(),
        article_fetcher=get_article_fetcher(),
        cache=get_cache(),
    )


def get_find_related_use_case() -> FindRelatedUseCase:
    """Assemble find related use case with dependencies."""
    return FindRelatedUseCase(
        news_aggregator=get_news_aggregator(),
        analyze_use_case=get_analyze_use_case(),
        cache=get_cache(),
    )


def get_compare_use_case() -> CompareArticlesUseCase:
    """Assemble compare articles use case with dependencies."""
    return CompareArticlesUseCase(
        ai_provider=get_ai_provider(),
        analyze_use_case=get_analyze_use_case(),
        cache=get_cache(),
    )


async def cleanup_resources():
    """Clean up all resources on shutdown."""
    global _cache_instance, _ai_provider_instance
    global _news_aggregator_instance, _article_fetcher_instance

    if _ai_provider_instance:
        await _ai_provider_instance.close()
        _ai_provider_instance = None

    if _news_aggregator_instance:
        await _news_aggregator_instance.close()
        _news_aggregator_instance = None

    if _article_fetcher_instance:
        await _article_fetcher_instance.close()
        _article_fetcher_instance = None

    if _cache_instance:
        await _cache_instance.close()
        _cache_instance = None
