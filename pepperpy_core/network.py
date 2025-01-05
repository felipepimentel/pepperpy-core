"""Network module."""

import asyncio
from dataclasses import dataclass
from typing import Optional


class NetworkError(Exception):
    """Network error."""

    pass


@dataclass
class NetworkConfig:
    """Network configuration."""

    host: str
    port: int
    timeout: float = 5.0
    retries: int = 3
    retry_delay: float = 1.0

    def __post_init__(self) -> None:
        """Validate configuration."""
        if not isinstance(self.host, str):
            raise TypeError("Host must be a string")
        if not isinstance(self.port, int):
            raise TypeError("Port must be an integer")
        if not isinstance(self.timeout, (int, float)):
            raise TypeError("Timeout must be a number")
        if not isinstance(self.retries, int):
            raise TypeError("Retries must be an integer")
        if not isinstance(self.retry_delay, (int, float)):
            raise TypeError("Retry delay must be a number")

        if not self.host:
            raise ValueError("Host cannot be empty")
        if self.port < 1:
            raise ValueError("Port must be greater than 0")
        if self.timeout <= 0:
            raise ValueError("Timeout must be greater than 0")
        if self.retries < 0:
            raise ValueError("Retries must be greater than or equal to 0")
        if self.retry_delay <= 0:
            raise ValueError("Retry delay must be greater than 0")


class NetworkClient:
    """Network client implementation."""

    def __init__(self, config: NetworkConfig) -> None:
        """Initialize network client.

        Args:
            config: Network configuration
        """
        self._config = config
        self._host = config.host
        self._port = config.port
        self._timeout = config.timeout
        self._retries = config.retries
        self._retry_delay = config.retry_delay
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected

    async def connect(self) -> None:
        """Connect to server.

        Raises:
            NetworkError: If connection fails
        """
        try:
            self._reader, self._writer = await asyncio.open_connection(
                self._host, self._port
            )
            self._connected = True
        except OSError as e:
            raise NetworkError(f"Failed to connect: {e}") from e

    async def disconnect(self) -> None:
        """Disconnect from server."""
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
            self._writer = None
            self._reader = None
            self._connected = False

    async def send(self, data: bytes) -> None:
        """Send data to server.

        Args:
            data: Data to send

        Raises:
            NetworkError: If sending fails
        """
        if not self._writer or not self._connected:
            raise NetworkError("Not connected")

        retries = 0
        while retries <= self._retries:
            try:
                self._writer.write(data)
                await self._writer.drain()
                return
            except ConnectionError:
                retries += 1
                if retries <= self._retries:
                    await asyncio.sleep(self._retry_delay)
                continue

        raise NetworkError("Failed to send data: max retries exceeded")

    async def receive(self, size: int) -> bytes:
        """Receive data from server.

        Args:
            size: Number of bytes to receive

        Returns:
            Received data

        Raises:
            NetworkError: If receiving fails
        """
        if not self._reader or not self._connected:
            raise NetworkError("Not connected")

        retries = 0
        while retries <= self._retries:
            try:
                data = await self._reader.read(size)
                return data
            except ConnectionError:
                retries += 1
                if retries <= self._retries:
                    await asyncio.sleep(self._retry_delay)
                continue

        raise NetworkError("Failed to receive data: max retries exceeded")

    async def __aenter__(self) -> "NetworkClient":
        """Enter async context."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[object],
    ) -> None:
        """Exit async context."""
        await self.disconnect()

    def __repr__(self) -> str:
        """Get string representation."""
        return f"NetworkClient(host={self._host}, port={self._port})"
