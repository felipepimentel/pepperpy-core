"""Validators module.

This module provides validation utilities for PepperPy.
It includes validators for common data types, protocols, and custom validation rules.
"""

import re
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, TypeVar, cast

from .core import PepperpyError


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
        super().__init__(message, cause)
        self.field_name = field_name
        self.invalid_value = invalid_value


T = TypeVar("T")


class BaseValidator(ABC, Generic[T]):
    """Base validator class."""

    @abstractmethod
    def validate(self, value: Any) -> T:
        """Validate value."""
        raise NotImplementedError


class DictValidator(BaseValidator[Dict[Any, Any]]):
    """Dict validator class."""

    def __init__(
        self, key_validator: BaseValidator[Any], value_validator: BaseValidator[Any]
    ) -> None:
        """Initialize validator."""
        self._key_validator = key_validator
        self._value_validator = value_validator

    def validate(self, value: Any) -> Dict[Any, Any]:
        """Validate value."""
        if not isinstance(value, dict):
            raise ValidationError("Value must be a dict")
        return {
            self._key_validator.validate(k): self._value_validator.validate(v)
            for k, v in value.items()
        }


class ListValidator(BaseValidator[List[Any]]):
    """List validator class."""

    def __init__(self, validator: BaseValidator[Any]) -> None:
        """Initialize validator."""
        self._validator = validator

    def validate(self, value: Any) -> List[Any]:
        """Validate value."""
        if not isinstance(value, list):
            raise ValidationError("Value must be a list")
        return [self._validator.validate(v) for v in value]


class StringValidator(BaseValidator[str]):
    """String validator class."""

    def validate(self, value: Any) -> str:
        """Validate value."""
        if not isinstance(value, str):
            raise ValidationError("Value must be a string")
        return value


class IntegerValidator(BaseValidator[int]):
    """Integer validator class."""

    def validate(self, value: Any) -> int:
        """Validate value."""
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValidationError("Value must be an integer")
        return cast(int, value)


class EmailValidator(BaseValidator[str]):
    """Email validator class."""

    _EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def validate(self, value: Any) -> str:
        """Validate value."""
        if not isinstance(value, str):
            raise ValidationError("Value must be a string")
        if not self._EMAIL_PATTERN.match(value):
            raise ValidationError("Invalid email address")
        return value


class URLValidator(BaseValidator[str]):
    """URL validator class."""

    _URL_PATTERN = re.compile(
        r"^(http|https|ftp)://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/[a-zA-Z0-9._/-]*)?$"
    )

    def validate(self, value: Any) -> str:
        """Validate value."""
        if not isinstance(value, str):
            raise ValidationError("Value must be a string")
        if not self._URL_PATTERN.match(value):
            raise ValidationError("Invalid URL")
        return value


class IPAddressValidator(BaseValidator[str]):
    """IP address validator class."""

    _IP_PATTERN = re.compile(
        r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    )

    def validate(self, value: Any) -> str:
        """Validate value."""
        if not isinstance(value, str):
            raise ValidationError("Value must be a string")
        if not self._IP_PATTERN.match(value):
            raise ValidationError("Invalid IP address")
        return value


class PhoneNumberValidator(BaseValidator[str]):
    """Phone number validator class."""

    _PHONE_PATTERN = re.compile(r"^\+\d+(?:[ -]\d+)*$")

    def validate(self, value: Any) -> str:
        """Validate value."""
        if not isinstance(value, str):
            raise ValidationError("Value must be a string")
        if not self._PHONE_PATTERN.match(value):
            raise ValidationError("Invalid phone number")
        return value


def validate_type(value: Any, expected_type: type[T]) -> T:
    """Validate that a value matches an expected type.

    This utility function provides runtime type checking to ensure type safety
    when working with external data or configuration values.

    Example:
        ```python
        # Validates that the value is a string
        name = validate_type(config.get("name"), str)

        # Validates that the value is a list of integers
        numbers = validate_type(data.get("numbers"), list[int])
        ```

    Args:
        value: The value to validate
        expected_type: The expected type of the value

    Returns:
        The validated value with proper typing

    Raises:
        TypeError: If value is not of expected type
    """
    if not isinstance(value, expected_type):
        raise TypeError(
            f"Expected {expected_type.__name__}, got {type(value).__name__}"
        )
    return value


def validate_protocol(value: Any, protocol: type) -> Any:
    """Validate protocol.

    Args:
        value: Value to validate
        protocol: Protocol to validate against

    Returns:
        Validated value

    Raises:
        TypeError: If value does not implement protocol
    """
    if not isinstance(value, protocol):
        raise TypeError(f"Value does not implement {protocol.__name__}")
    return value


__all__ = [
    "BaseValidator",
    "DictValidator",
    "ListValidator",
    "StringValidator",
    "IntegerValidator",
    "EmailValidator",
    "URLValidator",
    "IPAddressValidator",
    "PhoneNumberValidator",
    "validate_type",
    "validate_protocol",
]
