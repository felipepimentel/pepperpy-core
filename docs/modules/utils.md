# Utilities Module

The PepperPy Core Utils module provides a collection of utility functions and classes for common tasks, including string manipulation, dates, files, and other resources.

## Core Components

### String Utilities

```python
from pepperpy_core.utils import strings

# String manipulation
text = strings.normalize("Hello World!")
slug = strings.slugify("Hello World!")
uuid = strings.generate_uuid()
```

### Date Utilities

```python
from pepperpy_core.utils import dates

# Date operations
now = dates.now()
tomorrow = dates.add_days(now, 1)
formatted = dates.format(now, "YYYY-MM-DD")
```

### File Utilities

```python
from pepperpy_core.utils import files

# File operations
exists = files.exists("data.txt")
size = files.get_size("data.txt")
mime = files.get_mime_type("image.png")
```

### Collection Utilities

```python
from pepperpy_core.utils import collections

# Collection operations
chunks = collections.chunk(data, size=100)
unique = collections.unique(items)
grouped = collections.group_by(items, key="type")
```

## Advanced Features

### Path Utilities

```python
from pepperpy_core.utils import paths

# Path operations
normalized = paths.normalize("/path/to/file")
relative = paths.make_relative(path, base)
absolute = paths.make_absolute(path)
```

### Hash Utilities

```python
from pepperpy_core.utils import hashing

# Hash operations
md5 = hashing.md5("data")
sha256 = hashing.sha256("data")
hash = hashing.hash_file("file.txt")
```

### Validation Utilities

```python
from pepperpy_core.utils import validation

# Validation operations
is_email = validation.is_email("user@example.com")
is_url = validation.is_url("https://example.com")
is_ip = validation.is_ip("192.168.1.1")
```

### Error Handling

```python
from pepperpy_core.utils.error import (
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

Best Practices:
- Use `format_exception` for basic error logging
- Use `format_error_context` for detailed error reporting
- Include cause chain for nested exceptions
- Add tracebacks in development/debugging
- Handle errors appropriately per context

## Best Practices

1. **String Operations**
   - Use proper encoding
   - Handle special chars
   - Validate input
   - Normalize output

2. **Date Operations**
   - Use UTC when possible
   - Handle timezones
   - Format consistently
   - Validate dates

3. **File Operations**
   - Check permissions
   - Handle errors
   - Clean up resources
   - Validate paths

4. **Collections**
   - Handle empty cases
   - Check types
   - Optimize operations
   - Document usage

5. **Security**
   - Validate input
   - Sanitize data
   - Use secure hashes
   - Handle errors

## Common Patterns

### String Processing

```python
from pepperpy_core.utils import strings

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
from pepperpy_core.utils import files

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
from pepperpy_core.utils import validation

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