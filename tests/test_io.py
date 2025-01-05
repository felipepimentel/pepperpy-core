"""Test io module."""

from pathlib import Path
from typing import Any

import pytest

from pepperpy_core.io import FileReader, FileWriter


@pytest.fixture
def test_file_reader() -> "TestFileReader":
    """Create a test file reader."""
    return TestFileReader()


class TestFileReader(FileReader):
    """Test file reader implementation."""

    def __init__(self) -> None:
        """Initialize test file reader."""
        self.data: dict[str, Any] = {}

    async def read(self, path: Path) -> Any:
        """Read data from path."""
        return self.data.get(str(path))


@pytest.fixture
def test_file_writer() -> "TestFileWriter":
    """Create a test file writer."""
    return TestFileWriter()


class TestFileWriter(FileWriter):
    """Test file writer implementation."""

    def __init__(self) -> None:
        """Initialize test file writer."""
        self.data: dict[str, Any] = {}

    async def write(self, path: Path, data: Any) -> None:
        """Write data to path."""
        self.data[str(path)] = data


@pytest.mark.asyncio
async def test_file_reader_read(test_file_reader: TestFileReader) -> None:
    """Test file reader read."""
    test_file_reader.data["test"] = "test"
    assert await test_file_reader.read(Path("test")) == "test"


@pytest.mark.asyncio
async def test_file_reader_read_missing(test_file_reader: TestFileReader) -> None:
    """Test file reader read missing."""
    assert await test_file_reader.read(Path("test")) is None


@pytest.mark.asyncio
async def test_file_writer_write(test_file_writer: TestFileWriter) -> None:
    """Test file writer write."""
    await test_file_writer.write(Path("test"), "test")
    assert test_file_writer.data["test"] == "test"
