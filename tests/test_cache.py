"""Test cache module."""

from typing import AsyncGenerator

import pytest

from pepperpy.cache import Cache, CacheConfig


@pytest.fixture
async def cache() -> AsyncGenerator[Cache[str], None]:
    """Get cache."""
    cache = Cache[str](CacheConfig(name="test"))
    await cache.initialize()
    yield cache
    await cache._teardown()


@pytest.mark.asyncio
async def test_cache_get_not_found(cache: Cache[str]) -> None:
    """Test cache get not found."""
    value = await cache.get("test")
    assert value is None


@pytest.mark.asyncio
async def test_cache_get_with_default(cache: Cache[str]) -> None:
    """Test cache get with default."""
    value = await cache.get("test", "default")
    assert value == "default"


@pytest.mark.asyncio
async def test_cache_set(cache: Cache[str]) -> None:
    """Test cache set."""
    await cache.set("test", "value")
    value = await cache.get("test")
    assert value == "value"


@pytest.mark.asyncio
async def test_cache_delete(cache: Cache[str]) -> None:
    """Test cache delete."""
    await cache.set("test", "value")
    await cache.delete("test")
    value = await cache.get("test")
    assert value is None


@pytest.mark.asyncio
async def test_cache_clear(cache: Cache[str]) -> None:
    """Test cache clear."""
    await cache.set("test1", "value1")
    await cache.set("test2", "value2")
    await cache.clear()
    value1 = await cache.get("test1")
    value2 = await cache.get("test2")
    assert value1 is None
    assert value2 is None


@pytest.mark.asyncio
async def test_cache_max_size(cache: Cache[str]) -> None:
    """Test cache max size."""
    cache = Cache[str](CacheConfig(name="test", max_size=2))
    await cache.initialize()
    await cache.set("test1", "value1")
    await cache.set("test2", "value2")
    await cache.set("test3", "value3")
    value1 = await cache.get("test1")
    value2 = await cache.get("test2")
    value3 = await cache.get("test3")
    assert value1 is None
    assert value2 is not None
    assert value3 is not None


@pytest.mark.asyncio
async def test_cache_get_stats(cache: Cache[str]) -> None:
    """Test cache get stats."""
    await cache.set("test1", "value1")
    await cache.set("test2", "value2")
    stats = await cache.get_stats()
    assert stats["name"] == "test"
    assert stats["size"] == 2
    assert stats["max_size"] == 1000
    assert stats["ttl"] == 60.0
