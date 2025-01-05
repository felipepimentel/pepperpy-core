"""Test resources module."""

import os
from pathlib import Path
from typing import Generator

import pytest

from pepperpy_core.resources import ResourceManager


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


def test_resource_manager_get_resource(resource_manager: ResourceManager) -> None:
    """Test resource manager get resource."""
    resource = resource_manager.get_resource("test")
    assert resource is None


def test_resource_manager_add_resource(
    resource_manager: ResourceManager, test_file: Path
) -> None:
    """Test resource manager add resource."""
    info = resource_manager.add_resource("test", test_file)
    assert info.name == "test"
    assert info.path == test_file
    assert info.size > 0


def test_resource_manager_remove_resource(
    resource_manager: ResourceManager, test_file: Path
) -> None:
    """Test resource manager remove resource."""
    resource_manager.add_resource("test", test_file)
    resource_manager.remove_resource("test")
    resource = resource_manager.get_resource("test")
    assert resource is None


def test_resource_manager_list_resources(
    resource_manager: ResourceManager, test_file: Path
) -> None:
    """Test resource manager list resources."""
    resource_manager.add_resource("test", test_file)
    resources = resource_manager.list_resources()
    assert len(resources) == 1
    assert resources[0].name == "test"
    assert resources[0].path == test_file
    assert resources[0].size > 0
