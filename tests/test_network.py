"""Test network module."""

import asyncio
from dataclasses import dataclass
from typing import Any

import pytest
from aiohttp import ClientResponse, ClientSession, FormData
from multidict import MultiDict
from yarl import URL

from pepperpy.network import (
    HTTPClient,
    HTTPConfig,
    NetworkError,
    RequestInterceptor,
    ResponseFormat,
)


@pytest.fixture
async def http_client() -> HTTPClient:
    """Create HTTP client fixture."""
    client = HTTPClient(HTTPConfig(base_url="http://example.com"))
    yield client
    await client.cleanup()


@dataclass
class TestInterceptor(RequestInterceptor):
    """Test interceptor."""

    pre_request_called: bool = False
    post_response_called: bool = False

    async def pre_request(
        self,
        method: str,
        url: str,
        params: MultiDict[str] | dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        proxy: str | None = None,
        timeout: Any | None = None,
        verify_ssl: bool | None = None,
        json: Any | None = None,
        data: FormData | None = None,
    ) -> None:
        """Pre-request hook."""
        self.pre_request_called = True

    async def post_response(self, response: ClientResponse) -> None:
        """Post-response hook."""
        self.post_response_called = True


async def test_http_client_initialization(http_client: HTTPClient) -> None:
    """Test HTTP client initialization."""
    assert not http_client._initialized
    assert http_client._session is None

    await http_client.initialize()
    assert http_client._initialized
    assert isinstance(http_client._session, ClientSession)
    assert http_client._session._base_url == URL("http://example.com")


async def test_http_client_cleanup(http_client: HTTPClient) -> None:
    """Test HTTP client cleanup."""
    await http_client.initialize()
    assert http_client._initialized
    assert http_client._session is not None

    await http_client.cleanup()
    assert not http_client._initialized
    assert http_client._session is None


async def test_http_client_context_manager(http_client: HTTPClient) -> None:
    """Test HTTP client context manager."""
    async with http_client:
        assert http_client._initialized
        assert http_client._session is not None

    assert not http_client._initialized
    assert http_client._session is None


async def test_http_client_request_formats(http_client: HTTPClient) -> None:
    """Test HTTP client request formats."""
    await http_client.initialize()

    # Mock session request method
    async def mock_request(*args: Any, **kwargs: Any) -> Any:
        class MockResponse:
            status = 200
            reason = "OK"

            async def json(self) -> dict[str, str]:
                return {"key": "value"}

            async def text(self) -> str:
                return "text"

            async def read(self) -> bytes:
                return b"bytes"

            def raise_for_status(self) -> None:
                pass

            async def __aenter__(self) -> "MockResponse":
                return self

            async def __aexit__(self, *args: Any) -> None:
                pass

        return MockResponse()

    http_client._session.request = mock_request  # type: ignore

    # Test JSON format
    result = await http_client._request(
        "GET", "/test", response_format=ResponseFormat.JSON
    )
    assert result == {"key": "value"}

    # Test text format
    result = await http_client._request(
        "GET", "/test", response_format=ResponseFormat.TEXT
    )
    assert result == "text"

    # Test bytes format
    result = await http_client._request(
        "GET", "/test", response_format=ResponseFormat.BYTES
    )
    assert result == b"bytes"


async def test_http_client_rate_limit(http_client: HTTPClient) -> None:
    """Test HTTP client rate limiting."""
    http_client._config.max_rate_limit = 2
    await http_client.initialize()

    # Mock session request
    async def mock_request(*args: Any, **kwargs: Any) -> Any:
        class MockResponse:
            status = 200
            reason = "OK"

            async def json(self) -> dict[str, Any]:
                return {}

            def raise_for_status(self) -> None:
                pass

            async def __aenter__(self) -> "MockResponse":
                return self

            async def __aexit__(self, *args: Any) -> None:
                pass

        return MockResponse()

    http_client._session.request = mock_request  # type: ignore

    # Make requests
    start_time = asyncio.get_event_loop().time()
    for _ in range(3):
        await http_client.get("/test")

    # Check that rate limiting was applied
    elapsed = asyncio.get_event_loop().time() - start_time
    assert elapsed >= 1.0  # At least 1 second delay between requests


async def test_http_client_retries(http_client: HTTPClient) -> None:
    """Test HTTP client retries."""
    await http_client.initialize()

    # Mock session request to fail twice then succeed
    attempts = 0

    async def mock_request(*args: Any, **kwargs: Any) -> Any:
        nonlocal attempts
        attempts += 1
        if attempts <= 2:
            raise ConnectionError("Test error")

        class MockResponse:
            status = 200
            reason = "OK"

            async def json(self) -> dict[str, int]:
                return {"attempt": attempts}

            def raise_for_status(self) -> None:
                pass

            async def __aenter__(self) -> "MockResponse":
                return self

            async def __aexit__(self, *args: Any) -> None:
                pass

        return MockResponse()

    http_client._session.request = mock_request  # type: ignore
    http_client._config.retries = 1

    # Should fail with max retries exceeded
    with pytest.raises(NetworkError, match="Request failed after 1 retries"):
        await http_client.get("/test")

    # Reset attempts and increase retries
    attempts = 0
    http_client._config.retries = 2

    # Should succeed on third attempt
    result = await http_client.get("/test")
    assert result == {"attempt": 3}


async def test_http_client_methods(http_client: HTTPClient) -> None:
    """Test HTTP client methods."""
    await http_client.initialize()

    # Mock session request
    async def mock_request(method: str, *args: Any, **kwargs: Any) -> Any:
        class MockResponse:
            status = 200
            reason = "OK"

            async def json(self) -> dict[str, str]:
                return {"method": method}

            def raise_for_status(self) -> None:
                pass

            async def __aenter__(self) -> "MockResponse":
                return self

            async def __aexit__(self, *args: Any) -> None:
                pass

        return MockResponse()

    http_client._session.request = mock_request  # type: ignore

    # Test GET
    result = await http_client.get("/test")
    assert result == {"method": "GET"}

    # Test POST
    result = await http_client.post("/test", json={"data": "test"})
    assert result == {"method": "POST"}

    # Test PUT
    result = await http_client.put("/test", json={"data": "test"})
    assert result == {"method": "PUT"}

    # Test DELETE
    result = await http_client.delete("/test")
    assert result == {"method": "DELETE"}


async def test_http_config_validation() -> None:
    """Test HTTP config validation."""
    # Test valid config
    config = HTTPConfig(base_url="http://example.com")
    assert config.base_url == "http://example.com"

    # Test invalid base URL
    with pytest.raises(ValueError, match="Base URL must be absolute"):
        HTTPConfig(base_url="invalid")

    # Test invalid timeout
    with pytest.raises(ValueError, match="Timeout must be greater than 0"):
        HTTPConfig(base_url="http://example.com", timeout=0)

    # Test invalid retries
    with pytest.raises(ValueError, match="Retries must be non-negative"):
        HTTPConfig(base_url="http://example.com", retries=-1)

    # Test invalid retry delay
    with pytest.raises(ValueError, match="Retry delay must be greater than 0"):
        HTTPConfig(base_url="http://example.com", retry_delay=0)

    # Test invalid rate limit
    with pytest.raises(ValueError, match="Rate limit must be non-negative"):
        HTTPConfig(base_url="http://example.com", max_rate_limit=-1)


async def test_http_client_status_codes(http_client: HTTPClient) -> None:
    """Test HTTP client status code handling."""
    await http_client.initialize()

    # Mock session request
    async def mock_request(*args: Any, **kwargs: Any) -> Any:
        class MockResponse:
            status = 404
            reason = "Not Found"

            async def json(self) -> dict[str, str]:
                return {"error": "not found"}

            def raise_for_status(self) -> None:
                raise Exception("404 Not Found")

            async def __aenter__(self) -> "MockResponse":
                return self

            async def __aexit__(self, *args: Any) -> None:
                pass

        return MockResponse()

    http_client._session.request = mock_request  # type: ignore

    # Test raise_for_status=True
    with pytest.raises(NetworkError, match="Request failed with status 404"):
        await http_client.get("/test")

    # Test raise_for_status=False
    http_client._config.raise_for_status = False
    result = await http_client.get("/test")
    assert result == {"error": "not found"}


async def test_http_client_form_data(http_client: HTTPClient) -> None:
    """Test HTTP client form data handling."""
    await http_client.initialize()

    # Mock session request
    async def mock_request(*args: Any, **kwargs: Any) -> Any:
        assert isinstance(kwargs.get("data"), FormData)

        class MockResponse:
            status = 200
            reason = "OK"

            async def json(self) -> dict[str, str]:
                return {"success": "true"}

            def raise_for_status(self) -> None:
                pass

            async def __aenter__(self) -> "MockResponse":
                return self

            async def __aexit__(self, *args: Any) -> None:
                pass

        return MockResponse()

    http_client._session.request = mock_request  # type: ignore

    # Test form data
    form = FormData()
    form.add_field("field", "value")
    result = await http_client.post("/test", data=form)
    assert result == {"success": "true"}


async def test_http_client_interceptors(http_client: HTTPClient) -> None:
    """Test HTTP client interceptors."""
    interceptor = TestInterceptor()
    http_client._config.interceptors.append(interceptor)
    await http_client.initialize()

    # Mock session request
    async def mock_request(*args: Any, **kwargs: Any) -> Any:
        class MockResponse:
            status = 200
            reason = "OK"

            async def json(self) -> dict[str, str]:
                return {"success": "true"}

            def raise_for_status(self) -> None:
                pass

            async def __aenter__(self) -> "MockResponse":
                return self

            async def __aexit__(self, *args: Any) -> None:
                pass

        return MockResponse()

    http_client._session.request = mock_request  # type: ignore

    # Make request
    await http_client.get("/test")

    # Check interceptor was called
    assert interceptor.pre_request_called
    assert interceptor.post_response_called
