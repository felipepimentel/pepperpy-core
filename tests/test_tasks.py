"""Test tasks functionality."""

import asyncio
from typing import Any

import pytest

from pepperpy_core.task import (
    Task,
    TaskConfig,
    TaskError,
    TaskQueue,
    TaskResult,
    TaskStatus,
    TaskWorker,
)


def test_task_config() -> None:
    """Test task configuration."""
    # Test default values
    config = TaskConfig(name="test")
    assert config.name == "test"
    assert config.enabled is True
    assert config.max_workers == 4
    assert config.queue_size == 100
    assert isinstance(config.metadata, dict)
    assert len(config.metadata) == 0

    # Test custom values
    config = TaskConfig(
        name="test",
        enabled=False,
        max_workers=2,
        queue_size=50,
        metadata={"key": "value"},
    )
    assert config.name == "test"
    assert config.enabled is False
    assert config.max_workers == 2
    assert config.queue_size == 50
    assert config.metadata == {"key": "value"}

    # Test validation
    config.validate()  # Should not raise

    # Test invalid values
    with pytest.raises(ValueError, match="max_workers must be greater than 0"):
        config = TaskConfig(name="test", max_workers=0)
        config.validate()
    with pytest.raises(ValueError, match="queue_size must be greater than 0"):
        config = TaskConfig(name="test", queue_size=0)
        config.validate()


def test_task_status() -> None:
    """Test task status."""
    assert str(TaskStatus.PENDING) == "pending"
    assert str(TaskStatus.RUNNING) == "running"
    assert str(TaskStatus.COMPLETED) == "completed"
    assert str(TaskStatus.FAILED) == "failed"
    assert str(TaskStatus.CANCELLED) == "cancelled"


def test_task_result() -> None:
    """Test task result."""
    # Test successful result
    result = TaskResult(
        task_id="test",
        status=TaskStatus.COMPLETED,
        result="success",
        metadata={"key": "value"},
    )
    assert result.task_id == "test"
    assert result.status == TaskStatus.COMPLETED
    assert result.result == "success"
    assert result.error is None
    assert result.metadata == {"key": "value"}

    # Test failed result
    error = ValueError("test error")
    result = TaskResult(
        task_id="test",
        status=TaskStatus.FAILED,
        error=error,
    )
    assert result.task_id == "test"
    assert result.status == TaskStatus.FAILED
    assert result.result is None
    assert result.error == error
    assert isinstance(result.metadata, dict)
    assert len(result.metadata) == 0


async def mock_task_func(**kwargs: Any) -> str:
    """Mock task function."""
    await asyncio.sleep(0.1)
    if kwargs.get("fail"):
        raise ValueError("test error")
    if kwargs.get("sleep"):
        await asyncio.sleep(1.0)
    return "success"


@pytest.mark.asyncio
async def test_task() -> None:
    """Test task."""
    # Test successful task
    task = Task("test", mock_task_func)
    assert task.name == "test"
    assert not task.is_running
    assert not task.is_completed
    assert not task.is_failed
    assert not task.is_cancelled

    result = await task.run()
    assert not task.is_running
    assert task.is_completed
    assert not task.is_failed
    assert not task.is_cancelled
    assert result.task_id == "test"
    assert result.status == TaskStatus.COMPLETED
    assert result.result == "success"
    assert result.error is None

    # Test failed task
    task = Task("test", mock_task_func, fail=True)
    with pytest.raises(TaskError, match="Task test failed"):
        await task.run()
    assert not task.is_running
    assert not task.is_completed
    assert task.is_failed
    assert not task.is_cancelled

    # Test running task
    task = Task("test", mock_task_func, sleep=True)
    run_task = asyncio.create_task(task.run())
    await asyncio.sleep(0.2)  # Let the task start
    with pytest.raises(TaskError, match="Task is already running"):
        await task.run()
    await task.cancel()
    with pytest.raises(TaskError):
        await run_task
    assert not task.is_running
    assert not task.is_completed
    assert not task.is_failed
    assert task.is_cancelled


@pytest.mark.asyncio
async def test_task_queue() -> None:
    """Test task queue."""
    queue = TaskQueue(maxsize=2)

    # Test queue operations
    task1 = Task("task1", mock_task_func)
    task2 = Task("task2", mock_task_func)

    await queue.put(task1)
    await queue.put(task2)

    assert queue.get_task("task1") == task1
    assert queue.get_task("task2") == task2
    with pytest.raises(KeyError):
        queue.get_task("nonexistent")

    # Test get and task_done
    task = await queue.get()
    assert task == task1
    queue.task_done()

    task = await queue.get()
    assert task == task2
    queue.task_done()

    # Test join
    await queue.join()  # Should not block since all tasks are done


@pytest.mark.asyncio
async def test_task_worker() -> None:
    """Test task worker."""
    queue = TaskQueue()
    worker = TaskWorker(queue)

    # Test worker lifecycle
    await worker.start()
    assert worker._running
    await worker.start()  # Should be idempotent
    assert worker._running

    # Test task processing
    task1 = Task("task1", mock_task_func)
    task2 = Task("task2", mock_task_func, fail=True)
    await queue.put(task1)
    await queue.put(task2)

    await asyncio.sleep(0.3)  # Let the worker process tasks
    assert task1.is_completed
    assert task2.is_failed

    # Test worker shutdown
    await worker.stop()
    assert not worker._running
    await worker.stop()  # Should be idempotent
    assert not worker._running
