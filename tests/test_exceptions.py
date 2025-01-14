"""Test exceptions module."""

from pepperpy.core import PepperpyError


def test_pepperpy_error() -> None:
    """Test pepperpy error."""
    error = PepperpyError("test error")
    assert str(error) == "test error"


def test_pepperpy_error_with_cause() -> None:
    """Test pepperpy error with cause."""
    cause = ValueError("cause error")
    error = PepperpyError("test error", cause=cause)
    assert str(error) == "test error"
    assert error.__cause__ == cause


def test_pepperpy_error_with_traceback() -> None:
    """Test pepperpy error with traceback."""
    try:
        raise ValueError("cause error")
    except ValueError as e:
        error = PepperpyError("test error", cause=e)
        assert error.__traceback__ == e.__traceback__
