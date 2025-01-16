"""Test module system."""

from dataclasses import dataclass

import pytest

from pepperpy.module import BaseModule, ModuleConfig


@dataclass
class TestConfig(ModuleConfig):
    """Test configuration."""

    value: str = "test"


class TestModule(BaseModule[TestConfig]):
    """Test module."""

    async def _setup(self) -> None:
        """Set up module."""
        pass

    async def _teardown(self) -> None:
        """Clean up module."""
        pass


@pytest.fixture
def test_config() -> TestConfig:
    """Create test configuration."""
    return TestConfig(name="test-module")


@pytest.fixture
def test_module(test_config: TestConfig) -> TestModule:
    """Create test module."""
    return TestModule(test_config)


@pytest.mark.asyncio
async def test_module_init(test_config: TestConfig) -> None:
    """Test module initialization."""
    module = TestModule(test_config)
    assert module.config == test_config
    assert not module.is_initialized


@pytest.mark.asyncio
async def test_module_init_with_invalid_name() -> None:
    """Test module initialization with invalid name."""
    with pytest.raises(ValueError):
        TestModule(TestConfig(name=""))


@pytest.mark.asyncio
async def test_module_initialize(test_module: TestModule) -> None:
    """Test module initialization."""
    await test_module.initialize()
    assert test_module.is_initialized


@pytest.mark.asyncio
async def test_module_initialize_twice(test_module: TestModule) -> None:
    """Test module initialization twice."""
    await test_module.initialize()
    await test_module.initialize()
    assert test_module.is_initialized


@pytest.mark.asyncio
async def test_module_teardown(test_module: TestModule) -> None:
    """Test module teardown."""
    await test_module.initialize()
    await test_module.teardown()
    assert not test_module.is_initialized


@pytest.mark.asyncio
async def test_module_teardown_twice(test_module: TestModule) -> None:
    """Test module teardown twice."""
    await test_module.initialize()
    await test_module.teardown()
    await test_module.teardown()
    assert not test_module.is_initialized
