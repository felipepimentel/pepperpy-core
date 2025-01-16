"""Event module."""

import asyncio
import inspect
from dataclasses import dataclass, field
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    TypeVar,
    runtime_checkable,
)

from pepperpy.core import PepperpyError
from pepperpy.module import BaseModule, ModuleConfig


class EventError(PepperpyError):
    """Event error."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        event_type: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> None:
        """Initialize event error.

        Args:
            message: Error message
            context: Error context
            cause: Error cause
            event_type: Event type
            event_id: Event ID
        """
        super().__init__(message, context, cause)
        self.event_type = event_type
        self.event_id = event_id


T = TypeVar("T")


@dataclass
class Event:
    """Event class."""

    name: str
    data: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate event."""
        if not isinstance(self.name, str):
            raise ValueError("Event name must be a string")
        if not self.name:
            raise ValueError("Event name cannot be empty")


@dataclass
class EventListener:
    """Event listener class."""

    event_name: str
    handler: Callable[[Event], Awaitable[None]]
    priority: int = 0


@runtime_checkable
class EventMiddleware(Protocol):
    """Event middleware protocol."""

    async def before_event(self, event: Event) -> None:
        """Called before event is processed.

        Args:
            event: Event being processed
        """
        ...

    async def after_event(self, event: Event) -> None:
        """Called after event is processed.

        Args:
            event: Event that was processed
        """
        ...


@dataclass
class EventBusConfig(ModuleConfig):
    """Event bus configuration."""

    name: str = "event_bus"
    max_listeners: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class EventBus(BaseModule[EventBusConfig]):
    """Event bus implementation."""

    def __init__(self, config: Optional[EventBusConfig] = None) -> None:
        """Initialize event bus.

        Args:
            config: Optional event bus configuration
        """
        super().__init__(config or EventBusConfig())
        self._handlers: Dict[str, List[EventListener]] = {}
        self._middleware: List[EventMiddleware] = []
        self._lock = asyncio.Lock()
        self._stats: Dict[str, int] = {"events_processed": 0}

    async def _setup(self) -> None:
        """Set up event bus."""
        pass

    async def _teardown(self) -> None:
        """Clean up event bus."""
        await self.clear()

    async def add_listener(
        self,
        event_name: str,
        handler: Callable[[Event], Awaitable[None]],
        priority: int = 0,
    ) -> None:
        """Add event listener.

        Args:
            event_name: Event name
            handler: Event handler
            priority: Handler priority (higher priority handlers are called first)

        Raises:
            EventError: If handler is not async or max listeners reached
        """
        if not inspect.iscoroutinefunction(handler):
            raise EventError(
                "Event handler must be async",
                {"event_name": event_name},
            )

        async with self._lock:
            if event_name not in self._handlers:
                self._handlers[event_name] = []

            if (
                self.config.max_listeners is not None
                and len(self._handlers[event_name]) >= self.config.max_listeners
            ):
                raise EventError(
                    "Max listeners reached",
                    {
                        "event_name": event_name,
                        "max_listeners": self.config.max_listeners,
                    },
                )

            listener = EventListener(
                event_name=event_name, handler=handler, priority=priority
            )
            self._handlers[event_name].append(listener)
            self._handlers[event_name].sort(key=lambda x: x.priority, reverse=True)

    async def remove_listener(
        self, event_name: str, handler: Callable[[Event], Awaitable[None]]
    ) -> None:
        """Remove event listener.

        Args:
            event_name: Event name
            handler: Event handler
        """
        async with self._lock:
            if event_name in self._handlers:
                self._handlers[event_name] = [
                    listener
                    for listener in self._handlers[event_name]
                    if listener.handler != handler
                ]
                if not self._handlers[event_name]:
                    del self._handlers[event_name]

    async def add_middleware(self, middleware: EventMiddleware) -> None:
        """Add event middleware.

        Args:
            middleware: Event middleware
        """
        self._middleware.append(middleware)

    async def remove_middleware(self, middleware: EventMiddleware) -> None:
        """Remove event middleware.

        Args:
            middleware: Event middleware
        """
        if middleware in self._middleware:
            self._middleware.remove(middleware)

    async def emit(self, event: Event) -> None:
        """Emit event.

        Args:
            event: Event to emit
        """
        async with self._lock:
            listeners = self._handlers.get(event.name, []).copy()

        if not listeners:
            return

        # Call middleware before event
        for middleware in self._middleware:
            await middleware.before_event(event)

        # Call handlers
        tasks = [listener.handler(event) for listener in listeners]
        await asyncio.gather(*tasks)

        # Call middleware after event
        for middleware in self._middleware:
            await middleware.after_event(event)

        # Update stats
        self._stats["events_processed"] += 1

    def get_listeners(self, event_name: str) -> List[EventListener]:
        """Get event listeners.

        Args:
            event_name: Event name

        Returns:
            List of event listeners
        """
        return self._handlers.get(event_name, []).copy()

    def get_stats(self) -> Dict[str, Any]:
        """Get event bus stats.

        Returns:
            Event bus stats
        """
        return dict(self._stats)

    async def clear(self) -> None:
        """Clear all event handlers and middleware."""
        async with self._lock:
            self._handlers.clear()
            self._middleware.clear()
            self._stats["events_processed"] = 0


__all__ = [
    "Event",
    "EventBus",
    "EventBusConfig",
    "EventError",
    "EventListener",
    "EventMiddleware",
]
