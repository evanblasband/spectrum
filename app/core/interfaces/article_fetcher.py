"""Abstract interface for article fetching."""

from abc import ABC, abstractmethod

from app.core.entities.article import Article
from app.core.errors import ErrorCode


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

    def __init__(
        self,
        url: str,
        message: str,
        code: ErrorCode = ErrorCode.CONTENT_EXTRACTION,
        details: dict | None = None,
    ):
        self.url = url
        self.message = message
        self.code = code
        self.details = details
        super().__init__(f"Failed to fetch {url}: {message}")
