"""Tests for the network module."""

import asyncio
from typing import AsyncGenerator

import pytest

from pepperpy_core.network import NetworkClient, NetworkConfig


class MockServer:
    """Mock server for testing."""

    def __init__(self, host: str, port: int) -> None:
        """Initialize mock server.

        Args:
            host: Server host
            port: Server port
        """
        self.host = host
        self.port = port
        self._server: asyncio.AbstractServer | None = None

    async def start(self) -> None:
        """Start server."""
        self._server = await asyncio.start_server(
            self._handle_client, self.host, self.port
        )

    async def stop(self) -> None:
        """Stop server."""
        if self._server:
            self._server.close()
            await self._server.wait_closed()

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """Handle client connection.

        Args:
            reader: Stream reader
            writer: Stream writer
        """
        while True:
            try:
                data = await reader.read(1024)
                if not data:
                    break
                writer.write(data)
                await writer.drain()
            except ConnectionError:
                break
        writer.close()
        await writer.wait_closed()


@pytest.fixture
async def mock_server() -> AsyncGenerator[MockServer, None]:
    """Create a mock server for testing."""
    server = MockServer("localhost", 8080)
    await server.start()
    yield server
    await server.stop()


@pytest.fixture
async def network_client(
    mock_server: MockServer,
) -> AsyncGenerator[NetworkClient, None]:
    """Create a network client for testing."""
    config = NetworkConfig(host=mock_server.host, port=mock_server.port)
    client = NetworkClient(config)
    await client.connect()
    yield client
    await client.disconnect()


@pytest.mark.asyncio
async def test_network_client_connect(network_client: NetworkClient) -> None:
    """Test network client connection."""
    assert network_client._config.host == "localhost"
    assert network_client._config.port == 8080


@pytest.mark.asyncio
async def test_network_client_disconnect(network_client: NetworkClient) -> None:
    """Test network client disconnection."""
    await network_client.disconnect()
    assert not network_client.is_connected


@pytest.mark.asyncio
async def test_network_client_send(network_client: NetworkClient) -> None:
    """Test network client send."""
    data = b"test"
    await network_client.send(data)
    received = await network_client.receive(size=len(data))
    assert received == data


@pytest.mark.asyncio
async def test_network_client_receive(network_client: NetworkClient) -> None:
    """Test network client receive."""
    data = b"test"
    await network_client.send(data)
    received = await network_client.receive(size=len(data))
    assert received == data


@pytest.mark.asyncio
async def test_network_client_context_manager(mock_server: MockServer) -> None:
    """Test network client context manager."""
    config = NetworkConfig(host=mock_server.host, port=mock_server.port)
    async with NetworkClient(config) as client:
        assert client.is_connected
        assert client._config.host == mock_server.host
        assert client._config.port == mock_server.port


@pytest.mark.asyncio
async def test_network_client_repr(network_client: NetworkClient) -> None:
    """Test network client string representation."""
    expected = (
        f"NetworkClient(host={network_client._config.host}, "
        f"port={network_client._config.port})"
    )
    assert repr(network_client) == expected
