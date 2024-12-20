"""Security implementation module."""

import functools
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import Any, ParamSpec, TypeVar, cast

from .exceptions import PepperpyError
from .module import BaseModule, ModuleConfig
from .validation import ValidationResult, Validator


class SecurityError(PepperpyError):
    """Security specific error."""

    pass


@dataclass
class SecurityConfig(ModuleConfig):
    """Security configuration."""

    # Required fields (inherited from ModuleConfig)
    name: str

    # Optional fields
    enabled: bool = True
    require_auth: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate configuration."""
        pass


@dataclass
class AuthInfo:
    """Authentication information."""

    user_id: str
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityContext:
    """Security context."""

    auth_info: AuthInfo | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_authenticated(self) -> bool:
        """Check if context is authenticated."""
        return self.auth_info is not None

    def has_role(self, role: str) -> bool:
        """Check if context has role.

        Args:
            role: Role to check

        Returns:
            True if role is present
        """
        return self.auth_info is not None and role in self.auth_info.roles

    def has_permission(self, permission: str) -> bool:
        """Check if context has permission.

        Args:
            permission: Permission to check

        Returns:
            True if permission is present
        """
        return self.auth_info is not None and permission in self.auth_info.permissions


class DefaultValidatorFactory:
    """Default validator factory implementation."""

    @staticmethod
    def create_type_validator(type_name: str) -> Validator[Any]:
        """Create type validator.

        Args:
            type_name: Type name

        Returns:
            Type validator
        """
        return DefaultValidator()


class DefaultValidator(Validator[Any]):
    """Default validator implementation."""

    async def validate(self, value: Any) -> ValidationResult:
        """Validate value.

        Args:
            value: Value to validate

        Returns:
            Validation result
        """
        # Implement actual validation logic
        return ValidationResult(valid=True)


class SecurityManager(BaseModule[SecurityConfig]):
    """Security manager implementation."""

    def __init__(self) -> None:
        """Initialize security manager."""
        config = SecurityConfig(name="security-manager")
        super().__init__(config)
        self._validator_factory = DefaultValidatorFactory()
        self._config_validator = self._create_config_validator()
        self._context = SecurityContext()

    def _create_config_validator(self) -> Validator[Any]:
        """Create config validator.

        Returns:
            Config validator
        """
        return self._validator_factory.create_type_validator("SecurityConfig")

    async def _setup(self) -> None:
        """Setup security manager."""
        result = await self._config_validator.validate(self.config)
        if not result.valid:
            raise SecurityError(f"Invalid security configuration: {result.message}")
        self._context = SecurityContext()

    async def _teardown(self) -> None:
        """Teardown security manager."""
        self._context = SecurityContext()

    async def get_stats(self) -> dict[str, Any]:
        """Get security manager statistics.

        Returns:
            Security manager statistics
        """
        self._ensure_initialized()
        return {
            "name": self.config.name,
            "enabled": self.config.enabled,
            "require_auth": self.config.require_auth,
            "is_authenticated": self._context.is_authenticated,
            "user_id": self._context.auth_info.user_id if self._context.auth_info else None,
            "roles_count": len(self._context.auth_info.roles)
            if self._context.auth_info
            else 0,
            "permissions_count": len(self._context.auth_info.permissions)
            if self._context.auth_info
            else 0,
        }

    async def authenticate(self, auth_info: AuthInfo) -> None:
        """Authenticate user.

        Args:
            auth_info: Authentication information
        """
        self._ensure_initialized()
        self._context.auth_info = auth_info

    def get_context(self) -> SecurityContext:
        """Get current security context.

        Returns:
            Security context
        """
        self._ensure_initialized()
        return self._context


# Type variables for function decorators
P = ParamSpec("P")
R = TypeVar("R")
AsyncFunc = Callable[P, Coroutine[Any, Any, R]]
SyncFunc = Callable[P, R]


def require_auth() -> Callable[[AsyncFunc[P, R]], AsyncFunc[P, R]]:
    """Require authentication decorator.

    Returns:
        Decorated function
    """

    def decorator(func: AsyncFunc[P, R]) -> AsyncFunc[P, R]:
        """Decorate function.

        Args:
            func: Function to decorate

        Returns:
            Decorated function
        """

        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            """Wrap function call.

            Args:
                *args: Function arguments
                **kwargs: Function keyword arguments

            Returns:
                Function result

            Raises:
                SecurityError: If not authenticated
            """
            manager = SecurityManager()
            context = manager.get_context()
            if not context.is_authenticated:
                raise SecurityError("Authentication required")
            return await func(*args, **kwargs)

        return cast(AsyncFunc[P, R], wrapper)

    return decorator


def require_roles(
    *roles: str,
) -> Callable[[AsyncFunc[P, R]], AsyncFunc[P, R]]:
    """Require roles decorator.

    Args:
        *roles: Required roles

    Returns:
        Decorated function
    """

    def decorator(func: AsyncFunc[P, R]) -> AsyncFunc[P, R]:
        """Decorate function.

        Args:
            func: Function to decorate

        Returns:
            Decorated function
        """

        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            """Wrap function call.

            Args:
                *args: Function arguments
                **kwargs: Function keyword arguments

            Returns:
                Function result

            Raises:
                SecurityError: If required roles not present
            """
            manager = SecurityManager()
            context = manager.get_context()
            if not context.is_authenticated:
                raise SecurityError("Authentication required")
            if not all(context.has_role(role) for role in roles):
                raise SecurityError("Required roles not present")
            return await func(*args, **kwargs)

        return cast(AsyncFunc[P, R], wrapper)

    return decorator


def require_permissions(
    *permissions: str,
) -> Callable[[AsyncFunc[P, R]], AsyncFunc[P, R]]:
    """Require permissions decorator.

    Args:
        *permissions: Required permissions

    Returns:
        Decorated function
    """

    def decorator(func: AsyncFunc[P, R]) -> AsyncFunc[P, R]:
        """Decorate function.

        Args:
            func: Function to decorate

        Returns:
            Decorated function
        """

        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            """Wrap function call.

            Args:
                *args: Function arguments
                **kwargs: Function keyword arguments

            Returns:
                Function result

            Raises:
                SecurityError: If required permissions not present
            """
            manager = SecurityManager()
            context = manager.get_context()
            if not context.is_authenticated:
                raise SecurityError("Authentication required")
            if not all(context.has_permission(perm) for perm in permissions):
                raise SecurityError("Required permissions not present")
            return await func(*args, **kwargs)

        return cast(AsyncFunc[P, R], wrapper)

    return decorator


__all__ = [
    "SecurityError",
    "SecurityConfig",
    "AuthInfo",
    "SecurityContext",
    "SecurityManager",
    "require_auth",
    "require_roles",
    "require_permissions",
] 