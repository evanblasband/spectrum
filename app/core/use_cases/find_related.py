"""Use case for finding related articles."""

import logging
from typing import Optional
from urllib.parse import urlparse

from app.core.interfaces.ai_provider import AIProviderInterface
from app.core.interfaces.article_fetcher import ArticleFetcherInterface
from app.core.interfaces.cache import CacheInterface
from app.core.interfaces.news_aggregator import NewsAggregatorInterface, NewsArticlePreview
from app.services.cache.cache_keys import CacheKeys
from app.services.fetchers.web_scraper import BLOCKED_SITES

logger = logging.getLogger(__name__)


def _is_blocked_source(url: str) -> bool:
    """Check if a URL is from a blocked source."""
    try:
        domain = urlparse(url).netloc.lower()
        # Remove www. prefix if present
        if domain.startswith("www."):
            domain = domain[4:]

        for blocked_domain in BLOCKED_SITES.keys():
            if domain == blocked_domain or domain.endswith("." + blocked_domain):
                return True
        return False
    except Exception:
        return False


class FindRelatedUseCase:
    """Use case for finding related articles."""

    def __init__(
        self,
        news_aggregator: NewsAggregatorInterface,
        ai_provider: AIProviderInterface,
        article_fetcher: ArticleFetcherInterface,
        cache: Optional[CacheInterface] = None,
    ):
        self.aggregator = news_aggregator
        self.ai = ai_provider
        self.fetcher = article_fetcher
        self.cache = cache

    async def execute(
        self,
        url: Optional[str] = None,
        keywords: Optional[list[str]] = None,
        topic: Optional[str] = None,
        limit: int = 5,
        days_back: int = 7,
    ) -> tuple[list[str], list[NewsArticlePreview]]:
        """
        Find related articles.

        Either provide a URL (to extract keywords from) or keywords/topic directly.

        Returns:
            Tuple of (keywords_used, articles_found)
        """
        # Check cache if URL provided
        if url and self.cache:
            cache_key = CacheKeys.related(url)
            cached = await self.cache.get(cache_key)
            if cached:
                logger.info(f"Cache hit for related articles: {cache_key}")
                return cached

        # Extract keywords from URL if provided
        if url and not keywords:
            keywords = await self._extract_keywords_from_url(url)

        # Use topic as keyword if provided
        if topic and not keywords:
            keywords = [topic]

        if not keywords:
            return [], []

        # Search for related articles
        articles = await self.aggregator.search(
            keywords=keywords,
            limit=limit,
            days_back=days_back,
        )

        # Filter out the original URL if present
        if url:
            articles = [a for a in articles if str(a.url) != url]

        # Filter out articles from blocked sources that we can't analyze
        original_count = len(articles)
        articles = [a for a in articles if not _is_blocked_source(str(a.url))]
        filtered_count = original_count - len(articles)
        if filtered_count > 0:
            logger.info(f"Filtered out {filtered_count} articles from blocked sources")

        # Cache results
        if url and self.cache:
            cache_key = CacheKeys.related(url)
            await self.cache.set(cache_key, (keywords, articles))

        return keywords, articles

    async def _extract_keywords_from_url(self, url: str) -> list[str]:
        """Extract keywords from article URL using AI."""
        try:
            # Fetch article
            article = await self.fetcher.fetch(url)

            # Extract topics using AI
            topics = await self.ai.extract_topics(article.title, article.content)

            # Combine keywords
            keywords = [topics.primary_topic]
            keywords.extend(topics.keywords[:4])  # Add top keywords

            return keywords[:5]  # Limit to 5 keywords

        except Exception as e:
            logger.error(f"Failed to extract keywords from {url}: {e}")
            return []
