# IO Module

The PepperPy Core IO module provides an asynchronous interface for input and output operations, including file reading and writing, streams, and buffers.

## Core Components

### AsyncFile

Class for asynchronous file operations:

```python
from pepperpy_core.io import AsyncFile

async with AsyncFile("data.txt", "r") as f:
    # Read content
    content = await f.read()
    
    # Process content
    result = process_data(content)
```

### AsyncBuffer

Buffer for asynchronous operations:

```python
from pepperpy_core.io import AsyncBuffer

buffer = AsyncBuffer()

# Write data
await buffer.write(b"Hello ")
await buffer.write(b"World!")

# Read data
data = await buffer.read()
```

### AsyncStream

Stream for asynchronous operations:

```python
from pepperpy_core.io import AsyncStream

async with AsyncStream() as stream:
    # Write data
    await stream.write("data")
    
    # Seek to start
    await stream.seek(0)
    
    # Read data
    content = await stream.read()
    print(f"Content: {content}")
```

### AsyncWriter

```python
from pepperpy_core.io import AsyncWriter

writer = AsyncWriter("output.txt")

# Write data
await writer.write("line 1\n")
await writer.write("line 2\n")

# Force flush
await writer.flush()
```

## Advanced Features

### Compressed Buffer

```python
from pepperpy_core.io import CompressedBuffer

buffer = CompressedBuffer()

# Write data
await buffer.write(large_data)

# Get compressed data
compressed = await buffer.get_compressed()

# Get original data
original = await buffer.get_decompressed()
```

### Stream with Transformation

```python
from pepperpy_core.io import TransformStream

class UpperStream(TransformStream):
    async def transform(self, data: str) -> str:
        return data.upper()

stream = UpperStream()
await stream.write("hello")
result = await stream.read()  # "HELLO"
```

## Best Practices

1. **Resource Management**
   - Use context managers
   - Close resources properly
   - Handle errors gracefully
   - Clean up properly

2. **Memory Management**
   - Manage memory usage
   - Use streaming for large files
   - Implement chunking
   - Monitor usage

3. **Performance**
   - Optimize operations
   - Use buffering
   - Implement batching
   - Monitor throughput

4. **Caching**
   - Cache when possible
   - Monitor memory usage
   - Implement eviction
   - Use appropriate sizes

5. **Security**
   - Validate paths
   - Handle permissions
   - Sanitize inputs
   - Secure sensitive data

## Common Patterns

### File Processing

```python
from pepperpy_core.io import AsyncFile, ChunkProcessor

class FileProcessor:
    def __init__(self, chunk_size: int = 8192):
        self.chunk_size = chunk_size
    
    async def process_file(self, path: str):
        async with AsyncFile(path, "rb") as f:
            processor = ChunkProcessor(
                chunk_size=self.chunk_size
            )
            
            while True:
                chunk = await f.read(
                    self.chunk_size
                )
                if not chunk:
                    break
                    
                await processor.process(chunk)
```

### Stream Pipeline

```python
from pepperpy_core.io import StreamPipeline

class DataPipeline(StreamPipeline):
    async def process(self, data: bytes) -> bytes:
        # Decompress
        decompressed = await self.decompress(data)
        
        # Transform
        transformed = await self.transform(
            decompressed
        )
        
        # Compress
        return await self.compress(transformed)
```

### Buffered Writer

```python
from pepperpy_core.io import BufferedWriter

class LogWriter(BufferedWriter):
    def __init__(
        self,
        path: str,
        buffer_size: int = 8192
    ):
        super().__init__(
            path,
            buffer_size=buffer_size
        )
    
    async def write_log(self, message: str):
        # Format message
        formatted = self.format_message(message)
        
        # Write to buffer
        await self.write(formatted)
        
        # Flush if needed
        if self.should_flush():
            await self.flush()
```

## API Reference

### AsyncFile

```python
class AsyncFile:
    async def read(
        self,
        size: int = -1
    ) -> bytes:
        """Read from file."""
        
    async def write(
        self,
        data: bytes
    ) -> int:
        """Write to file."""
        
    async def seek(
        self,
        offset: int,
        whence: int = 0
    ) -> int:
        """Seek in file."""
```

### AsyncBuffer

```python
class AsyncBuffer:
    async def read(
        self,
        size: int = -1
    ) -> bytes:
        """Read from buffer."""
        
    async def write(
        self,
        data: bytes
    ) -> int:
        """Write to buffer."""
        
    def clear(self):
        """Clear buffer."""
```

### AsyncStream

```python
class AsyncStream:
    async def read(
        self,
        size: int = -1
    ) -> bytes:
        """Read from stream."""
        
    async def write(
        self,
        data: bytes
    ) -> int:
        """Write to stream."""
        
    async def close(self):
        """Close stream."""
```
``` 