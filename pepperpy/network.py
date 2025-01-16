"""Network module."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from pepperpy.core import PepperpyError
from pepperpy.module import BaseModule, ModuleConfig


class NetworkError(PepperpyError):
    """Network error."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, details, cause)


@dataclass
class NetworkConfig(ModuleConfig):
    """Network configuration."""

    name: str = "network_manager"
    metadata: Dict[str, Any] = field(default_factory=dict)


class NetworkManager(BaseModule[NetworkConfig]):
    """Network manager."""

    def __init__(self, config: Optional[NetworkConfig] = None) -> None:
        """Initialize network manager.

        Args:
            config: Network configuration
        """
        super().__init__(config or NetworkConfig())

    def _ensure_initialized(self) -> None:
        """Ensure manager is initialized.

        Raises:
            NetworkError: If manager is not initialized
        """
        if not self.is_initialized:
            raise NetworkError(
                "Network manager is not initialized",
                {"manager_name": self.config.name},
            )

    async def _setup(self) -> None:
        """Set up network manager."""
        pass

    async def _teardown(self) -> None:
        """Clean up network manager."""
        pass

    async def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Send HTTP request.

        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            data: Request data

        Returns:
            Response data

        Raises:
            NetworkError: If request fails
        """
        self._ensure_initialized()
        # Implement request logic here
        return {}


__all__ = ["NetworkConfig", "NetworkError", "NetworkManager"]
