"""Generator protocols and utilities.

This module provides protocols and utilities for working with generators in PepperPy.
It includes both synchronous and asynchronous generator protocols, along with
validation utilities.
"""

from typing import Any, Protocol, TypeVar, cast, runtime_checkable
from typing import AsyncGenerator as AsyncGen
from typing import Generator as Gen

T = TypeVar("T", covariant=True)


@runtime_checkable
class Generator(Protocol[T]):
    """Generator protocol."""

    def __iter__(self) -> "Generator[T]":
        """Get iterator.

        Returns:
            Generator iterator
        """
        ...

    def __next__(self) -> T:
        """Get next value.

        Returns:
            Next value

        Raises:
            StopIteration: When no more values are available
        """
        ...


@runtime_checkable
class AsyncGenerator(Protocol[T]):
    """Async generator protocol."""

    def __aiter__(self) -> "AsyncGenerator[T]":
        """Get async iterator.

        Returns:
            Async generator iterator
        """
        ...

    async def __anext__(self) -> T:
        """Get next value.

        Returns:
            Next value

        Raises:
            StopAsyncIteration: When no more values are available
        """
        ...


def validate_generator(value: Any) -> Gen[Any, Any, Any]:
    """Validate generator.

    Args:
        value: Value to validate

    Returns:
        Validated generator

    Raises:
        TypeError: If value is not a generator
    """
    if not hasattr(value, "__iter__") or not hasattr(value, "__next__"):
        raise TypeError(f"Expected generator, got {type(value).__name__}")
    return cast(Gen[Any, Any, Any], value)


def validate_async_generator(value: Any) -> AsyncGen[Any, None]:
    """Validate async generator.

    Args:
        value: Value to validate

    Returns:
        Validated async generator

    Raises:
        TypeError: If value is not an async generator
    """
    if not hasattr(value, "__aiter__") or not hasattr(value, "__anext__"):
        raise TypeError(f"Expected async generator, got {type(value).__name__}")
    return cast(AsyncGen[Any, None], value)


__all__ = [
    "Generator",
    "AsyncGenerator",
    "validate_generator",
    "validate_async_generator",
]
