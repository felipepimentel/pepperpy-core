"""All exceptions for pepperpy-core."""

from typing import Any


class PepperpyError(Exception):
    """Base exception for all pepperpy errors."""

    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
        details: dict[str, Any] | None = None,
        error_code: str | None = None,
    ) -> None:
        """Initialize exception.

        Args:
            message: Error message
            cause: Original exception that caused this error
            details: Additional error details
            error_code: Unique error code for this error
        """
        super().__init__(message)
        self.cause = cause
        self.details = details or {}
        self.error_code = error_code

    def __str__(self) -> str:
        """Return string representation."""
        parts = [self.args[0]]

        if self.error_code:
            parts.insert(0, f"[{self.error_code}]")

        if self.cause:
            parts.append(f"(caused by: {self.cause})")

        if self.details:
            parts.append(f"details: {self.details}")

        return " - ".join(parts)

    def get_full_details(self) -> dict[str, Any]:
        """Get full error details including cause chain.

        Returns:
            Dictionary with all error details
        """
        details = {
            "message": str(self.args[0]),
            "type": self.__class__.__name__,
        }

        if self.error_code:
            details["error_code"] = self.error_code

        if self.details:
            details["details"] = self.details

        if self.cause:
            if isinstance(self.cause, PepperpyError):
                details["cause"] = self.cause.get_full_details()
            else:
                details["cause"] = {
                    "message": str(self.cause),
                    "type": self.cause.__class__.__name__,
                }

        return details


# Configuration Errors
class ConfigError(PepperpyError):
    """Configuration-related errors."""

    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
        config_name: str | None = None,
    ) -> None:
        """Initialize configuration error.

        Args:
            message: Error message
            cause: Original exception that caused this error
            config_name: Name of the configuration that caused the error
        """
        super().__init__(
            message, cause, {"config_name": config_name} if config_name else None
        )
        self.config_name = config_name


# Validation Errors
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


# Resource Errors
class ResourceError(PepperpyError):
    """Resource-related errors."""

    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
        resource_name: str | None = None,
    ) -> None:
        """Initialize resource error.

        Args:
            message: Error message
            cause: Original exception that caused this error
            resource_name: Name of the resource that caused the error
        """
        super().__init__(
            message, cause, {"resource_name": resource_name} if resource_name else None
        )
        self.resource_name = resource_name


# State Errors
class StateError(PepperpyError):
    """State-related errors."""

    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
        current_state: str | None = None,
    ) -> None:
        """Initialize state error.

        Args:
            message: Error message
            cause: Original exception that caused this error
            current_state: Current state when the error occurred
        """
        super().__init__(
            message, cause, {"current_state": current_state} if current_state else None
        )
        self.current_state = current_state


# Module Errors
class ModuleError(PepperpyError):
    """Module-related errors."""

    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
        module_name: str | None = None,
    ) -> None:
        """Initialize module error.

        Args:
            message: Error message
            cause: Original exception that caused this error
            module_name: Name of the module that caused the error
        """
        super().__init__(
            message, cause, {"module_name": module_name} if module_name else None
        )
        self.module_name = module_name


class InitializationError(ModuleError):
    """Initialization-related errors."""

    pass


class ModuleNotFoundError(ModuleError):
    """Module not found errors."""

    pass


# Cache Errors
class CacheError(PepperpyError):
    """Cache-related errors."""

    def __init__(
        self, message: str, cause: Exception | None = None, key: str | None = None
    ) -> None:
        """Initialize cache error.

        Args:
            message: Error message
            cause: Original exception that caused this error
            key: Cache key that caused the error
        """
        super().__init__(message, cause, {"cache_key": key} if key else None)
        self.key = key


# Security Errors
class SecurityError(PepperpyError):
    """Security-related errors."""

    def __init__(
        self, message: str, cause: Exception | None = None, operation: str | None = None
    ) -> None:
        """Initialize security error.

        Args:
            message: Error message
            cause: Original exception that caused this error
            operation: Security operation that failed
        """
        super().__init__(
            message, cause, {"operation": operation} if operation else None
        )
        self.operation = operation


class AuthError(SecurityError):
    """Authentication error."""

    pass


class PermissionError(SecurityError):
    """Permission error."""

    pass


class TokenError(SecurityError):
    """Token error."""

    pass


class CryptoError(SecurityError):
    """Cryptography error."""

    pass


# Task Errors
class TaskError(PepperpyError):
    """Task-related errors."""

    def __init__(
        self, message: str, cause: Exception | None = None, task_id: str | None = None
    ) -> None:
        """Initialize task error.

        Args:
            message: Error message
            cause: Original exception that caused this error
            task_id: ID of the task that failed
        """
        super().__init__(message, cause, {"task_id": task_id} if task_id else None)
        self.task_id = task_id


class TaskExecutionError(TaskError):
    """Task execution error."""

    pass


class TaskNotFoundError(TaskError):
    """Task not found error."""

    pass


# Event Errors
class EventError(PepperpyError):
    """Event-related errors."""

    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
        event_type: str | None = None,
        event_id: str | None = None,
    ) -> None:
        """Initialize event error.

        Args:
            message: Error message
            cause: Original exception that caused this error
            event_type: Type of event that caused the error
            event_id: ID of event that caused the error
        """
        details = {}
        if event_type:
            details["event_type"] = event_type
        if event_id:
            details["event_id"] = event_id
        super().__init__(message, cause, details or None)
        self.event_type = event_type
        self.event_id = event_id


class EventHandlerError(EventError):
    """Event handler-related errors."""

    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
        event_type: str | None = None,
        event_id: str | None = None,
        handler_name: str | None = None,
    ) -> None:
        """Initialize event handler error.

        Args:
            message: Error message
            cause: Original exception that caused this error
            event_type: Type of event that caused the error
            event_id: ID of event that caused the error
            handler_name: Name of handler that failed
        """
        super().__init__(message, cause, event_type, event_id)
        if handler_name:
            self.details["handler_name"] = handler_name
        self.handler_name = handler_name


class EventMiddlewareError(EventError):
    """Event middleware-related errors."""

    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
        event_type: str | None = None,
        event_id: str | None = None,
        middleware_name: str | None = None,
        stage: str | None = None,
    ) -> None:
        """Initialize event middleware error.

        Args:
            message: Error message
            cause: Original exception that caused this error
            event_type: Type of event that caused the error
            event_id: ID of event that caused the error
            middleware_name: Name of middleware that failed
            stage: Stage where middleware failed (before/after)
        """
        super().__init__(message, cause, event_type, event_id)
        if middleware_name:
            self.details["middleware_name"] = middleware_name
        if stage:
            self.details["stage"] = stage
        self.middleware_name = middleware_name
        self.stage = stage


# Network Errors
class NetworkError(PepperpyError):
    """Network-related errors."""

    pass


class ConnectionError(NetworkError):
    """Connection error."""

    pass


class RequestError(NetworkError):
    """Request error."""

    pass


class ResponseError(NetworkError):
    """Response error."""

    pass


class TimeoutError(NetworkError):
    """Timeout error."""

    pass


class SSLError(NetworkError):
    """SSL error."""

    pass


class ProxyError(NetworkError):
    """Proxy error."""

    pass


class DNSError(NetworkError):
    """DNS error."""

    pass


# Plugin Errors
class PluginError(PepperpyError):
    """Plugin-related errors."""

    pass


class PluginNotFoundError(PluginError):
    """Plugin not found error."""

    pass


class PluginLoadError(PluginError):
    """Plugin load error."""

    pass


# Logging Errors
class LoggingError(PepperpyError):
    """Logging-related errors."""

    pass


class LogConfigError(LoggingError):
    """Log configuration error."""

    pass


class LogHandlerError(LoggingError):
    """Log handler error."""

    pass


class LogFormatError(LoggingError):
    """Log format error."""

    pass


# Telemetry Errors
class TelemetryError(PepperpyError):
    """Telemetry-related errors."""

    pass


class MetricError(TelemetryError):
    """Metric error."""

    pass


class CollectorError(MetricError):
    """Collector error."""

    pass


class MetricValueError(MetricError):
    """Metric value error."""

    pass


class TracingError(TelemetryError):
    """Tracing error."""

    pass


class PerformanceError(TelemetryError):
    """Performance error."""

    pass


__all__ = [
    # Base
    "PepperpyError",
    # Configuration
    "ConfigError",
    # Validation
    "ValidationError",
    # Resource
    "ResourceError",
    # State
    "StateError",
    # Module
    "ModuleError",
    "InitializationError",
    "ModuleNotFoundError",
    # Cache
    "CacheError",
    # Security
    "SecurityError",
    "AuthError",
    "PermissionError",
    "TokenError",
    "CryptoError",
    # Task
    "TaskError",
    "TaskExecutionError",
    "TaskNotFoundError",
    # Event
    "EventError",
    "EventHandlerError",
    "EventMiddlewareError",
    # Network
    "NetworkError",
    "ConnectionError",
    "RequestError",
    "ResponseError",
    "TimeoutError",
    "SSLError",
    "ProxyError",
    "DNSError",
    # Plugin
    "PluginError",
    "PluginNotFoundError",
    "PluginLoadError",
    # Logging
    "LoggingError",
    "LogConfigError",
    "LogHandlerError",
    "LogFormatError",
    # Telemetry
    "TelemetryError",
    "MetricError",
    "CollectorError",
    "MetricValueError",
    "TracingError",
    "PerformanceError",
]
