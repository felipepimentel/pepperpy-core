"""Tests for the io module."""

import json
from collections.abc import AsyncIterator
from os import PathLike
from pathlib import Path
from unittest.mock import MagicMock, patch

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


class MockPath(PathLike):
    """Mock Path object."""

    def __init__(self, suffix: str = ".txt") -> None:
        """Initialize mock path.

        Args:
            suffix: File suffix
        """
        self.exists = MagicMock(return_value=True)
        self.is_dir = MagicMock(return_value=False)
        self.read_text = MagicMock()
        self.write_text = MagicMock()
        self.resolve = MagicMock(return_value=self)
        self._suffix = suffix
        self._str = f"test{suffix}"

    def __str__(self) -> str:
        """Return string representation."""
        return self._str

    def __fspath__(self) -> str:
        """Return file system path representation."""
        return self._str

    @property
    def suffix(self) -> str:
        """Get file suffix."""
        return self._suffix

    @suffix.setter
    def suffix(self, value: str) -> None:
        """Set file suffix."""
        self._suffix = value
        self._str = f"test{value}"


@pytest_asyncio.fixture
async def file_io() -> AsyncIterator[FileIO]:
    """Create a test file I/O manager."""
    io = FileIO()
    await io.initialize()
    yield io
    await io.teardown()


def test_text_file_handler() -> None:
    """Test text file handler."""
    handler = TextFileHandler()
    path = MagicMock(spec=Path)
    path.exists.return_value = True
    path.is_dir.return_value = False

    # Test read
    content = "Hello, World!"
    path.read_text.return_value = content
    assert handler.read(path) == content

    # Test write
    handler.write(path, content)
    path.write_text.assert_called_once_with(content, encoding="utf-8")

    # Test read error (file not found)
    path.exists.return_value = False
    with pytest.raises(IOError) as exc_info:
        handler.read(path)
    error_msg = str(exc_info.value)
    assert error_msg.startswith(f"Failed to read text file {path}")
    assert "No such file or directory" in error_msg

    # Test write error (directory)
    path.is_dir.return_value = True
    with pytest.raises(IOError) as exc_info:
        handler.write(path, content)
    error_msg = str(exc_info.value)
    assert error_msg.startswith(f"Failed to write text file {path}")
    assert "Is a directory" in error_msg


def test_json_file_handler() -> None:
    """Test JSON file handler."""
    handler = JsonFileHandler()
    path = MagicMock(spec=Path)
    path.exists.return_value = True
    path.is_dir.return_value = False

    # Test write
    content = {"message": "Hello, World!", "value": 42}
    handler.write(path, content)
    path.write_text.assert_called_once_with(json.dumps(content), encoding="utf-8")

    # Test read
    path.read_text.return_value = json.dumps(content)
    assert handler.read(path) == content

    # Test read error (file not found)
    path.exists.return_value = False
    with pytest.raises(IOError) as exc_info:
        handler.read(path)
    error_msg = str(exc_info.value)
    assert error_msg.startswith(f"Failed to read JSON file {path}")
    assert "No such file or directory" in error_msg

    # Test write error (directory)
    path.is_dir.return_value = True
    with pytest.raises(IOError) as exc_info:
        handler.write(path, content)
    error_msg = str(exc_info.value)
    assert error_msg.startswith(f"Failed to write JSON file {path}")
    assert "Is a directory" in error_msg

    # Test read error (invalid JSON)
    path.exists.return_value = True
    path.is_dir.return_value = False
    path.read_text.return_value = "invalid json"
    with pytest.raises(IOError) as exc_info:
        handler.read(path)
    assert "Failed to read JSON file" in str(exc_info.value)


def test_yaml_file_handler() -> None:
    """Test YAML file handler."""
    handler = YamlFileHandler()
    path = MagicMock(spec=Path)
    path.exists.return_value = True
    path.is_dir.return_value = False
    path.__str__.return_value = "test.yaml"

    # Test write
    content = {"message": "Hello, World!", "value": 42}
    handler.write(path, content)
    path.write_text.assert_called_once_with(yaml.dump(content), encoding="utf-8")

    # Test read
    path.read_text.return_value = yaml.dump(content)
    assert handler.read(path) == content

    # Test read error (file not found)
    path.exists.return_value = False
    with pytest.raises(OSError) as exc_info:
        handler.read(path)
    error_msg = str(exc_info.value)
    assert error_msg.startswith(f"Failed to read YAML file {path}")
    assert "No such file or directory" in error_msg

    # Test write error (directory)
    path.is_dir.return_value = True
    with pytest.raises(OSError) as exc_info:
        handler.write(path, content)
    error_msg = str(exc_info.value)
    assert error_msg.startswith(f"Failed to write YAML file {path}")
    assert "Is a directory" in error_msg

    # Test read error (invalid YAML)
    path.exists.return_value = True
    path.is_dir.return_value = False
    path.read_text.return_value = "key: [invalid: yaml"
    with pytest.raises(OSError) as exc_info:
        handler.read(path)
    assert "Failed to read YAML file" in str(exc_info.value)

    # Test write error (invalid YAML)
    path.exists.return_value = True
    path.is_dir.return_value = False
    path.read_text.side_effect = None

    # Mock yaml.dump to raise an error
    with patch("yaml.dump") as mock_dump:
        mock_dump.side_effect = yaml.YAMLError("Failed to serialize")
        with pytest.raises(OSError) as exc_info:
            handler.write(path, content)
        error_msg = str(exc_info.value)
        assert error_msg.startswith(f"Failed to write YAML file {path}")


def test_ini_file_handler() -> None:
    """Test INI file handler."""
    handler = IniFileHandler()
    path = MagicMock(spec=Path)
    path.exists.return_value = True
    path.is_dir.return_value = False
    path.__str__.return_value = "test.ini"

    # Test write
    content = {"section1": {"key1": "value1", "key2": "value2"}}
    handler.write(path, content)

    # Test read
    path.read_text.return_value = """[section1]
key1 = value1
key2 = value2
"""
    assert handler.read(path) == content

    # Test read error (file not found)
    path.exists.return_value = False
    with pytest.raises(IOError) as exc_info:
        handler.read(path)
    error_msg = str(exc_info.value)
    assert error_msg.startswith(f"Failed to read INI file {path}")
    assert "File not found" in error_msg

    # Test write error (directory)
    path.is_dir.return_value = True
    with pytest.raises(IOError) as exc_info:
        handler.write(path, content)
    error_msg = str(exc_info.value)
    assert error_msg.startswith(f"Failed to write INI file {path}")
    assert "Cannot write to directory" in error_msg


@pytest.mark.asyncio
async def test_file_io_manager(file_io: FileIO) -> None:
    """Test file I/O manager."""
    # Create a mock path with a proper suffix
    path = MockPath(".txt")
    path.read_text.return_value = "Hello, World!"

    # Test read
    content = "Hello, World!"
    assert await file_io.read(path) == content

    # Test write
    await file_io.write(path, content)
    path.write_text.assert_called_once_with(content, encoding="utf-8")

    # Test unsupported file type
    path = MockPath(".unsupported")
    with pytest.raises(OSError) as exc_info:
        await file_io.read(path)
    assert "Unsupported file type: .unsupported" in str(exc_info.value)

    # Test write to unsupported file type
    with pytest.raises(OSError) as exc_info:
        await file_io.write(path, content)
    assert "Unsupported file type: .unsupported" in str(exc_info.value)


@pytest.mark.asyncio
async def test_file_io_stats(file_io: FileIO) -> None:
    """Test file I/O statistics."""
    stats = await file_io.get_stats()
    assert stats["name"] == "file-io"
    assert sorted(stats["supported_extensions"]) == sorted(
        [
            ".txt",
            ".yaml",
            ".yml",
            ".ini",
            ".json",
        ]
    )
