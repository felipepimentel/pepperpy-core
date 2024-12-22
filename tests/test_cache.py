"""Tests for the cache module."""

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio

from pepperpy_core.cache import Cache, CacheConfig
from pepperpy_core.module import ModuleError


@pytest_asyncio.fixture
async def cache() -> AsyncIterator[Cache[str]]:
    """Create a test cache."""
    cache = Cache[str]()
    await cache.initialize()
    yield cache
    await cache.teardown()


@pytest.mark.asyncio
async def test_cache_operations(cache: Cache[str]) -> None:
    """Test basic cache operations."""
    # Set and get
    await cache.set("key1", "value1")
    assert await cache.get("key1") == "value1"

    # Get non-existent key
    assert await cache.get("missing") is None
    assert await cache.get("missing", "default") == "default"

    # Delete
    await cache.delete("key1")
    assert await cache.get("key1") is None

    # Clear
    await cache.set("key1", "value1")
    await cache.set("key2", "value2")
    await cache.clear()
    assert await cache.get("key1") is None
    assert await cache.get("key2") is None


@pytest.mark.asyncio
async def test_cache_max_size() -> None:
    """Test cache max size limit."""
    config = CacheConfig(name="test_cache", max_size=2)
    cache = Cache[str](config)
    await cache.initialize()

    await cache.set("key1", "value1")
    await cache.set("key2", "value2")
    await cache.set("key3", "value3")  # Should evict key1

    assert await cache.get("key1") is None
    assert await cache.get("key2") == "value2"
    assert await cache.get("key3") == "value3"

    await cache.teardown()


@pytest.mark.asyncio
async def test_cache_config_validation() -> None:
    """Test cache configuration validation."""
    with pytest.raises(ValueError, match="max_size must be positive"):
        CacheConfig(name="test_cache", max_size=0)

    with pytest.raises(ValueError, match="ttl must be positive"):
        CacheConfig(name="test_cache", ttl=0)


@pytest.mark.asyncio
async def test_cache_uninitialized_operations() -> None:
    """Test cache operations when uninitialized."""
    cache = Cache[str]()

    with pytest.raises(ModuleError):
        await cache.set("key1", "value1")

    with pytest.raises(ModuleError):
        await cache.get("key1")

    with pytest.raises(ModuleError):
        await cache.delete("key1")

    with pytest.raises(ModuleError):
        await cache.clear()

    with pytest.raises(ModuleError):
        await cache.get_stats()


@pytest.mark.asyncio
async def test_cache_reinitialization(cache: Cache[str]) -> None:
    """Test cache reinitialization."""
    await cache.set("key1", "value1")
    await cache.teardown()
    assert not cache.is_initialized

    await cache.initialize()
    assert cache.is_initialized
    assert (
        await cache.get("key1") is None
    )  # Cache should be empty after reinitialization


@pytest.mark.asyncio
async def test_cache_stats(cache: Cache[str]) -> None:
    """Test cache statistics."""
    stats = await cache.get_stats()
    assert stats["name"] == "cache"
    assert stats["size"] == 0
    assert stats["max_size"] == 1000
    assert stats["ttl"] == 60.0

    await cache.set("key1", "value1")
    await cache.set("key2", "value2")

    stats = await cache.get_stats()
    assert stats["size"] == 2
