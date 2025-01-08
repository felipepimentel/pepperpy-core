# Resources Module

## Overview

The resources module provides a robust system for managing application resources such as files, configurations, templates, and assets. It supports loading, caching, validation, and lifecycle management of resources.

## Key Components

### ResourceManager

```python
from pepperpy_core.resources import (
    ResourceManager,
    ResourceConfig
)

# Create manager
manager = ResourceManager(
    config=ResourceConfig(
        base_path="resources",
        cache_enabled=True,
        validate=True
    )
)

# Initialize manager
await manager.initialize()
```

### Resource Loading

```python
from pepperpy_core.resources import (
    ResourceLoader,
    LoaderConfig
)

# Create loader
loader = ResourceLoader(
    config=LoaderConfig(
        formats=["yaml", "json"],
        encoding="utf-8"
    )
)

# Load resource
config = await loader.load(
    path="config/app.yaml"
)
```

### Resource Validation

```python
from pepperpy_core.resources import (
    ResourceValidator,
    ValidationConfig
)

# Create validator
validator = ResourceValidator(
    config=ValidationConfig(
        schema_path="schemas",
        strict=True
    )
)

# Validate resource
valid = await validator.validate(
    resource=config,
    schema="config.schema.json"
)
```

## Usage Patterns

### 1. Configuration Management

```python
from pepperpy_core.resources import (
    ConfigManager,
    ConfigFormat
)

class ApplicationConfig:
    def __init__(self):
        self.manager = ConfigManager(
            base_path="config",
            default_format=ConfigFormat.YAML
        )
    
    async def load_configs(self):
        # Load app config
        self.app_config = await self.manager.load(
            "app.yaml"
        )
        
        # Load database config
        self.db_config = await self.manager.load(
            "database.yaml"
        )
        
        # Load service configs
        self.service_configs = await self.manager.load_dir(
            "services/*.yaml"
        )
    
    async def get_config(
        self,
        path: str,
        required: bool = True
    ):
        try:
            # Get config
            config = await self.manager.get(path)
            
            if not config and required:
                raise ConfigError(
                    f"Required config not found: {path}"
                )
            
            return config
            
        except Exception as e:
            raise ResourceError(
                f"Failed to get config: {e}"
            )
    
    async def validate_configs(self):
        try:
            # Validate all configs
            await self.manager.validate_all()
            
        except Exception as e:
            raise ConfigError(
                f"Config validation failed: {e}"
            )
```

### 2. Template Management

```python
from pepperpy_core.resources import (
    TemplateManager,
    TemplateConfig
)

class ApplicationTemplates:
    def __init__(self):
        self.manager = TemplateManager(
            config=TemplateConfig(
                path="templates",
                cache_size=100
            )
        )
    
    async def initialize(self):
        # Load templates
        await self.manager.load_templates()
        
        # Register filters
        self.register_filters()
        
        # Register functions
        self.register_functions()
    
    def register_filters(self):
        # Add custom filters
        self.manager.add_filter(
            "datetime",
            self.format_datetime
        )
        
        self.manager.add_filter(
            "currency",
            self.format_currency
        )
    
    def register_functions(self):
        # Add custom functions
        self.manager.add_function(
            "url_for",
            self.generate_url
        )
        
        self.manager.add_function(
            "static_url",
            self.generate_static_url
        )
    
    async def render_template(
        self,
        name: str,
        context: dict
    ):
        try:
            # Get template
            template = await self.manager.get_template(
                name
            )
            
            # Render template
            result = await template.render(
                context
            )
            
            return result
            
        except Exception as e:
            raise TemplateError(
                f"Template render failed: {e}"
            )
```

### 3. Asset Management

```python
from pepperpy_core.resources import (
    AssetManager,
    AssetConfig
)

class ApplicationAssets:
    def __init__(self):
        self.manager = AssetManager(
            config=AssetConfig(
                path="static",
                url_prefix="/static",
                cache=True
            )
        )
    
    async def initialize(self):
        # Load assets
        await self.manager.load_assets()
        
        # Build manifest
        await self.manager.build_manifest()
        
        # Start serving
        await self.manager.start_server()
    
    async def get_asset_url(
        self,
        path: str
    ):
        try:
            # Get asset
            asset = await self.manager.get_asset(
                path
            )
            
            if not asset:
                raise AssetError(
                    f"Asset not found: {path}"
                )
            
            # Get URL
            return await self.manager.get_url(
                asset
            )
            
        except Exception as e:
            raise ResourceError(
                f"Failed to get asset URL: {e}"
            )
    
    async def process_assets(self):
        try:
            # Process all assets
            await self.manager.process_all(
                minify=True,
                compress=True
            )
            
        except Exception as e:
            raise AssetError(
                f"Asset processing failed: {e}"
            )
```

## Best Practices

### 1. Resource Configuration

```python
from pepperpy_core.resources import (
    ResourceConfig,
    CacheConfig
)

class ResourceSetup:
    def configure(self):
        return ResourceConfig(
            # Basic settings
            base_path="resources",
            encoding="utf-8",
            
            # Loading
            formats={
                "yaml": {
                    "loader": "yaml.safe_load",
                    "dumper": "yaml.safe_dump"
                },
                "json": {
                    "loader": "json.loads",
                    "dumper": "json.dumps"
                }
            },
            
            # Validation
            validation={
                "enabled": True,
                "schema_path": "schemas",
                "strict": True
            },
            
            # Caching
            cache=CacheConfig(
                enabled=True,
                backend="memory",
                max_size=1000,
                ttl=3600
            )
        )
```

### 2. Loading Configuration

```python
from pepperpy_core.resources import (
    LoaderConfig,
    LoaderHooks
)

class LoaderSetup:
    def configure(self):
        return LoaderConfig(
            # Basic settings
            encoding="utf-8",
            recursive=True,
            
            # Formats
            formats=[
                "yaml",
                "json",
                "toml"
            ],
            
            # Processing
            processing={
                "interpolate": True,
                "validate": True
            },
            
            # Hooks
            hooks=LoaderHooks(
                before_load=self.before_load,
                after_load=self.after_load,
                on_error=self.on_error
            )
        )
```

### 3. Validation Configuration

```python
from pepperpy_core.resources import (
    ValidationConfig,
    SchemaConfig
)

class ValidationSetup:
    def configure(self):
        return ValidationConfig(
            # Basic settings
            enabled=True,
            strict=True,
            
            # Schemas
            schemas=SchemaConfig(
                path="schemas",
                format="json",
                cache=True
            ),
            
            # Rules
            rules={
                "config": {
                    "required": True,
                    "type": "object"
                },
                "template": {
                    "required": False,
                    "type": "string"
                }
            },
            
            # Custom
            custom_validators={
                "email": self.validate_email,
                "url": self.validate_url
            }
        )
```

## Complete Examples

### 1. Configuration System

```python
from pepperpy_core.resources import (
    ConfigSystem,
    ConfigFormat,
    ConfigValidator
)

class ApplicationConfig:
    def __init__(self):
        self.system = ConfigSystem(
            base_path="config"
        )
        
        self.validator = ConfigValidator(
            schema_path="schemas"
        )
    
    async def initialize(self):
        # Load configurations
        await self.load_configs()
        
        # Validate configurations
        await self.validate_configs()
        
        # Process configurations
        await self.process_configs()
    
    async def load_configs(self):
        try:
            # Load app config
            self.app_config = await self.system.load(
                "app.yaml",
                format=ConfigFormat.YAML
            )
            
            # Load database config
            self.db_config = await self.system.load(
                "database.yaml",
                format=ConfigFormat.YAML
            )
            
            # Load service configs
            self.service_configs = await self.system.load_dir(
                "services",
                pattern="*.yaml",
                format=ConfigFormat.YAML
            )
            
        except Exception as e:
            raise ConfigError(
                f"Config loading failed: {e}"
            )
    
    async def validate_configs(self):
        try:
            # Validate app config
            await self.validator.validate(
                self.app_config,
                schema="app.schema.json"
            )
            
            # Validate database config
            await self.validator.validate(
                self.db_config,
                schema="database.schema.json"
            )
            
            # Validate service configs
            for config in self.service_configs:
                await self.validator.validate(
                    config,
                    schema="service.schema.json"
                )
                
        except Exception as e:
            raise ConfigError(
                f"Config validation failed: {e}"
            )
    
    async def process_configs(self):
        try:
            # Process app config
            self.app_config = await self.system.process(
                self.app_config,
                interpolate=True
            )
            
            # Process database config
            self.db_config = await self.system.process(
                self.db_config,
                interpolate=True
            )
            
            # Process service configs
            self.service_configs = await self.system.process_all(
                self.service_configs,
                interpolate=True
            )
            
        except Exception as e:
            raise ConfigError(
                f"Config processing failed: {e}"
            )
```

### 2. Template System

```python
from pepperpy_core.resources import (
    TemplateSystem,
    TemplateLoader,
    TemplateCache
)

class ApplicationTemplates:
    def __init__(self):
        self.system = TemplateSystem(
            path="templates"
        )
        
        self.loader = TemplateLoader(
            encoding="utf-8"
        )
        
        self.cache = TemplateCache(
            max_size=100
        )
    
    async def initialize(self):
        # Load templates
        await self.load_templates()
        
        # Register extensions
        self.register_extensions()
        
        # Register filters
        self.register_filters()
    
    async def load_templates(self):
        try:
            # Load all templates
            templates = await self.loader.load_dir(
                "templates",
                pattern="*.html"
            )
            
            # Cache templates
            for name, template in templates.items():
                await self.cache.set(
                    name,
                    template
                )
                
        except Exception as e:
            raise TemplateError(
                f"Template loading failed: {e}"
            )
    
    def register_extensions(self):
        # Add extensions
        self.system.add_extension(
            "jinja2.ext.do"
        )
        
        self.system.add_extension(
            "jinja2.ext.loopcontrols"
        )
    
    def register_filters(self):
        # Add filters
        self.system.add_filter(
            "datetime",
            self.format_datetime
        )
        
        self.system.add_filter(
            "markdown",
            self.render_markdown
        )
    
    async def render(
        self,
        template: str,
        context: dict
    ):
        try:
            # Get from cache
            template = await self.cache.get(
                template
            )
            
            if not template:
                # Load template
                template = await self.loader.load(
                    template
                )
                
                # Cache template
                await self.cache.set(
                    template.name,
                    template
                )
            
            # Render template
            result = await template.render(
                context
            )
            
            return result
            
        except Exception as e:
            raise TemplateError(
                f"Template render failed: {e}"
            )
```
``` 