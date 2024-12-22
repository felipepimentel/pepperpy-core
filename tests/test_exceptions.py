"""Test exceptions functionality"""

from pepperpy_core.exceptions import (
    AuthError,
    CacheError,
    ConfigError,
    CryptoError,
    InitializationError,
    ModuleError,
    ModuleNotFoundError,
    PepperpyError,
    PermissionError,
    ResourceError,
    SecurityError,
    StateError,
    TaskError,
    TaskExecutionError,
    TaskNotFoundError,
    TokenError,
    ValidationError,
)


def test_base_error() -> None:
    """Test base error class with all features."""
    # Test basic error
    error = PepperpyError("Test error")
    assert str(error) == "Test error"
    assert error.get_full_details() == {
        "message": "Test error",
        "type": "PepperpyError",
    }

    # Test with error code
    error = PepperpyError("Test error", error_code="E001")
    assert str(error) == "[E001] - Test error"
    assert error.get_full_details() == {
        "message": "Test error",
        "type": "PepperpyError",
        "error_code": "E001",
    }

    # Test with details
    error = PepperpyError("Test error", details={"key": "value"})
    assert str(error) == "Test error - details: {'key': 'value'}"
    assert error.get_full_details() == {
        "message": "Test error",
        "type": "PepperpyError",
        "details": {"key": "value"},
    }

    # Test with cause
    cause = ValueError("Original error")
    error = PepperpyError("Test error", cause=cause)
    assert str(error) == "Test error - (caused by: Original error)"
    assert error.get_full_details() == {
        "message": "Test error",
        "type": "PepperpyError",
        "cause": {
            "message": "Original error",
            "type": "ValueError",
        },
    }

    # Test with pepperpy error as cause
    cause = PepperpyError("Inner error", error_code="E002")
    error = PepperpyError("Test error", cause=cause)
    assert str(error) == "Test error - (caused by: [E002] - Inner error)"
    assert error.get_full_details() == {
        "message": "Test error",
        "type": "PepperpyError",
        "cause": {
            "message": "Inner error",
            "type": "PepperpyError",
            "error_code": "E002",
        },
    }


def test_config_error() -> None:
    """Test configuration error."""
    error = ConfigError("Invalid config", config_name="test_config")
    assert str(error) == "Invalid config - details: {'config_name': 'test_config'}"
    assert error.config_name == "test_config"
    assert isinstance(error, PepperpyError)


def test_validation_error() -> None:
    """Test validation error."""
    error = ValidationError(
        "Invalid value",
        field_name="test_field",
        invalid_value=123,
    )
    assert "Invalid value" in str(error)
    assert "field_name" in str(error)
    assert "invalid_value" in str(error)
    assert error.field_name == "test_field"
    assert error.invalid_value == 123
    assert isinstance(error, PepperpyError)


def test_resource_error() -> None:
    """Test resource error."""
    error = ResourceError("Resource not found", resource_name="test_resource")
    assert (
        str(error) == "Resource not found - details: {'resource_name': 'test_resource'}"
    )
    assert error.resource_name == "test_resource"
    assert isinstance(error, PepperpyError)


def test_state_error() -> None:
    """Test state error."""
    error = StateError("Invalid state", current_state="running")
    assert str(error) == "Invalid state - details: {'current_state': 'running'}"
    assert error.current_state == "running"
    assert isinstance(error, PepperpyError)


def test_module_errors() -> None:
    """Test module-related errors."""
    # Test ModuleError
    error = ModuleError("Module failed", module_name="test_module")
    assert str(error) == "Module failed - details: {'module_name': 'test_module'}"
    assert error.module_name == "test_module"
    assert isinstance(error, PepperpyError)

    # Test InitializationError
    error = InitializationError("Init failed", module_name="test_module")
    assert str(error) == "Init failed - details: {'module_name': 'test_module'}"
    assert error.module_name == "test_module"
    assert isinstance(error, ModuleError)

    # Test ModuleNotFoundError
    error = ModuleNotFoundError("Module not found", module_name="test_module")
    assert str(error) == "Module not found - details: {'module_name': 'test_module'}"
    assert error.module_name == "test_module"
    assert isinstance(error, ModuleError)


def test_cache_error() -> None:
    """Test cache error."""
    error = CacheError("Cache miss", key="test_key")
    assert str(error) == "Cache miss - details: {'cache_key': 'test_key'}"
    assert error.key == "test_key"
    assert isinstance(error, PepperpyError)


def test_security_errors() -> None:
    """Test security-related errors."""
    # Test SecurityError
    error = SecurityError("Security breach", operation="login")
    assert str(error) == "Security breach - details: {'operation': 'login'}"
    assert error.operation == "login"
    assert isinstance(error, PepperpyError)

    # Test AuthError
    error = AuthError("Auth failed", operation="login")
    assert str(error) == "Auth failed - details: {'operation': 'login'}"
    assert error.operation == "login"
    assert isinstance(error, SecurityError)

    # Test PermissionError
    error = PermissionError("Permission denied", operation="access")
    assert str(error) == "Permission denied - details: {'operation': 'access'}"
    assert error.operation == "access"
    assert isinstance(error, SecurityError)

    # Test TokenError
    error = TokenError("Invalid token", operation="verify")
    assert str(error) == "Invalid token - details: {'operation': 'verify'}"
    assert error.operation == "verify"
    assert isinstance(error, SecurityError)

    # Test CryptoError
    error = CryptoError("Encryption failed", operation="encrypt")
    assert str(error) == "Encryption failed - details: {'operation': 'encrypt'}"
    assert error.operation == "encrypt"
    assert isinstance(error, SecurityError)


def test_task_errors() -> None:
    """Test task-related errors."""
    # Test TaskError
    error = TaskError("Task failed", task_id="task1")
    assert str(error) == "Task failed - details: {'task_id': 'task1'}"
    assert error.task_id == "task1"
    assert isinstance(error, PepperpyError)

    # Test TaskExecutionError
    error = TaskExecutionError("Execution failed", task_id="task1")
    assert str(error) == "Execution failed - details: {'task_id': 'task1'}"
    assert error.task_id == "task1"
    assert isinstance(error, TaskError)

    # Test TaskNotFoundError
    error = TaskNotFoundError("Task not found", task_id="task1")
    assert str(error) == "Task not found - details: {'task_id': 'task1'}"
    assert error.task_id == "task1"
    assert isinstance(error, TaskError)
