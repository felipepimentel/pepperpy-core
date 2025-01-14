"""Context and state management module."""

from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Generic, Optional, TypeVar, cast

from .core import PepperpyError


class ContextError(PepperpyError):
    """Context-related errors."""

    def __init__(
        self,
        message: str,
        cause: Optional[Exception] = None,
        context_key: Optional[str] = None,
    ) -> None:
        """Initialize context error.

        Args:
            message: Error message
            cause: Optional cause of the error
            context_key: Optional key that caused the error
        """
        super().__init__(message, cause)
        self.context_key = context_key


T = TypeVar("T")


@dataclass
class State(Generic[T]):
    """State container."""

    value: T
    metadata: dict[str, Any] = field(default_factory=dict)


class Context(Generic[T]):
    """Context management class."""

    def __init__(self) -> None:
        """Initialize context."""
        self._data: dict[str, Any] = {}
        self._context: ContextVar[T | None] = ContextVar("context", default=None)
        self._state: State[T] | None = None

    def get(self, key: str, default: T | None = None) -> T | None:
        """Get context value."""
        value = self._data.get(key, default)
        if value is None:
            return None
        return cast(T, value)

    def set(self, key: str, value: T) -> None:
        """Set context value."""
        self._data[key] = value

    def update(self, data: dict[str, T]) -> None:
        """Update context with dictionary."""
        for key, value in data.items():
            self.set(key, value)

    def get_context(self) -> T | None:
        """Get current context value."""
        return self._context.get()

    def set_context(self, value: T | None) -> None:
        """Set current context value."""
        self._context.set(value)

    def get_state(self) -> State[T] | None:
        """Get current state."""
        return self._state

    def set_state(self, value: T, **metadata: Any) -> None:
        """Set current state."""
        self._state = State(value=value, metadata=metadata)


__all__ = [
    "ContextError",
    "State",
    "Context",
]
