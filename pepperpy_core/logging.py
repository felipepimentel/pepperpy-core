"""Logging implementation module."""

import logging
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TextIO

from .exceptions import PepperpyError
from .module import BaseModule, ModuleConfig


class LoggingError(PepperpyError):
    """Logging specific error."""

    pass


class LogLevel(str, Enum):
    """Log levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

    def to_python_level(self) -> int:
        """Convert to Python logging level.

        Returns:
            Python logging level
        """
        level_map = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
        }
        return level_map[self]


@dataclass
class LoggingConfig(ModuleConfig):
    """Logging configuration."""

    # Required fields (inherited from ModuleConfig)
    name: str

    # Optional fields
    enabled: bool = True
    level: LogLevel = LogLevel.DEBUG
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handlers: dict[str, Any] = field(default_factory=dict)
    formatters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate configuration."""
        for name, handler in self.handlers.items():
            if "class" not in handler:
                raise ValueError(f"Handler '{name}' must have a 'class' field")

        for name, formatter in self.formatters.items():
            if "format" not in formatter:
                raise ValueError(f"Formatter '{name}' must have a 'format' field")


@dataclass
class LogRecord:
    """Log record data."""

    level: LogLevel
    message: str
    logger_name: str
    module: str
    function: str
    line: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HandlerConfig:
    """Handler configuration."""

    name: str = ""
    level: LogLevel = LogLevel.DEBUG
    format: str = "%(levelname)s: %(message)s"
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseHandler:
    """Base logging handler."""

    def __init__(self, config: HandlerConfig | None = None) -> None:
        """Initialize handler.

        Args:
            config: Handler configuration
        """
        self.config = config or HandlerConfig()

    def emit(self, record: LogRecord) -> None:
        """Emit log record."""
        raise NotImplementedError


class StreamHandler(BaseHandler):
    """Stream handler implementation."""

    def __init__(self, stream: TextIO, config: HandlerConfig | None = None) -> None:
        """Initialize handler.

        Args:
            stream: Output stream
            config: Handler configuration
        """
        super().__init__(config)
        self.stream = stream

    def emit(self, record: LogRecord) -> None:
        """Emit log record."""
        try:
            message = self.format(record)
            self.stream.write(message + "\n")
            self.stream.flush()
        except Exception as e:
            # Avoid recursion if error occurs during logging
            print(f"Error in log handler: {e}", file=self.stream)

    def format(self, record: LogRecord) -> str:
        """Format log record.

        Args:
            record: Log record

        Returns:
            Formatted message
        """
        return self.config.format % {
            "levelname": record.level.name,
            "message": record.message,
            "logger": record.logger_name,
            "module": record.module,
            "function": record.function,
            "line": record.line,
            **record.metadata,
        }


class BaseLogger(ABC):
    """Base logger interface."""

    @abstractmethod
    def log(self, level: LogLevel, message: str, **kwargs: Any) -> None:
        """Log message.

        Args:
            level: Log level
            message: Log message
            **kwargs: Additional log data
        """
        pass

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self.log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self.log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self.log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self.log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message."""
        self.log(LogLevel.CRITICAL, message, **kwargs)


class Logger(BaseLogger):
    """Logger implementation."""

    def __init__(self, name: str) -> None:
        """Initialize logger.

        Args:
            name: Logger name
        """
        self.name = name
        self._handlers: list[BaseHandler] = []
        self._default_handler = StreamHandler(
            sys.stdout, HandlerConfig(level=LogLevel.DEBUG)
        )
        self._handlers.append(self._default_handler)

    def add_handler(self, handler: BaseHandler) -> None:
        """Add log handler.

        Args:
            handler: Log handler
        """
        self._handlers.append(handler)

    def remove_handler(self, handler: BaseHandler) -> None:
        """Remove log handler.

        Args:
            handler: Log handler
        """
        if handler is not self._default_handler:
            self._handlers.remove(handler)

    def log(self, level: LogLevel, message: str, **kwargs: Any) -> None:
        """Log message.

        Args:
            level: Log level
            message: Log message
            **kwargs: Additional log data
        """
        record = LogRecord(
            level=level,
            message=message,
            logger_name=self.name,
            module=kwargs.get("module", ""),
            function=kwargs.get("function", ""),
            line=kwargs.get("line", 0),
            metadata=kwargs,
        )

        for handler in self._handlers:
            if level.to_python_level() >= handler.config.level.to_python_level():
                handler.emit(record)


class LoggingManager(BaseModule[LoggingConfig]):
    """Logging manager implementation."""

    def __init__(self) -> None:
        """Initialize logging manager."""
        config = LoggingConfig(name="logging-manager", level=LogLevel.DEBUG)
        super().__init__(config)
        self._loggers: dict[str, Logger] = {}

    async def _setup(self) -> None:
        """Setup logging manager."""
        self._loggers.clear()

        # Configure Python logging
        logging.basicConfig(
            level=self.config.level.to_python_level(),
            format=self.config.format,
        )

    async def _teardown(self) -> None:
        """Teardown logging manager."""
        self._loggers.clear()

    async def get_stats(self) -> dict[str, Any]:
        """Get logging manager statistics.

        Returns:
            Logging manager statistics
        """
        self._ensure_initialized()
        return {
            "name": self.config.name,
            "enabled": self.config.enabled,
            "level": self.config.level.value,
            "total_loggers": len(self._loggers),
            "logger_names": list(self._loggers.keys()),
        }

    def get_logger(self, name: str) -> Logger:
        """Get logger by name.

        Args:
            name: Logger name

        Returns:
            Logger instance
        """
        self._ensure_initialized()

        if name not in self._loggers:
            self._loggers[name] = Logger(name)

        return self._loggers[name]


__all__ = [
    "LoggingError",
    "LogLevel",
    "LoggingConfig",
    "LogRecord",
    "HandlerConfig",
    "BaseHandler",
    "StreamHandler",
    "BaseLogger",
    "Logger",
    "LoggingManager",
]
