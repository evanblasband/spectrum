"""Abstract interface for news aggregation services."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class NewsArticlePreview(BaseModel):
    """Preview of a news article from search results."""

    url: HttpUrl
    title: str
    source: str
    published_at: Optional[datetime] = None
    snippet: Optional[str] = None
    image_url: Optional[HttpUrl] = None


class NewsSearchResult(BaseModel):
    """Result of a news search."""

    articles: list[NewsArticlePreview]
    total_results: int
    query_keywords: list[str]
    search_source: str


class NewsAggregatorInterface(ABC):
    """Abstract interface for news aggregation APIs."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Aggregator name for logging/tracking."""
        pass

    @abstractmethod
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
            limit: Maximum number of results
            language: Language code (default: en)
            exclude_domains: Domains to exclude from results

        Returns:
            NewsSearchResult with matching articles
        """
        pass

    @abstractmethod
    async def search_by_topic(
        self,
        topic: str,
        days_back: int = 7,
        limit: int = 10,
    ) -> NewsSearchResult:
        """Search for news by topic/category.

        Args:
            topic: Topic or category name
            days_back: How many days back to search
            limit: Maximum number of results

        Returns:
            NewsSearchResult with matching articles
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if aggregator API is available."""
        pass

    async def close(self) -> None:
        """Clean up resources. Override if needed."""
        pass
