"""Tests for the plugin module."""

from pathlib import Path

import pytest
import pytest_asyncio

from pepperpy_core.exceptions import PluginError
from pepperpy_core.plugin import PluginConfig, PluginManager, is_plugin, plugin


@pytest.fixture
def plugin_dir(tmp_path: Path) -> Path:
    """Create a temporary plugin directory."""
    return tmp_path / "plugins"


@pytest.fixture
def plugin_manager(plugin_dir: Path) -> PluginManager:
    """Create a plugin manager for testing."""
    return PluginManager(PluginConfig(name="test_manager", plugin_dir=plugin_dir))


@pytest.fixture
def plugin_file(plugin_dir: Path) -> Path:
    """Create a test plugin file."""
    plugin_dir.mkdir(exist_ok=True)
    plugin_file = plugin_dir / "test_plugin.py"
    plugin_file.write_text(
        """
from pepperpy_core.plugin import plugin

@plugin("test_plugin")
class TestPlugin:
    def hello(self) -> str:
        return "Hello from test plugin!"
"""
    )
    return plugin_file


@pytest.fixture
def invalid_plugin_file(plugin_dir: Path) -> Path:
    """Create an invalid plugin file."""
    plugin_dir.mkdir(exist_ok=True)
    plugin_file = plugin_dir / "invalid_plugin.py"
    plugin_file.write_text("this is not valid Python code")
    return plugin_file


def test_plugin_decorator() -> None:
    """Test plugin decorator."""

    @plugin("test")
    class TestPlugin:
        pass

    assert is_plugin(TestPlugin)
    assert TestPlugin.__plugin_name__ == "test"


def test_is_plugin() -> None:
    """Test is_plugin function."""

    @plugin("test")
    class TestPlugin:
        pass

    class NotAPlugin:
        pass

    assert is_plugin(TestPlugin)
    assert not is_plugin(NotAPlugin)
    assert not is_plugin(object())


@pytest_asyncio.fixture
async def initialized_manager(plugin_manager: PluginManager) -> PluginManager:
    """Create an initialized plugin manager."""
    await plugin_manager.initialize()
    return plugin_manager


@pytest.mark.asyncio
async def test_plugin_manager_init() -> None:
    """Test plugin manager initialization."""
    manager = PluginManager()
    assert manager.config.name == "plugin_manager"
    assert manager.config.plugin_dir == "plugins"
    assert manager.config.enabled is True

    config = PluginConfig(name="test", plugin_dir="test_plugins", enabled=False)
    manager = PluginManager(config)
    assert manager.config.name == "test"
    assert manager.config.plugin_dir == "test_plugins"
    assert manager.config.enabled is False


@pytest.mark.asyncio
async def test_plugin_manager_stats(initialized_manager: PluginManager) -> None:
    """Test plugin manager statistics."""
    stats = await initialized_manager.get_stats()
    assert stats["name"] == "test_manager"
    assert stats["enabled"] is True
    assert stats["plugin_dir"] == str(initialized_manager.config.plugin_dir)
    assert stats["total_plugins"] == 0
    assert stats["plugin_names"] == []


@pytest.mark.asyncio
async def test_load_plugin(
    initialized_manager: PluginManager, plugin_file: Path
) -> None:
    """Test loading a plugin."""
    initialized_manager.load_plugin(plugin_file)
    plugin_instance = initialized_manager.get_plugin("test_plugin")
    assert plugin_instance is not None
    assert plugin_instance.hello() == "Hello from test plugin!"


@pytest.mark.asyncio
async def test_load_invalid_plugin(
    initialized_manager: PluginManager, invalid_plugin_file: Path
) -> None:
    """Test loading an invalid plugin."""
    with pytest.raises(PluginError):
        initialized_manager.load_plugin(invalid_plugin_file)


@pytest.mark.asyncio
async def test_get_nonexistent_plugin(initialized_manager: PluginManager) -> None:
    """Test getting a nonexistent plugin."""
    with pytest.raises(KeyError):
        initialized_manager.get_plugin("nonexistent")


@pytest.mark.asyncio
async def test_get_plugins(
    initialized_manager: PluginManager, plugin_file: Path
) -> None:
    """Test getting all plugins."""
    assert initialized_manager.get_plugins() == []

    initialized_manager.load_plugin(plugin_file)
    plugins = initialized_manager.get_plugins()
    assert len(plugins) == 1
    assert plugins[0].hello() == "Hello from test plugin!"


@pytest.mark.asyncio
async def test_plugin_manager_teardown(
    initialized_manager: PluginManager, plugin_file: Path
) -> None:
    """Test plugin manager teardown."""
    initialized_manager.load_plugin(plugin_file)
    assert len(initialized_manager.get_plugins()) == 1

    await initialized_manager.teardown()
    assert not initialized_manager.is_initialized
