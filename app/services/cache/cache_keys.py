"""Cache key generation utilities."""

import hashlib


class CacheKeys:
    """Cache key generation utilities.

    Key format: "{type}:{optional_subtype}:{hash}"

    Types:
    - article: Fetched article content
    - analysis: AI analysis results
    - search: News search results
    - related: Related articles for a URL
    """

    @staticmethod
    def _hash(value: str) -> str:
        """Generate short hash for cache key."""
        return hashlib.md5(value.encode()).hexdigest()[:12]

    @classmethod
    def article(cls, url: str) -> str:
        """Generate cache key for article content.

        Args:
            url: Article URL

        Returns:
            Cache key like "article:a1b2c3d4e5f6"
        """
        return f"article:{cls._hash(url)}"

    @classmethod
    def analysis(cls, url: str, provider: str) -> str:
        """Generate cache key for analysis result.

        Different providers may produce different results, so include
        provider in the key.

        Args:
            url: Article URL
            provider: AI provider name

        Returns:
            Cache key like "analysis:groq:a1b2c3d4e5f6"
        """
        return f"analysis:{provider}:{cls._hash(url)}"

    @classmethod
    def search(cls, keywords: list[str], source: str) -> str:
        """Generate cache key for search results.

        Args:
            keywords: Search keywords (order-independent)
            source: News aggregator name

        Returns:
            Cache key like "search:newsapi:a1b2c3d4e5f6"
        """
        # Sort keywords for consistent keys regardless of order
        keywords_str = "|".join(sorted(k.lower() for k in keywords))
        return f"search:{source}:{cls._hash(keywords_str)}"

    @classmethod
    def related(cls, url: str) -> str:
        """Generate cache key for related articles.

        Args:
            url: Original article URL

        Returns:
            Cache key like "related:a1b2c3d4e5f6"
        """
        return f"related:{cls._hash(url)}"

    @classmethod
    def comparison(cls, urls: list[str]) -> str:
        """Generate cache key for article comparison.

        Args:
            urls: List of article URLs being compared

        Returns:
            Cache key like "comparison:a1b2c3d4e5f6"
        """
        # Sort URLs for consistent keys regardless of order
        urls_str = "|".join(sorted(urls))
        return f"comparison:{cls._hash(urls_str)}"
