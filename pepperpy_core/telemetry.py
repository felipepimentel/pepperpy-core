"""Telemetry module."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .exceptions import TelemetryError
from .module import BaseModule, ModuleConfig


@dataclass
class TelemetryConfig(ModuleConfig):
    """Telemetry configuration."""

    name: str
    enabled: bool = True
    buffer_size: int = 1000
    flush_interval: float = 60.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Post initialization validation."""
        self.validate()

    def validate(self) -> None:
        """Validate configuration."""
        if not self.name:
            raise ValueError("name cannot be empty")
        if self.buffer_size <= 0:
            raise ValueError("Buffer size must be positive")
        if self.flush_interval <= 0:
            raise ValueError("Flush interval must be positive")


@dataclass
class Metric:
    """Metric data."""

    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class MetricsCollector(BaseModule[TelemetryConfig]):
    """Metrics collector implementation."""

    def __init__(self) -> None:
        """Initialize metrics collector."""
        config = TelemetryConfig(name="metrics-collector")
        super().__init__(config)
        self._metrics: list[Metric] = []
        self._flush_task: asyncio.Task[None] | None = None

    async def _setup(self) -> None:
        """Setup metrics collector."""
        self._metrics.clear()
        if self.config.enabled:
            self._flush_task = asyncio.create_task(self._flush_loop())

    async def _teardown(self) -> None:
        """Teardown metrics collector."""
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
            self._flush_task = None
        await self._flush_metrics()
        self._metrics.clear()
        self._is_initialized = False

    async def _flush_loop(self) -> None:
        """Flush metrics periodically."""
        while True:
            try:
                await asyncio.sleep(self.config.flush_interval)
                await self._flush_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error and continue
                print(f"Error in flush loop: {e}")

    async def _flush_metrics(self) -> None:
        """Flush metrics to storage."""
        if not self._metrics:
            return

        try:
            # Implementation would send metrics to storage
            # This is a placeholder implementation
            await asyncio.sleep(0.1)
            self._metrics.clear()
        except Exception as e:
            raise TelemetryError(f"Failed to flush metrics: {e}") from e

    async def record(
        self,
        name: str,
        value: float,
        tags: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record metric.

        Args:
            name: Metric name
            value: Metric value
            tags: Metric tags
            metadata: Metric metadata

        Raises:
            TelemetryError: If recording fails
        """
        self._ensure_initialized()

        if not self.config.enabled:
            return

        if tags is None:
            tags = {}
        if metadata is None:
            metadata = {}

        metric = Metric(
            name=name,
            value=value,
            tags=tags,
            metadata=metadata,
        )

        if len(self._metrics) >= self.config.buffer_size:
            await self._flush_metrics()

        self._metrics.append(metric)

    async def get_stats(self) -> dict[str, Any]:
        """Get metrics collector statistics.

        Returns:
            Metrics collector statistics
        """
        self._ensure_initialized()
        return {
            "name": self.config.name,
            "enabled": self.config.enabled,
            "buffer_size": self.config.buffer_size,
            "flush_interval": self.config.flush_interval,
            "metrics_count": len(self._metrics),
            "is_flushing": self._flush_task is not None,
        }


__all__ = [
    "TelemetryConfig",
    "Metric",
    "MetricsCollector",
]
