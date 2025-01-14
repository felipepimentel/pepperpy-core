"""Test module implementation."""

import pytest

from pepperpy.module import BaseModule, ModuleConfig, ModuleError


class TestModuleConfig(ModuleConfig):
    """Test module configuration."""

    pass


class TestModule(BaseModule[TestModuleConfig]):
    """Test module implementation."""

    async def _setup(self) -> None:
        """Setup module."""
        pass

    async def _teardown(self) -> None:
        """Teardown module."""
        pass


@pytest.mark.asyncio
async def test_module_init() -> None:
    """Test module initialization."""
    config = TestModuleConfig(name="test")
    module = TestModule(config)
    assert module.config == config
    assert not module.is_initialized


@pytest.mark.asyncio
async def test_module_init_with_metadata() -> None:
    """Test module initialization with metadata."""
    config = TestModuleConfig(name="test", metadata={"key": "value"})
    module = TestModule(config)
    assert module.config == config
    assert module.config.metadata == {"key": "value"}


@pytest.mark.asyncio
async def test_module_init_with_invalid_name() -> None:
    """Test module initialization with invalid name."""
    with pytest.raises(ValueError):
        TestModuleConfig(name="")


@pytest.mark.asyncio
async def test_module_get_stats() -> None:
    """Test get stats."""
    config = TestModuleConfig(name="test")
    module = TestModule(config)
    await module.initialize()
    assert module.is_initialized


@pytest.mark.asyncio
async def test_module_clear() -> None:
    """Test clear."""
    config = TestModuleConfig(name="test")
    module = TestModule(config)
    await module.initialize()
    await module.teardown()
    assert not module.is_initialized


@pytest.mark.asyncio
async def test_module_initialize() -> None:
    """Test initialize."""
    config = TestModuleConfig(name="test")
    module = TestModule(config)
    await module.initialize()
    assert module.is_initialized
    with pytest.raises(ModuleError):
        await module.initialize()


@pytest.mark.asyncio
async def test_module_cleanup() -> None:
    """Test cleanup."""
    config = TestModuleConfig(name="test")
    module = TestModule(config)
    await module.initialize()
    await module.teardown()
    assert not module.is_initialized
    # Calling teardown on uninitialized module should not raise
    await module.teardown()
