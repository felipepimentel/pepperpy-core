"""Cache example."""

from typing import Any

from pepperpy_core.cache import BaseCache, CacheConfig, CacheEntry


class ExampleCache(BaseCache[CacheConfig]):
    """Example cache implementation."""

    def __init__(self) -> None:
        """Initialize cache."""
        config = CacheConfig(name="example-cache")
        super().__init__(config)
        self._data: dict[str, CacheEntry] = {}

    async def _setup(self) -> None:
        """Setup cache resources."""
        # Exemplo simples usando dicionário em memória
        self._data = {}

    async def _teardown(self) -> None:
        """Teardown cache resources."""
        self._data.clear()

    async def get(self, key: str) -> Any:
        """Get value from cache."""
        entry = self._data.get(key)
        if entry is None:
            return None
        return entry.value

    async def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        import time

        entry = CacheEntry(
            key=key, value=value, expires_at=time.time() + self.config.ttl
        )
        self._data[key] = entry

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        self._data.pop(key, None)

    async def clear(self) -> None:
        """Clear all values from cache."""
        self._data.clear()


async def main() -> None:
    """Run example."""
    # Create cache instance
    cache = ExampleCache()

    # Initialize cache
    await cache.initialize()

    try:
        # Set some values
        await cache.set("key1", "value1")
        await cache.set("key2", {"nested": "value2"})

        # Get values
        value1 = await cache.get("key1")
        value2 = await cache.get("key2")

        print(f"Value1: {value1}")
        print(f"Value2: {value2}")

        # Delete a value
        await cache.delete("key1")
        value1 = await cache.get("key1")
        print(f"Value1 after delete: {value1}")

        # Clear cache
        await cache.clear()
        value2 = await cache.get("key2")
        print(f"Value2 after clear: {value2}")

    finally:
        await cache.cleanup()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
