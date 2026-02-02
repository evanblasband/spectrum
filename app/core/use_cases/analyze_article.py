"""Use case for analyzing a single article."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from app.core.entities.analysis import ArticleAnalysis
from app.core.entities.article import Article
from app.core.interfaces.ai_provider import AIProviderInterface
from app.core.interfaces.article_fetcher import ArticleFetcherInterface
from app.core.interfaces.cache import CacheInterface
from app.services.cache.cache_keys import CacheKeys

logger = logging.getLogger(__name__)


class AnalyzeArticleUseCase:
    """Use case for analyzing a single article."""

    def __init__(
        self,
        ai_provider: AIProviderInterface,
        article_fetcher: ArticleFetcherInterface,
        cache: Optional[CacheInterface] = None,
    ):
        self.ai = ai_provider
        self.fetcher = article_fetcher
        self.cache = cache

    async def execute(
        self,
        url: str,
        force_refresh: bool = False,
        include_points: bool = True,
    ) -> ArticleAnalysis:
        """
        Analyze an article's political leaning.

        1. Check cache for existing analysis
        2. Fetch article content (cached)
        3. Run AI analysis
        4. Cache and return results
        """
        logger.info(f"Analyzing article: {url}")

        # Check for cached analysis
        if self.cache and not force_refresh:
            cache_key = CacheKeys.analysis(url, self.ai.name)
            cached = await self.cache.get(cache_key)
            if cached:
                logger.info(f"Cache hit for analysis: {cache_key}")
                cached.cached = True
                return cached

        # Fetch article
        logger.info("Fetching article content")
        article = await self._fetch_article(url, force_refresh)

        # Run AI analysis in parallel
        logger.info("Running AI analysis")
        leaning, topics = await asyncio.gather(
            self.ai.analyze_political_leaning(
                article.title,
                article.content,
                article.source.name,
            ),
            self.ai.extract_topics(article.title, article.content),
        )

        # Extract points if requested
        points = []
        if include_points:
            points = await self.ai.extract_key_points(article.title, article.content)

        # Build result
        analysis = ArticleAnalysis(
            article_id=article.id,
            article_url=url,
            article_title=article.title,
            source_name=article.source.name,
            political_leaning=leaning,
            topics=topics,
            key_points=points,
            analyzed_at=datetime.now(timezone.utc),
            ai_provider=self.ai.name,
            cached=False,
        )

        # Cache result
        if self.cache:
            cache_key = CacheKeys.analysis(url, self.ai.name)
            await self.cache.set(cache_key, analysis)

        logger.info(f"Analysis complete: score={leaning.score}")
        return analysis

    async def _fetch_article(self, url: str, force_refresh: bool = False) -> Article:
        """Fetch article with caching."""
        if self.cache and not force_refresh:
            cache_key = CacheKeys.article(url)
            cached = await self.cache.get(cache_key)
            if cached:
                logger.info(f"Cache hit for article: {cache_key}")
                return cached

        article = await self.fetcher.fetch(url)

        if self.cache:
            cache_key = CacheKeys.article(url)
            await self.cache.set(cache_key, article)

        return article
