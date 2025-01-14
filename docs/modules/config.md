# Configuration Module

## Overview

The configuration module provides a flexible and robust system for managing application configurations, with support for multiple sources, validation, environment variable substitution, and dynamic loading.

## Core Components

### ConfigManager

```python
from pepperpy.config import ConfigManager

# Create manager
manager = ConfigManager()

# Add sources
manager.add_source("config.yaml")
manager.add_source("secrets.yaml")
manager.add_source(env_prefix="APP_")

# Load configuration
config = await manager.load()
```

### ConfigBuilder

```python
from pepperpy.config import ConfigBuilder

# Build configuration
builder = ConfigBuilder()
builder.set_defaults({
    "app": {
        "name": "myapp",
        "port": 8000
    }
})
builder.from_env(prefix="APP_")
builder.from_file("config.yaml")

config = builder.build()
```

### ConfigValidator

```python
from pepperpy.config import ConfigValidator

validator = ConfigValidator({
    "app.name": str,
    "app.port": int,
    "db.url": str
})

# Validate configuration
validator.validate(config)
```

## Usage Patterns

### 1. Environment-based Configuration

```python
from pepperpy.config import EnvConfig

class AppConfig(EnvConfig):
    def __init__(self):
        super().__init__(prefix="APP_")
        
        # Define defaults
        self.defaults = {
            "debug": False,
            "port": 8000,
            "host": "localhost"
        }
    
    def load(self):
        config = super().load()
        
        # Add computed values
        config["url"] = f"http://{config['host']}:{config['port']}"
        
        return config
```

### 2. Dynamic Configuration

```python
from pepperpy.config import DynamicConfig

class ServiceConfig(DynamicConfig):
    def __init__(self):
        super().__init__()
        self.watchers = []
    
    def add_watcher(self, callback):
        self.watchers.append(callback)
    
    async def update(self, changes):
        # Apply changes
        self.config.update(changes)
        
        # Notify watchers
        for watcher in self.watchers:
            await watcher(changes)
```

### 3. Secure Configuration

```python
from pepperpy.config import SecureConfig

class SecretsConfig(SecureConfig):
    def __init__(self):
        super().__init__(
            encryption_key=os.environ["SECRET_KEY"]
        )
    
    def decrypt_value(self, value: str) -> str:
        if self.is_encrypted(value):
            return self.decrypt(value)
        return value
```

## Best Practices

1. **Sources**
   - Use multiple sources
   - Define clear hierarchy
   - Handle conflicts
   - Document sources

2. **Validation**
   - Validate all inputs
   - Use schemas
   - Check types
   - Verify constraints

3. **Security**
   - Encrypt sensitive data
   - Use environment variables
   - Separate secrets
   - Control access

4. **Maintenance**
   - Keep documentation updated
   - Monitor changes
   - Audit access
   - Backup configs

## Common Patterns

### 1. Complete Configuration System

```python
from pepperpy.config import (
    ConfigManager,
    ConfigValidator,
    ConfigWatcher
)

class ApplicationConfig:
    def __init__(self):
        self.manager = ConfigManager()
        self.validator = ConfigValidator()
        self.watcher = ConfigWatcher()
    
    async def initialize(self):
        # Add sources
        self.manager.add_source(
            "config/default.yaml",
            required=True
        )
        self.manager.add_source(
            f"config/{env}.yaml",
            required=False
        )
        self.manager.add_source(
            env_prefix="APP_"
        )
        
        # Add validation
        self.validator.add_schema({
            "app.name": str,
            "app.port": int,
            "db.url": str,
            "redis.url": str
        })
        
        # Load config
        config = await self.manager.load()
        
        # Validate
        self.validator.validate(config)
        
        # Watch for changes
        self.watcher.watch(config, self.on_change)
        
        return config
    
    async def on_change(self, changes):
        # Validate changes
        self.validator.validate_changes(changes)
        
        # Apply changes
        await self.apply_changes(changes)
        
        # Notify services
        await self.notify_services(changes)
```

### 2. Service Configuration

```python
from pepperpy.config import ServiceConfig

class DatabaseConfig(ServiceConfig):
    def __init__(self):
        super().__init__(name="database")
        
        # Define schema
        self.schema = {
            "url": str,
            "pool_size": int,
            "timeout": float
        }
        
        # Set defaults
        self.defaults = {
            "pool_size": 10,
            "timeout": 30.0
        }
    
    def validate(self, config):
        # Validate schema
        super().validate(config)
        
        # Custom validation
        if config["pool_size"] < 1:
            raise ValueError("Pool size must be positive")
        
        if config["timeout"] <= 0:
            raise ValueError("Timeout must be positive")
    
    async def apply(self, config):
        # Apply configuration
        await self.database.configure(
            url=config["url"],
            pool_size=config["pool_size"],
            timeout=config["timeout"]
        )
```

## API Reference

### ConfigManager

```python
class ConfigManager:
    def add_source(
        self,
        source: str | dict,
        required: bool = True
    ):
        """Add configuration source."""
        
    async def load(self) -> dict:
        """Load configuration from all sources."""
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
```

### ConfigValidator

```python
class ConfigValidator:
    def add_schema(self, schema: dict):
        """Add validation schema."""
        
    def validate(self, config: dict):
        """Validate configuration."""
        
    def validate_changes(self, changes: dict):
        """Validate configuration changes."""
```

### ConfigWatcher

```python
class ConfigWatcher:
    def watch(
        self,
        config: dict,
        callback: callable
    ):
        """Watch for configuration changes."""
        
    def notify(self, changes: dict):
        """Notify watchers of changes."""
```
``` 