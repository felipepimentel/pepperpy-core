# Registry Module

## Overview

The registry module provides a centralized component registry system for managing application dependencies, services, and configurations. It supports dependency injection, lazy loading, and lifecycle management.

## Key Components

### Registry

```python
from pepperpy.registry import (
    Registry,
    RegistryConfig
)

# Create registry
registry = Registry(
    config=RegistryConfig(
        name="app",
        auto_load=True,
        strict=True
    )
)

# Initialize registry
await registry.initialize()
```

### Component Registration

```python
from pepperpy.registry import (
    Component,
    Dependency,
    Lifecycle
)

@component
class Database:
    def __init__(self, config: dict):
        self.config = config
        self.pool = None
    
    async def initialize(self):
        self.pool = await create_pool(
            self.config
        )
    
    async def cleanup(self):
        await self.pool.close()

# Register component
registry.register(
    name="database",
    component=Database,
    config=db_config
)
```

### Dependency Injection

```python
from pepperpy.registry import (
    inject,
    provides
)

@component
class UserService:
    # Inject dependencies
    database = inject("database")
    cache = inject("cache")
    
    @provides("users")
    async def get_users(self):
        # Get from cache
        users = await self.cache.get("users")
        if users:
            return users
        
        # Get from database
        users = await self.database.get_users()
        
        # Cache results
        await self.cache.set(
            "users",
            users,
            ttl=300
        )
        
        return users
```

## Usage Patterns

### 1. Component Management

```python
from pepperpy.registry import (
    ComponentManager,
    ManagerConfig
)

class ApplicationComponents:
    def __init__(self):
        self.manager = ComponentManager(
            config=ManagerConfig(
                auto_start=True,
                strict=True
            )
        )
    
    async def initialize(self):
        # Register core components
        await self.register_core()
        
        # Register services
        await self.register_services()
        
        # Start components
        await self.start_components()
    
    async def register_core(self):
        # Register database
        await self.manager.register(
            name="database",
            component=Database,
            config=db_config,
            required=True
        )
        
        # Register cache
        await self.manager.register(
            name="cache",
            component=Cache,
            config=cache_config,
            required=True
        )
        
        # Register queue
        await self.manager.register(
            name="queue",
            component=Queue,
            config=queue_config,
            required=False
        )
    
    async def register_services(self):
        # Register user service
        await self.manager.register(
            name="users",
            component=UserService,
            depends=["database", "cache"]
        )
        
        # Register auth service
        await self.manager.register(
            name="auth",
            component=AuthService,
            depends=["users", "cache"]
        )
    
    async def start_components(self):
        try:
            # Start in order
            await self.manager.start_all()
            
        except Exception as e:
            # Handle startup error
            await self.handle_startup_error(e)
            raise
```

### 2. Dependency Resolution

```python
from pepperpy.registry import (
    DependencyResolver,
    ResolverConfig
)

class ServiceDependencies:
    def __init__(self):
        self.resolver = DependencyResolver(
            config=ResolverConfig(
                strict=True,
                max_depth=10
            )
        )
    
    async def resolve_dependencies(
        self,
        service: str
    ):
        try:
            # Get dependencies
            deps = await self.resolver.resolve(
                service
            )
            
            # Check circular
            if await self.resolver.has_circular(
                deps
            ):
                raise DependencyError(
                    "Circular dependency detected"
                )
            
            # Order dependencies
            ordered = await self.resolver.order(
                deps
            )
            
            return ordered
            
        except Exception as e:
            raise DependencyError(
                f"Resolution failed: {e}"
            )
    
    async def validate_dependencies(
        self,
        service: str
    ):
        try:
            # Get dependencies
            deps = await self.resolver.resolve(
                service
            )
            
            # Validate each
            for dep in deps:
                await self.validate_dependency(dep)
            
        except Exception as e:
            raise DependencyError(
                f"Validation failed: {e}"
            )
```

### 3. Lifecycle Management

```python
from pepperpy.registry import (
    LifecycleManager,
    LifecycleConfig
)

class ComponentLifecycle:
    def __init__(self):
        self.lifecycle = LifecycleManager(
            config=LifecycleConfig(
                timeout=30,
                retry_count=3
            )
        )
    
    async def start_component(
        self,
        name: str,
        component: object
    ):
        try:
            # Initialize
            await self.lifecycle.initialize(
                name,
                component
            )
            
            # Start
            await self.lifecycle.start(
                name,
                component
            )
            
        except Exception as e:
            await self.handle_lifecycle_error(
                "start",
                name,
                e
            )
    
    async def stop_component(
        self,
        name: str,
        component: object
    ):
        try:
            # Stop
            await self.lifecycle.stop(
                name,
                component
            )
            
            # Cleanup
            await self.lifecycle.cleanup(
                name,
                component
            )
            
        except Exception as e:
            await self.handle_lifecycle_error(
                "stop",
                name,
                e
            )
```

## Best Practices

### 1. Component Configuration

```python
from pepperpy.registry import (
    ComponentConfig,
    LifecycleConfig
)

class ComponentSetup:
    def configure(self):
        return ComponentConfig(
            # Basic info
            name="database",
            version="1.0.0",
            description="Database component",
            
            # Dependencies
            requires=[
                "config",
                "metrics"
            ],
            
            # Lifecycle
            lifecycle=LifecycleConfig(
                startup_timeout=30,
                shutdown_timeout=30,
                retry_count=3
            ),
            
            # Settings
            settings={
                "pool_size": 10,
                "timeout": 30,
                "retry": True
            }
        )
```

### 2. Dependency Configuration

```python
from pepperpy.registry import (
    DependencyConfig,
    InjectionConfig
)

class DependencySetup:
    def configure(self):
        return DependencyConfig(
            # Resolution
            resolution={
                "strict": True,
                "max_depth": 10,
                "allow_circular": False
            },
            
            # Injection
            injection=InjectionConfig(
                mode="constructor",
                lazy=True,
                optional=False
            ),
            
            # Validation
            validation={
                "check_types": True,
                "check_interfaces": True
            }
        )
```

### 3. Registry Configuration

```python
from pepperpy.registry import (
    RegistryConfig,
    StorageConfig
)

class RegistrySetup:
    def configure(self):
        return RegistryConfig(
            # Basic settings
            name="app",
            version="1.0.0",
            
            # Components
            components={
                "database": {
                    "required": True,
                    "startup_order": 0
                },
                "cache": {
                    "required": True,
                    "startup_order": 1
                },
                "services": {
                    "required": False,
                    "startup_order": 2
                }
            },
            
            # Storage
            storage=StorageConfig(
                type="memory",
                persistence=False
            ),
            
            # Lifecycle
            lifecycle={
                "startup_timeout": 60,
                "shutdown_timeout": 30
            }
        )
```

## Complete Examples

### 1. Application Registry

```python
from pepperpy.registry import (
    Registry,
    Component,
    inject
)

class Application:
    def __init__(self):
        self.registry = Registry(
            name="app"
        )
    
    async def initialize(self):
        # Register components
        await self.register_components()
        
        # Start registry
        await self.registry.start()
    
    async def register_components(self):
        # Register database
        await self.registry.register(
            "database",
            Database(db_config)
        )
        
        # Register cache
        await self.registry.register(
            "cache",
            Cache(cache_config)
        )
        
        # Register services
        await self.registry.register(
            "users",
            UserService()
        )
        
        await self.registry.register(
            "auth",
            AuthService()
        )
    
    async def get_component(
        self,
        name: str
    ):
        try:
            # Get component
            component = await self.registry.get(
                name
            )
            
            if not component:
                raise ComponentError(
                    f"Component not found: {name}"
                )
            
            return component
            
        except Exception as e:
            raise RegistryError(
                f"Failed to get component: {e}"
            )
    
    async def cleanup(self):
        try:
            # Stop registry
            await self.registry.stop()
            
            # Cleanup components
            await self.registry.cleanup()
            
        except Exception as e:
            raise RegistryError(
                f"Cleanup failed: {e}"
            )
```

### 2. Service Registry

```python
from pepperpy.registry import (
    ServiceRegistry,
    Service,
    inject
)

class ServiceManager:
    def __init__(self):
        self.registry = ServiceRegistry(
            name="services"
        )
    
    async def initialize(self):
        # Register services
        await self.register_services()
        
        # Start registry
        await self.registry.start()
    
    async def register_services(self):
        # User service
        await self.registry.register(
            name="users",
            service=UserService(),
            version="1.0.0",
            metadata={
                "type": "core",
                "critical": True
            }
        )
        
        # Auth service
        await self.registry.register(
            name="auth",
            service=AuthService(),
            version="1.0.0",
            metadata={
                "type": "core",
                "critical": True
            }
        )
        
        # Email service
        await self.registry.register(
            name="email",
            service=EmailService(),
            version="1.0.0",
            metadata={
                "type": "support",
                "critical": False
            }
        )
    
    async def get_service(
        self,
        name: str,
        version: str | None = None
    ):
        try:
            # Get service
            service = await self.registry.get(
                name,
                version=version
            )
            
            if not service:
                raise ServiceError(
                    f"Service not found: {name}"
                )
            
            return service
            
        except Exception as e:
            raise RegistryError(
                f"Failed to get service: {e}"
            )
    
    async def list_services(
        self,
        type: str | None = None,
        critical: bool | None = None
    ):
        try:
            # Build filter
            filters = {}
            if type:
                filters["type"] = type
            if critical is not None:
                filters["critical"] = critical
            
            # Get services
            services = await self.registry.list(
                filters=filters
            )
            
            return services
            
        except Exception as e:
            raise RegistryError(
                f"Failed to list services: {e}"
            )
```
``` 