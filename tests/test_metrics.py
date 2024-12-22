"""Tests for the metrics module."""

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio

from pepperpy_core.module import ModuleError
from pepperpy_core.telemetry import MetricsCollector, TelemetryConfig


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
    await collector.teardown()


@pytest.mark.asyncio
async def test_record_metric(metrics_collector: MetricsCollector) -> None:
    """Test recording a metric."""
    await metrics_collector.record(
        name="test_metric",
        value=1.0,
        tags={"test": "true"},
    )

    stats = await metrics_collector.get_stats()
    assert stats["metrics_count"] == 1


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
    assert stats["metrics_count"] == 5


@pytest.mark.asyncio
async def test_buffer_overflow(metrics_collector: MetricsCollector) -> None:
    """Test buffer overflow handling."""
    metrics_collector.config.buffer_size = 2

    # Record more metrics than buffer size
    for i in range(5):
        await metrics_collector.record(
            name=f"test_metric_{i}",
            value=float(i),
            tags={"test": "true"},
        )

    stats = await metrics_collector.get_stats()
    assert stats["metrics_count"] <= 2  # Should have flushed


@pytest.mark.asyncio
async def test_disabled_collector(metrics_collector: MetricsCollector) -> None:
    """Test disabled metrics collector."""
    metrics_collector.config.enabled = False

    await metrics_collector.record(
        name="test_metric",
        value=1.0,
        tags={"test": "true"},
    )

    stats = await metrics_collector.get_stats()
    assert stats["metrics_count"] == 0


@pytest.mark.asyncio
async def test_metrics_with_metadata(metrics_collector: MetricsCollector) -> None:
    """Test metrics with metadata."""
    await metrics_collector.record(
        name="test_metric",
        value=1.0,
        tags={"test": "true"},
        metadata={"source": "test", "timestamp": 123},
    )

    stats = await metrics_collector.get_stats()
    assert stats["metrics_count"] == 1


@pytest.mark.asyncio
async def test_metrics_validation() -> None:
    """Test metrics configuration validation."""
    # Test invalid buffer size
    with pytest.raises(ValueError, match="Buffer size must be positive"):
        TelemetryConfig(name="test", buffer_size=0)

    # Test invalid flush interval
    with pytest.raises(ValueError, match="Flush interval must be positive"):
        TelemetryConfig(name="test", flush_interval=0)


@pytest.mark.asyncio
async def test_metrics_uninitialized() -> None:
    """Test metrics operations when uninitialized."""
    collector = MetricsCollector()

    with pytest.raises(ModuleError):
        await collector.record(
            name="test_metric",
            value=1.0,
            tags={"test": "true"},
        )

    with pytest.raises(ModuleError):
        await collector.get_stats()


@pytest.mark.asyncio
async def test_metrics_reinitialization(metrics_collector: MetricsCollector) -> None:
    """Test metrics reinitialization."""
    await metrics_collector.teardown()
    assert not metrics_collector.is_initialized

    await metrics_collector.initialize()
    assert metrics_collector.is_initialized


@pytest.mark.asyncio
async def test_metrics_stats(metrics_collector: MetricsCollector) -> None:
    """Test metrics statistics."""
    # Initial stats
    stats = await metrics_collector.get_stats()
    assert stats["name"] == "test-metrics"
    assert stats["enabled"] is True
    assert stats["buffer_size"] == 1000
    assert stats["flush_interval"] == 60.0
    assert stats["metrics_count"] == 0
    assert stats["is_flushing"] is True

    # Record some metrics
    for i in range(5):
        await metrics_collector.record(
            name=f"test_metric_{i}",
            value=float(i),
            tags={"test": "true"},
        )

    # Check updated stats
    stats = await metrics_collector.get_stats()
    assert stats["metrics_count"] == 5
