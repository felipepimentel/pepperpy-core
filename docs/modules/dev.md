# Development Module

The PepperPy Core Dev module provides utilities for development, including tools for logging, timing, debugging, and asynchronous testing.

## Core Components

### LogLevel

Enumeration for log levels:

```python
from pepperpy.dev import LogLevel

# Available levels
class LogLevel(Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
```

### Timer

Context manager for time measurement:

```python
from pepperpy.dev import Timer

async with Timer() as timer:
    # Operation to be measured
    await process_data()

print(f"Duration: {timer.duration}ms")
```

### AsyncTestCase

Base class for asynchronous tests:

```python
from pepperpy.dev import AsyncTestCase

class TestExample(AsyncTestCase):
    async def setUp(self):
        self.data = await load_test_data()
    
    async def test_process(self):
        result = await process_data(self.data)
        self.assertEqual(result.status, "success")
    
    async def tearDown(self):
        await cleanup_test_data()
```

### Decorators

```python
from pepperpy.dev import debug, async_debug

# Decorator for sync function
@debug
def process_data(data: dict) -> dict:
    return transform_data(data)

# Decorator for async function
@async_debug
async def process_async(data: dict) -> dict:
    return await transform_async(data)
```

### Protocol

```python
from pepperpy.dev import Protocol

class DataProcessor(Protocol):
    async def process(self, data: dict) -> dict:
        """Process data asynchronously."""
        
    def validate(self, data: dict) -> bool:
        """Validate data synchronously."""
        
    # Implement other protocol methods...
```

### Profiler

```python
from pepperpy.dev import Profiler

async with Profiler() as profiler:
    # Timer will record start and end
    await process_data()
```

## Advanced Features

### Memory Profiler

```python
from pepperpy.dev import MemoryProfiler

profiler = MemoryProfiler()

# Start tracking
profiler.start()

# Run operations
await process_large_data()

# Get memory usage
usage = profiler.get_usage()
print(f"Peak memory: {usage.peak_mb}MB")
```

### Debug Utilities

```python
from pepperpy.dev import DebugContext

async with DebugContext() as ctx:
    # Configure context
    ctx.set_log_level(LogLevel.DEBUG)
    ctx.enable_profiling()
    
    # Execute function
    await process_data()
    
    # Get debug info
    print(ctx.get_logs())
    print(ctx.get_profile())
```

## Best Practices

1. **Logging**
   - Use appropriate levels
   - Include context
   - Format messages

2. **Testing**
   - Implement all methods
   - Mock dependencies
   - Test edge cases

3. **Profiling**
   - Measure specific operations
   - Track memory usage
   - Monitor performance

4. **Debugging**
   - Log useful information
   - Use breakpoints
   - Check variables

5. **Testing**
   - Write unit tests
   - Test exceptions
   - Mock services

6. **Monitoring**
   - Monitor memory
   - Track performance
   - Log errors

## Common Patterns

### Timer with Metrics

```python
from pepperpy.dev import Timer, Metrics

class TimedOperation:
    def __init__(self):
        self.metrics = Metrics()
    
    async def execute(self, operation):
        async with Timer() as timer:
            try:
                # Execute operation
                result = await operation()
                
                # Record metrics
                self.metrics.record_success(
                    operation=operation.__name__,
                    duration=timer.duration
                )
                
                return result
            except Exception as e:
                # Record failure
                self.metrics.record_failure(
                    operation=operation.__name__,
                    error=str(e)
                )
                raise
```

### Debug Protocol

```python
from pepperpy.dev import DebugProtocol

class Debuggable(DebugProtocol):
    def __init__(self):
        self.debug_info = {}
    
    def set_debug(self, key: str, value: Any):
        self.debug_info[key] = value
    
    def get_debug(self, key: str) -> Any:
        return self.debug_info.get(key)
    
    # Implement other protocol methods...
```
``` 