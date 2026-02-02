"""Web scraping implementation for article fetching."""

import hashlib
import logging
import re
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.entities.article import Article, ArticleSource
from app.core.interfaces.article_fetcher import ArticleFetchError, ArticleFetcherInterface

logger = logging.getLogger(__name__)


class WebScraper(ArticleFetcherInterface):
    """Web scraper for extracting article content from URLs."""

    def __init__(
        self,
        timeout: int = 30,
        user_agent: str = "Spectrum/1.0 (News Analysis Bot)",
    ):
        self.timeout = timeout
        self.user_agent = user_agent
        self._client: httpx.AsyncClient | None = None

    async def get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={"User-Agent": self.user_agent},
                follow_redirects=True,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
    async def fetch(self, url: str) -> Article:
        """Fetch and parse article content from URL."""
        logger.info(f"Fetching article from {url}")

        try:
            client = await self.get_client()
            response = await client.get(url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ArticleFetchError(url, f"HTTP {e.response.status_code}")
        except httpx.RequestError as e:
            raise ArticleFetchError(url, str(e))

        html = response.text
        soup = BeautifulSoup(html, "lxml")

        # Extract metadata
        title = self._extract_title(soup)
        content = self._extract_content(soup)
        author = self._extract_author(soup)
        published_at = self._extract_published_date(soup)

        if not content or len(content) < 100:
            raise ArticleFetchError(url, "Could not extract article content")

        # Parse domain for source info
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace("www.", "")
        source_name = self._domain_to_source_name(domain)

        # Generate unique ID from URL
        article_id = hashlib.md5(url.encode()).hexdigest()[:12]

        return Article(
            id=article_id,
            url=url,
            title=title,
            content=content,
            source=ArticleSource(name=source_name, domain=domain),
            published_at=published_at,
            author=author,
            word_count=len(content.split()),
            fetched_at=datetime.now(timezone.utc),
        )

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title."""
        # Try Open Graph title first
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"].strip()

        # Try standard title tag
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text().strip()
            # Remove common suffixes like " - News Site Name"
            title = re.sub(r"\s*[-|]\s*[^-|]+$", "", title)
            return title

        # Try h1 tag
        h1 = soup.find("h1")
        if h1:
            return h1.get_text().strip()

        return "Untitled Article"

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main article content."""
        # Remove unwanted elements
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "ad"]):
            tag.decompose()

        # Try article tag first
        article = soup.find("article")
        if article:
            paragraphs = article.find_all("p")
            if paragraphs:
                return self._clean_text("\n\n".join(p.get_text() for p in paragraphs))

        # Try common content containers
        content_selectors = [
            {"class_": re.compile(r"article[-_]?(body|content|text)", re.I)},
            {"class_": re.compile(r"(post|entry)[-_]?(body|content)", re.I)},
            {"class_": re.compile(r"story[-_]?(body|content)", re.I)},
            {"id": re.compile(r"article[-_]?(body|content)", re.I)},
        ]

        for selector in content_selectors:
            container = soup.find("div", **selector)
            if container:
                paragraphs = container.find_all("p")
                if paragraphs:
                    return self._clean_text("\n\n".join(p.get_text() for p in paragraphs))

        # Fallback: get all paragraphs with substantial text
        all_paragraphs = soup.find_all("p")
        content_paragraphs = [
            p.get_text() for p in all_paragraphs if len(p.get_text().strip()) > 50
        ]

        return self._clean_text("\n\n".join(content_paragraphs))

    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article author."""
        # Try meta tag
        author_meta = soup.find("meta", {"name": "author"})
        if author_meta and author_meta.get("content"):
            return author_meta["content"].strip()

        # Try common author patterns
        author_patterns = [
            {"class_": re.compile(r"author", re.I)},
            {"rel": "author"},
            {"itemprop": "author"},
        ]

        for pattern in author_patterns:
            author_el = soup.find(["a", "span", "div"], **pattern)
            if author_el:
                text = author_el.get_text().strip()
                if text and len(text) < 100:  # Sanity check
                    return text

        return None

    def _extract_published_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract article publication date."""
        # Try meta tags
        date_metas = [
            ("meta", {"property": "article:published_time"}),
            ("meta", {"name": "publication_date"}),
            ("meta", {"name": "date"}),
            ("time", {"datetime": True}),
        ]

        for tag_name, attrs in date_metas:
            el = soup.find(tag_name, **attrs)
            if el:
                date_str = el.get("content") or el.get("datetime")
                if date_str:
                    try:
                        # Handle ISO format
                        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    except ValueError:
                        pass

        return None

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove empty lines
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return "\n\n".join(lines)

    def _domain_to_source_name(self, domain: str) -> str:
        """Convert domain to readable source name."""
        # Common mappings
        known_sources = {
            "nytimes.com": "The New York Times",
            "washingtonpost.com": "The Washington Post",
            "cnn.com": "CNN",
            "foxnews.com": "Fox News",
            "bbc.com": "BBC",
            "bbc.co.uk": "BBC",
            "reuters.com": "Reuters",
            "apnews.com": "Associated Press",
            "huffpost.com": "HuffPost",
            "breitbart.com": "Breitbart",
            "theguardian.com": "The Guardian",
            "wsj.com": "Wall Street Journal",
            "politico.com": "Politico",
            "thehill.com": "The Hill",
            "npr.org": "NPR",
            "nbcnews.com": "NBC News",
            "cbsnews.com": "CBS News",
            "abcnews.go.com": "ABC News",
            "msnbc.com": "MSNBC",
            "economist.com": "The Economist",
            "nationalreview.com": "National Review",
            "motherjones.com": "Mother Jones",
            "slate.com": "Slate",
            "vox.com": "Vox",
            "theatlantic.com": "The Atlantic",
        }

        if domain in known_sources:
            return known_sources[domain]

        # Convert domain to title case
        name = domain.split(".")[0]
        return name.replace("-", " ").replace("_", " ").title()

    async def health_check(self) -> bool:
        """Check if fetcher is operational."""
        try:
            client = await self.get_client()
            response = await client.get("https://httpbin.org/get")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Web scraper health check failed: {e}")
            return False
