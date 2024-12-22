"""Tests for the pipeline module."""

import pytest
import pytest_asyncio

from pepperpy_core.exceptions import PepperpyError
from pepperpy_core.pipeline import (
    Pipeline,
    PipelineConfig,
    PipelineError,
    PipelineManager,
    PipelineResult,
    PipelineStep,
)


def test_pipeline_config() -> None:
    """Test pipeline configuration."""
    # Test default values
    config = PipelineConfig(name="test")
    config.validate()  # Validate default values
    assert config.name == "test"
    assert config.enabled is True
    assert config.max_concurrent == 10
    assert config.timeout == 60.0
    assert isinstance(config.metadata, dict)
    assert len(config.metadata) == 0

    # Test custom values
    config = PipelineConfig(
        name="test",
        enabled=False,
        max_concurrent=5,
        timeout=30.0,
        metadata={"key": "value"},
    )
    config.validate()  # Validate custom values
    assert config.name == "test"
    assert config.enabled is False
    assert config.max_concurrent == 5
    assert config.timeout == 30.0
    assert config.metadata == {"key": "value"}

    # Test validation
    config = PipelineConfig(name="test", max_concurrent=0)
    with pytest.raises(ValueError):
        config.validate()

    config = PipelineConfig(name="test", timeout=0)
    with pytest.raises(ValueError):
        config.validate()


class TestStep(PipelineStep[str, str]):
    """Test pipeline step."""

    async def execute(self, input_data: str) -> str:
        """Execute test step."""
        return input_data.upper()


class ErrorStep(PipelineStep[str, str]):
    """Test pipeline step that raises an error."""

    async def execute(self, input_data: str) -> str:
        """Execute error step."""
        raise PepperpyError("Test error")


@pytest.mark.asyncio
async def test_pipeline_step() -> None:
    """Test pipeline step."""
    step = TestStep()
    result = await step.execute("hello")
    assert result == "HELLO"

    error_step = ErrorStep()
    with pytest.raises(PepperpyError):
        await error_step.execute("hello")


@pytest.mark.asyncio
async def test_pipeline() -> None:
    """Test pipeline."""
    config = PipelineConfig(name="test")
    pipeline = Pipeline[str, str](config)

    # Test empty pipeline
    result = await pipeline.execute("hello")
    assert isinstance(result, PipelineResult)
    assert result.output == "hello"
    assert result.metadata == {"steps": 0}

    # Test pipeline with one step
    pipeline.add_step(TestStep())
    result = await pipeline.execute("hello")
    assert result.output == "HELLO"
    assert result.metadata == {"steps": 1}

    # Test pipeline with multiple steps
    pipeline.add_step(TestStep())
    result = await pipeline.execute("hello")
    assert result.output == "HELLO"  # Second uppercase has no effect
    assert result.metadata == {"steps": 2}


@pytest_asyncio.fixture
async def pipeline_manager() -> PipelineManager:
    """Create a pipeline manager for testing."""
    manager = PipelineManager()
    await manager.initialize()
    return manager


@pytest.mark.asyncio
async def test_pipeline_manager_init() -> None:
    """Test pipeline manager initialization."""
    manager = PipelineManager()
    assert manager.config.name == "pipeline-manager"
    assert manager.config.enabled is True
    assert manager.config.max_concurrent == 10
    assert manager.config.timeout == 60.0


@pytest.mark.asyncio
async def test_pipeline_manager_stats(pipeline_manager: PipelineManager) -> None:
    """Test pipeline manager statistics."""
    stats = await pipeline_manager.get_stats()
    assert stats["name"] == "pipeline-manager"
    assert stats["enabled"] is True
    assert stats["active_pipelines"] == 0
    assert stats["max_concurrent"] == 10
    assert stats["timeout"] == 60.0


@pytest.mark.asyncio
async def test_pipeline_manager_register(pipeline_manager: PipelineManager) -> None:
    """Test pipeline registration."""
    pipeline = Pipeline[str, str](PipelineConfig(name="test"))
    pipeline_manager.register_pipeline("test", pipeline)

    # Test getting registered pipeline
    assert pipeline_manager.get_pipeline("test") is pipeline

    # Test getting non-existent pipeline
    with pytest.raises(KeyError):
        pipeline_manager.get_pipeline("nonexistent")

    # Test maximum concurrent pipelines
    pipeline_manager.config.max_concurrent = 1
    with pytest.raises(PipelineError):
        pipeline_manager.register_pipeline("test2", pipeline)


@pytest.mark.asyncio
async def test_pipeline_manager_teardown(pipeline_manager: PipelineManager) -> None:
    """Test pipeline manager teardown."""
    pipeline = Pipeline[str, str](PipelineConfig(name="test"))
    pipeline_manager.register_pipeline("test", pipeline)
    assert len(pipeline_manager._active_pipelines) == 1

    await pipeline_manager.teardown()
    assert not pipeline_manager.is_initialized
    assert len(pipeline_manager._active_pipelines) == 0
