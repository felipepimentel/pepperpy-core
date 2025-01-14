"""Test plugin implementation."""

import pytest

from pepperpy.plugin import PluginConfig, PluginManager


@pytest.mark.asyncio
async def test_plugin_init() -> None:
    """Test plugin initialization."""
    config = PluginConfig(name="test")
    manager = PluginManager(config)
    assert manager.config == config
    assert not manager.is_initialized


@pytest.mark.asyncio
async def test_plugin_init_with_metadata() -> None:
    """Test plugin initialization with metadata."""
    config = PluginConfig(name="test", metadata={"key": "value"})
    manager = PluginManager(config)
    assert manager.config == config
    assert manager.config.metadata == {"key": "value"}


@pytest.mark.asyncio
async def test_plugin_init_with_invalid_name() -> None:
    """Test plugin initialization with invalid name."""
    with pytest.raises(ValueError):
        PluginConfig(name="")


@pytest.mark.asyncio
async def test_plugin_manager_init() -> None:
    """Test plugin manager initialization."""
    manager = PluginManager()
    assert manager.config.name == "plugin_manager"
    assert manager.config.plugin_dir == "plugins"
    assert manager._plugins == {}


@pytest.mark.asyncio
async def test_plugin_manager_init_with_config() -> None:
    """Test plugin manager initialization with config."""
    config = PluginConfig(name="test", plugin_dir="test_plugins")
    manager = PluginManager(config)
    assert manager.config == config


@pytest.mark.asyncio
async def test_plugin_manager_setup() -> None:
    """Test plugin manager setup."""
    manager = PluginManager()
    await manager.initialize()
    assert manager.is_initialized
    assert manager._plugins == {}


@pytest.mark.asyncio
async def test_plugin_manager_teardown() -> None:
    """Test plugin manager teardown."""
    manager = PluginManager()
    await manager.initialize()
    await manager.teardown()
    assert not manager.is_initialized
    assert manager._plugins == {}


@pytest.mark.asyncio
async def test_plugin_manager_get_stats() -> None:
    """Test get stats."""
    manager = PluginManager()
    stats = await manager.get_stats()
    assert stats["name"] == "plugin_manager"
    assert stats["enabled"] is True
    assert stats["plugin_dir"] == "plugins"
    assert stats["total_plugins"] == 0
    assert stats["plugin_names"] == []
