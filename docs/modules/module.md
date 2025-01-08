# Module

The PepperPy Core Module provides the base structure for module implementation, with support for initialization, configuration, and lifecycle management.

## Core Components

### BaseModule

Base class for module implementation:

```python
from pepperpy_core.module import BaseModule

class CustomModule(BaseModule):
    async def initialize(self):
        # Module initialization
        await self.setup()
    
    async def cleanup(self):
        # Module cleanup
        await self.teardown()

# Create and initialize module
module = CustomModule()
await module.initialize()
```

### ModuleConfig

Base configuration for modules:

```python
from pepperpy_core.module import ModuleConfig

# Basic configuration
config = ModuleConfig(
    name="custom",
    version="1.0.0",
    dependencies=[]
)
```

### Basic Module

```python
from pepperpy_core.module import Module
from dataclasses import dataclass

@dataclass
class DBConfig:
    host: str
    port: int

class DatabaseModule(Module):
    def __init__(self, config: DBConfig):
        super().__init__()
        self.config = config
        self.connection = None
    
    async def initialize(self):
        # Connect to database
        self.connection = await connect(
            self.config.host,
            self.config.port
        )
    
    async def cleanup(self):
        # Close connection
        if self.connection:
            await self.connection.close()
```

### Module with Resources

```python
from pepperpy_core.module import ResourceModule

class CacheModule(ResourceModule):
    def __init__(self, size: int = 1000):
        super().__init__()
        self.size = size
        self.cache = {}
    
    async def get(self, key: str) -> Any:
        return self.cache.get(key)
    
    async def set(self, key: str, value: Any):
        if len(self.cache) >= self.size:
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = value
```

## Advanced Features

### Module with Dependencies

```python
from pepperpy_core.module import DependentModule

class APIModule(DependentModule):
    def __init__(self, cache: CacheModule):
        super().__init__()
        self.cache = cache
    
    async def initialize(self):
        # Initialize dependencies first
        await self.cache.initialize()
        
        # Initialize this module
        await self.setup_api()
```

### Module with State

```python
from pepperpy_core.module import StateModule
from dataclasses import dataclass

@dataclass
class ModuleState:
    is_active: bool
    last_update: float

class ServiceModule(StateModule[ModuleState]):
    async def initialize(self):
        await self.set_state(ModuleState(
            is_active=True,
            last_update=time.time()
        ))
    
    async def update(self):
        state = await self.get_state()
        await self.set_state(ModuleState(
            is_active=state.is_active,
            last_update=time.time()
        ))
```

## Best Practices

1. **Initialization**
   - Validate configuration
   - Initialize resources
   - Handle errors
   - Log status

2. **Cleanup**
   - Release resources
   - Close connections
   - Clear state
   - Log cleanup

3. **Dependencies**
   - Declare dependencies
   - Handle circular deps
   - Validate versions
   - Monitor health

4. **State**
   - Keep minimal state
   - Use immutable data
   - Handle updates
   - Monitor changes

5. **Resources**
   - Manage lifecycle
   - Handle cleanup
   - Monitor usage
   - Log errors

## Common Patterns

### Module with Retry

```python
from pepperpy_core.module import RetryModule

class NetworkModule(RetryModule):
    def __init__(
        self,
        max_retries: int = 3,
        delay: float = 1.0
    ):
        super().__init__()
        self.max_retries = max_retries
        self.delay = delay
    
    async def initialize(self):
        retries = 0
        while True:
            try:
                await self.connect()
                break
            except ConnectionError as e:
                retries += 1
                if retries >= self.max_retries:
                    raise
                await asyncio.sleep(self.delay)
```

### Module with Cache

```python
from pepperpy_core.module import CachedModule

class DataModule(CachedModule):
    def __init__(self):
        super().__init__()
        self.cache = {}
    
    async def get_data(self, key: str) -> Any:
        # Check cache
        if key in self.cache:
            return self.cache[key]
        
        # Get data
        data = await self.fetch_data(key)
        
        # Update cache
        self.cache[key] = data
        return data
```

### Module with Metrics

```python
from pepperpy_core.module import MetricsModule

class ServiceModule(MetricsModule):
    async def initialize(self):
        # Start timer
        with self.timer("initialize"):
            try:
                await super().initialize()
                self.record_success()
            except Exception as e:
                self.record_failure(str(e))
                raise
```

## API Reference

### BaseModule

```python
class BaseModule:
    async def initialize(self):
        """Initialize module."""
        
    async def cleanup(self):
        """Clean up module."""
        
    async def health_check(self) -> bool:
        """Check module health."""
```

### ModuleConfig

```python
class ModuleConfig:
    def validate(self):
        """Validate configuration."""
        
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        
    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary."""
```

### StateModule

```python
class StateModule[T]:
    async def get_state(self) -> T:
        """Get current state."""
        
    async def set_state(
        self,
        state: T
    ):
        """Set new state."""
        
    async def update_state(
        self,
        updater: Callable[[T], T]
    ):
        """Update state."""
```
``` 