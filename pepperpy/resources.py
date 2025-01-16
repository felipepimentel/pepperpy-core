"""Resources module."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from pepperpy.core import PepperpyError
from pepperpy.module import BaseModule, ModuleConfig


class ResourceError(PepperpyError):
    """Resource error."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, details, cause)


@dataclass
class ResourceConfig(ModuleConfig):
    """Resource configuration."""

    name: str = "resource_manager"
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResourceManager(BaseModule[ResourceConfig]):
    """Resource manager."""

    def __init__(self, config: Optional[ResourceConfig] = None) -> None:
        """Initialize resource manager.

        Args:
            config: Resource configuration
        """
        super().__init__(config or ResourceConfig())
        self._resources: Dict[str, Any] = {}

    def _ensure_initialized(self) -> None:
        """Ensure manager is initialized.

        Raises:
            ResourceError: If manager is not initialized
        """
        if not self.is_initialized:
            raise ResourceError(
                "Resource manager is not initialized",
                {"manager_name": self.config.name},
            )

    async def _setup(self) -> None:
        """Set up resource manager."""
        self._resources = {}

    async def _teardown(self) -> None:
        """Clean up resource manager."""
        self._resources = {}

    def register(self, name: str, resource: Any) -> None:
        """Register resource.

        Args:
            name: Resource name
            resource: Resource instance

        Raises:
            ResourceError: If resource cannot be registered
        """
        self._ensure_initialized()
        if name in self._resources:
            raise ResourceError(
                "Resource already registered",
                {"name": name, "manager_name": self.config.name},
            )
        self._resources[name] = resource

    def get(self, name: str) -> Any:
        """Get resource.

        Args:
            name: Resource name

        Returns:
            Resource instance

        Raises:
            ResourceError: If resource is not found
        """
        self._ensure_initialized()
        if name not in self._resources:
            raise ResourceError(
                "Resource not found",
                {"name": name, "manager_name": self.config.name},
            )
        return self._resources[name]

    def unregister(self, name: str) -> None:
        """Unregister resource.

        Args:
            name: Resource name

        Raises:
            ResourceError: If resource cannot be unregistered
        """
        self._ensure_initialized()
        if name not in self._resources:
            raise ResourceError(
                "Resource not found",
                {"name": name, "manager_name": self.config.name},
            )
        del self._resources[name]

    def clear(self) -> None:
        """Clear all resources.

        Raises:
            ResourceError: If resources cannot be cleared
        """
        self._ensure_initialized()
        self._resources = {}


__all__ = ["ResourceConfig", "ResourceError", "ResourceManager"]
