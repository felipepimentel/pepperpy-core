# State Module

The PepperPy Core State module provides a robust system for application state management, including persistence, synchronization, and change observability.

## Core Components

### State Manager

```python
from pepperpy_core.state import StateManager

# Create manager
manager = StateManager()

# Set value
await manager.set("config.debug", True)

# Get value
debug = await manager.get("config.debug")
```

### State Container

```python
from pepperpy_core.state import Container
from dataclasses import dataclass

@dataclass
class AppState:
    debug: bool
    version: str

# Create container
container = Container[AppState]()

# Set state
await container.set(AppState(
    debug=True,
    version="1.0.0"
))
```

### State Observer

Change observer:

```python
from pepperpy_core.state import Observer

class ConfigObserver(Observer):
    async def on_change(
        self,
        path: str,
        value: Any
    ):
        # Observe changes
        print(f"Config changed: {path} = {value}")
```

### State Persistence

```python
from pepperpy_core.state import PersistentState

class AppState(PersistentState):
    def __init__(self):
        super().__init__("app.state")
        self.config = {}
    
    async def set_config(self, key: str, value: Any):
        self.config[key] = value
        # State is saved automatically
        await self.save()
```

## Advanced Features

### State with History

```python
from pepperpy_core.state import HistoryState

class AppState(HistoryState):
    def __init__(self):
        super().__init__()
        self.history = []
    
    async def set(self, path: str, value: Any):
        # Record change
        self.history.append({
            "path": path,
            "value": value,
            "timestamp": time.time()
        })
        
        # Limit history
        if len(self.history) > 1000:
            self.history.pop(0)
        
        await super().set(path, value)
```

### State with Validation

```python
from pepperpy_core.state import ValidatedState

class AppState(ValidatedState):
    def __init__(self):
        super().__init__()
        self.validators = {}
    
    def add_validator(
        self,
        path: str,
        validator: Callable[[Any], bool]
    ):
        self.validators[path] = validator
    
    async def validate(self, path: str, value: Any):
        if path in self.validators:
            if not self.validators[path](value):
                raise ValueError(
                    f"Invalid value for {path}: {value}"
                )
```

## Best Practices

1. **State Management**
   - Keep state minimal
   - Use immutable data
   - Handle updates
   - Monitor changes

2. **Persistence**
   - Handle failures
   - Handle corruption
   - Implement backup
   - Monitor storage

3. **Performance**
   - Optimize access
   - Use caching
   - Batch updates
   - Monitor usage

4. **Security**
   - Validate input
   - Protect state
   - Audit changes
   - Monitor access

5. **Maintenance**
   - Monitor changes
   - Clean up state
   - Document structure
   - Handle migrations

## Common Patterns

### State with Cache

```python
from pepperpy_core.state import CachedState

class AppState(CachedState):
    def __init__(self):
        super().__init__()
        self.cache = {}
    
    async def get(self, path: str) -> Any:
        # Check cache
        if path in self.cache:
            return self.cache[path]
        
        # Get value
        value = await super().get(path)
        
        # Update cache
        self.cache[path] = value
        return value
```

### State with Transactions

```python
from pepperpy_core.state import TransactionalState

class AppState(TransactionalState):
    def __init__(self):
        super().__init__()
        self.transactions = {}
    
    async def begin(self) -> str:
        # Create transaction
        tx_id = str(uuid.uuid4())
        self.transactions[tx_id] = {
            "changes": {},
            "timestamp": time.time()
        }
        return tx_id
    
    async def commit(self, tx_id: str):
        if tx_id not in self.transactions:
            raise ValueError(f"Transaction {tx_id} does not exist")
        
        # Apply changes
        changes = self.transactions[tx_id]["changes"]
        for path, value in changes.items():
            await super().set(path, value)
        
        # Clear transaction
        del self.transactions[tx_id]
    
    async def rollback(self, tx_id: str):
        if tx_id not in self.transactions:
            raise ValueError(f"Transaction {tx_id} does not exist")
        
        # Clear transaction
        del self.transactions[tx_id]
```

## API Reference

### StateManager

```python
class StateManager:
    async def get(
        self,
        path: str
    ) -> Any:
        """Get value by path."""
        
    async def set(
        self,
        path: str,
        value: Any
    ):
        """Set value by path."""
        
    async def delete(
        self,
        path: str
    ):
        """Delete value by path."""
```

### Container

```python
class Container[T]:
    async def get(self) -> T:
        """Get current state."""
        
    async def set(
        self,
        state: T
    ):
        """Set new state."""
        
    async def update(
        self,
        updater: Callable[[T], T]
    ):
        """Update state."""
```

### Observer

```python
class Observer:
    async def on_change(
        self,
        path: str,
        value: Any
    ):
        """Handle state change."""
        
    async def on_delete(
        self,
        path: str
    ):
        """Handle state deletion."""
``` 