"""Task implementation module."""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Generic, TypeVar

from .exceptions import PepperpyError
from .module import BaseModule, ModuleConfig


class TaskError(PepperpyError):
    """Task specific error."""

    pass


class TaskStatus(Enum):
    """Task status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    def __str__(self) -> str:
        """Return string representation."""
        return self.value


@dataclass
class TaskConfig(ModuleConfig):
    """Task configuration."""

    # Required fields (inherited from ModuleConfig)
    name: str

    # Optional fields
    enabled: bool = True
    max_workers: int = 4
    queue_size: int = 100
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate configuration."""
        if self.max_workers < 1:
            raise ValueError("max_workers must be greater than 0")
        if self.queue_size < 1:
            raise ValueError("queue_size must be greater than 0")


T = TypeVar("T")


@dataclass
class TaskResult(Generic[T]):
    """Task execution result."""

    task_id: str
    status: TaskStatus
    result: T | None = None
    error: Exception | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class Task:
    """Task implementation."""

    def __init__(
        self,
        name: str,
        func: Callable[..., Any],
        **kwargs: Any,
    ) -> None:
        """Initialize task.

        Args:
            name: Task name
            func: Task function
            **kwargs: Additional task arguments
        """
        self.name = name
        self._func = func
        self._kwargs = kwargs
        self._task: asyncio.Task[Any] | None = None
        self._status = TaskStatus.PENDING
        self._result: Any = None
        self._error: Exception | None = None

    @property
    def is_running(self) -> bool:
        """Check if task is running."""
        return self._status == TaskStatus.RUNNING

    @property
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self._status == TaskStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if task is failed."""
        return self._status == TaskStatus.FAILED

    @property
    def is_cancelled(self) -> bool:
        """Check if task is cancelled."""
        return self._status == TaskStatus.CANCELLED

    async def run(self) -> TaskResult[Any]:
        """Run task.

        Returns:
            Task result

        Raises:
            TaskError: If task fails or is already running
        """
        if self.is_running:
            raise TaskError("Task is already running")

        self._status = TaskStatus.RUNNING
        try:
            self._task = asyncio.create_task(self._func(**self._kwargs))
            self._result = await self._task
            self._status = TaskStatus.COMPLETED
            return TaskResult(
                task_id=self.name,
                status=self._status,
                result=self._result,
                error=self._error,
            )
        except asyncio.CancelledError as e:
            self._error = e
            self._status = TaskStatus.CANCELLED
            raise TaskError(f"Task {self.name} cancelled") from e
        except Exception as e:
            self._error = e
            self._status = TaskStatus.FAILED
            raise TaskError(f"Task {self.name} failed") from e

    async def cancel(self) -> None:
        """Cancel task."""
        if not self.is_running or not self._task:
            return

        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            self._status = TaskStatus.CANCELLED


class TaskQueue:
    """Task queue implementation."""

    def __init__(self, maxsize: int = 0) -> None:
        """Initialize task queue.

        Args:
            maxsize: Maximum queue size
        """
        self._queue: asyncio.Queue[Task] = asyncio.Queue(maxsize=maxsize)
        self._tasks: dict[str, Task] = {}

    async def put(self, task: Task) -> None:
        """Put task in queue.

        Args:
            task: Task to queue
        """
        await self._queue.put(task)
        self._tasks[task.name] = task

    async def get(self) -> Task:
        """Get task from queue.

        Returns:
            Next task
        """
        task = await self._queue.get()
        return task

    def task_done(self) -> None:
        """Mark task as done."""
        self._queue.task_done()

    async def join(self) -> None:
        """Wait for all tasks to complete."""
        await self._queue.join()

    def get_task(self, name: str) -> Task:
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
        self._task: asyncio.Task[Any] | None = None

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
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass

    async def _run(self) -> None:
        """Run worker loop."""
        while self._running:
            task = None
            try:
                task = await self._queue.get()
                try:
                    await task.run()
                except TaskError:
                    # Task failed or was cancelled, continue processing
                    pass
            except asyncio.CancelledError:
                # Worker is being stopped
                if task is not None:
                    self._queue.task_done()
                raise
            except Exception:
                # Log error but continue processing
                pass
            finally:
                if task is not None:
                    self._queue.task_done()


class TaskManager(BaseModule[TaskConfig]):
    """Task manager implementation."""

    def __init__(self) -> None:
        """Initialize task manager."""
        config = TaskConfig(name="task-manager")
        super().__init__(config)
        self._queue: TaskQueue | None = None
        self._workers: list[TaskWorker] = []

    async def _setup(self) -> None:
        """Setup task manager."""
        self._queue = TaskQueue(maxsize=self.config.queue_size)
        self._workers = [
            TaskWorker(self._queue) for _ in range(self.config.max_workers)
        ]
        for worker in self._workers:
            await worker.start()

    async def _teardown(self) -> None:
        """Teardown task manager."""
        for worker in self._workers:
            await worker.stop()
        self._workers.clear()
        self._queue = None

    async def get_stats(self) -> dict[str, Any]:
        """Get task manager statistics.

        Returns:
            Task manager statistics
        """
        self._ensure_initialized()
        return {
            "name": self.config.name,
            "enabled": self.config.enabled,
            "max_workers": self.config.max_workers,
            "active_workers": len(self._workers),
            "queue_size": self.config.queue_size,
        }

    async def create_task(
        self, name: str, func: Callable[..., Any], **kwargs: Any
    ) -> Task:
        """Create a new task.

        Args:
            name: Task name
            func: Task function
            **kwargs: Additional task arguments

        Returns:
            Created task
        """
        self._ensure_initialized()
        if not self._queue:
            raise TaskError("Task manager not initialized")

        task = Task(name=name, func=func, **kwargs)
        await self._queue.put(task)
        return task

    def get_task(self, name: str) -> Task:
        """Get task by name.

        Args:
            name: Task name

        Returns:
            Task instance

        Raises:
            KeyError: If task not found
        """
        self._ensure_initialized()
        if not self._queue:
            raise TaskError("Task manager not initialized")

        return self._queue.get_task(name)


__all__ = [
    "TaskError",
    "TaskStatus",
    "TaskConfig",
    "TaskResult",
    "Task",
    "TaskQueue",
    "TaskWorker",
    "TaskManager",
]
