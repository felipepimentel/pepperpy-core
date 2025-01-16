"""Module base classes."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Generic, TypeVar

TConfig = TypeVar("TConfig", bound="ModuleConfig")


@dataclass
class ModuleConfig:
    """Module configuration."""

    name: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseModule(Generic[TConfig], ABC):
    """Base module."""

    def __init__(self, config: TConfig) -> None:
        """Initialize module.

        Args:
            config: Module configuration.

        Raises:
            ValueError: If module name is invalid.
        """
        if not config.name:
            raise ValueError("Module name cannot be empty")
        if not config.name.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Module name must be alphanumeric")
        self.config = config
        self._initialized = False

    @property
    def is_initialized(self) -> bool:
        """Get initialization status.

        Returns:
            True if module is initialized, False otherwise.
        """
        return self._initialized

    async def initialize(self) -> None:
        """Initialize module."""
        if not self.is_initialized:
            await self._setup()
            self._initialized = True

    async def teardown(self) -> None:
        """Clean up module."""
        if self.is_initialized:
            await self._teardown()
            self._initialized = False

    @abstractmethod
    async def _setup(self) -> None:
        """Set up module."""
        ...

    @abstractmethod
    async def _teardown(self) -> None:
        """Clean up module."""
        ...
