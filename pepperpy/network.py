"""Network module."""

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Protocol, TypeVar

from aiohttp import ClientResponse, ClientSession, ClientTimeout, FormData
from multidict import MultiDict
from yarl import URL

from pepperpy.exceptions import PepperpyError
from pepperpy.logging import LoggerMixin


class NetworkError(PepperpyError):
    """Network error."""


class ResponseFormat(str, Enum):
    """Response format."""

    JSON = "json"
    TEXT = "text"
    BYTES = "bytes"


T = TypeVar("T")


class RequestInterceptor(Protocol):
    """Request interceptor protocol."""

    async def pre_request(
        self,
        method: str,
        url: str,
        params: MultiDict[str] | dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        proxy: str | None = None,
        timeout: ClientTimeout | None = None,
        verify_ssl: bool | None = None,
        json: Any | None = None,
        data: FormData | None = None,
    ) -> None:
        """Pre-request hook.

        Args:
            method: HTTP method
            url: URL path
            params: Query parameters
            headers: Request headers
            proxy: Proxy URL
            timeout: Request timeout
            verify_ssl: Whether to verify SSL certificates
            json: JSON data
            data: Form data
        """
        ...

    async def post_response(self, response: ClientResponse) -> None:
        """Post-response hook.

        Args:
            response: Response object
        """
        ...


@dataclass
class HTTPConfig:
    """HTTP client configuration."""

    base_url: str
    headers: Optional[dict[str, str]] = None
    timeout: float = 30.0
    verify_ssl: bool = True
    response_format: ResponseFormat = ResponseFormat.JSON
    retries: int = 1
    retry_delay: float = 0.1
    max_rate_limit: int = 0
    raise_for_status: bool = True
    interceptors: list[RequestInterceptor] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate configuration."""
        try:
            url = URL(self.base_url)
            if not url.is_absolute():
                raise ValueError("Base URL must be absolute")
        except Exception as e:
            raise ValueError("Base URL must be absolute") from e

        if self.timeout <= 0:
            raise ValueError("Timeout must be greater than 0")

        if self.retries < 0:
            raise ValueError("Retries must be non-negative")

        if self.retry_delay <= 0:
            raise ValueError("Retry delay must be greater than 0")

        if self.max_rate_limit < 0:
            raise ValueError("Rate limit must be non-negative")


class HTTPClient(LoggerMixin):
    """HTTP client."""

    def __init__(self, config: HTTPConfig) -> None:
        """Initialize HTTP client.

        Args:
            config: Client configuration
        """
        super().__init__()
        self._config = config
        self._session: Optional[ClientSession] = None
        self._initialized = False
        self._last_request_time = 0.0

    async def initialize(self) -> None:
        """Initialize client."""
        if self._initialized:
            return

        self._session = ClientSession(
            base_url=self._config.base_url,
            headers=self._config.headers,
            timeout=ClientTimeout(total=self._config.timeout),
            raise_for_status=self._config.raise_for_status,
        )
        self._initialized = True

    async def cleanup(self) -> None:
        """Clean up client."""
        if not self._initialized:
            return

        if self._session:
            await self._session.close()
            self._session = None

        self._initialized = False

    async def __aenter__(self) -> "HTTPClient":
        """Enter context manager."""
        await self.initialize()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit context manager."""
        await self.cleanup()

    async def _check_rate_limit(self) -> None:
        """Check rate limit."""
        if not self._config.max_rate_limit:
            return

        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time

        if elapsed < 1.0 / self._config.max_rate_limit:
            await asyncio.sleep(1.0 / self._config.max_rate_limit - elapsed)

        self._last_request_time = asyncio.get_event_loop().time()

    async def _handle_response(
        self, response: ClientResponse, response_format: ResponseFormat
    ) -> Any:
        """Handle response.

        Args:
            response: Response object
            response_format: Response format

        Returns:
            Response data in requested format

        Raises:
            NetworkError: If response format is invalid or status code is invalid
        """
        # Run post-response interceptors
        for interceptor in self._config.interceptors:
            await interceptor.post_response(response)

        # Check status code if configured
        if self._config.raise_for_status:
            try:
                response.raise_for_status()
            except Exception as e:
                raise NetworkError(
                    f"Request failed with status {response.status}: {response.reason}"
                ) from e

        try:
            if response_format == ResponseFormat.JSON:
                return await response.json()
            elif response_format == ResponseFormat.TEXT:
                return await response.text()
            elif response_format == ResponseFormat.BYTES:
                return await response.read()
            else:
                raise NetworkError(f"Invalid response format: {response_format}")
        except Exception as e:
            raise NetworkError(f"Failed to parse response: {e}") from e

    async def _request(
        self,
        method: str,
        url: str,
        params: MultiDict[str] | dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        proxy: str | None = None,
        timeout: ClientTimeout | None = None,
        verify_ssl: bool | None = None,
        json: Any | None = None,
        data: FormData | None = None,
        response_format: ResponseFormat | None = None,
        retries: int | None = None,
        retry_delay: float | None = None,
    ) -> Any:
        """Send HTTP request.

        Args:
            method: HTTP method
            url: URL path (will be joined with base_url if set)
            params: Query parameters
            headers: Request headers (merged with default headers)
            proxy: Proxy URL
            timeout: Request timeout
            verify_ssl: Whether to verify SSL certificates
            json: JSON data
            data: Form data
            response_format: Response format
            retries: Number of retries
            retry_delay: Delay between retries

        Returns:
            Response data in requested format

        Raises:
            NetworkError: If request fails
        """
        if not self._session:
            await self.initialize()

        # Merge configuration
        final_headers = {**(self._config.headers or {}), **(headers or {})}
        final_verify_ssl = (
            verify_ssl if verify_ssl is not None else self._config.verify_ssl
        )
        final_format = response_format or self._config.response_format
        final_retries = retries if retries is not None else self._config.retries
        final_retry_delay = (
            retry_delay if retry_delay is not None else self._config.retry_delay
        )

        # Run pre-request interceptors
        for interceptor in self._config.interceptors:
            await interceptor.pre_request(
                method,
                url,
                params=params,
                headers=final_headers,
                proxy=proxy,
                timeout=timeout,
                verify_ssl=final_verify_ssl,
                json=json,
                data=data,
            )

        retry_count = 0
        last_error = None

        while retry_count < final_retries + 1:
            try:
                await self._check_rate_limit()

                assert self._session is not None  # for type checking
                response = await self._session.request(
                    method,
                    url,
                    params=params,
                    headers=final_headers,
                    proxy=proxy,
                    timeout=timeout,
                    ssl=final_verify_ssl,
                    json=json,
                    data=data,
                )
                async with response:
                    return await self._handle_response(response, final_format)

            except Exception as exc:
                last_error = exc
                retry_count += 1
                if retry_count <= final_retries:
                    self.logger.warning(
                        f"Request failed (attempt {retry_count}/{final_retries}): {exc}"
                    )
                    await asyncio.sleep(final_retry_delay)
                    continue
                break

        raise NetworkError(
            f"Request failed after {final_retries} retries: {last_error}"
        ) from last_error

    async def get(
        self,
        url: str,
        params: MultiDict[str] | dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        proxy: str | None = None,
        timeout: ClientTimeout | None = None,
        verify_ssl: bool | None = None,
        response_format: ResponseFormat | None = None,
        retries: int | None = None,
        retry_delay: float | None = None,
    ) -> Any:
        """Send GET request.

        Args:
            url: URL path (will be joined with base_url if set)
            params: Query parameters
            headers: Request headers (merged with default headers)
            proxy: Proxy URL
            timeout: Request timeout
            verify_ssl: Whether to verify SSL certificates
            response_format: Response format
            retries: Number of retries
            retry_delay: Delay between retries

        Returns:
            Response data in requested format

        Raises:
            NetworkError: If request fails
        """
        return await self._request(
            "GET",
            url,
            params=params,
            headers=headers,
            proxy=proxy,
            timeout=timeout,
            verify_ssl=verify_ssl,
            response_format=response_format,
            retries=retries,
            retry_delay=retry_delay,
        )

    async def post(
        self,
        url: str,
        params: MultiDict[str] | dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        proxy: str | None = None,
        timeout: ClientTimeout | None = None,
        verify_ssl: bool | None = None,
        json: Any | None = None,
        data: FormData | None = None,
        response_format: ResponseFormat | None = None,
        retries: int | None = None,
        retry_delay: float | None = None,
    ) -> Any:
        """Send POST request.

        Args:
            url: URL path (will be joined with base_url if set)
            params: Query parameters
            headers: Request headers (merged with default headers)
            proxy: Proxy URL
            timeout: Request timeout
            verify_ssl: Whether to verify SSL certificates
            json: JSON data
            data: Form data
            response_format: Response format
            retries: Number of retries
            retry_delay: Delay between retries

        Returns:
            Response data in requested format

        Raises:
            NetworkError: If request fails
        """
        return await self._request(
            "POST",
            url,
            params=params,
            headers=headers,
            proxy=proxy,
            timeout=timeout,
            verify_ssl=verify_ssl,
            json=json,
            data=data,
            response_format=response_format,
            retries=retries,
            retry_delay=retry_delay,
        )

    async def put(
        self,
        url: str,
        params: MultiDict[str] | dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        proxy: str | None = None,
        timeout: ClientTimeout | None = None,
        verify_ssl: bool | None = None,
        json: Any | None = None,
        data: FormData | None = None,
        response_format: ResponseFormat | None = None,
        retries: int | None = None,
        retry_delay: float | None = None,
    ) -> Any:
        """Send PUT request.

        Args:
            url: URL path (will be joined with base_url if set)
            params: Query parameters
            headers: Request headers (merged with default headers)
            proxy: Proxy URL
            timeout: Request timeout
            verify_ssl: Whether to verify SSL certificates
            json: JSON data
            data: Form data
            response_format: Response format
            retries: Number of retries
            retry_delay: Delay between retries

        Returns:
            Response data in requested format

        Raises:
            NetworkError: If request fails
        """
        return await self._request(
            "PUT",
            url,
            params=params,
            headers=headers,
            proxy=proxy,
            timeout=timeout,
            verify_ssl=verify_ssl,
            json=json,
            data=data,
            response_format=response_format,
            retries=retries,
            retry_delay=retry_delay,
        )

    async def delete(
        self,
        url: str,
        params: MultiDict[str] | dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        proxy: str | None = None,
        timeout: ClientTimeout | None = None,
        verify_ssl: bool | None = None,
        response_format: ResponseFormat | None = None,
        retries: int | None = None,
        retry_delay: float | None = None,
    ) -> Any:
        """Send DELETE request.

        Args:
            url: URL path (will be joined with base_url if set)
            params: Query parameters
            headers: Request headers (merged with default headers)
            proxy: Proxy URL
            timeout: Request timeout
            verify_ssl: Whether to verify SSL certificates
            response_format: Response format
            retries: Number of retries
            retry_delay: Delay between retries

        Returns:
            Response data in requested format

        Raises:
            NetworkError: If request fails
        """
        return await self._request(
            "DELETE",
            url,
            params=params,
            headers=headers,
            proxy=proxy,
            timeout=timeout,
            verify_ssl=verify_ssl,
            response_format=response_format,
            retries=retries,
            retry_delay=retry_delay,
        )
