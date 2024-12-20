"""Cache tests."""

from collections.abc import AsyncGenerator

import pytest
from pepperpy_core.cache import BaseCache, CacheConfig


@pytest.fixture
def cache_config() -> CacheConfig:
    """Create test cache config."""
    return CacheConfig(
        name="test_cache",
        ttl=60,
        max_size=100,
    )


@pytest.fixture
async def cache(
    cache_config: CacheConfig,
) -> AsyncGenerator[BaseCache[CacheConfig], None]:
    """Create test cache."""
    cache_instance = _TestCache(cache_config)
    await cache_instance.initialize()
    try:
        yield cache_instance
    finally:
        await cache_instance.cleanup()


class _TestCache(BaseCache[CacheConfig]):
    """Test cache implementation."""

    def __init__(self, config: CacheConfig) -> None:
        """Initialize cache."""
        super().__init__(config)
        self._data: dict[str, str] = {}

    async def _setup(self) -> None:
        """Setup cache resources."""
        self._data = {}

    async def _teardown(self) -> None:
        """Teardown cache resources."""
        self._data.clear()

    async def get(self, key: str) -> str | None:
        """Get value from cache."""
        return self._data.get(key)

    async def set(self, key: str, value: str) -> None:
        """Set value in cache."""
        self._data[key] = value

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        self._data.pop(key, None)

    async def clear(self) -> None:
        """Clear all values from cache."""
        self._data.clear()


@pytest.mark.asyncio
async def test_cache_operations(
    cache: AsyncGenerator[BaseCache[CacheConfig], None]
) -> None:
    """Test basic cache operations."""
    cache_instance = await anext(cache)

    # Test set
    await cache_instance.set("test", "value")

    # Test get
    result = await cache_instance.get("test")
    assert result == "value"

    # Test delete
    await cache_instance.delete("test")
    result = await cache_instance.get("test")
    assert result is None
