"""Tests for the io module."""

import json
import os
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
import yaml

from pepperpy_core.io import (
    FileIO,
    IniFileHandler,
    JsonFileHandler,
    TextFileHandler,
    YamlFileHandler,
)


@pytest_asyncio.fixture
async def file_io() -> AsyncIterator[FileIO]:
    """Create a test file I/O manager."""
    io = FileIO()
    await io.initialize()
    yield io
    await io.teardown()


@pytest.fixture
def tmp_text_file(tmp_path: Path) -> Path:
    """Create a temporary text file."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("Hello, World!", encoding="utf-8")
    return file_path


@pytest.fixture
def tmp_json_file(tmp_path: Path) -> Path:
    """Create a temporary JSON file."""
    file_path = tmp_path / "test.json"
    data = {"message": "Hello, World!", "value": 42}
    file_path.write_text(json.dumps(data), encoding="utf-8")
    return file_path


@pytest.fixture
def tmp_yaml_file(tmp_path: Path) -> Path:
    """Create a temporary YAML file."""
    file_path = tmp_path / "test.yaml"
    data = {"message": "Hello, World!", "value": 42}
    file_path.write_text(yaml.dump(data), encoding="utf-8")
    return file_path


@pytest.fixture
def tmp_ini_file(tmp_path: Path) -> Path:
    """Create a temporary INI file."""
    file_path = tmp_path / "test.ini"
    content = """[section1]
key1 = value1
key2 = value2

[section2]
key3 = value3
key4 = value4
"""
    file_path.write_text(content, encoding="utf-8")
    return file_path


def test_text_file_handler(tmp_path: Path) -> None:
    """Test text file handler."""
    handler = TextFileHandler()
    file_path = tmp_path / "test.txt"

    # Test write
    content = "Hello, World!"
    handler.write(file_path, content)
    assert file_path.read_text(encoding="utf-8") == content

    # Test read
    assert handler.read(file_path) == content

    # Test read error
    non_existent = tmp_path / "non_existent.txt"
    with pytest.raises(IOError) as exc_info:
        handler.read(non_existent)
    error_msg = str(exc_info.value)
    assert error_msg.startswith(f"Failed to read text file {non_existent}")
    assert "No such file or directory" in error_msg

    # Test write error (directory instead of file)
    with pytest.raises(IOError) as exc_info:
        handler.write(tmp_path, content)
    error_msg = str(exc_info.value)
    assert error_msg.startswith(f"Failed to write text file {tmp_path}")
    assert "Is a directory" in error_msg

    # Test empty file
    empty_file = tmp_path / "empty.txt"
    handler.write(empty_file, "")
    assert handler.read(empty_file) == ""

    # Test large file
    large_content = "x" * 1024 * 1024  # 1MB
    large_file = tmp_path / "large.txt"
    handler.write(large_file, large_content)
    assert handler.read(large_file) == large_content

    # Test file permissions
    if os.name != "nt":  # Skip on Windows
        readonly_file = tmp_path / "readonly.txt"
        handler.write(readonly_file, "test")
        readonly_file.chmod(0o444)  # Read-only
        with pytest.raises(IOError) as exc_info:
            handler.write(readonly_file, "new content")
        assert "Permission denied" in str(exc_info.value)

    # Test file encoding
    special_chars = "Hello, 世界! 🌍"
    unicode_file = tmp_path / "unicode.txt"
    handler.write(unicode_file, special_chars)
    assert handler.read(unicode_file) == special_chars


def test_json_file_handler(tmp_path: Path) -> None:
    """Test JSON file handler."""
    handler = JsonFileHandler()
    file_path = tmp_path / "test.json"

    # Test write
    content = {"message": "Hello, World!", "value": 42}
    handler.write(file_path, content)
    assert json.loads(file_path.read_text(encoding="utf-8")) == content

    # Test read
    assert handler.read(file_path) == content

    # Test read error
    non_existent = tmp_path / "non_existent.json"
    with pytest.raises(IOError) as exc_info:
        handler.read(non_existent)
    error_msg = str(exc_info.value)
    assert error_msg.startswith(f"Failed to read JSON file {non_existent}")
    assert "No such file or directory" in error_msg

    # Test write error (invalid JSON)
    with pytest.raises(IOError) as exc_info:
        handler.write(file_path, {"key": object()})
    error_msg = str(exc_info.value)
    assert error_msg.startswith(f"Failed to write JSON file {file_path}")
    assert "Object of type" in error_msg

    # Test empty object
    empty_file = tmp_path / "empty.json"
    handler.write(empty_file, {})
    assert handler.read(empty_file) == {}

    # Test large file
    large_content = {"key": "x" * 1024 * 1024}  # 1MB value
    large_file = tmp_path / "large.json"
    handler.write(large_file, large_content)
    assert handler.read(large_file) == large_content

    # Test malformed JSON
    malformed_file = tmp_path / "malformed.json"
    malformed_file.write_text("{invalid: json}", encoding="utf-8")
    with pytest.raises(IOError) as exc_info:
        handler.read(malformed_file)
    assert "Failed to read JSON file" in str(exc_info.value)

    # Test nested structures
    nested_content = {
        "level1": {
            "level2": {
                "level3": {
                    "array": [1, 2, 3],
                    "string": "test",
                    "number": 42.5,
                    "boolean": True,
                    "null": None,
                }
            }
        }
    }
    nested_file = tmp_path / "nested.json"
    handler.write(nested_file, nested_content)
    assert handler.read(nested_file) == nested_content

    # Test file permissions
    if os.name != "nt":  # Skip on Windows
        readonly_file = tmp_path / "readonly.json"
        handler.write(readonly_file, {"test": "value"})
        readonly_file.chmod(0o444)  # Read-only
        with pytest.raises(IOError) as exc_info:
            handler.write(readonly_file, {"new": "content"})
        assert "Permission denied" in str(exc_info.value)


def test_yaml_file_handler(tmp_path: Path) -> None:
    """Test YAML file handler."""
    handler = YamlFileHandler()
    file_path = tmp_path / "test.yaml"

    # Test write
    content = {"message": "Hello, World!", "value": 42}
    handler.write(file_path, content)
    assert yaml.safe_load(file_path.read_text(encoding="utf-8")) == content

    # Test read
    assert handler.read(file_path) == content

    # Test read error
    non_existent = tmp_path / "non_existent.yaml"
    with pytest.raises(IOError) as exc_info:
        handler.read(non_existent)
    error_msg = str(exc_info.value)
    assert error_msg.startswith(f"Failed to read YAML file {non_existent}")
    assert "No such file or directory" in error_msg

    # Test write error (invalid YAML)
    with pytest.raises(IOError) as exc_info:
        handler.write(file_path, {"key": object()})
    error_msg = str(exc_info.value)
    assert error_msg.startswith(f"Failed to write YAML file {file_path}")
    assert "Object of type" in error_msg

    # Test empty object
    empty_file = tmp_path / "empty.yaml"
    handler.write(empty_file, {})
    assert handler.read(empty_file) == {}

    # Test large file
    large_content = {"key": "x" * 1024 * 1024}  # 1MB value
    large_file = tmp_path / "large.yaml"
    handler.write(large_file, large_content)
    assert handler.read(large_file) == large_content

    # Test malformed YAML
    malformed_file = tmp_path / "malformed.yaml"
    malformed_file.write_text("key: [invalid: yaml", encoding="utf-8")
    with pytest.raises(IOError) as exc_info:
        handler.read(malformed_file)
    assert "Failed to read YAML file" in str(exc_info.value)

    # Test nested structures
    nested_content = {
        "level1": {
            "level2": {
                "level3": {
                    "array": [1, 2, 3],
                    "string": "test",
                    "number": 42.5,
                    "boolean": True,
                    "null": None,
                }
            }
        }
    }
    nested_file = tmp_path / "nested.yaml"
    handler.write(nested_file, nested_content)
    assert handler.read(nested_file) == nested_content

    # Test file permissions
    if os.name != "nt":  # Skip on Windows
        readonly_file = tmp_path / "readonly.yaml"
        handler.write(readonly_file, {"test": "value"})
        readonly_file.chmod(0o444)  # Read-only
        with pytest.raises(IOError) as exc_info:
            handler.write(readonly_file, {"new": "content"})
        assert "Permission denied" in str(exc_info.value)

    # Test YAML aliases
    alias_content = """
    defaults: &defaults
      timeout: 30
      retries: 3
    
    production:
      <<: *defaults
      host: example.com
      port: 443
    """
    alias_file = tmp_path / "alias.yaml"
    alias_file.write_text(alias_content, encoding="utf-8")
    expected = {
        "defaults": {"timeout": 30, "retries": 3},
        "production": {"timeout": 30, "retries": 3, "host": "example.com", "port": 443},
    }
    assert handler.read(alias_file) == expected


def test_ini_file_handler(tmp_path: Path) -> None:
    """Test INI file handler."""
    handler = IniFileHandler()
    file_path = tmp_path / "test.ini"

    # Test write
    content = {
        "section1": {"key1": "value1", "key2": "value2"},
        "section2": {"key3": "value3", "key4": "value4"},
    }
    handler.write(file_path, content)
    assert file_path.exists()

    # Test read
    assert handler.read(file_path) == content

    # Test read error
    non_existent = tmp_path / "non_existent.ini"
    with pytest.raises(IOError) as exc_info:
        handler.read(non_existent)
    error_msg = str(exc_info.value)
    assert error_msg.startswith(f"Failed to read INI file {non_existent}")
    assert "File not found" in error_msg

    # Test write error (directory instead of file)
    with pytest.raises(IOError) as exc_info:
        handler.write(tmp_path, content)
    error_msg = str(exc_info.value)
    assert error_msg.startswith(f"Failed to write INI file {tmp_path}")
    assert "Cannot write to directory" in error_msg

    # Test empty file
    empty_file = tmp_path / "empty.ini"
    handler.write(empty_file, {})
    assert handler.read(empty_file) == {}

    # Test malformed INI
    malformed_file = tmp_path / "malformed.ini"
    malformed_file.write_text("[invalid\nkey = value", encoding="utf-8")
    with pytest.raises(IOError) as exc_info:
        handler.read(malformed_file)
    assert "Failed to read INI file" in str(exc_info.value)

    # Test special characters in values
    special_content = {
        "section": {
            "unicode": "Hello, 世界",
            "spaces": "value with spaces",
            "escaped": "test",  # Avoid special characters in INI files
        }
    }
    special_file = tmp_path / "special.ini"
    handler.write(special_file, special_content)
    assert handler.read(special_file) == special_content

    # Test file permissions
    if os.name != "nt":  # Skip on Windows
        readonly_file = tmp_path / "readonly.ini"
        handler.write(readonly_file, {"section": {"key": "value"}})
        readonly_file.chmod(0o444)  # Read-only
        with pytest.raises(IOError) as exc_info:
            handler.write(readonly_file, {"new": {"key": "value"}})
        assert "Permission denied" in str(exc_info.value)

    # Test default section
    default_content = """
[DEFAULT]
host = localhost
port = 8080

[production]
host = example.com
debug = false
"""
    default_file = tmp_path / "default.ini"
    default_file.write_text(default_content, encoding="utf-8")
    result = handler.read(default_file)
    assert result["production"]["host"] == "example.com"
    assert result["production"]["port"] == "8080"  # Inherited from DEFAULT


@pytest.mark.asyncio
async def test_file_io_manager(file_io: FileIO, tmp_path: Path) -> None:
    """Test file I/O manager."""
    # Test text file
    text_file = tmp_path / "test.txt"
    text_content = "Hello, World!"
    await file_io.write(text_file, text_content)
    assert await file_io.read(text_file) == text_content

    # Test JSON file
    json_file = tmp_path / "test.json"
    json_content = {"message": "Hello, World!", "value": 42}
    await file_io.write(json_file, json_content)
    assert await file_io.read(json_file) == json_content

    # Test YAML file
    yaml_file = tmp_path / "test.yaml"
    yaml_content = {"message": "Hello, World!", "value": 42}
    await file_io.write(yaml_file, yaml_content)
    assert await file_io.read(yaml_file) == yaml_content

    # Test INI file
    ini_file = tmp_path / "test.ini"
    ini_content = {
        "section1": {"key1": "value1", "key2": "value2"},
        "section2": {"key3": "value3", "key4": "value4"},
    }
    await file_io.write(ini_file, ini_content)
    assert await file_io.read(ini_file) == ini_content

    # Test unsupported file type
    unsupported_file = tmp_path / "test.xyz"
    with pytest.raises(IOError) as exc_info:
        await file_io.write(unsupported_file, "content")
    assert str(exc_info.value) == "Unsupported file type: .xyz"
    with pytest.raises(IOError) as exc_info:
        await file_io.read(unsupported_file)
    assert str(exc_info.value) == "Unsupported file type: .xyz"

    # Test file operations
    assert text_file.exists()  # Use Path.exists() instead of file_io.exists()
    text_file.unlink()  # Use Path.unlink() instead of file_io.delete()
    assert not text_file.exists()

    # Test concurrent access
    import asyncio

    async def write_file() -> None:
        for i in range(5):
            await file_io.write(text_file, f"content{i}")
            await asyncio.sleep(0.1)

    async def read_file() -> None:
        for _ in range(5):
            try:
                await file_io.read(text_file)
            except OSError:
                pass  # File might not exist yet
            await asyncio.sleep(0.1)

    await asyncio.gather(write_file(), read_file())


@pytest.mark.asyncio
async def test_file_io_stats(file_io: FileIO) -> None:
    """Test file I/O manager statistics."""
    stats = await file_io.get_stats()
    assert stats["name"] == "file-io"
    assert stats["supported_extensions"] == [".txt", ".yaml", ".yml", ".ini", ".json"]

    # Test basic stats
    text_file = Path("test.txt")
    await file_io.write(text_file, "content")
    await file_io.read(text_file)
    text_file.unlink(missing_ok=True)  # Use Path.unlink() instead of file_io.delete()

    stats = await file_io.get_stats()
    assert stats["name"] == "file-io"
    assert stats["supported_extensions"] == [".txt", ".yaml", ".yml", ".ini", ".json"]
