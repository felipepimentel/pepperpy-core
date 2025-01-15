"""Test plugin implementation."""

from pathlib import Path

import pytest

from pepperpy.plugin import (
    PluginConfig,
    PluginError,
    PluginManager,
    ResourcePlugin,
    ResourcePluginConfig,
    is_plugin,
    plugin,
)
from pepperpy.resources import ResourceError, ResourceInfo


@pytest.fixture
def plugin_dir(tmp_path: Path) -> Path:
    """Create a temporary plugin directory."""
    return tmp_path / "plugins"


@pytest.fixture
def plugin_file(plugin_dir: Path) -> Path:
    """Create a temporary plugin file."""
    plugin_dir.mkdir(exist_ok=True)
    plugin_file = plugin_dir / "test_plugin.py"
    plugin_file.write_text(
        """
from pepperpy.plugin import plugin

@plugin("test")
class TestPlugin:
    def __init__(self):
        self.name = "test"
"""
    )
    return plugin_file


@pytest.fixture
def resource_dir(tmp_path: Path) -> Path:
    """Create a temporary resource directory."""
    return tmp_path / "resources"


@pytest.fixture
def resource_file(resource_dir: Path) -> Path:
    """Create a temporary resource file."""
    resource_dir.mkdir(exist_ok=True)
    resource_file = resource_dir / "test_resource.txt"
    resource_file.write_text("test resource content")
    return resource_file


@pytest.fixture
async def resource_plugin(resource_dir: Path) -> ResourcePlugin:
    """Create a resource plugin fixture."""
    config = ResourcePluginConfig(
        name="test",
        plugin_dir="plugins",
        resource_dir=str(resource_dir),
    )
    plugin = ResourcePlugin(config)
    await plugin.initialize()
    yield plugin
    await plugin.cleanup()


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
async def test_plugin_init_with_invalid_plugin_dir() -> None:
    """Test plugin initialization with invalid plugin directory."""
    with pytest.raises(ValueError):
        PluginConfig(name="test", plugin_dir=123)  # type: ignore


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


@pytest.mark.asyncio
async def test_plugin_manager_load_plugin(plugin_file: Path) -> None:
    """Test loading a plugin."""
    manager = PluginManager()
    await manager.initialize()
    manager.load_plugin(plugin_file)
    assert len(manager._plugins) == 1
    assert "test" in manager._plugins


@pytest.mark.asyncio
async def test_plugin_manager_load_plugin_error(plugin_dir: Path) -> None:
    """Test loading a non-existent plugin."""
    manager = PluginManager()
    await manager.initialize()
    with pytest.raises(PluginError):
        manager.load_plugin(plugin_dir / "non_existent.py")


@pytest.mark.asyncio
async def test_plugin_manager_get_plugin(plugin_file: Path) -> None:
    """Test getting a plugin."""
    manager = PluginManager()
    await manager.initialize()
    manager.load_plugin(plugin_file)
    plugin_instance = manager.get_plugin("test")
    assert plugin_instance.name == "test"


@pytest.mark.asyncio
async def test_plugin_manager_get_plugin_error() -> None:
    """Test getting a non-existent plugin."""
    manager = PluginManager()
    await manager.initialize()
    with pytest.raises(PluginError):
        manager.get_plugin("non_existent")


@pytest.mark.asyncio
async def test_plugin_manager_get_plugins(plugin_file: Path) -> None:
    """Test getting all plugins."""
    manager = PluginManager()
    await manager.initialize()
    manager.load_plugin(plugin_file)
    plugins = manager.get_plugins()
    assert len(plugins) == 1
    assert plugins[0].name == "test"


@pytest.mark.asyncio
async def test_plugin_decorator() -> None:
    """Test plugin decorator."""

    @plugin("test")
    class TestPlugin:
        pass

    assert hasattr(TestPlugin, "__plugin_name__")
    assert TestPlugin.__plugin_name__ == "test"


@pytest.mark.asyncio
async def test_is_plugin() -> None:
    """Test is_plugin function."""

    @plugin("test")
    class TestPlugin:
        pass

    class NotAPlugin:
        pass

    assert is_plugin(TestPlugin)
    assert not is_plugin(NotAPlugin)


@pytest.mark.asyncio
async def test_resource_plugin_config() -> None:
    """Test resource plugin configuration."""
    config = ResourcePluginConfig(
        name="test",
        plugin_dir="plugins",
        resource_dir="resources",
    )
    assert config.name == "test"
    assert config.plugin_dir == "plugins"
    assert config.resource_dir == "resources"


@pytest.mark.asyncio
async def test_resource_plugin() -> None:
    """Test resource plugin."""
    plugin = ResourcePlugin()
    assert plugin.config.name == "resource_manager"
    assert plugin.config.resource_dir == "resources"
    assert not plugin._initialized

    await plugin.initialize()
    assert plugin._initialized

    await plugin.cleanup()
    assert not plugin._initialized


@pytest.mark.asyncio
async def test_resource_plugin_with_config() -> None:
    """Test resource plugin with custom configuration."""
    config = ResourcePluginConfig(
        name="test",
        plugin_dir="plugins",
        resource_dir="test_resources",
    )
    plugin = ResourcePlugin(config)
    assert plugin.config == config
    assert not plugin._initialized

    await plugin.initialize()
    assert plugin._initialized

    await plugin.cleanup()
    assert not plugin._initialized


@pytest.mark.asyncio
async def test_resource_plugin_double_initialize() -> None:
    """Test resource plugin double initialization."""
    plugin = ResourcePlugin()
    await plugin.initialize()
    await plugin.initialize()  # Should not raise
    assert plugin._initialized


@pytest.mark.asyncio
async def test_resource_plugin_double_cleanup() -> None:
    """Test resource plugin double cleanup."""
    plugin = ResourcePlugin()
    await plugin.initialize()
    await plugin.cleanup()
    await plugin.cleanup()  # Should not raise
    assert not plugin._initialized


@pytest.mark.asyncio
async def test_resource_plugin_ensure_initialized() -> None:
    """Test resource plugin ensure initialized."""
    plugin = ResourcePlugin()
    with pytest.raises(ResourceError):
        plugin._ensure_initialized()

    await plugin.initialize()
    plugin._ensure_initialized()  # Should not raise


@pytest.mark.asyncio
async def test_resource_plugin_create_resource(
    resource_plugin: ResourcePlugin, resource_file: Path
) -> None:
    """Test creating a resource."""
    metadata = {"test": True}
    resource = await resource_plugin.create_resource(
        "test", str(resource_file), metadata
    )
    assert isinstance(resource, ResourceInfo)
    assert resource.name == "test"
    assert str(resource.path) == str(resource_file)
    assert resource.metadata == metadata


@pytest.mark.asyncio
async def test_resource_plugin_get_resource(
    resource_plugin: ResourcePlugin, resource_file: Path
) -> None:
    """Test getting a resource."""
    await resource_plugin.create_resource("test", str(resource_file))
    resource = await resource_plugin.get_resource("test")
    assert resource is not None
    assert resource.name == "test"
    assert str(resource.path) == str(resource_file)


@pytest.mark.asyncio
async def test_resource_plugin_get_missing_resource(
    resource_plugin: ResourcePlugin,
) -> None:
    """Test getting a non-existent resource."""
    resource = await resource_plugin.get_resource("missing")
    assert resource is None


@pytest.mark.asyncio
async def test_resource_plugin_list_resources(
    resource_plugin: ResourcePlugin, resource_file: Path
) -> None:
    """Test listing resources."""
    await resource_plugin.create_resource("test1", str(resource_file))
    await resource_plugin.create_resource("test2", str(resource_file))

    resources = await resource_plugin.list_resources()
    assert len(resources) == 2
    assert {r.name for r in resources} == {"test1", "test2"}


@pytest.mark.asyncio
async def test_resource_plugin_update_resource(
    resource_plugin: ResourcePlugin, resource_file: Path
) -> None:
    """Test updating a resource."""
    await resource_plugin.create_resource(
        "test", str(resource_file), {"version": "1.0"}
    )

    resource = await resource_plugin.update_resource(
        "test", {"version": "2.0", "updated": True}
    )
    assert resource.metadata == {"version": "2.0", "updated": True}


@pytest.mark.asyncio
async def test_resource_plugin_update_missing_resource(
    resource_plugin: ResourcePlugin,
) -> None:
    """Test updating a non-existent resource."""
    with pytest.raises(ResourceError):
        await resource_plugin.update_resource("missing", {"test": True})


@pytest.mark.asyncio
async def test_resource_plugin_delete_resource(
    resource_plugin: ResourcePlugin, resource_file: Path
) -> None:
    """Test deleting a resource."""
    await resource_plugin.create_resource("test", str(resource_file))
    await resource_plugin.delete_resource("test")
    assert await resource_plugin.get_resource("test") is None


@pytest.mark.asyncio
async def test_resource_plugin_delete_missing_resource(
    resource_plugin: ResourcePlugin,
) -> None:
    """Test deleting a non-existent resource."""
    with pytest.raises(ResourceError):
        await resource_plugin.delete_resource("missing")
