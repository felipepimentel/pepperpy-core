"""Test error module."""

from typing import List

from pepperpy.utils.error import Error, ErrorLevel

__all__: List[str] = ["test_error_level", "test_error_str"]


def test_error_level() -> None:
    """Test error level."""
    error = Error("test", ErrorLevel.ERROR)
    assert error.level == ErrorLevel.ERROR


def test_error_str() -> None:
    """Test error string representation."""
    error = Error("test", ErrorLevel.ERROR)
    assert str(error) == "ERROR: test"
