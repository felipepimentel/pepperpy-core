"""Event implementation module."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Generic, TypeVar

from .exceptions import EventError
from .module import BaseModule, ModuleConfig


class EventPriority(Enum):
    """Event listener priority."""

    LOWEST = 0
    LOW = 1
    NORMAL = 2
    HIGH = 3
    HIGHEST = 4


@dataclass
class EventConfig(ModuleConfig):
    """Event bus configuration."""

    name: str
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


T = TypeVar("T")


@dataclass
class Event(Generic[T]):
    """Event data container."""

    name: str
    data: T
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EventListener(Generic[T]):
    """Event listener data."""

    handler: Callable[[Event[T]], Awaitable[None]]
    priority: EventPriority = EventPriority.NORMAL


class EventBus(Generic[T], BaseModule[EventConfig]):
    """Event bus implementation."""

    def __init__(self, config: EventConfig | None = None) -> None:
        """Initialize event bus.

        Args:
            config: Event bus configuration
        """
        super().__init__(config or EventConfig(name="event_bus"))
        self._listeners: dict[str, list[EventListener[T]]] = {}
        self._events: list[Event[T]] = []

    async def _setup(self) -> None:
        """Setup event bus."""
        self._listeners.clear()
        self._events.clear()

    async def _teardown(self) -> None:
        """Cleanup event bus."""
        self._listeners.clear()
        self._events.clear()

    async def get_stats(self) -> dict[str, Any]:
        """Get event bus statistics.

        Returns:
            Event bus statistics
        """
        if not self.is_initialized:
            await self.initialize()

        return {
            "name": self.config.name,
            "enabled": self.config.enabled,
            "total_listeners": sum(
                len(listeners) for listeners in self._listeners.values()
            ),
            "total_events": len(self._events),
            "event_types": list(self._listeners.keys()),
        }

    async def emit(self, event: Event[T]) -> None:
        """Emit event.

        Args:
            event: Event to emit
        """
        if not self.is_initialized:
            await self.initialize()

        self._events.append(event)

        if event.name not in self._listeners:
            return

        listeners = self._listeners[event.name]
        for listener in listeners:
            try:
                await listener.handler(event)
            except Exception as e:
                raise EventError(f"Failed to handle event {event.name}: {e}")

    def add_listener(
        self,
        event_name: str,
        handler: Callable[[Event[T]], Awaitable[None]],
        priority: EventPriority = EventPriority.NORMAL,
    ) -> None:
        """Add event listener.

        Args:
            event_name: Event name
            handler: Event handler function
            priority: Event priority
        """
        self._ensure_initialized()

        if event_name not in self._listeners:
            self._listeners[event_name] = []

        listeners = self._listeners[event_name]

        # Insert listener in priority order
        index = 0
        for i, listener in enumerate(listeners):
            if listener.priority.value < priority.value:
                index = i

        listeners.insert(index, EventListener(handler=handler, priority=priority))

    def remove_listener(
        self,
        event_name: str,
        handler: Callable[[Event[T]], Awaitable[None]],
    ) -> None:
        """Remove event listener.

        Args:
            event_name: Event name
            handler: Event handler function
        """
        self._ensure_initialized()

        if event_name not in self._listeners:
            return

        self._listeners[event_name] = [
            listener
            for listener in self._listeners[event_name]
            if listener.handler != handler
        ]

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
