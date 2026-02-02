"""In-memory cache implementation."""

import asyncio
import logging
from datetime import timedelta
from typing import Any, Optional

from cachetools import TTLCache

from app.core.interfaces.cache import CacheInterface

logger = logging.getLogger(__name__)


class MemoryCache(CacheInterface):
    """Thread-safe in-memory cache with TTL support."""

    # Default TTLs for different data types
    DEFAULT_TTLS = {
        "article": timedelta(hours=1),
        "analysis": timedelta(hours=24),
        "search": timedelta(minutes=15),
        "related": timedelta(minutes=30),
    }

    def __init__(self, maxsize: int = 500):
        self._caches: dict[str, TTLCache] = {}
        self._lock = asyncio.Lock()
        self._maxsize = maxsize

    def _get_cache_for_type(self, key: str) -> TTLCache:
        """Get or create cache for key type."""
        # Extract type from key prefix (e.g., "article:xxx" -> "article")
        key_type = key.split(":")[0] if ":" in key else "default"
        ttl_seconds = self.DEFAULT_TTLS.get(
            key_type, timedelta(hours=1)
        ).total_seconds()

        if key_type not in self._caches:
            self._caches[key_type] = TTLCache(maxsize=self._maxsize, ttl=ttl_seconds)
        return self._caches[key_type]

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self._lock:
            cache = self._get_cache_for_type(key)
            return cache.get(key)

    async def set(
        self, key: str, value: Any, ttl: Optional[timedelta] = None
    ) -> None:
        """Set value in cache."""
        async with self._lock:
            cache = self._get_cache_for_type(key)
            cache[key] = value

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        async with self._lock:
            cache = self._get_cache_for_type(key)
            cache.pop(key, None)

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        async with self._lock:
            cache = self._get_cache_for_type(key)
            return key in cache

    async def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching pattern (simple prefix matching)."""
        count = 0
        async with self._lock:
            prefix = pattern.rstrip("*")
            for cache in self._caches.values():
                keys_to_delete = [k for k in list(cache.keys()) if k.startswith(prefix)]
                for key in keys_to_delete:
                    del cache[key]
                    count += 1
        return count
