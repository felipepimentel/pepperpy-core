"""Module base implementation.

This module provides the base infrastructure for creating modular components in
PepperPy. It implements the Template Method pattern to define a consistent
lifecycle for all modules, including initialization, setup, and teardown phases.

The module system provides:
- Consistent module lifecycle management
- Type-safe configuration handling
- Proper cleanup of resources
- Extensible module hierarchy

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
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from pepperpy.config import BaseConfig
from pepperpy.core import PepperpyError


class ModuleError(PepperpyError):
    """Module-related errors."""

    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
        module_name: str | None = None,
    ) -> None:
        """Initialize module error.

        Args:
            message: Error message
            cause: Original exception that caused this error
            module_name: Name of the module that caused the error
        """
        super().__init__(message, cause)
        self.module_name = module_name


class InitializationError(ModuleError):
    """Initialization-related errors."""

    pass


class ModuleNotFoundError(ModuleError):
    """Module not found errors."""

    pass


@dataclass
class ModuleConfig(BaseConfig):
    """Module configuration."""

    name: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate configuration after initialization.

        Raises:
            ValueError: If name is empty or invalid
        """
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Module name must be a non-empty string")


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

    @abstractmethod
    async def _setup(self) -> None:
        """Setup module."""
        pass

    @abstractmethod
    async def _teardown(self) -> None:
        """Teardown module."""
        pass


__all__ = [
    "ModuleError",
    "ModuleConfig",
    "BaseModule",
]
