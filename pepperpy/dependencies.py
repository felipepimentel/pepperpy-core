"""Dependencies module."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from pepperpy.core import PepperpyError
from pepperpy.module import BaseModule, ModuleConfig


class DependencyError(PepperpyError):
    """Dependency error."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, details, cause)


@dataclass
class DependencyConfig(ModuleConfig):
    """Dependency configuration."""

    name: str = "dependency_manager"
    metadata: Dict[str, Any] = field(default_factory=dict)


class DependencyManager(BaseModule[DependencyConfig]):
    """Dependency manager."""

    def __init__(self, config: Optional[DependencyConfig] = None) -> None:
        """Initialize dependency manager.

        Args:
            config: Dependency configuration
        """
        super().__init__(config or DependencyConfig())
        self._dependencies: Dict[str, Any] = {}

    def _ensure_initialized(self) -> None:
        """Ensure manager is initialized.

        Raises:
            DependencyError: If manager is not initialized
        """
        if not self.is_initialized:
            raise DependencyError(
                "Dependency manager is not initialized",
                {"manager_name": self.config.name},
            )

    async def _setup(self) -> None:
        """Set up dependency manager."""
        self._dependencies = {}

    async def _teardown(self) -> None:
        """Clean up dependency manager."""
        self._dependencies = {}

    def register(self, name: str, dependency: Any) -> None:
        """Register dependency.

        Args:
            name: Dependency name
            dependency: Dependency instance

        Raises:
            DependencyError: If dependency cannot be registered
        """
        self._ensure_initialized()
        if name in self._dependencies:
            raise DependencyError(
                "Dependency already registered",
                {"name": name, "manager_name": self.config.name},
            )
        self._dependencies[name] = dependency

    def get(self, name: str) -> Any:
        """Get dependency.

        Args:
            name: Dependency name

        Returns:
            Dependency instance

        Raises:
            DependencyError: If dependency is not found
        """
        self._ensure_initialized()
        if name not in self._dependencies:
            raise DependencyError(
                "Dependency not found",
                {"name": name, "manager_name": self.config.name},
            )
        return self._dependencies[name]

    def unregister(self, name: str) -> None:
        """Unregister dependency.

        Args:
            name: Dependency name

        Raises:
            DependencyError: If dependency cannot be unregistered
        """
        self._ensure_initialized()
        if name not in self._dependencies:
            raise DependencyError(
                "Dependency not found",
                {"name": name, "manager_name": self.config.name},
            )
        del self._dependencies[name]

    def clear(self) -> None:
        """Clear all dependencies.

        Raises:
            DependencyError: If dependencies cannot be cleared
        """
        self._ensure_initialized()
        self._dependencies = {}


__all__ = ["DependencyConfig", "DependencyError", "DependencyManager"]
