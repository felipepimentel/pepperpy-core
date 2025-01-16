"""Cache module."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

JsonDict = Dict[str, Any]


@dataclass
class CacheEntry:
    """Cache entry."""

    value: Any
    expires_at: Optional[datetime] = None
    metadata: Optional[JsonDict] = None


@dataclass
class CacheConfig:
    """Cache configuration."""

    ttl: Optional[int] = None
    max_size: Optional[int] = None


class Cache(ABC):
    """Cache interface."""

    @abstractmethod
    def get(self, key: str) -> Optional[CacheEntry]:
        """Get value from cache.

        Args:
            key: Cache key.

        Returns:
            Cache entry or None if not found.
        """
        ...

    @abstractmethod
    def set(
        self,
        key: str,
        value: Any,
        expires_at: Optional[datetime] = None,
        metadata: Optional[JsonDict] = None,
    ) -> CacheEntry:
        """Set value in cache.

        Args:
            key: Cache key.
            value: Value to cache.
            expires_at: Expiration time.
            metadata: Additional metadata.

        Returns:
            Cache entry.
        """
        ...

    @abstractmethod
    def delete(self, key: str) -> Optional[CacheEntry]:
        """Delete value from cache.

        Args:
            key: Cache key.

        Returns:
            Deleted cache entry or None if not found.
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear cache."""
        ...


class MemoryCache(Cache):
    """Memory cache implementation."""

    def __init__(self, config: Optional[CacheConfig] = None) -> None:
        """Initialize memory cache.

        Args:
            config: Cache configuration.
        """
        self.config = config or CacheConfig()
        self._cache: Dict[str, CacheEntry] = {}

    def get(self, key: str) -> Optional[CacheEntry]:
        """Get value from cache.

        Args:
            key: Cache key.

        Returns:
            Cache entry or None if not found.
        """
        entry = self._cache.get(key)
        if entry is None:
            return None

        if entry.expires_at and entry.expires_at <= datetime.now():
            del self._cache[key]
            return None

        return entry

    def set(
        self,
        key: str,
        value: Any,
        expires_at: Optional[datetime] = None,
        metadata: Optional[JsonDict] = None,
    ) -> CacheEntry:
        """Set value in cache.

        Args:
            key: Cache key.
            value: Value to cache.
            expires_at: Expiration time.
            metadata: Additional metadata.

        Returns:
            Cache entry.
        """
        if self.config.max_size and len(self._cache) >= self.config.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        if self.config.ttl and not expires_at:
            expires_at = datetime.now() + timedelta(seconds=self.config.ttl)

        entry = CacheEntry(value=value, expires_at=expires_at, metadata=metadata)
        self._cache[key] = entry
        return entry

    def delete(self, key: str) -> Optional[CacheEntry]:
        """Delete value from cache.

        Args:
            key: Cache key.

        Returns:
            Deleted cache entry or None if not found.
        """
        return self._cache.pop(key, None)

    def clear(self) -> None:
        """Clear cache."""
        self._cache.clear()
