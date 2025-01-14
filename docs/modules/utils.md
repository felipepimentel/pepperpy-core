# Utilities Module

The PepperPy Utils module provides a collection of utility functions and classes for common tasks, including string manipulation, dates, files, error handling, logging, and other resources.

## Core Components

### Error Utilities

```python
from pepperpy.error import (
    format_exception,
    format_error_context,
    get_error_type
)

# Basic exception formatting
try:
    result = await process_data()
except Exception as e:
    error_details = format_exception(e)
    logger.error(f"Processing failed: {error_details}")

# Detailed error context
try:
    await task.execute()
except TaskError as e:
    error_details = format_error_context(
        e,
        include_traceback=True,
        include_cause=True
    )
    logger.error(f"Task failed: {error_details}")

# Dynamic error type handling
error_type = get_error_type("ValidationError")
if error_type:
    raise error_type("Invalid input data")
```

The error utilities provide:

1. `format_exception(error: Exception) -> str`
   - Formats an exception with its full traceback
   - Useful for debugging and logging
   - Includes complete stack trace

2. `format_error_context(error: Exception, *, include_traceback: bool = True, include_cause: bool = True) -> str`
   - Enhanced error formatting with context
   - Includes error type and message
   - Shows PepperpyError specific attributes
   - Optional traceback and cause chain
   - Structured output format

3. `get_error_type(error_name: str) -> Optional[Type[Exception]]`
   - Gets exception type by name
   - Searches PepperpyError hierarchy
   - Useful for dynamic error handling
   - Returns None if not found

### Logging Utilities

```python
from pepperpy.logging import (
    get_logger,
    get_module_logger,
    get_package_logger,
    LoggerMixin
)

# Get loggers
logger = get_logger("my_logger")
module_logger = get_module_logger(__name__)
package_logger = get_package_logger()

# Use LoggerMixin
class MyClass(LoggerMixin):
    def process(self):
        self.logger.info("Processing...")
        try:
            result = do_something()
            self.logger.debug(f"Result: {result}")
        except Exception as e:
            self.logger.error(f"Error: {e}")
```

The logging utilities provide:

1. `get_logger(name: str) -> logging.Logger`
   - Gets a logger by name
   - Returns standard Python logger
   - Consistent naming convention

2. `get_module_logger(module_name: str) -> logging.Logger`
   - Gets a logger for a module
   - Uses module name as logger name
   - Consistent module logging

3. `get_package_logger() -> logging.Logger`
   - Gets the package logger
   - Uses "pepperpy" as name
   - Central package logging

4. `LoggerMixin`
   - Adds logging capabilities to classes
   - Provides standard logging methods
   - Uses class name as logger name

### Package Utilities

```python
from pepperpy.package import (
    get_package_name,
    get_package_version
)

# Get package info
name = get_package_name()  # "pepperpy"
version = get_package_version()  # e.g. "1.0.0"
```

The package utilities provide:

1. `get_package_name() -> str`
   - Gets the package name
   - Returns "pepperpy"
   - Consistent package naming

2. `get_package_version() -> str`
   - Gets the package version
   - Uses importlib.metadata
   - Returns "0.0.0" if not found

### String Utilities

```python
from pepperpy.utils import strings

# String manipulation
text = strings.normalize("Hello World!")
slug = strings.slugify("Hello World!")
uuid = strings.generate_uuid()
```

### Date Utilities

```python
from pepperpy.utils import dates

# Date operations
now = dates.now()
tomorrow = dates.add_days(now, 1)
formatted = dates.format(now, "YYYY-MM-DD")
```

### File Utilities

```python
from pepperpy.utils import files

# File operations
exists = files.exists("data.txt")
size = files.get_size("data.txt")
mime = files.get_mime_type("image.png")
```

### Collection Utilities

```python
from pepperpy.utils import collections

# Collection operations
chunks = collections.chunk(data, size=100)
unique = collections.unique(items)
grouped = collections.group_by(items, key="type")
```

## Advanced Features

### Path Utilities

```python
from pepperpy.utils import paths

# Path operations
normalized = paths.normalize("/path/to/file")
relative = paths.make_relative(path, base)
absolute = paths.make_absolute(path)
```

### Hash Utilities

```python
from pepperpy.utils import hashing

# Hash operations
md5 = hashing.md5("data")
sha256 = hashing.sha256("data")
hash = hashing.hash_file("file.txt")
```

### Validation Utilities

```python
from pepperpy.utils import validation

# Validation operations
is_email = validation.is_email("user@example.com")
is_url = validation.is_url("https://example.com")
is_ip = validation.is_ip("192.168.1.1")
```

## Best Practices

1. **Error Handling**
   - Use proper error formatting
   - Include context in errors
   - Handle errors appropriately
   - Log errors with details

2. **Logging**
   - Use appropriate log levels
   - Include relevant context
   - Follow naming conventions
   - Use LoggerMixin when needed

3. **String Operations**
   - Use proper encoding
   - Handle special chars
   - Validate input
   - Normalize output

4. **Date Operations**
   - Use UTC when possible
   - Handle timezones
   - Format consistently
   - Validate dates

5. **File Operations**
   - Check permissions
   - Handle errors
   - Clean up resources
   - Validate paths

6. **Collections**
   - Handle empty cases
   - Check types
   - Optimize operations
   - Document usage

7. **Security**
   - Validate input
   - Sanitize data
   - Use secure hashes
   - Handle errors

## Common Patterns

### String Processing

```python
from pepperpy.utils import strings

class TextProcessor:
    def __init__(self):
        self.processors = []
    
    def add_processor(self, func):
        self.processors.append(func)
    
    def process(self, text: str) -> str:
        result = text
        for processor in self.processors:
            result = processor(result)
        return result
```

### File Processing

```python
from pepperpy.utils import files

class FileProcessor:
    def __init__(self, chunk_size: int = 8192):
        self.chunk_size = chunk_size
    
    async def process_file(self, path: str):
        # Check file
        if not files.exists(path):
            raise FileNotFoundError(path)
        
        # Process chunks
        async for chunk in files.read_chunks(
            path,
            self.chunk_size
        ):
            await self.process_chunk(chunk)
```

### Data Validation

```python
from pepperpy.utils import validation

class DataValidator:
    def __init__(self):
        self.validators = {}
    
    def add_validator(self, field: str, func: callable):
        self.validators[field] = func
    
    def validate(self, data: dict) -> bool:
        for field, validator in self.validators.items():
            if field in data:
                if not validator(data[field]):
                    return False
        return True
```

## API Reference

### String Utils

```python
class StringUtils:
    def normalize(text: str) -> str:
        """Normalize text."""
        
    def slugify(text: str) -> str:
        """Create URL slug."""
        
    def truncate(
        text: str,
        length: int
    ) -> str:
        """Truncate text."""
```

### Date Utils

```python
class DateUtils:
    def now() -> datetime:
        """Get current time."""
        
    def parse(text: str) -> datetime:
        """Parse date string."""
        
    def format(
        date: datetime,
        format: str
    ) -> str:
        """Format date."""
```

### File Utils

```python
class FileUtils:
    def exists(path: str) -> bool:
        """Check if file exists."""
        
    def get_size(path: str) -> int:
        """Get file size."""
        
    def get_mime(path: str) -> str:
        """Get MIME type."""
```
```