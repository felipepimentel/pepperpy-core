"""Validators module."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional, Type


@dataclass
class ValidationResult:
    """Validation result."""

    is_valid: bool
    message: Optional[str] = None


class BaseValidator(ABC):
    """Base validator."""

    @abstractmethod
    def validate(self, value: Any) -> ValidationResult:
        """Validate value.

        Args:
            value: Value to validate.

        Returns:
            Validation result.
        """
        ...


class TypeValidator(BaseValidator):
    """Type validator."""

    def __init__(self, type_: Type[Any]) -> None:
        """Initialize type validator.

        Args:
            type_: Type to validate against.
        """
        self.type = type_

    def validate(self, value: Any) -> ValidationResult:
        """Validate value.

        Args:
            value: Value to validate.

        Returns:
            Validation result.

        Raises:
            ValueError: If value is not of the expected type.
        """
        if not isinstance(value, self.type):
            raise ValueError(
                f"Expected {self.type.__name__}, got {type(value).__name__}"
            )
        return ValidationResult(True)


class ChainValidator(BaseValidator):
    """Chain validator."""

    def __init__(self, validators: List[BaseValidator]) -> None:
        """Initialize chain validator.

        Args:
            validators: List of validators to chain.
        """
        self.validators = validators

    def validate(self, value: Any) -> ValidationResult:
        """Validate value.

        Args:
            value: Value to validate.

        Returns:
            Validation result.

        Raises:
            ValueError: If any validator fails.
        """
        for validator in self.validators:
            try:
                result = validator.validate(value)
                if not result.is_valid:
                    raise ValueError(result.message or "Validation failed")
            except ValueError as e:
                raise ValueError(str(e)) from e
        return ValidationResult(True)
