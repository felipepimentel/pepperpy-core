"""Cache module."""

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from .module import BaseModule, ModuleConfig


@dataclass
class CacheConfig(ModuleConfig):
    """Cache configuration."""

    name: str
    max_size: int = 1000
    ttl: float = 60.0  # seconds
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Post initialization validation."""
        self.validate()

    def validate(self) -> None:
        """Validate configuration."""
        if self.max_size <= 0:
            raise ValueError("max_size must be positive")
        if self.ttl <= 0:
            raise ValueError("ttl must be positive")


T = TypeVar("T")


class Cache(BaseModule[CacheConfig], Generic[T]):
    """Cache implementation."""

    def __init__(self, config: CacheConfig | None = None) -> None:
        """Initialize cache.

        Args:
            config: Cache configuration
        """
        if config is None:
            config = CacheConfig(name="cache")
        super().__init__(config)
        self._cache: dict[str, T] = {}

    async def _setup(self) -> None:
        """Setup cache."""
        self._cache.clear()

    async def _teardown(self) -> None:
        """Teardown cache."""
        self._cache.clear()
        self._is_initialized = False

    async def get(self, key: str, default: T | None = None) -> T | None:
        """Get value from cache.

        Args:
            key: Cache key
            default: Default value if key not found

        Returns:
            Cached value or default if not found

        Raises:
            CacheError: If cache is not initialized
        """
        self._ensure_initialized()
        return self._cache.get(key, default)

    async def set(self, key: str, value: T) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache

        Raises:
            CacheError: If cache is not initialized
        """
        self._ensure_initialized()

        if len(self._cache) >= self.config.max_size:
            # Simple LRU: remove first item
            if self._cache:
                del self._cache[next(iter(self._cache))]

        self._cache[key] = value

    async def delete(self, key: str) -> None:
        """Delete value from cache.

        Args:
            key: Cache key

        Raises:
            CacheError: If cache is not initialized
        """
        self._ensure_initialized()
        self._cache.pop(key, None)

    async def clear(self) -> None:
        """Clear cache.

        Raises:
            CacheError: If cache is not initialized
        """
        self._ensure_initialized()
        self._cache.clear()

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Cache statistics

        Raises:
            CacheError: If cache is not initialized
        """
        self._ensure_initialized()
        return {
            "name": self.config.name,
            "size": len(self._cache),
            "max_size": self.config.max_size,
            "ttl": self.config.ttl,
        }


__all__ = [
    "CacheConfig",
    "Cache",
]
