"""Tests for the event module."""

import pytest
import pytest_asyncio

from pepperpy_core.event import Event, EventBus
from pepperpy_core.exceptions import EventError


@pytest_asyncio.fixture
async def event_bus() -> EventBus:
    """Create a test event bus."""
    bus = EventBus()
    await bus.initialize()
    yield bus
    await bus.teardown()


@pytest.mark.asyncio
async def test_event_bus_initialization() -> None:
    """Test event bus initialization."""
    bus = EventBus()
    assert not bus.is_initialized

    await bus.initialize()
    assert bus.is_initialized
    assert bus._listeners == {}
    assert bus._stats["total_events"] == 0
    assert bus._stats["total_listeners"] == 0
    assert bus._stats["active_listeners"] == 0

    await bus.teardown()
    assert not bus.is_initialized
    assert bus._listeners == {}


@pytest.mark.asyncio
async def test_event_emission(event_bus: EventBus) -> None:
    """Test event emission."""
    # Create test event
    event = Event("test_event", "test_data")

    # Create test handler
    handled_events = []

    async def handler(e: Event) -> None:
        handled_events.append(e)

    # Add handler and emit event
    event_bus.add_listener("test_event", handler)
    await event_bus.emit(event)

    # Check handler was called
    assert len(handled_events) == 1
    assert handled_events[0] == event


@pytest.mark.asyncio
async def test_event_priority(event_bus: EventBus) -> None:
    """Test event priority."""
    # Create test event
    event = Event("test_event", "test_data")

    # Create test handlers
    handled_events = []

    async def handler1(e: Event) -> None:
        handled_events.append(("handler1", e))

    async def handler2(e: Event) -> None:
        handled_events.append(("handler2", e))

    # Add handlers with different priorities
    event_bus.add_listener("test_event", handler1, priority=1)
    event_bus.add_listener("test_event", handler2, priority=2)

    # Emit event
    await event_bus.emit(event)

    # Check handlers were called in priority order
    assert len(handled_events) == 2
    assert handled_events[0][0] == "handler2"  # Higher priority
    assert handled_events[1][0] == "handler1"  # Lower priority


@pytest.mark.asyncio
async def test_remove_listener(event_bus: EventBus) -> None:
    """Test removing event listener."""
    # Create test event
    event = Event("test_event", "test_data")

    # Create test handler
    handled_events = []

    async def handler(e: Event) -> None:
        handled_events.append(e)

    # Add handler
    event_bus.add_listener("test_event", handler)

    # Remove handler
    event_bus.remove_listener("test_event", handler)

    # Emit event
    await event_bus.emit(event)

    # Check handler was not called
    assert len(handled_events) == 0


@pytest.mark.asyncio
async def test_get_events(event_bus: EventBus) -> None:
    """Test getting event listeners."""

    # Create test handlers
    async def handler1(e: Event) -> None:
        pass

    async def handler2(e: Event) -> None:
        pass

    # Add handlers
    event_bus.add_listener("test_event1", handler1)
    event_bus.add_listener("test_event2", handler2)

    # Get listeners
    listeners1 = event_bus.get_listeners("test_event1")
    listeners2 = event_bus.get_listeners("test_event2")

    # Check listeners
    assert len(listeners1) == 1
    assert len(listeners2) == 1
    assert listeners1[0].handler == handler1
    assert listeners2[0].handler == handler2


@pytest.mark.asyncio
async def test_event_with_metadata(event_bus: EventBus) -> None:
    """Test event with metadata."""
    # Create test event with metadata
    metadata = {"key": "value"}
    event = Event("test_event", "test_data", metadata=metadata)

    # Create test handler
    handled_events = []

    async def handler(e: Event) -> None:
        handled_events.append(e)

    # Add handler and emit event
    event_bus.add_listener("test_event", handler)
    await event_bus.emit(event)

    # Check handler was called with metadata
    assert len(handled_events) == 1
    assert handled_events[0].metadata == metadata


@pytest.mark.asyncio
async def test_event_bus_stats(event_bus: EventBus) -> None:
    """Test event bus statistics."""

    # Create test handlers
    async def handler1(e: Event) -> None:
        pass

    async def handler2(e: Event) -> None:
        pass

    # Add handlers
    event_bus.add_listener("test_event", handler1)
    event_bus.add_listener("test_event", handler2)

    # Emit events
    await event_bus.emit(Event("test_event", "test_data"))
    await event_bus.emit(Event("test_event", "test_data"))

    # Check stats
    assert event_bus._stats["total_events"] == 2
    assert event_bus._stats["total_listeners"] == 2
    assert event_bus._stats["active_listeners"] == 2


@pytest.mark.asyncio
async def test_event_error_handling(event_bus: EventBus) -> None:
    """Test event error handling."""
    # Create test event
    event = Event("test_event", "test_data")

    # Create failing handler
    async def failing_handler(e: Event) -> None:
        raise ValueError("Test error")

    # Add handler
    event_bus.add_listener("test_event", failing_handler)

    # Check error is propagated
    with pytest.raises(EventError) as exc_info:
        await event_bus.emit(event)
    assert "Failed to handle event test_event" in str(exc_info.value)
