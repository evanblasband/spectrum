"""Abstract interface for article fetching."""

from abc import ABC, abstractmethod

from app.core.entities.article import Article


class ArticleFetcherInterface(ABC):
    """Abstract interface for fetching article content from URLs."""

    @abstractmethod
    async def fetch(self, url: str) -> Article:
        """Fetch and parse article from URL.

        Args:
            url: Article URL to fetch

        Returns:
            Article entity with extracted content

        Raises:
            FetchError: If article cannot be fetched
            ParseError: If content cannot be extracted
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if fetcher is operational."""
        pass


class FetchError(Exception):
    """Error fetching article from URL."""

    def __init__(self, url: str, message: str, status_code: int | None = None):
        self.url = url
        self.status_code = status_code
        super().__init__(f"Failed to fetch {url}: {message}")


class ParseError(Exception):
    """Error parsing article content."""

    def __init__(self, url: str, message: str):
        self.url = url
        super().__init__(f"Failed to parse {url}: {message}")
