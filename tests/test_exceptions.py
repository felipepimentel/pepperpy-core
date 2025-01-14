"""Test exceptions module."""

from pepperpy.exceptions import PepperpyError


def test_pepperpy_error() -> None:
    """Test pepperpy error."""
    error = PepperpyError("test")
    assert str(error) == "test"


def test_pepperpy_error_with_cause() -> None:
    """Test pepperpy error with cause."""
    cause = ValueError("cause")
    error = PepperpyError("test", cause)
    assert str(error) == "test"
    assert error.__cause__ == cause


def test_pepperpy_error_with_traceback() -> None:
    """Test pepperpy error with traceback."""
    try:
        raise ValueError("test")
    except ValueError as e:
        error = PepperpyError("test", e)
        assert error.__traceback__ is not None
