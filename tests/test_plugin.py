"""Test plugin module."""

from pathlib import Path
from typing import AsyncGenerator

import pytest

from pepperpy_core.plugin import PluginConfig, PluginManager, plugin


@plugin("test")
class TestPlugin:
    """Test plugin implementation."""

    def test_method(self) -> None:
        """Test method."""
        assert "test" == "test"


@pytest.fixture
async def plugin_manager() -> AsyncGenerator[PluginManager, None]:
    """Get plugin manager."""
    manager = PluginManager(PluginConfig(name="test"))
    await manager.initialize()
    yield manager
    await manager._teardown()


@pytest.mark.asyncio
async def test_plugin_manager_load_plugin(
    plugin_manager: PluginManager, tmp_path: Path
) -> None:
    """Test plugin manager load plugin."""
    plugin_file = tmp_path / "test_plugin.py"
    with open(plugin_file, "w") as f:
        f.write(
            """
from pepperpy_core.plugin import plugin

@plugin("test")
class TestPlugin:
    def test_method(self):
        return "test"
"""
        )
    plugin_manager.load_plugin(plugin_file)
    plugins = plugin_manager.get_plugins()
    assert len(plugins) == 1
    assert plugins[0].test_method() == "test"


@pytest.mark.asyncio
async def test_plugin_manager_get_plugin(
    plugin_manager: PluginManager, tmp_path: Path
) -> None:
    """Test plugin manager get plugin."""
    plugin_file = tmp_path / "test_plugin.py"
    with open(plugin_file, "w") as f:
        f.write(
            """
from pepperpy_core.plugin import plugin

@plugin("test")
class TestPlugin:
    def test_method(self):
        return "test"
"""
        )
    plugin_manager.load_plugin(plugin_file)
    plugin = plugin_manager.get_plugin("test")
    assert plugin.test_method() == "test"


@pytest.mark.asyncio
async def test_plugin_manager_get_plugin_invalid(plugin_manager: PluginManager) -> None:
    """Test plugin manager get plugin invalid."""
    with pytest.raises(KeyError):
        plugin_manager.get_plugin("invalid")


@pytest.mark.asyncio
async def test_plugin_manager_get_stats(plugin_manager: PluginManager) -> None:
    """Test plugin manager get stats."""
    stats = await plugin_manager.get_stats()
    assert stats["name"] == "test"
    assert stats["enabled"] is True
    assert stats["plugin_dir"] == "plugins"
    assert stats["total_plugins"] == 0
    assert stats["plugin_names"] == []
