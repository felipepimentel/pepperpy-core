"""Test logging module."""

import pytest

from pepperpy_core.logging import (
    BaseHandler,
    HandlerConfig,
    Logger,
    LogLevel,
    LogRecord,
)


@pytest.fixture
def test_handler() -> "TestHandler":
    """Create a test handler."""
    return TestHandler(HandlerConfig(level=LogLevel.DEBUG))


class TestHandler(BaseHandler):
    """Test handler implementation."""

    def __init__(self, config: HandlerConfig) -> None:
        """Initialize handler."""
        super().__init__(config)
        self.messages: list[str] = []

    def handle(self, message: str) -> None:
        """Handle message."""
        self.messages.append(message)

    def emit(self, record: "LogRecord") -> None:
        """Emit log record."""
        self.handle(record.message)


def test_logger_debug(test_handler: TestHandler) -> None:
    """Test logger debug."""
    logger = Logger("test_debug")
    logger.add_handler(test_handler)
    logger.debug("test")
    assert test_handler.messages == ["test"]


def test_logger_info(test_handler: TestHandler) -> None:
    """Test logger info."""
    logger = Logger("test_info")
    logger.add_handler(test_handler)
    logger.info("test")
    assert test_handler.messages == ["test"]


def test_logger_warning(test_handler: TestHandler) -> None:
    """Test logger warning."""
    logger = Logger("test_warning")
    logger.add_handler(test_handler)
    logger.warning("test")
    assert test_handler.messages == ["test"]


def test_logger_error(test_handler: TestHandler) -> None:
    """Test logger error."""
    logger = Logger("test_error")
    logger.add_handler(test_handler)
    logger.error("test")
    assert test_handler.messages == ["test"]


def test_logger_critical(test_handler: TestHandler) -> None:
    """Test logger critical."""
    logger = Logger("test_critical")
    logger.add_handler(test_handler)
    logger.critical("test")
    assert test_handler.messages == ["test"]


def test_logger_multiple_handlers(test_handler: TestHandler) -> None:
    """Test logger multiple handlers."""
    logger = Logger("test_multiple")
    handler1 = test_handler
    handler2 = TestHandler(HandlerConfig(level=LogLevel.DEBUG))
    logger.add_handler(handler1)
    logger.add_handler(handler2)
    logger.debug("test")
    assert handler1.messages == ["test"]
    assert handler2.messages == ["test"]


def test_logger_remove_handler(test_handler: TestHandler) -> None:
    """Test logger remove handler."""
    logger = Logger("test_remove")
    logger.add_handler(test_handler)
    logger.remove_handler(test_handler)
    logger.debug("test")
    assert test_handler.messages == []


def test_logger_clear_handlers(test_handler: TestHandler) -> None:
    """Test logger clear handlers."""
    logger = Logger("test_clear")
    logger.add_handler(test_handler)
    for handler in logger._handlers:
        logger.remove_handler(handler)
    logger.debug("test")
    assert test_handler.messages == []
