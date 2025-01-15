"""Test event module."""

import pytest

from pepperpy.event import (
    Event,
    EventBus,
    EventError,
    EventHandler,
    EventListener,
    EventMiddleware,
)


def test_event_init() -> None:
    """Test event initialization."""
    event = Event(name="test", data="test")
    assert event.name == "test"
    assert event.data == "test"


def test_event_init_with_metadata() -> None:
    """Test event initialization with metadata."""
    event = Event(name="test", data={"key": "value"})
    assert event.name == "test"
    assert event.data == {"key": "value"}


def test_event_init_with_invalid_name() -> None:
    """Test event initialization with invalid name."""
    with pytest.raises(ValueError):
        Event(name="", data="test")
    with pytest.raises(ValueError):
        Event(name=123)  # type: ignore


def test_event_error() -> None:
    """Test event error."""
    error = EventError(
        "test error",
        ValueError("cause"),
        "test_event",
        "event_123",
    )
    assert str(error) == "test error"
    assert isinstance(error.__cause__, ValueError)
    assert error.event_type == "test_event"
    assert error.event_id == "event_123"


class TestEventHandler(EventHandler):
    """Test event handler implementation."""

    def __init__(self) -> None:
        """Initialize test event handler."""
        self.events: list[Event] = []

    async def handle(self, event: Event) -> None:
        """Handle event."""
        self.events.append(event)


class TestEventMiddleware(EventMiddleware):
    """Test event middleware implementation."""

    def __init__(self) -> None:
        """Initialize test event middleware."""
        self.before_events: list[Event] = []
        self.after_events: list[Event] = []
        self.error_events: list[tuple[Event, Exception]] = []

    def before(self, event: Event) -> None:
        """Called before event is handled."""
        self.before_events.append(event)

    def after(self, event: Event) -> None:
        """Called after event is handled."""
        self.after_events.append(event)

    def error(self, event: Event, error: Exception) -> None:
        """Called when error occurs during event handling."""
        self.error_events.append((event, error))


@pytest.mark.asyncio
async def test_event_bus_init() -> None:
    """Test event bus initialization."""
    bus = EventBus()
    await bus.initialize()
    assert bus._initialized
    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_init_with_max_listeners() -> None:
    """Test event bus initialization with max listeners."""
    bus = EventBus(max_listeners=5)
    await bus.initialize()
    assert bus._max_listeners == 5
    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_double_init() -> None:
    """Test event bus double initialization."""
    bus = EventBus()
    await bus.initialize()
    await bus.initialize()  # Should not raise
    assert bus._initialized
    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_double_cleanup() -> None:
    """Test event bus double cleanup."""
    bus = EventBus()
    await bus.initialize()
    await bus.cleanup()
    await bus.cleanup()  # Should not raise
    assert not bus._initialized


@pytest.mark.asyncio
async def test_event_bus_add_listener() -> None:
    """Test add listener."""
    bus = EventBus()
    await bus.initialize()

    async def handler(event: Event) -> None:
        pass

    bus.add_listener("test", handler)
    assert len(bus.get_listeners("test")) == 1
    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_add_listener_with_priority() -> None:
    """Test add listener with priority."""
    bus = EventBus()
    await bus.initialize()

    async def handler1(event: Event) -> None:
        pass

    async def handler2(event: Event) -> None:
        pass

    bus.add_listener("test", handler1, priority=1)
    bus.add_listener("test", handler2, priority=2)

    listeners = bus.get_listeners("test")
    assert len(listeners) == 2
    assert listeners[0].priority == 2
    assert listeners[1].priority == 1

    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_add_listener_max_exceeded() -> None:
    """Test add listener max exceeded."""
    bus = EventBus(max_listeners=1)
    await bus.initialize()

    async def handler1(event: Event) -> None:
        pass

    async def handler2(event: Event) -> None:
        pass

    bus.add_listener("test", handler1)
    with pytest.raises(ValueError):
        bus.add_listener("test", handler2)

    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_remove_listener() -> None:
    """Test remove listener."""
    bus = EventBus()
    await bus.initialize()

    async def handler(event: Event) -> None:
        pass

    bus.add_listener("test", handler)
    bus.remove_listener("test", handler)
    assert len(bus.get_listeners("test")) == 0

    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_remove_nonexistent_listener() -> None:
    """Test remove nonexistent listener."""
    bus = EventBus()
    await bus.initialize()

    async def handler(event: Event) -> None:
        pass

    # Remove from nonexistent event
    bus.remove_listener("test", handler)  # Should not raise

    # Add and remove different handler
    bus.add_listener("test", handler)

    async def other_handler(event: Event) -> None:
        pass

    bus.remove_listener("test", other_handler)  # Should not raise
    assert len(bus.get_listeners("test")) == 1

    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_get_listeners() -> None:
    """Test get listeners."""
    bus = EventBus()
    await bus.initialize()

    async def handler(event: Event) -> None:
        pass

    bus.add_listener("test", handler)
    listeners = bus.get_listeners("test")
    assert len(listeners) == 1
    assert listeners[0].handler == handler

    # Test nonexistent event
    assert bus.get_listeners("nonexistent") == []

    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_emit() -> None:
    """Test emit event."""
    bus = EventBus()
    await bus.initialize()

    events = []

    async def handler(event: Event) -> None:
        events.append(event)

    bus.add_listener("test", handler)
    event = Event(name="test", data="test")
    await bus.emit(event)

    assert len(events) == 1
    assert events[0] == event

    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_emit_with_error() -> None:
    """Test emit event with error."""
    bus = EventBus()
    await bus.initialize()

    async def handler(event: Event) -> None:
        raise ValueError("test error")

    bus.add_listener("test", handler)
    event = Event(name="test", data="test")

    with pytest.raises(EventError) as exc_info:
        await bus.emit(event)
    assert "Event handler failed" in str(exc_info.value)
    assert "test error" in str(exc_info.value.__cause__)
    assert exc_info.value.event_type == "test"

    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_emit_with_multiple_handlers() -> None:
    """Test emit event with multiple handlers."""
    bus = EventBus()
    await bus.initialize()

    events1 = []
    events2 = []

    async def handler1(event: Event) -> None:
        events1.append(event)

    async def handler2(event: Event) -> None:
        events2.append(event)

    bus.add_listener("test", handler1, priority=1)
    bus.add_listener("test", handler2, priority=2)

    event = Event(name="test", data="test")
    await bus.emit(event)

    assert len(events1) == 1
    assert len(events2) == 1
    assert events1[0] == event
    assert events2[0] == event

    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_emit_with_handler_class() -> None:
    """Test emit event with handler class."""
    bus = EventBus()
    await bus.initialize()

    handler = TestEventHandler()
    bus.add_listener("test", handler)

    event = Event(name="test", data="test")
    await bus.emit(event)

    assert len(handler.events) == 1
    assert handler.events[0] == event

    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_emit_with_middleware() -> None:
    """Test emit event with middleware."""
    bus = EventBus()
    await bus.initialize()

    middleware = TestEventMiddleware()
    bus.add_middleware(middleware)

    events = []

    async def handler(event: Event) -> None:
        events.append(event)

    bus.add_listener("test", handler)
    event = Event(name="test", data="test")
    await bus.emit(event)

    assert len(events) == 1
    assert len(middleware.before_events) == 1
    assert len(middleware.after_events) == 1
    assert middleware.before_events[0] == event
    assert middleware.after_events[0] == event
    assert len(middleware.error_events) == 0

    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_emit_with_middleware_error() -> None:
    """Test emit event with middleware error."""
    bus = EventBus()
    await bus.initialize()

    middleware = TestEventMiddleware()
    bus.add_middleware(middleware)

    async def handler(event: Event) -> None:
        raise ValueError("test error")

    bus.add_listener("test", handler)
    event = Event(name="test", data="test")

    with pytest.raises(EventError) as exc_info:
        await bus.emit(event)

    assert len(middleware.before_events) == 1
    assert len(middleware.after_events) == 0
    assert len(middleware.error_events) == 1
    assert middleware.before_events[0] == event
    assert middleware.error_events[0][0] == event
    assert isinstance(middleware.error_events[0][1], ValueError)
    assert "Event handler failed" in str(exc_info.value)
    assert "test error" in str(exc_info.value.__cause__)

    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_get_stats() -> None:
    """Test get stats."""
    bus = EventBus()
    await bus.initialize()

    async def handler(event: Event) -> None:
        pass

    bus.add_listener("test", handler)
    event = Event(name="test", data="test")
    await bus.emit(event)
    await bus.emit(event)

    stats = bus.get_stats()
    assert stats["test"] == 2

    await bus.cleanup()


def test_event_listener() -> None:
    """Test event listener."""

    async def handler(event: Event) -> None:
        pass

    listener = EventListener("test", handler, priority=1)
    assert listener.event_name == "test"
    assert listener.handler == handler
    assert listener.priority == 1


@pytest.mark.asyncio
async def test_event_bus_add_middleware() -> None:
    """Test add middleware."""
    bus = EventBus()
    await bus.initialize()

    middleware = TestEventMiddleware()
    bus.add_middleware(middleware)
    assert middleware in bus._middleware

    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_add_middleware_not_initialized() -> None:
    """Test add middleware when bus is not initialized."""
    bus = EventBus()
    middleware = TestEventMiddleware()

    with pytest.raises(EventError) as exc_info:
        bus.add_middleware(middleware)
    assert "not initialized" in str(exc_info.value)


@pytest.mark.asyncio
async def test_event_bus_remove_middleware() -> None:
    """Test remove middleware."""
    bus = EventBus()
    await bus.initialize()

    middleware = TestEventMiddleware()
    bus.add_middleware(middleware)
    assert middleware in bus._middleware

    bus.remove_middleware(middleware)
    assert middleware not in bus._middleware

    # Remove nonexistent middleware should not raise
    bus.remove_middleware(middleware)

    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_remove_middleware_not_initialized() -> None:
    """Test remove middleware when bus is not initialized."""
    bus = EventBus()
    middleware = TestEventMiddleware()

    with pytest.raises(EventError) as exc_info:
        bus.remove_middleware(middleware)
    assert "not initialized" in str(exc_info.value)


@pytest.mark.asyncio
async def test_event_bus_middleware_before_error() -> None:
    """Test middleware before hook error."""
    bus = EventBus()
    await bus.initialize()

    class ErrorMiddleware(TestEventMiddleware):
        def before(self, event: Event) -> None:
            raise ValueError("before error")

    middleware = ErrorMiddleware()
    bus.add_middleware(middleware)

    event = Event(name="test", data="test")
    with pytest.raises(EventError) as exc_info:
        await bus.emit(event)
    assert "before hook failed" in str(exc_info.value)
    assert "before error" in str(exc_info.value.__cause__)

    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_middleware_after_error() -> None:
    """Test middleware after hook error."""
    bus = EventBus()
    await bus.initialize()

    class ErrorMiddleware(TestEventMiddleware):
        def after(self, event: Event) -> None:
            raise ValueError("after error")

    middleware = ErrorMiddleware()
    bus.add_middleware(middleware)

    async def handler(event: Event) -> None:
        pass

    bus.add_listener("test", handler)
    event = Event(name="test", data="test")

    with pytest.raises(EventError) as exc_info:
        await bus.emit(event)
    assert "after hook failed" in str(exc_info.value)
    assert "after error" in str(exc_info.value.__cause__)

    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_middleware_error_hook_error() -> None:
    """Test middleware error hook error."""
    bus = EventBus()
    await bus.initialize()

    class ErrorMiddleware(TestEventMiddleware):
        def error(self, event: Event, error: Exception) -> None:
            raise ValueError("error hook error")

    middleware = ErrorMiddleware()
    bus.add_middleware(middleware)

    async def handler(event: Event) -> None:
        raise ValueError("handler error")

    bus.add_listener("test", handler)
    event = Event(name="test", data="test")

    with pytest.raises(EventError) as exc_info:
        await bus.emit(event)
    assert "Event handler failed" in str(exc_info.value)
    assert "handler error" in str(exc_info.value.__cause__)
    # Error hook errors should be suppressed
    assert "error hook error" not in str(exc_info.value)

    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_emit_with_multiple_middleware() -> None:
    """Test emit event with multiple middleware."""
    bus = EventBus()
    await bus.initialize()

    middleware1 = TestEventMiddleware()
    middleware2 = TestEventMiddleware()
    bus.add_middleware(middleware1)
    bus.add_middleware(middleware2)

    events = []

    async def handler(event: Event) -> None:
        events.append(event)

    bus.add_listener("test", handler)
    event = Event(name="test", data="test")
    await bus.emit(event)

    assert len(events) == 1
    assert len(middleware1.before_events) == 1
    assert len(middleware1.after_events) == 1
    assert len(middleware2.before_events) == 1
    assert len(middleware2.after_events) == 1
    assert middleware1.before_events[0] == event
    assert middleware1.after_events[0] == event
    assert middleware2.before_events[0] == event
    assert middleware2.after_events[0] == event

    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_emit_with_sync_handler() -> None:
    """Test emit event with synchronous handler."""
    bus = EventBus()
    await bus.initialize()

    events = []

    def handler(event: Event) -> None:
        events.append(event)

    bus.add_listener("test", handler)
    event = Event(name="test", data="test")
    await bus.emit(event)

    assert len(events) == 1
    assert events[0] == event

    await bus.cleanup()


@pytest.mark.asyncio
async def test_event_bus_emit_with_sync_handler_error() -> None:
    """Test emit event with synchronous handler error."""
    bus = EventBus()
    await bus.initialize()

    def handler(event: Event) -> None:
        raise ValueError("sync error")

    bus.add_listener("test", handler)
    event = Event(name="test", data="test")

    with pytest.raises(EventError) as exc_info:
        await bus.emit(event)
    assert "Event handler failed" in str(exc_info.value)
    assert "sync error" in str(exc_info.value.__cause__)

    await bus.cleanup()
