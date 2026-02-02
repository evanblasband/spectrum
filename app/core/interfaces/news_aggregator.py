"""Abstract interface for news aggregators."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class NewsArticlePreview(BaseModel):
    """Preview of a news article from aggregator."""

    url: HttpUrl
    title: str
    source: str
    published_at: Optional[datetime] = None
    snippet: Optional[str] = None
    image_url: Optional[str] = None


class NewsAggregatorInterface(ABC):
    """Abstract interface for news aggregators."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Aggregator name for logging/tracking."""
        pass

    @abstractmethod
    async def search(
        self,
        keywords: list[str],
        limit: int = 5,
        days_back: int = 7,
    ) -> list[NewsArticlePreview]:
        """
        Search for articles matching keywords.

        Args:
            keywords: Search keywords
            limit: Maximum number of results
            days_back: How far back to search

        Returns:
            List of matching article previews
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if aggregator is available."""
        pass
