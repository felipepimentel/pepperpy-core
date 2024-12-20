"""File I/O operations module."""

import configparser
from pathlib import Path
from typing import Any, Protocol

from .exceptions import PepperpyError
from .module import BaseModule, ModuleConfig


class IOError(PepperpyError):
    """I/O specific error."""

    pass


class FileReader(Protocol):
    """File reader protocol."""

    def read(self, path: Path) -> Any:
        """Read file content.

        Args:
            path: File path

        Returns:
            File content

        Raises:
            IOError: If reading fails
        """
        ...


class FileWriter(Protocol):
    """File writer protocol."""

    def write(self, path: Path, content: Any) -> None:
        """Write content to file.

        Args:
            path: File path
            content: Content to write

        Raises:
            IOError: If writing fails
        """
        ...


class TextFileHandler:
    """Text file handler implementation."""

    @staticmethod
    def read(path: Path) -> str:
        """Read text file.

        Args:
            path: File path

        Returns:
            File content as string

        Raises:
            IOError: If reading fails
        """
        try:
            return path.read_text(encoding="utf-8")
        except Exception as e:
            raise IOError(f"Failed to read text file {path}: {e}") from e

    @staticmethod
    def write(path: Path, content: str) -> None:
        """Write text to file.

        Args:
            path: File path
            content: Text content

        Raises:
            IOError: If writing fails
        """
        try:
            path.write_text(content, encoding="utf-8")
        except Exception as e:
            raise IOError(f"Failed to write text file {path}: {e}") from e


class YamlFileHandler:
    """YAML file handler implementation."""

    @staticmethod
    def read(path: Path) -> dict[str, Any]:
        """Read YAML file.

        Args:
            path: File path

        Returns:
            File content as dictionary

        Raises:
            IOError: If reading fails
        """
        try:
            try:
                import yaml
            except ImportError:
                raise IOError("PyYAML package is not installed. Please install it with: pip install pyyaml")

            with path.open("r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise IOError(f"Failed to read YAML file {path}: {e}") from e

    @staticmethod
    def write(path: Path, content: dict[str, Any]) -> None:
        """Write dictionary to YAML file.

        Args:
            path: File path
            content: Dictionary content

        Raises:
            IOError: If writing fails
        """
        try:
            try:
                import yaml
            except ImportError:
                raise IOError("PyYAML package is not installed. Please install it with: pip install pyyaml")

            with path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(content, f, default_flow_style=False)
        except Exception as e:
            raise IOError(f"Failed to write YAML file {path}: {e}") from e


class IniFileHandler:
    """INI file handler implementation."""

    @staticmethod
    def read(path: Path) -> dict[str, dict[str, str]]:
        """Read INI file.

        Args:
            path: File path

        Returns:
            File content as nested dictionary

        Raises:
            IOError: If reading fails
        """
        try:
            config = configparser.ConfigParser()
            config.read(path)
            return {section: dict(config[section]) for section in config.sections()}
        except Exception as e:
            raise IOError(f"Failed to read INI file {path}: {e}") from e

    @staticmethod
    def write(path: Path, content: dict[str, dict[str, str]]) -> None:
        """Write nested dictionary to INI file.

        Args:
            path: File path
            content: Nested dictionary content

        Raises:
            IOError: If writing fails
        """
        try:
            config = configparser.ConfigParser()
            for section, values in content.items():
                config[section] = values
            with path.open("w", encoding="utf-8") as f:
                config.write(f)
        except Exception as e:
            raise IOError(f"Failed to write INI file {path}: {e}") from e


class FileIO(BaseModule[ModuleConfig]):
    """File I/O manager implementation."""

    def __init__(self) -> None:
        """Initialize file I/O manager."""
        super().__init__(ModuleConfig(name="file-io"))
        self._handlers: dict[str, tuple[FileReader, FileWriter]] = {
            ".txt": (TextFileHandler(), TextFileHandler()),
            ".yaml": (YamlFileHandler(), YamlFileHandler()),
            ".yml": (YamlFileHandler(), YamlFileHandler()),
            ".ini": (IniFileHandler(), IniFileHandler()),
        }

    async def _setup(self) -> None:
        """Setup file I/O manager."""
        pass

    async def _teardown(self) -> None:
        """Teardown file I/O manager."""
        pass

    async def get_stats(self) -> dict[str, Any]:
        """Get file I/O manager statistics.

        Returns:
            File I/O manager statistics
        """
        self._ensure_initialized()
        return {
            "name": self.config.name,
            "enabled": self.config.enabled,
            "supported_extensions": list(self._handlers.keys()),
        }

    def register_handler(
        self,
        extension: str,
        reader: FileReader,
        writer: FileWriter,
    ) -> None:
        """Register file handler.

        Args:
            extension: File extension (with dot)
            reader: File reader
            writer: File writer

        Raises:
            ValueError: If extension is invalid
        """
        if not extension.startswith("."):
            raise ValueError("Extension must start with a dot")
        self._handlers[extension] = (reader, writer)

    def read(self, path: Path | str) -> Any:
        """Read file content.

        Args:
            path: File path

        Returns:
            File content

        Raises:
            IOError: If reading fails or file type not supported
        """
        self._ensure_initialized()
        path = Path(path)
        extension = path.suffix.lower()

        if extension not in self._handlers:
            raise IOError(f"Unsupported file type: {extension}")

        reader = self._handlers[extension][0]
        return reader.read(path)

    def write(self, path: Path | str, content: Any) -> None:
        """Write content to file.

        Args:
            path: File path
            content: Content to write

        Raises:
            IOError: If writing fails or file type not supported
        """
        self._ensure_initialized()
        path = Path(path)
        extension = path.suffix.lower()

        if extension not in self._handlers:
            raise IOError(f"Unsupported file type: {extension}")

        writer = self._handlers[extension][1]
        writer.write(path, content)


__all__ = [
    "IOError",
    "FileReader",
    "FileWriter",
    "TextFileHandler",
    "YamlFileHandler",
    "IniFileHandler",
    "FileIO",
] 