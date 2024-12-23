"""Validation functionality."""

import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from re import Pattern
from typing import Any, Generic, TypeVar

from .exceptions import ValidationError


class ValidationLevel(Enum):
    """Validation level types."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

    def __str__(self) -> str:
        """Return string representation."""
        return self.value


@dataclass
class ValidationContext:
    """Validation context with metadata."""

    path: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    parent: "ValidationContext | None" = None
    _children: list["ValidationContext"] = field(default_factory=list, init=False)
    _cleanup_handlers: list[Callable[[], Any]] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        """Validate context."""
        if not isinstance(self.path, str):
            raise ValidationError(
                f"path must be a string, got {type(self.path).__name__}"
            )
        if not isinstance(self.metadata, dict):
            raise ValidationError(
                f"metadata must be a dictionary, got {type(self.metadata).__name__}"
            )

    async def __aenter__(self) -> "ValidationContext":
        """Enter async context."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context and run cleanup handlers."""
        for handler in self._cleanup_handlers:
            try:
                result = handler()
                if hasattr(result, "__await__"):
                    await result
            except Exception:
                pass  # Ignore cleanup errors


@dataclass
class ValidationResult:
    """Validation result."""

    valid: bool
    level: ValidationLevel = ValidationLevel.ERROR
    message: str | None = None
    context: ValidationContext | None = None


T = TypeVar("T")


class Validator(ABC, Generic[T]):
    """Base validator interface."""

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
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Internal validation method.

        Args:
            value: Value to validate
            context: Optional validation context

        Returns:
            Validation result
        """
        raise NotImplementedError

    async def validate(
        self,
        value: T,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate value.

        Args:
            value: Value to validate
            context: Optional validation context

        Returns:
            Validation result
        """
        if not self.enabled:
            return ValidationResult(
                valid=True,
                level=ValidationLevel.INFO,
                message="Validator is disabled",
                context=context,
            )
        return await self._validate(value, context)

    async def validate_many(
        self,
        values: list[T],
        context: ValidationContext | None = None,
    ) -> list[ValidationResult]:
        """Validate multiple values.

        Args:
            values: Values to validate
            context: Optional validation context

        Returns:
            List of validation results
        """
        return [await self.validate(value, context) for value in values]


class RequiredValidator(Validator[Any]):
    """Validates that a value is not None."""

    async def _validate(
        self,
        value: Any,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate value is not None.

        Args:
            value: Value to validate
            context: Optional validation context

        Returns:
            Validation result
        """
        if value is None:
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message="Value is required",
                context=context,
            )
        return ValidationResult(valid=True, context=context)


class TypeValidator(Validator[Any]):
    """Validates value type."""

    def __init__(
        self,
        expected_type: type | tuple[type, ...],
        name: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize validator.

        Args:
            expected_type: Expected type(s)
            name: Validator name
            enabled: Whether validator is enabled
        """
        super().__init__(name=name, enabled=enabled)
        self.expected_type = expected_type

    async def _validate(
        self,
        value: Any,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate value type.

        Args:
            value: Value to validate
            context: Optional validation context

        Returns:
            Validation result
        """
        if not isinstance(value, self.expected_type):
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=(
                    f"Expected type {self.expected_type}, got {type(value).__name__}"
                ),
                context=context,
            )
        return ValidationResult(valid=True, context=context)


class RangeValidator(Validator[int | float]):
    """Validates numeric range."""

    def __init__(
        self,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        inclusive: bool = True,
        name: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize validator.

        Args:
            min_value: Minimum value (inclusive)
            max_value: Maximum value (inclusive)
            inclusive: Whether range is inclusive
            name: Validator name
            enabled: Whether validator is enabled
        """
        super().__init__(name=name, enabled=enabled)
        self.min_value = min_value
        self.max_value = max_value
        self.inclusive = inclusive

    async def _validate(
        self,
        value: int | float,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate numeric range.

        Args:
            value: Value to validate
            context: Optional validation context

        Returns:
            Validation result
        """
        if self.min_value is not None:
            if self.inclusive and value < self.min_value:
                return ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Value must be >= {self.min_value}",
                    context=context,
                )
            if not self.inclusive and value <= self.min_value:
                return ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Value must be > {self.min_value}",
                    context=context,
                )

        if self.max_value is not None:
            if self.inclusive and value > self.max_value:
                return ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Value must be <= {self.max_value}",
                    context=context,
                )
            if not self.inclusive and value >= self.max_value:
                return ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Value must be < {self.max_value}",
                    context=context,
                )

        return ValidationResult(valid=True, context=context)


class LengthValidator(Validator[str | list | dict]):
    """Validates length of strings, lists, or dictionaries."""

    def __init__(
        self,
        min_length: int | None = None,
        max_length: int | None = None,
        name: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize validator.

        Args:
            min_length: Minimum length
            max_length: Maximum length
            name: Validator name
            enabled: Whether validator is enabled
        """
        super().__init__(name=name, enabled=enabled)
        self.min_length = min_length
        self.max_length = max_length

    async def _validate(
        self,
        value: str | list | dict,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate length.

        Args:
            value: Value to validate
            context: Optional validation context

        Returns:
            Validation result
        """
        length = len(value)

        if self.min_length is not None and length < self.min_length:
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Length must be >= {self.min_length}",
                context=context,
            )

        if self.max_length is not None and length > self.max_length:
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Length must be <= {self.max_length}",
                context=context,
            )

        return ValidationResult(valid=True, context=context)


class PatternValidator(Validator[str]):
    """Validates string patterns using regex."""

    def __init__(
        self,
        pattern: str | Pattern[str],
        name: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize validator.

        Args:
            pattern: Regex pattern
            name: Validator name
            enabled: Whether validator is enabled
        """
        super().__init__(name=name, enabled=enabled)
        self.pattern = pattern if isinstance(pattern, Pattern) else re.compile(pattern)

    async def _validate(
        self,
        value: str,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate pattern.

        Args:
            value: Value to validate
            context: Optional validation context

        Returns:
            Validation result
        """
        if not self.pattern.match(value):
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Value must match pattern {self.pattern.pattern}",
                context=context,
            )
        return ValidationResult(valid=True, context=context)


class PathValidator(Validator[Path | str]):
    """Validates file system paths."""

    def __init__(
        self,
        must_exist: bool = True,
        must_be_file: bool = False,
        must_be_dir: bool = False,
        name: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize validator.

        Args:
            must_exist: Whether path must exist
            must_be_file: Whether path must be a file
            must_be_dir: Whether path must be a directory
            name: Validator name
            enabled: Whether validator is enabled
        """
        super().__init__(name=name, enabled=enabled)
        self.must_exist = must_exist
        self.must_be_file = must_be_file
        self.must_be_dir = must_be_dir

    async def _validate(
        self,
        value: Path | str,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate path.

        Args:
            value: Value to validate
            context: Optional validation context

        Returns:
            Validation result
        """
        path = Path(value)

        if self.must_exist and not path.exists():
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Path {path} does not exist",
                context=context,
            )

        if self.must_be_file and not path.is_file():
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Path {path} is not a file",
                context=context,
            )

        if self.must_be_dir and not path.is_dir():
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Path {path} is not a directory",
                context=context,
            )

        return ValidationResult(valid=True, context=context)


# Common validator instances
required = RequiredValidator()
is_string = TypeValidator(str)
is_int = TypeValidator(int)
is_float = TypeValidator((int, float))
is_bool = TypeValidator(bool)
is_list = TypeValidator(list)
is_dict = TypeValidator(dict)
is_path = TypeValidator((str, Path))


# Helper functions
def in_range(
    min_value: int | float | None = None,
    max_value: int | float | None = None,
    inclusive: bool = True,
) -> RangeValidator:
    """Create range validator."""
    return RangeValidator(min_value, max_value, inclusive)


def length_between(
    min_length: int | None = None,
    max_length: int | None = None,
) -> LengthValidator:
    """Create length validator."""
    return LengthValidator(min_length, max_length)


__all__ = [
    # Base types
    "ValidationLevel",
    "ValidationContext",
    "ValidationResult",
    "Validator",
    # Validator classes
    "RequiredValidator",
    "TypeValidator",
    "RangeValidator",
    "LengthValidator",
    "PatternValidator",
    "PathValidator",
    # Common instances
    "required",
    "is_string",
    "is_int",
    "is_float",
    "is_bool",
    "is_list",
    "is_dict",
    "is_path",
    # Helper functions
    "in_range",
    "length_between",
]
