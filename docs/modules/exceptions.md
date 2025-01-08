# Exceptions Module

The PepperPy Core Exceptions module provides a complete hierarchy of exceptions for handling specific library errors.

## Exception Hierarchy

### BaseException

Base class for all exceptions:

```python
from pepperpy_core.exceptions import PepperPyException

try:
    # Operation that may fail
    result = process_data()
except PepperPyException as e:
    print(f"Error: {e}")
```

### Configuration Exceptions

```python
from pepperpy_core.exceptions import ConfigError

try:
    config.validate()
except ConfigError as e:
    print(f"Configuration error: {e}")
    print(f"Config: {e.config_name}")
```

### Validation Exceptions

```python
from pepperpy_core.exceptions import ValidationError

try:
    validator.validate(data)
except ValidationError as e:
    print(f"Validation error: {e}")
    print(f"Invalid value: {e.invalid_value}")
```

## Exception Categories

### Module Exceptions

```python
from pepperpy_core.exceptions import (
    ModuleError,
    ModuleInitError,
    ModuleNotFoundError
)

try:
    await module.initialize()
except ModuleInitError as e:
    print(f"Initialization error: {e}")
    print(f"Module: {e.module_name}")
except ModuleNotFoundError as e:
    print(f"Module not found: {e}")
```

### Security Exceptions

```python
from pepperpy_core.exceptions import (
    SecurityError,
    AuthenticationError,
    AuthorizationError,
    InvalidTokenError
)

try:
    await security.authenticate(token)
except AuthenticationError:
    print("Authentication error")
except AuthorizationError:
    print("Permission error")
except InvalidTokenError:
    print("Invalid token")
```

### Task Exceptions

```python
from pepperpy_core.exceptions import (
    TaskError,
    TaskExecutionError,
    TaskNotFoundError
)

try:
    await task.execute()
except TaskExecutionError as e:
    print(f"Task execution error: {e}")
    print(f"Task ID: {e.task_id}")
except TaskNotFoundError as e:
    print(f"Task not found: {e}")
```

## Usage Examples

### Basic Error Handling

```python
from pepperpy_core.exceptions import (
    ValidationError,
    ProcessingError,
    ResourceError
)

async def process_data(data: dict) -> dict:
    try:
        # Validate data
        if not is_valid(data):
            raise ValidationError("Invalid data")
            
        # Process data
        result = await process(data)
        
        return result
    except ValidationError as e:
        print(f"Invalid data: {e}")
        raise
```

### Exception Chaining

```python
from pepperpy_core.exceptions import (
    ConfigError,
    ValidationError,
    ProcessingError
)

async def initialize_system():
    try:
        # Load configuration
        config = await load_config()
        
        # Validate configuration
        if not is_valid_config(config):
            raise ConfigError(
                "Invalid configuration",
                config_name="system"
            )
        
        return config
    except FileNotFoundError as e:
        raise ConfigError(
            "Configuration file not found"
        ) from e
```

### Custom Exceptions

```python
from pepperpy_core.exceptions import PepperPyException

class CustomError(PepperPyException):
    def __init__(
        self,
        message: str,
        code: int = None
    ):
        super().__init__(message)
        self.code = code
```

## Best Practices

1. **Exception Design**
   - Keep hierarchy clean
   - Use descriptive names
   - Include context
   - Follow patterns

2. **Error Handling**
   - Handle specific errors
   - Provide context
   - Log appropriately
   - Clean up resources

3. **Documentation**
   - Document exceptions
   - Include examples
   - Explain causes
   - Suggest solutions

4. **Testing**
   - Test error cases
   - Verify messages
   - Check context
   - Test cleanup

## Common Patterns

### Retry Pattern

```python
from pepperpy_core.exceptions import RetryableError

class RetryHandler:
    async def execute(
        self,
        operation: callable,
        max_retries: int = 3
    ):
        retries = 0
        while True:
            try:
                return await operation()
            except RetryableError as e:
                retries += 1
                if retries >= max_retries:
                    raise
                await self.wait(retries)
```

### Context Exceptions

```python
from pepperpy_core.exceptions import ContextError

class Context:
    def __init__(self):
        self.state = {}
    
    def get(self, key: str) -> Any:
        try:
            return self.state[key]
        except KeyError:
            raise ContextError(
                f"Missing context: {key}"
            )
```

### Exception Translation

```python
from pepperpy_core.exceptions import ExceptionTranslator

class APITranslator(ExceptionTranslator):
    def translate(self, error: Exception) -> dict:
        if isinstance(error, ValidationError):
            return {
                "code": 400,
                "error": "validation_error",
                "message": str(error)
            }
        elif isinstance(error, AuthenticationError):
            return {
                "code": 401,
                "error": "authentication_error",
                "message": str(error)
            }
        else:
            return {
                "code": 500,
                "error": "internal_error",
                "message": "Internal server error"
            }
```

## API Reference

### Base Exceptions

```python
class PepperPyException(Exception):
    """Base exception for all PepperPy errors."""

class ConfigError(PepperPyException):
    """Configuration related errors."""

class ValidationError(PepperPyException):
    """Validation related errors."""
```

### Error Context

```python
class ErrorContext:
    def __init__(
        self,
        message: str,
        code: str = None,
        details: dict = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
```

### Exception Events

The exceptions module emits the following events:

- `error.raised` - When an error is raised
- `error.handled` - When an error is handled
- `error.logged` - When an error is logged

### Error Handling

```python
try:
    result = await process()
except ValidationError as e:
    logger.error(f"Validation error: {e}")
    raise APIError(400, str(e))
except ProcessingError as e:
    logger.error(f"Processing error: {e}")
    raise APIError(500, "Internal error")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise APIError(500, "System error")
``` 