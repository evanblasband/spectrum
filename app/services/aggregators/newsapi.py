"""NewsAPI.org integration for finding related articles."""

from datetime import datetime, timedelta
from typing import Optional

import httpx

from app.core.interfaces.news_aggregator import (
    NewsAggregatorInterface,
    NewsArticlePreview,
    NewsSearchResult,
)


class NewsAPIAggregator(NewsAggregatorInterface):
    """NewsAPI.org implementation for news aggregation.

    Free tier: 100 requests/day, 1 month old articles
    Developer tier: 250 requests/day, 1 month old articles
    """

    BASE_URL = "https://newsapi.org/v2"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def name(self) -> str:
        return "newsapi"

    async def get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={"X-Api-Key": self.api_key},
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
            days_back: How many days back to search (max 30 for free tier)
            limit: Maximum number of results (max 100)
            language: Language code
            exclude_domains: Domains to exclude

        Returns:
            NewsSearchResult with matching articles
        """
        client = await self.get_client()

        # Build query
        query = " OR ".join(keywords)

        # Calculate date range (NewsAPI free tier limited to 1 month)
        from_date = (datetime.utcnow() - timedelta(days=min(days_back, 30))).strftime(
            "%Y-%m-%d"
        )

        params = {
            "q": query,
            "from": from_date,
            "language": language,
            "sortBy": "relevancy",
            "pageSize": min(limit, 100),
        }

        if exclude_domains:
            params["excludeDomains"] = ",".join(exclude_domains)

        response = await client.get("/everything", params=params)
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
                        image_url=article.get("urlToImage"),
                    )
                )

        return NewsSearchResult(
            articles=articles,
            total_results=data.get("totalResults", len(articles)),
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

        NewsAPI supports these categories:
        business, entertainment, general, health, science, sports, technology
        """
        client = await self.get_client()

        # Map common topics to NewsAPI categories
        category_map = {
            "business": "business",
            "tech": "technology",
            "technology": "technology",
            "science": "science",
            "health": "health",
            "sports": "sports",
            "entertainment": "entertainment",
            "politics": "general",
        }

        category = category_map.get(topic.lower())

        if category:
            # Use top-headlines endpoint for categories
            params = {
                "category": category,
                "country": "us",
                "pageSize": min(limit, 100),
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
                        image_url=article.get("urlToImage"),
                    )
                )

        return NewsSearchResult(
            articles=articles,
            total_results=data.get("totalResults", len(articles)),
            query_keywords=[topic],
            search_source=self.name,
        )

    async def health_check(self) -> bool:
        """Check if NewsAPI is available."""
        try:
            client = await self.get_client()
            response = await client.get(
                "/top-headlines",
                params={"country": "us", "pageSize": 1},
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
