"""Configuration module.

This module provides a flexible configuration system for PepperPy applications.
It includes:
- Base configuration class for all config objects
- Configuration items for storing values
- Configuration sections for organizing items
- Full configuration management with validation
"""

from dataclasses import dataclass, field
from typing import Any

from .core import PepperpyError


class ConfigError(PepperpyError):
    """Configuration-related errors."""

    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
        config_name: str | None = None,
    ) -> None:
        """Initialize configuration error.

        Args:
            message: Error message
            cause: Original exception that caused this error
            config_name: Name of the configuration that caused the error
        """
        super().__init__(message, cause)
        self.config_name = config_name


class BaseConfig:
    """Base configuration class for PepperPy modules and components.

    This class provides the foundation for all configuration objects in the system.
    It enforces a consistent configuration pattern where each config must have a name
    and can optionally include metadata. The metadata can be used to store additional
    configuration parameters specific to each module.

    Example:
        ```python
        config = BaseConfig("database", metadata={
            "host": "localhost",
            "port": 5432
        })
        ```

    Raises:
        ValueError: If name is empty or metadata is not a dictionary
    """

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialize base configuration.

        Args:
            name: Configuration name
            kwargs: Additional arguments

        Raises:
            ValueError: If name is empty
        """
        if not name:
            raise ValueError("name cannot be empty")

        self.name = name
        self.metadata = kwargs.get("metadata", {})

        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")


@dataclass
class ConfigItem:
    """Configuration item."""

    name: str
    value: Any
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Post initialization validation."""
        self.validate()

    def validate(self) -> None:
        """Validate configuration item."""
        if not self.name:
            raise ValueError("name cannot be empty")


@dataclass
class ConfigSection(BaseConfig):
    """Configuration section."""

    name: str
    items: dict[str, ConfigItem] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Post initialization validation."""
        self.validate()

    def validate(self) -> None:
        """Validate configuration section."""
        if not self.name:
            raise ValueError("name cannot be empty")
        for item in self.items.values():
            item.validate()


@dataclass
class Config(BaseConfig):
    """Configuration."""

    name: str
    sections: dict[str, ConfigSection] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Post initialization validation."""
        self.validate()

    def validate(self) -> None:
        """Validate configuration."""
        if not self.name:
            raise ValueError("name cannot be empty")
        for section in self.sections.values():
            section.validate()

    def get_section(self, name: str) -> ConfigSection:
        """Get configuration section.

        Args:
            name: Section name

        Returns:
            Configuration section

        Raises:
            ConfigError: If section not found
        """
        if name not in self.sections:
            raise ConfigError(f"Section {name} not found")
        return self.sections[name]

    def get_item(self, section_name: str, item_name: str) -> ConfigItem:
        """Get configuration item.

        Args:
            section_name: Section name
            item_name: Item name

        Returns:
            Configuration item

        Raises:
            ConfigError: If section or item not found
        """
        section = self.get_section(section_name)
        if item_name not in section.items:
            raise ConfigError(f"Item {item_name} not found in section {section_name}")
        return section.items[item_name]

    def get_value(self, section_name: str, item_name: str) -> Any:
        """Get configuration value.

        Args:
            section_name: Section name
            item_name: Item name

        Returns:
            Configuration value

        Raises:
            ConfigError: If section or item not found
        """
        return self.get_item(section_name, item_name).value

    def set_value(self, section_name: str, item_name: str, value: Any) -> None:
        """Set configuration value.

        Args:
            section_name: Section name
            item_name: Item name
            value: Configuration value

        Raises:
            ConfigError: If section not found
        """
        section = self.get_section(section_name)
        section.items[item_name] = ConfigItem(name=item_name, value=value)

    def add_section(self, name: str, metadata: dict[str, Any] | None = None) -> None:
        """Add configuration section.

        Args:
            name: Section name
            metadata: Section metadata
        """
        self.sections[name] = ConfigSection(
            name=name,
            metadata=metadata or {},
        )

    def remove_section(self, name: str) -> None:
        """Remove configuration section.

        Args:
            name: Section name

        Raises:
            ConfigError: If section not found
        """
        if name not in self.sections:
            raise ConfigError(f"Section {name} not found")
        del self.sections[name]

    def clear(self) -> None:
        """Clear configuration."""
        self.sections.clear()
        self.metadata.clear()

    def get_stats(self) -> dict[str, Any]:
        """Get configuration statistics.

        Returns:
            Configuration statistics
        """
        total_items = sum(len(section.items) for section in self.sections.values())
        return {
            "name": self.name,
            "sections": len(self.sections),
            "items": total_items,
        }


__all__ = [
    "ConfigItem",
    "ConfigSection",
    "Config",
]
