# Module System

The Module system provides the foundation for creating modular components in PepperPy. It implements the Template Method pattern to define a consistent lifecycle for all modules, including initialization, setup, and teardown phases.

## Key Features

- Consistent module lifecycle management
- Type-safe configuration handling
- Proper cleanup and resource management
- Extensible module hierarchy
- Integration with dependency injection

## Usage

### Basic Module

```python
from dataclasses import dataclass
from pepperpy import BaseModule, ModuleConfig

@dataclass
class CacheConfig(ModuleConfig):
    capacity: int = 1000
    ttl: int = 3600

class CacheModule(BaseModule[CacheConfig]):
    async def _setup(self) -> None:
        self._cache = {}
        self._stats = {"hits": 0, "misses": 0}
    
    async def _teardown(self) -> None:
        self._cache.clear()
        self._stats.clear()
    
    def get(self, key: str) -> Any:
        self._ensure_initialized()
        if key in self._cache:
            self._stats["hits"] += 1
            return self._cache[key]
        self._stats["misses"] += 1
        return None
```

### Module Lifecycle

```python
# Create module
config = CacheConfig(name="cache", capacity=5000)
cache = CacheModule(config)

# Initialize module
await cache.initialize()  # Calls _setup()

# Use module
value = cache.get("key")

# Cleanup
await cache.teardown()  # Calls _teardown()
```

### Error Handling

```python
from pepperpy import ModuleError, InitializationError

try:
    await module.initialize()
except InitializationError as e:
    # Handle initialization error
    print(f"Failed to initialize: {e}")

try:
    module.do_something()
except ModuleError as e:
    # Handle module operation error
    print(f"Operation failed: {e}")
```

## Best Practices

1. **Configuration**: Use dataclasses for type-safe configuration
2. **Initialization**: Perform all setup in `_setup()` method
3. **Cleanup**: Release all resources in `_teardown()` method
4. **State Management**: Check initialization state before operations
5. **Error Handling**: Use appropriate exception types

## Integration with Registry

While modules can be used standalone, they can also be registered in a Registry for centralized management:

```python
from pepperpy import Registry, BaseModule

# Create registry for modules
registry = Registry[BaseModule](BaseModule)

# Register modules
registry.register("cache", CacheModule(cache_config))
registry.register("auth", AuthModule(auth_config))

# Get module
cache = registry.get("cache")
await cache.initialize()
```

## Advanced Usage

### Dependency Injection

```python
@dataclass
class ServiceConfig(ModuleConfig):
    cache_module: str = "cache"
    auth_module: str = "auth"

class ServiceModule(BaseModule[ServiceConfig]):
    def __init__(self, config: ServiceConfig, registry: Registry) -> None:
        super().__init__(config)
        self._registry = registry
        self._cache = None
        self._auth = None
    
    async def _setup(self) -> None:
        # Get dependencies
        self._cache = self._registry.get(self.config.cache_module)
        self._auth = self._registry.get(self.config.auth_module)
        
        # Initialize if needed
        if not self._cache.is_initialized:
            await self._cache.initialize()
        if not self._auth.is_initialized:
            await self._auth.initialize()
    
    async def _teardown(self) -> None:
        # Cleanup dependencies
        if self._cache and self._cache.is_initialized:
            await self._cache.teardown()
        if self._auth and self._auth.is_initialized:
            await self._auth.teardown()
```

### Module Composition

```python
class CompositeModule(BaseModule[ModuleConfig]):
    def __init__(self, config: ModuleConfig) -> None:
        super().__init__(config)
        self._submodules: List[BaseModule] = []
    
    def add_module(self, module: BaseModule) -> None:
        self._submodules.append(module)
    
    async def _setup(self) -> None:
        # Initialize all submodules
        for module in self._submodules:
            await module.initialize()
    
    async def _teardown(self) -> None:
        # Cleanup all submodules in reverse order
        for module in reversed(self._submodules):
            await module.teardown()
```

## See Also

- [Registry](registry.md) - For managing module implementations
- [Plugin System](plugin.md) - For creating plugin modules
``` 