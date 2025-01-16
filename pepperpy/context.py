"""Context management for PepperPy.

This module provides a robust context management system that supports:
- Context chaining
- Resource scoping
- State management
- Type-safe interfaces
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, Generic, Optional, TypeVar

from .core import PepperpyError


class ContextError(PepperpyError):
    """Context-related errors."""

    pass


@dataclass
class State:
    """State information with metadata."""

    value: Any
    metadata: Dict[str, Any] = field(default_factory=dict)


T = TypeVar("T")


class Context(Generic[T]):
    """Context class for managing context values."""

    def __init__(
        self,
        name: str = "default",
        *,
        timeout: Optional[float] = None,
        parent: Optional["Context[T]"] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize context.

        Args:
            name: Context name
            timeout: Optional timeout in seconds
            parent: Optional parent context
            data: Optional initial data
        """
        self.name = name
        self.timeout = timeout
        self.parent = parent
        self.data = data or {}
        self._context_value: Optional[T | "Context[T]"] = None
        self._state: Optional[State] = None
        self._cancel_event: asyncio.Event = asyncio.Event()

    def _ensure_type(self, value: Any) -> Optional[T]:
        """Ensure value is of type T.

        Args:
            value: Value to check

        Returns:
            Value as type T or None if not compatible
        """
        if value is None:
            return None
        if isinstance(value, Context):
            return value.get_context()
        return value  # type: ignore[no-any-return]

    def get_context(self) -> Optional[T]:
        """Get the current context value.

        Returns:
            Optional[T]: The current context value, or None if not set.
        """
        return self._ensure_type(self._context_value)

    def set_context(self, value: Optional[T]) -> None:
        """Set the current context value.

        Args:
            value: The value to set
        """
        self._context_value = value

    def get(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """Get value from context.

        Args:
            key: Data key
            default: Default value if key not found

        Returns:
            Value or default if not found
        """
        value = self.data.get(key, default)
        return self._ensure_type(value)

    def set(self, key: str, value: T) -> None:
        """Set value in context.

        Args:
            key: Data key
            value: Data value
        """
        self.data[key] = value

    def update(self, data: Dict[str, Any]) -> None:
        """Update context with dictionary.

        Args:
            data: Dictionary of values to update
        """
        self.data.update(data)

    def get_state(self) -> Optional[State]:
        """Get current state.

        Returns:
            Current state or None
        """
        return self._state

    def set_state(self, value: Any, **metadata: Any) -> None:
        """Set current state.

        Args:
            value: State value
            **metadata: Additional state metadata
        """
        self._state = State(value=value, metadata=metadata)

    def chain(self, name: str) -> "Context[T]":
        """Create a new chained context.

        Args:
            name: Child context name

        Returns:
            New context with this as parent
        """
        return Context[T](name=name, parent=self)

    async def cancel(self) -> None:
        """Cancel context operations."""
        self._cancel_event.set()

    @property
    def cancelled(self) -> bool:
        """Check if context is cancelled.

        Returns:
            True if context is cancelled
        """
        return self._cancel_event.is_set()

    async def wait_for_cancel(self) -> None:
        """Wait for context cancellation."""
        await self._cancel_event.wait()
