"""Tests for the dev module."""

from pathlib import Path
from typing import Any, Protocol

import pytest

from pepperpy_core.dev import (
    AsyncTestCase,
    MockResponse,
    Profiler,
    Timer,
    debug_call,
    debug_error,
    debug_result,
)


class TestLogger(Protocol):
    """Test logger protocol."""

    messages: list[tuple[str, str, dict[str, Any]]]

    @classmethod
    def debug(cls, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        ...

    @classmethod
    def info(cls, message: str, **kwargs: Any) -> None:
        """Log info message."""
        ...

    @classmethod
    def warning(cls, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        ...

    @classmethod
    def error(cls, message: str, **kwargs: Any) -> None:
        """Log error message."""
        ...

    @classmethod
    def clear(cls) -> None:
        """Clear messages."""
        ...


@pytest.fixture
def test_logger() -> type[TestLogger]:
    """Create a test logger."""

    class TestLoggerImpl:
        """Test logger implementation."""

        messages: list[tuple[str, str, dict[str, Any]]] = []

        @classmethod
        def debug(cls, message: str, **kwargs: Any) -> None:
            """Log debug message."""
            cls.messages.append(("debug", message, kwargs))

        @classmethod
        def info(cls, message: str, **kwargs: Any) -> None:
            """Log info message."""
            cls.messages.append(("info", message, kwargs))

        @classmethod
        def warning(cls, message: str, **kwargs: Any) -> None:
            """Log warning message."""
            cls.messages.append(("warning", message, kwargs))

        @classmethod
        def error(cls, message: str, **kwargs: Any) -> None:
            """Log error message."""
            cls.messages.append(("error", message, kwargs))

        @classmethod
        def clear(cls) -> None:
            """Clear messages."""
            cls.messages.clear()

    return TestLoggerImpl


def test_timer(test_logger: type[TestLogger]) -> None:
    """Test timer functionality."""
    test_logger.clear()  # Clear any previous messages
    with Timer("test_operation", logger=test_logger) as timer:
        # Simulate some work
        for _ in range(1000000):
            pass

    assert len(test_logger.messages) == 1
    level, message, kwargs = test_logger.messages[0]
    assert level == "info"
    assert "test_operation took" in message
    assert "seconds" in message
    assert kwargs["timer"] == "test_operation"
    assert isinstance(kwargs["duration"], float)
    assert kwargs["duration"] > 0


def test_timer_without_logger() -> None:
    """Test timer without logger."""
    with Timer("test_operation") as timer:
        # Simulate some work
        for _ in range(1000000):
            pass

    assert timer._end > timer._start


def test_profiler(test_logger: type[TestLogger], tmp_path: Path) -> None:
    """Test profiler functionality."""
    test_logger.clear()  # Clear any previous messages
    output_path = tmp_path / "profile.stats"

    with Profiler(
        "test_profiling", logger=test_logger, output_path=output_path
    ) as profiler:
        # Simulate some work
        for _ in range(1000000):
            pass

    assert len(test_logger.messages) == 1
    level, message, kwargs = test_logger.messages[0]
    assert level == "info"
    assert "Profile results for test_profiling" in message
    assert kwargs["profiler"] == "test_profiling"
    assert isinstance(kwargs["stats"], str)
    assert output_path.exists()


def test_profiler_without_logger(tmp_path: Path) -> None:
    """Test profiler without logger."""
    output_path = tmp_path / "profile.stats"

    with Profiler("test_profiling", output_path=output_path) as profiler:
        # Simulate some work
        for _ in range(1000000):
            pass

    assert output_path.exists()


def test_profiler_without_output(test_logger: type[TestLogger]) -> None:
    """Test profiler without output path."""
    test_logger.clear()  # Clear any previous messages
    with Profiler("test_profiling", logger=test_logger) as profiler:
        # Simulate some work
        for _ in range(1000000):
            pass

    assert len(test_logger.messages) == 1
    level, message, kwargs = test_logger.messages[0]
    assert level == "info"
    assert "Profile results for test_profiling" in message


def test_debug_logging(test_logger: type[TestLogger]) -> None:
    """Test debug logging decorators."""
    test_logger.clear()  # Clear any previous messages

    def test_function(x: int, y: str) -> str:
        return f"{x} {y}"

    # Test debug_call
    debug_call(test_logger, "test_function", 42, "hello")
    assert len(test_logger.messages) == 1
    level, message, kwargs = test_logger.messages[0]
    assert level == "debug"
    assert "Calling test_function" in message
    assert kwargs["args"] == (42, "hello")

    # Test debug_result
    test_logger.clear()
    debug_result(test_logger, "test_function", "42 hello")
    assert len(test_logger.messages) == 1
    level, message, kwargs = test_logger.messages[0]
    assert level == "debug"
    assert "Result from test_function" in message
    assert kwargs["result"] == "42 hello"

    # Test debug_error
    test_logger.clear()
    error = ValueError("Test error")
    debug_error(test_logger, "test_function", error)
    assert len(test_logger.messages) == 1
    level, message, kwargs = test_logger.messages[0]
    assert level == "debug"
    assert "Error in test_function" in message
    assert kwargs["error"] == "Test error"
    assert kwargs["error_type"] == "ValueError"


@pytest.mark.asyncio
async def test_mock_response() -> None:
    """Test mock response creation."""
    # Test with string data
    response = MockResponse(200, "test data")
    assert response.status == 200
    assert await response.text() == "test data"
    with pytest.raises(ValueError):
        await response.json()

    # Test with bytes data
    response = MockResponse(200, b"test data")
    assert response.status == 200
    assert await response.text() == "test data"
    with pytest.raises(ValueError):
        await response.json()

    # Test with dict data
    data = {"key": "value"}
    response = MockResponse(200, data)
    assert response.status == 200
    assert await response.text() == '{"key": "value"}'
    assert await response.json() == data

    # Test with headers
    headers = {"Content-Type": "application/json"}
    response = MockResponse(200, data, headers)
    assert response.status == 200
    assert response.headers == headers


def test_async_test_case() -> None:
    """Test async test case."""
    test_case = AsyncTestCase()
    test_case.setUp()  # Initialize the event loop

    async def async_func() -> str:
        return "result"

    result = test_case.run_async(async_func())
    assert result == "result"

    test_case.tearDown()  # Clean up the event loop
