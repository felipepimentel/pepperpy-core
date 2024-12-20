"""Configuration system implementation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Generic, TypeVar

from ..exceptions.base import ConfigError
from ..module import BaseModule, ModuleConfig
from ..validation.base import ValidationLevel, ValidationResult, Validator

class ConfigSource(Enum):
    """Configuration source types."""
    
    DEFAULT = "default"
    ENV = "env"
    FILE = "file"
    OVERRIDE = "override"

@dataclass
class ConfigValue:
    """Configuration value with metadata."""
    
    value: Any
    source: ConfigSource = ConfigSource.DEFAULT
    path: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

class ConfigValidator(Validator[Any]):
    """Configuration validator interface."""
    
    def __init__(self, field_name: str) -> None:
        """Initialize validator.
        
        Args:
            field_name: Configuration field name
        """
        super().__init__(name=f"config_{field_name}")
        self.field_name = field_name

class ConfigLoader(ABC):
    """Configuration loader interface."""
    
    @abstractmethod
    async def load(self, path: str | Path) -> dict[str, ConfigValue]:
        """Load configuration from source.
        
        Args:
            path: Configuration source path
            
        Returns:
            Dictionary of configuration values
            
        Raises:
            ConfigError: If loading fails
        """
        pass
    
    @abstractmethod
    async def supports_reload(self) -> bool:
        """Check if loader supports reloading.
        
        Returns:
            True if reloading is supported
        """
        pass

ConfigChangeHandler = Callable[["Config", str, Any, Any], None]

@dataclass
class Config(ModuleConfig):
    """Base configuration class."""
    
    name: str
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    _values: dict[str, ConfigValue] = field(default_factory=dict, init=False)
    _parent: "Config | None" = field(default=None, init=False)
    _validators: dict[str, ConfigValidator] = field(default_factory=dict, init=False)
    _change_handlers: list[ConfigChangeHandler] = field(default_factory=list, init=False)
    _nested_configs: dict[str, "Config"] = field(default_factory=dict, init=False)
    _loader: ConfigLoader | None = field(default=None, init=False)
    _path: str | Path | None = field(default=None, init=False)
    
    def __post_init__(self) -> None:
        """Initialize configuration."""
        super().__post_init__()
        
        # Initialize values
        for field_info in field(self.__class__):
            if not field_info.name.startswith("_"):
                self._values[field_info.name] = ConfigValue(
                    value=getattr(self, field_info.name),
                )
    
    def set_parent(self, parent: "Config") -> None:
        """Set parent configuration.
        
        Args:
            parent: Parent configuration
        """
        self._parent = parent
    
    def add_validator(self, field_name: str, validator: ConfigValidator) -> None:
        """Add field validator.
        
        Args:
            field_name: Field name
            validator: Field validator
        """
        self._validators[field_name] = validator
    
    def add_change_handler(self, handler: ConfigChangeHandler) -> None:
        """Add change handler.
        
        Args:
            handler: Change handler function
        """
        self._change_handlers.append(handler)
    
    def add_nested_config(self, name: str, config: "Config") -> None:
        """Add nested configuration.
        
        Args:
            name: Configuration name
            config: Nested configuration
        """
        config.set_parent(self)
        self._nested_configs[name] = config
    
    def get_nested_config(self, name: str) -> "Config":
        """Get nested configuration.
        
        Args:
            name: Configuration name
            
        Returns:
            Nested configuration
            
        Raises:
            ConfigError: If configuration not found
        """
        if name not in self._nested_configs:
            raise ConfigError(f"Nested configuration {name} not found")
        return self._nested_configs[name]
    
    def get_value(self, name: str) -> Any:
        """Get configuration value.
        
        Args:
            name: Value name
            
        Returns:
            Configuration value
            
        Raises:
            ConfigError: If value not found
        """
        # Check for nested config path
        if "." in name:
            config_name, field_name = name.split(".", 1)
            return self.get_nested_config(config_name).get_value(field_name)
            
        if name in self._values:
            return self._values[name].value
            
        if self._parent:
            return self._parent.get_value(name)
            
        raise ConfigError(f"Configuration value {name} not found")
    
    async def validate_value(self, name: str, value: Any) -> ValidationResult:
        """Validate configuration value.
        
        Args:
            name: Value name
            value: Value to validate
            
        Returns:
            Validation result
        """
        if name in self._validators:
            return await self._validators[name].validate(value)
        return ValidationResult(valid=True)
    
    def set_value(
        self,
        name: str,
        value: Any,
        source: ConfigSource = ConfigSource.OVERRIDE,
        path: str = "",
    ) -> None:
        """Set configuration value.
        
        Args:
            name: Value name
            value: Value to set
            source: Value source
            path: Value path
            
        Raises:
            ConfigError: If value is invalid
        """
        # Check for nested config path
        if "." in name:
            config_name, field_name = name.split(".", 1)
            return self.get_nested_config(config_name).set_value(
                field_name, value, source, path
            )
            
        if not hasattr(self, name):
            raise ConfigError(f"Configuration value {name} not found")
            
        # Validate value type
        field_type = type(getattr(self, name))
        if not isinstance(value, field_type):
            raise ConfigError(f"Value must be of type {field_type.__name__}, got {type(value).__name__}")
            
        # Get old value for change notification
        old_value = getattr(self, name)
            
        # Update value
        setattr(self, name, value)
        self._values[name] = ConfigValue(
            value=value,
            source=source,
            path=path,
            timestamp=datetime.now(),
        )
        
        # Notify change handlers
        for handler in self._change_handlers:
            try:
                handler(self, name, old_value, value)
            except Exception:
                pass  # Ignore handler errors
    
    async def load(self, loader: ConfigLoader, path: str | Path) -> None:
        """Load configuration from source.
        
        Args:
            loader: Configuration loader
            path: Configuration source path
            
        Raises:
            ConfigError: If loading fails
        """
        try:
            self._loader = loader
            self._path = path
            
            values = await loader.load(path)
            
            for name, value in values.items():
                if "." in name:
                    # Handle nested config
                    config_name, field_name = name.split(".", 1)
                    if config_name in self._nested_configs:
                        self._nested_configs[config_name].set_value(
                            field_name,
                            value.value,
                            value.source,
                            value.path,
                        )
                elif hasattr(self, name):
                    # Validate value
                    validation = await self.validate_value(name, value.value)
                    if not validation.valid:
                        raise ConfigError(
                            f"Invalid configuration value for {name}: {validation.message}"
                        )
                        
                    self.set_value(name, value.value, value.source, value.path)
                    
        except Exception as e:
            raise ConfigError("Failed to load configuration", cause=e)
    
    async def reload(self) -> None:
        """Reload configuration from source.
        
        Raises:
            ConfigError: If reloading fails or is not supported
        """
        if not self._loader or not self._path:
            raise ConfigError("Configuration not loaded from source")
            
        if not await self._loader.supports_reload():
            raise ConfigError("Configuration loader does not support reloading")
            
        await self.load(self._loader, self._path)
        
        # Reload nested configs
        for config in self._nested_configs.values():
            await config.reload()
    
    def get_stats(self) -> dict[str, Any]:
        """Get configuration statistics."""
        stats = {
            "name": self.name,
            "enabled": self.enabled,
            "metadata": self.metadata,
            "config_class": self.__class__.__name__,
            "values": {
                name: {
                    "value": value.value,
                    "source": str(value.source),
                    "path": value.path,
                    "timestamp": value.timestamp.isoformat(),
                    "metadata": value.metadata,
                }
                for name, value in self._values.items()
            },
            "validators": list(self._validators.keys()),
            "change_handlers": len(self._change_handlers),
        }
        
        if self._nested_configs:
            stats["nested_configs"] = {
                name: config.get_stats()
                for name, config in self._nested_configs.items()
            }
            
        return stats

__all__ = [
    "Config",
    "ConfigSource",
    "ConfigValue",
    "ConfigValidator",
    "ConfigLoader",
    "ConfigChangeHandler",
]
