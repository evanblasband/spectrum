"""NewsAPI.org implementation."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.interfaces.news_aggregator import NewsAggregatorInterface, NewsArticlePreview

logger = logging.getLogger(__name__)


class NewsAPIAggregator(NewsAggregatorInterface):
    """NewsAPI.org news aggregator implementation."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def name(self) -> str:
        return "newsapi"

    async def get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"X-Api-Key": self.api_key},
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
    async def search(
        self,
        keywords: list[str],
        limit: int = 5,
        days_back: int = 7,
    ) -> list[NewsArticlePreview]:
        """Search for articles matching keywords."""
        if not keywords:
            return []

        client = await self.get_client()

        # Build query
        query = " OR ".join(keywords[:5])  # Limit keywords
        from_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime(
            "%Y-%m-%d"
        )

        try:
            response = await client.get(
                "/everything",
                params={
                    "q": query,
                    "from": from_date,
                    "sortBy": "relevancy",
                    "pageSize": min(limit, 100),
                    "language": "en",
                },
            )
            response.raise_for_status()
            data = response.json()

            articles = []
            for article in data.get("articles", [])[:limit]:
                # Skip articles without URLs
                if not article.get("url"):
                    continue

                # Parse published date
                published_at = None
                if article.get("publishedAt"):
                    try:
                        published_at = datetime.fromisoformat(
                            article["publishedAt"].replace("Z", "+00:00")
                        )
                    except ValueError:
                        pass

                articles.append(
                    NewsArticlePreview(
                        url=article["url"],
                        title=article.get("title", "Untitled"),
                        source=article.get("source", {}).get("name", "Unknown"),
                        published_at=published_at,
                        snippet=article.get("description"),
                        image_url=article.get("urlToImage"),
                    )
                )

            logger.info(f"Found {len(articles)} articles for keywords: {keywords}")
            return articles

        except httpx.HTTPStatusError as e:
            logger.error(f"NewsAPI search failed: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"NewsAPI search error: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if aggregator is available."""
        try:
            client = await self.get_client()
            response = await client.get(
                "/top-headlines", params={"country": "us", "pageSize": 1}
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"NewsAPI health check failed: {e}")
            return False
