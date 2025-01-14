"""Test config module."""

import pytest

from pepperpy.config import Config, ConfigError, ConfigItem, ConfigSection


def test_config_item_init() -> None:
    """Test config item initialization."""
    item = ConfigItem(name="test", value="value")
    assert item.name == "test"
    assert item.value == "value"
    assert item.metadata == {}


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
    assert section.items == {}
    assert section.metadata == {}


def test_config_section_init_with_metadata() -> None:
    """Test config section initialization with metadata."""
    section = ConfigSection(name="test", metadata={"key": "value"})
    assert section.name == "test"
    assert section.items == {}
    assert section.metadata == {"key": "value"}


def test_config_section_init_with_invalid_name() -> None:
    """Test config section initialization with invalid name."""
    with pytest.raises(ValueError):
        ConfigSection(name="")


def test_config_init() -> None:
    """Test config initialization."""
    config = Config(name="test")
    assert config.name == "test"
    assert config.sections == {}
    assert config.metadata == {}


def test_config_init_with_metadata() -> None:
    """Test config initialization with metadata."""
    config = Config(name="test", metadata={"key": "value"})
    assert config.name == "test"
    assert config.sections == {}
    assert config.metadata == {"key": "value"}


def test_config_init_with_invalid_name() -> None:
    """Test config initialization with invalid name."""
    with pytest.raises(ValueError):
        Config(name="")


def test_config_get_section() -> None:
    """Test get section."""
    config = Config(name="test")
    section = ConfigSection(name="section")
    config.sections["section"] = section
    assert config.get_section("section") == section


def test_config_get_section_not_found() -> None:
    """Test get section not found."""
    config = Config(name="test")
    with pytest.raises(ConfigError):
        config.get_section("section")


def test_config_get_item() -> None:
    """Test get item."""
    config = Config(name="test")
    section = ConfigSection(name="section")
    item = ConfigItem(name="item", value="value")
    section.items["item"] = item
    config.sections["section"] = section
    assert config.get_item("section", "item") == item


def test_config_get_item_not_found() -> None:
    """Test get item not found."""
    config = Config(name="test")
    section = ConfigSection(name="section")
    config.sections["section"] = section
    with pytest.raises(ConfigError):
        config.get_item("section", "item")


def test_config_get_value() -> None:
    """Test get value."""
    config = Config(name="test")
    section = ConfigSection(name="section")
    item = ConfigItem(name="item", value="value")
    section.items["item"] = item
    config.sections["section"] = section
    assert config.get_value("section", "item") == "value"


def test_config_get_value_not_found() -> None:
    """Test get value not found."""
    config = Config(name="test")
    section = ConfigSection(name="section")
    config.sections["section"] = section
    with pytest.raises(ConfigError):
        config.get_value("section", "item")


def test_config_set_value() -> None:
    """Test set value."""
    config = Config(name="test")
    section = ConfigSection(name="section")
    config.sections["section"] = section
    config.set_value("section", "item", "value")
    assert config.get_value("section", "item") == "value"


def test_config_set_value_section_not_found() -> None:
    """Test set value section not found."""
    config = Config(name="test")
    with pytest.raises(ConfigError):
        config.set_value("section", "item", "value")


def test_config_add_section() -> None:
    """Test add section."""
    config = Config(name="test")
    config.add_section("section")
    assert "section" in config.sections


def test_config_remove_section() -> None:
    """Test remove section."""
    config = Config(name="test")
    config.add_section("section")
    config.remove_section("section")
    assert "section" not in config.sections


def test_config_remove_section_not_found() -> None:
    """Test remove section not found."""
    config = Config(name="test")
    with pytest.raises(ConfigError):
        config.remove_section("section")


def test_config_clear() -> None:
    """Test clear."""
    config = Config(name="test")
    config.add_section("section")
    config.metadata["key"] = "value"
    config.clear()
    assert config.sections == {}
    assert config.metadata == {}


def test_config_get_stats() -> None:
    """Test get stats."""
    config = Config(name="test")
    section = ConfigSection(name="section")
    item = ConfigItem(name="item", value="value")
    section.items["item"] = item
    config.sections["section"] = section
    stats = config.get_stats()
    assert stats["name"] == "test"
    assert stats["sections"] == 1
    assert stats["items"] == 1
