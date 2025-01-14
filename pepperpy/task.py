"""Task module."""

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Generic, Optional, TypeVar

from .core import PepperpyError
from .module import BaseModule, ModuleConfig


class TaskError(PepperpyError):
    """Task-related errors."""

    def __init__(
        self,
        message: str,
        cause: Optional[Exception] = None,
        task_id: Optional[str] = None,
    ) -> None:
        """Initialize task error.

        Args:
            message: Error message
            cause: Optional cause of the error
            task_id: Optional ID of the task that caused the error
        """
        super().__init__(message, cause)
        self.task_id = task_id


class TaskState(str, Enum):
    """Task state."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskConfig(ModuleConfig):
    """Task configuration."""

    # Required fields (inherited from ModuleConfig)
    name: str

    # Optional fields
    max_workers: int = 1
    max_queue_size: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate configuration."""
        if self.max_workers < 1:
            raise ValueError("max_workers must be greater than 0")
        if self.max_queue_size < 0:
            raise ValueError("max_queue_size must be greater than or equal to 0")


@dataclass
class TaskResult:
    """Task result."""

    task_id: str
    state: TaskState
    result: Any | None = None


T = TypeVar("T")


class Task(Generic[T]):
    """Task implementation."""

    def __init__(
        self,
        name: str,
        func: Callable[..., Awaitable[T]],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize task.

        Args:
            name: Task name
            func: Task function
            *args: Function arguments
            **kwargs: Function keyword arguments
        """
        self.name = name
        self.callback = func
        self._args = args
        self._kwargs = kwargs
        self._task: asyncio.Task[T] | None = None
        self.state = TaskState.PENDING
        self.result: T | None = None
        self.error: Exception | None = None

    async def run(self, retries: int = 0) -> TaskResult:
        """Run task.

        Args:
            retries: Number of retries on failure

        Returns:
            Task result

        Raises:
            TaskError: If task fails after all retries
        """
        if self.state == TaskState.RUNNING:
            raise TaskError(f"Task {self.name} already running")

        if self.state == TaskState.CANCELLED:
            raise TaskError(f"Task {self.name} was cancelled")

        attempts = 0
        last_error: Exception | None = None

        while attempts <= retries:
            self.state = TaskState.RUNNING
            try:
                coro = self.callback(*self._args, **self._kwargs)
                if not asyncio.iscoroutine(coro):
                    raise TaskError(f"Task {self.name} function must be a coroutine")
                self._task = asyncio.create_task(coro)
                self.result = await self._task
                self.state = TaskState.COMPLETED
                return TaskResult(
                    task_id=self.name, state=self.state, result=self.result
                )
            except asyncio.CancelledError as e:
                self.error = e
                self.state = TaskState.CANCELLED
                raise TaskError(f"Task {self.name} cancelled") from e
            except Exception as e:
                self.error = e
                last_error = e
                self.state = TaskState.FAILED
                if attempts < retries:
                    attempts += 1
                    self.state = TaskState.PENDING
                    continue
                raise TaskError(f"Task {self.name} failed: {e}") from e
            finally:
                self._task = None

        assert last_error is not None  # for type checker
        raise TaskError(
            f"Task {self.name} failed after {retries} retries: {last_error}"
        ) from last_error

    async def cancel(self) -> None:
        """Cancel task."""
        if not self.state == TaskState.RUNNING or not self._task:
            return

        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            self.state = TaskState.CANCELLED
        finally:
            self._task = None


class TaskQueue:
    """Task queue implementation."""

    def __init__(self, maxsize: int = 0) -> None:
        """Initialize task queue.

        Args:
            maxsize: Maximum queue size
        """
        self._queue: asyncio.PriorityQueue[tuple[int, int, Task[Any]]] = (
            asyncio.PriorityQueue(maxsize=maxsize)
        )
        self._tasks: dict[str, Task[Any]] = {}
        self._counter = 0  # Used to maintain FIFO order for tasks with same priority

    async def put(self, task: Task[Any], priority: int = 1) -> None:
        """Put task in queue.

        Args:
            task: Task to queue
            priority: Task priority (higher number means higher priority)
        """
        # Negate priority since PriorityQueue returns lowest values first
        # This way higher priority values will be processed first
        await self._queue.put((-priority, self._counter, task))
        self._counter += 1
        self._tasks[task.name] = task

    async def get(self) -> Task[Any]:
        """Get task from queue.

        Returns:
            Next task
        """
        _, _, task = await self._queue.get()
        return task

    def task_done(self) -> None:
        """Mark task as done."""
        self._queue.task_done()

    async def join(self) -> None:
        """Wait for all tasks to complete."""
        await self._queue.join()

    def get_task(self, name: str) -> Task[Any]:
        """Get task by name.

        Args:
            name: Task name

        Returns:
            Task instance

        Raises:
            KeyError: If task not found
        """
        if name not in self._tasks:
            raise KeyError(f"Task {name} not found")
        return self._tasks[name]


class TaskWorker:
    """Task worker implementation."""

    def __init__(self, queue: TaskQueue) -> None:
        """Initialize task worker.

        Args:
            queue: Task queue
        """
        self._queue = queue
        self._running = False
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """Start worker."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        """Stop worker."""
        if not self._running or not self._task:
            return

        self._running = False
        if not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        self._task = None

    async def _run(self) -> None:
        """Run worker loop."""
        try:
            while True:
                if not self._running:
                    break

                task = await self._queue.get()
                try:
                    await task.run()
                except Exception:
                    # Handle any errors (including TaskError)
                    pass
                finally:
                    self._queue.task_done()
        except asyncio.CancelledError:
            pass


class TaskManager(BaseModule):
    """Task manager implementation."""

    def __init__(self, config: Optional[TaskConfig] = None) -> None:
        """Initialize task manager.

        Args:
            config: Optional task configuration
        """
        super().__init__(config or TaskConfig(name="task_manager"))
        self._queue: Optional[TaskQueue] = None
        self._workers: list[TaskWorker] = []
        self.tasks: dict[str, Task[Any]] = {}

    async def _setup(self) -> None:
        """Set up task manager."""
        if not isinstance(self.config, TaskConfig):
            raise TypeError("Invalid config type")

        self._queue = TaskQueue(maxsize=self.config.max_queue_size)
        self._workers = []
        for _ in range(self.config.max_workers):
            worker = TaskWorker(self._queue)
            self._workers.append(worker)
            await worker.start()

    async def _teardown(self) -> None:
        """Tear down task manager."""
        if not self._queue:
            return

        # Stop all workers
        for worker in self._workers:
            await worker.stop()
        self._workers.clear()

        # Cancel all tasks
        for task in self.tasks.values():
            await task.cancel()
        self.tasks.clear()

        self._queue = None

    async def submit(self, task: Task[Any], priority: int = 1) -> None:
        """Submit task.

        Args:
            task: Task to submit
            priority: Task priority (higher number means higher priority)

        Raises:
            TaskError: If task already exists
        """
        if not self.is_initialized:
            raise TaskError("Task manager not initialized")

        if task.name in self.tasks:
            raise TaskError(f"Task {task.name} already exists")

        assert self._queue is not None  # for type checker
        await self._queue.put(task, priority)
        self.tasks[task.name] = task

    async def cancel(self, task: Task[Any]) -> None:
        """Cancel task.

        Args:
            task: Task to cancel

        Raises:
            TaskError: If task not found
        """
        if not self.is_initialized:
            raise TaskError("Task manager not initialized")

        if task.name not in self.tasks:
            raise TaskError(f"Task {task.name} not found")

        await task.cancel()
        del self.tasks[task.name]

    def get_task(self, name: str) -> Task[Any]:
        """Get task by name.

        Args:
            name: Task name

        Returns:
            Task instance

        Raises:
            TaskError: If task not found
        """
        if not self.initialized:
            raise TaskError("Task manager not initialized")

        if name not in self.tasks:
            raise TaskError(f"Task {name} not found")

        return self.tasks[name]

    def get_stats(self) -> dict[str, Any]:
        """Get task manager statistics.

        Returns:
            Task manager statistics
        """
        stats = super().get_stats()
        stats.update(
            {
                "tasks": len(self.tasks),
                "workers": len(self._workers),
                "queue_size": self._queue.qsize() if self._queue else 0,
            }
        )
        return stats


__all__ = [
    "TaskState",
    "TaskConfig",
    "TaskResult",
    "Task",
    "TaskQueue",
    "TaskWorker",
    "TaskManager",
]
