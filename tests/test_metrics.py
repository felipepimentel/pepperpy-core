"""Test metrics functionality."""

from collections.abc import AsyncGenerator
from typing import AsyncIterator, TypeVar

import pytest
import pytest_asyncio

from pepperpy_core.telemetry import MetricsCollector, TelemetryConfig

T = TypeVar("T")


async def async_next(agen: AsyncGenerator[T, None]) -> T:
    """Get next value from async generator."""
    try:
        return await agen.__anext__()
    except StopAsyncIteration:
        raise StopAsyncIteration("No more items")


@pytest.fixture
def metrics_config() -> TelemetryConfig:
    """Create metrics configuration."""
    return TelemetryConfig(
        name="test-metrics",
        enabled=True,
        buffer_size=1000,
        flush_interval=60.0,
    )


@pytest_asyncio.fixture
async def metrics_collector(
    metrics_config: TelemetryConfig,
) -> AsyncIterator[MetricsCollector]:
    """Create metrics collector."""
    collector = MetricsCollector()
    collector.config = metrics_config
    await collector.initialize()
    yield collector
    await collector.cleanup()


@pytest.mark.asyncio
async def test_record_metric(metrics_collector: MetricsCollector) -> None:
    """Test recording metrics."""
    await metrics_collector.record(
        name="test_metric",
        value=1.0,
        tags={"test": "true"},
    )

    stats = await metrics_collector.get_stats()
    assert stats["total_metrics"] == 1


@pytest.mark.asyncio
async def test_record_multiple_metrics(metrics_collector: MetricsCollector) -> None:
    """Test recording multiple metrics."""
    for i in range(5):
        await metrics_collector.record(
            name=f"test_metric_{i}",
            value=float(i),
            tags={"test": "true"},
        )

    stats = await metrics_collector.get_stats()
    assert stats["total_metrics"] == 5


@pytest.mark.asyncio
async def test_cleanup(metrics_collector: MetricsCollector) -> None:
    """Test cleanup."""
    await metrics_collector.record(
        name="test_metric",
        value=1.0,
        tags={"test": "true"},
    )

    await metrics_collector.cleanup()
    assert not metrics_collector.is_initialized
