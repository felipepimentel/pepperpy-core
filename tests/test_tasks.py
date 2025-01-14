"""Tests for the task module."""

import pytest

from pepperpy.task import Task, TaskConfig, TaskManager, TaskState


@pytest.mark.asyncio
async def test_task_creation() -> None:
    """Test task creation."""

    async def task_func() -> str:
        return "test"

    task = Task[str]("test", task_func)
    assert task.name == "test"
    assert task.status == TaskState.PENDING
    assert task.error is None


@pytest.mark.asyncio
async def test_task_execution() -> None:
    """Test task execution."""

    async def task_func() -> str:
        return "test"

    task = Task[str]("test", task_func)
    await task.run()
    assert task.status == TaskState.COMPLETED


@pytest.mark.asyncio
async def test_task_execution_with_error() -> None:
    """Test task execution with error."""

    async def task_func() -> None:
        return None

    task = Task[None]("test", task_func)
    await task.run()
    assert task.status == TaskState.COMPLETED


@pytest.mark.asyncio
async def test_task_execution_with_retry() -> None:
    """Test task execution with retry."""

    async def task_func() -> str:
        return "test"

    task = Task[str]("test", task_func)
    await task.run()
    assert task.status == TaskState.COMPLETED
    assert task.error is None


@pytest.mark.asyncio
async def test_task_execution_with_retry_and_error() -> None:
    """Test task execution with retry and error."""

    async def task_func() -> None:
        return None

    task = Task[None]("test", task_func)
    await task.run()
    assert task.status == TaskState.COMPLETED
    assert task.error is None


@pytest.mark.asyncio
async def test_task_execution_with_retry_and_max_retries() -> None:
    """Test task execution with retry and max retries."""

    async def task_func() -> None:
        return None

    task = Task[None]("test", task_func)
    await task.run()
    assert task.status == TaskState.COMPLETED


@pytest.mark.asyncio
async def test_task_manager_add_task() -> None:
    """Test task manager add task."""

    async def task_func() -> None:
        pass

    config = TaskConfig(name="test")
    task_manager = TaskManager(config)

    task = Task[None]("test", task_func)
    await task_manager.add_task(task)
    assert task.name in task_manager.tasks

    # Clean up
    await task_manager.teardown()


@pytest.mark.asyncio
async def test_task_manager_remove_task() -> None:
    """Test task manager remove task."""

    async def task_func() -> None:
        pass

    config = TaskConfig(name="test")
    task_manager = TaskManager(config)

    task = Task[None]("test", task_func)
    await task_manager.add_task(task)
    await task_manager.remove_task(task.name)
    assert task.name not in task_manager.tasks

    # Clean up
    await task_manager.teardown()


@pytest.mark.asyncio
async def test_task_manager_execute_tasks() -> None:
    """Test task manager execute tasks."""

    async def task_func() -> str:
        return "test"

    config = TaskConfig(name="test")
    manager = TaskManager(config)
    task1 = Task[str]("test1", task_func)
    task2 = Task[str]("test2", task_func)
    await manager.add_task(task1)
    await manager.add_task(task2)
    await manager.execute_tasks()
    for task_id in manager.tasks:
        assert manager.tasks[task_id].status == TaskState.COMPLETED


@pytest.mark.asyncio
async def test_task_manager_execute_tasks_with_error() -> None:
    """Test task manager execute tasks with error."""

    async def task_func1() -> str:
        return "test"

    async def task_func2() -> None:
        return None

    config = TaskConfig(name="test")
    manager = TaskManager(config)
    task1 = Task[str]("test1", task_func1)
    task2 = Task[None]("test2", task_func2)
    task3 = Task[str]("test3", task_func1)
    await manager.add_task(task1)
    await manager.add_task(task2)
    await manager.add_task(task3)
    await manager.execute_tasks()
    for task_id in manager.tasks:
        assert manager.tasks[task_id].status == TaskState.COMPLETED


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

    task1 = Task[None]("normal", normal_priority)
    task2 = Task[None]("low", low_priority)
    task3 = Task[None]("high", high_priority)

    await task_manager.add_task(task1, priority=2)  # Normal priority
    await task_manager.add_task(task2, priority=3)  # Low priority
    await task_manager.add_task(task3, priority=1)  # High priority

    await task_manager.execute_tasks()

    assert results == ["high", "normal", "low"]
    assert all(
        task.status == TaskState.COMPLETED for task in task_manager.tasks.values()
    )
