"""Core functionality."""

from typing import Any, Dict, Optional


class PepperpyError(Exception):
    """Base class for all pepperpy errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize error.

        Args:
            message: Error message.
            details: Error details.
            cause: Original exception that caused this error.
        """
        super().__init__(message)
        self.details = details or {}
        if cause:
            self.__cause__ = cause
            self.__traceback__ = cause.__traceback__


def get_error_context(error: Exception) -> Dict[str, Any]:
    """Get error context.

    Args:
        error: Exception to get context from.

    Returns:
        Error context.
    """
    if isinstance(error, PepperpyError):
        return error.details
    return {}


def format_error_context(context: Dict[str, Any]) -> str:
    """Format error context.

    Args:
        context: Error context.

    Returns:
        Formatted error context.
    """
    if not context:
        return ""
    return "\n".join(f"{key}: {value}" for key, value in context.items())


def format_exception(error: Exception) -> str:
    """Format exception.

    Args:
        error: Exception to format.

    Returns:
        Formatted exception.
    """
    message = str(error)
    context = get_error_context(error)
    if context:
        context_str = format_error_context(context)
        return f"{message}\nContext:\n{context_str}"
    return message


__all__ = [
    "PepperpyError",
    "get_error_context",
    "format_error_context",
    "format_exception",
]
