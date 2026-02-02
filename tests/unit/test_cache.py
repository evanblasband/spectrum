"""Unit tests for cache implementation."""

import pytest
from datetime import timedelta

from app.services.cache.memory_cache import MemoryCache
from app.services.cache.cache_keys import CacheKeys


@pytest.mark.asyncio
async def test_memory_cache_set_get():
    """Test basic set and get operations."""
    cache = MemoryCache(maxsize=100)

    await cache.set("test:key1", "value1")
    result = await cache.get("test:key1")

    assert result == "value1"


@pytest.mark.asyncio
async def test_memory_cache_get_missing():
    """Test get returns None for missing keys."""
    cache = MemoryCache(maxsize=100)

    result = await cache.get("nonexistent:key")

    assert result is None


@pytest.mark.asyncio
async def test_memory_cache_delete():
    """Test delete removes key."""
    cache = MemoryCache(maxsize=100)

    await cache.set("test:key1", "value1")
    await cache.delete("test:key1")
    result = await cache.get("test:key1")

    assert result is None


@pytest.mark.asyncio
async def test_memory_cache_exists():
    """Test exists checks key presence."""
    cache = MemoryCache(maxsize=100)

    await cache.set("test:key1", "value1")

    assert await cache.exists("test:key1") is True
    assert await cache.exists("test:key2") is False


@pytest.mark.asyncio
async def test_memory_cache_clear_pattern():
    """Test clear_pattern removes matching keys."""
    cache = MemoryCache(maxsize=100)

    await cache.set("article:abc", "value1")
    await cache.set("article:def", "value2")
    await cache.set("analysis:abc", "value3")

    count = await cache.clear_pattern("article:*")

    assert count == 2
    assert await cache.get("article:abc") is None
    assert await cache.get("article:def") is None
    assert await cache.get("analysis:abc") == "value3"


def test_cache_keys_article():
    """Test article cache key generation."""
    key1 = CacheKeys.article("https://example.com/article1")
    key2 = CacheKeys.article("https://example.com/article2")
    key3 = CacheKeys.article("https://example.com/article1")

    assert key1.startswith("article:")
    assert key1 != key2  # Different URLs produce different keys
    assert key1 == key3  # Same URL produces same key


def test_cache_keys_analysis():
    """Test analysis cache key generation."""
    key1 = CacheKeys.analysis("https://example.com/article", "groq")
    key2 = CacheKeys.analysis("https://example.com/article", "claude")
    key3 = CacheKeys.analysis("https://example.com/other", "groq")

    assert key1.startswith("analysis:groq:")
    assert key2.startswith("analysis:claude:")
    assert key1 != key2  # Different providers produce different keys
    assert key1 != key3  # Different URLs produce different keys


def test_cache_keys_search():
    """Test search cache key generation."""
    # Order shouldn't matter
    key1 = CacheKeys.search(["politics", "economy"], "newsapi")
    key2 = CacheKeys.search(["economy", "politics"], "newsapi")
    key3 = CacheKeys.search(["politics", "economy"], "gnews")

    assert key1 == key2  # Same keywords in different order = same key
    assert key1 != key3  # Different sources = different keys
