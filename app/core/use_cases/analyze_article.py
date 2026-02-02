"""Use case for analyzing a single article's political leaning."""

import asyncio
from datetime import datetime

import structlog

from app.core.entities.analysis import ArticleAnalysis
from app.core.entities.article import Article
from app.core.interfaces.ai_provider import AIProviderInterface
from app.core.interfaces.article_fetcher import ArticleFetcherInterface
from app.core.interfaces.cache import CacheInterface
from app.services.cache.cache_keys import CacheKeys

logger = structlog.get_logger()


class AnalyzeArticleUseCase:
    """Use case for analyzing a single article.

    Orchestrates:
    1. Fetching article content (with caching)
    2. Running AI analysis for political leaning
    3. Extracting topics and keywords
    4. Extracting key points (optional)
    5. Caching results
    """

    def __init__(
        self,
        ai_provider: AIProviderInterface,
        article_fetcher: ArticleFetcherInterface,
        cache: CacheInterface,
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
        """Analyze an article's political leaning.

        Args:
            url: Article URL to analyze
            force_refresh: Bypass cache and re-analyze
            include_points: Extract key points (slower but more detailed)

        Returns:
            ArticleAnalysis with political leaning, topics, and points

        Raises:
            FetchError: If article cannot be fetched
            ParseError: If content cannot be extracted
        """
        log = logger.bind(url=url, provider=self.ai.name)

        # Check for cached analysis
        if not force_refresh:
            cache_key = CacheKeys.analysis(url, self.ai.name)
            cached = await self.cache.get(cache_key)
            if cached:
                log.info("cache_hit", cache_key=cache_key)
                cached.cached = True
                return cached

        # Fetch article (with caching)
        log.info("fetching_article")
        article = await self._fetch_article(url)
        log.info(
            "article_fetched",
            title=article.title[:50],
            word_count=article.word_count,
        )

        # Run AI analysis in parallel
        log.info("running_analysis")
        leaning, topics = await asyncio.gather(
            self.ai.analyze_political_leaning(
                article.title,
                article.content,
                article.source.name,
            ),
            self.ai.extract_topics(article.title, article.content),
        )

        # Extract key points if requested
        points = []
        if include_points:
            points = await self.ai.extract_key_points(
                article.title,
                article.content,
            )

        # Build result
        analysis = ArticleAnalysis(
            article_id=article.id,
            article_url=url,
            article_title=article.title,
            source_name=article.source.name,
            political_leaning=leaning,
            topics=topics,
            key_points=points,
            analyzed_at=datetime.utcnow(),
            ai_provider=self.ai.name,
            cached=False,
        )

        # Cache result
        cache_key = CacheKeys.analysis(url, self.ai.name)
        await self.cache.set(cache_key, analysis)

        log.info(
            "analysis_complete",
            score=leaning.score,
            label=leaning.label,
            confidence=leaning.confidence,
        )

        return analysis

    async def _fetch_article(self, url: str) -> Article:
        """Fetch article with caching.

        Args:
            url: Article URL

        Returns:
            Article entity
        """
        cache_key = CacheKeys.article(url)

        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        article = await self.fetcher.fetch(url)
        await self.cache.set(cache_key, article)

        return article
