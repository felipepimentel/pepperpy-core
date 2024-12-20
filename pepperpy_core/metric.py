"""Metrics implementation module."""

import asyncio
import functools
import time
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import Any, Generic, ParamSpec, TypeVar, Union, cast

from .exceptions import PepperpyError
from .module import BaseModule, ModuleConfig


class MetricError(PepperpyError):
    """Metric specific error."""

    pass


@dataclass
class MetricConfig(ModuleConfig):
    """Metric configuration."""

    # Required fields (inherited from ModuleConfig)
    name: str

    # Optional fields
    enabled: bool = True
    interval: float = 60.0  # Collection interval in seconds
    buffer_size: int = 1000  # Maximum number of metrics to buffer
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate configuration."""
        if self.interval <= 0:
            raise ValueError("interval must be positive")
        if self.buffer_size < 1:
            raise ValueError("buffer_size must be greater than 0")


@dataclass
class MetricData:
    """Metric data."""

    name: str
    value: float
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class MetricCollector(BaseModule[MetricConfig]):
    """Base metrics collector implementation."""

    def __init__(self, config: MetricConfig | None = None) -> None:
        """Initialize metrics collector.

        Args:
            config: Metrics configuration
        """
        super().__init__(config or MetricConfig(name="metrics-collector"))
        self._metrics: dict[str, Any] = {}
        self._count: int = 0

    async def _setup(self) -> None:
        """Setup metrics collector."""
        self._metrics.clear()
        self._count = 0

    async def _teardown(self) -> None:
        """Cleanup metrics collector."""
        self._metrics.clear()
        self._count = 0

    async def collect(
        self, name: str, value: Any, tags: dict[str, str] | None = None
    ) -> None:
        """Collect metric.

        Args:
            name: Metric name
            value: Metric value
            tags: Optional metric tags
        """
        if not self.is_initialized:
            await self.initialize()

        if not self.config.enabled:
            return

        self._metrics[name] = {
            "value": value,
            "tags": tags or {},
            "timestamp": self._count,
        }
        self._count += 1

        # Buffer management
        if len(self._metrics) > self.config.buffer_size:
            # Remove oldest metrics
            sorted_metrics = sorted(
                self._metrics.items(), key=lambda x: x[1]["timestamp"]
            )
            for name, _ in sorted_metrics[: -self.config.buffer_size]:
                del self._metrics[name]

    async def get_stats(self) -> dict[str, Any]:
        """Get metrics statistics.

        Returns:
            Metrics statistics
        """
        if not self.is_initialized:
            await self.initialize()

        return {
            "name": self.config.name,
            "enabled": self.config.enabled,
            "interval": self.config.interval,
            "buffer_size": self.config.buffer_size,
            "metrics_count": len(self._metrics),
            "total_collected": self._count,
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
    collector: MetricCollector | None = None,
) -> Callable[[AnyFunc[P, R]], AnyFunc[P, R]]:
    """Decorator to measure function execution time.

    Args:
        collector: Optional metrics collector. If not provided, a new one will be created.

    Returns:
        Decorated function
    """
    metrics = collector or MetricCollector(MetricConfig(name="timing-metrics"))

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
    collector: MetricCollector | None = None,
) -> Callable[[AnyFunc[P, R]], AnyFunc[P, R]]:
    """Decorator to count function calls.

    Args:
        collector: Optional metrics collector. If not provided, a new one will be created.

    Returns:
        Decorated function
    """
    metrics = collector or MetricCollector(MetricConfig(name="count-metrics"))

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
    "MetricError",
    "MetricConfig",
    "MetricData",
    "MetricCollector",
    "timing",
    "count",
] 