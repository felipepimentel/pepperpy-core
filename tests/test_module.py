"""Tests for the module module."""

import pytest
import pytest_asyncio

from pepperpy_core.module import BaseModule, ModuleError

from .conftest import TestConfig


class TestModule(BaseModule[TestConfig]):
    """Test module implementation."""

    @classmethod
    def create(cls) -> "TestModule":
        """Create a test module instance."""
        instance = cls.__new__(cls)
        super(cls, instance).__init__(TestConfig())
        return instance

    async def _setup(self) -> None:
        """Setup test module."""
        pass

    async def _teardown(self) -> None:
        """Teardown test module."""
        pass


@pytest_asyncio.fixture
async def test_module():
    """Create a test module for testing."""
    module = TestModule.create()
    await module.initialize()
    yield module
    await module.teardown()


@pytest.mark.asyncio
async def test_module_initialization() -> None:
    """Test module initialization."""
    module = TestModule.create()
    assert not module.is_initialized
    await module.initialize()
    assert module.is_initialized
    await module.teardown()
    assert not module.is_initialized


@pytest.mark.asyncio
async def test_module_double_initialization() -> None:
    """Test double initialization."""
    module = TestModule.create()
    await module.initialize()
    with pytest.raises(ModuleError):
        await module.initialize()
    await module.teardown()


@pytest.mark.asyncio
async def test_module_ensure_initialized() -> None:
    """Test ensure initialized check."""
    module = TestModule.create()
    with pytest.raises(ModuleError):
        module._ensure_initialized()

    await module.initialize()
    module._ensure_initialized()  # Should not raise
    await module.teardown()


@pytest.mark.asyncio
async def test_module_config(test_module) -> None:
    """Test module configuration."""
    config = TestConfig(name="custom_module", metadata={"key": "value"})
    test_module.config = config

    assert test_module.config.name == "custom_module"
    assert test_module.config.metadata == {"key": "value"}
