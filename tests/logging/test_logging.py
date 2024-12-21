"""Test logging functionality."""

from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Protocol, TypeVar

import pytest
import pytest_asyncio

from pepperpy_core.module import BaseModule
from pepperpy_core.types import BaseConfigData

T = TypeVar("T")


async def async_next(agen: AsyncGenerator[T, None]) -> T:
    """Get next value from async generator."""
    try:
        return await agen.__anext__()
    except StopAsyncIteration:
        raise StopAsyncIteration("No more items")


@dataclass
class LogConfig(BaseConfigData):
    """Log configuration."""

    name: str
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


class LogManagerProtocol(Protocol):
    """Log manager protocol."""

    async def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        ...

    async def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        ...

    async def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        ...

    async def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        ...


class BaseLogManager(BaseModule[LogConfig]):
    """Base log manager implementation."""

    config: LogConfig


class MockLogManager(BaseLogManager):
    """Mock log manager for testing."""

    def __init__(self, config: LogConfig) -> None:
        """Initialize mock log manager."""
        super().__init__(config)
        self.logs: list[str] = []
        self.metadata: list[dict[str, Any]] = []

    async def _setup(self) -> None:
        """Setup mock log manager."""
        self.logs = []
        self.metadata = []

    async def _teardown(self) -> None:
        """Teardown mock log manager."""
        self.logs.clear()
        self.metadata.clear()

    async def get_stats(self) -> dict[str, Any]:
        """Get log manager statistics."""
        return {
            "name": self.config.name,
            "logs": len(self.logs),
            "metadata": len(self.metadata),
        }

    async def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self.logs.append(f"DEBUG: {message}")
        self.metadata.append(kwargs)

    async def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self.logs.append(f"INFO: {message}")
        self.metadata.append(kwargs)

    async def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self.logs.append(f"WARNING: {message}")
        self.metadata.append(kwargs)

    async def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self.logs.append(f"ERROR: {message}")
        self.metadata.append(kwargs)


@pytest.fixture
def log_config() -> LogConfig:
    """Create test log config."""
    return LogConfig(name="test")


@pytest_asyncio.fixture
async def log_manager(log_config: LogConfig) -> AsyncIterator[MockLogManager]:
    """Create test log manager."""
    manager = MockLogManager(config=log_config)
    await manager.initialize()
    yield manager
    await manager.cleanup()


@pytest.mark.asyncio
async def test_log_manager_levels(log_manager: MockLogManager) -> None:
    """Test log manager levels."""
    await log_manager.debug("Debug message")
    await log_manager.info("Info message")
    await log_manager.warning("Warning message")
    await log_manager.error("Error message")

    assert len(log_manager.logs) == 4
    assert log_manager.logs[0] == "DEBUG: Debug message"
    assert log_manager.logs[1] == "INFO: Info message"
    assert log_manager.logs[2] == "WARNING: Warning message"
    assert log_manager.logs[3] == "ERROR: Error message"


@pytest.mark.asyncio
async def test_log_manager_metadata(log_manager: MockLogManager) -> None:
    """Test log manager metadata."""
    await log_manager.info("Test message", user="test_user", action="test_action")

    assert len(log_manager.metadata) == 1
    assert log_manager.metadata[0] == {"user": "test_user", "action": "test_action"}
