# Registry System

The Registry system provides a centralized component registry for managing application dependencies, services, and configurations. It implements a type-safe container for protocol implementations, allowing runtime validation and dependency injection.

## Key Features

- Type-safe registration and retrieval
- Protocol-based implementation management
- Automatic instantiation of components
- Runtime protocol validation
- Clean-up functionality for registered components

## Usage

### Basic Registry

```python
from typing import Protocol
from pepperpy import Registry

# Define protocol
class DataStore(Protocol):
    def get(self, key: str) -> Any: ...
    def set(self, key: str, value: Any) -> None: ...

# Create registry
registry = Registry[DataStore](DataStore)

# Register implementation
class MemoryStore(DataStore):
    def __init__(self):
        self._data = {}
    
    def get(self, key: str) -> Any:
        return self._data.get(key)
    
    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

# Register instance
registry.register("memory", MemoryStore())

# Get instance
store = registry.get("memory")
store.set("key", "value")
```

### Component Registration

```python
from dataclasses import dataclass
from pepperpy import Registry, BaseModule, ModuleConfig

@dataclass
class CacheConfig(ModuleConfig):
    capacity: int = 1000

class CacheModule(BaseModule[CacheConfig]):
    async def _setup(self) -> None:
        self._cache = {}
    
    async def _teardown(self) -> None:
        self._cache.clear()

# Register with config
registry = Registry[BaseModule](BaseModule)
config = CacheConfig(name="cache", capacity=5000)
registry.register("cache", CacheModule(config))
```

### Dependency Injection

```python
from typing import Protocol
from pepperpy import Registry

class Logger(Protocol):
    def log(self, message: str) -> None: ...

class Service:
    def __init__(self, logger: Logger):
        self._logger = logger
    
    def do_something(self):
        self._logger.log("Doing something")

# Create registries
logger_registry = Registry[Logger](Logger)
service_registry = Registry[Service](Service)

# Register logger
class ConsoleLogger(Logger):
    def log(self, message: str) -> None:
        print(f"[LOG] {message}")

logger_registry.register("console", ConsoleLogger())

# Register service with dependency
service = Service(logger_registry.get("console"))
service_registry.register("main", service)
```

## Best Practices

### Component Configuration

1. **Naming**: Use descriptive names for registered components
2. **Validation**: Validate components implement required protocols
3. **Lifecycle**: Handle initialization and cleanup properly
4. **Dependencies**: Manage dependencies through registry

### Dependency Configuration

1. **Injection**: Use constructor injection for dependencies
2. **Resolution**: Resolve dependencies at component creation
3. **Validation**: Validate required dependencies exist
4. **Cleanup**: Handle dependency cleanup order

### Registry Configuration

1. **Scope**: Create separate registries for different component types
2. **Access**: Control registry access through dependency injection
3. **Validation**: Enable runtime protocol validation
4. **Cleanup**: Implement proper cleanup for all components

## Integration with Module System

The Registry system works seamlessly with the Module system for managing module implementations:

```python
from pepperpy import Registry, BaseModule

# Create module registry
module_registry = Registry[BaseModule](BaseModule)

# Register modules
module_registry.register("cache", CacheModule(cache_config))
module_registry.register("auth", AuthModule(auth_config))
module_registry.register("storage", StorageModule(storage_config))

# Initialize modules
async def initialize_modules():
    for name in module_registry.list():
        module = module_registry.get(name)
        await module.initialize()

# Cleanup modules
async def cleanup_modules():
    for name in reversed(module_registry.list()):
        module = module_registry.get(name)
        await module.teardown()
```

## Application Registry

Example of using Registry for application-level component management:

```python
from pepperpy import Registry

class Application:
    def __init__(self):
        # Create registries
        self.modules = Registry[BaseModule](BaseModule)
        self.services = Registry[Service](Service)
        self.loggers = Registry[Logger](Logger)
    
    async def initialize(self):
        # Register components
        self._register_modules()
        self._register_services()
        self._register_loggers()
        
        # Initialize modules
        for name in self.modules.list():
            await self.modules.get(name).initialize()
    
    async def cleanup(self):
        # Cleanup in reverse order
        for name in reversed(self.modules.list()):
            await self.modules.get(name).teardown()

# Create application
app = Application()
await app.initialize()
```

## Service Registry

Example of using Registry for service management:

```python
from pepperpy import Registry, Service

class ServiceRegistry:
    def __init__(self):
        self._registry = Registry[Service](Service)
        self._active = set()
    
    def register(self, name: str, service: Service):
        self._registry.register(name, service)
    
    async def start(self, name: str):
        service = self._registry.get(name)
        await service.start()
        self._active.add(name)
    
    async def stop(self, name: str):
        if name in self._active:
            service = self._registry.get(name)
            await service.stop()
            self._active.remove(name)
    
    def is_active(self, name: str) -> bool:
        return name in self._active

# Use service registry
registry = ServiceRegistry()
registry.register("auth", AuthService())
await registry.start("auth")
```

## See Also

- [Module System](module.md) - For creating modular components
- [Plugin System](plugin.md) - For creating plugin modules
``` 