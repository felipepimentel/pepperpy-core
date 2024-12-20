"""Example of using the configuration system."""

import asyncio
from pathlib import Path

from pepperpy_core.config import ConfigManager, ConfigManagerConfig
from pydantic import BaseModel


class ExampleConfig(BaseModel):
    """Example configuration."""

    name: str = "example"
    value: str = "default"


async def main() -> None:
    """Run the example."""
    # Create config directory
    config_dir = Path("/tmp/example_config")
    config_dir.mkdir(exist_ok=True)

    # Create config file
    config_file = config_dir / "example.json"
    config_file.write_text('{"name": "test", "value": "custom"}')

    # Initialize config manager
    config = ConfigManagerConfig(
        name="example",
        config_path=str(config_dir),
        enabled=True,
    )
    manager = ConfigManager(config=config)
    await manager.initialize()

    try:
        # Load configuration
        example_config = await manager.get_config("example", ExampleConfig)
        print(f"Loaded config: {example_config}")
    finally:
        # Cleanup
        await manager.cleanup()
        config_file.unlink(missing_ok=True)
        config_dir.rmdir()


if __name__ == "__main__":
    asyncio.run(main())
