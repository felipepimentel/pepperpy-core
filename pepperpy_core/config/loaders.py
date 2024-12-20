"""Configuration loaders implementation."""

import json
import os
from pathlib import Path
from typing import Any, Protocol

import yaml

from ..exceptions.base import ConfigError
from .base import ConfigLoader, ConfigSource, ConfigValue

class FileWatcher(Protocol):
    """File watcher protocol."""
    
    async def watch(self, path: Path) -> None:
        """Watch file for changes.
        
        Args:
            path: File path to watch
            
        Raises:
            ConfigError: If watching fails
        """
        ...
        
    async def unwatch(self, path: Path) -> None:
        """Stop watching file.
        
        Args:
            path: File path to unwatch
            
        Raises:
            ConfigError: If unwatching fails
        """
        ...
        
    async def has_changed(self, path: Path) -> bool:
        """Check if file has changed.
        
        Args:
            path: File path to check
            
        Returns:
            True if file has changed
            
        Raises:
            ConfigError: If checking fails
        """
        ...

class SimpleFileWatcher:
    """Simple file watcher based on modification time."""
    
    def __init__(self) -> None:
        """Initialize watcher."""
        self._mtimes: dict[Path, float] = {}
        
    async def watch(self, path: Path) -> None:
        """Watch file for changes.
        
        Args:
            path: File path to watch
            
        Raises:
            ConfigError: If watching fails
        """
        try:
            self._mtimes[path] = path.stat().st_mtime
        except Exception as e:
            raise ConfigError(f"Failed to watch file: {path}", cause=e)
        
    async def unwatch(self, path: Path) -> None:
        """Stop watching file.
        
        Args:
            path: File path to unwatch
            
        Raises:
            ConfigError: If unwatching fails
        """
        self._mtimes.pop(path, None)
        
    async def has_changed(self, path: Path) -> bool:
        """Check if file has changed.
        
        Args:
            path: File path to check
            
        Returns:
            True if file has changed
            
        Raises:
            ConfigError: If checking fails
        """
        try:
            if path not in self._mtimes:
                return False
                
            current_mtime = path.stat().st_mtime
            return current_mtime > self._mtimes[path]
            
        except Exception as e:
            raise ConfigError(f"Failed to check file: {path}", cause=e)

class EnvConfigLoader(ConfigLoader):
    """Environment variables configuration loader."""
    
    def __init__(self, prefix: str = "", auto_reload: bool = False) -> None:
        """Initialize loader.
        
        Args:
            prefix: Optional environment variable prefix
            auto_reload: Whether to automatically reload on changes
        """
        self.prefix = prefix
        self.auto_reload = auto_reload
        self._last_env: dict[str, str] = {}
        
    async def supports_reload(self) -> bool:
        """Check if loader supports reloading.
        
        Returns:
            True if reloading is supported
        """
        return self.auto_reload
        
    async def load(self, path: str | Path) -> dict[str, ConfigValue]:
        """Load configuration from environment variables.
        
        Args:
            path: Configuration path prefix
            
        Returns:
            Dictionary of configuration values
            
        Raises:
            ConfigError: If loading fails
        """
        try:
            values: dict[str, ConfigValue] = {}
            current_env = dict(os.environ)
            
            for key, value in current_env.items():
                if self.prefix and not key.startswith(self.prefix):
                    continue
                    
                # Skip if unchanged
                if (
                    self.auto_reload
                    and key in self._last_env
                    and self._last_env[key] == value
                ):
                    continue
                    
                # Remove prefix and convert to lowercase
                name = key[len(self.prefix):].lower()
                
                # Try to parse value as JSON
                try:
                    parsed_value = json.loads(value)
                except json.JSONDecodeError:
                    parsed_value = value
                    
                values[name] = ConfigValue(
                    value=parsed_value,
                    source=ConfigSource.ENV,
                    path=key,
                )
                
            # Update last environment
            if self.auto_reload:
                self._last_env = current_env
                
            return values
            
        except Exception as e:
            raise ConfigError("Failed to load environment variables", cause=e)

class FileConfigLoader(ConfigLoader):
    """Base file configuration loader."""
    
    def __init__(
        self,
        watcher: FileWatcher | None = None,
        encoding: str = "utf-8",
    ) -> None:
        """Initialize loader.
        
        Args:
            watcher: Optional file watcher
            encoding: File encoding
        """
        self.watcher = watcher or SimpleFileWatcher()
        self.encoding = encoding
        
    async def supports_reload(self) -> bool:
        """Check if loader supports reloading.
        
        Returns:
            True if reloading is supported
        """
        return True
        
    async def _read_file(self, path: Path) -> Any:
        """Read and parse file.
        
        Args:
            path: File path
            
        Returns:
            Parsed file contents
            
        Raises:
            ConfigError: If reading fails
        """
        raise NotImplementedError
        
    async def load(self, path: str | Path) -> dict[str, ConfigValue]:
        """Load configuration from file.
        
        Args:
            path: File path
            
        Returns:
            Dictionary of configuration values
            
        Raises:
            ConfigError: If loading fails
        """
        try:
            path = Path(path)
            if not path.exists():
                raise ConfigError(f"Configuration file not found: {path}")
                
            # Start watching file
            await self.watcher.watch(path)
                
            data = await self._read_file(path)
            return self._process_dict(data, str(path))
            
        except Exception as e:
            raise ConfigError(f"Failed to load file: {path}", cause=e)
            
    def _process_dict(
        self,
        data: dict[str, Any],
        path: str,
        prefix: str = "",
    ) -> dict[str, ConfigValue]:
        """Process dictionary recursively.
        
        Args:
            data: Dictionary to process
            path: Configuration path
            prefix: Key prefix
            
        Returns:
            Dictionary of configuration values
        """
        values: dict[str, ConfigValue] = {}
        
        for key, value in data.items():
            full_key = f"{prefix}{key}" if prefix else key
            
            if isinstance(value, dict):
                # Process nested dictionary
                nested = self._process_dict(value, path, f"{full_key}.")
                values.update(nested)
            else:
                values[full_key] = ConfigValue(
                    value=value,
                    source=ConfigSource.FILE,
                    path=f"{path}:{full_key}",
                )
                
        return values

class JsonConfigLoader(FileConfigLoader):
    """JSON file configuration loader."""
    
    async def _read_file(self, path: Path) -> Any:
        """Read and parse JSON file.
        
        Args:
            path: File path
            
        Returns:
            Parsed JSON data
            
        Raises:
            ConfigError: If reading fails
        """
        try:
            with path.open(encoding=self.encoding) as f:
                return json.load(f)
        except Exception as e:
            raise ConfigError(f"Failed to read JSON file: {path}", cause=e)

class YamlConfigLoader(FileConfigLoader):
    """YAML file configuration loader."""
    
    async def _read_file(self, path: Path) -> Any:
        """Read and parse YAML file.
        
        Args:
            path: File path
            
        Returns:
            Parsed YAML data
            
        Raises:
            ConfigError: If reading fails
        """
        try:
            with path.open(encoding=self.encoding) as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise ConfigError(f"Failed to read YAML file: {path}", cause=e)

class ChainedConfigLoader(ConfigLoader):
    """Chained configuration loader that combines multiple loaders."""
    
    def __init__(self, loaders: list[ConfigLoader]) -> None:
        """Initialize loader.
        
        Args:
            loaders: List of loaders to chain
        """
        self.loaders = loaders
        
    async def supports_reload(self) -> bool:
        """Check if loader supports reloading.
        
        Returns:
            True if any loader supports reloading
        """
        return any(
            await loader.supports_reload()
            for loader in self.loaders
        )
        
    async def load(self, path: str | Path) -> dict[str, ConfigValue]:
        """Load configuration from all loaders.
        
        Args:
            path: Configuration path
            
        Returns:
            Dictionary of configuration values
            
        Raises:
            ConfigError: If loading fails
        """
        values: dict[str, ConfigValue] = {}
        errors: list[Exception] = []
        
        for loader in self.loaders:
            try:
                loader_values = await loader.load(path)
                values.update(loader_values)
            except Exception as e:
                errors.append(e)
                
        if errors and len(errors) == len(self.loaders):
            # All loaders failed
            raise ConfigError(
                "All configuration loaders failed",
                details={"errors": [str(e) for e in errors]},
            )
            
        return values

__all__ = [
    "FileWatcher",
    "SimpleFileWatcher",
    "EnvConfigLoader",
    "JsonConfigLoader",
    "YamlConfigLoader",
    "ChainedConfigLoader",
] 