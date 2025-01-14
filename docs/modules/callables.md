# Callables Module

The callables module provides protocols and utilities for working with callable objects in PepperPy. It includes protocols for synchronous and asynchronous callables, coroutines, and validation utilities.

## Overview

The module implements:
- Type-safe callable protocols
- Async callable protocols
- Coroutine protocols
- Validation utilities for all callable types
- Runtime type checking support

## Protocols

### Callable

A protocol defining the interface for synchronous callable objects.

```python
@runtime_checkable
class Callable(Protocol[P, T]):
    def __call__(self, *args: Any, **kwargs: Any) -> T
```

The protocol is generic over:
- `P`: Parameter specification
- `T`: Return type

**Arguments:**
- `args`: Positional arguments
- `kwargs`: Keyword arguments

**Returns:**
- Value of type `T`

### AsyncCallable

A protocol defining the interface for asynchronous callable objects.

```python
@runtime_checkable
class AsyncCallable(Protocol[P, T]):
    async def __call__(self, *args: Any, **kwargs: Any) -> T
```

The protocol is generic over:
- `P`: Parameter specification
- `T`: Return type

**Arguments:**
- `args`: Positional arguments
- `kwargs`: Keyword arguments

**Returns:**
- Value of type `T` (asynchronously)

### Coroutine

A protocol defining the interface for coroutine objects.

```python
@runtime_checkable
class Coroutine(Protocol[T]):
    def send(self, value: Any) -> T
    def throw(self, typ: Any, val: Any = None, tb: Any = None) -> T
    def close(self) -> None
```

The protocol is generic over type `T` and provides:
- `send`: Send a value to the coroutine
- `throw`: Throw an exception into the coroutine
- `close`: Close the coroutine

## Functions

### validate_callable

```python
def validate_callable(value: Any) -> Callable[..., Any]
```

Validate that a value is a synchronous callable.

**Arguments:**
- `value`: Value to validate

**Returns:**
- Validated callable

**Raises:**
- `TypeError`: If value is not callable

### validate_async_callable

```python
def validate_async_callable(value: Any) -> AsyncCallable[Any, Any]
```

Validate that a value is an asynchronous callable.

**Arguments:**
- `value`: Value to validate

**Returns:**
- Validated async callable

**Raises:**
- `TypeError`: If value is not an async callable

### validate_coroutine

```python
def validate_coroutine(value: Any) -> Coroutine[Any, Any, Any]
```

Validate that a value is a coroutine.

**Arguments:**
- `value`: Value to validate

**Returns:**
- Validated coroutine

**Raises:**
- `TypeError`: If value is not a coroutine

## Usage Examples

### Using Callable Protocol

```python
from pepperpy.callables import Callable, validate_callable

# Function callable
def add(a: int, b: int) -> int:
    return a + b

# Class callable
class Multiplier:
    def __call__(self, x: int, y: int) -> int:
        return x * y

# Validate callables
func = validate_callable(add)
obj = validate_callable(Multiplier())

# Use callables
print(func(1, 2))  # Prints 3
print(obj(2, 3))   # Prints 6
```

### Using AsyncCallable Protocol

```python
from pepperpy.callables import AsyncCallable, validate_async_callable

# Async function callable
async def fetch_data(url: str) -> str:
    return f"Data from {url}"

# Async class callable
class AsyncProcessor:
    async def __call__(self, data: str) -> str:
        return f"Processed {data}"

# Validate async callables
async_func = validate_async_callable(fetch_data)
async_obj = validate_async_callable(AsyncProcessor())

# Use async callables
data = await async_func("https://api.example.com")
result = await async_obj(data)
```

### Using Coroutine Protocol

```python
from pepperpy.callables import Coroutine, validate_coroutine

async def data_processor():
    while True:
        data = yield
        print(f"Processing {data}")

# Create and validate coroutine
coro = data_processor()
validated_coro = validate_coroutine(coro)

# Use coroutine
validated_coro.send(None)  # Start coroutine
validated_coro.send("sample data")
validated_coro.close()
```

### Runtime Type Checking

```python
from pepperpy.callables import Callable, AsyncCallable, Coroutine

def is_callable(obj: Any) -> bool:
    return isinstance(obj, Callable)

def is_async_callable(obj: Any) -> bool:
    return isinstance(obj, AsyncCallable)

def is_coroutine(obj: Any) -> bool:
    return isinstance(obj, Coroutine)
```

## Best Practices

1. **Type Safety**: Use the callable protocols to ensure type safety in your code
2. **Validation**: Always validate callables before using them in critical code paths
3. **Error Handling**: Handle exceptions appropriately when working with callables
4. **Coroutine Management**: Always close coroutines when done to prevent resource leaks
5. **Documentation**: Document the expected arguments and return types of your callables

## See Also

- [Core Module](core.md) - Core functionality and base types
- [Types Module](types.md) - Common type definitions and utilities
- [Validation Module](validation.md) - General validation utilities 