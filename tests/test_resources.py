"""Test resources module."""

import os
from pathlib import Path
from typing import Generator

import pytest

from pepperpy.resources import (
    ResourceConfig,
    ResourceError,
    ResourceInfo,
    ResourceManager,
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
def resource_manager() -> ResourceManager:
    """Get resource manager."""
    manager = ResourceManager()
    manager.initialize()
    return manager


def test_resource_config() -> None:
    """Test resource configuration."""
    config = ResourceConfig(name="test", path="test.txt")
    assert config.name == "test"
    assert config.path == "test.txt"
    assert config.metadata == {}

    config = ResourceConfig(
        name="test", path=Path("test.txt"), metadata={"key": "value"}
    )
    assert config.name == "test"
    assert isinstance(config.path, Path)
    assert config.metadata == {"key": "value"}


def test_resource_info() -> None:
    """Test resource information."""
    info = ResourceInfo(name="test", path=Path("test.txt"), size=123)
    assert info.name == "test"
    assert info.path == Path("test.txt")
    assert info.size == 123
    assert info.metadata == {}

    info = ResourceInfo(
        name="test",
        path=Path("test.txt"),
        size=123,
        metadata={"key": "value"},
    )
    assert info.name == "test"
    assert info.path == Path("test.txt")
    assert info.size == 123
    assert info.metadata == {"key": "value"}


def test_resource_error() -> None:
    """Test resource error."""
    error = ResourceError("test error")
    assert str(error) == "test error"
    assert error.resource_name is None

    error = ResourceError(
        "test error",
        ValueError("cause"),
        "test_resource",
    )
    assert str(error) == "test error"
    assert isinstance(error.__cause__, ValueError)
    assert error.resource_name == "test_resource"


def test_resource_manager_initialize() -> None:
    """Test resource manager initialize."""
    manager = ResourceManager()
    assert not manager._initialized

    manager.initialize()
    assert manager._initialized

    # Double initialization should not raise
    manager.initialize()
    assert manager._initialized


def test_resource_manager_cleanup() -> None:
    """Test resource manager cleanup."""
    manager = ResourceManager()
    manager.initialize()
    assert manager._initialized

    manager.cleanup()
    assert not manager._initialized

    # Double cleanup should not raise
    manager.cleanup()
    assert not manager._initialized


def test_resource_manager_get_resource_not_initialized() -> None:
    """Test resource manager get resource when not initialized."""
    manager = ResourceManager()
    with pytest.raises(ResourceError, match="Resource manager not initialized"):
        manager.get_resource("test")


def test_resource_manager_get_resource(resource_manager: ResourceManager) -> None:
    """Test resource manager get resource."""
    resource = resource_manager.get_resource("test")
    assert resource is None


def test_resource_manager_add_resource_not_initialized() -> None:
    """Test resource manager add resource when not initialized."""
    manager = ResourceManager()
    with pytest.raises(ResourceError, match="Resource manager not initialized"):
        manager.add_resource("test", "test.txt")


def test_resource_manager_add_resource_duplicate(
    resource_manager: ResourceManager, test_file: Path
) -> None:
    """Test resource manager add resource with duplicate name."""
    resource_manager.add_resource("test", test_file)
    with pytest.raises(ResourceError, match="Resource test already exists"):
        resource_manager.add_resource("test", test_file)


def test_resource_manager_add_resource_missing_file(
    resource_manager: ResourceManager,
) -> None:
    """Test resource manager add resource with missing file."""
    with pytest.raises(ResourceError, match="Resource path .* does not exist"):
        resource_manager.add_resource("test", "missing.txt")


def test_resource_manager_add_resource(
    resource_manager: ResourceManager, test_file: Path
) -> None:
    """Test resource manager add resource."""
    info = resource_manager.add_resource("test", test_file)
    assert info.name == "test"
    assert info.path == test_file
    assert info.size > 0
    assert info.metadata == {}

    info = resource_manager.add_resource("test2", test_file, metadata={"key": "value"})
    assert info.name == "test2"
    assert info.path == test_file
    assert info.size > 0
    assert info.metadata == {"key": "value"}


def test_resource_manager_remove_resource_not_initialized() -> None:
    """Test resource manager remove resource when not initialized."""
    manager = ResourceManager()
    with pytest.raises(ResourceError, match="Resource manager not initialized"):
        manager.remove_resource("test")


def test_resource_manager_remove_resource_missing(
    resource_manager: ResourceManager,
) -> None:
    """Test resource manager remove resource with missing name."""
    with pytest.raises(ResourceError, match="Resource test not found"):
        resource_manager.remove_resource("test")


def test_resource_manager_remove_resource(
    resource_manager: ResourceManager, test_file: Path
) -> None:
    """Test resource manager remove resource."""
    resource_manager.add_resource("test", test_file)
    resource_manager.remove_resource("test")
    resource = resource_manager.get_resource("test")
    assert resource is None


def test_resource_manager_list_resources_not_initialized() -> None:
    """Test resource manager list resources when not initialized."""
    manager = ResourceManager()
    with pytest.raises(ResourceError, match="Resource manager not initialized"):
        manager.list_resources()


def test_resource_manager_list_resources(
    resource_manager: ResourceManager, test_file: Path
) -> None:
    """Test resource manager list resources."""
    assert resource_manager.list_resources() == []

    resource_manager.add_resource("test", test_file)
    resources = resource_manager.list_resources()
    assert len(resources) == 1
    assert resources[0].name == "test"
    assert resources[0].path == test_file
    assert resources[0].size > 0
