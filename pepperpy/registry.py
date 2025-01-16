"""Registry module."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Generic, Optional, TypeVar

from pepperpy.module import BaseModule, ModuleConfig

T = TypeVar("T", bound="RegistryProtocol")


class RegistryError(Exception):
    """Registry error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize error.

        Args:
            message: Error message.
            details: Error details.
        """
        super().__init__(message)
        self.details = details or {}


class RegistryProtocol(ABC):
    """Registry protocol."""

    @abstractmethod
    def register(self, name: str, implementation: Any) -> None:
        """Register implementation.

        Args:
            name: Implementation name.
            implementation: Implementation instance.
        """
        ...

    @abstractmethod
    def get(self, name: str) -> Any:
        """Get implementation.

        Args:
            name: Implementation name.

        Returns:
            Implementation instance.
        """
        ...

    @abstractmethod
    def list(self) -> Dict[str, Any]:
        """List implementations.

        Returns:
            Dictionary of implementation names and instances.
        """
        ...


@dataclass
class RegistryConfig(ModuleConfig):
    """Registry configuration."""

    name: str = "registry"
    metadata: Dict[str, Any] = field(default_factory=dict)


class Registry(BaseModule[RegistryConfig], Generic[T]):
    """Registry implementation."""

    def __init__(self, config: Optional[RegistryConfig] = None) -> None:
        """Initialize registry.

        Args:
            config: Registry configuration.
        """
        super().__init__(config or RegistryConfig())
        self._implementations: Dict[str, T] = {}

    def _ensure_initialized(self) -> None:
        """Ensure registry is initialized."""
        if not self.is_initialized:
            raise RegistryError(
                "Registry is not initialized",
                {"registry_name": self.config.name},
            )

    async def _setup(self) -> None:
        """Set up registry."""
        pass

    async def _teardown(self) -> None:
        """Clean up registry."""
        self._implementations = {}

    def register(self, name: str, implementation: T) -> None:
        """Register implementation.

        Args:
            name: Implementation name.
            implementation: Implementation instance.

        Raises:
            RegistryError: If implementation already exists.
        """
        self._ensure_initialized()
        if name in self._implementations:
            raise RegistryError(
                "Implementation already exists",
                {"name": name, "registry_name": self.config.name},
            )
        self._implementations[name] = implementation

    def get(self, name: str) -> T:
        """Get implementation.

        Args:
            name: Implementation name.

        Returns:
            Implementation instance.

        Raises:
            RegistryError: If implementation does not exist.
        """
        self._ensure_initialized()
        if name not in self._implementations:
            raise RegistryError(
                "Implementation not found",
                {"name": name, "registry_name": self.config.name},
            )
        return self._implementations[name]

    def list(self) -> Dict[str, T]:
        """List implementations.

        Returns:
            Dictionary of implementation names and instances.
        """
        self._ensure_initialized()
        return self._implementations.copy()


__all__ = ["Registry", "RegistryConfig", "RegistryError", "RegistryProtocol"]
