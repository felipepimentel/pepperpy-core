"""Test cache module."""

import asyncio
from datetime import datetime, timedelta

import pytest

from pepperpy.cache import Cache, CacheEntry, JsonDict, MemoryCache, MemoryCacheConfig


@pytest.fixture
def cache_config() -> MemoryCacheConfig:
    """Create cache config fixture."""
    return MemoryCacheConfig(
        name="test_cache",
        max_size=100,
        metadata={"test": True},
    )


@pytest.fixture
async def cache(cache_config: MemoryCacheConfig) -> Cache:
    """Create cache fixture."""
    cache = MemoryCache(config=cache_config)
    await cache.initialize()
    yield cache
    await cache.teardown()


@pytest.mark.asyncio
async def test_cache_config_init() -> None:
    """Test cache config initialization."""
    config = MemoryCacheConfig(
        name="test_cache",
        max_size=100,
        metadata={"test": True},
    )
    assert config.name == "test_cache"
    assert config.max_size == 100
    assert config.metadata == {"test": True}


@pytest.mark.asyncio
async def test_cache_init(cache_config: MemoryCacheConfig) -> None:
    """Test cache initialization."""
    cache = MemoryCache(config=cache_config)
    await cache.initialize()
    assert cache.config == cache_config
    await cache.teardown()


@pytest.mark.asyncio
async def test_cache_set_get(cache: Cache) -> None:
    """Test cache set and get."""
    metadata: JsonDict = {"test": True}
    entry = await cache.set("key", "value", metadata=metadata)
    assert isinstance(entry, CacheEntry)
    assert entry.key == "key"
    assert entry.value == "value"
    assert entry.metadata == metadata

    result = await cache.get("key")
    assert result is not None
    assert result.key == "key"
    assert result.value == "value"
    assert result.metadata == metadata


@pytest.mark.asyncio
async def test_cache_get_value(cache: Cache) -> None:
    """Test cache get_value."""
    await cache.set("key", "value")
    value = await cache.get_value("key")
    assert value == "value"

    value = await cache.get_value("missing")
    assert value is None


@pytest.mark.asyncio
async def test_cache_expiration(cache: Cache) -> None:
    """Test cache expiration."""
    expires_at = datetime.now() + timedelta(seconds=1)
    entry = await cache.set("key", "value", expires_at=expires_at)
    assert not entry.is_expired()

    result = await cache.get("key")
    assert result is not None
    assert result.value == "value"

    await asyncio.sleep(1.1)  # Wait for expiration
    result = await cache.get("key")
    assert result is None


@pytest.mark.asyncio
async def test_cache_delete(cache: Cache) -> None:
    """Test cache delete."""
    await cache.set("key", "value")
    result = await cache.get("key")
    assert result is not None

    await cache.delete("key")
    result = await cache.get("key")
    assert result is None


@pytest.mark.asyncio
async def test_cache_clear(cache: Cache) -> None:
    """Test cache clear."""
    await cache.set("key1", "value1")
    await cache.set("key2", "value2")

    await cache.clear()
    assert await cache.get("key1") is None
    assert await cache.get("key2") is None


@pytest.mark.asyncio
async def test_cache_cleanup_expired(cache: Cache) -> None:
    """Test cache cleanup of expired entries."""
    expires_at = datetime.now() + timedelta(seconds=1)
    await cache.set("key1", "value1", expires_at=expires_at)
    await cache.set("key2", "value2")  # No expiration

    await asyncio.sleep(1.1)  # Wait for expiration
    result = await cache.get("key1")
    assert result is None  # Expired entry should be cleaned up

    result = await cache.get("key2")
    assert result is not None  # Non-expired entry should remain
    assert result.value == "value2"
