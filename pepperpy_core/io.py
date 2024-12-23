"""File I/O operations module."""

import configparser
import json
from pathlib import Path
from typing import Any, Protocol

from .module import BaseModule, ModuleConfig


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
            if not path.exists():
                raise OSError(
                    f"Failed to read text file {path}: No such file or directory"
                )
            return path.read_text(encoding="utf-8")
        except OSError as e:
            raise OSError(f"Failed to read text file {path}: {e}") from e

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
            if path.is_dir():
                raise OSError(f"Failed to write text file {path}: Is a directory")
            path.write_text(content, encoding="utf-8")
        except OSError as e:
            raise OSError(f"Failed to write text file {path}: {e}") from e


class JsonFileHandler:
    """JSON file handler implementation."""

    @staticmethod
    def read(path: Path) -> dict[str, Any]:
        """Read JSON file.

        Args:
            path: File path

        Returns:
            File content as dictionary

        Raises:
            IOError: If reading fails
        """
        try:
            if not path.exists():
                raise OSError(
                    f"Failed to read JSON file {path}: No such file or directory"
                )
            content = path.read_text(encoding="utf-8")
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                raise OSError(f"Failed to read JSON file {path}: {e}") from e
        except OSError as e:
            raise OSError(f"Failed to read JSON file {path}: {e}") from e

    @staticmethod
    def write(path: Path, content: dict[str, Any]) -> None:
        """Write dictionary to JSON file.

        Args:
            path: File path
            content: Dictionary content

        Raises:
            IOError: If writing fails
        """
        try:
            if path.is_dir():
                raise OSError(f"Failed to write JSON file {path}: Is a directory")
            try:
                json_str = json.dumps(content)
            except (TypeError, ValueError) as e:
                raise OSError(f"Failed to write JSON file {path}: {e}") from e
            path.write_text(json_str, encoding="utf-8")
        except OSError as e:
            raise OSError(f"Failed to write JSON file {path}: {e}") from e


class YamlFileHandler:
    """YAML file handler implementation."""

    @staticmethod
    def read(path: Path) -> dict[str, Any]:
        """Read YAML file and return dictionary.

        Args:
            path: File path

        Returns:
            File content as dictionary

        Raises:
            IOError: If reading fails
        """
        try:
            if not path.exists():
                raise OSError(
                    f"Failed to read YAML file {path}: No such file or directory"
                )
            import yaml

            content = path.read_text(encoding="utf-8")
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError as e:
                raise OSError(f"Failed to read YAML file {path}: {e}") from e
        except OSError as e:
            raise OSError(f"Failed to read YAML file {path}: {e}") from e

    @staticmethod
    def write(path: Path, content: dict[str, Any]) -> None:
        """Write dictionary to YAML file.

        Args:
            path: File path
            content: Dictionary content

        Raises:
            IOError: If writing fails
        """
        import yaml

        if path.is_dir():
            raise OSError(f"Failed to write YAML file {path}: Is a directory")

        try:
            yaml_str = yaml.dump(content)
        except (TypeError, ValueError, yaml.YAMLError) as e:
            raise OSError(f"Failed to write YAML file {path}: {e}") from e

        try:
            path.write_text(yaml_str, encoding="utf-8")
        except OSError as e:
            raise OSError(f"Failed to write YAML file {path}: {e}") from e


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
            if not path.exists():
                raise OSError(f"Failed to read INI file {path}: File not found")
            config = configparser.ConfigParser()
            try:
                config.read_string(path.read_text(encoding="utf-8"))
                return {section: dict(config[section]) for section in config.sections()}
            except configparser.Error as e:
                raise OSError(f"Failed to read INI file {path}: {e}") from e
        except OSError as e:
            raise OSError(f"Failed to read INI file {path}: {e}") from e

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
            if path.is_dir():
                raise OSError(
                    f"Failed to write INI file {path}: Cannot write to directory"
                )
            config = configparser.ConfigParser()
            try:
                config.read_dict(content)
            except (TypeError, ValueError) as e:
                raise OSError(f"Failed to write INI file {path}: {e}") from e
            with path.open("w", encoding="utf-8") as f:
                config.write(f)
        except OSError as e:
            raise OSError(f"Failed to write INI file {path}: {e}") from e


class FileIO(BaseModule[ModuleConfig]):
    """File I/O manager."""

    def __init__(self, config: ModuleConfig | None = None) -> None:
        """Initialize file I/O manager.

        Args:
            config: Optional configuration
        """
        super().__init__(config or ModuleConfig(name="file-io"))
        self._handlers: dict[str, type[FileReader] | type[FileWriter]] = {
            ".txt": TextFileHandler,
            ".yaml": YamlFileHandler,
            ".yml": YamlFileHandler,
            ".ini": IniFileHandler,
            ".json": JsonFileHandler,
        }

    async def _setup(self) -> None:
        """Set up file I/O manager."""
        pass

    async def _teardown(self) -> None:
        """Clean up file I/O manager."""
        pass

    async def read(self, path: str | Path) -> Any:
        """Read file content.

        Args:
            path: File path

        Returns:
            File content

        Raises:
            IOError: If reading fails
        """
        self._ensure_initialized()
        if isinstance(path, str):
            path = Path(path)
        handler = self._get_handler(path)
        return handler.read(path)

    async def write(self, path: str | Path, content: Any) -> None:
        """Write content to file.

        Args:
            path: File path
            content: Content to write

        Raises:
            IOError: If writing fails
        """
        self._ensure_initialized()
        if isinstance(path, str):
            path = Path(path)
        handler = self._get_handler(path)
        handler.write(path, content)

    def _get_handler(self, path: Path) -> type[FileReader] | type[FileWriter]:
        """Get file handler for path.

        Args:
            path: File path

        Returns:
            File handler

        Raises:
            IOError: If file type is not supported
        """
        suffix = path.suffix.lower()
        if suffix not in self._handlers:
            raise OSError(f"Unsupported file type: {suffix}")
        return self._handlers[suffix]

    async def get_stats(self) -> dict[str, Any]:
        """Get file I/O statistics.

        Returns:
            Statistics dictionary
        """
        self._ensure_initialized()
        return {
            "name": self.config.name,
            "supported_extensions": sorted(self._handlers.keys()),
        }


__all__ = [
    "FileReader",
    "FileWriter",
    "TextFileHandler",
    "YamlFileHandler",
    "IniFileHandler",
    "JsonFileHandler",
    "FileIO",
]
