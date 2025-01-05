"""Test logging module."""

from typing import Any, AsyncGenerator

import pytest

from pepperpy_core.logging import BaseHandler, HandlerConfig, LoggingManager, LogLevel


class TestHandler(BaseHandler):
    """Test handler."""

    def __init__(self) -> None:
        """Initialize test handler."""
        super().__init__(HandlerConfig())
        self.messages: list[tuple[LogLevel, str, dict[str, Any]]] = []

    def emit(self, record: Any) -> None:
        """Handle log message.

        Args:
            record: Log record
        """
        self.messages.append((record.level, record.message, record.metadata))


@pytest.fixture
async def logging_manager() -> AsyncGenerator[LoggingManager, None]:
    """Get logging manager."""
    manager = LoggingManager()
    await manager.initialize()
    yield manager
    await manager._teardown()


@pytest.mark.asyncio
async def test_logging_manager_logger(logging_manager: LoggingManager) -> None:
    """Test logging manager logger."""
    logger = logging_manager._loggers.get("test")
    assert logger is None

    logger = logging_manager.get_logger("test")
    assert logger is not None
    assert logger.name == "test"


@pytest.mark.asyncio
async def test_logging_manager_logger_handlers(logging_manager: LoggingManager) -> None:
    """Test logging manager logger handlers."""
    logger = logging_manager.get_logger("test")
    handler = TestHandler()
    logger.add_handler(handler)
    assert handler in logger._handlers

    logger.remove_handler(handler)
    assert handler not in logger._handlers


@pytest.mark.asyncio
async def test_logging_manager_logger_log(logging_manager: LoggingManager) -> None:
    """Test logging manager logger log."""
    logger = logging_manager.get_logger("test")
    handler = TestHandler()
    logger.add_handler(handler)
    logger.log(LogLevel.INFO, "test")
    assert len(handler.messages) == 1
    assert handler.messages[0][0] == LogLevel.INFO
    assert handler.messages[0][1] == "test"


@pytest.mark.asyncio
async def test_logging_manager_logger_debug(logging_manager: LoggingManager) -> None:
    """Test logging manager logger debug."""
    logger = logging_manager.get_logger("test")
    handler = TestHandler()
    logger.add_handler(handler)
    logger.debug("test")
    assert len(handler.messages) == 1
    assert handler.messages[0][0] == LogLevel.DEBUG
    assert handler.messages[0][1] == "test"


@pytest.mark.asyncio
async def test_logging_manager_logger_info(logging_manager: LoggingManager) -> None:
    """Test logging manager logger info."""
    logger = logging_manager.get_logger("test")
    handler = TestHandler()
    logger.add_handler(handler)
    logger.info("test")
    assert len(handler.messages) == 1
    assert handler.messages[0][0] == LogLevel.INFO
    assert handler.messages[0][1] == "test"


@pytest.mark.asyncio
async def test_logging_manager_logger_warning(logging_manager: LoggingManager) -> None:
    """Test logging manager logger warning."""
    logger = logging_manager.get_logger("test")
    handler = TestHandler()
    logger.add_handler(handler)
    logger.warning("test")
    assert len(handler.messages) == 1
    assert handler.messages[0][0] == LogLevel.WARNING
    assert handler.messages[0][1] == "test"


@pytest.mark.asyncio
async def test_logging_manager_logger_error(logging_manager: LoggingManager) -> None:
    """Test logging manager logger error."""
    logger = logging_manager.get_logger("test")
    handler = TestHandler()
    logger.add_handler(handler)
    logger.error("test")
    assert len(handler.messages) == 1
    assert handler.messages[0][0] == LogLevel.ERROR
    assert handler.messages[0][1] == "test"


@pytest.mark.asyncio
async def test_logging_manager_logger_critical(logging_manager: LoggingManager) -> None:
    """Test logging manager logger critical."""
    logger = logging_manager.get_logger("test")
    handler = TestHandler()
    logger.add_handler(handler)
    logger.critical("test")
    assert len(handler.messages) == 1
    assert handler.messages[0][0] == LogLevel.CRITICAL
    assert handler.messages[0][1] == "test"
