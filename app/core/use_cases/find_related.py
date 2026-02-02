"""Use case for finding related articles on the same topic."""

from urllib.parse import urlparse

import structlog

from app.core.entities.analysis import ArticleAnalysis
from app.core.interfaces.cache import CacheInterface
from app.core.interfaces.news_aggregator import (
    NewsAggregatorInterface,
    NewsArticlePreview,
    NewsSearchResult,
)
from app.core.use_cases.analyze_article import AnalyzeArticleUseCase
from app.services.cache.cache_keys import CacheKeys

logger = structlog.get_logger()


class FindRelatedUseCase:
    """Use case for finding related articles.

    Orchestrates:
    1. Analyzing original article (if URL provided)
    2. Searching news APIs for related articles
    3. Deduplicating and filtering results
    4. Optionally analyzing related articles
    """

    def __init__(
        self,
        news_aggregator: NewsAggregatorInterface,
        analyze_use_case: AnalyzeArticleUseCase,
        cache: CacheInterface,
    ):
        self.news = news_aggregator
        self.analyze = analyze_use_case
        self.cache = cache

    async def execute(
        self,
        url: str | None = None,
        keywords: list[str] | None = None,
        topic: str | None = None,
        limit: int = 5,
        days_back: int = 7,
        analyze_results: bool = False,
    ) -> dict:
        """Find related articles on the same topic.

        Must provide either url, keywords, or topic.

        Args:
            url: Original article URL (will extract keywords)
            keywords: Direct search keywords
            topic: Topic/category to search
            limit: Maximum number of results
            days_back: How many days back to search
            analyze_results: Run political analysis on results

        Returns:
            Dict with original_analysis (if URL), related articles, and optionally analyses
        """
        log = logger.bind(
            url=url,
            keywords=keywords,
            topic=topic,
            aggregator=self.news.name,
        )

        result = {
            "original_analysis": None,
            "search_keywords": [],
            "related_articles": [],
            "related_analyses": [],
        }

        # Get keywords from URL or direct input
        search_keywords = keywords or []
        exclude_domain = None

        if url:
            # Check cache for related articles
            cache_key = CacheKeys.related(url)
            cached = await self.cache.get(cache_key)
            if cached:
                log.info("cache_hit", cache_key=cache_key)
                return cached

            # Analyze original to get keywords
            log.info("analyzing_original")
            original = await self.analyze.execute(url, include_points=False)
            result["original_analysis"] = original

            # Use extracted keywords
            search_keywords = original.topics.keywords[:5]
            if original.topics.primary_topic:
                search_keywords.insert(0, original.topics.primary_topic)

            # Exclude original source from results
            exclude_domain = urlparse(url).netloc.replace("www.", "")

        elif topic:
            search_keywords = [topic]

        if not search_keywords:
            raise ValueError("Must provide url, keywords, or topic")

        result["search_keywords"] = search_keywords

        # Search for related articles
        log.info("searching_related", keywords=search_keywords)
        search_result = await self.news.search(
            keywords=search_keywords,
            days_back=days_back,
            limit=limit + 5,  # Get extras to allow for filtering
            exclude_domains=[exclude_domain] if exclude_domain else None,
        )

        # Deduplicate and filter
        related = self._deduplicate_and_filter(
            search_result.articles,
            exclude_url=url,
            limit=limit,
        )
        result["related_articles"] = related

        log.info("found_related", count=len(related))

        # Optionally analyze related articles
        if analyze_results and related:
            log.info("analyzing_related")
            analyses = []
            for article in related[:limit]:
                try:
                    analysis = await self.analyze.execute(
                        str(article.url),
                        include_points=False,
                    )
                    analyses.append(analysis)
                except Exception as e:
                    log.warning("related_analysis_failed", url=str(article.url), error=str(e))
            result["related_analyses"] = analyses

        # Cache results (if URL was provided)
        if url:
            cache_key = CacheKeys.related(url)
            await self.cache.set(cache_key, result)

        return result

    def _deduplicate_and_filter(
        self,
        articles: list[NewsArticlePreview],
        exclude_url: str | None = None,
        limit: int = 5,
    ) -> list[NewsArticlePreview]:
        """Deduplicate and filter article results.

        - Remove duplicates by URL
        - Remove original article
        - Ensure source diversity (max 2 per source)
        - Limit to requested count
        """
        seen_urls = set()
        source_counts: dict[str, int] = {}
        filtered = []

        for article in articles:
            url_str = str(article.url)

            # Skip original
            if exclude_url and url_str == exclude_url:
                continue

            # Skip duplicates
            if url_str in seen_urls:
                continue

            # Limit per source for diversity
            source = article.source
            if source_counts.get(source, 0) >= 2:
                continue

            seen_urls.add(url_str)
            source_counts[source] = source_counts.get(source, 0) + 1
            filtered.append(article)

            if len(filtered) >= limit:
                break

        return filtered
