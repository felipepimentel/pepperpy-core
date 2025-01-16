"""Error handling utilities."""

from enum import Enum, auto


class ErrorLevel(Enum):
    """Error level enumeration."""

    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


class Error:
    """Error class."""

    def __init__(self, message: str, level: ErrorLevel) -> None:
        """Initialize error.

        Args:
            message: Error message.
            level: Error level.
        """
        self.message = message
        self.level = level

    def __str__(self) -> str:
        """Return string representation.

        Returns:
            String representation.
        """
        return f"{self.level.name}: {self.message}"
