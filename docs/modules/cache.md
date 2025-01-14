# Cache Module

The PepperPy Core Cache module provides a generic in-memory cache implementation with support for TTL (Time To Live) and size limits.

## Core Components

### Cache Configuration

```python
from pepperpy.cache import Cache, CacheConfig

# Create cache
cache = Cache()

# Configure cache
config = CacheConfig(
    max_size=1000,  # Maximum number of items
    ttl=300,        # Time to live in seconds
    cleanup_interval=60  # Cleanup interval in seconds
)

cache.configure(config)
```

## Usage Examples

### Basic Cache

```python
from pepperpy.cache import Cache

# Create cache
cache = Cache()

# Store data
await cache.set("user:123", {
    "id": "123",
    "name": "John"
})

# Get data
cached_user = await cache.get("user:123")
print(f"User: {cached_user['name']}")
```

### Cache with Generic Types

```python
from pepperpy.cache import Cache
from typing import TypeVar, Generic

T = TypeVar("T")

class TypedCache(Cache, Generic[T]):
    async def get(self, key: str) -> T:
        return await super().get(key)
    
    async def set(self, key: str, value: T):
        await super().set(key, value)
```

## Advanced Features

### Cache with Statistics

```python
from pepperpy.cache import StatsCache

class MonitoredCache(StatsCache):
    def __init__(self):
        super().__init__()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
    
    async def get(self, key: str) -> Any:
        try:
            value = await super().get(key)
            self.stats["hits"] += 1
            return value
        except KeyError:
            self.stats["misses"] += 1
            raise
    
    def evict(self, key: str):
        super().evict(key)
        self.stats["evictions"] += 1
    
    def get_stats(self) -> dict:
        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_ratio": self._calculate_hit_ratio(),
            "evictions": self.stats["evictions"],
            "size": len(self),
            "memory": self.memory_usage()
        }
```

## Best Practices

1. **Configuration**
   - Set appropriate maximum size
   - Configure TTL wisely
   - Document settings
   - Monitor usage

2. **Memory Usage**
   - Monitor memory usage
   - Implement periodic cleanup
   - Set size limits
   - Use eviction policies

3. **Performance**
   - Use appropriate data structures
   - Implement efficient lookups
   - Cache hot data
   - Monitor hit rates

4. **Maintenance**
   - Monitor statistics
   - Track usage patterns
   - Perform periodic cleanup
   - Update configurations

5. **Type Safety**
   - Use generic types
   - Validate data types
   - Maintain consistency
   - Handle type errors

## Common Patterns

### Cache with Expiration

```python
from pepperpy.cache import ExpiringCache

class TimedCache(ExpiringCache):
    def __init__(self, ttl: int = 300):
        super().__init__()
        self.ttl = ttl
    
    async def get(self, key: str) -> Any:
        # Check expiration
        if self.is_expired(key):
            self.evict(key)
            raise KeyError(key)
        
        return await super().get(key)
    
    async def set(self, key: str, value: Any):
        await super().set(key, value)
        self.set_expiration(key, self.ttl)
```

### Cache with Fallback

```python
from pepperpy.cache import Cache

class FallbackCache(Cache):
    def __init__(self, fallback: callable):
        super().__init__()
        self.fallback = fallback
    
    async def get(self, key: str) -> Any:
        try:
            return await super().get(key)
        except KeyError:
            # Get from fallback
            value = await self.fallback(key)
            
            # Cache value
            await self.set(key, value)
            
            return value
```

### Cache with Validation

```python
from pepperpy.cache import Cache

class ValidatedCache(Cache):
    def __init__(self, validator: callable):
        super().__init__()
        self.validator = validator
    
    async def set(self, key: str, value: Any):
        # Validate value
        if not self.validator(value):
            raise ValueError("Invalid value")
        
        await super().set(key, value)
```

## API Reference

### Base Cache

```python
class Cache:
    async def get(self, key: str) -> Any:
        """Get value by key."""
        
    async def set(self, key: str, value: Any):
        """Set value by key."""
        
    async def delete(self, key: str):
        """Delete value by key."""
        
    def clear(self):
        """Clear all values."""
```

### Cache Options

```python
class CacheOptions:
    max_size: int = None
    ttl: int = None
    cleanup_interval: int = 60
    eviction_policy: str = "lru"
    validate: bool = False
```

### Cache Events

The cache module emits the following events:

- `cache.hit` - When a cache hit occurs
- `cache.miss` - When a cache miss occurs
- `cache.evict` - When an item is evicted
- `cache.error` - When an error occurs

### Error Handling

```python
try:
    value = await cache.get(key)
except KeyError:
    logger.warning(f"Cache miss: {key}")
except ValueError as e:
    logger.error(f"Invalid value: {e}")
except CacheError as e:
    logger.error(f"Cache error: {e}")
```
``` 