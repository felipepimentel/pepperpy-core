"""Test tasks functionality."""

from typing import Any

import pytest
from pepperpy_core.tasks import Task


class MockTask(Task):
    """Mock task for testing."""

    def __init__(self) -> None:
        """Initialize mock task."""
        self.was_run = False

    async def run(self, *args: Any, **kwargs: Any) -> None:
        """Run mock task."""
        self.was_run = True


@pytest.fixture
def mock_task() -> MockTask:
    """Create mock task fixture."""
    return MockTask()


@pytest.mark.asyncio
async def test_task_run(mock_task: MockTask) -> None:
    """Test task run."""
    assert not mock_task.was_run
    await mock_task.run()
    assert mock_task.was_run
