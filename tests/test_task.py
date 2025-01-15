"""Test task module."""

import asyncio

import pytest

from pepperpy.task import (
    Task,
    TaskConfig,
    TaskError,
    TaskManager,
    TaskQueue,
    TaskState,
    TaskWorker,
)


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
async def test_task_run_with_retries() -> None:
    """Test task run with retries."""
    attempts = 0

    async def failing_task() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("test error")
        return "success"

    task = Task("test", failing_task)
    result = await task.run(retries=2)
    assert result.task_id == "test"
    assert result.state == TaskState.COMPLETED
    assert result.result == "success"
    assert attempts == 3


@pytest.mark.asyncio
async def test_task_run_with_retries_failure() -> None:
    """Test task run with retries that ultimately fails."""
    attempts = 0

    async def failing_task() -> None:
        nonlocal attempts
        attempts += 1
        raise ValueError("test error")

    task = Task("test", failing_task)
    with pytest.raises(TaskError) as exc_info:
        await task.run(retries=2)
    assert "test error" in str(exc_info.value)
    assert attempts == 3
    assert task.state == TaskState.FAILED


@pytest.mark.asyncio
async def test_task_run_invalid_coroutine() -> None:
    """Test task run with invalid coroutine."""

    def sync_task() -> str:
        return "test"

    task = Task("test", sync_task)  # type: ignore
    with pytest.raises(TaskError) as exc_info:
        await task.run()
    assert "Task test function must be a coroutine" in str(exc_info.value)


@pytest.mark.asyncio
async def test_task_run_already_running() -> None:
    """Test task run when already running."""

    async def long_task() -> None:
        await asyncio.sleep(1)

    task = Task("test", long_task)
    run_task = asyncio.create_task(task.run())
    await asyncio.sleep(0.1)  # Let the task start

    with pytest.raises(TaskError) as exc_info:
        await task.run()
    assert "Task test already running" in str(exc_info.value)

    await task.cancel()
    try:
        await run_task
    except TaskError:
        pass


@pytest.mark.asyncio
async def test_task_run_cancelled() -> None:
    """Test task run when cancelled."""
    task = Task("test", test_task)
    task.state = TaskState.CANCELLED
    with pytest.raises(TaskError) as exc_info:
        await task.run()
    assert "Task test was cancelled" in str(exc_info.value)


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
async def test_task_cancel_not_running() -> None:
    """Test task cancel when not running."""
    task = Task("test", test_task)
    await task.cancel()  # Should not raise
    assert task.state == TaskState.PENDING


@pytest.mark.asyncio
async def test_task_queue_operations() -> None:
    """Test task queue operations."""
    queue = TaskQueue(maxsize=2)
    task1 = Task("task1", test_task)
    task2 = Task("task2", test_task)

    # Test put with different priorities
    await queue.put(task1, priority=1)
    await queue.put(task2, priority=2)

    # Higher priority task should be retrieved first
    retrieved_task = await queue.get()
    assert retrieved_task.name == "task2"
    queue.task_done()

    retrieved_task = await queue.get()
    assert retrieved_task.name == "task1"
    queue.task_done()

    await queue.join()  # Should complete immediately since all tasks are done


@pytest.mark.asyncio
async def test_task_queue_get_task() -> None:
    """Test task queue get_task operation."""
    queue = TaskQueue()
    task = Task("test", test_task)
    await queue.put(task)

    assert queue.get_task("test") == task
    with pytest.raises(KeyError):
        queue.get_task("nonexistent")


@pytest.mark.asyncio
async def test_task_worker() -> None:
    """Test task worker."""
    queue = TaskQueue()
    worker = TaskWorker(queue)

    # Start worker
    await worker.start()
    assert worker._running

    # Starting again should be no-op
    await worker.start()
    assert worker._running

    # Stop worker
    await worker.stop()
    assert not worker._running

    # Stopping again should be no-op
    await worker.stop()
    assert not worker._running


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
async def test_task_manager_submit_not_initialized() -> None:
    """Test task manager submit when not initialized."""
    config = TaskConfig(name="test")
    manager = TaskManager(config)
    task = Task("test", test_task)
    with pytest.raises(TaskError) as exc_info:
        await manager.submit(task)
    assert "Task manager not initialized" in str(exc_info.value)


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


@pytest.mark.asyncio
async def test_task_manager_cancel_not_initialized() -> None:
    """Test task manager cancel when not initialized."""
    config = TaskConfig(name="test")
    manager = TaskManager(config)
    task = Task("test", test_task)
    with pytest.raises(TaskError) as exc_info:
        await manager.cancel(task)
    assert "Task manager not initialized" in str(exc_info.value)


def test_task_config() -> None:
    """Test task configuration."""
    # Valid configurations
    config = TaskConfig(name="test", max_workers=1, max_queue_size=0)
    assert config.name == "test"
    assert config.max_workers == 1
    assert config.max_queue_size == 0
    assert config.metadata == {}
