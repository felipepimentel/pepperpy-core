"""Tests for the resources module."""

from pathlib import Path

import pytest

from pepperpy_core.resources import (
    ResourceConfig,
    ResourceError,
    ResourceInfo,
    ResourceManager,
)


@pytest.fixture
def resource_dir(tmp_path: Path) -> Path:
    """Create a temporary resource directory."""
    resource_dir = tmp_path / "resources"
    resource_dir.mkdir()
    return resource_dir


@pytest.fixture
def resource_file(resource_dir: Path) -> Path:
    """Create a test resource file."""
    resource_file = resource_dir / "test.txt"
    resource_file.write_text("test content")
    return resource_file


@pytest.fixture
def resource_manager() -> ResourceManager:
    """Create a resource manager for testing."""
    manager = ResourceManager()
    manager.initialize()
    return manager


def test_resource_config() -> None:
    """Test resource configuration."""
    # Test default values
    config = ResourceConfig(name="test", path="/path/to/resource")
    assert config.name == "test"
    assert config.path == "/path/to/resource"
    assert isinstance(config.metadata, dict)
    assert len(config.metadata) == 0

    # Test custom values
    config = ResourceConfig(
        name="test",
        path=Path("/path/to/resource"),
        metadata={"key": "value"},
    )
    assert config.name == "test"
    assert isinstance(config.path, Path)
    assert str(config.path) == "/path/to/resource"
    assert config.metadata == {"key": "value"}


def test_resource_info() -> None:
    """Test resource information."""
    # Test default values
    info = ResourceInfo(name="test", path=Path("/path/to/resource"), size=100)
    assert info.name == "test"
    assert isinstance(info.path, Path)
    assert str(info.path) == "/path/to/resource"
    assert info.size == 100
    assert isinstance(info.metadata, dict)
    assert len(info.metadata) == 0

    # Test custom values
    info = ResourceInfo(
        name="test",
        path=Path("/path/to/resource"),
        size=100,
        metadata={"key": "value"},
    )
    assert info.name == "test"
    assert isinstance(info.path, Path)
    assert str(info.path) == "/path/to/resource"
    assert info.size == 100
    assert info.metadata == {"key": "value"}


def test_resource_manager_initialization() -> None:
    """Test resource manager initialization."""
    manager = ResourceManager()
    assert not manager._initialized

    # Test double initialization
    manager.initialize()
    assert manager._initialized
    manager.initialize()  # Should not raise
    assert manager._initialized

    # Test cleanup
    manager.cleanup()
    assert not manager._initialized
    manager.cleanup()  # Should not raise
    assert not manager._initialized


def test_resource_manager_uninitialized() -> None:
    """Test resource manager operations when uninitialized."""
    manager = ResourceManager()

    with pytest.raises(ResourceError, match="Resource manager not initialized"):
        manager.get_resource("test")

    with pytest.raises(ResourceError, match="Resource manager not initialized"):
        manager.add_resource("test", "/path/to/resource")

    with pytest.raises(ResourceError, match="Resource manager not initialized"):
        manager.remove_resource("test")

    with pytest.raises(ResourceError, match="Resource manager not initialized"):
        manager.list_resources()


def test_resource_manager_add_resource(
    resource_manager: ResourceManager, resource_file: Path
) -> None:
    """Test adding resources."""
    # Test basic add
    info = resource_manager.add_resource("test", resource_file)
    assert isinstance(info, ResourceInfo)
    assert info.name == "test"
    assert info.path == resource_file
    assert info.size == len("test content")
    assert isinstance(info.metadata, dict)
    assert len(info.metadata) == 0

    # Test add with metadata
    info = resource_manager.add_resource("test2", resource_file, {"key": "value"})
    assert info.name == "test2"
    assert info.metadata == {"key": "value"}

    # Test add duplicate
    with pytest.raises(ResourceError, match="Resource test already exists"):
        resource_manager.add_resource("test", resource_file)

    # Test add non-existent file
    with pytest.raises(
        ResourceError, match="Resource path /nonexistent/file does not exist"
    ):
        resource_manager.add_resource("test3", "/nonexistent/file")


def test_resource_manager_get_resource(
    resource_manager: ResourceManager, resource_file: Path
) -> None:
    """Test getting resources."""
    # Test get non-existent resource
    assert resource_manager.get_resource("test") is None

    # Test get existing resource
    info = resource_manager.add_resource("test", resource_file)
    retrieved = resource_manager.get_resource("test")
    assert retrieved == info


def test_resource_manager_remove_resource(
    resource_manager: ResourceManager, resource_file: Path
) -> None:
    """Test removing resources."""
    # Test remove non-existent resource
    with pytest.raises(ResourceError, match="Resource test not found"):
        resource_manager.remove_resource("test")

    # Test remove existing resource
    resource_manager.add_resource("test", resource_file)
    resource_manager.remove_resource("test")
    assert resource_manager.get_resource("test") is None


def test_resource_manager_list_resources(
    resource_manager: ResourceManager, resource_file: Path
) -> None:
    """Test listing resources."""
    # Test empty list
    assert resource_manager.list_resources() == []

    # Test list with resources
    info1 = resource_manager.add_resource("test1", resource_file)
    info2 = resource_manager.add_resource("test2", resource_file)

    resources = resource_manager.list_resources()
    assert len(resources) == 2
    assert info1 in resources
    assert info2 in resources
