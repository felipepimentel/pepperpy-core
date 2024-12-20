"""Module example."""

from dataclasses import dataclass, field
from typing import Any

from pepperpy_core.module import BaseModule, ModuleConfig
from pepperpy_core.types import JsonDict


@dataclass
class ProcessorConfig(ModuleConfig):
    """Processor configuration."""

    batch_size: int = 100
    max_workers: int = 4
    timeout: float = 30.0
    metadata: JsonDict = field(default_factory=dict)


class DataProcessor(BaseModule[ProcessorConfig]):
    """Example data processor module."""

    def __init__(self) -> None:
        """Initialize processor."""
        config = ProcessorConfig(name="processor")
        super().__init__(config)
        self._processed: int = 0

    async def _setup(self) -> None:
        """Setup processor resources."""
        pass

    async def _teardown(self) -> None:
        """Teardown processor resources."""
        self._processed = 0

    async def process(self, data: Any) -> Any:
        """Process data.

        Args:
            data: Data to process

        Returns:
            Processed data
        """
        if not self.is_initialized:
            await self.initialize()

        if not self.config.enabled:
            return data

        # Simulate processing
        self._processed += 1
        return f"Processed: {data}"

    async def get_stats(self) -> dict[str, Any]:
        """Get processor statistics."""
        if not self.is_initialized:
            await self.initialize()

        return {
            "name": self.config.name,
            "enabled": self.config.enabled,
            "batch_size": self.config.batch_size,
            "max_workers": self.config.max_workers,
            "processed": self._processed,
        }
