"""Type definitions."""

from typing import (
    Any,
    ParamSpec,
    Protocol,
    TypeVar,
    cast,
    runtime_checkable,
)
from typing import (
    AsyncGenerator as AsyncGen,
)
from typing import (
    Callable as Call,
)
from typing import (
    Coroutine as Coro,
)
from typing import (
    Generator as Gen,
)

T = TypeVar("T", covariant=True)
P = ParamSpec("P")


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


class BaseConfig:
    """Base configuration."""

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialize base configuration.

        Args:
            name: Configuration name
            kwargs: Additional arguments

        Raises:
            ValueError: If name is empty
        """
        if not name:
            raise ValueError("name cannot be empty")

        self.name = name
        self.metadata = kwargs.get("metadata", {})

        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")


def validate_type(value: Any, expected_type: type[T]) -> T:
    """Validate type.

    Args:
        value: Value to validate
        expected_type: Expected type

    Returns:
        Validated value

    Raises:
        TypeError: If value is not of expected type
    """
    if not isinstance(value, expected_type):
        raise TypeError(
            f"Expected {expected_type.__name__}, got {type(value).__name__}"
        )
    return value


def validate_protocol(value: Any, protocol: type[T]) -> T:
    """Validate protocol.

    Args:
        value: Value to validate
        protocol: Protocol to validate against

    Returns:
        Validated value

    Raises:
        TypeError: If value does not implement protocol
    """
    if not isinstance(value, protocol):
        raise TypeError(f"Value does not implement {protocol.__name__}")
    return value


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
