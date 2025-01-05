"""Security module."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TypeVar

from .exceptions import SecurityError
from .module import BaseModule, ModuleConfig


class SecurityLevel(Enum):
    """Security level types."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    def __str__(self) -> str:
        """Return string representation."""
        return self.value


@dataclass
class SecurityContext:
    """Security context with metadata."""

    path: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    parent: "SecurityContext | None" = None
    _children: list["SecurityContext"] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        """Validate context."""
        if not isinstance(self.path, str):
            raise SecurityError(
                f"path must be a string, got {type(self.path).__name__}"
            )
        if not isinstance(self.metadata, dict):
            raise SecurityError(
                f"metadata must be a dictionary, got {type(self.metadata).__name__}"
            )


@dataclass(frozen=True)  # Make immutable for thread safety
class SecurityResult:
    """Security result."""

    valid: bool
    level: SecurityLevel = SecurityLevel.HIGH
    message: str | None = None
    context: SecurityContext | None = None


T = TypeVar("T")


class SecurityValidator(ABC):
    """Base security validator interface."""

    def __init__(self, name: str = "", enabled: bool = True) -> None:
        """Initialize validator.

        Args:
            name: Validator name
            enabled: Whether validator is enabled
        """
        self.name = name
        self.enabled = enabled

    @abstractmethod
    async def _validate(
        self,
        value: T,
        context: SecurityContext | None = None,
    ) -> SecurityResult:
        """Internal validation method.

        Args:
            value: Value to validate
            context: Optional validation context

        Returns:
            Security result
        """
        raise NotImplementedError

    async def validate(
        self,
        value: T,
        context: SecurityContext | None = None,
    ) -> SecurityResult:
        """Validate value.

        Args:
            value: Value to validate
            context: Optional validation context

        Returns:
            Security result
        """
        if not self.enabled:
            return SecurityResult(
                valid=True,
                level=SecurityLevel.LOW,
                message="Validator is disabled",
                context=context,
            )
        return await self._validate(value, context)


@dataclass
class AuthInfo:
    """Authentication information."""

    username: str
    password: list[str]


class SecurityConfig(ModuleConfig):
    """Security configuration."""

    def __init__(self) -> None:
        """Initialize security configuration."""
        super().__init__(name="security-manager")
        self.auth_info: dict[str, AuthInfo] = {}
        self.enabled = True
        self.level = SecurityLevel.HIGH


class SecurityManager(BaseModule[SecurityConfig]):
    """Security manager implementation."""

    def __init__(self) -> None:
        """Initialize security manager."""
        config = SecurityConfig()
        super().__init__(config)
        self._validators: list[SecurityValidator] = []

    async def _setup(self) -> None:
        """Setup security manager."""
        self._validators.clear()

    async def _teardown(self) -> None:
        """Teardown security manager."""
        self._validators.clear()

    async def authenticate(self, auth_info: AuthInfo) -> None:
        """Authenticate user.

        Args:
            auth_info: Authentication information

        Raises:
            SecurityError: If authentication fails
        """
        self._ensure_initialized()

        if not auth_info.username:
            raise SecurityError("Username is required")

        if not auth_info.password:
            raise SecurityError("Password is required")

        if auth_info.username not in self.config.auth_info:
            raise SecurityError("Invalid username")

        stored_auth = self.config.auth_info[auth_info.username]
        if auth_info.password != stored_auth.password:
            raise SecurityError("Invalid password")

    async def add_validator(self, validator: SecurityValidator) -> None:
        """Add security validator.

        Args:
            validator: Security validator
        """
        self._ensure_initialized()
        self._validators.append(validator)

    async def remove_validator(self, validator: SecurityValidator) -> None:
        """Remove security validator.

        Args:
            validator: Security validator
        """
        self._ensure_initialized()
        self._validators.remove(validator)

    async def validate(
        self,
        value: Any,
        context: SecurityContext | None = None,
    ) -> SecurityResult:
        """Validate value.

        Args:
            value: Value to validate
            context: Optional validation context

        Returns:
            Security result
        """
        self._ensure_initialized()

        if not self.config.enabled:
            return SecurityResult(
                valid=True,
                level=SecurityLevel.LOW,
                message="Security is disabled",
                context=context,
            )

        for validator in self._validators:
            result = await validator.validate(value, context)
            if not result.valid:
                return result

        return SecurityResult(valid=True, context=context)


__all__ = [
    "SecurityLevel",
    "SecurityContext",
    "SecurityResult",
    "SecurityValidator",
    "AuthInfo",
    "SecurityConfig",
    "SecurityManager",
]
