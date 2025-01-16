"""Module example module."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from pepperpy.module import BaseModule, ModuleConfig


@dataclass
class ProcessorConfig(ModuleConfig):
    """Processor configuration."""

    name: str = "processor"
    enabled: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)


class Processor(BaseModule[ProcessorConfig]):
    """Example processor module."""

    def __init__(self, config: Optional[ProcessorConfig] = None) -> None:
        """Initialize processor.

        Args:
            config: Optional processor configuration
        """
        super().__init__(config or ProcessorConfig())

    async def _setup(self) -> None:
        """Set up processor."""
        if not self.config.enabled:
            return
        print(f"Initializing processor: {self.config.name}")

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data.

        Args:
            data: Input data

        Returns:
            Processed data
        """
        if not self.config.enabled:
            return data

        print(f"Processing data with {self.config.name}")
        data["processed"] = True
        data["processor"] = self.config.name
        return data

    async def _teardown(self) -> None:
        """Clean up processor."""
        if not self.config.enabled:
            return
        print(f"Cleaning up processor: {self.config.name}")


async def main() -> None:
    """Run example."""
    # Create processor with custom config
    config = ProcessorConfig(
        name="example_processor",
        enabled=True,
        settings={"key": "value"},
        dependencies=["other_processor"],
    )
    processor = Processor(config)

    # Initialize processor
    await processor.initialize()

    try:
        # Process some data
        data = {"input": "value"}
        result = await processor.process(data)
        print(f"Processed data: {result}")

    finally:
        # Clean up
        await processor.teardown()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
