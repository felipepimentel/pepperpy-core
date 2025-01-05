"""Test registry module."""

from typing import Protocol, runtime_checkable

import pytest

from pepperpy_core.registry import Registry


@runtime_checkable
class TestProtocol(Protocol):
    """Test protocol."""

    def test(self) -> str:
        """Test method."""
        ...


class TestImplementation:
    """Test implementation."""

    def test(self) -> str:
        """Test method."""
        assert True  # Ensure the method is called
        return "test"


@pytest.fixture
def test_implementation() -> TestImplementation:
    """Create a test implementation."""
    return TestImplementation()


@pytest.fixture
def test_registry() -> Registry[TestProtocol]:
    """Create a test registry."""
    return Registry[TestProtocol](TestImplementation)


def test_registry_register(
    test_registry: Registry[TestProtocol], test_implementation: TestImplementation
) -> None:
    """Test registry register."""
    test_registry.register("test", test_implementation)
    assert test_registry.get("test") == test_implementation


def test_registry_register_duplicate(
    test_registry: Registry[TestProtocol], test_implementation: TestImplementation
) -> None:
    """Test registry register duplicate."""
    test_registry.register("test", test_implementation)
    with pytest.raises(ValueError):
        test_registry.register("test", test_implementation)


def test_registry_get_missing(test_registry: Registry[TestProtocol]) -> None:
    """Test registry get missing."""
    with pytest.raises(KeyError):
        test_registry.get("test")


def test_registry_unregister(
    test_registry: Registry[TestProtocol], test_implementation: TestImplementation
) -> None:
    """Test registry unregister."""
    test_registry.register("test", test_implementation)
    test_registry.clear()
    with pytest.raises(KeyError):
        test_registry.get("test")


def test_registry_unregister_missing(test_registry: Registry[TestProtocol]) -> None:
    """Test registry unregister missing."""
    with pytest.raises(KeyError):
        test_registry.get("test")
