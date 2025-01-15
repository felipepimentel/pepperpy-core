"""Test registry module."""

from typing import Protocol, runtime_checkable

import pytest

from pepperpy.registry import Registry, RegistryError


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


class InvalidImplementation:
    """Invalid implementation."""

    def invalid(self) -> str:
        """Invalid method."""
        return "invalid"


@pytest.fixture
def test_implementation() -> TestImplementation:
    """Create a test implementation."""
    return TestImplementation()


@pytest.fixture
def test_registry() -> Registry[TestProtocol]:
    """Create a test registry."""
    return Registry[TestProtocol](TestProtocol)


def test_registry_register(
    test_registry: Registry[TestProtocol], test_implementation: TestImplementation
) -> None:
    """Test registry register."""
    test_registry.register("test", test_implementation)
    assert test_registry.get("test") == test_implementation


def test_registry_register_class(test_registry: Registry[TestProtocol]) -> None:
    """Test registry register class."""
    test_registry.register("test", TestImplementation)
    impl = test_registry.get("test")
    assert isinstance(impl, TestImplementation)
    assert impl.test() == "test"


def test_registry_register_invalid_implementation(
    test_registry: Registry[TestProtocol],
) -> None:
    """Test registry register invalid implementation."""
    with pytest.raises(TypeError):
        test_registry.register("test", InvalidImplementation())


def test_registry_register_invalid_class(test_registry: Registry[TestProtocol]) -> None:
    """Test registry register invalid class."""
    with pytest.raises(TypeError):
        test_registry.register("test", InvalidImplementation)


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


def test_registry_list_implementations(
    test_registry: Registry[TestProtocol], test_implementation: TestImplementation
) -> None:
    """Test registry list implementations."""
    assert test_registry.list_implementations() == []
    test_registry.register("test1", test_implementation)
    test_registry.register("test2", TestImplementation)
    assert sorted(test_registry.list_implementations()) == ["test1", "test2"]


def test_registry_clear(
    test_registry: Registry[TestProtocol], test_implementation: TestImplementation
) -> None:
    """Test registry clear."""
    test_registry.register("test", test_implementation)
    assert test_registry.list_implementations() == ["test"]
    test_registry.clear()
    assert test_registry.list_implementations() == []


def test_registry_error() -> None:
    """Test registry error."""
    error = RegistryError(
        "test error",
        ValueError("cause"),
        "test_implementation",
        "test_protocol",
    )
    assert str(error) == "test error"
    assert isinstance(error.__cause__, ValueError)
    assert error.implementation_name == "test_implementation"
    assert error.protocol_name == "test_protocol"
