"""Task module."""

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Generic, TypeVar

from pepperpy_core.exceptions import TaskError
from pepperpy_core.module import BaseModule, ModuleConfig


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
    status: TaskState
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
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._task: asyncio.Task[T] | None = None
        self.status = TaskState.PENDING
        self.result: T | None = None
        self.error: Exception | None = None

    async def run(self) -> TaskResult:
        """Run task.

        Returns:
            Task result

        Raises:
            TaskError: If task fails
        """
        if self.status == TaskState.RUNNING:
            raise TaskError(f"Task {self.name} already running")

        self.status = TaskState.RUNNING
        try:
            coro = self._func(*self._args, **self._kwargs)
            if not asyncio.iscoroutine(coro):
                raise TaskError(f"Task {self.name} function must be a coroutine")
            self._task = asyncio.create_task(coro)
            self.result = await self._task
            self.status = TaskState.COMPLETED
            return TaskResult(
                task_id=self.name,
                status=self.status,
                result=self.result,
            )
        except asyncio.CancelledError as e:
            self.error = Exception(str(e))
            self.status = TaskState.CANCELLED
            raise TaskError(f"Task {self.name} cancelled") from e
        except Exception as e:
            self.error = e
            self.status = TaskState.FAILED
            raise TaskError(f"Task {self.name} failed: {e}") from e
        finally:
            self._task = None

    async def cancel(self) -> None:
        """Cancel task."""
        if not self.status == TaskState.RUNNING or not self._task:
            return

        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            self.status = TaskState.CANCELLED
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
        # Invert priority since PriorityQueue returns lowest values first
        await self._queue.put((priority, self._counter, task))
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


class TaskManager(BaseModule[TaskConfig]):
    """Task manager implementation."""

    def __init__(self, config: TaskConfig) -> None:
        """Initialize task manager.

        Args:
            config: Task manager configuration
        """
        super().__init__(config)
        self._queue: TaskQueue = TaskQueue(maxsize=config.max_queue_size)
        self._workers: list[TaskWorker] = []
        self._tasks: dict[str, Task[Any]] = {}

    async def _setup(self) -> None:
        """Set up task manager."""
        # Only create one worker to ensure tasks are executed in order
        worker = TaskWorker(self._queue)
        await worker.start()
        self._workers.append(worker)

    async def _teardown(self) -> None:
        """Tear down task manager."""
        if self._workers:
            await asyncio.gather(*(worker.stop() for worker in self._workers))
            self._workers.clear()
        # Create a new queue to ensure type safety
        self._queue = TaskQueue(maxsize=self.config.max_queue_size)

    async def add_task(self, task: Task[Any], priority: int = 1) -> None:
        """Add task to manager.

        Args:
            task: Task to add
            priority: Task priority (lower number means higher priority)

        Raises:
            TaskError: If task already exists
        """
        if not self.is_initialized:
            await self.initialize()

        if task.name in self._tasks:
            raise TaskError(f"Task {task.name} already exists")

        self._tasks[task.name] = task
        await self._queue.put(task, priority=priority)

    async def remove_task(self, task_name: str) -> None:
        """Remove task from manager.

        Args:
            task_name: Task name

        Raises:
            TaskError: If task not found
        """
        if task_name not in self._tasks:
            raise TaskError(f"Task {task_name} not found")

        task = self._tasks[task_name]
        await task.cancel()
        del self._tasks[task_name]

    async def execute_tasks(self) -> None:
        """Execute all tasks."""
        if not self.is_initialized:
            await self.initialize()

        # Wait for the queue to be processed completely
        await self._queue.join()

    @property
    def tasks(self) -> dict[str, Task[Any]]:
        """Return tasks.

        Returns:
            Tasks dictionary
        """
        return self._tasks


__all__ = [
    "TaskState",
    "TaskConfig",
    "TaskResult",
    "Task",
    "TaskQueue",
    "TaskWorker",
    "TaskManager",
]
