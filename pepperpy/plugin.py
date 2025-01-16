"""Plugin module."""

import importlib.util
import inspect
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Optional, Protocol, Type, TypeVar, runtime_checkable

from pepperpy.core import PepperpyError
from pepperpy.module import BaseModule, ModuleConfig


class PluginError(PepperpyError):
    """Plugin error."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize plugin error.

        Args:
            message: Error message
            context: Error context
            cause: Error cause
        """
        super().__init__(message, context, cause)


@runtime_checkable
class PluginProtocol(Protocol):
    """Plugin protocol."""

    async def setup(self) -> None:
        """Set up plugin."""
        ...

    async def teardown(self) -> None:
        """Clean up plugin."""
        ...


@dataclass
class Plugin:
    """Plugin class."""

    name: str
    module: ModuleType
    metadata: Dict[str, Any] = field(default_factory=dict)


T = TypeVar("T", bound=PluginProtocol)


@dataclass
class PluginManagerConfig(ModuleConfig):
    """Plugin manager configuration."""

    name: str = "plugin_manager"
    plugin_paths: List[Path] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PluginManager(BaseModule[PluginManagerConfig]):
    """Plugin manager implementation."""

    def __init__(self, config: Optional[PluginManagerConfig] = None) -> None:
        """Initialize plugin manager.

        Args:
            config: Optional plugin manager configuration
        """
        super().__init__(config or PluginManagerConfig())
        self._plugins: Dict[str, Plugin] = {}

    async def _setup(self) -> None:
        """Set up plugin manager."""
        for path in self.config.plugin_paths:
            await self.load(path)

    async def _teardown(self) -> None:
        """Clean up plugin manager."""
        for name in list(self._plugins.keys()):
            await self.unload(name)

    async def load(self, path: Path) -> None:
        """Load plugin.

        Args:
            path: Plugin path

        Raises:
            PluginError: If plugin loading fails
        """
        try:
            plugin = load_plugin(path)
            if plugin.name in self._plugins:
                raise PluginError(
                    "Plugin already loaded",
                    context={"plugin_name": plugin.name},
                )
            self._plugins[plugin.name] = plugin
        except Exception as e:
            raise PluginError(
                "Failed to load plugin",
                context={"plugin_path": str(path)},
                cause=e,
            ) from e

    async def unload(self, name: str) -> None:
        """Unload plugin.

        Args:
            name: Plugin name

        Raises:
            PluginError: If plugin unloading fails
        """
        if name not in self._plugins:
            raise PluginError(
                "Plugin not found",
                context={"plugin_name": name},
            )
        del self._plugins[name]

    def list(self) -> List[str]:
        """List plugins.

        Returns:
            List of plugin names
        """
        return list(self._plugins.keys())

    def get(self, name: str) -> Plugin:
        """Get plugin.

        Args:
            name: Plugin name

        Returns:
            Plugin instance

        Raises:
            PluginError: If plugin not found
        """
        if name not in self._plugins:
            raise PluginError(
                "Plugin not found",
                context={"plugin_name": name},
            )
        return self._plugins[name]


def load_plugin(path: Path) -> Plugin:
    """Load plugin from path.

    Args:
        path: Plugin path

    Returns:
        Plugin instance

    Raises:
        PluginError: If plugin loading fails
    """
    if not path.exists():
        raise PluginError(
            "Plugin file not found",
            context={"plugin_path": str(path)},
        )

    if not path.is_file():
        raise PluginError(
            "Plugin path is not a file",
            context={"plugin_path": str(path)},
        )

    try:
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            raise PluginError(
                "Failed to create module spec",
                context={"plugin_path": str(path)},
            )

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return Plugin(name=path.stem, module=module)
    except Exception as e:
        raise PluginError(
            "Failed to load plugin",
            context={"plugin_path": str(path)},
            cause=e,
        ) from e


def get_plugin_class(plugin: Plugin, base_class: Type[T]) -> Type[T]:
    """Get plugin class.

    Args:
        plugin: Plugin instance
        base_class: Base class to search for

    Returns:
        Plugin class

    Raises:
        PluginError: If plugin class is not found
    """
    for _, obj in inspect.getmembers(plugin.module, inspect.isclass):
        if issubclass(obj, base_class) and obj != base_class:
            return obj

    raise PluginError(
        "Plugin class not found",
        context={"plugin_name": plugin.name},
    )


__all__ = [
    "Plugin",
    "PluginError",
    "PluginManager",
    "PluginManagerConfig",
    "PluginProtocol",
    "get_plugin_class",
    "load_plugin",
]
