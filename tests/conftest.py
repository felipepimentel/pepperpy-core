"""Test configuration module."""

from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from typing import Any

import pytest
from pepperpy_core.base import BaseConfigData, BaseModule


@dataclass
class _TestConfig(BaseConfigData):  # Inherit from BaseConfigData
    """Test configuration."""

    name: str = "test"
    value: str = "test_value"
    enabled: bool = True  # Required by BaseConfigData
    metadata: dict[str, Any] = field(default_factory=dict)  # Required by BaseConfigData


class _TestModule(BaseModule[_TestConfig]):
    """Test module implementation."""

    def __init__(self, config: _TestConfig) -> None:
        """Initialize test module."""
        super().__init__(config)
        self._data: dict[str, Any] = {}

    async def _setup(self) -> None:
        """Setup module resources."""
        self._data = {}

    async def _teardown(self) -> None:
        """Teardown module resources."""
        self._data.clear()

    async def get_stats(self) -> dict[str, Any]:
        """Get module statistics."""
        self._ensure_initialized()
        return {
            "total_data": len(self._data),
            "data_keys": list(self._data.keys()),
            "test_value": self.config.value,
        }


@pytest.fixture
async def test_module() -> AsyncGenerator[_TestModule, None]:
    """Create test module fixture."""
    module = _TestModule(_TestConfig())
    await module.initialize()
    try:
        yield module
    finally:
        await module.cleanup()
