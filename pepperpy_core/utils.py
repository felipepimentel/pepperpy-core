"""Utility functions and helpers."""

import datetime as dt
from typing import Any, TypeVar

T = TypeVar("T")


def utcnow() -> dt.datetime:
    """Get current UTC datetime.

    Returns:
        Current UTC datetime
    """
    return dt.datetime.now(dt.timezone.utc)


def format_datetime(value: dt.datetime) -> str:
    """Format datetime in ISO format.

    Args:
        value: Datetime to format

    Returns:
        Formatted datetime string
    """
    return value.isoformat()


def parse_datetime(value: str) -> dt.datetime:
    """Parse datetime from ISO format.

    Args:
        value: Datetime string to parse

    Returns:
        Parsed datetime

    Raises:
        ValueError: If datetime string is invalid
    """
    return dt.datetime.fromisoformat(value)


def get_type_name(obj: Any) -> str:
    """Get type name of object.

    Args:
        obj: Object to get type name for

    Returns:
        Type name
    """
    return type(obj).__name__


def safe_cast(value: Any, target_type: type[T]) -> T | None:
    """Safely cast value to target type.

    Args:
        value: Value to cast
        target_type: Target type

    Returns:
        Cast value or None if casting fails
    """
    try:
        return target_type(value)
    except (TypeError, ValueError):
        return None


__all__ = [
    "utcnow",
    "format_datetime",
    "parse_datetime",
    "get_type_name",
    "safe_cast",
]
