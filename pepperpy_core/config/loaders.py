"""Configuration loaders implementation."""

import json
import os
from pathlib import Path
from typing import Any

import yaml

from ..exceptions.base import ConfigError
from .base import ConfigLoader, ConfigSource, ConfigValue

class EnvConfigLoader(ConfigLoader):
    """Environment variables configuration loader."""
    
    def __init__(self, prefix: str = "") -> None:
        """Initialize loader.
        
        Args:
            prefix: Optional environment variable prefix
        """
        self.prefix = prefix
        
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
            
            for key, value in os.environ.items():
                if self.prefix and not key.startswith(self.prefix):
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
                
            return values
            
        except Exception as e:
            raise ConfigError("Failed to load environment variables", cause=e)

class JsonConfigLoader(ConfigLoader):
    """JSON file configuration loader."""
    
    async def load(self, path: str | Path) -> dict[str, ConfigValue]:
        """Load configuration from JSON file.
        
        Args:
            path: JSON file path
            
        Returns:
            Dictionary of configuration values
            
        Raises:
            ConfigError: If loading fails
        """
        try:
            path = Path(path)
            if not path.exists():
                raise ConfigError(f"Configuration file not found: {path}")
                
            with path.open() as f:
                data = json.load(f)
                
            return self._process_dict(data, str(path))
            
        except Exception as e:
            raise ConfigError(f"Failed to load JSON file: {path}", cause=e)
            
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

class YamlConfigLoader(JsonConfigLoader):
    """YAML file configuration loader."""
    
    async def load(self, path: str | Path) -> dict[str, ConfigValue]:
        """Load configuration from YAML file.
        
        Args:
            path: YAML file path
            
        Returns:
            Dictionary of configuration values
            
        Raises:
            ConfigError: If loading fails
        """
        try:
            path = Path(path)
            if not path.exists():
                raise ConfigError(f"Configuration file not found: {path}")
                
            with path.open() as f:
                data = yaml.safe_load(f)
                
            return self._process_dict(data, str(path))
            
        except Exception as e:
            raise ConfigError(f"Failed to load YAML file: {path}", cause=e)

class ChainedConfigLoader(ConfigLoader):
    """Chained configuration loader that combines multiple loaders."""
    
    def __init__(self, loaders: list[ConfigLoader]) -> None:
        """Initialize loader.
        
        Args:
            loaders: List of loaders to chain
        """
        self.loaders = loaders
        
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
    "EnvConfigLoader",
    "JsonConfigLoader",
    "YamlConfigLoader",
    "ChainedConfigLoader",
] 