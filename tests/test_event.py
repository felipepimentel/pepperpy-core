"""Test event module."""

import pytest

from pepperpy.event import Event, EventBus


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
