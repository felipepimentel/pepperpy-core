# Serialization Module

The PepperPy Core Serialization module provides utilities for object serialization and deserialization, with special support for JSON and custom objects.

## Core Components

### Serializable Protocol

Protocol for serializable objects:

```python
from pepperpy.serialization import Serializable

class User(Serializable):
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
    
    def serialize(self) -> dict:
        return {
            "name": self.name,
            "email": self.email
        }
    
    @classmethod
    def deserialize(cls, data: dict) -> "User":
        return cls(
            name=data["name"],
            email=data["email"]
        )
```

### Basic Serialization

```python
from pepperpy.serialization import JsonSerializer

# Create serializer
serializer = JsonSerializer()

# Serialize object
data = {"name": "John", "age": 30}
json_str = serializer.serialize(data)

# Deserialize object
data = serializer.deserialize(json_str)
```

### Complex Serialization

```python
from pepperpy.serialization import (
    Serializer,
    Field,
    serialize,
    deserialize
)

@serialize
class User:
    name: str = Field()
    email: str = Field()
    age: int = Field(default=0)
    active: bool = Field(default=True)

# Create object
user = User(
    name="John",
    email="john@example.com"
)

# Serialize
data = user.serialize()

# Deserialize
user = User.deserialize(data)
```

## Advanced Features

### Serializer with Validation

```python
from pepperpy.serialization import ValidatedSerializer

class UserSerializer(ValidatedSerializer):
    def validate(self, data: dict) -> bool:
        # Validate required fields
        if "name" not in data:
            raise ValueError("Name is required")
        
        if "email" not in data:
            raise ValueError("Email is required")
        
        # Validate types
        if not isinstance(data["name"], str):
            raise ValueError("Name must be string")
        
        if not isinstance(data["email"], str):
            raise ValueError("Email must be string")
        
        return True
```

## Best Practices

1. **Serialization**
   - Validate input
   - Handle types
   - Use schemas
   - Document format

2. **Deserialization**
   - Validate data
   - Handle errors
   - Maintain consistency
   - Check types

3. **Performance**
   - Optimize conversions
   - Use caching
   - Batch operations
   - Monitor usage

4. **Security**
   - Validate input
   - Sanitize data
   - Protect sensitive data
   - Monitor access

5. **Maintenance**
   - Document changes
   - Test conversions
   - Update schemas
   - Monitor usage

## Common Patterns

### Versioned Serializer

```python
from pepperpy.serialization import VersionedSerializer

class DataSerializer(VersionedSerializer):
    def serialize(self, obj: Any) -> dict:
        # Add version
        data = super().serialize(obj)
        data["_version"] = "1.0"
        return data
    
    def deserialize(self, data: dict) -> Any:
        # Extract and check version
        version = data.get("_version")
        if version != "1.0":
            raise ValueError(
                f"Incompatible version: {version}"
            )
        
        return super().deserialize(data)
```

### Compressed Serializer

```python
from pepperpy.serialization import CompressedSerializer

class DataSerializer(CompressedSerializer):
    def serialize(self, obj: Any) -> bytes:
        # Serialize and compress
        data = super().serialize(obj)
        return self.compress(data)
    
    def deserialize(self, data: bytes) -> Any:
        # Decompress and deserialize
        data = self.decompress(data)
        return super().deserialize(data)
```

### Cached Serializer

```python
from pepperpy.serialization import CachedSerializer

class DataSerializer(CachedSerializer):
    def __init__(self):
        super().__init__()
        self.cache = {}
    
    def serialize(self, obj: Any) -> str:
        # Check cache
        key = self.get_cache_key(obj)
        if key in self.cache:
            return self.cache[key]
        
        # Serialize
        data = super().serialize(obj)
        
        # Update cache
        self.cache[key] = data
        return data
```

## API Reference

### Serializer

```python
class Serializer:
    def serialize(
        self,
        obj: Any
    ) -> Union[str, bytes, dict]:
        """Serialize object."""
        
    def deserialize(
        self,
        data: Union[str, bytes, dict]
    ) -> Any:
        """Deserialize object."""
```

### Field

```python
class Field:
    def __init__(
        self,
        type_: Type = None,
        default: Any = None,
        required: bool = True
    ):
        """Initialize field."""
```

### Decorators

```python
def serialize(cls: Type[T]) -> Type[T]:
    """Add serialization to class."""
    
def deserialize(cls: Type[T]) -> Type[T]:
    """Add deserialization to class."""
``` 