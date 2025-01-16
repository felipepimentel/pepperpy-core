"""Task module."""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Awaitable, Callable, Dict, Generic, Optional, TypeVar

from pepperpy.core import PepperpyError
from pepperpy.module import BaseModule, ModuleConfig


class TaskError(PepperpyError):
    """Task error."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, details, cause)


class TaskState(Enum):
    """Task state."""

    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


T = TypeVar("T")


@dataclass
class TaskResult(Generic[T]):
    """Task result."""

    task_id: str
    state: TaskState
    result: Optional[T] = None
    error: Optional[Exception] = None


@dataclass
class TaskConfig(ModuleConfig):
    """Task configuration."""

    name: str = "task_manager"
    metadata: Dict[str, Any] = field(default_factory=dict)


class Task(Generic[T]):
    """Task."""

    def __init__(
        self,
        task_id: str,
        callback: Callable[[], Awaitable[T]],
    ) -> None:
        """Initialize task.

        Args:
            task_id: Task ID
            callback: Task callback
        """
        self.task_id = task_id
        self._callback = callback
        self._state = TaskState.PENDING
        self._result: Optional[TaskResult[T]] = None

    @property
    def state(self) -> TaskState:
        """Get task state.

        Returns:
            Task state
        """
        return self._state

    @property
    def result(self) -> Optional[TaskResult[T]]:
        """Get task result.

        Returns:
            Task result
        """
        return self._result

    async def run(self) -> TaskResult[T]:
        """Run task.

        Returns:
            Task result

        Raises:
            TaskError: If task is already running or cancelled
        """
        if self._state == TaskState.RUNNING:
            raise TaskError(
                "Task is already running",
                {"task_id": self.task_id},
            )
        if self._state == TaskState.CANCELLED:
            raise TaskError(
                "Task is cancelled",
                {"task_id": self.task_id},
            )

        self._state = TaskState.RUNNING
        try:
            result = await self._callback()
            self._state = TaskState.COMPLETED
            self._result = TaskResult(
                task_id=self.task_id,
                state=self._state,
                result=result,
            )
        except Exception as e:
            self._state = TaskState.FAILED
            self._result = TaskResult(
                task_id=self.task_id,
                state=self._state,
                error=e,
            )
            raise TaskError(
                "Task failed",
                {"task_id": self.task_id},
                e,
            ) from e
        return self._result

    def cancel(self) -> None:
        """Cancel task.

        Raises:
            TaskError: If task is already completed or failed
        """
        if self._state in (TaskState.COMPLETED, TaskState.FAILED):
            raise TaskError(
                "Task is already completed or failed",
                {"task_id": self.task_id},
            )
        self._state = TaskState.CANCELLED
        self._result = TaskResult(
            task_id=self.task_id,
            state=self._state,
        )


class TaskManager(BaseModule[TaskConfig]):
    """Task manager."""

    def __init__(self, config: Optional[TaskConfig] = None) -> None:
        """Initialize task manager.

        Args:
            config: Task configuration
        """
        super().__init__(config or TaskConfig())
        self._tasks: Dict[str, Task[Any]] = {}

    def _ensure_initialized(self) -> None:
        """Ensure manager is initialized.

        Raises:
            TaskError: If manager is not initialized
        """
        if not self.is_initialized:
            raise TaskError(
                "Task manager is not initialized",
                {"manager_name": self.config.name},
            )

    async def _setup(self) -> None:
        """Set up task manager."""
        self._tasks = {}

    async def _teardown(self) -> None:
        """Clean up task manager."""
        self._tasks = {}

    def submit(self, task_id: str, callback: Callable[[], Awaitable[T]]) -> Task[T]:
        """Submit task.

        Args:
            task_id: Task ID
            callback: Task callback

        Returns:
            Task instance

        Raises:
            TaskError: If task cannot be submitted
        """
        self._ensure_initialized()
        if task_id in self._tasks:
            raise TaskError(
                "Task already exists",
                {"task_id": task_id, "manager_name": self.config.name},
            )
        task = Task(task_id, callback)
        self._tasks[task_id] = task
        return task

    def get(self, task_id: str) -> Task[Any]:
        """Get task.

        Args:
            task_id: Task ID

        Returns:
            Task instance

        Raises:
            TaskError: If task is not found
        """
        self._ensure_initialized()
        if task_id not in self._tasks:
            raise TaskError(
                "Task not found",
                {"task_id": task_id, "manager_name": self.config.name},
            )
        return self._tasks[task_id]

    def cancel(self, task_id: str) -> None:
        """Cancel task.

        Args:
            task_id: Task ID

        Raises:
            TaskError: If task cannot be cancelled
        """
        self._ensure_initialized()
        task = self.get(task_id)
        task.cancel()


__all__ = ["Task", "TaskConfig", "TaskError", "TaskManager", "TaskResult", "TaskState"]
