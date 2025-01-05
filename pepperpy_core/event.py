"""Event handling module."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from pepperpy_core.exceptions import EventError
from pepperpy_core.module import BaseModule, ModuleConfig


class Event:
    """Base event class."""

    def __init__(
        self,
        data: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize event.

        Args:
            data: Event data
            metadata: Event metadata
        """
        self.data = data
        self.metadata = metadata or {}


class EventListener:
    """Event listener."""

    def __init__(
        self,
        event_type: type[Event],
        handler: Callable[[Event], None | Awaitable[None]],
        priority: int = 0,
    ) -> None:
        """Initialize event listener.

        Args:
            event_type: Event type
            handler: Event handler
            priority: Handler priority (higher priority handlers are called first)
        """
        self.event_type = event_type
        self.handler = handler
        self.priority = priority


class EventBusConfig(ModuleConfig):
    """Event bus configuration."""

    def __init__(self) -> None:
        """Initialize event bus configuration."""
        super().__init__(name="event_bus")
        self.max_listeners = 100


class EventBus(BaseModule[EventBusConfig]):
    """Event bus for handling events."""

    def __init__(self) -> None:
        """Initialize event bus."""
        config = EventBusConfig()
        super().__init__(config)
        self._listeners: Dict[type[Event], List[EventListener]] = {}
        self._stats = {
            "total_events": 0,
            "total_listeners": 0,
            "active_listeners": 0,
        }

    async def _setup(self) -> None:
        """Setup event bus."""
        self._listeners.clear()
        self._stats["total_events"] = 0
        self._stats["total_listeners"] = 0
        self._stats["active_listeners"] = 0

    async def _teardown(self) -> None:
        """Tear down event bus."""
        self._listeners.clear()

    async def emit(self, event: Event) -> None:
        """Emit an event.

        Args:
            event: Event to emit

        Raises:
            EventError: If event handling fails
        """
        if not self.is_initialized:
            raise EventError("Event bus not initialized")

        self._stats["total_events"] += 1

        event_type = type(event)
        if event_type not in self._listeners:
            return

        # Sort listeners by priority
        listeners = sorted(
            self._listeners[event_type],
            key=lambda x: x.priority,
            reverse=True,
        )

        # Call handlers
        for listener in listeners:
            try:
                result = listener.handler(event)
                if result is not None and hasattr(result, "__await__"):
                    await result
            except Exception as e:
                raise EventError(
                    f"Failed to handle event {event_type.__name__}: {e}"
                ) from e

    def add_listener(
        self,
        event_type: type[Event],
        handler: Callable[[Event], None | Awaitable[None]],
        priority: int = 0,
    ) -> None:
        """Add event listener.

        Args:
            event_type: Event type
            handler: Event handler
            priority: Handler priority (higher priority handlers are called first)

        Raises:
            EventError: If max listeners exceeded
        """
        if not self.is_initialized:
            raise EventError("Event bus not initialized")

        total_listeners = sum(len(listeners) for listeners in self._listeners.values())
        if total_listeners >= self.config.max_listeners:
            raise EventError(f"Max listeners ({self.config.max_listeners}) exceeded")

        if event_type not in self._listeners:
            self._listeners[event_type] = []

        listener = EventListener(event_type, handler, priority)
        self._listeners[event_type].append(listener)
        self._stats["total_listeners"] += 1
        self._stats["active_listeners"] += 1

    def remove_listener(
        self,
        event_type: type[Event],
        listener: Callable[[Event], Awaitable[None] | None],
    ) -> None:
        """Remove event listener.

        Args:
            event_type: Event type
            listener: Event listener
        """
        if event_type in self._listeners:
            listeners_to_remove = [
                event_listener
                for event_listener in self._listeners[event_type]
                if event_listener.handler == listener
            ]
            for event_listener in listeners_to_remove:
                self._listeners[event_type].remove(event_listener)
                self._stats["active_listeners"] -= 1
            if not self._listeners[event_type]:
                del self._listeners[event_type]

    def get_listeners(self, event_type: type[Event]) -> List[EventListener]:
        """Get event listeners.

        Args:
            event_type: Event type

        Returns:
            List of event listeners

        Raises:
            EventError: If event bus not initialized
        """
        if not self.is_initialized:
            raise EventError("Event bus not initialized")

        return self._listeners.get(event_type, [])
