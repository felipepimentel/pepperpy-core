"""IO module for reading and writing files."""

import json
from pathlib import Path
from typing import Protocol

import aiofiles


class IOError(Exception):
    """IO error."""


class FileReader(Protocol):
    """File reader protocol."""

    async def read(self, path: Path) -> str:
        """Read file.

        Args:
            path: Path to file.

        Returns:
            File content.

        Raises:
            IOError: If file cannot be read.
        """
        ...


class FileWriter(Protocol):
    """File writer protocol."""

    async def write(self, path: Path, content: str) -> None:
        """Write file.

        Args:
            path: Path to file.
            content: File content.

        Raises:
            IOError: If file cannot be written.
        """
        ...


class TextFileReader:
    """Text file reader."""

    async def read(self, path: Path) -> str:
        """Read text file.

        Args:
            path: Path to file.

        Returns:
            File content.

        Raises:
            IOError: If file cannot be read.
        """
        try:
            async with aiofiles.open(path, mode="r") as f:
                return await f.read()
        except (FileNotFoundError, PermissionError) as e:
            raise IOError(f"Failed to read file {path}: {e}") from e


class TextFileWriter:
    """Text file writer."""

    async def write(self, path: Path, content: str) -> None:
        """Write text file.

        Args:
            path: Path to file.
            content: File content.

        Raises:
            IOError: If file cannot be written.
        """
        try:
            async with aiofiles.open(path, mode="w") as f:
                await f.write(content)
        except (FileNotFoundError, PermissionError) as e:
            raise IOError(f"Failed to write file {path}: {e}") from e


class JsonFileReader:
    """JSON file reader."""

    async def read(self, path: Path) -> str:
        """Read JSON file.

        Args:
            path: Path to file.

        Returns:
            File content.

        Raises:
            IOError: If file cannot be read or is not valid JSON.
        """
        try:
            async with aiofiles.open(path, mode="r") as f:
                content = await f.read()
                return json.dumps(json.loads(content))
        except (FileNotFoundError, PermissionError) as e:
            raise IOError(f"Failed to read file {path}: {e}") from e
        except json.JSONDecodeError as e:
            raise IOError(f"Failed to parse JSON file {path}: {e}") from e


class JsonFileWriter:
    """JSON file writer."""

    async def write(self, path: Path, content: str) -> None:
        """Write JSON file.

        Args:
            path: Path to file.
            content: File content.

        Raises:
            IOError: If file cannot be written or content is not valid JSON.
        """
        try:
            async with aiofiles.open(path, mode="w") as f:
                await f.write(json.dumps(json.loads(content), indent=2))
        except (FileNotFoundError, PermissionError) as e:
            raise IOError(f"Failed to write file {path}: {e}") from e
        except json.JSONDecodeError as e:
            raise IOError(f"Failed to parse JSON content: {e}") from e


__all__ = [
    "IOError",
    "FileReader",
    "FileWriter",
    "TextFileReader",
    "TextFileWriter",
    "JsonFileReader",
    "JsonFileWriter",
]
