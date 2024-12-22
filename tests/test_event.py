"""Tests for the event module."""

from typing import Any

import pytest
import pytest_asyncio

from pepperpy_core.event import Event, EventBus, EventConfig, EventPriority


@pytest_asyncio.fixture
async def event_bus() -> EventBus[Any]:
    """Create an event bus for testing."""
    bus = EventBus(EventConfig(name="test_bus"))
    await bus.initialize()
    yield bus
    await bus._teardown()


@pytest.mark.asyncio
async def test_event_bus_initialization() -> None:
    """Test event bus initialization."""
    bus = EventBus[Any]()
    assert not bus.is_initialized
    await bus.initialize()
    assert bus.is_initialized
    await bus._teardown()


@pytest.mark.asyncio
async def test_event_emission(event_bus: EventBus[Any]) -> None:
    """Test event emission and handling."""
    received_events: list[Event[Any]] = []

    async def handler(event: Event[Any]) -> None:
        received_events.append(event)

    event_bus.add_listener("test_event", handler)
    event = Event(name="test_event", data="test_data")
    await event_bus.emit(event)

    assert len(received_events) == 1
    assert received_events[0].name == "test_event"
    assert received_events[0].data == "test_data"


@pytest.mark.asyncio
async def test_event_priority(event_bus: EventBus[Any]) -> None:
    """Test event handling priority."""
    received: list[str] = []

    async def low_priority(event: Event[Any]) -> None:
        received.append("low")

    async def high_priority(event: Event[Any]) -> None:
        received.append("high")

    event_bus.add_listener("test_event", low_priority, EventPriority.LOW)
    event_bus.add_listener("test_event", high_priority, EventPriority.HIGH)

    event = Event(name="test_event", data="test")
    await event_bus.emit(event)

    assert received == ["high", "low"]


@pytest.mark.asyncio
async def test_remove_listener(event_bus: EventBus[Any]) -> None:
    """Test removing event listener."""
    received_events: list[Event[Any]] = []

    async def handler(event: Event[Any]) -> None:
        received_events.append(event)

    event_bus.add_listener("test_event", handler)
    event_bus.remove_listener("test_event", handler)

    event = Event(name="test_event", data="test")
    await event_bus.emit(event)

    assert len(received_events) == 0


@pytest.mark.asyncio
async def test_get_events(event_bus: EventBus[Any]) -> None:
    """Test getting events."""
    event1 = Event(name="test_event1", data="test1")
    event2 = Event(name="test_event2", data="test2")
    event3 = Event(name="test_event1", data="test3")

    await event_bus.emit(event1)
    await event_bus.emit(event2)
    await event_bus.emit(event3)

    all_events = event_bus.get_events()
    assert len(all_events) == 3

    test_event1s = event_bus.get_events("test_event1")
    assert len(test_event1s) == 2
    assert all(e.name == "test_event1" for e in test_event1s)


@pytest.mark.asyncio
async def test_event_with_metadata(event_bus: EventBus[Any]) -> None:
    """Test event with metadata."""
    received_events: list[Event[Any]] = []

    async def handler(event: Event[Any]) -> None:
        received_events.append(event)

    event_bus.add_listener("test_event", handler)
    event = Event(
        name="test_event",
        data="test_data",
        metadata={"source": "test", "timestamp": 123},
    )
    await event_bus.emit(event)

    assert len(received_events) == 1
    assert received_events[0].metadata["source"] == "test"
    assert received_events[0].metadata["timestamp"] == 123


@pytest.mark.asyncio
async def test_event_bus_stats(event_bus: EventBus[Any]) -> None:
    """Test event bus statistics."""

    async def handler(event: Event[Any]) -> None:
        pass

    event_bus.add_listener("event1", handler)
    event_bus.add_listener("event2", handler)
    event_bus.add_listener("event2", handler)

    await event_bus.emit(Event(name="event1", data="test1"))
    await event_bus.emit(Event(name="event2", data="test2"))

    stats = await event_bus.get_stats()
    assert stats["name"] == "test_bus"
    assert stats["enabled"] is True
    assert stats["total_listeners"] == 3
    assert stats["total_events"] == 2
    assert set(stats["event_types"]) == {"event1", "event2"}


@pytest.mark.asyncio
async def test_event_error_handling(event_bus: EventBus[Any]) -> None:
    """Test error handling during event processing."""

    async def failing_handler(event: Event[Any]) -> None:
        raise ValueError("Test error")

    event_bus.add_listener("test_event", failing_handler)

    with pytest.raises(Exception) as exc_info:
        await event_bus.emit(Event(name="test_event", data="test"))
    assert "Test error" in str(exc_info.value)
