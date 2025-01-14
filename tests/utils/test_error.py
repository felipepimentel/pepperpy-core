"""Test error utilities module."""

from pepperpy_core.error import (
    format_error_context,
    format_exception,
    get_error_type,
)
from pepperpy_core.exceptions import TaskError, ValidationError


def test_format_exception() -> None:
    """Test format_exception utility."""
    try:
        raise ValueError("Test error")
    except ValueError as e:
        result = format_exception(e)
        assert "ValueError: Test error" in result
        assert "test_error.py" in result


def test_format_error_context_basic() -> None:
    """Test basic error context formatting."""
    error = ValueError("Test error")
    result = format_error_context(error, include_traceback=False)
    assert "Error Type: ValueError" in result
    assert "Message: Test error" in result


def test_format_error_context_pepperpy_error() -> None:
    """Test error context formatting with PepperpyError."""
    error = TaskError("Task failed", task_id="123")
    result = format_error_context(error, include_traceback=False)
    assert "Error Type: TaskError" in result
    assert "Message: Task failed" in result
    assert "task_id: 123" in result


def test_format_error_context_with_cause() -> None:
    """Test error context formatting with cause chain."""
    try:
        try:
            raise ValueError("Inner error")
        except ValueError as e:
            raise TaskError("Task failed", cause=e) from e
    except TaskError as e:
        result = format_error_context(e, include_traceback=False)
        assert "Error Type: TaskError" in result
        assert "Message: Task failed" in result
        assert "Caused by:" in result
        assert "ValueError: Inner error" in result


def test_format_error_context_with_traceback() -> None:
    """Test error context formatting with traceback."""
    try:
        raise TaskError("Task failed")
    except TaskError as e:
        result = format_error_context(e, include_traceback=True)
        assert "Error Type: TaskError" in result
        assert "Message: Task failed" in result
        assert "Traceback:" in result
        assert "test_error.py" in result


def test_get_error_type_valid() -> None:
    """Test getting valid error type."""
    error_type = get_error_type("ValidationError")
    assert error_type == ValidationError


def test_get_error_type_invalid() -> None:
    """Test getting invalid error type."""
    error_type = get_error_type("NonExistentError")
    assert error_type is None
