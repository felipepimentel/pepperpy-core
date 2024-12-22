"""Development tools for testing, debugging and profiling."""

import asyncio
import cProfile
import functools
import json
import pstats
import time
import unittest
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, TypeVar, cast


class LoggerProtocol(Protocol):
    """Protocol for logger interface."""

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        ...

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        ...


@dataclass
class Timer:
    """Simple timer for benchmarking."""

    name: str
    logger: LoggerProtocol | None = None
    _start: float = field(default=0.0, init=False)
    _end: float = field(default=0.0, init=False)

    def __enter__(self) -> "Timer":
        """Start timer."""
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        """Stop timer and log result."""
        self._end = time.perf_counter()
        duration = self._end - self._start

        if self.logger:
            self.logger.info(
                f"{self.name} took {duration:.4f} seconds",
                timer=self.name,
                duration=duration,
            )


@dataclass
class Profiler:
    """Simple profiler for performance analysis."""

    name: str
    logger: LoggerProtocol | None = None
    output_path: Path | None = None
    _profiler: cProfile.Profile = field(default_factory=cProfile.Profile, init=False)

    def __enter__(self) -> "Profiler":
        """Start profiling."""
        self._profiler.enable()
        return self

    def __exit__(self, *args: Any) -> None:
        """Stop profiling and save results."""
        self._profiler.disable()

        stats = pstats.Stats(self._profiler)
        stats.sort_stats("cumulative")

        if self.output_path:
            stats.dump_stats(self.output_path)

        if self.logger:
            # Log top 10 functions
            self.logger.info(
                f"Profile results for {self.name}",
                profiler=self.name,
                stats=str(stats.print_stats(10)),
            )


@dataclass
class MockResponse:
    """Mock HTTP response for testing."""

    status: int = 200
    data: str | bytes | dict[str, Any] | None = None
    headers: dict[str, str] | None = field(default_factory=dict)

    async def json(self) -> dict[str, Any]:
        """Get JSON response data."""
        if isinstance(self.data, (str, bytes)):
            return cast(dict[str, Any], json.loads(self.data))
        return cast(dict[str, Any], self.data or {})

    async def text(self) -> str:
        """Get text response data."""
        if isinstance(self.data, bytes):
            return self.data.decode()
        if isinstance(self.data, dict):
            return json.dumps(self.data)
        return str(self.data or "")


def mock_response(
    status: int = 200,
    data: str | bytes | dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> Callable[..., MockResponse]:
    """Create mock response factory."""

    def factory(*args: Any, **kwargs: Any) -> MockResponse:
        return MockResponse(status, data, headers)

    return factory


def debug_call(
    logger: LoggerProtocol,
    func_name: str,
    *args: Any,
    **kwargs: Any,
) -> None:
    """Log function call debug information."""
    logger.debug(
        f"Calling {func_name}",
        args=args,
        kwargs=kwargs,
    )


def debug_result(
    logger: LoggerProtocol,
    func_name: str,
    result: Any,
) -> None:
    """Log function result debug information."""
    logger.debug(
        f"Result from {func_name}",
        result=result,
    )


def debug_error(
    logger: LoggerProtocol,
    func_name: str,
    error: Exception,
) -> None:
    """Log function error debug information."""
    logger.debug(
        f"Error in {func_name}",
        error=str(error),
        error_type=type(error).__name__,
    )


# Type variables for testing
T = TypeVar("T", bound=Callable[..., Awaitable[Any]])


def async_test(func: T) -> Callable[..., Any]:
    """Decorator for running async test functions in a new event loop.

    Args:
        func: The async test function to decorate.

    Returns:
        A wrapped function that runs the async test in a new event loop.

    Example:
        @async_test
        async def test_something():
            result = await some_async_function()
            assert result == expected
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Run async function in event loop."""
        return asyncio.run(func(*args, **kwargs))

    return cast(Callable[..., Any], wrapper)


class AsyncTestCase(unittest.TestCase):
    """Base class for async test cases.

    Provides setup and teardown of an event loop for the test case,
    and a helper method for running coroutines in tests.

    Example:
        class TestSomething(AsyncTestCase):
            async def test_feature(self):
                result = await self.run_async(some_async_function())
                self.assertEqual(result, expected)
    """

    def setUp(self) -> None:
        """Set up test case."""
        super().setUp()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self) -> None:
        """Tear down test case."""
        self.loop.close()
        asyncio.set_event_loop(None)
        super().tearDown()

    def run_async(self, coro: Awaitable[T]) -> T:
        """Run a coroutine in the test loop.

        Args:
            coro: The coroutine to run.

        Returns:
            The result of the coroutine.
        """
        return self.loop.run_until_complete(coro)


def run_async(coro: Awaitable[T]) -> T:
    """Run a coroutine in a new event loop.

    This is a standalone function for running coroutines outside of a test case.
    It creates a new event loop, runs the coroutine, and cleans up the loop.

    Args:
        coro: The coroutine to run.

    Returns:
        The result of the coroutine.

    Example:
        result = run_async(some_async_function())
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
        asyncio.set_event_loop(None)


__all__ = [
    "LoggerProtocol",
    "Timer",
    "Profiler",
    "MockResponse",
    "mock_response",
    "debug_call",
    "debug_result",
    "debug_error",
    "async_test",
    "AsyncTestCase",
    "run_async",
]
