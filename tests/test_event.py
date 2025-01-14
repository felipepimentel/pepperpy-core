"""Test event module."""

import asyncio
from dataclasses import dataclass
from typing import Any, AsyncGenerator, List, Tuple

import pytest

from pepperpy.event import Event, EventBus, EventListener
from pepperpy.exceptions import EventError


@dataclass
class TestEvent(Event):
    """Test event."""

    data: Any


@pytest.fixture
async def event_bus() -> AsyncGenerator[EventBus, None]:
    """Create an event bus."""
    bus = EventBus()
    await bus.initialize()
    yield bus
    await bus.teardown()


@pytest.fixture
def test_event() -> TestEvent:
    """Create a test event."""
    return TestEvent(data="test")


@pytest.mark.asyncio
async def test_event_bus_emit(event_bus: EventBus, test_event: TestEvent) -> None:
    """Test event bus emit."""
    events: List[Event] = []

    def handler(event: Event) -> None:
        events.append(event)

    event_bus.add_listener(TestEvent, handler)
    await event_bus.emit(test_event)
    assert len(events) == 1
    assert events[0] == test_event


@pytest.mark.asyncio
async def test_event_bus_emit_async(event_bus: EventBus, test_event: TestEvent) -> None:
    """Test event bus emit with async handler."""
    events: List[Event] = []

    async def handler(event: Event) -> None:
        await asyncio.sleep(0.1)
        events.append(event)

    event_bus.add_listener(TestEvent, handler)
    await event_bus.emit(test_event)
    assert len(events) == 1
    assert events[0] == test_event


@pytest.mark.asyncio
async def test_event_bus_emit_priority(
    event_bus: EventBus, test_event: TestEvent
) -> None:
    """Test event bus emit with priority."""
    events: List[Tuple[str, Event]] = []

    def handler1(event: Event) -> None:
        events.append(("handler1", event))

    def handler2(event: Event) -> None:
        events.append(("handler2", event))

    event_bus.add_listener(TestEvent, handler1, priority=1)
    event_bus.add_listener(TestEvent, handler2, priority=2)
    await event_bus.emit(test_event)
    assert len(events) == 2
    assert events[0] == ("handler2", test_event)  # Higher priority handler called first
    assert events[1] == ("handler1", test_event)


@pytest.mark.asyncio
async def test_event_bus_remove_listener(
    event_bus: EventBus, test_event: TestEvent
) -> None:
    """Test event bus remove listener."""
    events: List[Event] = []

    def handler(event: Event) -> None:
        events.append(event)

    event_bus.add_listener(TestEvent, handler)
    event_bus.remove_listener(TestEvent, handler)
    await event_bus.emit(test_event)
    assert len(events) == 0


@pytest.mark.asyncio
async def test_event_bus_get_listeners(event_bus: EventBus) -> None:
    """Test event bus get listeners."""

    def handler1(event: Event) -> None:
        pass

    def handler2(event: Event) -> None:
        pass

    event_bus.add_listener(TestEvent, handler1)
    event_bus.add_listener(TestEvent, handler2)

    listeners = event_bus.get_listeners(TestEvent)
    assert len(listeners) == 2
    assert all(isinstance(listener, EventListener) for listener in listeners)
    assert {listener.handler for listener in listeners} == {handler1, handler2}


@pytest.mark.asyncio
async def test_event_bus_emit_error(event_bus: EventBus, test_event: TestEvent) -> None:
    """Test event bus emit error."""

    def handler(event: Event) -> None:
        raise ValueError("test error")

    event_bus.add_listener(TestEvent, handler)
    with pytest.raises(EventError):
        await event_bus.emit(test_event)


@pytest.mark.asyncio
async def test_event_bus_emit_not_initialized(test_event: TestEvent) -> None:
    """Test event bus emit when not initialized."""
    bus = EventBus()
    with pytest.raises(EventError):
        await bus.emit(test_event)


@pytest.mark.asyncio
async def test_event_bus_max_listeners(event_bus: EventBus) -> None:
    """Test event bus max listeners."""
    max_listeners = event_bus.config.max_listeners

    def handler(event: Event) -> None:
        pass

    # Add max_listeners listeners
    for _ in range(max_listeners):
        event_bus.add_listener(TestEvent, handler)

    # Try to add one more listener
    with pytest.raises(EventError):
        event_bus.add_listener(TestEvent, handler)


@pytest.mark.asyncio
async def test_event_bus_stats(event_bus: EventBus, test_event: TestEvent) -> None:
    """Test event bus stats."""

    def handler(event: Event) -> None:
        pass

    event_bus.add_listener(TestEvent, handler)
    await event_bus.emit(test_event)

    assert event_bus._stats["total_events"] == 1
    assert event_bus._stats["total_listeners"] == 1
    assert event_bus._stats["active_listeners"] == 1

    event_bus.remove_listener(TestEvent, handler)
    assert event_bus._stats["active_listeners"] == 0
