"""Test plugin module."""

import os
from pathlib import Path
from typing import Generator

import pytest

from pepperpy_core.exceptions import PluginError
from pepperpy_core.plugin import (
    PluginManager,
    ResourcePlugin,
    ResourcePluginConfig,
    plugin,
)


@pytest.fixture
def test_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a test file."""
    file_path = tmp_path / "test.txt"
    with open(file_path, "w") as f:
        f.write("test")
    yield file_path
    os.unlink(file_path)


@pytest.fixture
def resource_plugin() -> ResourcePlugin:
    """Get resource plugin."""
    plugin = ResourcePlugin()
    return plugin


@pytest.mark.asyncio
async def test_resource_plugin_create_resource(
    resource_plugin: ResourcePlugin, test_file: Path
) -> None:
    """Test resource plugin create resource."""
    await resource_plugin.initialize()
    info = await resource_plugin.create_resource("test", test_file)
    assert info.name == "test"
    assert info.path == test_file
    assert info.size > 0


@pytest.mark.asyncio
async def test_resource_plugin_get_resource(
    resource_plugin: ResourcePlugin, test_file: Path
) -> None:
    """Test resource plugin get resource."""
    await resource_plugin.initialize()
    await resource_plugin.create_resource("test", test_file)
    resource = await resource_plugin.get_resource("test")
    assert resource is not None
    assert resource.name == "test"
    assert resource.path == test_file


@pytest.mark.asyncio
async def test_resource_plugin_list_resources(
    resource_plugin: ResourcePlugin, test_file: Path
) -> None:
    """Test resource plugin list resources."""
    await resource_plugin.initialize()
    await resource_plugin.create_resource("test", test_file)
    resources = await resource_plugin.list_resources()
    assert len(resources) == 1
    assert resources[0].name == "test"
    assert resources[0].path == test_file


@pytest.mark.asyncio
async def test_resource_plugin_update_resource(
    resource_plugin: ResourcePlugin, test_file: Path
) -> None:
    """Test resource plugin update resource."""
    await resource_plugin.initialize()
    await resource_plugin.create_resource("test", test_file)
    updated = await resource_plugin.update_resource("test", {"version": "1.1"})
    assert updated.metadata["version"] == "1.1"


@pytest.mark.asyncio
async def test_resource_plugin_delete_resource(
    resource_plugin: ResourcePlugin, test_file: Path
) -> None:
    """Test resource plugin delete resource."""
    await resource_plugin.initialize()
    await resource_plugin.create_resource("test", test_file)
    await resource_plugin.delete_resource("test")
    resource = await resource_plugin.get_resource("test")
    assert resource is None


@plugin("test")
class TestPlugin:
    """Test plugin implementation."""

    def test_method(self) -> None:
        """Test method."""
        pass


@pytest.mark.asyncio
async def test_plugin_manager_load_plugin(tmp_path: Path) -> None:
    """Test plugin manager load plugin."""
    # Create plugin file
    plugin_file = tmp_path / "test_plugin.py"
    with open(plugin_file, "w") as f:
        f.write(
            """
from pepperpy_core.plugin import plugin

@plugin("test")
class TestPlugin:
    def test_method(self):
        pass
"""
        )

    # Load plugin
    manager = PluginManager()
    await manager.initialize()
    manager.load_plugin(plugin_file)

    # Get plugin
    plugin_instance = manager.get_plugin("test")
    assert plugin_instance is not None


@pytest.mark.asyncio
async def test_plugin_manager_get_plugin() -> None:
    """Test plugin manager get plugin."""
    manager = PluginManager()
    await manager.initialize()
    manager._plugins["test"] = TestPlugin()
    plugin_instance = manager.get_plugin("test")
    assert plugin_instance is not None


@pytest.mark.asyncio
async def test_plugin_manager_get_plugin_invalid() -> None:
    """Test plugin manager get plugin invalid."""
    manager = PluginManager()
    await manager.initialize()
    with pytest.raises(KeyError):
        manager.get_plugin("invalid")


@pytest.mark.asyncio
async def test_plugin_manager_get_stats() -> None:
    """Test plugin manager get stats."""
    manager = PluginManager()
    await manager.initialize()
    manager._plugins["test"] = TestPlugin()
    stats = await manager.get_stats()
    assert stats["name"] == "plugin_manager"
    assert stats["enabled"] is True
    assert stats["total_plugins"] == 1
    assert stats["plugin_names"] == ["test"]
