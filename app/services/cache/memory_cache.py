"""In-memory cache implementation with TTL support."""

import asyncio
from datetime import timedelta
from typing import Any, Optional

from cachetools import TTLCache

from app.core.interfaces.cache import CacheInterface


class MemoryCache(CacheInterface):
    """Thread-safe in-memory cache with TTL support.

    Uses separate caches for different data types with appropriate TTLs.
    """

    # Default TTLs for different data types (extracted from key prefix)
    DEFAULT_TTLS = {
        "article": timedelta(hours=1),
        "analysis": timedelta(hours=24),
        "search": timedelta(minutes=15),
        "related": timedelta(minutes=30),
        "default": timedelta(hours=1),
    }

    def __init__(self, maxsize: int = 500):
        """Initialize memory cache.

        Args:
            maxsize: Maximum number of items per cache type
        """
        self._caches: dict[str, TTLCache] = {}
        self._lock = asyncio.Lock()
        self._maxsize = maxsize

    def _get_key_type(self, key: str) -> str:
        """Extract type from cache key prefix."""
        if ":" in key:
            return key.split(":")[0]
        return "default"

    def _get_cache_for_type(self, key_type: str) -> TTLCache:
        """Get or create cache for key type."""
        if key_type not in self._caches:
            ttl = self.DEFAULT_TTLS.get(key_type, self.DEFAULT_TTLS["default"])
            self._caches[key_type] = TTLCache(
                maxsize=self._maxsize,
                ttl=ttl.total_seconds(),
            )
        return self._caches[key_type]

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key (format: "type:identifier")

        Returns:
            Cached value or None if not found/expired
        """
        async with self._lock:
            key_type = self._get_key_type(key)
            cache = self._get_cache_for_type(key_type)
            return cache.get(key)

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[timedelta] = None,
    ) -> None:
        """Set value in cache.

        Args:
            key: Cache key (format: "type:identifier")
            value: Value to cache
            ttl: Optional custom TTL (uses default for key type if not specified)
        """
        async with self._lock:
            key_type = self._get_key_type(key)
            cache = self._get_cache_for_type(key_type)
            cache[key] = value

    async def delete(self, key: str) -> None:
        """Delete value from cache.

        Args:
            key: Cache key to delete
        """
        async with self._lock:
            key_type = self._get_key_type(key)
            cache = self._get_cache_for_type(key_type)
            cache.pop(key, None)

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists and hasn't expired
        """
        async with self._lock:
            key_type = self._get_key_type(key)
            cache = self._get_cache_for_type(key_type)
            return key in cache

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern.

        Supports simple prefix matching with * wildcard.

        Args:
            pattern: Pattern to match (e.g., "article:*", "analysis:groq:*")

        Returns:
            Number of keys deleted
        """
        prefix = pattern.rstrip("*")
        count = 0

        async with self._lock:
            for cache in self._caches.values():
                # Get keys to delete (can't modify during iteration)
                keys_to_delete = [
                    k for k in list(cache.keys())
                    if k.startswith(prefix)
                ]
                for key in keys_to_delete:
                    del cache[key]
                    count += 1

        return count

    async def get_stats(self) -> dict:
        """Get cache statistics for monitoring.

        Returns:
            Dict with cache size and hit rate info per type
        """
        async with self._lock:
            stats = {}
            for key_type, cache in self._caches.items():
                stats[key_type] = {
                    "size": len(cache),
                    "maxsize": cache.maxsize,
                    "ttl_seconds": cache.ttl,
                }
            return stats
