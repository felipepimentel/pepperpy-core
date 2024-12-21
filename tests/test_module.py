"""Test module functionality."""

from collections.abc import AsyncGenerator
from typing import Any, AsyncIterator, TypeVar

import pytest
import pytest_asyncio

from pepperpy_core.module import BaseModule
from pepperpy_core.types import BaseConfigData

T = TypeVar("T")


async def async_next(agen: AsyncGenerator[T, None]) -> T:
    """Get next value from async generator."""
    try:
        return await agen.__anext__()
    except StopAsyncIteration:
        raise StopAsyncIteration("No more items")


class MockModuleConfig(BaseConfigData):
    """Mock module configuration for testing."""

    name: str = "test"


class MockModule(BaseModule[MockModuleConfig]):
    """Mock module implementation for testing."""

    async def _setup(self) -> None:
        """Setup mock module."""
        pass

    async def _teardown(self) -> None:
        """Teardown mock module."""
        pass

    async def get_stats(self) -> dict[str, Any]:
        """Get mock module statistics."""
        return {
            "name": self.config.name,
            "total_data": 0,
            "data_keys": [],
            "test_value": None,
        }


@pytest_asyncio.fixture
async def test_module() -> AsyncIterator[MockModule]:
    """Create test module fixture."""
    config = MockModuleConfig(name="test", enabled=True)
    module = MockModule(config)
    await module.initialize()
    yield module
    await module.cleanup()


@pytest.mark.asyncio
async def test_module_initialization(test_module: MockModule) -> None:
    """Test module initialization."""
    assert test_module.is_initialized
    await test_module.initialize()  # Should be idempotent
    assert test_module.is_initialized


@pytest.mark.asyncio
async def test_module_cleanup(test_module: MockModule) -> None:
    """Test module cleanup."""
    assert test_module.is_initialized
    await test_module.cleanup()
    assert not test_module.is_initialized


@pytest.mark.asyncio
async def test_module_stats(test_module: MockModule) -> None:
    """Test module statistics."""
    stats = await test_module.get_stats()
    assert isinstance(stats, dict)
    assert stats["name"] == "test"
    assert stats["total_data"] == 0
    assert stats["data_keys"] == []
    assert stats["test_value"] is None


@pytest.mark.asyncio
async def test_module_error_handling(test_module: MockModule) -> None:
    """Test module error handling."""
    # Test uninitialized state
    await test_module.cleanup()
    assert not test_module.is_initialized

    # Reinitialize for cleanup
    await test_module.initialize()
