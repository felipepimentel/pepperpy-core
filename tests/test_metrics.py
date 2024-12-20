"""Test metrics functionality."""

from collections.abc import AsyncGenerator

import pytest
from pepperpy_core.telemetry.config import TelemetryConfig
from pepperpy_core.telemetry.metrics import MetricsCollector


@pytest.fixture
def metrics_config() -> TelemetryConfig:
    """Create metrics configuration."""
    return TelemetryConfig(
        name="test-metrics",
        enabled=True,
        buffer_size=1000,
        flush_interval=60.0,
    )


@pytest.fixture
async def metrics_collector(
    metrics_config: TelemetryConfig,
) -> AsyncGenerator[MetricsCollector, None]:
    """Create metrics collector."""
    collector = MetricsCollector()
    collector.config = metrics_config
    await collector.initialize()
    try:
        yield collector
    finally:
        await collector.cleanup()


@pytest.mark.asyncio
async def test_record_metric(
    metrics_collector: AsyncGenerator[MetricsCollector, None]
) -> None:
    """Test recording metrics."""
    collector = await anext(metrics_collector)
    await collector.collect(
        name="test_metric",
        value=1.0,
        tags={"test": "true"},
    )

    stats = await collector.get_stats()
    assert stats["total_metrics"] == 1


@pytest.mark.asyncio
async def test_record_multiple_metrics(
    metrics_collector: AsyncGenerator[MetricsCollector, None]
) -> None:
    """Test recording multiple metrics."""
    collector = await anext(metrics_collector)
    for i in range(5):
        await collector.collect(
            name=f"test_metric_{i}",
            value=float(i),
            tags={"test": "true"},
        )

    stats = await collector.get_stats()
    assert stats["total_metrics"] == 5


@pytest.mark.asyncio
async def test_cleanup(
    metrics_collector: AsyncGenerator[MetricsCollector, None]
) -> None:
    """Test cleanup."""
    collector = await anext(metrics_collector)
    await collector.collect(
        name="test_metric",
        value=1.0,
        tags={"test": "true"},
    )

    await collector.cleanup()
    assert not collector.is_initialized
