"""Test registry module."""

from typing import Any, Dict

import pytest

from pepperpy.registry import Registry, RegistryError, RegistryProtocol


class TestProtocol(RegistryProtocol):
    """Test protocol."""

    def register(self, name: str, implementation: Any) -> None:
        """Register implementation."""
        return None

    def get(self, name: str) -> Any:
        """Get implementation."""
        return None

    def list(self) -> Dict[str, Any]:
        """List implementations."""
        return {}

    def test(self) -> str:
        """Test method."""
        return "test"


class TestImplementation(TestProtocol):
    """Test implementation."""

    def __init__(self) -> None:
        """Initialize test implementation."""
        self._implementations: Dict[str, Any] = {}

    def register(self, name: str, implementation: Any) -> None:
        """Register implementation."""
        self._implementations[name] = implementation

    def get(self, name: str) -> Any:
        """Get implementation."""
        return self._implementations[name]

    def list(self) -> Dict[str, Any]:
        """List implementations."""
        return self._implementations

    def test(self) -> str:
        """Test method."""
        return "test"


class InvalidImplementation:
    """Invalid implementation."""

    pass


@pytest.fixture
async def test_registry() -> Registry[TestProtocol]:
    """Create a test registry."""
    registry = Registry[TestProtocol]()
    await registry.initialize()
    return registry


@pytest.mark.asyncio
async def test_register_implementation(test_registry: Registry[TestProtocol]) -> None:
    """Test register implementation."""
    impl = TestImplementation()
    test_registry.register("test", impl)
    assert "test" in test_registry.list()


@pytest.mark.asyncio
async def test_register_duplicate_implementation(
    test_registry: Registry[TestProtocol],
) -> None:
    """Test register duplicate implementation."""
    impl = TestImplementation()
    test_registry.register("test", impl)
    with pytest.raises(RegistryError):
        test_registry.register("test", impl)


@pytest.mark.asyncio
async def test_get_implementation(test_registry: Registry[TestProtocol]) -> None:
    """Test get implementation."""
    impl = TestImplementation()
    test_registry.register("test", impl)
    assert test_registry.get("test") is impl


@pytest.mark.asyncio
async def test_get_invalid_implementation(
    test_registry: Registry[TestProtocol],
) -> None:
    """Test get invalid implementation."""
    with pytest.raises(RegistryError):
        test_registry.get("test")


@pytest.mark.asyncio
async def test_list_implementations(test_registry: Registry[TestProtocol]) -> None:
    """Test list implementations."""
    impl1 = TestImplementation()
    impl2 = TestImplementation()
    test_registry.register("test1", impl1)
    test_registry.register("test2", impl2)
    implementations = test_registry.list()
    assert len(implementations) == 2
    assert "test1" in implementations
    assert "test2" in implementations
