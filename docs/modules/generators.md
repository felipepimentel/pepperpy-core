# Generators Module

The generators module provides protocols and utilities for working with generators in PepperPy. It includes both synchronous and asynchronous generator protocols, along with validation utilities.

## Overview

The module implements:
- Type-safe generator protocols
- Async generator protocols
- Generator validation utilities
- Runtime type checking support

## Protocols

### Generator

A protocol defining the interface for synchronous generators.

```python
@runtime_checkable
class Generator(Protocol[T]):
    def __iter__(self) -> Generator[T]
    def __next__(self) -> T
```

The protocol is generic over type `T` and provides:
- `__iter__`: Returns the generator iterator
- `__next__`: Returns the next value in the sequence

**Raises:**
- `StopIteration`: When no more values are available

### AsyncGenerator

A protocol defining the interface for asynchronous generators.

```python
@runtime_checkable
class AsyncGenerator(Protocol[T]):
    def __aiter__(self) -> AsyncGenerator[T]
    async def __anext__(self) -> T
```

The protocol is generic over type `T` and provides:
- `__aiter__`: Returns the async generator iterator
- `__anext__`: Returns the next value in the sequence asynchronously

**Raises:**
- `StopAsyncIteration`: When no more values are available

## Functions

### validate_generator

```python
def validate_generator(value: Any) -> Generator[Any, Any, Any]
```

Validate that a value is a synchronous generator.

**Arguments:**
- `value`: Value to validate

**Returns:**
- Validated generator

**Raises:**
- `TypeError`: If value is not a generator

### validate_async_generator

```python
def validate_async_generator(value: Any) -> AsyncGenerator[Any, None]
```

Validate that a value is an asynchronous generator.

**Arguments:**
- `value`: Value to validate

**Returns:**
- Validated async generator

**Raises:**
- `TypeError`: If value is not an async generator

## Usage Examples

### Using Generator Protocol

```python
from pepperpy.generators import Generator, validate_generator

def number_generator() -> Generator[int]:
    for i in range(5):
        yield i

# Validate generator
gen = validate_generator(number_generator())

# Use generator
for num in gen:
    print(num)  # Prints 0, 1, 2, 3, 4
```

### Using AsyncGenerator Protocol

```python
from pepperpy.generators import AsyncGenerator, validate_async_generator

async def async_number_generator() -> AsyncGenerator[int]:
    for i in range(5):
        yield i

# Validate async generator
async_gen = validate_async_generator(async_number_generator())

# Use async generator
async for num in async_gen:
    print(num)  # Prints 0, 1, 2, 3, 4
```

### Runtime Type Checking

```python
from pepperpy.generators import Generator, AsyncGenerator

def is_generator(obj: Any) -> bool:
    return isinstance(obj, Generator)

def is_async_generator(obj: Any) -> bool:
    return isinstance(obj, AsyncGenerator)

# Check types at runtime
print(is_generator(number_generator()))  # True
print(is_async_generator(async_number_generator()))  # True
```

## Best Practices

1. **Type Safety**: Use the generator protocols to ensure type safety in your code
2. **Validation**: Always validate generators before using them in critical code paths
3. **Error Handling**: Handle StopIteration and StopAsyncIteration appropriately
4. **Runtime Checking**: Use runtime_checkable protocols for dynamic type checking
5. **Documentation**: Document the type of values your generators yield

## See Also

- [Core Module](core.md) - Core functionality and base types
- [Types Module](types.md) - Common type definitions and utilities
- [Validation Module](validation.md) - General validation utilities 