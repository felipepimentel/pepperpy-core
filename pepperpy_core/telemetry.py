"""Telemetry implementation module."""

from dataclasses import dataclass, field
from typing import Any

from .exceptions import PepperpyError
from .module import BaseModule, ModuleConfig


class TelemetryError(PepperpyError):
    """Telemetry specific error."""

    pass


@dataclass
class TelemetryConfig(ModuleConfig):
    """Telemetry configuration."""

    # Required fields (inherited from ModuleConfig)
    name: str

    # Optional fields
    enabled: bool = True
    buffer_size: int = 1000
    flush_interval: int = 60  # seconds
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate configuration."""
        if self.buffer_size < 1:
            raise ValueError("buffer_size must be greater than 0")
        if self.flush_interval < 1:
            raise ValueError("flush_interval must be greater than 0")


@dataclass
class MetricData:
    """Metric data."""

    name: str
    value: float
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class TelemetryCollector(BaseModule[TelemetryConfig]):
    """Telemetry collector implementation."""

    def __init__(self) -> None:
        """Initialize telemetry collector."""
        config = TelemetryConfig(name="telemetry-collector")
        super().__init__(config)
        self._metrics: list[dict[str, Any]] = []

    async def _setup(self) -> None:
        """Setup telemetry collector."""
        self._metrics.clear()

    async def _teardown(self) -> None:
        """Teardown telemetry collector."""
        await self.flush()
        self._metrics.clear()

    async def collect(self, metric: dict[str, Any]) -> None:
        """Collect metric.

        Args:
            metric: Metric data to collect
        """
        if not self.is_initialized:
            await self.initialize()
        if len(self._metrics) >= self.config.buffer_size:
            await self.flush()
        self._metrics.append(metric)

    async def flush(self) -> None:
        """Flush collected metrics."""
        if not self.is_initialized:
            await self.initialize()
        # Implementation for sending metrics to telemetry service would go here
        self._metrics.clear()

    async def get_stats(self) -> dict[str, Any]:
        """Get telemetry collector statistics.

        Returns:
            Telemetry collector statistics
        """
        if not self.is_initialized:
            await self.initialize()
        return {
            "name": self.config.name,
            "enabled": self.config.enabled,
            "buffered_metrics": len(self._metrics),
            "buffer_size": self.config.buffer_size,
            "flush_interval": self.config.flush_interval,
        }


class MetricsCollector(BaseModule[TelemetryConfig]):
    """Metrics collector implementation."""

    def __init__(self) -> None:
        """Initialize metrics collector."""
        config = TelemetryConfig(name="metrics-collector")
        super().__init__(config)
        self._metrics: dict[str, list[MetricData]] = {}

    async def _setup(self) -> None:
        """Setup metrics collector."""
        self._metrics.clear()

    async def _teardown(self) -> None:
        """Teardown metrics collector."""
        self._metrics.clear()

    async def collect(
        self, name: str, value: float, tags: dict[str, str] | None = None
    ) -> None:
        """Collect metric.

        Args:
            name: Metric name
            value: Metric value
            tags: Optional metric tags
        """
        if not self.is_initialized:
            await self.initialize()

        if name not in self._metrics:
            self._metrics[name] = []

        metric = MetricData(
            name=name,
            value=value,
            tags=tags or {},
        )

        metrics = self._metrics[name]
        metrics.append(metric)

        if len(metrics) > self.config.buffer_size:
            self._metrics[name] = metrics[-self.config.buffer_size :]

    async def get_stats(self) -> dict[str, Any]:
        """Get metrics collector statistics.

        Returns:
            Metrics collector statistics
        """
        if not self.is_initialized:
            await self.initialize()

        total_metrics = sum(len(metrics) for metrics in self._metrics.values())

        return {
            "name": self.config.name,
            "enabled": self.config.enabled,
            "total_metrics": total_metrics,
            "metric_names": list(self._metrics.keys()),
            "buffer_size": self.config.buffer_size,
            "flush_interval": self.config.flush_interval,
        }


__all__ = [
    "TelemetryError",
    "TelemetryConfig",
    "MetricData",
    "TelemetryCollector",
    "MetricsCollector",
] 