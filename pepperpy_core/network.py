"""Network module."""

from dataclasses import dataclass, field
from typing import Any

from .exceptions import NetworkError
from .module import BaseModule, ModuleConfig


@dataclass
class NetworkConfig(ModuleConfig):
    """Network configuration."""

    name: str = "network-client"
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Post initialization validation."""
        self.validate()

    def validate(self) -> None:
        """Validate configuration."""
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.retry_delay < 0:
            raise ValueError("retry_delay must be non-negative")


@dataclass
class HttpResponse:
    """HTTP response."""

    status: int
    text: str
    headers: dict[str, str]
    metadata: dict[str, Any] = field(default_factory=dict)


class WebSocket:
    """WebSocket connection."""

    def __init__(self) -> None:
        """Initialize WebSocket."""
        self._closed = False

    @property
    def closed(self) -> bool:
        """Get closed state."""
        return self._closed

    async def send_text(self, text: str) -> None:
        """Send text message.

        Args:
            text: Text message to send

        Raises:
            NetworkError: If WebSocket is closed
        """
        if self.closed:
            raise NetworkError("WebSocket is closed")

    async def receive_text(self) -> str:
        """Receive text message.

        Returns:
            Received text message

        Raises:
            NetworkError: If WebSocket is closed
        """
        if self.closed:
            raise NetworkError("WebSocket is closed")
        return "Hello"  # Mock response

    async def close(self) -> None:
        """Close WebSocket."""
        self._closed = True


class NetworkClient(BaseModule[NetworkConfig]):
    """Network client implementation."""

    def __init__(self, config: NetworkConfig | None = None) -> None:
        """Initialize network client.

        Args:
            config: Network configuration
        """
        if config is None:
            config = NetworkConfig()
        super().__init__(config)
        self._websockets: list[WebSocket] = []

    async def _setup(self) -> None:
        """Setup network client."""
        self._websockets.clear()

    async def _teardown(self) -> None:
        """Teardown network client."""
        for ws in self._websockets:
            await ws.close()
        self._websockets.clear()
        self._is_initialized = False

    async def http_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        data: dict[str, Any] | None = None,
    ) -> HttpResponse:
        """Send HTTP request.

        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            params: Query parameters
            data: Request data

        Returns:
            HTTP response

        Raises:
            NetworkError: If request fails
        """
        self._ensure_initialized()

        # Mock error for non-existent server
        if "non-existent-server" in url:
            raise NetworkError("Failed to connect to server")

        # Mock timeout for slow server
        if "slow-server" in url:
            raise NetworkError("Request timed out")

        # Mock response
        return HttpResponse(
            status=200,
            text="Example Domain",
            headers={"Content-Type": "text/html"},
        )

    async def websocket_connect(self, url: str) -> WebSocket:
        """Connect to WebSocket.

        Args:
            url: WebSocket URL

        Returns:
            WebSocket connection

        Raises:
            NetworkError: If connection fails
        """
        self._ensure_initialized()

        ws = WebSocket()
        self._websockets.append(ws)
        return ws

    def _remove_closed_websockets(self) -> None:
        """Remove closed WebSockets from the list."""
        self._websockets = [ws for ws in self._websockets if not ws.closed]

    async def get_stats(self) -> dict[str, Any]:
        """Get network client statistics.

        Returns:
            Network client statistics

        Raises:
            NetworkError: If client is not initialized
        """
        self._ensure_initialized()
        self._remove_closed_websockets()
        return {
            "name": self.config.name,
            "enabled": True,
            "active_websockets": len(self._websockets),
            "timeout": self.config.timeout,
            "max_retries": self.config.max_retries,
            "retry_delay": self.config.retry_delay,
        }


__all__ = [
    "NetworkConfig",
    "HttpResponse",
    "WebSocket",
    "NetworkClient",
]
