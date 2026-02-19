"""
Live tests for news source compatibility.

These tests make real HTTP requests to news sites to verify they work.
They are NOT run automatically - use pytest with the -m flag:

    pytest tests/live/test_sources.py -m live -v

Or run all live tests:

    pytest -m live -v

To run a specific source:

    pytest tests/live/test_sources.py -k "npr" -m live -v

To run the comprehensive report:

    pytest tests/live/test_sources.py::test_all_sources_report -m live -v -s
"""

import asyncio
import re
from urllib.parse import urljoin
import pytest
from typing import NamedTuple

import httpx

from app.services.fetchers.web_scraper import WebScraper, SUPPORTED_SITES, BLOCKED_SITES, PARTIAL_SUPPORT_SITES


class SourceTestResult(NamedTuple):
    domain: str
    success: bool
    title: str | None
    error: str | None
    content_length: int
    article_url: str | None


# Section/index pages for each source - used to find actual article URLs
SOURCE_SECTION_URLS = {
    # Left-leaning
    "npr.org": "https://www.npr.org/sections/politics/",
    "theguardian.com": "https://www.theguardian.com/us-news",
    "huffpost.com": "https://www.huffpost.com/news/",
    "vox.com": "https://www.vox.com/policy",
    "motherjones.com": "https://www.motherjones.com/politics/",
    "slate.com": "https://slate.com/news-and-politics",
    "theatlantic.com": "https://www.theatlantic.com/politics/",
    "msnbc.com": "https://www.msnbc.com/opinion",

    # Center
    "apnews.com": "https://apnews.com/hub/politics",
    "bbc.com": "https://www.bbc.com/news/world/us_and_canada",
    "bbc.co.uk": "https://www.bbc.co.uk/news/world/us_and_canada",
    "pbs.org": "https://www.pbs.org/newshour/politics",
    "usatoday.com": "https://www.usatoday.com/news/nation/",
    "abcnews.go.com": "https://abcnews.go.com/Politics",
    "cbsnews.com": "https://www.cbsnews.com/politics/",
    "nbcnews.com": "https://www.nbcnews.com/politics",

    # Right-leaning
    "foxnews.com": "https://www.foxnews.com/politics",
    "nationalreview.com": "https://www.nationalreview.com/news/",
    "breitbart.com": "https://www.breitbart.com/politics/",
    "nypost.com": "https://nypost.com/news/",
    "washingtonexaminer.com": "https://www.washingtonexaminer.com/news/",
    "dailywire.com": "https://www.dailywire.com/news",

    # Major papers
    "nytimes.com": "https://www.nytimes.com/section/politics",
    "latimes.com": "https://www.latimes.com/politics",
    "chicagotribune.com": "https://www.chicagotribune.com/news/",
    "cnn.com": "https://www.cnn.com/politics",
}


async def find_article_url(section_url: str, domain: str) -> str | None:
    """
    Find an actual article URL from a section/index page.

    Looks for common article URL patterns in the HTML.
    """
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            http2=True,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
        ) as client:
            resp = await client.get(section_url)
            html = resp.text

            # Patterns for finding article URLs (ordered by specificity)
            patterns = [
                # Date-based URLs (most reliable for news)
                rf'href="(https?://[^"]*{re.escape(domain)}[^"]*/\d{{4}}/\d{{2}}/\d{{2}}/[^"]+)"',
                rf'href="(/\d{{4}}/\d{{2}}/\d{{2}}/[^"]+)"',
                # Article path patterns
                rf'href="(https?://[^"]*{re.escape(domain)}[^"]*/article/[^"]+)"',
                rf'href="(https?://[^"]*{re.escape(domain)}[^"]*/story/[^"]+)"',
                rf'href="(https?://[^"]*{re.escape(domain)}[^"]*/news/[a-z0-9-]+-[a-z0-9-]+)"',
                # Slug with numbers (common pattern)
                rf'href="(https?://[^"]*{re.escape(domain)}[^"]*/[a-z-]+/[a-z0-9-]+-\d+[^"]*)"',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                for match in matches[:5]:  # Try first 5 matches
                    url = match
                    if not url.startswith('http'):
                        url = urljoin(section_url, url)

                    # Skip section/category/tag pages
                    skip_patterns = ['/section/', '/category/', '/tag/', '/author/',
                                    '/topics/', '/search/', '.jpg', '.png', '.gif']
                    if any(skip in url.lower() for skip in skip_patterns):
                        continue

                    return url

    except Exception:
        pass

    return None


@pytest.fixture
def scraper():
    """Create a WebScraper instance for testing."""
    return WebScraper(timeout=30)


@pytest.mark.live
@pytest.mark.asyncio
class TestSupportedSources:
    """Test that all supported sources can be fetched."""

    @pytest.mark.parametrize("domain", SUPPORTED_SITES)
    async def test_source_fetchable(self, domain: str):
        """Test that a supported source can be fetched successfully."""
        section_url = SOURCE_SECTION_URLS.get(domain)
        if not section_url:
            pytest.skip(f"No test URL configured for {domain}")

        # Find an actual article URL
        article_url = await find_article_url(section_url, domain)
        if not article_url:
            pytest.skip(f"Could not find article URL for {domain}")

        scraper = WebScraper(timeout=30)
        try:
            article = await scraper.fetch(article_url)

            # Verify we got meaningful content
            assert article.title, f"No title extracted from {domain}"
            assert article.content, f"No content extracted from {domain}"
            assert len(article.content) > 100, f"Content too short from {domain}: {len(article.content)} chars"

            print(f"\n✓ {domain}: '{article.title[:60]}...' ({len(article.content)} chars)")

        except Exception as e:
            pytest.fail(f"Failed to fetch {domain} ({article_url}): {e}")
        finally:
            await scraper.close()


@pytest.mark.live
@pytest.mark.asyncio
class TestBlockedSources:
    """Verify that blocked sources are correctly identified."""

    @pytest.mark.parametrize("domain,reason", list(BLOCKED_SITES.items()))
    async def test_blocked_source_fails_gracefully(self, domain: str, reason: str, scraper: WebScraper):
        """Test that blocked sources fail with appropriate error messages."""
        # Construct a test URL
        url = f"https://www.{domain}/test-article"

        try:
            from app.core.interfaces.article_fetcher import ArticleFetchError

            with pytest.raises(ArticleFetchError) as exc_info:
                await scraper.fetch(url)

            # Verify the error message mentions the site is not supported
            assert "not supported" in str(exc_info.value).lower() or domain in str(exc_info.value).lower()
            print(f"\n✓ {domain}: Correctly blocked with message: {exc_info.value.message[:60]}")

        finally:
            await scraper.close()


@pytest.mark.live
@pytest.mark.asyncio
async def test_all_sources_report():
    """
    Run a comprehensive test of all sources and generate a report.

    This test finds real article URLs from each source's section page,
    then attempts to fetch and parse them.

    Run with: pytest tests/live/test_sources.py::test_all_sources_report -m live -v -s
    """
    results: list[SourceTestResult] = []

    print("\n" + "=" * 70)
    print("TESTING ALL SUPPORTED SOURCES")
    print("This finds real article URLs and tests fetching them.")
    print("=" * 70 + "\n")

    for domain in SUPPORTED_SITES:
        section_url = SOURCE_SECTION_URLS.get(domain)
        if not section_url:
            results.append(SourceTestResult(
                domain=domain,
                success=False,
                title=None,
                error="No section URL configured",
                content_length=0,
                article_url=None,
            ))
            print(f"⊘ {domain:<25} SKIP (no section URL)")
            continue

        # Find an actual article URL
        article_url = await find_article_url(section_url, domain)
        if not article_url:
            results.append(SourceTestResult(
                domain=domain,
                success=False,
                title=None,
                error="Could not find article URL on section page",
                content_length=0,
                article_url=None,
            ))
            print(f"⊘ {domain:<25} SKIP (no article found)")
            await asyncio.sleep(0.3)
            continue

        try:
            # Create fresh scraper for each request
            scraper = WebScraper(timeout=25)
            article = await scraper.fetch(article_url)
            await scraper.close()

            if article.content and len(article.content) > 200:
                results.append(SourceTestResult(
                    domain=domain,
                    success=True,
                    title=article.title[:50] if article.title else None,
                    error=None,
                    content_length=len(article.content),
                    article_url=article_url,
                ))
                print(f"✓ {domain:<25} OK ({len(article.content):,} chars)")
            else:
                results.append(SourceTestResult(
                    domain=domain,
                    success=False,
                    title=article.title,
                    error=f"Content too short: {len(article.content)} chars",
                    content_length=len(article.content),
                    article_url=article_url,
                ))
                print(f"✗ {domain:<25} FAIL (content too short: {len(article.content)} chars)")

        except Exception as e:
            error_msg = str(e)
            # Extract just the meaningful part of the error
            if ":" in error_msg:
                error_msg = error_msg.split(":")[-1].strip()[:40]
            else:
                error_msg = error_msg[:40]

            results.append(SourceTestResult(
                domain=domain,
                success=False,
                title=None,
                error=error_msg,
                content_length=0,
                article_url=article_url,
            ))
            print(f"✗ {domain:<25} FAIL ({error_msg})")

        # Small delay to avoid rate limiting
        await asyncio.sleep(0.5)

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    working = [r for r in results if r.success]
    failing = [r for r in results if not r.success]
    skipped = [r for r in results if r.article_url is None]

    print(f"\n✅ Working: {len(working)}/{len(results)}")
    print(f"❌ Failing: {len(failing) - len(skipped)}/{len(results)}")
    print(f"⊘  Skipped: {len(skipped)}/{len(results)}")

    if failing:
        actual_failures = [r for r in failing if r.article_url is not None]
        if actual_failures:
            print("\n❌ FAILING SOURCES (need investigation):")
            for r in actual_failures:
                print(f"  - {r.domain}: {r.error}")
                if r.article_url:
                    print(f"    URL: {r.article_url[:70]}...")

    print("\n✅ WORKING SOURCES:")
    for r in working:
        print(f"  - {r.domain}")

    # Don't fail the test - this is informational
    success_rate = len(working) / max(len(results) - len(skipped), 1)
    print(f"\nSuccess rate (excluding skipped): {success_rate:.0%}")
