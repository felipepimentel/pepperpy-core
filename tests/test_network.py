"""Tests for the network module."""

import pytest
import pytest_asyncio

from pepperpy_core.exceptions import NetworkError
from pepperpy_core.module import ModuleError
from pepperpy_core.network import (
    HttpResponse,
    NetworkClient,
    NetworkConfig,
    WebSocket,
)


def test_network_config_validation() -> None:
    """Test network configuration validation."""
    # Test default values
    config = NetworkConfig()
    assert config.name == "network-client"
    assert config.timeout == 30.0
    assert config.max_retries == 3
    assert config.retry_delay == 1.0
    assert config.metadata == {}

    # Test custom values
    config = NetworkConfig(
        name="custom-client",
        timeout=10.0,
        max_retries=5,
        retry_delay=0.5,
        metadata={"key": "value"},
    )
    assert config.name == "custom-client"
    assert config.timeout == 10.0
    assert config.max_retries == 5
    assert config.retry_delay == 0.5
    assert config.metadata == {"key": "value"}

    # Test validation errors
    with pytest.raises(ValueError, match="timeout must be positive"):
        NetworkConfig(timeout=0)

    with pytest.raises(ValueError, match="timeout must be positive"):
        NetworkConfig(timeout=-1.0)

    with pytest.raises(ValueError, match="max_retries must be non-negative"):
        NetworkConfig(max_retries=-1)

    with pytest.raises(ValueError, match="retry_delay must be non-negative"):
        NetworkConfig(retry_delay=-0.5)


@pytest.mark.asyncio
async def test_websocket() -> None:
    """Test WebSocket functionality."""
    ws = WebSocket()
    assert not ws.closed

    # Test send and receive
    await ws.send_text("Hello")
    response = await ws.receive_text()
    assert response == "Hello"  # Mock response

    # Test closing
    await ws.close()
    assert ws.closed

    # Test operations on closed WebSocket
    with pytest.raises(NetworkError, match="WebSocket is closed"):
        await ws.send_text("Hello")

    with pytest.raises(NetworkError, match="WebSocket is closed"):
        await ws.receive_text()


@pytest_asyncio.fixture
async def network_client():
    """Create a network client for testing."""
    client = NetworkClient()
    await client.initialize()
    yield client
    await client.teardown()


@pytest.mark.asyncio
async def test_network_client_initialization() -> None:
    """Test network client initialization."""
    client = NetworkClient()
    assert not client.is_initialized

    await client.initialize()
    assert client.is_initialized

    await client.teardown()
    assert not client.is_initialized


@pytest.mark.asyncio
async def test_network_client_http_request(network_client) -> None:
    """Test HTTP request functionality."""
    # Test successful request
    response = await network_client.http_request(
        method="GET",
        url="https://example.com",
        headers={"User-Agent": "Test"},
        params={"key": "value"},
        data={"data": "test"},
    )
    assert isinstance(response, HttpResponse)
    assert response.status == 200
    assert response.text == "Example Domain"
    assert response.headers == {"Content-Type": "text/html"}

    # Test request to non-existent server
    with pytest.raises(NetworkError, match="Failed to connect to server"):
        await network_client.http_request(
            method="GET",
            url="https://non-existent-server.com",
        )

    # Test request to slow server
    with pytest.raises(NetworkError, match="Request timed out"):
        await network_client.http_request(
            method="GET",
            url="https://slow-server.com",
        )


@pytest.mark.asyncio
async def test_network_client_websocket(network_client) -> None:
    """Test WebSocket functionality in network client."""
    # Connect to WebSocket
    ws = await network_client.websocket_connect("wss://example.com")
    assert isinstance(ws, WebSocket)
    assert not ws.closed
    assert len(network_client._websockets) == 1

    # Test WebSocket operations
    await ws.send_text("Hello")
    response = await ws.receive_text()
    assert response == "Hello"  # Mock response

    # Close WebSocket
    await ws.close()
    assert ws.closed

    # Test WebSocket cleanup
    stats = await network_client.get_stats()
    assert stats["active_websockets"] == 0


@pytest.mark.asyncio
async def test_network_client_multiple_websockets(network_client) -> None:
    """Test handling multiple WebSocket connections."""
    # Create multiple WebSocket connections
    ws1 = await network_client.websocket_connect("wss://example1.com")
    ws2 = await network_client.websocket_connect("wss://example2.com")
    ws3 = await network_client.websocket_connect("wss://example3.com")

    assert len(network_client._websockets) == 3

    # Close some WebSockets
    await ws1.close()
    await ws2.close()

    # Check stats after closing
    stats = await network_client.get_stats()
    assert stats["active_websockets"] == 1

    # Close remaining WebSocket
    await ws3.close()
    stats = await network_client.get_stats()
    assert stats["active_websockets"] == 0


@pytest.mark.asyncio
async def test_network_client_stats(network_client) -> None:
    """Test network client statistics."""
    stats = await network_client.get_stats()
    assert stats["name"] == "network-client"
    assert stats["enabled"] is True
    assert stats["active_websockets"] == 0
    assert stats["timeout"] == 30.0
    assert stats["max_retries"] == 3
    assert stats["retry_delay"] == 1.0

    # Test stats with custom configuration
    custom_config = NetworkConfig(
        name="custom-client",
        timeout=10.0,
        max_retries=5,
        retry_delay=0.5,
    )
    custom_client = NetworkClient(custom_config)
    await custom_client.initialize()

    stats = await custom_client.get_stats()
    assert stats["name"] == "custom-client"
    assert stats["timeout"] == 10.0
    assert stats["max_retries"] == 5
    assert stats["retry_delay"] == 0.5

    await custom_client.teardown()


@pytest.mark.asyncio
async def test_network_client_uninitialized_operations() -> None:
    """Test operations on uninitialized network client."""
    client = NetworkClient()

    with pytest.raises(ModuleError):
        await client.http_request("GET", "https://example.com")

    with pytest.raises(ModuleError):
        await client.websocket_connect("wss://example.com")

    with pytest.raises(ModuleError):
        await client.get_stats()


@pytest.mark.asyncio
async def test_network_client_teardown_cleanup(network_client) -> None:
    """Test cleanup during network client teardown."""
    # Create multiple WebSocket connections
    ws1 = await network_client.websocket_connect("wss://example1.com")
    ws2 = await network_client.websocket_connect("wss://example2.com")

    assert len(network_client._websockets) == 2

    # Teardown should close all WebSockets
    await network_client.teardown()
    assert ws1.closed
    assert ws2.closed
    assert len(network_client._websockets) == 0
    assert not network_client.is_initialized
