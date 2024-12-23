"""Event handling module."""

from typing import Any, Callable, Dict, List, Optional

from pepperpy_core.exceptions import EventError
from pepperpy_core.module import BaseModule
from pepperpy_core.types import BaseConfig


class Event:
    """Base event class."""

    def __init__(
        self,
        name: str,
        data: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize event.

        Args:
            name: Event name
            data: Event data
            metadata: Event metadata
        """
        self.name = name
        self.data = data
        self.metadata = metadata or {}


class EventListener:
    """Event listener class."""

    def __init__(
        self,
        event_name: str,
        handler: Callable[[Event], None],
        priority: int = 0,
    ) -> None:
        """Initialize event listener.

        Args:
            event_name: Event name to listen for
            handler: Event handler function
            priority: Handler priority (higher priority handlers run first)
        """
        self.event_name = event_name
        self.handler = handler
        self.priority = priority


class EventBusConfig(BaseConfig):
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
        self._listeners: Dict[str, List[EventListener]] = {}
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
        """
        if not self.is_initialized:
            raise EventError("Event bus not initialized")

        self._stats["total_events"] += 1

        if event.name not in self._listeners:
            return

        # Sort listeners by priority
        listeners = sorted(
            self._listeners[event.name],
            key=lambda x: x.priority,
            reverse=True,
        )

        # Call handlers
        for listener in listeners:
            try:
                await listener.handler(event)
            except Exception as e:
                raise EventError(f"Failed to handle event {event.name}: {e}") from e

    def add_listener(
        self,
        event_name: str,
        handler: Callable[[Event], None],
        priority: int = 0,
    ) -> None:
        """Add event listener.

        Args:
            event_name: Event name to listen for
            handler: Event handler function
            priority: Handler priority (higher priority handlers run first)

        Raises:
            EventError: If event bus not initialized or max listeners reached
        """
        if not self.is_initialized:
            raise EventError("Event bus not initialized")

        if event_name not in self._listeners:
            self._listeners[event_name] = []

        # Check max listeners
        if len(self._listeners[event_name]) >= self.config.max_listeners:
            raise EventError(f"Max listeners ({self.config.max_listeners}) reached")

        # Add listener
        listener = EventListener(event_name, handler, priority)
        self._listeners[event_name].append(listener)
        self._stats["total_listeners"] += 1
        self._stats["active_listeners"] += 1

    def remove_listener(
        self,
        event_name: str,
        handler: Callable[[Event], None],
    ) -> None:
        """Remove event listener.

        Args:
            event_name: Event name
            handler: Event handler function

        Raises:
            EventError: If event bus not initialized or listener not found
        """
        if not self.is_initialized:
            raise EventError("Event bus not initialized")

        if event_name not in self._listeners:
            raise EventError(f"No listeners found for event {event_name}")

        # Find and remove listener
        for listener in self._listeners[event_name]:
            if listener.handler == handler:
                self._listeners[event_name].remove(listener)
                self._stats["active_listeners"] -= 1
                return

        raise EventError(f"Listener not found for event {event_name}")

    def get_listeners(self, event_name: str) -> List[EventListener]:
        """Get event listeners.

        Args:
            event_name: Event name

        Returns:
            List of event listeners

        Raises:
            EventError: If event bus not initialized
        """
        if not self.is_initialized:
            raise EventError("Event bus not initialized")

        return self._listeners.get(event_name, [])
