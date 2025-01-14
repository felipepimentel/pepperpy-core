"""IO module."""

import json
from pathlib import Path
from typing import Optional, Protocol, runtime_checkable

import aiofiles

from .core import PepperpyError


class IOError(PepperpyError):
    """IO-related errors."""

    def __init__(
        self,
        message: str,
        cause: Optional[Exception] = None,
        file_path: Optional[str] = None,
    ) -> None:
        """Initialize IO error.

        Args:
            message: Error message
            cause: Optional cause of the error
            file_path: Optional path of the file that caused the error
        """
        super().__init__(message, cause)
        self.file_path = file_path


@runtime_checkable
class FileReader(Protocol):
    """File reader protocol."""

    async def read(self, path: Path) -> str:
        """Read file.

        Args:
            path: File path

        Returns:
            File contents
        """
        ...


@runtime_checkable
class FileWriter(Protocol):
    """File writer protocol."""

    async def write(self, path: Path, content: str) -> None:
        """Write file.

        Args:
            path: File path
            content: File contents
        """
        ...


class TextFileReader(FileReader):
    """Text file reader implementation."""

    async def read(self, path: Path) -> str:
        """Read text file.

        Args:
            path: File path

        Returns:
            File contents
        """
        async with aiofiles.open(path, mode="r") as f:
            return await f.read()


class TextFileWriter(FileWriter):
    """Text file writer implementation."""

    async def write(self, path: Path, content: str) -> None:
        """Write text file.

        Args:
            path: File path
            content: File contents
        """
        async with aiofiles.open(path, mode="w") as f:
            await f.write(content)


class JsonFileReader(FileReader):
    """JSON file reader implementation."""

    async def read(self, path: Path) -> str:
        """Read JSON file.

        Args:
            path: File path

        Returns:
            File contents as JSON string
        """
        async with aiofiles.open(path, mode="r") as f:
            content = await f.read()
            return json.dumps(json.loads(content))


class JsonFileWriter(FileWriter):
    """JSON file writer implementation."""

    async def write(self, path: Path, content: str) -> None:
        """Write JSON file.

        Args:
            path: File path
            content: File contents as JSON string
        """
        async with aiofiles.open(path, mode="w") as f:
            await f.write(json.dumps(json.loads(content), indent=2))


__all__ = [
    "FileReader",
    "FileWriter",
    "TextFileReader",
    "TextFileWriter",
    "JsonFileReader",
    "JsonFileWriter",
]
