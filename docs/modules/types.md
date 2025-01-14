# Types Module

The PepperPy Core Types module provides type definitions and base classes for static typing, including generic types, protocols, and utilities for type hints.

## Core Components

### Base Types

```python
from pepperpy.types import (
    JsonDict,
    JsonList,
    PathLike,
    Callback
)

# Type aliases
Json = Union[str, int, float, bool, None, JsonDict, JsonList]
Handler = Callable[[Event], Awaitable[None]]
```

### Generic Types

```python
from pepperpy.types import (
    T,
    K,
    V,
    Container,
    Processor
)

class Cache(Container[T]):
    async def get(self, key: str) -> T:
        # Implementation
        pass
    
    async def set(self, key: str, value: T):
        # Implementation
        pass

class DataProcessor(Processor[T, V]):
    async def process(self, data: T) -> V:
        # Implementation
        pass
```

### Protocols

```python
from pepperpy.types import (
    Serializable,
    Validator,
    Handler
)

class JsonSerializable(Protocol):
    def to_json(self) -> str:
        # Implementation
        pass
    
    @classmethod
    def from_json(cls, data: str) -> Self:
        # Implementation
        pass
```

## Advanced Features

### Type Guards

```python
from pepperpy.types import TypeGuard

def is_user(data: Any) -> TypeGuard[User]:
    try:
        # data is typed as User
        print(f"User: {data['name']}")
        return True
    except (KeyError, TypeError):
        # data is typed as Any
        print("Invalid data")
        return False
```

### Type Registry

```python
from pepperpy.types import Registry

registry = Registry[Type[T]]()

# Business types
registry.register("user", User)
registry.register("order", Order)

# Function types
registry.register("processor", Processor)
registry.register("validator", Validator)
```

## Best Practices

1. **Type Hints**
   - Use type hints
   - Document types
   - Check coverage
   - Handle edge cases

2. **Generics**
   - Keep simple
   - Use constraints
   - Document variance
   - Test bounds

3. **Validation**
   - Validate types
   - Check bounds
   - Handle errors
   - Log issues

4. **Maintenance**
   - Keep up to date
   - Remove duplication
   - Maintain consistency
   - Test changes

5. **Documentation**
   - Document types
   - Include examples
   - Document changes
   - Keep updated

## Common Patterns

### Type Factory

```python
from pepperpy.types import TypeFactory

class Factory(TypeFactory[T]):
    def __init__(self):
        self.types: dict[str, Type[T]] = {}
    
    def register(
        self,
        name: str,
        type_: Type[T]
    ):
        self.types[name] = type_
    
    def create(self, name: str, **kwargs) -> T:
        if name not in self.types:
            raise ValueError(
                f"Type {name} not registered"
            )
        
        return self.types[name](**kwargs)
```

### Type Converter

```python
from pepperpy.types import TypeConverter

class Converter(TypeConverter):
    def __init__(self):
        self.converters = {}
    
    def register(
        self,
        source: Type,
        target: Type,
        converter: Callable
    ):
        self.converters[(source, target)] = converter
    
    def convert(
        self,
        value: Any,
        target: Type
    ) -> Any:
        source = type(value)
        key = (source, target)
        
        if key not in self.converters:
            raise TypeError(
                f"Unsupported type: {type(obj)}"
            )
        
        return self.converters[key](value)
```

### Type Cache

```python
from pepperpy.types import TypeCache

class Cache(TypeCache[T]):
    def __init__(self):
        self.cache: dict[str, T] = {}
    
    def get(self, key: str) -> Optional[T]:
        return self.cache.get(key)
    
    def set(self, key: str, value: T):
        self.cache[key] = value
    
    def clear(self):
        self.cache.clear()
```

## API Reference

### Base Types

```python
class JsonDict(TypedDict):
    """JSON object type."""

class JsonList(List[Json]):
    """JSON array type."""

class PathLike(Protocol):
    """Path-like object."""
    
    def __fspath__(self) -> str:
        """Return file system path."""
```

### Generic Types

```python
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

class Container(Generic[T]):
    """Generic container."""
    
    def get(self) -> T:
        """Get value."""
    
    def set(self, value: T):
        """Set value."""

class Processor(Generic[T, V]):
    """Generic processor."""
    
    def process(self, data: T) -> V:
        """Process data."""
```

### Type Guards

```python
class TypeGuard(Generic[T]):
    """Type guard protocol."""
    
    def check(self, value: Any) -> bool:
        """Check if value is of type T."""
    
    def cast(self, value: Any) -> T:
        """Cast value to type T."""
``` 