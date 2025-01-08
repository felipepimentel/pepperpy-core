# Context Module

The PepperPy Core Context module provides a flexible implementation for state and context management in applications, with support for generic types and metadata.

## Core Components

### Context

Base class for context management:

```python
from pepperpy_core.context import Context

# Create context
context = Context()

# Set value
await context.set("user", {"id": 1})

# Get value
user = await context.get("user")
```

### State

State management with validation:

```python
from pepperpy_core.context import State
from dataclasses import dataclass

@dataclass
class UserState:
    username: str
    role: str

# Create state
state = State[UserState]()

# Set state
await state.set(UserState(
    username="john",
    role="admin"
))
```

### Session

Session management:

```python
from pepperpy_core.context import Session

# Create session
session = Session()

# Set multiple values
await session.update({
    "user_id": 1,
    "role": "admin",
    "permissions": ["read", "write"]
})
```

## Usage Examples

### Basic Context

```python
from pepperpy_core.context import Context

# Create context
context = Context()

# Set current session
await context.set(
    "session",
    {"user": "john"}
)

# Get value
state = await context.get("session")
print(f"User: {state.value.username}")
```

## Advanced Features

### Validated Context

```python
from pepperpy_core.context import ValidatedContext
from pydantic import BaseModel

class Config(BaseModel):
    host: str
    port: int

class AppContext(ValidatedContext):
    async def validate(self, key: str, value: Any):
        if key == "config":
            if not isinstance(value, Config):
                raise ValueError(
                    f"Validation failed for {key}"
                )
```

## Best Practices

1. **Type Safety**
   - Use generic types
   - Validate inputs
   - Maintain consistency
   - Handle errors

2. **State Management**
   - Keep state minimal
   - Use immutable data
   - Handle updates
   - Monitor changes

3. **Validation**
   - Implement validation
   - Check types
   - Validate format
   - Handle errors

4. **Performance**
   - Optimize access
   - Use caching
   - Monitor usage
   - Handle cleanup

5. **Security**
   - Protect sensitive data
   - Validate access
   - Clean sensitive data
   - Monitor usage

## Common Patterns

### Context with Cache

```python
from pepperpy_core.context import CachedContext

class AppContext(CachedContext):
    def __init__(self):
        super().__init__()
        self.cache = {}
    
    async def get(self, key: str) -> Any:
        # Check cache
        if key in self.cache:
            return self.cache[key]
        
        # Get value
        value = await super().get(key)
        
        # Update cache
        self.cache[key] = value
        return value
```

### Context with History

```python
from pepperpy_core.context import HistoryContext

class AppContext(HistoryContext):
    def __init__(self):
        super().__init__()
        self.history = []
    
    async def set(self, key: str, value: Any):
        # Record change
        self.history.append({
            "key": key,
            "value": value,
            "timestamp": time.time()
        })
        
        await super().set(key, value)
```

## API Reference

### Context

```python
class Context:
    async def get(
        self,
        key: str
    ) -> Any:
        """Get value by key."""
        
    async def set(
        self,
        key: str,
        value: Any
    ):
        """Set value by key."""
        
    async def delete(
        self,
        key: str
    ):
        """Delete value by key."""
```

### State

```python
class State[T]:
    async def get(self) -> T:
        """Get current state."""
        
    async def set(
        self,
        value: T
    ):
        """Set new state."""
        
    async def update(
        self,
        updater: Callable[[T], T]
    ):
        """Update state."""
```

### Session

```python
class Session:
    async def start(self):
        """Start session."""
        
    async def end(self):
        """End session."""
        
    async def clear(self):
        """Clear session data."""
``` 