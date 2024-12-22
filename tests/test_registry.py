"""Tests for the registry module."""

import pytest
import pytest_asyncio

from pepperpy_core.registry import Registry, RegistryConfig, RegistryError, RegistryItem


def test_registry_config() -> None:
    """Test registry configuration."""
    # Test default values
    config = RegistryConfig(name="test")
    config.validate()
    assert config.name == "test"
    assert config.enabled is True
    assert config.max_items == 1000
    assert isinstance(config.metadata, dict)
    assert len(config.metadata) == 0

    # Test custom values
    config = RegistryConfig(
        name="test",
        enabled=False,
        max_items=100,
        metadata={"key": "value"},
    )
    config.validate()
    assert config.name == "test"
    assert config.enabled is False
    assert config.max_items == 100
    assert config.metadata == {"key": "value"}

    # Test validation
    config = RegistryConfig(name="test", max_items=0)
    with pytest.raises(ValueError):
        config.validate()


def test_registry_item() -> None:
    """Test registry item."""
    # Test default values
    item = RegistryItem[str](name="test", value="value")
    assert item.name == "test"
    assert item.value == "value"
    assert isinstance(item.metadata, dict)
    assert len(item.metadata) == 0

    # Test custom values
    item = RegistryItem[int](
        name="test",
        value=42,
        metadata={"key": "value"},
    )
    assert item.name == "test"
    assert item.value == 42
    assert item.metadata == {"key": "value"}


@pytest_asyncio.fixture
async def registry() -> Registry[str]:
    """Create a registry for testing."""
    registry = Registry[str]()
    await registry.initialize()
    return registry


@pytest.mark.asyncio
async def test_registry_init() -> None:
    """Test registry initialization."""
    registry = Registry[str]()
    assert registry.config.name == "registry"
    assert registry.config.enabled is True
    assert registry.config.max_items == 1000


@pytest.mark.asyncio
async def test_registry_stats(registry: Registry[str]) -> None:
    """Test registry statistics."""
    stats = await registry.get_stats()
    assert stats["name"] == "registry"
    assert stats["enabled"] is True
    assert stats["total_items"] == 0
    assert stats["item_names"] == []
    assert stats["max_items"] == 1000


@pytest.mark.asyncio
async def test_registry_register(registry: Registry[str]) -> None:
    """Test item registration."""
    # Test basic registration
    registry.register("test", "value")
    assert registry.get("test") == "value"

    # Test registration with metadata
    registry.register("test2", "value2", {"key": "value"})
    item = registry.get_item("test2")
    assert item.value == "value2"
    assert item.metadata == {"key": "value"}

    # Test duplicate registration
    with pytest.raises(RegistryError):
        registry.register("test", "value3")

    # Test registry full
    registry.config.max_items = 2
    with pytest.raises(RegistryError):
        registry.register("test3", "value3")


@pytest.mark.asyncio
async def test_registry_unregister(registry: Registry[str]) -> None:
    """Test item unregistration."""
    registry.register("test", "value")
    assert registry.get("test") == "value"

    registry.unregister("test")
    with pytest.raises(KeyError):
        registry.get("test")

    # Test unregistering non-existent item
    with pytest.raises(KeyError):
        registry.unregister("nonexistent")


@pytest.mark.asyncio
async def test_registry_get(registry: Registry[str]) -> None:
    """Test getting items."""
    registry.register("test", "value")

    # Test get value
    assert registry.get("test") == "value"

    # Test get item
    item = registry.get_item("test")
    assert isinstance(item, RegistryItem)
    assert item.name == "test"
    assert item.value == "value"

    # Test getting non-existent item
    with pytest.raises(KeyError):
        registry.get("nonexistent")

    with pytest.raises(KeyError):
        registry.get_item("nonexistent")


@pytest.mark.asyncio
async def test_registry_list_items(registry: Registry[str]) -> None:
    """Test listing items."""
    assert registry.list_items() == []

    registry.register("test1", "value1")
    registry.register("test2", "value2")

    items = registry.list_items()
    assert len(items) == 2
    assert all(isinstance(item, RegistryItem) for item in items)
    assert {item.name for item in items} == {"test1", "test2"}
    assert {item.value for item in items} == {"value1", "value2"}


@pytest.mark.asyncio
async def test_registry_clear(registry: Registry[str]) -> None:
    """Test clearing registry."""
    registry.register("test1", "value1")
    registry.register("test2", "value2")
    assert len(registry.list_items()) == 2

    registry.clear()
    assert len(registry.list_items()) == 0


@pytest.mark.asyncio
async def test_registry_teardown(registry: Registry[str]) -> None:
    """Test registry teardown."""
    registry.register("test", "value")
    assert len(registry.list_items()) == 1

    await registry.teardown()
    assert not registry.is_initialized
    assert len(registry._items) == 0
