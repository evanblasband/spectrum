"""Abstract interface for article fetching."""

from abc import ABC, abstractmethod

from app.core.entities.article import Article


class ArticleFetcherInterface(ABC):
    """Abstract interface for article fetchers."""

    @abstractmethod
    async def fetch(self, url: str) -> Article:
        """
        Fetch and parse article content from URL.

        Args:
            url: The article URL to fetch

        Returns:
            Article: Parsed article with content and metadata

        Raises:
            ArticleFetchError: If fetching or parsing fails
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if fetcher is operational."""
        pass


class ArticleFetchError(Exception):
    """Exception raised when article fetching fails."""

    def __init__(self, url: str, message: str):
        self.url = url
        self.message = message
        super().__init__(f"Failed to fetch {url}: {message}")
