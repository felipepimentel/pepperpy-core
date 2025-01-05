"""Test utils module."""

import asyncio
from typing import AsyncGenerator

import pytest

from pepperpy_core.utils import LoggerMixin, get_logger


@pytest.fixture
async def test_logger() -> AsyncGenerator["TestLogger", None]:
    """Create a test logger."""
    logger = TestLogger()
    yield logger
    await logger.cleanup()


class TestLogger(LoggerMixin):
    """Test logger implementation."""

    async def cleanup(self) -> None:
        """Clean up resources."""
        await asyncio.sleep(0)  # Allow event loop to clean up


def test_get_logger() -> None:
    """Test get logger."""
    logger = get_logger(__name__)
    assert logger is not None
    assert logger.name == __name__


@pytest.mark.asyncio
async def test_logger_mixin(test_logger: TestLogger) -> None:
    """Test logger mixin."""
    assert test_logger.logger is not None
    assert test_logger.logger.name == "TestLogger"
