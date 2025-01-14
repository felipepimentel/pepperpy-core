"""Test module module."""

from typing import AsyncGenerator

import pytest

from pepperpy.exceptions import InitializationError
from pepperpy.module import BaseModule, ModuleConfig


class TestModule(BaseModule[ModuleConfig]):
    """Test module implementation."""

    def __init__(self, config: ModuleConfig | None = None) -> None:
        """Initialize test module.

        Args:
            config: Module configuration
        """
        super().__init__(config or ModuleConfig(name="test"))

    async def _setup(self) -> None:
        """Set up module."""
        pass

    async def _teardown(self) -> None:
        """Tear down module."""
        pass


@pytest.fixture
async def module() -> AsyncGenerator[TestModule, None]:
    """Get test module."""
    module = TestModule()
    await module.initialize()
    yield module
    await module.teardown()


@pytest.mark.asyncio
async def test_module_initialize(module: TestModule) -> None:
    """Test module initialize."""
    assert module.is_initialized


@pytest.mark.asyncio
async def test_module_teardown(module: TestModule) -> None:
    """Test module teardown."""
    await module.teardown()
    assert not module.is_initialized


@pytest.mark.asyncio
async def test_module_initialize_twice(module: TestModule) -> None:
    """Test module initialize twice."""
    with pytest.raises(InitializationError):
        await module.initialize()


@pytest.mark.asyncio
async def test_module_teardown_twice(module: TestModule) -> None:
    """Test module teardown twice."""
    await module.teardown()
    await module.teardown()
    assert not module.is_initialized
