"""Tests for the network module."""
# mypy: disable-error-code=unreachable

import asyncio
from typing import AsyncGenerator

import pytest
from aiohttp import ClientSession, ClientTimeout, web

from pepperpy.network import (
    HTTPClient,
    NetworkClient,
    NetworkConfig,
    NetworkError,
    RequestData,
)


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
        self._last_request: bytes | None = None

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
                self._last_request = data
                writer.write(data)
                await writer.drain()
            except ConnectionError:
                break
        writer.close()
        await writer.wait_closed()

    @property
    def last_request(self) -> bytes | None:
        """Get the last received request."""
        return self._last_request


class MockHTTPServer:
    """Mock HTTP server for testing."""

    def __init__(self, host: str, port: int) -> None:
        """Initialize mock HTTP server.

        Args:
            host: Server host
            port: Server port
        """
        self.host = host
        self.port = port
        self._runner: web.AppRunner | None = None
        self._site: web.TCPSite | None = None
        self._app = web.Application()
        self._app.router.add_routes(
            [
                web.get("/{tail:.*}", self._handle_request),
                web.post("/{tail:.*}", self._handle_request),
                web.put("/{tail:.*}", self._handle_request),
                web.delete("/{tail:.*}", self._handle_request),
            ]
        )

    async def start(self) -> None:
        """Start server."""
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, self.host, self.port)
        await self._site.start()

    async def stop(self) -> None:
        """Stop server."""
        if self._runner:
            await self._runner.cleanup()
            self._runner = None
            self._site = None

    async def _handle_request(self, request: web.Request) -> web.Response:
        """Handle HTTP request.

        Args:
            request: HTTP request

        Returns:
            HTTP response
        """
        return web.Response(text="OK")


@pytest.fixture
def test_host() -> str:
    """Get test host."""
    return "localhost"


@pytest.fixture
def test_port() -> int:
    """Get test port."""
    return 8080


@pytest.fixture
def test_url(test_host: str, test_port: int) -> str:
    """Get test URL."""
    return f"http://{test_host}:{test_port}/"


@pytest.fixture
def test_params() -> dict[str, str]:
    """Get test query parameters."""
    return {"key": "value"}


@pytest.fixture
def test_headers() -> dict[str, str]:
    """Get test headers."""
    return {"User-Agent": "test"}


@pytest.fixture
def test_timeout() -> ClientTimeout:
    """Get test timeout."""
    return ClientTimeout(total=5)


@pytest.fixture
def test_json() -> RequestData:
    """Get test JSON data."""
    return {"str_value": "test"}


@pytest.fixture
async def mock_server(
    test_host: str, test_port: int
) -> AsyncGenerator[MockServer, None]:
    """Create a mock server for testing."""
    server = MockServer(test_host, test_port)
    await server.start()
    yield server
    await server.stop()


@pytest.fixture
async def mock_http_server(
    test_host: str, test_port: int
) -> AsyncGenerator[MockHTTPServer, None]:
    """Create a mock HTTP server for testing."""
    server = MockHTTPServer(test_host, test_port)
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


@pytest.fixture
async def http_client() -> AsyncGenerator[HTTPClient, None]:
    """Create an HTTP client for testing."""
    client = HTTPClient()
    await client.initialize()
    yield client
    await client.cleanup()


@pytest.mark.asyncio
async def test_network_client_connect(
    network_client: NetworkClient, test_host: str, test_port: int
) -> None:
    """Test network client connection."""
    assert network_client._config.host == test_host
    assert network_client._config.port == test_port


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
async def test_network_client_context_manager(
    mock_server: MockServer, test_host: str, test_port: int
) -> None:
    """Test network client context manager."""
    config = NetworkConfig(host=test_host, port=test_port)
    async with NetworkClient(config) as client:
        assert client.is_connected
        assert client._config.host == test_host
        assert client._config.port == test_port


@pytest.mark.asyncio
async def test_network_client_repr(
    network_client: NetworkClient, test_host: str, test_port: int
) -> None:
    """Test network client string representation."""
    expected = f"NetworkClient(host={test_host}, port={test_port})"
    assert repr(network_client) == expected


@pytest.mark.asyncio
async def test_http_client_initialize_and_cleanup() -> None:
    """Test HTTP client initialization and cleanup."""
    client = HTTPClient()
    assert not client._initialized
    assert client._session is None

    await client.initialize()
    assert client._initialized
    assert isinstance(client._session, ClientSession)

    await client.cleanup()
    assert not client._initialized
    assert client._session is None


@pytest.mark.asyncio
async def test_http_client_session_property() -> None:
    """Test HTTP client session property.

    Note:
        There is a known issue with mypy's control flow analysis where it incorrectly
        marks the session property access as unreachable. This is a false positive
        as the code is working correctly and all tests pass.
    """
    # Test not initialized case
    client = HTTPClient()
    with pytest.raises(NetworkError):
        _ = client.session

    # Test initialized case
    await client.initialize()
    session = client.session
    assert isinstance(session, ClientSession)
    await client.cleanup()


@pytest.mark.asyncio
async def test_http_client_context_manager() -> None:
    """Test HTTP client context manager."""
    async with HTTPClient() as client:
        assert client._initialized
        assert isinstance(client._session, ClientSession)


@pytest.mark.asyncio
async def test_http_client_get(
    http_client: HTTPClient,
    mock_http_server: MockHTTPServer,
    test_url: str,
    test_params: dict[str, str],
    test_headers: dict[str, str],
    test_timeout: ClientTimeout,
) -> None:
    """Test HTTP client GET request."""
    response = await http_client.get(
        test_url,
        params=test_params,
        headers=test_headers,
        timeout=test_timeout,
        verify_ssl=True,
    )
    assert response == "OK"


@pytest.mark.asyncio
async def test_http_client_post(
    http_client: HTTPClient,
    mock_http_server: MockHTTPServer,
    test_url: str,
    test_params: dict[str, str],
    test_headers: dict[str, str],
    test_timeout: ClientTimeout,
    test_json: RequestData,
) -> None:
    """Test HTTP client POST request."""
    response = await http_client.post(
        test_url,
        params=test_params,
        headers=test_headers,
        timeout=test_timeout,
        verify_ssl=True,
        json=test_json,
    )
    assert response == "OK"


@pytest.mark.asyncio
async def test_http_client_put(
    http_client: HTTPClient,
    mock_http_server: MockHTTPServer,
    test_url: str,
    test_params: dict[str, str],
    test_headers: dict[str, str],
    test_timeout: ClientTimeout,
    test_json: RequestData,
) -> None:
    """Test HTTP client PUT request."""
    response = await http_client.put(
        test_url,
        params=test_params,
        headers=test_headers,
        timeout=test_timeout,
        verify_ssl=True,
        json=test_json,
    )
    assert response == "OK"


@pytest.mark.asyncio
async def test_http_client_delete(
    http_client: HTTPClient,
    mock_http_server: MockHTTPServer,
    test_url: str,
    test_params: dict[str, str],
    test_headers: dict[str, str],
    test_timeout: ClientTimeout,
) -> None:
    """Test HTTP client DELETE request."""
    response = await http_client.delete(
        test_url,
        params=test_params,
        headers=test_headers,
        timeout=test_timeout,
        verify_ssl=True,
    )
    assert response == "OK"


@pytest.mark.asyncio
async def test_http_client_request_error(
    mock_server: MockServer, test_url: str
) -> None:
    """Test HTTP client request error."""
    # Stop the server to simulate a connection error
    await mock_server.stop()

    client = HTTPClient()
    with pytest.raises(NetworkError):
        await client._request(
            "GET",
            test_url,
        )
