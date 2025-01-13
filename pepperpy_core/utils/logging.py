"""Logging utilities."""

import logging
from typing import Any


def get_logger(name: str) -> logging.Logger:
    """Get logger by name.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def get_module_logger(module_name: str) -> logging.Logger:
    """Get logger for module.

    Args:
        module_name: Module name

    Returns:
        Logger instance
    """
    return get_logger(module_name)


def get_package_logger() -> logging.Logger:
    """Get logger for package.

    Returns:
        Logger instance
    """
    return get_logger("pepperpy_core")


class LoggerMixin:
    """Logger mixin."""

    def __init__(self) -> None:
        """Initialize logger mixin."""
        self._logger = get_logger(self.__class__.__name__)

    @property
    def logger(self) -> logging.Logger:
        """Get logger.

        Returns:
            Logger instance
        """
        return self._logger

    def log(self, level: int, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log message.

        Args:
            level: Log level
            msg: Log message
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        self.logger.log(level, msg, *args, **kwargs)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log debug message.

        Args:
            msg: Log message
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log info message.

        Args:
            msg: Log message
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log warning message.

        Args:
            msg: Log message
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log error message.

        Args:
            msg: Log message
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log critical message.

        Args:
            msg: Log message
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        self.logger.critical(msg, *args, **kwargs)
