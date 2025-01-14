"""Test task module."""

import asyncio

import pytest

from pepperpy.task import Task, TaskConfig, TaskError, TaskManager, TaskState


async def test_task() -> None:
    """Test task."""
    return "test"


@pytest.mark.asyncio
async def test_task_init() -> None:
    """Test task initialization."""
    task = Task("test", test_task)
    assert task.name == "test"
    assert task.callback == test_task
    assert task.state == TaskState.PENDING


@pytest.mark.asyncio
async def test_task_run() -> None:
    """Test task run."""
    task = Task("test", test_task)
    result = await task.run()
    assert result.task_id == "test"
    assert result.state == TaskState.COMPLETED
    assert result.result == "test"


@pytest.mark.asyncio
async def test_task_cancel() -> None:
    """Test task cancel."""

    async def long_task() -> None:
        await asyncio.sleep(1)

    task = Task("test", long_task)
    with pytest.raises(TaskError):
        run_task = asyncio.create_task(task.run())
        await asyncio.sleep(0.1)  # Let the task start
        await task.cancel()
        await run_task
    assert task.state == TaskState.CANCELLED


@pytest.mark.asyncio
async def test_task_manager_init() -> None:
    """Test task manager initialization."""
    config = TaskConfig(name="test")
    manager = TaskManager(config)
    assert manager.config == config
    assert not manager.is_initialized


@pytest.mark.asyncio
async def test_task_manager_init_with_metadata() -> None:
    """Test task manager initialization with metadata."""
    config = TaskConfig(name="test", metadata={"key": "value"})
    manager = TaskManager(config)
    assert manager.config == config
    assert manager.config.metadata == {"key": "value"}


@pytest.mark.asyncio
async def test_task_manager_setup() -> None:
    """Test task manager setup."""
    config = TaskConfig(name="test")
    manager = TaskManager(config)
    await manager.initialize()
    assert manager.is_initialized


@pytest.mark.asyncio
async def test_task_manager_teardown() -> None:
    """Test task manager teardown."""
    config = TaskConfig(name="test")
    manager = TaskManager(config)
    await manager.initialize()
    await manager.teardown()
    assert not manager.is_initialized


@pytest.mark.asyncio
async def test_task_manager_submit() -> None:
    """Test task manager submit."""
    config = TaskConfig(name="test")
    manager = TaskManager(config)
    await manager.initialize()
    task = Task("test", test_task)
    await manager.submit(task)
    result = await task.run()
    assert result.task_id == "test"
    assert result.state == TaskState.COMPLETED
    assert result.result == "test"


@pytest.mark.asyncio
async def test_task_manager_cancel() -> None:
    """Test task manager cancel."""

    async def long_task() -> None:
        await asyncio.sleep(1)

    config = TaskConfig(name="test")
    manager = TaskManager(config)
    await manager.initialize()
    task = Task("test", long_task)
    await manager.submit(task)
    with pytest.raises(TaskError):
        run_task = asyncio.create_task(task.run())
        await asyncio.sleep(0.1)  # Let the task start
        await manager.cancel(task)
        await run_task
    assert task.state == TaskState.CANCELLED
