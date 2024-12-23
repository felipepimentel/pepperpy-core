"""Tests for the module module."""

from dataclasses import dataclass, field
from typing import Any

import pytest

from pepperpy_core.module import BaseModule, ModuleConfig, ModuleError


@pytest.fixture
def test_config() -> ModuleConfig:
    """Create a test configuration."""

    @dataclass
    class Config(ModuleConfig):
        """Test configuration."""

        name: str = "test-module"
        metadata: dict[str, Any] = field(default_factory=dict)

        def validate(self) -> None:
            """Validate configuration."""
            pass

    return Config()


@pytest.fixture
def test_module(test_config: ModuleConfig) -> BaseModule[ModuleConfig]:
    """Create a test module."""

    class Module(BaseModule[ModuleConfig]):
        """Test module implementation."""

        async def _setup(self) -> None:
            """Setup test module."""
            pass

        async def _teardown(self) -> None:
            """Teardown test module."""
            pass

    return Module(test_config)


@pytest.mark.asyncio
async def test_module_initialization_flow(
    test_module: BaseModule[ModuleConfig],
) -> None:
    """Test module initialization flow."""
    # Test initial state
    assert not test_module.is_initialized

    # Test successful initialization
    await test_module.initialize()
    assert test_module.is_initialized

    # Test double initialization protection
    try:
        await test_module.initialize()
        pytest.fail("Should have raised ModuleError")
    except ModuleError as error:
        assert str(error) == f"Module {test_module.config.name} is already initialized"

    # Test _ensure_initialized when initialized
    test_module._ensure_initialized()  # Should not raise

    # Test teardown
    await test_module.teardown()
    assert not test_module.is_initialized

    # Test _ensure_initialized when not initialized
    try:
        test_module._ensure_initialized()
        pytest.fail("Should have raised ModuleError")
    except ModuleError as error:
        assert str(error) == f"Module {test_module.config.name} is not initialized"


@pytest.mark.asyncio
async def test_module_config(test_config: ModuleConfig) -> None:
    """Test module configuration."""

    class Module(BaseModule[ModuleConfig]):
        """Test module implementation."""

        async def _setup(self) -> None:
            """Setup test module."""
            pass

        async def _teardown(self) -> None:
            """Teardown test module."""
            pass

    module = Module(test_config)
    assert module.config.name == "test-module"

    await module.initialize()
    assert module.is_initialized
    await module.teardown()
