"""Cache key generation utilities."""

import hashlib


class CacheKeys:
    """Cache key generation utilities."""

    @staticmethod
    def article(url: str) -> str:
        """Generate cache key for article content."""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        return f"article:{url_hash}"

    @staticmethod
    def analysis(url: str, provider: str) -> str:
        """Generate cache key for analysis result."""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        return f"analysis:{provider}:{url_hash}"

    @staticmethod
    def search(keywords: list[str], source: str) -> str:
        """Generate cache key for search results."""
        keywords_str = "|".join(sorted(keywords))
        kw_hash = hashlib.md5(keywords_str.encode()).hexdigest()[:12]
        return f"search:{source}:{kw_hash}"

    @staticmethod
    def related(url: str) -> str:
        """Generate cache key for related articles."""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        return f"related:{url_hash}"
