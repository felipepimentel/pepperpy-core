"""Validators module."""

import re
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, TypeVar, cast

from pepperpy_core.exceptions import ValidationError

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
