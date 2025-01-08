# Logging Module

The PepperPy Core Logging module provides a flexible and extensible implementation for logging, with support for multiple handlers, custom formatting, and log levels.

## Core Components

### Logger

```python
from pepperpy_core.logging import Logger

# Create logger
logger = Logger("app")

# Log messages
logger.debug("Detailed information")
logger.info("Application started")
logger.warning("Resource near limit")
logger.error("Operation failed")
```

### LogLevel

Enumeration for log levels:

```python
from pepperpy_core.logging import LogLevel

# Available levels
level = LogLevel.DEBUG    # Detailed information
level = LogLevel.INFO     # General information
level = LogLevel.WARNING  # Warnings
level = LogLevel.ERROR    # Errors
level = LogLevel.CRITICAL # Critical errors
```

### LogConfig

Logging system configuration:

```python
from pepperpy_core.logging import LogConfig

# Basic configuration
config = LogConfig(
    level=LogLevel.INFO,
    format="{time} {level} {message}",
    handlers=["console", "file"]
)
```

### Basic Logger

```python
from pepperpy_core.logging import Logger

# Create logger
logger = Logger("app")

# Logs at different levels
logger.debug("Processing started")
logger.warning("Resource near limit")
logger.error("Operation failed")
logger.critical("System unavailable")

# Structured logging
logger.info(
    "User authenticated",
    extra={
        "user_id": "123",
        "ip": "192.168.1.1"
    }
)
```

### Handler Configuration

```python
from pepperpy_core.logging import (
    FileHandler,
    ConsoleHandler,
    NetworkHandler
)

# Configure handlers
handlers = [
    FileHandler("app.log"),
    ConsoleHandler(),
    NetworkHandler("logs.server.com")
]

# Create logger with handlers
logger = Logger("app", handlers=handlers)
```

## Advanced Features

### Custom Handler

```python
from pepperpy_core.logging import Handler

class DatabaseHandler(Handler):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection
    
    async def emit(self, record: LogRecord):
        await self.connection.execute(
            "INSERT INTO logs VALUES (?, ?, ?)",
            record.time,
            record.level,
            record.message
        )
```

### Advanced Formatting

```python
from pepperpy_core.logging import Formatter

class CustomFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        return (
            f"[{record.time}] "
            f"{record.level}: "
            f"{record.message} "
            f"({record.extra})"
        )
```

## Best Practices

1. **Log Levels**
   - Use appropriate levels
   - Be consistent
   - Document usage
   - Configure defaults

2. **Formatting**
   - Include timestamp
   - Add context
   - Use structured data
   - Be consistent

3. **Handlers**
   - Use multiple handlers
   - Implement rotation
   - Configure levels
   - Handle errors

4. **Performance**
   - Optimize formatting
   - Batch writes
   - Configure buffers
   - Monitor impact

5. **Security**
   - Sanitize sensitive data
   - Control access
   - Encrypt if needed
   - Monitor usage

## Common Patterns

### Logger with Metrics

```python
from pepperpy_core.logging import MetricsLogger

class MonitoredLogger(MetricsLogger):
    def __init__(self):
        super().__init__()
        self.metrics = {
            "debug": 0,
            "info": 0,
            "warning": 0,
            "error": 0
        }
    
    async def log(
        self,
        level: LogLevel,
        message: str,
        **kwargs
    ):
        # Update metrics
        self.metrics[level.name.lower()] += 1
        
        # Log message
        await super().log(level, message, **kwargs)
    
    def get_metrics(self) -> dict:
        return {
            "total": sum(self.metrics.values()),
            "by_level": self.metrics.copy()
        }
```

### Logger with Aggregation

```python
from pepperpy_core.logging import AggregateLogger

class BatchLogger(AggregateLogger):
    def __init__(
        self,
        batch_size: int = 100,
        flush_interval: float = 1.0
    ):
        super().__init__()
        self.batch = []
        self.batch_size = batch_size
        self.last_flush = time.time()
    
    async def log(
        self,
        level: LogLevel,
        message: str,
        **kwargs
    ):
        # Add to batch
        self.batch.append({
            "level": level,
            "message": message,
            "time": time.time(),
            **kwargs
        })
        
        # Aggregate if needed
        if len(self.batch) >= self.batch_size:
            await self.flush()
```

## API Reference

### Logger

```python
class Logger:
    async def log(
        self,
        level: LogLevel,
        message: str,
        **kwargs
    ):
        """Log a message."""
        
    def set_level(
        self,
        level: LogLevel
    ):
        """Set logger level."""
        
    def add_handler(
        self,
        handler: Handler
    ):
        """Add log handler."""
```

### Handler

```python
class Handler:
    async def emit(
        self,
        record: LogRecord
    ):
        """Emit log record."""
        
    def set_formatter(
        self,
        formatter: Formatter
    ):
        """Set record formatter."""
```

### Formatter

```python
class Formatter:
    def format(
        self,
        record: LogRecord
    ) -> str:
        """Format log record."""
        
    def format_time(
        self,
        time: float
    ) -> str:
        """Format timestamp."""
``` 