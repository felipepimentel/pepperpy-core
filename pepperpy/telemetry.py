"""Telemetry module."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from pepperpy.core import PepperpyError
from pepperpy.module import BaseModule, ModuleConfig


class TelemetryError(PepperpyError):
    """Telemetry error."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, details, cause)


@dataclass
class TelemetryConfig(ModuleConfig):
    """Telemetry configuration."""

    name: str = "metrics_collector"
    metadata: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector(BaseModule[TelemetryConfig]):
    """Metrics collector."""

    def __init__(self, config: Optional[TelemetryConfig] = None) -> None:
        """Initialize metrics collector.

        Args:
            config: Telemetry configuration
        """
        super().__init__(config or TelemetryConfig())
        self._metrics: Dict[str, Any] = {}

    def _ensure_initialized(self) -> None:
        """Ensure collector is initialized.

        Raises:
            TelemetryError: If collector is not initialized
        """
        if not self.is_initialized:
            raise TelemetryError(
                "Metrics collector is not initialized",
                {"collector_name": self.config.name},
            )

    async def _setup(self) -> None:
        """Set up metrics collector."""
        self._metrics.clear()

    async def _teardown(self) -> None:
        """Clean up metrics collector."""
        self._metrics.clear()

    def record_metric(
        self,
        name: str,
        value: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record metric.

        Args:
            name: Metric name
            value: Metric value
            metadata: Metric metadata

        Raises:
            TelemetryError: If metric recording fails
        """
        self._ensure_initialized()
        self._metrics[name] = {
            "value": value,
            "metadata": metadata or {},
        }

    def get_metric(self, name: str) -> Any:
        """Get metric value.

        Args:
            name: Metric name

        Returns:
            Metric value

        Raises:
            TelemetryError: If metric not found
        """
        self._ensure_initialized()
        if name not in self._metrics:
            raise TelemetryError(
                "Metric not found",
                {"metric_name": name, "collector_name": self.config.name},
            )
        return self._metrics[name]["value"]

    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics.

        Returns:
            Dictionary of metrics
        """
        self._ensure_initialized()
        return {name: data["value"] for name, data in self._metrics.items()}


__all__ = ["MetricsCollector", "TelemetryConfig", "TelemetryError"]
