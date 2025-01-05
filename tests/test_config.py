"""Test config module."""

import pytest

from pepperpy_core.config import Config, ConfigItem, ConfigSection
from pepperpy_core.exceptions import ConfigError


def test_config_item_init() -> None:
    """Test config item initialization."""
    item = ConfigItem(name="test", value="value")
    assert item.name == "test"
    assert item.value == "value"
    assert isinstance(item.metadata, dict)
    assert len(item.metadata) == 0


def test_config_item_init_with_metadata() -> None:
    """Test config item initialization with metadata."""
    item = ConfigItem(name="test", value="value", metadata={"key": "value"})
    assert item.name == "test"
    assert item.value == "value"
    assert item.metadata == {"key": "value"}


def test_config_item_init_with_invalid_name() -> None:
    """Test config item initialization with invalid name."""
    with pytest.raises(ValueError):
        ConfigItem(name="", value="value")


def test_config_section_init() -> None:
    """Test config section initialization."""
    section = ConfigSection(name="test")
    assert section.name == "test"
    assert isinstance(section.items, dict)
    assert len(section.items) == 0
    assert isinstance(section.metadata, dict)
    assert len(section.metadata) == 0


def test_config_section_init_with_metadata() -> None:
    """Test config section initialization with metadata."""
    section = ConfigSection(name="test", metadata={"key": "value"})
    assert section.name == "test"
    assert section.metadata == {"key": "value"}


def test_config_section_init_with_invalid_name() -> None:
    """Test config section initialization with invalid name."""
    with pytest.raises(ValueError):
        ConfigSection(name="")


def test_config_init() -> None:
    """Test config initialization."""
    config = Config(name="test")
    assert config.name == "test"
    assert isinstance(config.sections, dict)
    assert len(config.sections) == 0
    assert isinstance(config.metadata, dict)
    assert len(config.metadata) == 0


def test_config_init_with_metadata() -> None:
    """Test config initialization with metadata."""
    config = Config(name="test", metadata={"key": "value"})
    assert config.name == "test"
    assert config.metadata == {"key": "value"}


def test_config_init_with_invalid_name() -> None:
    """Test config initialization with invalid name."""
    with pytest.raises(ValueError):
        Config(name="")


def test_config_get_section() -> None:
    """Test config get section."""
    config = Config(name="test")
    config.add_section("section")
    section = config.get_section("section")
    assert section.name == "section"


def test_config_get_section_not_found() -> None:
    """Test config get section not found."""
    config = Config(name="test")
    with pytest.raises(ConfigError):
        config.get_section("section")


def test_config_get_item() -> None:
    """Test config get item."""
    config = Config(name="test")
    config.add_section("section")
    config.set_value("section", "item", "value")
    item = config.get_item("section", "item")
    assert item.name == "item"
    assert item.value == "value"


def test_config_get_item_not_found() -> None:
    """Test config get item not found."""
    config = Config(name="test")
    config.add_section("section")
    with pytest.raises(ConfigError):
        config.get_item("section", "item")


def test_config_get_value() -> None:
    """Test config get value."""
    config = Config(name="test")
    config.add_section("section")
    config.set_value("section", "item", "value")
    value = config.get_value("section", "item")
    assert value == "value"


def test_config_get_value_not_found() -> None:
    """Test config get value not found."""
    config = Config(name="test")
    config.add_section("section")
    with pytest.raises(ConfigError):
        config.get_value("section", "item")


def test_config_set_value() -> None:
    """Test config set value."""
    config = Config(name="test")
    config.add_section("section")
    config.set_value("section", "item", "value")
    assert config.get_value("section", "item") == "value"


def test_config_set_value_section_not_found() -> None:
    """Test config set value section not found."""
    config = Config(name="test")
    with pytest.raises(ConfigError):
        config.set_value("section", "item", "value")


def test_config_add_section() -> None:
    """Test config add section."""
    config = Config(name="test")
    config.add_section("section")
    assert "section" in config.sections


def test_config_remove_section() -> None:
    """Test config remove section."""
    config = Config(name="test")
    config.add_section("section")
    config.remove_section("section")
    assert "section" not in config.sections


def test_config_remove_section_not_found() -> None:
    """Test config remove section not found."""
    config = Config(name="test")
    with pytest.raises(ConfigError):
        config.remove_section("section")


def test_config_clear() -> None:
    """Test config clear."""
    config = Config(name="test")
    config.add_section("section")
    config.set_value("section", "item", "value")
    config.clear()
    assert len(config.sections) == 0
    assert len(config.metadata) == 0


def test_config_get_stats() -> None:
    """Test config get stats."""
    config = Config(name="test")
    config.add_section("section1")
    config.set_value("section1", "item1", "value1")
    config.set_value("section1", "item2", "value2")
    config.add_section("section2")
    config.set_value("section2", "item3", "value3")
    stats = config.get_stats()
    assert stats["name"] == "test"
    assert stats["sections"] == 2
    assert stats["items"] == 3
