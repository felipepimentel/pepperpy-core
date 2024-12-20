"""Example of using the logging module."""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any


class LogLevel(Enum):
    """Log level enumeration."""

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


@dataclass
class BasicLogConfig:
    """Basic log configuration."""

    level: LogLevel
    format: str
    datefmt: str | None = None

    def get_level(self) -> int:
        """Get log level value."""
        return self.level.value


def setup_logging(config: BasicLogConfig) -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=config.get_level(),
        format=config.format,
        datefmt=config.datefmt,
    )


def log_message(level: LogLevel, message: str, **kwargs: Any) -> None:
    """Log a message with the specified level."""
    logger = logging.getLogger(__name__)
    logger.log(level.value, message, **kwargs)


def main() -> None:
    """Main function."""
    config = BasicLogConfig(
        level=LogLevel[logging.getLevelName(logging.INFO).upper()],
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    setup_logging(config)

    # Log messages at different levels
    log_message(
        LogLevel[logging.getLevelName(logging.DEBUG).upper()],
        "This is a debug message",
    )
    log_message(
        LogLevel[logging.getLevelName(logging.INFO).upper()],
        "This is an info message",
    )
    log_message(
        LogLevel[logging.getLevelName(logging.WARNING).upper()],
        "This is a warning message",
    )
    log_message(
        LogLevel[logging.getLevelName(logging.ERROR).upper()],
        "This is an error message",
    )
    log_message(
        LogLevel[logging.getLevelName(logging.CRITICAL).upper()],
        "This is a critical message",
    )


if __name__ == "__main__":
    main()
