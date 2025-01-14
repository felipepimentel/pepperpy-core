# Storage Module

The PepperPy Core Storage module provides a unified interface for storage operations, supporting different backends such as file system, memory, and cloud storage.

## Basic Usage

```python
from pepperpy.storage import Storage

# Create storage instance
storage = Storage()

# Store data
await storage.put("key", "value")

# Retrieve data
value = await storage.get("key")

# Delete data
await storage.delete("key")
```

## Storage Types

### File System Storage

```python
from pepperpy.storage import FileStorage

storage = FileStorage(base_path="/data")

# Store file
await storage.put("config.json", json_data)

# Read file
content = await storage.get("config.json")
```

### Memory Storage

```python
from pepperpy.storage import MemoryStorage

storage = MemoryStorage()

# Store in memory
await storage.put("user", {"name": "John"})

# Check existence
exists = await storage.exists("user")

# Read from memory
user = await storage.get("user")
print(f"Content: {content}")
```

## Advanced Features

### Memory Cache

```python
from pepperpy.storage import CachedStorage

# Create cached storage
storage = CachedStorage(
    backend=FileStorage("/data"),
    cache_size=1000
)

# Store with caching
await storage.put("user", {"name": "John"})

# Read from cache
user = await storage.get("user")
print(f"User: {user['name']}")
```

## Advanced Features

### Compressed Storage

```python
from pepperpy.storage import CompressedStorage

# Create compressed storage
storage = CompressedStorage(
    backend=FileStorage("/data")
)

# Compress content
await storage.put(
    "data.txt",
    large_content,
    compression_level=9
)

# Auto-decompression on read
content = await storage.get("data.txt")
```

### Encrypted Storage

```python
from pepperpy.storage import EncryptedStorage

# Create encrypted storage
storage = EncryptedStorage(
    backend=FileStorage("/data"),
    key="secret-key"
)

# Encrypt content
await storage.put(
    "sensitive.dat",
    secret_data
)

# Auto-decryption on read
data = await storage.get("sensitive.dat")
```

## Best Practices

1. **Data Validation**
   - Validate extensions
   - Check file sizes
   - Verify data types

2. **Error Handling**
   - Handle I/O errors
   - Manage timeouts
   - Retry operations

3. **Performance**
   - Use caching
   - Compress large data
   - Batch operations

4. **Security**
   - Encrypt sensitive data
   - Validate permissions
   - Sanitize paths

5. **Maintenance**
   - Monitor space
   - Clean old data
   - Backup regularly

## Common Patterns

### Retry Pattern

```python
from pepperpy.storage import RetryStorage

storage = RetryStorage(
    backend=FileStorage("/data"),
    max_retries=3,
    delay=1.0
)

try:
    await storage.put("key", "value")
except StorageError as e:
    print(
        f"Failed after {retries} attempts: {last_error}"
    )
```

### Storage with Metrics

```python
from pepperpy.storage import MetricsStorage

storage = MetricsStorage(
    backend=FileStorage("/data")
)

# Operations are automatically measured
await storage.put("key", "value")

# Get metrics
metrics = storage.get_metrics()
print(metrics.operations_count)
print(metrics.total_bytes)
print(metrics.average_latency)
```

### Composite Storage

```python
from pepperpy.storage import CompositeStorage

storage = CompositeStorage([
    MemoryStorage(),  # Fast cache
    FileStorage("/data"),  # Persistent
    S3Storage("bucket")  # Backup
])

# Write to all storages
await storage.put("key", "value")

# Read from first available
value = await storage.get("key")
```

## API Reference

### Base Storage

```python
class Storage:
    async def get(self, key: str) -> Any:
        """Get value by key."""
        
    async def put(
        self,
        key: str,
        value: Any,
        **options
    ) -> None:
        """Store value by key."""
        
    async def delete(self, key: str) -> None:
        """Delete value by key."""
        
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        
    async def list(
        self,
        prefix: str = ""
    ) -> List[str]:
        """List keys with prefix."""
```

### Storage Options

```python
class StorageOptions:
    compression: bool = False
    encryption: bool = False
    cache: bool = False
    retry: bool = False
    timeout: float = 30.0
    max_size: int = None
```

## Events

The storage module emits the following events:

- `storage.put` - When data is stored
- `storage.get` - When data is retrieved  
- `storage.delete` - When data is deleted
- `storage.error` - When an error occurs

## Error Handling

```python
try:
    await storage.get("key")
except StorageError as e:
    logger.error(f"Storage error: {e}")
except StorageNotFoundError as e:
    logger.warning(f"Key not found: {e}")
except StorageTimeoutError as e:
    logger.error(f"Operation timeout: {e}")
```

## Configuration

```yaml
storage:
  type: file
  path: /data
  options:
    compression: true
    encryption: false
    cache:
      enabled: true
      size: 1000
    retry:
      max: 3
      delay: 1.0
```

## Testing

```python
from pepperpy.testing import MockStorage

# Create mock storage
storage = MockStorage()

# Configure mock
storage.mock_get("key", "value")

# Test code
result = await storage.get("key")
assert result == "value"
``` 