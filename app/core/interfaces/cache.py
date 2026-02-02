"""Abstract interface for caching."""

from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Optional


class CacheInterface(ABC):
    """Abstract cache interface for storing and retrieving data."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        pass

    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[timedelta] = None,
    ) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live (uses default if not specified)
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete value from cache.

        Args:
            key: Cache key to delete
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists and hasn't expired
        """
        pass

    @abstractmethod
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern.

        Args:
            pattern: Pattern to match (supports * wildcard)

        Returns:
            Number of keys deleted
        """
        pass

    async def close(self) -> None:
        """Clean up resources. Override if needed."""
        pass
