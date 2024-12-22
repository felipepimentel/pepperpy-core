"""Tests for the config module."""

import pytest

from pepperpy_core.config import Config, ConfigError, ConfigItem, ConfigSection


@pytest.fixture
def config() -> Config:
    """Create a test configuration."""
    return Config(name="test")


@pytest.mark.asyncio
async def test_config_sections(config: Config) -> None:
    """Test configuration sections."""
    # Add section
    config.add_section("section1", {"meta": "data"})
    assert "section1" in config.sections
    assert config.sections["section1"].metadata == {"meta": "data"}

    # Get section
    section = config.get_section("section1")
    assert section.name == "section1"
    assert section.metadata == {"meta": "data"}

    # Remove section
    config.remove_section("section1")
    assert "section1" not in config.sections

    # Get non-existent section
    with pytest.raises(ConfigError):
        config.get_section("missing")

    # Remove non-existent section
    with pytest.raises(ConfigError):
        config.remove_section("missing")


@pytest.mark.asyncio
async def test_config_items(config: Config) -> None:
    """Test configuration items."""
    config.add_section("section1")

    # Set value
    config.set_value("section1", "item1", "value1")
    assert "item1" in config.sections["section1"].items

    # Get value
    value = config.get_value("section1", "item1")
    assert value == "value1"

    # Get item
    item = config.get_item("section1", "item1")
    assert item.name == "item1"
    assert item.value == "value1"

    # Get non-existent item
    with pytest.raises(ConfigError):
        config.get_item("section1", "missing")

    # Get value from non-existent section
    with pytest.raises(ConfigError):
        config.get_value("missing", "item1")


@pytest.mark.asyncio
async def test_config_validation() -> None:
    """Test configuration validation."""
    # Empty name
    with pytest.raises(ValueError):
        Config(name="")

    # Empty section name
    with pytest.raises(ValueError):
        ConfigSection(name="")

    # Empty item name
    with pytest.raises(ValueError):
        ConfigItem(name="", value="test")

    # Valid config
    config = Config(name="test")
    config.validate()  # Should not raise


@pytest.mark.asyncio
async def test_config_clear(config: Config) -> None:
    """Test configuration clear."""
    config.add_section("section1")
    config.set_value("section1", "item1", "value1")
    config.metadata["key"] = "value"

    config.clear()
    assert not config.sections
    assert not config.metadata


@pytest.mark.asyncio
async def test_config_stats(config: Config) -> None:
    """Test configuration statistics."""
    # Initial stats
    stats = config.get_stats()
    assert stats["name"] == "test"
    assert stats["sections"] == 0
    assert stats["items"] == 0

    # Add some data
    config.add_section("section1")
    config.set_value("section1", "item1", "value1")
    config.set_value("section1", "item2", "value2")

    config.add_section("section2")
    config.set_value("section2", "item3", "value3")

    # Check updated stats
    stats = config.get_stats()
    assert stats["name"] == "test"
    assert stats["sections"] == 2
    assert stats["items"] == 3
