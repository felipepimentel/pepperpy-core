"""Base module implementation."""

import asyncio
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Generic, TypeVar

from .exceptions import InitializationError, ModuleError, StateError
from .types import BaseConfigData


@dataclass
class ModuleConfig(BaseConfigData):
    """Module configuration."""

    # Required fields (inherited from BaseConfigData)
    name: str

    # Optional fields
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


class ModuleState(Enum):
    """Module lifecycle states."""

    CREATED = "created"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    CLEANING_UP = "cleaning_up"
    ERROR = "error"

    def __str__(self) -> str:
        """Return string representation."""
        return self.value


@dataclass
class DependencyInfo:
    """Module dependency information."""

    name: str
    module: "BaseModule[Any]"
    optional: bool = False
    lazy: bool = False

    def __post_init__(self) -> None:
        """Validate dependency info."""
        if not isinstance(self.name, str):
            raise ModuleError(f"name must be a string, got {type(self.name).__name__}")
        if not self.name:
            raise ModuleError("name cannot be empty")
        if not isinstance(self.module, BaseModule):
            raise ModuleError(
                f"module must be a BaseModule instance, got {type(self.module).__name__}"
            )
        if not isinstance(self.optional, bool):
            raise ModuleError(
                f"optional must be a boolean, got {type(self.optional).__name__}"
            )
        if not isinstance(self.lazy, bool):
            raise ModuleError(f"lazy must be a boolean, got {type(self.lazy).__name__}")


class LifecycleHook(ABC):
    """Base class for module lifecycle hooks."""

    @abstractmethod
    async def before_setup(self, module: "BaseModule[Any]") -> None:
        """Called before module setup.

        Args:
            module: Module instance
        """
        pass

    @abstractmethod
    async def after_setup(self, module: "BaseModule[Any]") -> None:
        """Called after module setup.

        Args:
            module: Module instance
        """
        pass

    @abstractmethod
    async def before_cleanup(self, module: "BaseModule[Any]") -> None:
        """Called before module cleanup.

        Args:
            module: Module instance
        """
        pass

    @abstractmethod
    async def after_cleanup(self, module: "BaseModule[Any]") -> None:
        """Called after module cleanup.

        Args:
            module: Module instance
        """
        pass


ConfigT = TypeVar("ConfigT", bound=ModuleConfig)


class BaseModule(Generic[ConfigT], ABC):
    """Base module class that provides common functionality for all modules."""

    def __init__(self, config: ConfigT) -> None:
        """Initialize module.

        Args:
            config: Module configuration

        Raises:
            ModuleError: If config is invalid
        """
        if not config:
            raise ModuleError("config cannot be None")
        if not config.enabled:
            raise ModuleError(f"Module {config.name} is disabled")

        self.config = config
        self._state = ModuleState.CREATED
        self._error: Exception | None = None
        self._dependencies: dict[str, DependencyInfo] = {}
        self._hooks: list[LifecycleHook] = []
        self._dependency_graph: dict[str, set[str]] = defaultdict(set)
        self._initialized_event = asyncio.Event()

    @property
    def is_initialized(self) -> bool:
        """Check if module is initialized."""
        return self._state == ModuleState.INITIALIZED

    @property
    def state(self) -> ModuleState:
        """Get current module state."""
        return self._state

    @property
    def error(self) -> Exception | None:
        """Get last error if any."""
        return self._error

    def _ensure_initialized(self) -> None:
        """Ensure module is initialized.

        Raises:
            StateError: If module not initialized
            ModuleError: If module is in error state
        """
        if self._state == ModuleState.ERROR:
            raise ModuleError(
                f"Module {self.config.name} is in error state: {self._error}"
            )
        if not self.is_initialized:
            raise StateError(f"Module {self.config.name} is not initialized")

    async def initialize(self) -> None:
        """Initialize module.

        Raises:
            InitializationError: If initialization fails
            StateError: If module already initialized
        """
        if self.is_initialized:
            return

        if self._state == ModuleState.INITIALIZING:
            await self._initialized_event.wait()
            return

        if self._state == ModuleState.ERROR:
            raise InitializationError(
                f"Cannot initialize module {self.config.name} in error state: {self._error}"
            )

        self._state = ModuleState.INITIALIZING
        try:
            # Initialize dependencies first
            for dep in self._dependencies.values():
                if not dep.lazy:
                    await dep.module.initialize()

            # Run pre-setup hooks
            for hook in self._hooks:
                await hook.before_setup(self)

            # Setup module
            await self._setup()

            # Run post-setup hooks
            for hook in self._hooks:
                await hook.after_setup(self)

            self._state = ModuleState.INITIALIZED
        except Exception as e:
            self._state = ModuleState.ERROR
            self._error = e
            raise InitializationError(
                f"Failed to initialize module {self.config.name}: {e}"
            )
        finally:
            self._initialized_event.set()

    async def cleanup(self) -> None:
        """Cleanup module resources.

        Raises:
            ModuleError: If cleanup fails
        """
        if not self.is_initialized:
            return

        self._state = ModuleState.CLEANING_UP
        try:
            # Run pre-cleanup hooks
            for hook in self._hooks:
                await hook.before_cleanup(self)

            # Cleanup module
            await self._teardown()

            # Run post-cleanup hooks
            for hook in self._hooks:
                await hook.after_cleanup(self)

            # Reset state
            self._state = ModuleState.CREATED
            self._error = None
            self._initialized_event.clear()
        except Exception as e:
            self._state = ModuleState.ERROR
            self._error = e
            raise ModuleError(f"Failed to cleanup module {self.config.name}: {e}")

    def add_dependency(
        self,
        name: str,
        module: "BaseModule[Any]",
        optional: bool = False,
        lazy: bool = False,
    ) -> None:
        """Add module dependency.

        Args:
            name: Dependency name
            module: Dependent module
            optional: Whether dependency is optional
            lazy: Whether to initialize dependency lazily

        Raises:
            ModuleError: If dependency is invalid or creates a cycle
        """
        if self.is_initialized:
            raise ModuleError("Cannot add dependency after initialization")

        # Check for dependency cycles
        visited = set()

        def check_cycle(mod: BaseModule[Any]) -> None:
            if mod == self:
                raise ModuleError(f"Dependency cycle detected: {name}")
            if mod in visited:
                return
            visited.add(mod)
            for dep in mod._dependencies.values():
                check_cycle(dep.module)

        check_cycle(module)

        # Add dependency
        self._dependencies[name] = DependencyInfo(
            name=name,
            module=module,
            optional=optional,
            lazy=lazy,
        )

        # Update dependency graph
        self._dependency_graph[module.config.name].add(self.config.name)

    def add_hook(self, hook: LifecycleHook) -> None:
        """Add lifecycle hook.

        Args:
            hook: Lifecycle hook

        Raises:
            ModuleError: If module already initialized
        """
        if self.is_initialized:
            raise ModuleError("Cannot add hook after initialization")
        self._hooks.append(hook)

    @abstractmethod
    async def _setup(self) -> None:
        """Setup module resources.

        This method should be implemented by subclasses to perform any necessary
        setup when the module is initialized.
        """
        pass

    @abstractmethod
    async def _teardown(self) -> None:
        """Cleanup module resources.

        This method should be implemented by subclasses to perform any necessary
        cleanup when the module is shut down.
        """
        pass

    @abstractmethod
    async def get_stats(self) -> dict[str, Any]:
        """Get module statistics.

        Returns:
            Dictionary of module statistics
        """
        pass


T = TypeVar("T")


class BaseManager(BaseModule[ConfigT], Generic[ConfigT, T]):
    """Base manager implementation with item management capabilities."""

    def __init__(self, config: ConfigT) -> None:
        """Initialize manager.

        Args:
            config: Manager configuration
        """
        super().__init__(config)
        self._items: dict[str, T] = {}

    async def _setup(self) -> None:
        """Setup manager resources."""
        self._items.clear()

    async def _teardown(self) -> None:
        """Teardown manager resources."""
        self._items.clear()

    async def get_stats(self) -> dict[str, Any]:
        """Get manager statistics.

        Returns:
            Manager statistics
        """
        stats = await super().get_stats()
        stats.update({
            "items_count": len(self._items),
            "item_names": sorted(self._items.keys()),
            "item_type": self._get_item_type().__name__,
        })
        return stats

    def get_item(self, name: str) -> T:
        """Get item by name.

        Args:
            name: Item name

        Returns:
            Item value

        Raises:
            KeyError: If item not found
            StateError: If manager not initialized
            ModuleError: If manager is in error state
            ValueError: If name is empty
        """
        if not name:
            raise ValueError("name cannot be empty")

        self._ensure_initialized()
        if name not in self._items:
            raise KeyError(f"Item {name} not found")
        return self._items[name]


__all__ = [
    "ModuleConfig",
    "ModuleState",
    "DependencyInfo",
    "LifecycleHook",
    "BaseModule",
    "BaseManager",
]
