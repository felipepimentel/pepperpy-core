"""Configuration example."""

from typing import Any

from pepperpy.config import (
    Config,
    ConfigLoader,
    JsonConfigLoader,
    YamlConfigLoader,
)


class ExampleConfig(Config):
    """Example configuration."""

    def __init__(self, name: str = "example") -> None:
        """Initialize configuration."""
        super().__init__(name=name)
        self._loader: ConfigLoader | None = None

    async def load_from_json(self, path: str) -> None:
        """Load configuration from JSON file."""
        loader = JsonConfigLoader()
        await self.load(loader, path)

    async def load_from_yaml(self, path: str) -> None:
        """Load configuration from YAML file."""
        loader = YamlConfigLoader()
        await self.load(loader, path)

    async def get_stats(self) -> dict[str, Any]:
        """Get configuration statistics."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "metadata": self.metadata,
            "loader": self._loader.__class__.__name__ if self._loader else None,
        }
