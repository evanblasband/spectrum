"""Web scraping implementation for article fetching."""

import hashlib
import logging
import re
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.entities.article import Article, ArticleSource
from app.core.errors import ErrorCode
from app.core.interfaces.article_fetcher import ArticleFetchError, ArticleFetcherInterface


class RetryableError(Exception):
    """Error that should be retried (e.g., timeouts, 5xx errors)."""
    pass


# Sites known to block automated access or require authentication
BLOCKED_SITES = {
    "washingtonpost.com": "Washington Post uses aggressive bot protection",
    "wsj.com": "Wall Street Journal requires subscription",
    "reuters.com": "Reuters requires authentication",
    "politico.com": "Politico blocks automated access",
    "thehill.com": "The Hill blocks automated access",
    "thefederalist.com": "The Federalist blocks automated access",
    "nytimes.com": "NY Times blocks automated access",
}

# Sites confirmed to work reliably
SUPPORTED_SITES = [
    # Confirmed working
    "npr.org",
    "bbc.com",
    "bbc.co.uk",
    "cnn.com",
    "foxnews.com",
    "breitbart.com",
    "latimes.com",
    "theguardian.com",
]

# Sites that may work but have inconsistent results
# (JavaScript-heavy, content extraction issues, or intermittent blocks)
PARTIAL_SUPPORT_SITES = [
    "huffpost.com",
    "vox.com",
    "motherjones.com",
    "slate.com",
    "theatlantic.com",
    "msnbc.com",
    "apnews.com",
    "pbs.org",
    "usatoday.com",
    "abcnews.go.com",
    "cbsnews.com",
    "nbcnews.com",
    "nationalreview.com",
    "nypost.com",
    "washingtonexaminer.com",
    "dailywire.com",
    "chicagotribune.com",
]

logger = logging.getLogger(__name__)


class WebScraper(ArticleFetcherInterface):
    """Web scraper for extracting article content from URLs."""

    # Browser-like User-Agent to avoid 403 blocks
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    def __init__(
        self,
        timeout: int = 30,
        user_agent: str | None = None,
    ):
        self.timeout = timeout
        self.user_agent = user_agent or self.DEFAULT_USER_AGENT
        self._client: httpx.AsyncClient | None = None

    async def get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with browser-like headers."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={
                    "User-Agent": self.user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                },
                follow_redirects=True,
                http2=True,  # Many news sites require HTTP/2
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")
        return domain

    def _check_blocked_site(self, url: str) -> None:
        """Check if URL is from a known blocked site and raise appropriate error."""
        domain = self._get_domain(url)
        for blocked_domain, reason in BLOCKED_SITES.items():
            if domain == blocked_domain or domain.endswith("." + blocked_domain):
                raise ArticleFetchError(
                    url,
                    f"{reason}. This source is not supported.",
                    code=ErrorCode.BLOCKED_SOURCE,
                    details={"domain": blocked_domain},
                )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_exception_type(RetryableError),
        reraise=True,
    )
    async def fetch(self, url: str) -> Article:
        """Fetch and parse article content from URL."""
        logger.info(f"Fetching article from {url}")

        # Check for known blocked sites first
        self._check_blocked_site(url)

        try:
            client = await self.get_client()
            response = await client.get(url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            # Don't retry client errors (4xx) - they won't recover
            if status_code == 403:
                raise ArticleFetchError(
                    url,
                    "Access denied (403). This site may block automated access.",
                    code=ErrorCode.BLOCKED_SOURCE,
                )
            elif status_code == 404:
                raise ArticleFetchError(
                    url,
                    "Article not found (404). The URL may be incorrect or the article was removed.",
                    code=ErrorCode.NOT_FOUND,
                )
            elif status_code == 429:
                raise ArticleFetchError(
                    url,
                    "Too many requests. Please try again later.",
                    code=ErrorCode.RATE_LIMITED,
                )
            elif 400 <= status_code < 500:
                raise ArticleFetchError(
                    url,
                    f"HTTP error {status_code}",
                    code=ErrorCode.NETWORK_ERROR,
                )
            else:
                # Server errors (5xx) are retriable
                raise RetryableError(f"HTTP error {status_code}")
        except httpx.TimeoutException:
            # Timeouts are retriable
            raise RetryableError(f"Request timed out")
        except httpx.RequestError as e:
            # Connection errors are retriable
            raise RetryableError(f"Connection error: {str(e)}")

        html = response.text
        soup = BeautifulSoup(html, "lxml")

        # Extract metadata
        title = self._extract_title(soup)
        content = self._extract_content(soup)
        author = self._extract_author(soup)
        published_at = self._extract_published_date(soup)

        if not content or len(content) < 100:
            raise ArticleFetchError(
                url,
                "Could not extract article content",
                code=ErrorCode.CONTENT_EXTRACTION,
            )

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
        # Remove unwanted elements (but NOT article or main)
        for tag in soup(["script", "style", "nav", "aside", "ad", "noscript"]):
            tag.decompose()

        # Try article tag first
        article = soup.find("article")
        if article:
            paragraphs = article.find_all("p")
            if paragraphs:
                content = self._clean_text("\n\n".join(p.get_text() for p in paragraphs))
                if len(content) >= 100:
                    return content

        # Try main tag (many modern sites use this)
        main = soup.find("main")
        if main:
            paragraphs = main.find_all("p")
            if paragraphs:
                content = self._clean_text("\n\n".join(p.get_text() for p in paragraphs))
                if len(content) >= 100:
                    return content

        # Try common content container classes
        content_selectors = [
            {"class_": re.compile(r"article[-_]?(body|content|text)", re.I)},
            {"class_": re.compile(r"(post|entry)[-_]?(body|content)", re.I)},
            {"class_": re.compile(r"story[-_]?(body|content)", re.I)},
            {"class_": re.compile(r"rich[-_]?text", re.I)},
            {"id": re.compile(r"article[-_]?(body|content)", re.I)},
            {"itemprop": "articleBody"},
        ]

        for selector in content_selectors:
            container = soup.find(["div", "section"], **selector)
            if container:
                paragraphs = container.find_all("p")
                if paragraphs:
                    content = self._clean_text("\n\n".join(p.get_text() for p in paragraphs))
                    if len(content) >= 100:
                        return content

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
        # Try Open Graph / meta tags first
        og_time = soup.find("meta", property="article:published_time")
        if og_time and og_time.get("content"):
            try:
                return datetime.fromisoformat(og_time["content"].replace("Z", "+00:00"))
            except ValueError:
                pass

        # Try meta name attributes
        for meta_name in ["publication_date", "date", "pubdate"]:
            meta = soup.find("meta", attrs={"name": meta_name})
            if meta and meta.get("content"):
                try:
                    return datetime.fromisoformat(meta["content"].replace("Z", "+00:00"))
                except ValueError:
                    pass

        # Try time element with datetime attribute
        time_el = soup.find("time", attrs={"datetime": True})
        if time_el and time_el.get("datetime"):
            try:
                return datetime.fromisoformat(time_el["datetime"].replace("Z", "+00:00"))
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
