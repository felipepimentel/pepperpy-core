"""Plugin implementation module."""

import importlib.util
import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeVar

from .exceptions import PluginError
from .module import BaseModule, ModuleConfig


@dataclass
class PluginConfig(ModuleConfig):
    """Plugin manager configuration."""

    name: str
    plugin_dir: str | Path = "plugins"
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


def plugin(name: str) -> Callable[[Any], Any]:
    """Plugin decorator.

    Args:
        name: Plugin name

    Returns:
        Decorated plugin class
    """

    def decorator(cls: Any) -> Any:
        """Plugin decorator implementation.

        Args:
            cls: Plugin class

        Returns:
            Decorated plugin class
        """
        cls.__plugin_name__ = name
        return cls

    return decorator


def is_plugin(obj: Any) -> bool:
    """Check if object is a plugin.

    Args:
        obj: Object to check

    Returns:
        True if object is a plugin
    """
    return hasattr(obj, "__plugin_name__")


T = TypeVar("T")


class PluginManager(BaseModule[PluginConfig]):
    """Plugin manager implementation."""

    def __init__(self, config: PluginConfig | None = None) -> None:
        """Initialize plugin manager.

        Args:
            config: Plugin manager configuration
        """
        super().__init__(
            config or PluginConfig(name="plugin_manager", plugin_dir="plugins")
        )
        self._plugins: dict[str, Any] = {}

    async def _setup(self) -> None:
        """Setup plugin manager."""
        self._plugins.clear()

    async def _teardown(self) -> None:
        """Cleanup plugin manager."""
        self._plugins.clear()

    async def get_stats(self) -> dict[str, Any]:
        """Get plugin manager statistics.

        Returns:
            Plugin manager statistics
        """
        if not self.is_initialized:
            await self.initialize()

        return {
            "name": self.config.name,
            "enabled": self.config.enabled,
            "plugin_dir": str(self.config.plugin_dir),
            "total_plugins": len(self._plugins),
            "plugin_names": list(self._plugins.keys()),
        }

    def load_plugin(self, path: str | Path) -> None:
        """Load plugin from file.

        Args:
            path: Plugin file path

        Raises:
            PluginError: If loading fails
        """
        self._ensure_initialized()

        try:
            # Load module
            spec = importlib.util.spec_from_file_location("plugin", path)
            if not spec or not spec.loader:
                raise PluginError(f"Failed to load plugin spec from {path}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find plugin classes
            for _name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and is_plugin(obj):
                    plugin_name = obj.__plugin_name__
                    self._plugins[plugin_name] = obj()

        except Exception as e:
            raise PluginError(f"Failed to load plugin from {path}: {e}") from e

    def get_plugin(self, name: str) -> Any:
        """Get plugin by name.

        Args:
            name: Plugin name

        Returns:
            Plugin instance

        Raises:
            KeyError: If plugin not found
        """
        self._ensure_initialized()
        if name not in self._plugins:
            raise KeyError(f"Plugin {name} not found")
        return self._plugins[name]

    def get_plugins(self) -> list[Any]:
        """Get all plugins.

        Returns:
            List of plugin instances
        """
        self._ensure_initialized()
        return list(self._plugins.values())
