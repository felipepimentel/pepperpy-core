"""Config example module."""

from dataclasses import dataclass, field
from typing import Any, Dict


class Config:
    """Base configuration class."""

    async def get_stats(self) -> Dict[str, Any]:
        """Get configuration stats.

        Returns:
            Configuration stats
        """
        raise NotImplementedError


@dataclass
class ExampleConfig(Config):
    """Example configuration."""

    name: str = "example"
    enabled: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)

    async def get_stats(self) -> Dict[str, Any]:
        """Get configuration stats.

        Returns:
            Configuration stats
        """
        return {
            "name": self.name,
            "enabled": self.enabled,
            "settings": self.settings,
        }


async def main() -> None:
    """Run example."""
    # Create config instance
    config = ExampleConfig(
        name="example",
        enabled=True,
        settings={"key": "value"},
    )

    # Get stats
    stats = await config.get_stats()
    print(f"Config stats: {stats}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
