"""Event handling system for PepperPy.

This module implements a robust event system that enables asynchronous communication
between different parts of the application. It provides:

- Event bus for publishing and subscribing to events
- Priority-based event handling
- Support for both function-based and class-based event handlers
- Event statistics tracking
- Configurable maximum listeners per event
- Middleware support for event lifecycle hooks
- Comprehensive error handling

The event system is designed to be:
- Asynchronous by default
- Type-safe with proper error handling
- Efficient with prioritized event processing
- Easy to monitor with built-in statistics
"""

import inspect
from typing import Any, Awaitable, Dict, List, Protocol, Union, runtime_checkable
from typing import Callable as Call

from .core import PepperpyError


class EventError(PepperpyError):
    """Event-related errors."""

    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
        event_type: str | None = None,
        event_id: str | None = None,
    ) -> None:
        """Initialize event error.

        Args:
            message: Error message
            cause: Original exception that caused this error
            event_type: Type of event that caused the error
            event_id: ID of the event that caused the error
        """
        super().__init__(message, cause)
        self.event_type = event_type
        self.event_id = event_id


class Event:
    """Base event class for the PepperPy event system.

    This class serves as the foundation for all events in the system. Events are
    used to communicate between different parts of the application in a loosely
    coupled way. Each event has a name for identification and optional data payload.

    Example:
        ```python
        class UserLoggedInEvent(Event):
            def __init__(self, user_id: str):
                super().__init__(name="user_logged_in", data={"user_id": user_id})
        ```
    """

    def __init__(self, name: str, data: Any = None) -> None:
        """Initialize event.

        Args:
            name: Event name
            data: Event data

        Raises:
            ValueError: If name is empty or invalid
        """
        if not name or not isinstance(name, str):
            raise ValueError("Event name must be a non-empty string")
        self.name = name
        self.data = data


@runtime_checkable
class EventHandler(Protocol):
    """Protocol defining the interface for event handlers.

    This protocol must be implemented by any class that wants to handle events
    in an object-oriented way. The handler method is asynchronous to support
    non-blocking event processing.

    Example:
        ```python
        class LoggingHandler(EventHandler):
            async def handle(self, event: Event) -> None:
                print(f"Handling event: {event.name}")
        ```
    """

    async def handle(self, event: Event) -> None:
        """Handle event.

        Args:
            event: Event to handle
        """
        ...


# Type alias for event handler functions
EventHandlerFunction = Call[[Event], Union[None, Awaitable[None]]]


class EventMiddleware(Protocol):
    """Event middleware protocol.

    This protocol defines the interface for middleware that can intercept
    and process events at various stages of their lifecycle.
    """

    def before(self, event: Event) -> None:
        """Called before event is handled."""
        ...

    def after(self, event: Event) -> None:
        """Called after event is handled."""
        ...

    def error(self, event: Event, error: Exception) -> None:
        """Called when error occurs during event handling."""
        ...


class EventListener:
    """Event listener that manages the binding between events and their handlers.

    This class represents a subscription to an event, containing:
    - The event name to listen for
    - The handler (function or class) to execute when the event occurs
    - The priority level that determines execution order

    Example:
        ```python
        async def log_event(event: Event) -> None:
            print(f"Event occurred: {event.name}")

        listener = EventListener("user_login", log_event, priority=1)
        ```
    """

    def __init__(
        self,
        event_name: str,
        handler: Union[EventHandler, EventHandlerFunction],
        priority: int = 0,
    ) -> None:
        """Initialize event listener.

        Args:
            event_name: Name of the event to listen for
            handler: Function or class that will handle the event
            priority: Execution priority (higher numbers execute first)
        """
        self.event_name = event_name
        self.handler = handler
        self.priority = priority


class EventBus:
    """Central event management system for asynchronous event handling.

    The EventBus provides a centralized point for:
    - Publishing events to interested subscribers
    - Managing event subscriptions with priority levels
    - Enforcing listener limits to prevent memory leaks
    - Tracking event statistics for monitoring
    - Supporting middleware for event lifecycle hooks
    - Comprehensive error handling

    The bus must be initialized before use and cleaned up when no longer needed.
    All operations are thread-safe and support async/await patterns.

    Example:
        ```python
        # Create and initialize the event bus
        bus = EventBus(max_listeners=5)
        await bus.initialize()

        # Add a listener
        async def handle_login(event: Event) -> None:
            user_id = event.data.get("user_id")
            print(f"User {user_id} logged in")

        bus.add_listener("user_login", handle_login)

        # Add middleware
        class LoggingMiddleware(EventMiddleware):
            def before(self, event: Event) -> None:
                print(f"Before event: {event.name}")
            def after(self, event: Event) -> None:
                print(f"After event: {event.name}")
            def error(self, event: Event, error: Exception) -> None:
                print(f"Error in event {event.name}: {error}")

        bus.add_middleware(LoggingMiddleware())

        # Emit an event
        event = Event("user_login", {"user_id": "123"})
        await bus.emit(event)

        # Clean up
        await bus.cleanup()
        ```
    """

    def __init__(self, max_listeners: int = 10) -> None:
        """Initialize event bus.

        Args:
            max_listeners: Maximum number of listeners allowed per event type.
                         This helps prevent memory leaks from unchecked listener growth.
        """
        self._listeners: Dict[str, List[EventListener]] = {}
        self._max_listeners = max_listeners
        self._stats: Dict[str, int] = {}
        self._initialized = False
        self._middleware: List[EventMiddleware] = []

    async def initialize(self) -> None:
        """Initialize the event bus for use.

        This method must be called before any other operations can be performed.
        It sets up internal data structures and prepares the bus for event handling.

        Raises:
            EventError: If initialization fails
        """
        await self._setup()
        self._initialized = True

    async def cleanup(self) -> None:
        """Clean up resources used by the event bus.

        This method should be called when the event bus is no longer needed.
        It removes all listeners, middleware, and clears statistics.

        Raises:
            EventError: If cleanup fails
        """
        await self._teardown()
        self._initialized = False

    async def _setup(self) -> None:
        """Set up internal event bus resources.

        This method can be overridden by subclasses to add custom initialization logic.
        """
        pass

    async def _teardown(self) -> None:
        """Release internal event bus resources.

        This method can be overridden by subclasses to add custom cleanup logic.
        """
        self._listeners.clear()
        self._stats.clear()
        self._middleware.clear()

    def add_listener(
        self,
        event_name: str,
        handler: Union[EventHandler, EventHandlerFunction],
        priority: int = 0,
    ) -> None:
        """Register a new event listener.

        This method adds a new handler for the specified event type. Handlers can be
        either functions or classes implementing the EventHandler protocol.

        Args:
            event_name: The name of the event to listen for
            handler: The function or class that will handle the event
            priority: Execution priority (higher numbers execute first)

        Raises:
            ValueError: If max listeners would be exceeded
            EventError: If event bus is not initialized
        """
        if not self._initialized:
            raise EventError("Event bus not initialized")

        if event_name not in self._listeners:
            self._listeners[event_name] = []

        if len(self._listeners[event_name]) >= self._max_listeners:
            raise ValueError(
                f"Max listeners ({self._max_listeners}) exceeded for event {event_name}"
            )

        listener = EventListener(event_name, handler, priority)
        self._listeners[event_name].append(listener)
        self._listeners[event_name].sort(key=lambda x: x.priority, reverse=True)

    def remove_listener(
        self, event_name: str, handler: Union[EventHandler, EventHandlerFunction]
    ) -> None:
        """Unregister an event listener.

        This method removes a previously registered handler for the specified event
        type.

        Args:
            event_name: Event type to unregister
            handler: Handler to unregister

        Raises:
            EventError: If event bus is not initialized
        """
        if not self._initialized:
            raise EventError("Event bus not initialized")

        if event_name in self._listeners:
            self._listeners[event_name] = [
                listener
                for listener in self._listeners[event_name]
                if listener.handler != handler
            ]

    def get_listeners(self, event_name: str) -> List[EventListener]:
        """Get all listeners registered for an event.

        This method returns a list of all handlers registered for the specified event,
        sorted by priority (highest first).

        Args:
            event_name: The name of the event to get listeners for

        Returns:
            List of event listeners sorted by priority

        Raises:
            EventError: If event bus is not initialized
        """
        if not self._initialized:
            raise EventError("Event bus not initialized")

        return self._listeners.get(event_name, [])

    def add_middleware(self, middleware: EventMiddleware) -> None:
        """Add middleware to the event bus.

        Args:
            middleware: The middleware instance to add

        Raises:
            EventError: If event bus is not initialized
        """
        if not self._initialized:
            raise EventError("Event bus not initialized")
        self._middleware.append(middleware)

    def remove_middleware(self, middleware: EventMiddleware) -> None:
        """Remove middleware from the event bus.

        Args:
            middleware: The middleware instance to remove

        Raises:
            EventError: If event bus is not initialized
        """
        if not self._initialized:
            raise EventError("Event bus not initialized")
        if middleware in self._middleware:
            self._middleware.remove(middleware)

    async def emit(self, event: Event) -> None:
        """Emit an event to all registered listeners.

        This method notifies all registered handlers of the event, executing them
        in priority order. Both synchronous and asynchronous handlers are supported.
        Middleware hooks are called before and after event handling, and on errors.

        Args:
            event: The event to emit

        Raises:
            EventError: If event bus is not initialized or if event handling fails
        """
        if not self._initialized:
            raise EventError("Event bus not initialized")

        if event.name not in self._stats:
            self._stats[event.name] = 0
        self._stats[event.name] += 1

        # Call before middleware hooks
        for middleware in self._middleware:
            try:
                middleware.before(event)
            except Exception as e:
                raise EventError(
                    "Middleware before hook failed", cause=e, event_type=event.name
                ) from e

        try:
            # Handle the event
            for listener in self.get_listeners(event.name):
                try:
                    handler = listener.handler
                    if isinstance(handler, EventHandler):
                        await handler.handle(event)
                    else:
                        result = handler(event)
                        if inspect.isawaitable(result):
                            await result
                except Exception as e:
                    # Call error middleware hooks
                    for middleware in self._middleware:
                        try:
                            middleware.error(event, e)
                        except Exception:
                            pass  # Don't let middleware errors propagate
                    raise EventError(
                        "Event handler failed", cause=e, event_type=event.name
                    ) from e

            # Call after middleware hooks
            for middleware in self._middleware:
                try:
                    middleware.after(event)
                except Exception as e:
                    raise EventError(
                        "Middleware after hook failed", cause=e, event_type=event.name
                    ) from e

        except Exception as e:
            if not isinstance(e, EventError):
                e = EventError("Event handling failed", cause=e, event_type=event.name)
            raise e

    def get_stats(self) -> Dict[str, int]:
        """Get event emission statistics.

        This method returns a dictionary containing the number of times each event
        type has been emitted. This is useful for monitoring and debugging.

        Returns:
            Dictionary mapping event names to emission counts

        Raises:
            EventError: If event bus is not initialized
        """
        if not self._initialized:
            raise EventError("Event bus not initialized")

        return self._stats.copy()
