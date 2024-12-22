"""Tests for the logging module."""

import io

import pytest
import pytest_asyncio

from pepperpy_core.logging import (
    HandlerConfig,
    Logger,
    LoggingConfig,
    LoggingManager,
    LogLevel,
    LogRecord,
    StreamHandler,
)


@pytest.fixture
def log_record() -> LogRecord:
    """Create a log record for testing."""
    return LogRecord(
        level=LogLevel.INFO,
        message="Test message",
        logger_name="test_logger",
        module="test_module",
        function="test_function",
        line=42,
        metadata={"extra": "data"},
    )


@pytest.fixture
def string_io() -> io.StringIO:
    """Create a string IO for testing."""
    return io.StringIO()


@pytest.fixture
def stream_handler(string_io: io.StringIO) -> StreamHandler:
    """Create a stream handler for testing."""
    config = HandlerConfig(
        name="test_handler",
        level=LogLevel.DEBUG,
        format="%(levelname)s: %(message)s",
    )
    return StreamHandler(string_io, config)


@pytest.fixture
def logger() -> Logger:
    """Create a logger for testing."""
    return Logger("test_logger")


class TestLogLevel:
    """Test LogLevel enum."""

    def test_to_python_level(self) -> None:
        """Test conversion to Python logging level."""
        assert LogLevel.DEBUG.to_python_level() == 10
        assert LogLevel.INFO.to_python_level() == 20
        assert LogLevel.WARNING.to_python_level() == 30
        assert LogLevel.ERROR.to_python_level() == 40
        assert LogLevel.CRITICAL.to_python_level() == 50


class TestLoggingConfig:
    """Test LoggingConfig."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = LoggingConfig(name="test")
        assert config.name == "test"
        assert config.enabled is True
        assert config.level == LogLevel.INFO
        assert isinstance(config.handlers, dict)
        assert isinstance(config.formatters, dict)
        assert isinstance(config.metadata, dict)

    def test_validate_handlers(self) -> None:
        """Test handler validation."""
        config = LoggingConfig(
            name="test",
            handlers={"console": {"class": "StreamHandler"}},
        )
        config.validate()  # Should not raise

        with pytest.raises(
            ValueError, match="Handler 'console' must have a 'class' field"
        ):
            config = LoggingConfig(
                name="test",
                handlers={"console": {}},  # Missing class
            )
            config.validate()

    def test_validate_formatters(self) -> None:
        """Test formatter validation."""
        config = LoggingConfig(
            name="test",
            formatters={"simple": {"format": "%(message)s"}},
        )
        config.validate()  # Should not raise

        with pytest.raises(
            ValueError, match="Formatter 'simple' must have a 'format' field"
        ):
            config = LoggingConfig(
                name="test",
                formatters={"simple": {}},  # Missing format
            )
            config.validate()


class TestStreamHandler:
    """Test StreamHandler."""

    def test_emit(self, stream_handler: StreamHandler, log_record: LogRecord) -> None:
        """Test log record emission."""
        stream_handler.emit(log_record)
        output = stream_handler.stream.getvalue()  # type: ignore
        assert "INFO: Test message" in output

    def test_format(self, stream_handler: StreamHandler, log_record: LogRecord) -> None:
        """Test log record formatting."""
        formatted = stream_handler.format(log_record)
        assert "INFO: Test message" in formatted
        assert log_record.metadata["extra"] == "data"


class TestLogger:
    """Test Logger."""

    def test_add_remove_handler(
        self, logger: Logger, stream_handler: StreamHandler
    ) -> None:
        """Test adding and removing handlers."""
        initial_handlers = len(logger._handlers)
        logger.add_handler(stream_handler)
        assert len(logger._handlers) == initial_handlers + 1

        logger.remove_handler(stream_handler)
        assert len(logger._handlers) == initial_handlers

    def test_log_levels(self, logger: Logger, string_io: io.StringIO) -> None:
        """Test different log levels."""
        handler = StreamHandler(string_io, HandlerConfig(level=LogLevel.DEBUG))
        logger.add_handler(handler)

        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

        output = string_io.getvalue()
        assert "DEBUG" in output
        assert "INFO" in output
        assert "WARNING" in output
        assert "ERROR" in output
        assert "CRITICAL" in output

    def test_log_with_metadata(self, logger: Logger, string_io: io.StringIO) -> None:
        """Test logging with metadata."""
        handler = StreamHandler(string_io)
        logger.add_handler(handler)

        logger.info("Test message", extra="data", user="test")
        output = string_io.getvalue()
        assert "Test message" in output


@pytest_asyncio.fixture
async def logging_manager() -> LoggingManager:
    """Create a logging manager for testing."""
    manager = LoggingManager()
    await manager.initialize()
    yield manager
    await manager._teardown()


@pytest.mark.asyncio
class TestLoggingManager:
    """Test LoggingManager."""

    async def test_initialization(self) -> None:
        """Test logging manager initialization."""
        manager = LoggingManager()
        assert not manager.is_initialized
        await manager.initialize()
        assert manager.is_initialized
        await manager._teardown()

    async def test_setup_teardown(self, logging_manager: LoggingManager) -> None:
        """Test setup and teardown."""
        # Test some logging
        logger = Logger("test")
        output = io.StringIO()
        handler = StreamHandler(output)
        logger.add_handler(handler)
        logger.info("Test message")

        assert "Test message" in output.getvalue()
