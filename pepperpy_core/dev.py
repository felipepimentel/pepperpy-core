"""Development utilities."""

import asyncio
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Coroutine, Optional, Protocol, TypeVar

T = TypeVar("T")


class LogLevel(Enum):
    """Log level enumeration."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LoggerProtocol(Protocol):
    """Logger protocol."""

    def log(self, level: LogLevel, message: str, **kwargs: Any) -> None:
        """Log a message."""
        ...

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message."""
        ...

    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message."""
        ...

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message."""
        ...

    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message."""
        ...

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log a critical message."""
        ...


@dataclass
class Timer:
    """Timer context manager."""

    name: str
    logger: Optional[LoggerProtocol] = None

    def __enter__(self) -> "Timer":
        """Enter context."""
        self._start = time.perf_counter()
        if self.logger:
            self.logger.info(f"Timer {self.name} started")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context."""
        self._end = time.perf_counter()
        if self.logger:
            duration = self._end - self._start
            self.logger.info(
                f"Timer {self.name} stopped after {duration:.3f} seconds",
                timer=self.name,
                duration=duration,
            )


def debug_call(
    logger: LoggerProtocol,
    func_name: str,
    *args: Any,
    **kwargs: Any,
) -> None:
    """Debug function call."""
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
    """Debug function result."""
    logger.debug(
        f"Result from {func_name}",
        result=result,
    )


def debug_error(
    logger: LoggerProtocol,
    func_name: str,
    error: Exception,
) -> None:
    """Debug function error."""
    logger.debug(
        f"Error in {func_name}",
        error=str(error),
        error_type=type(error).__name__,
    )


class AsyncTestCase:
    """Base class for async test cases."""

    def setUp(self) -> None:
        """Set up test case."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self) -> None:
        """Tear down test case."""
        self.loop.close()

    def run_async(self, coro: Any) -> Any:
        """Run coroutine."""
        return self.loop.run_until_complete(coro)


def debug_decorator(
    logger: LoggerProtocol,
    func_name: Optional[str] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Debug decorator."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        """Decorate function."""
        nonlocal func_name
        if func_name is None:
            func_name = func.__name__

        def wrapper(*args: Any, **kwargs: Any) -> T:
            """Wrap function."""
            debug_call(logger, func_name, *args, **kwargs)
            try:
                result = func(*args, **kwargs)
                debug_result(logger, func_name, result)
                return result
            except Exception as e:
                debug_error(logger, func_name, e)
                raise

        return wrapper

    return decorator


def async_debug_decorator(
    logger: LoggerProtocol,
    func_name: Optional[str] = None,
) -> Callable[
    [Callable[..., Coroutine[Any, Any, T]]], Callable[..., Coroutine[Any, Any, T]]
]:
    """Async debug decorator."""

    def decorator(
        func: Callable[..., Coroutine[Any, Any, T]],
    ) -> Callable[..., Coroutine[Any, Any, T]]:
        """Decorate function."""
        nonlocal func_name
        if func_name is None:
            func_name = func.__name__

        async def wrapper(*args: Any, **kwargs: Any) -> T:
            """Wrap function."""
            debug_call(logger, func_name, *args, **kwargs)
            try:
                result = await func(*args, **kwargs)
                debug_result(logger, func_name, result)
                return result
            except Exception as e:
                debug_error(logger, func_name, e)
                raise

        return wrapper

    return decorator


__all__ = [
    "LogLevel",
    "LoggerProtocol",
    "Timer",
    "AsyncTestCase",
    "debug_decorator",
    "async_debug_decorator",
]
