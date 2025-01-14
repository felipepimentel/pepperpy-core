"""Callable protocols and utilities.

This module provides protocols and utilities for working with callables in PepperPy.
It includes protocols for synchronous and asynchronous callables, coroutines, and
validation utilities.
"""

from typing import Any, ParamSpec, Protocol, TypeVar, cast, runtime_checkable
from typing import Callable as Call
from typing import Coroutine as Coro

T = TypeVar("T", covariant=True)
P = ParamSpec("P")


@runtime_checkable
class Callable(Protocol[P, T]):
    """Callable protocol."""

    def __call__(self, *args: Any, **kwargs: Any) -> T:
        """Call callable.

        Args:
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Return value
        """
        ...


@runtime_checkable
class AsyncCallable(Protocol[P, T]):
    """Async callable protocol."""

    async def __call__(self, *args: Any, **kwargs: Any) -> T:
        """Call async callable.

        Args:
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Return value
        """
        ...


@runtime_checkable
class Coroutine(Protocol[T]):
    """Coroutine protocol."""

    def send(self, value: Any) -> T:
        """Send value to coroutine.

        Args:
            value: Value to send

        Returns:
            Return value
        """
        ...

    def throw(self, typ: Any, val: Any = None, tb: Any = None) -> T:
        """Throw exception into coroutine.

        Args:
            typ: Exception type
            val: Exception value
            tb: Traceback

        Returns:
            Return value
        """
        ...

    def close(self) -> None:
        """Close coroutine."""
        ...


def validate_callable(value: Any) -> Call[..., Any]:
    """Validate callable.

    Args:
        value: Value to validate

    Returns:
        Validated callable

    Raises:
        TypeError: If value is not callable
    """
    if not callable(value):
        raise TypeError(f"Expected callable, got {type(value).__name__}")
    return cast(Call[..., Any], value)


def validate_async_callable(value: Any) -> AsyncCallable[Any, Any]:
    """Validate async callable.

    Args:
        value: Value to validate

    Returns:
        Validated async callable

    Raises:
        TypeError: If value is not an async callable
    """
    if not callable(value):
        raise TypeError(f"Expected callable, got {type(value).__name__}")

    # Check if it's an async function by checking __code__ and CO_COROUTINE
    if hasattr(value, "__code__") and bool(value.__code__.co_flags & 0x0080):
        return cast(AsyncCallable[Any, Any], value)

    # Check if it's an async callable object by checking __call__
    if (
        callable(value)
        and hasattr(value.__call__, "__code__")
        and bool(value.__call__.__code__.co_flags & 0x0080)
    ):
        return cast(AsyncCallable[Any, Any], value)

    raise TypeError(f"Expected async callable, got {type(value).__name__}")


def validate_coroutine(value: Any) -> Coro[Any, Any, Any]:
    """Validate coroutine.

    Args:
        value: Value to validate

    Returns:
        Validated coroutine

    Raises:
        TypeError: If value is not a coroutine
    """
    if (
        not hasattr(value, "send")
        or not hasattr(value, "throw")
        or not hasattr(value, "close")
    ):
        raise TypeError(f"Expected coroutine, got {type(value).__name__}")
    return cast(Coro[Any, Any, Any], value)


__all__ = [
    "Callable",
    "AsyncCallable",
    "Coroutine",
    "validate_callable",
    "validate_async_callable",
    "validate_coroutine",
]
