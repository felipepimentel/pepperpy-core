"""Cache implementation."""

from dataclasses import dataclass, field
from typing import Any

from .module import BaseModule, ModuleConfig


@dataclass
class CacheConfig(ModuleConfig):
    """Cache configuration."""
    
    name: str
    max_size: int = 1000
    ttl: float = 60.0  # Time to live in seconds
    metadata: dict[str, Any] = field(default_factory=dict)


class Cache(BaseModule[CacheConfig]):
    """Simple in-memory cache implementation."""
    
    def __init__(self, config: CacheConfig | None = None) -> None:
        """Initialize cache.
        
        Args:
            config: Cache configuration
        """
        super().__init__(config or CacheConfig(name="cache"))
        self._cache: dict[str, Any] = {}
        
    async def _setup(self) -> None:
        """Setup cache."""
        self._cache.clear()
        
    async def _teardown(self) -> None:
        """Cleanup cache."""
        self._cache.clear()
        
    async def get(self, key: str) -> Any:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if found, None otherwise
        """
        if not self.is_initialized:
            await self.initialize()
        return self._cache.get(key)
        
    async def set(self, key: str, value: Any) -> None:
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        if not self.is_initialized:
            await self.initialize()
            
        # Enforce max size
        if len(self._cache) >= self.config.max_size:
            # Simple LRU: remove oldest item
            if self._cache:
                self._cache.pop(next(iter(self._cache)))
                
        self._cache[key] = value
        
    async def delete(self, key: str) -> None:
        """Delete value from cache.
        
        Args:
            key: Cache key
        """
        if not self.is_initialized:
            await self.initialize()
        self._cache.pop(key, None)
        
    async def clear(self) -> None:
        """Clear all values from cache."""
        if not self.is_initialized:
            await self.initialize()
        self._cache.clear()
        
    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Cache statistics
        """
        if not self.is_initialized:
            await self.initialize()
        return {
            "size": len(self._cache),
            "max_size": self.config.max_size,
            "ttl": self.config.ttl,
        }


__all__ = [
    "Cache",
    "CacheConfig",
] 