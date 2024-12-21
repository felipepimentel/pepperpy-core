"""Configuration tests."""

import json
from pathlib import Path
from typing import Any, AsyncIterator

import pytest
import pytest_asyncio

from pepperpy_core.config import (
    Config,
    JsonConfigLoader,
)
from pepperpy_core.exceptions import ConfigError


class _TestConfig(Config):
    """Test configuration."""

    def __init__(self) -> None:
        """Initialize test configuration."""
        super().__init__(name="test", enabled=True, metadata={})

    def get(self, key: str) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key

        Returns:
            Configuration value
        """
        return self._values[key].value

    async def cleanup(self) -> None:
        """Cleanup configuration."""
        self._values.clear()


@pytest_asyncio.fixture
async def config() -> AsyncIterator[_TestConfig]:
    """Test configuration fixture."""
    config_instance = _TestConfig()
    yield config_instance
    await config_instance.cleanup()


@pytest.mark.asyncio
async def test_config_load(config: _TestConfig, tmp_path: Path) -> None:
    """Test config loading."""
    loader = JsonConfigLoader()

    # Create a test config file
    config_path = tmp_path / "test_config.json"
    with config_path.open("w", encoding="utf-8") as f:
        json.dump({"test_key": "test_value"}, f)

    await config.load(loader, config_path)
    assert config.get("test_key") == "test_value"


@pytest.mark.asyncio
async def test_config_validation(config: _TestConfig, tmp_path: Path) -> None:
    """Test config validation."""
    loader = JsonConfigLoader()

    # Ensure the config file doesn't exist
    config_path = tmp_path / "invalid_config.json"
    if config_path.exists():
        config_path.unlink()

    with pytest.raises(
        ConfigError, match="Failed to load configuration: Failed to load config file"
    ):
        await config.load(loader, config_path)
