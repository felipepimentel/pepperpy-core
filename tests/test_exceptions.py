"""Test exceptions functionality"""

from pepperpy_core.exceptions import PepperpyError
from pepperpy_core.exceptions.module import ModuleError


def test_base_error() -> None:
    """Test base error class"""
    error = PepperpyError("Test error")
    assert str(error) == "Test error"


def test_module_error() -> None:
    """Test module error class"""
    error = ModuleError("Test module error")
    assert str(error) == "Test module error"
    assert isinstance(error, PepperpyError)


def test_error_with_cause() -> None:
    """Test error with cause"""
    cause = ValueError("Original error")
    error = PepperpyError("Test error", cause=cause)
    assert str(error) == "Test error"
    assert error.cause == cause
