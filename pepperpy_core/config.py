"""Configuration system implementation."""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Protocol

from .exceptions import ConfigError
from .io import FileIO
from .module import BaseModule, ModuleConfig
from .validation import ValidationLevel, ValidationResult, Validator


class ConfigSource(Enum):
    """Configuration source types."""
    
    DEFAULT = "default"
    ENV = "env"
    FILE = "file"
    OVERRIDE = "override"
    
    def __str__(self) -> str:
        """Return string representation."""
        return self.value


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


class FileWatcher(Protocol):
    """File watcher protocol."""
    
    async def watch(self, path: Path) -> None:
        """Watch file for changes.
        
        Args:
            path: File path to watch
            
        Raises:
            ConfigError: If watching fails
        """
        ...
        
    async def unwatch(self, path: Path) -> None:
        """Stop watching file.
        
        Args:
            path: File path to unwatch
            
        Raises:
            ConfigError: If unwatching fails
        """
        ...
        
    async def has_changed(self, path: Path) -> bool:
        """Check if file has changed.
        
        Args:
            path: File path to check
            
        Returns:
            True if file has changed
            
        Raises:
            ConfigError: If checking fails
        """
        ...


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


class FileConfigLoader(ConfigLoader):
    """Base file configuration loader."""
    
    def __init__(self) -> None:
        """Initialize loader."""
        self._file_io = FileIO()
    
    async def initialize(self) -> None:
        """Initialize file I/O."""
        await self._file_io.initialize()
    
    async def cleanup(self) -> None:
        """Cleanup file I/O."""
        await self._file_io.cleanup()
    
    async def load(self, path: str | Path) -> dict[str, ConfigValue]:
        """Load configuration from file.
        
        Args:
            path: File path
            
        Returns:
            Dictionary of configuration values
            
        Raises:
            ConfigError: If loading fails
        """
        try:
            await self.initialize()
            try:
                data = self._file_io.read(path)
                return {
                    key: ConfigValue(
                        value=value,
                        source=ConfigSource.FILE,
                        path=str(path),
                    )
                    for key, value in data.items()
                }
            finally:
                await self.cleanup()
        except Exception as e:
            raise ConfigError(f"Failed to load config file {path}: {e}")
    
    async def supports_reload(self) -> bool:
        """Check if loader supports reloading.
        
        Returns:
            True if reloading is supported
        """
        return True


class JsonConfigLoader(FileConfigLoader):
    """JSON configuration loader."""
    pass


class YamlConfigLoader(FileConfigLoader):
    """YAML configuration loader."""
    pass


class EnvConfigLoader(ConfigLoader):
    """Environment variable configuration loader."""
    
    def __init__(self, prefix: str = "") -> None:
        """Initialize loader.
        
        Args:
            prefix: Environment variable prefix
        """
        self.prefix = prefix
    
    async def load(self, path: str | Path) -> dict[str, ConfigValue]:
        """Load configuration from environment variables.
        
        Args:
            path: Ignored for environment variables
            
        Returns:
            Dictionary of configuration values
        """
        values = {}
        prefix = self.prefix.upper() + "_" if self.prefix else ""
        
        for key, value in os.environ.items():
            if prefix and not key.startswith(prefix):
                continue
                
            config_key = key[len(prefix):].lower()
            values[config_key] = ConfigValue(
                value=value,
                source=ConfigSource.ENV,
                path=f"env:{key}",
            )
            
        return values
    
    async def supports_reload(self) -> bool:
        """Check if loader supports reloading.
        
        Returns:
            True if reloading is supported
        """
        return True


class ChainedConfigLoader(ConfigLoader):
    """Chained configuration loader."""
    
    def __init__(self, loaders: list[ConfigLoader]) -> None:
        """Initialize loader.
        
        Args:
            loaders: List of loaders to chain
        """
        self.loaders = loaders
    
    async def load(self, path: str | Path) -> dict[str, ConfigValue]:
        """Load configuration from all chained loaders.
        
        Args:
            path: Configuration source path
            
        Returns:
            Dictionary of configuration values
            
        Raises:
            ConfigError: If loading fails
        """
        values = {}
        for loader in self.loaders:
            try:
                loader_values = await loader.load(path)
                values.update(loader_values)
            except Exception as e:
                raise ConfigError(f"Failed to load config from {loader.__class__.__name__}: {e}")
        return values
    
    async def supports_reload(self) -> bool:
        """Check if loader supports reloading.
        
        Returns:
            True if all loaders support reloading
        """
        return all(await loader.supports_reload() for loader in self.loaders)


ConfigChangeHandler = Callable[["Config", str, Any, Any], None]


@dataclass
class Config(ModuleConfig):
    """Configuration container."""
    
    name: str
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Initialize configuration."""
        super().__post_init__()
        self._values: dict[str, ConfigValue] = {}
        self._validators: dict[str, ConfigValidator] = {}
        self._change_handlers: list[ConfigChangeHandler] = []
        self._nested_configs: dict[str, "Config"] = {}
        self._loader: ConfigLoader | None = None
        self._path: str | Path | None = None
        self._parent: "Config | None" = None
    
    def set_parent(self, parent: "Config") -> None:
        """Set parent configuration.
        
        Args:
            parent: Parent configuration
        """
        self._parent = parent
    
    def get_parent(self) -> "Config | None":
        """Get parent configuration.
        
        Returns:
            Parent configuration if set
        """
        return self._parent
    
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
    
    async def load(self, loader: ConfigLoader, path: str | Path) -> None:
        """Load configuration from source.
        
        Args:
            loader: Configuration loader
            path: Configuration source path
            
        Raises:
            ConfigError: If loading fails
        """
        self._loader = loader
        self._path = path
        
        try:
            values = await loader.load(path)
            self._values.update(values)
            
            # Load nested configs
            for name, config in self._nested_configs.items():
                await config.load(loader, path)
        except Exception as e:
            raise ConfigError(f"Failed to load configuration: {e}")
    
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
    "JsonConfigLoader",
    "YamlConfigLoader",
    "EnvConfigLoader",
    "ChainedConfigLoader",
    "ConfigChangeHandler",
] 