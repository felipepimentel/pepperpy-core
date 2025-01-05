"""Test dev module."""

import asyncio
import time
from typing import Any

import pytest

from pepperpy_core.dev import (
    AsyncTestCase,
    LoggerProtocol,
    LogLevel,
    Timer,
    async_debug_decorator,
    debug_call,
    debug_decorator,
    debug_error,
    debug_result,
)
from pepperpy_core.logging import (
    BaseHandler,
    HandlerConfig,
    LogRecord,
)
from pepperpy_core.logging import LogLevel as LoggingLevel


@pytest.fixture
def test_logger() -> "TestLogger":
    """Create a test logger."""
    return TestLogger(HandlerConfig(level=LoggingLevel.DEBUG))


class TestLogger(BaseHandler, LoggerProtocol):
    """Test logger implementation."""

    def __init__(self, config: HandlerConfig) -> None:
        """Initialize test logger."""
        super().__init__(config)
        self.messages: list[str] = []

    def handle(self, message: str) -> None:
        """Handle message."""
        self.messages.append(message)

    def emit(self, record: "LogRecord") -> None:
        """Emit log record."""
        self.handle(record.message)

    def log(self, level: LogLevel, message: str, **kwargs: Any) -> None:
        """Log a message."""
        self.messages.append(message)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message."""
        self.log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message."""
        self.log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message."""
        self.log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message."""
        self.log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log a critical message."""
        self.log(LogLevel.CRITICAL, message, **kwargs)


def test_timer_without_logger() -> None:
    """Test timer without logger."""
    with Timer("test") as timer:
        time.sleep(0.1)
    assert hasattr(timer, "_start")
    assert hasattr(timer, "_end")
    assert timer._end - timer._start >= 0.1


def test_timer_with_logger(test_logger: TestLogger) -> None:
    """Test timer with logger."""
    with Timer("test", test_logger):
        time.sleep(0.1)
    assert len(test_logger.messages) == 2
    assert "Timer test started" in test_logger.messages[0]
    assert "Timer test stopped after" in test_logger.messages[1]
    assert "seconds" in test_logger.messages[1]


def test_debug_call(test_logger: TestLogger) -> None:
    """Test debug call."""
    debug_call(test_logger, "test_func", 1, 2, a=3, b=4)
    assert len(test_logger.messages) == 1
    assert "Calling test_func" in test_logger.messages[0]


def test_debug_result(test_logger: TestLogger) -> None:
    """Test debug result."""
    debug_result(test_logger, "test_func", "result")
    assert len(test_logger.messages) == 1
    assert "Result from test_func" in test_logger.messages[0]


def test_debug_error(test_logger: TestLogger) -> None:
    """Test debug error."""
    error = ValueError("test error")
    debug_error(test_logger, "test_func", error)
    assert len(test_logger.messages) == 1
    assert "Error in test_func" in test_logger.messages[0]


def test_debug_decorator(test_logger: TestLogger) -> None:
    """Test debug decorator."""

    @debug_decorator(test_logger)
    def test_func(a: int, b: int) -> int:
        return a + b

    result = test_func(1, 2)
    assert result == 3
    assert len(test_logger.messages) == 2
    assert "Calling" in test_logger.messages[0]
    assert "Result from" in test_logger.messages[1]


@pytest.mark.asyncio
async def test_async_debug_decorator(test_logger: TestLogger) -> None:
    """Test async debug decorator."""

    @async_debug_decorator(test_logger)
    async def test_func(a: int, b: int) -> int:
        await asyncio.sleep(0.1)
        return a + b

    result = await test_func(1, 2)
    assert result == 3
    assert len(test_logger.messages) == 2
    assert "Calling" in test_logger.messages[0]
    assert "Result from" in test_logger.messages[1]


def test_async_test_case() -> None:
    """Test async test case."""

    class TestCase(AsyncTestCase):
        """Test case implementation."""

        async def test_method(self) -> None:
            """Test method."""
            await asyncio.sleep(0.1)

    test_case = TestCase()
    test_case.setUp()
    test_case.run_async(test_case.test_method())
    test_case.tearDown()
