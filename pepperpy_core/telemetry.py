"""Telemetry implementation module."""

import asyncio
import functools
import time
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ParamSpec, TypeVar

from .exceptions import PepperpyError
from .module import BaseModule, ModuleConfig
from .utils import utcnow


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
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate configuration."""
        if self.buffer_size < 1:
            raise ValueError("buffer_size must be greater than 0")
        if self.flush_interval <= 0:
            raise ValueError("flush_interval must be positive")


@dataclass
class MetricData:
    """Metric data."""

    name: str
    value: float
    tags: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


class MetricsCollector(BaseModule[TelemetryConfig]):
    """Simple metrics collector implementation."""

    def __init__(self) -> None:
        """Initialize metrics collector."""
        config = TelemetryConfig(name="metrics-collector")
        super().__init__(config)
        self._metrics: dict[str, list[MetricData]] = {}
        self._counters: dict[str, float] = {}

    async def _setup(self) -> None:
        """Setup metrics collector."""
        self._metrics.clear()
        self._counters.clear()

    async def _teardown(self) -> None:
        """Teardown metrics collector."""
        self._metrics.clear()
        self._counters.clear()

    async def record(
        self, name: str, value: float, tags: dict[str, str] | None = None
    ) -> None:
        """Record a metric value.

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

    async def increment(
        self, name: str, value: float = 1.0, tags: dict[str, str] | None = None
    ) -> None:
        """Increment a counter.

        Args:
            name: Counter name
            value: Value to increment by
            tags: Optional counter tags
        """
        if not self.is_initialized:
            await self.initialize()

        if name not in self._counters:
            self._counters[name] = 0

        self._counters[name] += value
        await self.record(name, self._counters[name], tags)

    def get_metric(self, name: str) -> list[MetricData]:
        """Get metric values.

        Args:
            name: Metric name

        Returns:
            List of metric values
        """
        self._ensure_initialized()
        return self._metrics.get(name, [])

    def get_counter(self, name: str) -> float:
        """Get counter value.

        Args:
            name: Counter name

        Returns:
            Counter value
        """
        self._ensure_initialized()
        return self._counters.get(name, 0)

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
            "counter_names": list(self._counters.keys()),
            "buffer_size": self.config.buffer_size,
            "flush_interval": self.config.flush_interval,
        }


# Type variables for function decorators
P = ParamSpec("P")
R = TypeVar("R")


def timing(
    collector: MetricsCollector,
    name: str | None = None,
    tags: dict[str, str] | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to measure function execution time.

    Args:
        collector: Metrics collector
        name: Optional metric name (defaults to function name)
        tags: Optional metric tags

    Returns:
        Decorated function
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        metric_name = name or f"{func.__module__}.{func.__qualname__}"

        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start_time = time.perf_counter()
            try:
                if not isinstance(func, Coroutine):
                    result = func(*args, **kwargs)
                else:
                    result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.perf_counter() - start_time
                await collector.record(
                    name=metric_name,
                    value=duration,
                    tags={"unit": "seconds", **(tags or {})},
                )

        @functools.wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start_time = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.perf_counter() - start_time
                # Note: This will work if there's an event loop running
                import asyncio

                asyncio.create_task(
                    collector.record(
                        name=metric_name,
                        value=duration,
                        tags={"unit": "seconds", **(tags or {})},
                    )
                )

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def count(
    collector: MetricsCollector,
    name: str | None = None,
    tags: dict[str, str] | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to count function calls.

    Args:
        collector: Metrics collector
        name: Optional metric name (defaults to function name)
        tags: Optional metric tags

    Returns:
        Decorated function
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        metric_name = name or f"{func.__module__}.{func.__qualname__}"

        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                if not isinstance(func, Coroutine):
                    result = func(*args, **kwargs)
                else:
                    result = await func(*args, **kwargs)
                return result
            finally:
                await collector.increment(
                    name=metric_name,
                    tags=tags,
                )

        @functools.wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return func(*args, **kwargs)
            finally:
                import asyncio

                asyncio.create_task(
                    collector.increment(
                        name=metric_name,
                        tags=tags,
                    )
                )

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


__all__ = [
    "TelemetryError",
    "TelemetryConfig",
    "MetricData",
    "MetricsCollector",
    "timing",
    "count",
]
