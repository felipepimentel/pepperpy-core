"""Configuration tests."""

import json
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest
from pepperpy_core.config import ConfigManager
from pepperpy_core.config.types import ConfigManagerConfig
from pydantic import BaseModel


class _TestConfig(BaseModel):
    """Test configuration model."""

    name: str = "test"
    value: str = "test_value"


@pytest.fixture
def test_config_dir() -> str:
    """Create and return a test config directory."""
    config_dir = "/tmp/test_config"
    Path(config_dir).mkdir(exist_ok=True)
    return config_dir


@pytest.fixture
def manager_config(test_config_dir: str) -> ConfigManagerConfig:
    """Create test configuration."""
    return ConfigManagerConfig(
        name="test_manager",
        config_path=test_config_dir,
        enabled=True,
    )


@pytest.fixture
async def config_manager(
    manager_config: ConfigManagerConfig,
) -> AsyncGenerator[ConfigManager, None]:
    """Create config manager fixture."""
    manager = ConfigManager(config=manager_config)
    await manager.initialize()
    try:
        yield manager
    finally:
        await manager.cleanup()


@pytest.fixture
def test_config_file(test_config_dir: str) -> Path:
    """Create a test config file."""
    config_path = Path(test_config_dir) / "test_config.json"
    config_data = {"name": "test", "value": "test_value"}
    config_path.write_text(json.dumps(config_data))
    return config_path


@pytest.mark.asyncio
async def test_config_get(
    config_manager: AsyncGenerator[ConfigManager, None],
    test_config_file: Path,
) -> None:
    """Test config loading."""
    manager = await anext(config_manager)
    config = await manager.get_config("test_config", _TestConfig)
    assert config is not None
    assert isinstance(config, _TestConfig)
    assert config.name == "test"
    assert config.value == "test_value"


@pytest.mark.asyncio
async def test_config_validation(
    config_manager: AsyncGenerator[ConfigManager, None],
    test_config_dir: str,
) -> None:
    """Test config validation."""
    manager = await anext(config_manager)

    # Ensure the config file doesn't exist
    config_path = Path(test_config_dir) / "invalid_config.json"
    if config_path.exists():
        config_path.unlink()

    with pytest.raises(ValueError, match="Config file not found: invalid_config"):
        await manager.get_config("invalid_config", _TestConfig)


@pytest.fixture(autouse=True)
def cleanup_test_files(test_config_dir: str) -> Generator[None, None, None]:
    """Clean up test files after each test."""
    yield
    import shutil

    shutil.rmtree(test_config_dir, ignore_errors=True)
