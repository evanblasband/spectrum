"""Web scraper for fetching article content."""

from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from readability import Document

from app.core.entities.article import Article, ArticleSource
from app.core.interfaces.article_fetcher import (
    ArticleFetcherInterface,
    FetchError,
    ParseError,
)


class WebScraper(ArticleFetcherInterface):
    """Web scraper implementation for fetching article content.

    Uses readability-lxml for content extraction and BeautifulSoup
    for metadata parsing.
    """

    def __init__(
        self,
        timeout: int = 30,
        user_agent: str = "Spectrum/1.0 (News Analysis Bot)",
    ):
        self.timeout = timeout
        self.user_agent = user_agent
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={
                    "User-Agent": self.user_agent,
                    "Accept": "text/html,application/xhtml+xml",
                    "Accept-Language": "en-US,en;q=0.9",
                },
                follow_redirects=True,
            )
        return self._client

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
        client = await self.get_client()

        # Fetch HTML
        try:
            response = await client.get(url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise FetchError(url, str(e), e.response.status_code)
        except httpx.RequestError as e:
            raise FetchError(url, str(e))

        html = response.text

        # Parse with readability
        try:
            doc = Document(html)
            title = doc.title()
            content = self._clean_content(doc.summary())
        except Exception as e:
            raise ParseError(url, f"Readability extraction failed: {e}")

        if not content or len(content) < 100:
            raise ParseError(url, "Could not extract meaningful content")

        # Extract metadata with BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        metadata = self._extract_metadata(soup, url)

        # Build article entity
        article_id = Article.generate_id(url)
        domain = urlparse(url).netloc.replace("www.", "")

        return Article(
            id=article_id,
            url=url,
            title=title or metadata.get("title", "Unknown"),
            content=content,
            source=ArticleSource(
                name=metadata.get("site_name", domain),
                domain=domain,
            ),
            published_at=metadata.get("published_at"),
            author=metadata.get("author"),
            word_count=len(content.split()),
            fetched_at=datetime.utcnow(),
        )

    async def health_check(self) -> bool:
        """Check if scraper is operational."""
        try:
            client = await self.get_client()
            response = await client.get("https://httpbin.org/status/200")
            return response.status_code == 200
        except Exception:
            return False

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _clean_content(self, html: str) -> str:
        """Clean HTML content to plain text."""
        soup = BeautifulSoup(html, "lxml")

        # Remove unwanted elements
        for tag in soup.find_all(["script", "style", "nav", "footer", "aside"]):
            tag.decompose()

        # Get text
        text = soup.get_text(separator=" ", strip=True)

        # Clean up whitespace
        lines = [line.strip() for line in text.split("\n")]
        text = " ".join(line for line in lines if line)

        return text

    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract article metadata from HTML."""
        metadata = {}

        # Try Open Graph tags first
        og_title = soup.find("meta", property="og:title")
        if og_title:
            metadata["title"] = og_title.get("content")

        og_site_name = soup.find("meta", property="og:site_name")
        if og_site_name:
            metadata["site_name"] = og_site_name.get("content")

        # Try article tags
        article_author = soup.find("meta", attrs={"name": "author"})
        if article_author:
            metadata["author"] = article_author.get("content")

        # Try published time
        published = soup.find("meta", property="article:published_time")
        if published:
            try:
                from dateutil.parser import parse as parse_date
                metadata["published_at"] = parse_date(published.get("content"))
            except Exception:
                pass

        # Try time tag
        if "published_at" not in metadata:
            time_tag = soup.find("time")
            if time_tag and time_tag.get("datetime"):
                try:
                    from dateutil.parser import parse as parse_date
                    metadata["published_at"] = parse_date(time_tag.get("datetime"))
                except Exception:
                    pass

        return metadata
