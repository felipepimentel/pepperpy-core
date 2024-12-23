"""Test development utilities."""

import asyncio
import time
from typing import Any

import pytest

from pepperpy_core.dev import (
    AsyncTestCase,
    LoggerProtocol,
    MockResponse,
    Timer,
    debug_call,
    debug_error,
    debug_result,
)


@pytest.fixture
def test_logger() -> type[LoggerProtocol]:
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
        def clear(cls) -> None:
            """Clear messages."""
            cls.messages.clear()

    return TestLoggerImpl


@pytest.mark.no_cover
def test_timer(test_logger: type[LoggerProtocol]) -> None:
    """Test timer functionality."""
    test_logger.clear()  # Clear any previous messages
    with Timer("test_operation", logger=test_logger):
        # Simulate some work
        time.sleep(0.1)

    assert len(test_logger.messages) == 1
    level, message, kwargs = test_logger.messages[0]
    assert level == "info"
    assert "test_operation took" in message
    assert "seconds" in message
    assert kwargs["timer"] == "test_operation"
    assert isinstance(kwargs["duration"], float)
    assert kwargs["duration"] > 0


@pytest.mark.no_cover
def test_timer_without_logger() -> None:
    """Test timer without logger."""
    with Timer("test_operation") as timer:
        # Simulate some work
        time.sleep(0.1)

    assert timer._end > timer._start


@pytest.mark.no_cover
def test_debug_logging(test_logger: type[LoggerProtocol]) -> None:
    """Test debug logging functions."""
    test_logger.clear()  # Clear any previous messages

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


@pytest.mark.no_cover
def test_mock_response() -> None:
    """Test mock response."""
    response = MockResponse(200, {"test": "test"})
    assert response.status == 200
    assert asyncio.run(response.json()) == {"test": "test"}


@pytest.mark.no_cover
def test_async_test_case() -> None:
    """Test async test case."""

    class TestCase(AsyncTestCase):
        """Test case."""

        async def test_method(self) -> None:
            """Test method."""
            await asyncio.sleep(0.1)

    test_case = TestCase()
    test_case.setUp()
    test_case.run_async(test_case.test_method())
    test_case.tearDown()
