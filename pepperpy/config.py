"""Configuration module."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from pepperpy.core import PepperpyError
from pepperpy.module import BaseModule, ModuleConfig


class ConfigError(PepperpyError):
    """Configuration error."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, details, cause)


@dataclass
class ConfigManagerConfig(ModuleConfig):
    """Configuration manager configuration."""

    name: str = "config_manager"
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConfigManager(BaseModule[ConfigManagerConfig]):
    """Configuration manager."""

    def __init__(self, config: Optional[ConfigManagerConfig] = None) -> None:
        """Initialize configuration manager.

        Args:
            config: Configuration manager configuration
        """
        super().__init__(config or ConfigManagerConfig())
        self._config_store: Dict[str, Any] = {}

    def _ensure_initialized(self) -> None:
        """Ensure manager is initialized.

        Raises:
            ConfigError: If manager is not initialized
        """
        if not self.is_initialized:
            raise ConfigError(
                "Configuration manager is not initialized",
                {"manager_name": self.config.name},
            )

    async def _setup(self) -> None:
        """Set up configuration manager."""
        self._config_store = {}

    async def _teardown(self) -> None:
        """Clean up configuration manager."""
        self._config_store = {}

    def get(self, key: str) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key

        Returns:
            Configuration value

        Raises:
            ConfigError: If value is not found
        """
        self._ensure_initialized()
        if key not in self._config_store:
            raise ConfigError(
                "Configuration value not found",
                {"key": key, "manager_name": self.config.name},
            )
        return self._config_store[key]

    def set(self, key: str, value: Any) -> None:
        """Set configuration value.

        Args:
            key: Configuration key
            value: Configuration value

        Raises:
            ConfigError: If value cannot be set
        """
        self._ensure_initialized()
        self._config_store[key] = value

    def delete(self, key: str) -> None:
        """Delete configuration value.

        Args:
            key: Configuration key

        Raises:
            ConfigError: If value cannot be deleted
        """
        self._ensure_initialized()
        if key not in self._config_store:
            raise ConfigError(
                "Configuration value not found",
                {"key": key, "manager_name": self.config.name},
            )
        del self._config_store[key]

    def clear(self) -> None:
        """Clear configuration store.

        Raises:
            ConfigError: If store cannot be cleared
        """
        self._ensure_initialized()
        self._config_store = {}


__all__ = ["ConfigError", "ConfigManager", "ConfigManagerConfig"]
