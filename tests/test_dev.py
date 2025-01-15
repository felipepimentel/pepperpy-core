"""Test development utilities."""

from typing import Any

import pytest

from pepperpy.dev import (
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


class TestLogger(LoggerProtocol):
    """Test logger implementation."""

    def __init__(self) -> None:
        """Initialize test logger."""
        self.messages: list[tuple[LogLevel, str, dict[str, Any]]] = []

    def log(self, level: LogLevel, message: str, **kwargs: Any) -> None:
        """Log a message."""
        self.messages.append((level, message, kwargs))

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


@pytest.fixture
def test_logger() -> TestLogger:
    """Create a test logger."""
    return TestLogger()


def test_log_level() -> None:
    """Test log level enumeration."""
    assert LogLevel.DEBUG.value == "debug"
    assert LogLevel.INFO.value == "info"
    assert LogLevel.WARNING.value == "warning"
    assert LogLevel.ERROR.value == "error"
    assert LogLevel.CRITICAL.value == "critical"


def test_timer(test_logger: TestLogger) -> None:
    """Test timer context manager."""
    with Timer("test", test_logger):
        pass

    assert len(test_logger.messages) == 2
    assert test_logger.messages[0][0] == LogLevel.INFO
    assert test_logger.messages[0][1] == "Timer test started"
    assert test_logger.messages[1][0] == LogLevel.INFO
    assert "Timer test stopped after" in test_logger.messages[1][1]
    assert test_logger.messages[1][2]["timer"] == "test"
    assert isinstance(test_logger.messages[1][2]["duration"], float)


def test_timer_without_logger() -> None:
    """Test timer context manager without logger."""
    with Timer("test"):
        pass


def test_debug_call(test_logger: TestLogger) -> None:
    """Test debug call."""
    debug_call(test_logger, "test_func", 1, 2, key="value")
    assert len(test_logger.messages) == 1
    assert test_logger.messages[0][0] == LogLevel.DEBUG
    assert test_logger.messages[0][1] == "Calling test_func"
    assert test_logger.messages[0][2]["args"] == (1, 2)
    assert test_logger.messages[0][2]["kwargs"] == {"key": "value"}


def test_debug_result(test_logger: TestLogger) -> None:
    """Test debug result."""
    debug_result(test_logger, "test_func", "result")
    assert len(test_logger.messages) == 1
    assert test_logger.messages[0][0] == LogLevel.DEBUG
    assert test_logger.messages[0][1] == "Result from test_func"
    assert test_logger.messages[0][2]["result"] == "result"


def test_debug_error(test_logger: TestLogger) -> None:
    """Test debug error."""
    error = ValueError("test error")
    debug_error(test_logger, "test_func", error)
    assert len(test_logger.messages) == 1
    assert test_logger.messages[0][0] == LogLevel.DEBUG
    assert test_logger.messages[0][1] == "Error in test_func"
    assert test_logger.messages[0][2]["error"] == "test error"
    assert test_logger.messages[0][2]["error_type"] == "ValueError"


def test_debug_decorator(test_logger: TestLogger) -> None:
    """Test debug decorator."""

    @debug_decorator(test_logger)
    def test_func(x: int, y: int) -> int:
        return x + y

    result = test_func(1, 2)
    assert result == 3
    assert len(test_logger.messages) == 2
    assert test_logger.messages[0][0] == LogLevel.DEBUG
    assert test_logger.messages[0][1] == "Calling test_func"
    assert test_logger.messages[1][0] == LogLevel.DEBUG
    assert test_logger.messages[1][1] == "Result from test_func"


def test_debug_decorator_with_error(test_logger: TestLogger) -> None:
    """Test debug decorator with error."""

    @debug_decorator(test_logger)
    def test_func() -> None:
        raise ValueError("test error")

    with pytest.raises(ValueError):
        test_func()

    assert len(test_logger.messages) == 2
    assert test_logger.messages[0][0] == LogLevel.DEBUG
    assert test_logger.messages[0][1] == "Calling test_func"
    assert test_logger.messages[1][0] == LogLevel.DEBUG
    assert test_logger.messages[1][1] == "Error in test_func"


def test_debug_decorator_with_name(test_logger: TestLogger) -> None:
    """Test debug decorator with custom name."""

    @debug_decorator(test_logger, "custom_name")
    def test_func() -> None:
        pass

    test_func()
    assert len(test_logger.messages) == 2
    assert test_logger.messages[0][1] == "Calling custom_name"
    assert test_logger.messages[1][1] == "Result from custom_name"


@pytest.mark.asyncio
async def test_async_debug_decorator(test_logger: TestLogger) -> None:
    """Test async debug decorator."""

    @async_debug_decorator(test_logger)
    async def test_func(x: int, y: int) -> int:
        return x + y

    result = await test_func(1, 2)
    assert result == 3
    assert len(test_logger.messages) == 2
    assert test_logger.messages[0][0] == LogLevel.DEBUG
    assert test_logger.messages[0][1] == "Calling test_func"
    assert test_logger.messages[1][0] == LogLevel.DEBUG
    assert test_logger.messages[1][1] == "Result from test_func"


@pytest.mark.asyncio
async def test_async_debug_decorator_with_error(test_logger: TestLogger) -> None:
    """Test async debug decorator with error."""

    @async_debug_decorator(test_logger)
    async def test_func() -> None:
        raise ValueError("test error")

    with pytest.raises(ValueError):
        await test_func()

    assert len(test_logger.messages) == 2
    assert test_logger.messages[0][0] == LogLevel.DEBUG
    assert test_logger.messages[0][1] == "Calling test_func"
    assert test_logger.messages[1][0] == LogLevel.DEBUG
    assert test_logger.messages[1][1] == "Error in test_func"


@pytest.mark.asyncio
async def test_async_debug_decorator_with_name(test_logger: TestLogger) -> None:
    """Test async debug decorator with custom name."""

    @async_debug_decorator(test_logger, "custom_name")
    async def test_func() -> None:
        pass

    await test_func()
    assert len(test_logger.messages) == 2
    assert test_logger.messages[0][1] == "Calling custom_name"
    assert test_logger.messages[1][1] == "Result from custom_name"


def test_async_test_case() -> None:
    """Test async test case."""

    class TestCase(AsyncTestCase):
        """Test case implementation."""

        async def test_coro(self) -> str:
            """Test coroutine."""
            return "test"

    test_case = TestCase()
    test_case.setUp()
    try:
        result = test_case.run_async(test_case.test_coro())
        assert result == "test"
    finally:
        test_case.tearDown()
