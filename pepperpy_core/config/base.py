"""Base configuration types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar, Generic, TypeVar

from ..exceptions.base import ConfigError
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
    
    def __post_init__(self) -> None:
        """Validate config value."""
        if not isinstance(self.source, ConfigSource):
            raise ConfigError(f"source must be a ConfigSource, got {type(self.source).__name__}")
        if not isinstance(self.path, str):
            raise ConfigError(f"path must be a string, got {type(self.path).__name__}")

class ConfigLoader(ABC):
    """Base configuration loader interface."""
    
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

class BaseConfig:
    """Base configuration class for all configurations in the system."""
    
    # Required fields
    name: str
    
    # Optional fields with defaults
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    
    # Class-level validators
    _validators: ClassVar[dict[str, list[Validator[Any]]]] = {}
    
    # Configuration values with metadata
    _values: dict[str, ConfigValue] = field(default_factory=dict)
    
    # Parent configuration
    _parent: "BaseConfig | None" = None

    def __init_subclass__(cls) -> None:
        """Initialize subclass with empty validator list."""
        super().__init_subclass__()
        cls._validators[cls.__name__] = []

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not isinstance(self.name, str):
            raise ConfigError(f"name must be a string, got {type(self.name).__name__}")
        if not self.name:
            raise ConfigError("name cannot be empty")
        if not isinstance(self.enabled, bool):
            raise ConfigError(f"enabled must be a boolean, got {type(self.enabled).__name__}")
        if not isinstance(self.metadata, dict):
            raise ConfigError(f"metadata must be a dictionary, got {type(self.metadata).__name__}")
            
        # Initialize values
        for field_info in fields(self):
            if not field_info.name.startswith("_"):
                self._values[field_info.name] = ConfigValue(
                    value=getattr(self, field_info.name),
                )

    def set_parent(self, parent: "BaseConfig") -> None:
        """Set parent configuration.
        
        Args:
            parent: Parent configuration
            
        Raises:
            ConfigError: If parent is invalid
        """
        if not isinstance(parent, BaseConfig):
            raise ConfigError(f"parent must be a BaseConfig instance, got {type(parent).__name__}")
        self._parent = parent

    def get_value(self, name: str) -> Any:
        """Get configuration value.
        
        Args:
            name: Value name
            
        Returns:
            Configuration value
            
        Raises:
            ConfigError: If value not found
        """
        if name in self._values:
            return self._values[name].value
            
        if self._parent:
            return self._parent.get_value(name)
            
        raise ConfigError(f"Configuration value {name} not found")

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
        if not hasattr(self, name):
            raise ConfigError(f"Configuration value {name} not found")
            
        # Validate value type
        field_type = type(getattr(self, name))
        if not isinstance(value, field_type):
            raise ConfigError(f"Value must be of type {field_type.__name__}, got {type(value).__name__}")
            
        # Update value
        setattr(self, name, value)
        self._values[name] = ConfigValue(value=value, source=source, path=path)

    async def load(self, loader: ConfigLoader, path: str | Path) -> None:
        """Load configuration from source.
        
        Args:
            loader: Configuration loader
            path: Configuration source path
            
        Raises:
            ConfigError: If loading fails
        """
        try:
            values = await loader.load(path)
            
            for name, value in values.items():
                if hasattr(self, name):
                    self.set_value(name, value.value, value.source, value.path)
                    
        except Exception as e:
            raise ConfigError("Failed to load configuration", cause=e)

    async def validate(self) -> list[ValidationResult]:
        """Validate configuration data.
        
        Returns:
            List of validation results
            
        Raises:
            ConfigError: If validation fails with critical errors
        """
        results = []
        
        # Run all validators for this class and its parent classes
        cls = self.__class__
        while cls is not object:
            if cls.__name__ in self._validators:
                for validator in self._validators[cls.__name__]:
                    try:
                        result = await validator.validate(self)
                        if isinstance(result, ValidationResult):
                            results.append(result)
                        else:
                            results.extend(result)
                    except Exception as e:
                        results.append(ValidationResult(
                            valid=False,
                            level=ValidationLevel.ERROR,
                            message=f"Validator {validator.__class__.__name__} failed: {e}",
                            metadata={
                                "error": str(e),
                                "validator": validator.__class__.__name__,
                                "config_class": cls.__name__,
                            },
                        ))
            cls = cls.__base__
        
        # Check for critical errors
        critical_errors = [
            r for r in results 
            if not r.valid and r.level == ValidationLevel.CRITICAL
        ]
        
        if critical_errors:
            messages = [r.message for r in critical_errors if r.message]
            raise ConfigError(
                f"Configuration validation failed for {self.name}: {'; '.join(messages)}",
                config_name=self.name,
            )
            
        return results

    def get_stats(self) -> dict[str, Any]:
        """Get configuration statistics."""
        cls = self.__class__
        validator_count = sum(
            len(validators)
            for class_name, validators in self._validators.items()
            if class_name == cls.__name__ or issubclass(cls, globals().get(class_name, object))
        )
        
        stats = {
            "name": self.name,
            "enabled": self.enabled,
            "metadata": self.metadata,
            "validator_count": validator_count,
            "config_class": cls.__name__,
            "values": {
                name: {
                    "value": value.value,
                    "source": str(value.source),
                    "path": value.path,
                }
                for name, value in self._values.items()
            },
        }
        
        if self._parent:
            stats["parent"] = self._parent.name
            
        return stats

    @classmethod
    def add_validator(cls, validator: Validator[Any]) -> None:
        """Add validator to configuration class.
        
        Args:
            validator: Validator instance
            
        Raises:
            ConfigError: If validator is invalid
        """
        if not isinstance(validator, Validator):
            raise ConfigError(f"validator must be a Validator instance, got {type(validator).__name__}")
        cls._validators[cls.__name__].append(validator)

    @classmethod
    def clear_validators(cls) -> None:
        """Clear all validators for this configuration class."""
        if cls.__name__ in cls._validators:
            cls._validators[cls.__name__].clear()

@dataclass
class ModuleConfig(BaseConfig):
    """Base configuration for modules with additional module-specific fields."""
    
    # Optional module-specific fields
    version: str = "0.1.0"
    description: str = ""
    
    def __post_init__(self) -> None:
        """Validate module configuration after initialization."""
        super().__post_init__()
        if not isinstance(self.version, str):
            raise ConfigError(f"version must be a string, got {type(self.version).__name__}")
        if not isinstance(self.description, str):
            raise ConfigError(f"description must be a string, got {type(self.description).__name__}")
    
    def get_stats(self) -> dict[str, Any]:
        """Get module configuration statistics."""
        stats = super().get_stats()
        stats.update({
            "version": self.version,
            "description": self.description,
        })
        return stats

class GenericConfig(BaseConfig, Generic[T]):
    """Base configuration class with generic type support."""
    
    # Generic value field
    value: T
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        super().__post_init__()
        # Validate generic type if possible
        type_hints = self.__class__.__orig_bases__[0].__args__  # type: ignore
        if type_hints and not isinstance(self.value, type_hints[0]):
            raise ConfigError(
                f"value must be of type {type_hints[0].__name__}, got {type(self.value).__name__}",
                config_name=self.name,
            )

    def get_stats(self) -> dict[str, Any]:
        """Get configuration statistics."""
        stats = super().get_stats()
        stats.update({
            "value_type": type(self.value).__name__,
        })
        return stats

# Type variable for generic configuration types
ConfigT = TypeVar("ConfigT", bound=BaseConfig)

__all__ = [
    "BaseConfig",
    "ModuleConfig",
    "GenericConfig",
    "ConfigT",
    "ConfigSource",
    "ConfigValue",
    "ConfigLoader",
]
