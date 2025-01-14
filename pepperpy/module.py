"""Module base implementation.

This module provides the base infrastructure for creating modular components in
PepperPy. It implements the Template Method pattern to define a consistent
lifecycle for all modules, including initialization, setup, and teardown phases.

The module system provides:
- Consistent module lifecycle management
- Type-safe configuration handling
- Proper cleanup of resources
- Extensible module hierarchy
- Resource management capabilities

Example:
    A simple cache module implementation:

    ```python
    class CacheModule(BaseModule):
        def __init__(self, config: CacheConfig) -> None:
            super().__init__(config)
            self._cache = {}

        async def _setup(self) -> None:
            # Set up cache
            self._cache = {}

        async def _teardown(self) -> None:
            # Clean up cache
            self._cache.clear()

        def get(self, key: str) -> Any:
            self._ensure_initialized()
            if key in self._cache:
                self._hits += 1
                return self._cache[key]
            self._misses += 1
            return None
    ```
"""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Generic, TypedDict, TypeVar

from .core import PepperpyError


class ModuleError(PepperpyError):
    """Module-related errors."""

    pass


class InitializationError(ModuleError):
    """Module initialization errors."""

    pass


@dataclass
class ModuleConfig:
    """Base module configuration."""

    name: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate configuration after initialization.

        Raises:
            ValueError: If name is empty or invalid
        """
        if not self.name:
            raise ValueError("Module name cannot be empty")
        if not isinstance(self.name, str):
            raise ValueError("Module name must be a string")


class ResourceValue(TypedDict, total=False):
    """Type hints for resource values."""

    value: str | int | float | bool | dict | list | None
    metadata: dict[str, str | int | float | bool | dict | list | None]


T = TypeVar("T", bound=ModuleConfig)


class BaseModule(Generic[T], ABC):
    """Base module implementation."""

    def __init__(self, config: T) -> None:
        """Initialize module.

        Args:
            config: Module configuration
        """
        self.config = config
        self._is_initialized = False
        self._resources: dict[str, ResourceValue] = {}

    @property
    def is_initialized(self) -> bool:
        """Get initialization state.

        Returns:
            True if module is initialized, False otherwise
        """
        return self._is_initialized

    async def initialize(self) -> None:
        """Initialize module.

        Raises:
            InitializationError: If module is already initialized
        """
        if self.is_initialized:
            raise InitializationError(
                f"Module {self.config.name} is already initialized"
            )

        await self._setup()
        self._is_initialized = True

    async def teardown(self) -> None:
        """Teardown module."""
        if not self.is_initialized:
            return

        await self._teardown()
        self._is_initialized = False

    def _ensure_initialized(self) -> None:
        """Ensure module is initialized."""
        if not self.is_initialized:
            raise ModuleError(f"Module {self.config.name} is not initialized")

    def get_resource(self, key: str) -> ResourceValue | None:
        """Get module resource.

        Args:
            key: Resource key.

        Returns:
            ResourceValue | None: Resource value or None if not found.
        """
        self._ensure_initialized()
        return self._resources.get(key)

    def set_resource(self, key: str, value: ResourceValue) -> None:
        """Set module resource.

        Args:
            key: Resource key.
            value: Resource value.
        """
        self._ensure_initialized()
        self._resources[key] = value

    def get_resources(self) -> Mapping[str, ResourceValue]:
        """Get all module resources.

        Returns:
            Mapping[str, ResourceValue]: Dictionary of resources.
        """
        self._ensure_initialized()
        return self._resources

    @abstractmethod
    async def _setup(self) -> None:
        """Setup module."""
        pass

    @abstractmethod
    async def _teardown(self) -> None:
        """Teardown module."""
        pass
