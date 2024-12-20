"""Base exceptions for pepperpy-core."""

from typing import Any


class PepperpyError(Exception):
    """Base exception for all pepperpy errors."""

    def __init__(self, message: str, cause: Exception | None = None, details: dict[str, Any] | None = None) -> None:
        """Initialize exception.

        Args:
            message: Error message
            cause: Original exception that caused this error
            details: Additional error details
        """
        super().__init__(message)
        self.cause = cause
        self.details = details or {}

    def __str__(self) -> str:
        """Return string representation."""
        result = self.args[0]
        if self.cause:
            result = f"{result} (caused by: {self.cause})"
        if self.details:
            result = f"{result} - details: {self.details}"
        return result


class ConfigError(PepperpyError):
    """Configuration-related errors."""

    def __init__(self, message: str, cause: Exception | None = None, config_name: str | None = None) -> None:
        """Initialize configuration error.

        Args:
            message: Error message
            cause: Original exception that caused this error
            config_name: Name of the configuration that caused the error
        """
        super().__init__(message, cause, {"config_name": config_name} if config_name else None)
        self.config_name = config_name


class ValidationError(PepperpyError):
    """Validation-related errors."""

    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
        field_name: str | None = None,
        invalid_value: Any = None,
    ) -> None:
        """Initialize validation error.

        Args:
            message: Error message
            cause: Original exception that caused this error
            field_name: Name of the field that failed validation
            invalid_value: The value that failed validation
        """
        details = {}
        if field_name:
            details["field_name"] = field_name
        if invalid_value is not None:
            details["invalid_value"] = str(invalid_value)
            details["invalid_value_type"] = type(invalid_value).__name__
        super().__init__(message, cause, details or None)
        self.field_name = field_name
        self.invalid_value = invalid_value


class ResourceError(PepperpyError):
    """Resource-related errors."""

    def __init__(self, message: str, cause: Exception | None = None, resource_name: str | None = None) -> None:
        """Initialize resource error.

        Args:
            message: Error message
            cause: Original exception that caused this error
            resource_name: Name of the resource that caused the error
        """
        super().__init__(message, cause, {"resource_name": resource_name} if resource_name else None)
        self.resource_name = resource_name


class StateError(PepperpyError):
    """State-related errors."""

    def __init__(self, message: str, cause: Exception | None = None, current_state: str | None = None) -> None:
        """Initialize state error.

        Args:
            message: Error message
            cause: Original exception that caused this error
            current_state: Current state when the error occurred
        """
        super().__init__(message, cause, {"current_state": current_state} if current_state else None)
        self.current_state = current_state


class ModuleError(PepperpyError):
    """Module-related errors."""

    def __init__(self, message: str, cause: Exception | None = None, module_name: str | None = None) -> None:
        """Initialize module error.

        Args:
            message: Error message
            cause: Original exception that caused this error
            module_name: Name of the module that caused the error
        """
        super().__init__(message, cause, {"module_name": module_name} if module_name else None)
        self.module_name = module_name


class InitializationError(ModuleError):
    """Initialization-related errors."""

    pass


class CacheError(PepperpyError):
    """Cache-related errors."""

    def __init__(self, message: str, cause: Exception | None = None, key: str | None = None) -> None:
        """Initialize cache error.

        Args:
            message: Error message
            cause: Original exception that caused this error
            key: Cache key that caused the error
        """
        super().__init__(message, cause, {"cache_key": key} if key else None)
        self.key = key


class SecurityError(PepperpyError):
    """Security-related errors."""

    def __init__(self, message: str, cause: Exception | None = None, operation: str | None = None) -> None:
        """Initialize security error.

        Args:
            message: Error message
            cause: Original exception that caused this error
            operation: Security operation that failed
        """
        super().__init__(message, cause, {"operation": operation} if operation else None)
        self.operation = operation


class TaskError(PepperpyError):
    """Task-related errors."""

    def __init__(self, message: str, cause: Exception | None = None, task_id: str | None = None) -> None:
        """Initialize task error.

        Args:
            message: Error message
            cause: Original exception that caused this error
            task_id: ID of the task that failed
        """
        super().__init__(message, cause, {"task_id": task_id} if task_id else None)
        self.task_id = task_id


__all__ = [
    "PepperpyError",
    "ConfigError",
    "ValidationError",
    "ResourceError",
    "StateError",
    "ModuleError",
    "InitializationError",
    "CacheError",
    "SecurityError",
    "TaskError",
]
