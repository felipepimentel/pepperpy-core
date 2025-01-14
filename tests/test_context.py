"""Tests for the context module."""

from typing import Any

import pytest

from pepperpy.context import Context, State


@pytest.fixture
def context() -> Context[Any]:
    """Create a context for testing."""
    return Context()


def test_context_get_set(context: Context[str]) -> None:
    """Test getting and setting context values."""
    assert context.get("key1") is None
    assert context.get("key1", "default") == "default"

    context.set("key1", "value1")
    assert context.get("key1") == "value1"


def test_context_update(context: Context[str]) -> None:
    """Test updating context with dictionary."""
    data = {
        "key1": "value1",
        "key2": "value2",
    }
    context.update(data)

    assert context.get("key1") == "value1"
    assert context.get("key2") == "value2"


def test_context_get_set_context(context: Context[str]) -> None:
    """Test getting and setting current context value."""
    assert context.get_context() is None

    context.set_context("test_value")
    assert context.get_context() == "test_value"

    context.set_context(None)
    assert context.get_context() is None


def test_context_get_set_state(context: Context[str]) -> None:
    """Test getting and setting state."""
    assert context.get_state() is None

    context.set_state("test_state", source="test", timestamp=123)
    state = context.get_state()

    assert state is not None
    assert state.value == "test_state"
    assert state.metadata["source"] == "test"
    assert state.metadata["timestamp"] == 123


def test_state_dataclass() -> None:
    """Test State dataclass."""
    state = State(value="test", metadata={"key": "value"})
    assert state.value == "test"
    assert state.metadata["key"] == "value"

    # Test default metadata
    state = State(value="test")
    assert isinstance(state.metadata, dict)
    assert len(state.metadata) == 0


def test_context_with_different_types() -> None:
    """Test context with different value types."""
    # String context
    str_context: Context[str] = Context()
    str_context.set("key", "value")
    assert str_context.get("key") == "value"

    # Integer context
    int_context: Context[int] = Context()
    int_context.set("key", 42)
    assert int_context.get("key") == 42

    # Dict context
    dict_context: Context[dict[str, Any]] = Context()
    dict_context.set("key", {"nested": "value"})
    assert dict_context.get("key") == {"nested": "value"}


def test_context_isolation() -> None:
    """Test that different contexts are isolated."""
    context1: Context[str] = Context()
    context2: Context[str] = Context()

    context1.set("key", "value1")
    context2.set("key", "value2")

    assert context1.get("key") == "value1"
    assert context2.get("key") == "value2"


def test_context_state_isolation() -> None:
    """Test that state is isolated between contexts."""
    context1: Context[str] = Context()
    context2: Context[str] = Context()

    context1.set_state("state1", meta="data1")
    context2.set_state("state2", meta="data2")

    state1 = context1.get_state()
    state2 = context2.get_state()

    assert state1 is not None and state2 is not None
    assert state1.value == "state1"
    assert state2.value == "state2"
    assert state1.metadata["meta"] == "data1"
    assert state2.metadata["meta"] == "data2"


def test_context_var_isolation() -> None:
    """Test that context variables are isolated."""
    context1: Context[str] = Context()
    context2: Context[str] = Context()

    context1.set_context("value1")
    context2.set_context("value2")

    assert context1.get_context() == "value1"
    assert context2.get_context() == "value2"
