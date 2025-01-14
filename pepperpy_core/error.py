"""Error utilities module."""

import traceback
from typing import Optional, Type

from pepperpy_core import exceptions


def format_exception(error: Exception) -> str:
    """Format an exception with its full traceback.

    This utility function formats an exception including its complete traceback,
    making it useful for debugging and logging purposes.

    Args:
        error: The exception to format.

    Returns:
        str: The formatted exception traceback as a string.

    Example:
        ```python
        try:
            # Some code that may raise an exception
            result = process_data()
        except Exception as e:
            error_details = format_exception(e)
            logger.error(f"Processing failed: {error_details}")
        ```
    """
    return "".join(traceback.format_exception(type(error), error, error.__traceback__))


def format_error_context(
    error: Exception,
    *,
    include_traceback: bool = True,
    include_cause: bool = True,
) -> str:
    """Format an exception with additional context information.

    This function provides a more detailed error format, including:
    - The error message
    - The error type
    - The traceback (optional)
    - The cause chain (optional)
    - Additional context for PepperpyError instances

    Args:
        error: The exception to format
        include_traceback: Whether to include the full traceback
        include_cause: Whether to include the cause chain

    Returns:
        str: The formatted error context as a string

    Example:
        ```python
        try:
            await task.execute()
        except TaskError as e:
            error_details = format_error_context(e)
            logger.error(f"Task execution failed: {error_details}")
        ```
    """
    parts = []

    # Add error type and message
    parts.append(f"Error Type: {error.__class__.__name__}")
    parts.append(f"Message: {str(error)}")

    # Add PepperpyError specific context
    if isinstance(error, exceptions.PepperpyError):
        # Add any additional attributes specific to the error type
        for attr in dir(error):
            if (
                not attr.startswith("_")
                and attr not in ("args", "with_traceback")
                and hasattr(error, attr)
            ):
                value = getattr(error, attr)
                if value is not None:
                    parts.append(f"{attr}: {value}")

    # Add cause chain
    if include_cause and error.__cause__:
        parts.append("\nCaused by:")
        cause = error.__cause__
        while cause:
            parts.append(f"  {cause.__class__.__name__}: {str(cause)}")
            cause = cause.__cause__

    # Add traceback
    if include_traceback:
        parts.append("\nTraceback:")
        parts.append(format_exception(error))

    return "\n".join(parts)


def get_error_type(error_name: str) -> Optional[Type[Exception]]:
    """Get an exception type from the PepperpyError hierarchy by name.

    Args:
        error_name: The name of the error type to get

    Returns:
        The exception type if found, None otherwise

    Example:
        ```python
        error_type = get_error_type("TaskError")
        if error_type:
            raise error_type("Task failed to execute")
        ```
    """
    try:
        return getattr(exceptions, error_name)
    except AttributeError:
        return None
