"""Base module implementation."""

import asyncio
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Generic, TypeVar, cast

from ..config.base import ConfigT
from ..exceptions.base import InitializationError, ModuleError, StateError

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
            raise ModuleError(f"module must be a BaseModule instance, got {type(self.module).__name__}")
        if not isinstance(self.optional, bool):
            raise ModuleError(f"optional must be a boolean, got {type(self.optional).__name__}")
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
            module: Module instance
            optional: Whether dependency is optional
            lazy: Whether dependency should be initialized lazily
            
        Raises:
            ModuleError: If dependency is invalid or creates a cycle
        """
        if not name:
            raise ModuleError("Dependency name cannot be empty")
        if not module:
            raise ModuleError("Dependency module cannot be None")
        if name in self._dependencies:
            raise ModuleError(f"Dependency {name} already exists")
            
        # Check for cycles
        if self._would_create_cycle(name, module):
            raise ModuleError(f"Adding dependency {name} would create a cycle")
            
        self._dependencies[name] = DependencyInfo(
            name=name,
            module=module,
            optional=optional,
            lazy=lazy,
        )
        self._dependency_graph[self.config.name].add(name)

    def get_dependency(self, name: str) -> "BaseModule[Any]":
        """Get module dependency.
        
        Args:
            name: Dependency name
            
        Returns:
            Module instance
            
        Raises:
            ModuleError: If dependency not found
        """
        if not name:
            raise ModuleError("Dependency name cannot be empty")
        if name not in self._dependencies:
            raise ModuleError(f"Dependency {name} not found")
            
        return self._dependencies[name].module

    def add_hook(self, hook: LifecycleHook) -> None:
        """Add lifecycle hook.
        
        Args:
            hook: Hook instance
        """
        self._hooks.append(hook)

    def _would_create_cycle(self, name: str, module: "BaseModule[Any]") -> bool:
        """Check if adding dependency would create a cycle.
        
        Args:
            name: Dependency name
            module: Module instance
            
        Returns:
            True if cycle would be created
        """
        # Add temporary edge
        self._dependency_graph[self.config.name].add(name)
        
        # Check for cycles using DFS
        visited = set()
        path = set()
        
        def has_cycle(node: str) -> bool:
            if node in path:
                return True
            if node in visited:
                return False
                
            visited.add(node)
            path.add(node)
            
            for dep in self._dependency_graph[node]:
                if has_cycle(dep):
                    return True
                    
            path.remove(node)
            return False
        
        has_cycles = has_cycle(self.config.name)
        
        # Remove temporary edge
        self._dependency_graph[self.config.name].remove(name)
        
        return has_cycles

    async def initialize(self) -> None:
        """Initialize module.
        
        Raises:
            InitializationError: If initialization fails
            StateError: If module is in invalid state
        """
        if self.is_initialized:
            return

        if self._state not in (ModuleState.CREATED, ModuleState.ERROR):
            raise StateError(f"Cannot initialize module in state {self._state}")

        try:
            # Initialize non-lazy dependencies first
            for dep in self._dependencies.values():
                if not dep.lazy:
                    try:
                        await dep.module.initialize()
                    except Exception as e:
                        if not dep.optional:
                            raise InitializationError(
                                f"Failed to initialize dependency {dep.name}",
                                cause=e,
                            )
            
            # Validate configuration before initialization
            await self.config.validate()
            
            # Run pre-setup hooks
            for hook in self._hooks:
                await hook.before_setup(self)
            
            self._state = ModuleState.INITIALIZING
            await self._setup()
            self._state = ModuleState.INITIALIZED
            self._error = None
            
            # Run post-setup hooks
            for hook in self._hooks:
                await hook.after_setup(self)
                
            # Signal initialization complete
            self._initialized_event.set()
            
        except Exception as e:
            self._error = e
            self._state = ModuleState.ERROR
            raise InitializationError(
                f"Failed to initialize module {self.config.name}",
                cause=e,
            )

    async def cleanup(self) -> None:
        """Cleanup module resources.
        
        Raises:
            ModuleError: If cleanup fails
            StateError: If module is in invalid state
        """
        if not self.is_initialized:
            return

        try:
            # Run pre-cleanup hooks
            for hook in self._hooks:
                await hook.before_cleanup(self)
            
            self._state = ModuleState.CLEANING_UP
            await self._teardown()
            
            # Cleanup dependencies in reverse order
            for name, dep in reversed(list(self._dependencies.items())):
                try:
                    await dep.module.cleanup()
                except Exception as e:
                    if not dep.optional:
                        raise ModuleError(
                            f"Failed to cleanup dependency {name}",
                            cause=e,
                        )
                    
            self._state = ModuleState.CREATED
            self._error = None
            
            # Run post-cleanup hooks
            for hook in self._hooks:
                await hook.after_cleanup(self)
                
            # Reset initialization event
            self._initialized_event.clear()
            
        except Exception as e:
            self._error = e
            self._state = ModuleState.ERROR
            raise ModuleError(
                f"Failed to cleanup module {self.config.name}",
                cause=e,
            )

    async def wait_initialized(self) -> None:
        """Wait for module to be initialized.
        
        Raises:
            ModuleError: If module is in error state
        """
        if self._state == ModuleState.ERROR:
            raise ModuleError(
                f"Module {self.config.name} is in error state: {self._error}",
                cause=self._error,
            )
            
        await self._initialized_event.wait()

    def _ensure_initialized(self) -> None:
        """Ensure module is initialized.

        Raises:
            StateError: If module is not initialized
            ModuleError: If module is in error state
        """
        if self._state == ModuleState.ERROR:
            raise ModuleError(
                f"Module {self.config.name} is in error state: {self._error}",
                cause=self._error,
            )
        if not self.is_initialized:
            raise StateError(f"Module {self.config.name} not initialized (state: {self._state})")

    @abstractmethod
    async def _setup(self) -> None:
        """Setup module resources. Override this method to implement initialization logic."""
        pass

    @abstractmethod
    async def _teardown(self) -> None:
        """Teardown module resources. Override this method to implement cleanup logic."""
        pass

    async def get_stats(self) -> dict[str, Any]:
        """Get module statistics.

        Returns:
            Module statistics

        Raises:
            StateError: If module is not initialized
        """
        self._ensure_initialized()
        
        stats = {
            "name": self.config.name,
            "enabled": self.config.enabled,
            "state": str(self._state),
            "initialized": self.is_initialized,
            "has_error": self._error is not None,
            "error_message": str(self._error) if self._error else None,
            "metadata": self.config.metadata,
            "dependencies": {
                name: {
                    "name": dep.name,
                    "module": dep.module.config.name,
                    "optional": dep.optional,
                    "lazy": dep.lazy,
                    "initialized": dep.module.is_initialized,
                }
                for name, dep in self._dependencies.items()
            },
            "hooks": [hook.__class__.__name__ for hook in self._hooks],
        }
        
        return stats

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

    def set_item(self, name: str, value: T) -> None:
        """Set item value.
        
        Args:
            name: Item name
            value: Item value
            
        Raises:
            StateError: If manager not initialized
            ModuleError: If manager is in error state
            ValueError: If name is empty or value has wrong type
        """
        if not name:
            raise ValueError("name cannot be empty")
            
        item_type = self._get_item_type()
        if not isinstance(value, item_type):
            raise ValueError(f"Value must be of type {item_type.__name__}, got {type(value).__name__}")
            
        self._ensure_initialized()
        self._items[name] = value

    def remove_item(self, name: str) -> None:
        """Remove item by name.
        
        Args:
            name: Item name
            
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
        del self._items[name]

    def _get_item_type(self) -> type:
        """Get the type of items managed by this manager."""
        # Get the second type argument (T) from the generic base class
        base = self.__orig_bases__[0]  # type: ignore
        return base.__args__[1]  # type: ignore

__all__ = [
    "ModuleState",
    "DependencyInfo",
    "LifecycleHook",
    "BaseModule",
    "BaseManager",
]
