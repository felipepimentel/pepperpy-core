# Plugin Module

## Overview

The plugin module provides a flexible and extensible system for adding plugins to your application. It supports dynamic loading, dependency management, lifecycle hooks, and plugin configuration.

## Key Components

### PluginManager

```python
from pepperpy_core.plugin import (
    PluginManager,
    PluginConfig,
    Plugin
)

# Create manager
manager = PluginManager(
    config=PluginConfig(
        plugin_dir="plugins",
        auto_load=True,
        hot_reload=True
    )
)

# Initialize plugins
await manager.initialize()

# Get plugin
auth_plugin = await manager.get("auth")
```

### Plugin

```python
from pepperpy_core.plugin import (
    Plugin,
    PluginMeta,
    hook
)

@plugin(
    name="auth",
    version="1.0.0",
    description="Authentication plugin"
)
class AuthPlugin(Plugin):
    def __init__(self, config: dict):
        self.config = config
    
    async def initialize(self):
        await self.setup_auth()
    
    @hook("user.login")
    async def on_login(self, user: dict):
        await self.log_login(user)
    
    @hook("user.logout")
    async def on_logout(self, user: dict):
        await self.log_logout(user)
```

### PluginLoader

```python
from pepperpy_core.plugin import (
    PluginLoader,
    LoaderConfig
)

# Create loader
loader = PluginLoader(
    config=LoaderConfig(
        paths=["plugins", "ext/plugins"],
        patterns=["*.py", "*/plugin.py"]
    )
)

# Load plugins
plugins = await loader.load_plugins()
```

## Usage Patterns

### 1. Plugin Development

```python
from pepperpy_core.plugin import (
    Plugin,
    hook,
    inject
)

class DatabasePlugin(Plugin):
    name = "database"
    version = "1.0.0"
    
    # Dependencies
    config = inject("config")
    cache = inject("cache")
    
    async def initialize(self):
        # Setup database
        self.db = await self.setup_database(
            self.config.get("database")
        )
        
        # Register models
        await self.register_models()
        
        # Setup migrations
        await self.setup_migrations()
    
    async def cleanup(self):
        # Close connections
        await self.db.close()
        
        # Clear cache
        await self.cache.clear()
    
    @hook("app.startup")
    async def on_startup(self):
        # Run migrations
        await self.db.migrate()
        
        # Warm up cache
        await self.cache.warmup()
    
    @hook("app.shutdown")
    async def on_shutdown(self):
        # Flush data
        await self.db.flush()
        
        # Clear cache
        await self.cache.clear()
```

### 2. Plugin Management

```python
from pepperpy_core.plugin import (
    PluginManager,
    PluginState
)

class ApplicationPlugins:
    def __init__(self):
        self.manager = PluginManager()
    
    async def initialize(self):
        # Load plugin configs
        configs = await self.load_configs()
        
        # Register plugins
        for config in configs:
            await self.register_plugin(config)
        
        # Start plugins
        await self.start_plugins()
    
    async def register_plugin(self, config: dict):
        try:
            # Create plugin
            plugin = await self.manager.create_plugin(
                name=config["name"],
                config=config
            )
            
            # Register plugin
            await self.manager.register(plugin)
            
        except Exception as e:
            await self.handle_plugin_error(
                "registration",
                config["name"],
                e
            )
    
    async def start_plugins(self):
        # Start in dependency order
        for plugin in self.manager.get_ordered():
            try:
                # Initialize plugin
                await plugin.initialize()
                
                # Register hooks
                await self.register_hooks(plugin)
                
            except Exception as e:
                await self.handle_plugin_error(
                    "initialization",
                    plugin.name,
                    e
                )
    
    async def register_hooks(self, plugin):
        for hook in plugin.get_hooks():
            self.manager.register_hook(
                event=hook.event,
                callback=hook.callback,
                priority=hook.priority
            )
```

### 3. Plugin Events

```python
from pepperpy_core.plugin import (
    PluginEvents,
    EventContext
)

class ApplicationEvents:
    def __init__(self):
        self.events = PluginEvents()
    
    async def initialize(self):
        # Register core events
        self.register_core_events()
        
        # Register plugin events
        await self.register_plugin_events()
    
    def register_core_events(self):
        # App events
        self.events.register("app.startup")
        self.events.register("app.shutdown")
        
        # User events
        self.events.register("user.login")
        self.events.register("user.logout")
        
        # Data events
        self.events.register("data.created")
        self.events.register("data.updated")
        self.events.register("data.deleted")
    
    async def emit_event(
        self,
        event: str,
        data: dict | None = None,
        context: dict | None = None
    ):
        # Create context
        ctx = EventContext(
            event=event,
            data=data,
            context=context
        )
        
        # Emit event
        results = await self.events.emit(
            event,
            ctx
        )
        
        # Handle results
        await self.handle_event_results(
            event,
            results
        )
```

## Best Practices

### 1. Plugin Structure

```python
from pepperpy_core.plugin import (
    Plugin,
    PluginConfig
)

class PluginStructure:
    def configure(self):
        return PluginConfig(
            # Basic info
            name="my-plugin",
            version="1.0.0",
            description="My plugin description",
            
            # Dependencies
            requires=[
                "database",
                "cache"
            ],
            
            # Hooks
            hooks=[
                "app.startup",
                "app.shutdown"
            ],
            
            # Settings
            settings={
                "enabled": True,
                "debug": False,
                "timeout": 30
            }
        )
    
    def create_plugin(self):
        class MyPlugin(Plugin):
            # Metadata
            name = "my-plugin"
            version = "1.0.0"
            
            # Dependencies
            database = inject("database")
            cache = inject("cache")
            
            async def initialize(self):
                # Setup plugin
                await self.setup()
                
                # Register hooks
                await self.register_hooks()
            
            async def cleanup(self):
                # Cleanup resources
                await self.cleanup_resources()
            
            @hook("app.startup")
            async def on_startup(self):
                # Handle startup
                await self.handle_startup()
            
            @hook("app.shutdown")
            async def on_shutdown(self):
                # Handle shutdown
                await self.handle_shutdown()
        
        return MyPlugin
```

### 2. Plugin Loading

```python
from pepperpy_core.plugin import (
    PluginLoader,
    LoaderConfig
)

class PluginLoading:
    def __init__(self):
        self.loader = PluginLoader()
    
    def configure(self):
        return LoaderConfig(
            # Paths
            paths=[
                "plugins",
                "ext/plugins"
            ],
            
            # Patterns
            patterns=[
                "*.py",
                "*/plugin.py"
            ],
            
            # Loading
            recursive=True,
            follow_links=False,
            
            # Validation
            validate=True,
            strict=True
        )
    
    async def load_plugins(self):
        try:
            # Discover plugins
            plugins = await self.loader.discover()
            
            # Load plugins
            loaded = await self.loader.load_all(
                plugins
            )
            
            # Validate plugins
            valid = await self.validate_plugins(
                loaded
            )
            
            return valid
            
        except Exception as e:
            await self.handle_load_error(e)
            raise
```

### 3. Plugin Hooks

```python
from pepperpy_core.plugin import (
    PluginHooks,
    HookConfig
)

class PluginHooks:
    def __init__(self):
        self.hooks = PluginHooks()
    
    def configure(self):
        return HookConfig(
            # Event types
            types={
                "app": ["startup", "shutdown"],
                "user": ["login", "logout"],
                "data": ["created", "updated", "deleted"]
            },
            
            # Priorities
            priorities={
                "high": 100,
                "normal": 50,
                "low": 0
            },
            
            # Execution
            parallel=True,
            timeout=30,
            
            # Error handling
            ignore_errors=False,
            retry_count=3
        )
    
    async def register_hook(
        self,
        event: str,
        callback: callable,
        **options
    ):
        # Validate hook
        await self.validate_hook(
            event,
            callback
        )
        
        # Register hook
        self.hooks.register(
            event=event,
            callback=callback,
            priority=options.get("priority", "normal"),
            parallel=options.get("parallel", True)
        )
    
    async def execute_hooks(
        self,
        event: str,
        context: dict
    ):
        try:
            # Get hooks
            hooks = self.hooks.get_hooks(event)
            
            # Execute hooks
            results = await self.hooks.execute(
                hooks,
                context
            )
            
            # Process results
            await self.process_results(
                event,
                results
            )
            
        except Exception as e:
            await self.handle_hook_error(
                event,
                e
            )
```

## Complete Examples

### 1. Authentication Plugin

```python
from pepperpy_core.plugin import (
    Plugin,
    hook,
    inject
)

class AuthPlugin(Plugin):
    # Metadata
    name = "auth"
    version = "1.0.0"
    description = "Authentication plugin"
    
    # Dependencies
    database = inject("database")
    cache = inject("cache")
    config = inject("config")
    
    async def initialize(self):
        # Load config
        self.settings = self.config.get("auth")
        
        # Setup providers
        self.providers = {
            "jwt": JWTProvider(self.settings),
            "oauth": OAuthProvider(self.settings),
            "basic": BasicAuthProvider(self.settings)
        }
        
        # Initialize providers
        for provider in self.providers.values():
            await provider.initialize()
    
    async def cleanup(self):
        # Cleanup providers
        for provider in self.providers.values():
            await provider.cleanup()
    
    @hook("http.request")
    async def authenticate_request(self, request):
        # Get auth header
        auth = request.headers.get("Authorization")
        if not auth:
            return None
        
        # Parse scheme
        scheme, token = auth.split(" ", 1)
        provider = self.providers.get(scheme.lower())
        
        if not provider:
            raise AuthError(f"Unknown scheme: {scheme}")
        
        # Authenticate
        return await provider.authenticate(token)
    
    @hook("user.login")
    async def on_login(self, user: dict):
        # Generate token
        token = await self.generate_token(user)
        
        # Cache token
        await self.cache.set(
            f"token:{user['id']}",
            token,
            ttl=self.settings["token_ttl"]
        )
        
        # Log event
        await self.log_login(user)
    
    @hook("user.logout")
    async def on_logout(self, user: dict):
        # Revoke token
        await self.cache.delete(
            f"token:{user['id']}"
        )
        
        # Log event
        await self.log_logout(user)
    
    async def generate_token(self, user: dict):
        # Create payload
        payload = {
            "sub": user["id"],
            "name": user["name"],
            "roles": user["roles"],
            "exp": time.time() + self.settings["token_ttl"]
        }
        
        # Sign token
        return await self.providers["jwt"].sign(
            payload
        )
    
    async def verify_token(self, token: str):
        try:
            # Verify signature
            payload = await self.providers["jwt"].verify(
                token
            )
            
            # Check expiration
            if payload["exp"] < time.time():
                raise AuthError("Token expired")
            
            # Get user
            user = await self.get_user(
                payload["sub"]
            )
            
            return user
            
        except Exception as e:
            raise AuthError(f"Invalid token: {e}")
    
    async def get_user(self, user_id: str):
        # Check cache
        user = await self.cache.get(
            f"user:{user_id}"
        )
        
        if not user:
            # Get from database
            user = await self.database.get_user(
                user_id
            )
            
            if user:
                # Cache user
                await self.cache.set(
                    f"user:{user_id}",
                    user,
                    ttl=300
                )
        
        return user
```

### 2. Database Plugin

```python
from pepperpy_core.plugin import (
    Plugin,
    hook,
    inject
)

class DatabasePlugin(Plugin):
    # Metadata
    name = "database"
    version = "1.0.0"
    description = "Database plugin"
    
    # Dependencies
    config = inject("config")
    
    async def initialize(self):
        # Load config
        self.settings = self.config.get("database")
        
        # Create pool
        self.pool = await self.create_pool(
            self.settings
        )
        
        # Setup models
        self.models = await self.setup_models()
        
        # Run migrations
        if self.settings.get("auto_migrate"):
            await self.run_migrations()
    
    async def cleanup(self):
        # Close pool
        await self.pool.close()
    
    @hook("app.startup")
    async def on_startup(self):
        # Check connection
        await self.check_connection()
        
        # Initialize tables
        await self.initialize_tables()
    
    @hook("app.shutdown")
    async def on_shutdown(self):
        # Close connections
        await self.close_connections()
    
    async def create_pool(self, settings: dict):
        return await create_pool(
            host=settings["host"],
            port=settings["port"],
            user=settings["user"],
            password=settings["password"],
            database=settings["database"],
            min_size=settings["pool_min_size"],
            max_size=settings["pool_max_size"]
        )
    
    async def get_connection(self):
        return await self.pool.acquire()
    
    async def release_connection(self, conn):
        await self.pool.release(conn)
    
    async def execute(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.execute(
                query,
                *args
            )
    
    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                query,
                *args
            )
    
    async def fetchrow(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                query,
                *args
            )
```

### Resource Plugin

```python
from pepperpy_core.plugin import ResourcePlugin, ResourcePluginConfig

# Create plugin with custom config
plugin = ResourcePlugin(
    config=ResourcePluginConfig(
        name="resource_manager",
        resource_dir="resources"
    )
)

# Initialize plugin
await plugin.initialize()

# Create a resource
resource = await plugin.create_resource(
    name="config",
    path="config.yaml",
    metadata={"type": "yaml", "version": "1.0"}
)

# Get resource
resource = await plugin.get_resource("config")

# List all resources
resources = await plugin.list_resources()

# Update resource metadata
updated = await plugin.update_resource(
    name="config",
    metadata={"version": "1.1"}
)

# Delete resource
await plugin.delete_resource("config")

# Cleanup
await plugin.cleanup()
```

The ResourcePlugin provides RESTful-like resource management capabilities:

- **create_resource**: Create a new resource with metadata
- **get_resource**: Retrieve a resource by name
- **list_resources**: List all available resources
- **update_resource**: Update resource metadata
- **delete_resource**: Remove a resource

The plugin integrates with the core ResourceManager and provides async operations with proper error handling.
``` 