"""Test task module."""

import asyncio

import pytest

from pepperpy.task import Task, TaskConfig, TaskError, TaskManager, TaskState


@pytest.mark.asyncio
async def test_task_creation() -> None:
    """Test task creation."""

    async def task_func() -> None:
        pass

    task = Task[None]("test", task_func)
    assert task.name == "test"
    assert task.callback == task_func
    assert task.state == TaskState.PENDING


@pytest.mark.asyncio
async def test_task_execution() -> None:
    """Test task execution."""

    async def task_func() -> str:
        return "test"

    task = Task[str]("test", task_func)
    result = await task.run()
    assert result.result == "test"
    assert task.state == TaskState.COMPLETED


@pytest.mark.asyncio
async def test_task_execution_with_error() -> None:
    """Test task execution with error."""

    async def task_func() -> None:
        raise ValueError("test")

    task = Task[None]("test", task_func)
    with pytest.raises(TaskError) as exc_info:
        await task.run()
    assert task.state == TaskState.FAILED
    assert str(exc_info.value) == "Task test failed: test"


@pytest.mark.asyncio
async def test_task_execution_with_retry() -> None:
    """Test task execution with retry."""
    attempts = 0

    async def task_func() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("test")
        return "test"

    task = Task[str]("test", task_func)
    result = await task.run(retries=3)
    assert result.result == "test"
    assert task.state == TaskState.COMPLETED
    assert attempts == 3


@pytest.mark.asyncio
async def test_task_execution_with_retry_and_error() -> None:
    """Test task execution with retry and error."""
    attempts = 0

    async def task_func() -> None:
        nonlocal attempts
        attempts += 1
        raise ValueError("test")

    task = Task[None]("test", task_func)
    with pytest.raises(TaskError) as exc_info:
        await task.run(retries=3)
    assert task.state == TaskState.FAILED
    assert attempts == 4
    assert str(exc_info.value) == "Task test failed: test"


@pytest.mark.asyncio
async def test_task_execution_with_retry_and_max_retries() -> None:
    """Test task execution with retry and max retries."""
    attempts = 0

    async def task_func() -> None:
        nonlocal attempts
        attempts += 1
        raise ValueError("test")

    task = Task[None]("test", task_func)
    with pytest.raises(TaskError) as exc_info:
        await task.run(retries=3)
    assert task.state == TaskState.FAILED
    assert attempts == 4
    assert str(exc_info.value) == "Task test failed: test"


@pytest.mark.asyncio
async def test_task_manager_submit() -> None:
    """Test task manager submit."""

    async def task_func() -> None:
        pass

    config = TaskConfig(name="test")
    task_manager = TaskManager(config)
    await task_manager.initialize()

    task = Task[None]("test", task_func)
    await task_manager.submit(task)
    assert task.name in task_manager.tasks


@pytest.mark.asyncio
async def test_task_manager_cancel() -> None:
    """Test task manager cancel."""

    async def task_func() -> None:
        pass

    config = TaskConfig(name="test")
    task_manager = TaskManager(config)
    await task_manager.initialize()

    task = Task[None]("test", task_func)
    await task_manager.submit(task)
    await task_manager.cancel(task)
    assert task.name not in task_manager.tasks


@pytest.mark.asyncio
async def test_task_manager_execute_tasks() -> None:
    """Test task manager execute tasks."""

    async def task_func() -> str:
        return "test"

    config = TaskConfig(name="test")
    manager = TaskManager(config)
    await manager.initialize()

    task1 = Task[str]("test1", task_func)
    task2 = Task[str]("test2", task_func)
    await manager.submit(task1)
    await manager.submit(task2)

    # Wait for tasks to complete
    await asyncio.sleep(0.1)

    assert task1.state == TaskState.COMPLETED
    assert task2.state == TaskState.COMPLETED

    await manager.teardown()


@pytest.mark.asyncio
async def test_task_manager_execute_tasks_with_error() -> None:
    """Test task manager execute tasks with error."""

    async def task_func1() -> str:
        return "test"

    async def task_func2() -> None:
        raise ValueError("test")

    config = TaskConfig(name="test")
    manager = TaskManager(config)
    await manager.initialize()

    task1 = Task[str]("test1", task_func1)
    task2 = Task[None]("test2", task_func2)
    task3 = Task[str]("test3", task_func1)
    await manager.submit(task1)
    await manager.submit(task2)
    await manager.submit(task3)

    # Wait for tasks to complete
    await asyncio.sleep(0.1)

    assert task1.state == TaskState.COMPLETED
    assert task2.state == TaskState.FAILED
    assert task3.state == TaskState.COMPLETED

    await manager.teardown()


@pytest.mark.asyncio
async def test_task_manager_execute_tasks_with_priority() -> None:
    """Test task manager execute tasks with priority."""
    results: list[str] = []

    async def high_priority() -> None:
        results.append("high")

    async def normal_priority() -> None:
        results.append("normal")

    async def low_priority() -> None:
        results.append("low")

    config = TaskConfig(name="test")
    task_manager = TaskManager(config)
    await task_manager.initialize()

    task1 = Task[None]("normal", normal_priority)
    task2 = Task[None]("low", low_priority)
    task3 = Task[None]("high", high_priority)

    await task_manager.submit(task1, priority=2)  # Normal priority
    await task_manager.submit(task2, priority=1)  # Low priority
    await task_manager.submit(task3, priority=3)  # High priority

    # Wait for tasks to complete
    await asyncio.sleep(0.1)

    assert task1.state == TaskState.COMPLETED
    assert task2.state == TaskState.COMPLETED
    assert task3.state == TaskState.COMPLETED
    assert results == ["high", "normal", "low"]

    await task_manager.teardown()
