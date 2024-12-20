"""Configuration tests."""

from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from pepperpy_core.config import Config, JsonConfigLoader


class _TestConfig(Config):
    """Test configuration."""

    def __init__(self, name: str = "test") -> None:
        """Initialize configuration."""
        super().__init__(name=name)


@pytest.fixture
async def config() -> AsyncGenerator[_TestConfig, None]:
    """Create test configuration."""
    config = _TestConfig()
    try:
        yield config
    finally:
        await config.cleanup()


@pytest.fixture
def test_config_file(tmp_path: Path) -> Path:
    """Create a test config file."""
    config_path = tmp_path / "test_config.json"
    config_path.write_text('{"name": "test", "value": "test_value"}')
    return config_path


@pytest.mark.asyncio
async def test_config_load(
    config: AsyncGenerator[_TestConfig, None],
    test_config_file: Path,
) -> None:
    """Test config loading."""
    config_instance = await anext(config)
    loader = JsonConfigLoader()
    await config_instance.load(loader, test_config_file)
    assert config_instance.name == "test"


@pytest.mark.asyncio
async def test_config_validation(
    config: AsyncGenerator[_TestConfig, None],
    tmp_path: Path,
) -> None:
    """Test config validation."""
    config_instance = await anext(config)
    loader = JsonConfigLoader()

    # Ensure the config file doesn't exist
    config_path = tmp_path / "invalid_config.json"
    if config_path.exists():
        config_path.unlink()

    with pytest.raises(ValueError, match="Config file not found: invalid_config"):
        await config_instance.load(loader, config_path)
