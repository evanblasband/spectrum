"""GNews API integration for finding related articles."""

from datetime import datetime, timedelta
from typing import Optional

import httpx

from app.core.interfaces.news_aggregator import (
    NewsAggregatorInterface,
    NewsArticlePreview,
    NewsSearchResult,
)


class GNewsAggregator(NewsAggregatorInterface):
    """GNews API implementation for news aggregation.

    Free tier: 100 requests/day, 1 year archive
    """

    BASE_URL = "https://gnews.io/api/v4"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def name(self) -> str:
        return "gnews"

    async def get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                timeout=30.0,
            )
        return self._client

    async def search(
        self,
        keywords: list[str],
        days_back: int = 7,
        limit: int = 10,
        language: str = "en",
        exclude_domains: list[str] | None = None,
    ) -> NewsSearchResult:
        """Search for news articles by keywords.

        Args:
            keywords: Search keywords
            days_back: How many days back to search
            limit: Maximum number of results (max 100)
            language: Language code
            exclude_domains: Domains to exclude (not supported by GNews)

        Returns:
            NewsSearchResult with matching articles
        """
        client = await self.get_client()

        # Build query - GNews uses AND by default, use OR for broader results
        query = " OR ".join(keywords)

        # Calculate date range
        from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        params = {
            "token": self.api_key,
            "q": query,
            "from": from_date,
            "lang": language,
            "max": min(limit, 100),
            "sortby": "relevance",
        }

        response = await client.get("/search", params=params)
        response.raise_for_status()

        data = response.json()

        articles = []
        for article in data.get("articles", []):
            if article.get("url") and article.get("title"):
                # Filter excluded domains manually
                if exclude_domains:
                    domain = self._extract_domain(article["url"])
                    if domain in exclude_domains:
                        continue

                articles.append(
                    NewsArticlePreview(
                        url=article["url"],
                        title=article["title"],
                        source=article.get("source", {}).get("name", "Unknown"),
                        published_at=self._parse_date(article.get("publishedAt")),
                        snippet=article.get("description"),
                        image_url=article.get("image"),
                    )
                )

        return NewsSearchResult(
            articles=articles,
            total_results=data.get("totalArticles", len(articles)),
            query_keywords=keywords,
            search_source=self.name,
        )

    async def search_by_topic(
        self,
        topic: str,
        days_back: int = 7,
        limit: int = 10,
    ) -> NewsSearchResult:
        """Search for news by topic/category.

        GNews supports these topics:
        world, nation, business, technology, entertainment, sports, science, health
        """
        client = await self.get_client()

        # Map common topics to GNews categories
        topic_map = {
            "world": "world",
            "politics": "nation",
            "business": "business",
            "tech": "technology",
            "technology": "technology",
            "entertainment": "entertainment",
            "sports": "sports",
            "science": "science",
            "health": "health",
        }

        gnews_topic = topic_map.get(topic.lower())

        if gnews_topic:
            params = {
                "token": self.api_key,
                "topic": gnews_topic,
                "lang": "en",
                "max": min(limit, 100),
            }
            response = await client.get("/top-headlines", params=params)
        else:
            # Fall back to search for non-standard topics
            return await self.search([topic], days_back, limit)

        response.raise_for_status()
        data = response.json()

        articles = []
        for article in data.get("articles", []):
            if article.get("url") and article.get("title"):
                articles.append(
                    NewsArticlePreview(
                        url=article["url"],
                        title=article["title"],
                        source=article.get("source", {}).get("name", "Unknown"),
                        published_at=self._parse_date(article.get("publishedAt")),
                        snippet=article.get("description"),
                        image_url=article.get("image"),
                    )
                )

        return NewsSearchResult(
            articles=articles,
            total_results=data.get("totalArticles", len(articles)),
            query_keywords=[topic],
            search_source=self.name,
        )

    async def health_check(self) -> bool:
        """Check if GNews API is available."""
        try:
            client = await self.get_client()
            response = await client.get(
                "/top-headlines",
                params={"token": self.api_key, "lang": "en", "max": 1},
            )
            return response.status_code == 200
        except Exception:
            return False

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO date string."""
        if not date_str:
            return None
        try:
            from dateutil.parser import parse as parse_date
            return parse_date(date_str)
        except Exception:
            return None

    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        return urlparse(url).netloc.replace("www.", "")
