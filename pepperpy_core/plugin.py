"""Plugin implementation module."""

import functools
import importlib.util
import inspect
import os
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

from .exceptions import PepperpyError
from .module import BaseModule, ModuleConfig


class PluginError(PepperpyError):
    """Plugin specific error."""

    pass


@dataclass
class PluginConfig(ModuleConfig):
    """Plugin configuration."""

    # Required fields (inherited from ModuleConfig)
    name: str

    # Optional fields
    enabled: bool = True
    auto_load: bool = True
    paths: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate configuration."""
        if not self.name.strip():
            raise ValueError("name must not be empty")
        if not self.paths:
            raise ValueError("paths must not be empty")
        if not all(path.strip() for path in self.paths):
            raise ValueError("paths must not contain empty strings")


T = TypeVar("T")


def plugin(name: str | None = None, **kwargs: Any) -> Callable[[T], T]:
    """Plugin decorator.

    Args:
        name: Plugin name
        **kwargs: Additional plugin metadata

    Returns:
        Decorated plugin
    """

    def decorator(obj: T) -> T:
        """Plugin decorator implementation.

        Args:
            obj: Object to decorate

        Returns:
            Decorated object
        """
        plugin_name = name or obj.__name__
        setattr(obj, "__plugin_name__", plugin_name)
        setattr(obj, "__plugin_metadata__", kwargs)
        return obj

    return decorator


def is_plugin(obj: Any) -> bool:
    """Check if object is a plugin.

    Args:
        obj: Object to check

    Returns:
        True if object is a plugin
    """
    return hasattr(obj, "__plugin_name__") and hasattr(obj, "__plugin_metadata__")


class PluginManager(BaseModule[PluginConfig]):
    """Plugin manager implementation."""

    def __init__(self) -> None:
        """Initialize plugin manager."""
        config = PluginConfig(name="plugin-manager")
        super().__init__(config)
        self._plugins: dict[str, Any] = {}

    async def _setup(self) -> None:
        """Setup plugin manager."""
        self._plugins.clear()
        if self.config.auto_load:
            await self.load_plugins()

    async def _teardown(self) -> None:
        """Teardown plugin manager."""
        self._plugins.clear()

    async def get_stats(self) -> dict[str, Any]:
        """Get plugin manager statistics.

        Returns:
            Plugin manager statistics
        """
        self._ensure_initialized()
        return {
            "name": self.config.name,
            "enabled": self.config.enabled,
            "auto_load": self.config.auto_load,
            "total_plugins": len(self._plugins),
            "plugin_names": list(self._plugins.keys()),
        }

    async def load_plugins(self) -> None:
        """Load plugins from configured paths."""
        if not self.config.enabled:
            return

        for path in self.config.paths:
            if not os.path.exists(path):
                raise PluginError(f"Plugin path {path} does not exist")
            await self._load_plugins_from_path(path)

    async def _load_plugins_from_path(self, path: str) -> None:
        """Load plugins from path.

        Args:
            path: Path to load plugins from
        """
        if os.path.isfile(path):
            await self._load_plugin_from_file(path)
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        await self._load_plugin_from_file(file_path)

    async def _load_plugin_from_file(self, file_path: str) -> None:
        """Load plugin from file.

        Args:
            file_path: Path to plugin file
        """
        try:
            spec = importlib.util.spec_from_file_location("plugin", file_path)
            if not spec or not spec.loader:
                raise PluginError(f"Failed to load plugin spec from {file_path}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for _, obj in inspect.getmembers(module):
                if is_plugin(obj):
                    name = getattr(obj, "__plugin_name__")
                    self._plugins[name] = obj

        except Exception as e:
            raise PluginError(f"Failed to load plugin from {file_path}") from e

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


__all__ = [
    "PluginError",
    "PluginConfig",
    "plugin",
    "is_plugin",
    "PluginManager",
] 