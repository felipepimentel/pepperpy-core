"""Event implementation module."""

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar

from .exceptions import PepperpyError
from .module import BaseModule, ModuleConfig
from .utils import utcnow


class EventError(PepperpyError):
    """Event specific error."""

    pass


class EventPriority(Enum):
    """Event priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

    def __str__(self) -> str:
        """Return string representation."""
        return self.value


@dataclass
class EventConfig(ModuleConfig):
    """Event configuration."""

    # Required fields (inherited from ModuleConfig)
    name: str

    # Optional fields
    enabled: bool = True
    max_listeners: int = 100
    buffer_size: int = 1000
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate configuration."""
        if self.max_listeners < 1:
            raise ValueError("max_listeners must be greater than 0")
        if self.buffer_size < 1:
            raise ValueError("buffer_size must be greater than 0")


T = TypeVar("T")


@dataclass
class Event(Generic[T]):
    """Event data."""

    name: str
    data: T
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


EventHandler = Callable[[Event[T]], Awaitable[None]]


@dataclass
class EventListener(Generic[T]):
    """Event listener."""

    name: str
    handler: EventHandler[T]
    priority: EventPriority = EventPriority.NORMAL
    metadata: dict[str, Any] = field(default_factory=dict)


class EventBus(Generic[T], BaseModule[EventConfig]):
    """Event bus implementation."""

    def __init__(self) -> None:
        """Initialize event bus."""
        config = EventConfig(name="event-bus")
        super().__init__(config)
        self._listeners: dict[str, list[EventListener[T]]] = {}
        self._events: list[Event[T]] = []

    async def _setup(self) -> None:
        """Setup event bus."""
        self._listeners.clear()
        self._events.clear()

    async def _teardown(self) -> None:
        """Teardown event bus."""
        self._listeners.clear()
        self._events.clear()

    async def get_stats(self) -> dict[str, Any]:
        """Get event bus statistics.

        Returns:
            Event bus statistics
        """
        self._ensure_initialized()
        return {
            "name": self.config.name,
            "enabled": self.config.enabled,
            "total_listeners": sum(len(l) for l in self._listeners.values()),
            "total_events": len(self._events),
            "event_types": list(self._listeners.keys()),
            "max_listeners": self.config.max_listeners,
            "buffer_size": self.config.buffer_size,
        }

    def add_listener(
        self,
        event_name: str,
        handler: EventHandler[T],
        priority: EventPriority = EventPriority.NORMAL,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add event listener.

        Args:
            event_name: Event name
            handler: Event handler
            priority: Event priority
            metadata: Optional listener metadata

        Raises:
            EventError: If too many listeners
        """
        self._ensure_initialized()

        if event_name not in self._listeners:
            self._listeners[event_name] = []

        listeners = self._listeners[event_name]
        if len(listeners) >= self.config.max_listeners:
            raise EventError(f"Too many listeners for event {event_name}")

        listener = EventListener(
            name=f"{event_name}_listener_{len(listeners)}",
            handler=handler,
            priority=priority,
            metadata=metadata or {},
        )

        # Insert listener in priority order
        index = 0
        for i, l in enumerate(listeners):
            if l.priority.value < priority.value:
                index = i
                break
        listeners.insert(index, listener)

    def remove_listener(self, event_name: str, handler: EventHandler[T]) -> None:
        """Remove event listener.

        Args:
            event_name: Event name
            handler: Event handler
        """
        self._ensure_initialized()

        if event_name not in self._listeners:
            return

        self._listeners[event_name] = [
            l for l in self._listeners[event_name] if l.handler != handler
        ]

    async def emit(
        self,
        event_name: str,
        data: T,
        priority: EventPriority = EventPriority.NORMAL,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Emit event.

        Args:
            event_name: Event name
            data: Event data
            priority: Event priority
            metadata: Optional event metadata
        """
        self._ensure_initialized()

        event = Event(
            name=event_name,
            data=data,
            priority=priority,
            metadata=metadata or {},
        )

        self._events.append(event)
        if len(self._events) > self.config.buffer_size:
            self._events.pop(0)

        if event_name not in self._listeners:
            return

        # Call handlers in priority order
        for listener in self._listeners[event_name]:
            try:
                await listener.handler(event)
            except Exception as e:
                # Log error but continue processing
                print(f"Error in event handler {listener.name}: {e}")

    def get_events(self, event_name: str | None = None) -> list[Event[T]]:
        """Get events.

        Args:
            event_name: Optional event name filter

        Returns:
            List of events
        """
        self._ensure_initialized()

        if event_name is None:
            return list(self._events)

        return [e for e in self._events if e.name == event_name]


__all__ = [
    "EventError",
    "EventPriority",
    "EventConfig",
    "Event",
    "EventHandler",
    "EventListener",
    "EventBus",
] 