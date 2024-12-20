"""Telemetry implementation module."""

import asyncio
import functools
import time
from collections.abc import Awaitable, Callable, Coroutine
from dataclasses import dataclass, field
from typing import Any, Generic, ParamSpec, Protocol, TypeVar, Union, cast

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
    flush_interval: float = 60.0  # seconds
    prometheus_port: int = 8000  # Port for Prometheus metrics
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate configuration."""
        if self.buffer_size < 1:
            raise ValueError("buffer_size must be greater than 0")
        if self.flush_interval <= 0:
            raise ValueError("flush_interval must be positive")
        if self.prometheus_port < 0:
            raise ValueError("prometheus_port must be non-negative")


@dataclass
class MetricData:
    """Metric data."""

    name: str
    value: float
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


# Prometheus integration
class CounterProtocol(Protocol):
    """Protocol for Prometheus counter type."""

    def inc(self, amount: float = 1.0) -> None:
        """Increment counter."""
        ...

    def labels(self, **kwargs: str) -> "CounterProtocol":
        """Get counter with labels."""
        ...


class HistogramProtocol(Protocol):
    """Protocol for Prometheus histogram type."""

    def observe(self, amount: float) -> None:
        """Observe value."""
        ...

    def labels(self, **kwargs: str) -> "HistogramProtocol":
        """Get histogram with labels."""
        ...


# Try importing prometheus
try:
    from prometheus_client import (
        Counter as PromCounter,
        Histogram as PromHistogram,
        start_http_server as prom_start_server,
    )

    prometheus_available = True
except ImportError:
    prometheus_available = False
    PromCounter = None  # type: ignore
    PromHistogram = None  # type: ignore
    prom_start_server = None  # type: ignore


class TelemetryCollector(BaseModule[TelemetryConfig]):
    """Telemetry collector implementation."""

    def __init__(self) -> None:
        """Initialize telemetry collector."""
        config = TelemetryConfig(name="telemetry-collector")
        super().__init__(config)
        self._metrics: list[dict[str, Any]] = []
        self._prometheus_started = False

    async def _setup(self) -> None:
        """Setup telemetry collector."""
        self._metrics.clear()
        if prometheus_available and not self._prometheus_started:
            prom_start_server(self.config.prometheus_port)
            self._prometheus_started = True

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
            "prometheus_enabled": prometheus_available,
            "prometheus_port": self.config.prometheus_port if prometheus_available else None,
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


# Type variables for function decorators
P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")

# Types for sync and async functions
SyncFunc = Callable[P, R]
AsyncFunc = Callable[P, Coroutine[Any, Any, R]]
AnyFunc = Union[SyncFunc[P, R], AsyncFunc[P, R]]


def timing(
    collector: MetricsCollector | None = None,
) -> Callable[[AnyFunc[P, R]], AnyFunc[P, R]]:
    """Decorator to measure function execution time.

    Args:
        collector: Optional metrics collector. If not provided, a new one will be created.

    Returns:
        Decorated function
    """
    metrics = collector or MetricsCollector()

    def decorator(func: AnyFunc[P, R]) -> AnyFunc[P, R]:
        """Decorate function.

        Args:
            func: Function to decorate

        Returns:
            Decorated function
        """
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                start_time = time.perf_counter()
                try:
                    result = await cast(AsyncFunc[P, R], func)(*args, **kwargs)
                    return result
                finally:
                    duration = time.perf_counter() - start_time
                    await metrics.collect(
                        name=f"{func.__module__}.{func.__qualname__}",
                        value=duration,
                        tags={"unit": "seconds"},
                    )

            return cast(AnyFunc[P, R], async_wrapper)
        else:

            @functools.wraps(func)
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                start_time = time.perf_counter()
                try:
                    result = cast(SyncFunc[P, R], func)(*args, **kwargs)
                    return result
                finally:
                    duration = time.perf_counter() - start_time
                    # Create task to collect metrics asynchronously
                    asyncio.create_task(
                        metrics.collect(
                            name=f"{func.__module__}.{func.__qualname__}",
                            value=duration,
                            tags={"unit": "seconds"},
                        )
                    )

            return cast(AnyFunc[P, R], sync_wrapper)

    return decorator


def count(
    collector: MetricsCollector | None = None,
) -> Callable[[AnyFunc[P, R]], AnyFunc[P, R]]:
    """Decorator to count function calls.

    Args:
        collector: Optional metrics collector. If not provided, a new one will be created.

    Returns:
        Decorated function
    """
    metrics = collector or MetricsCollector()

    def decorator(func: AnyFunc[P, R]) -> AnyFunc[P, R]:
        """Decorate function.

        Args:
            func: Function to decorate

        Returns:
            Decorated function
        """
        counter = 0

        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                nonlocal counter
                counter += 1
                try:
                    result = await cast(AsyncFunc[P, R], func)(*args, **kwargs)
                    return result
                finally:
                    await metrics.collect(
                        name=f"{func.__module__}.{func.__qualname__}",
                        value=counter,
                        tags={"type": "counter"},
                    )

            return cast(AnyFunc[P, R], async_wrapper)
        else:

            @functools.wraps(func)
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                nonlocal counter
                counter += 1
                try:
                    result = cast(SyncFunc[P, R], func)(*args, **kwargs)
                    return result
                finally:
                    # Create task to collect metrics asynchronously
                    asyncio.create_task(
                        metrics.collect(
                            name=f"{func.__module__}.{func.__qualname__}",
                            value=counter,
                            tags={"type": "counter"},
                        )
                    )

            return cast(AnyFunc[P, R], sync_wrapper)

    return decorator


__all__ = [
    "TelemetryError",
    "TelemetryConfig",
    "MetricData",
    "CounterProtocol",
    "HistogramProtocol",
    "TelemetryCollector",
    "MetricsCollector",
    "timing",
    "count",
] 