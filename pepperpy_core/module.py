"""Module base implementation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from .exceptions import InitializationError, PepperpyError
from .types import BaseConfig


class ModuleError(PepperpyError):
    """Module specific error."""

    pass


@dataclass
class ModuleConfig(BaseConfig):
    """Module configuration."""

    name: str
    metadata: dict[str, Any] = field(default_factory=dict)


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
