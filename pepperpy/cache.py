"""Cache module for PepperPy.

This module provides a flexible caching system with support for:
- Async operations
- Expiration times
- Metadata storage
- Type-safe interfaces
- Memory-based implementation
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, TypedDict

from .core import PepperpyError
from .module import BaseModule, ModuleConfig


class CacheError(PepperpyError):
    """Cache-related errors."""

    pass


class JsonDict(TypedDict, total=False):
    """JSON dictionary type for cache metadata."""

    str_value: str | None
    int_value: int | None
    float_value: float | None
    bool_value: bool | None
    dict_value: dict | None
    list_value: list | None


class CacheEntry:
    """Cache entry with metadata and expiration support."""

    def __init__(
        self,
        key: str,
        value: Any,
        expires_at: datetime | None = None,
        metadata: JsonDict | None = None,
    ) -> None:
        """Initialize cache entry.

        Args:
            key: Cache key
            value: Cache value
            expires_at: Optional expiration time
            metadata: Optional metadata
        """
        self.key = key
        self.value = value
        self.expires_at = expires_at
        self.metadata = metadata or {}

    def is_expired(self) -> bool:
        """Check if entry is expired.

        Returns:
            bool: True if expired, False otherwise
        """
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


class Cache(ABC):
    """Abstract base class for cache implementations."""

    @abstractmethod
    async def get(self, key: str) -> CacheEntry | None:
        """Get cache entry.

        Args:
            key: Cache key

        Returns:
            CacheEntry if found and not expired, None otherwise

        Raises:
            CacheError: If operation fails
        """
        raise NotImplementedError

    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        expires_at: datetime | None = None,
        metadata: JsonDict | None = None,
    ) -> CacheEntry:
        """Set cache entry.

        Args:
            key: Cache key
            value: Cache value
            expires_at: Optional expiration time
            metadata: Optional metadata

        Returns:
            Created cache entry

        Raises:
            CacheError: If operation fails
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete cache entry.

        Args:
            key: Cache key

        Raises:
            CacheError: If operation fails
        """
        raise NotImplementedError

    @abstractmethod
    async def clear(self) -> None:
        """Clear all cache entries.

        Raises:
            CacheError: If operation fails
        """
        raise NotImplementedError

    async def get_value(self, key: str) -> Any | None:
        """Get cache value directly.

        Args:
            key: Cache key

        Returns:
            Cached value if found and not expired, None otherwise

        Raises:
            CacheError: If operation fails
        """
        entry = await self.get(key)
        if entry is None or entry.is_expired():
            return None
        return entry.value


class MemoryCacheConfig(ModuleConfig):
    """Memory cache configuration."""

    def __init__(
        self,
        name: str = "memory_cache",
        max_size: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize memory cache configuration.

        Args:
            name: Cache name
            max_size: Optional maximum number of entries
            metadata: Optional metadata
        """
        super().__init__(name=name, metadata=metadata or {})
        self.max_size = max_size


class MemoryCache(BaseModule[MemoryCacheConfig], Cache):
    """Memory-based cache implementation.

    This implementation stores cache entries in memory using a dictionary.
    It supports:
    - Expiration times
    - Maximum size limits
    - Metadata storage
    - Automatic cleanup of expired entries
    """

    def __init__(self, config: MemoryCacheConfig | None = None) -> None:
        """Initialize memory cache.

        Args:
            config: Optional cache configuration
        """
        super().__init__(config or MemoryCacheConfig())
        self._cache: Dict[str, CacheEntry] = {}

    async def _setup(self) -> None:
        """Set up cache."""
        self._cache.clear()

    async def _teardown(self) -> None:
        """Clean up cache."""
        self._cache.clear()

    def _cleanup_expired(self) -> None:
        """Remove expired entries."""
        now = datetime.now()
        expired = [
            key
            for key, entry in self._cache.items()
            if entry.expires_at and entry.expires_at <= now
        ]
        for key in expired:
            del self._cache[key]

    async def get(self, key: str) -> CacheEntry | None:
        """Get cache entry.

        Args:
            key: Cache key

        Returns:
            CacheEntry if found and not expired, None otherwise

        Raises:
            CacheError: If cache is not initialized
        """
        self._ensure_initialized()
        self._cleanup_expired()

        entry = self._cache.get(key)
        if entry is None:
            return None

        if entry.is_expired():
            await self.delete(key)
            return None

        return entry

    async def set(
        self,
        key: str,
        value: Any,
        expires_at: datetime | None = None,
        metadata: JsonDict | None = None,
    ) -> CacheEntry:
        """Set cache entry.

        Args:
            key: Cache key
            value: Cache value
            expires_at: Optional expiration time
            metadata: Optional metadata

        Returns:
            Created cache entry

        Raises:
            CacheError: If cache is not initialized or max size is reached
        """
        self._ensure_initialized()
        self._cleanup_expired()

        if (
            self.config.max_size
            and len(self._cache) >= self.config.max_size
            and key not in self._cache
        ):
            raise CacheError("Cache max size reached")

        entry = CacheEntry(key, value, expires_at, metadata)
        self._cache[key] = entry
        return entry

    async def delete(self, key: str) -> None:
        """Delete cache entry.

        Args:
            key: Cache key

        Raises:
            CacheError: If cache is not initialized
        """
        self._ensure_initialized()
        self._cache.pop(key, None)

    async def clear(self) -> None:
        """Clear all cache entries.

        Raises:
            CacheError: If cache is not initialized
        """
        self._ensure_initialized()
        self._cache.clear()

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary containing cache statistics

        Raises:
            CacheError: If cache is not initialized
        """
        self._ensure_initialized()
        self._cleanup_expired()

        return {
            "size": len(self._cache),
            "max_size": self.config.max_size,
            "metadata": self.config.metadata,
        }
