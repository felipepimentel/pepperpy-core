"""Test validators module."""

from typing import Any, Sequence

import pytest

from pepperpy.validators import (
    ChainValidator,
    TypeValidator,
    ValidationResult,
)


class OptionalValidator(TypeValidator):
    """Optional validator."""

    def __init__(self, inner_validator: TypeValidator) -> None:
        """Initialize optional validator."""
        self.inner_validator = inner_validator

    def validate(self, value: Any) -> ValidationResult:
        """Validate value."""
        if value is None:
            return ValidationResult(True)
        try:
            result = self.inner_validator.validate(value)
            if not result.is_valid:
                raise ValueError(f"Invalid value: {value}")
            return result
        except ValueError as e:
            raise ValueError(f"Invalid value: {value}") from e


class ListValidator(TypeValidator):
    """List validator."""

    def __init__(self, inner_validator: TypeValidator) -> None:
        """Initialize list validator."""
        self.inner_validator = inner_validator

    def validate(self, value: Any) -> ValidationResult:
        """Validate value."""
        if not isinstance(value, list):
            raise ValueError(f"Expected list, got {type(value)}")
        for item in value:
            try:
                result = self.inner_validator.validate(item)
                if not result.is_valid:
                    raise ValueError(f"Invalid item: {item}")
            except ValueError as e:
                raise ValueError(f"Invalid item: {item}") from e
        return ValidationResult(True)


class DictValidator(TypeValidator):
    """Dict validator."""

    def __init__(self, value_validator: TypeValidator) -> None:
        """Initialize dict validator."""
        self.value_validator = value_validator

    def validate(self, value: Any) -> ValidationResult:
        """Validate value."""
        if not isinstance(value, dict):
            raise ValueError(f"Expected dict, got {type(value)}")
        for k, v in value.items():
            try:
                result = self.value_validator.validate(v)
                if not result.is_valid:
                    raise ValueError(f"Invalid value for key {k}: {v}")
            except ValueError as e:
                raise ValueError(f"Invalid value for key {k}: {v}") from e
        return ValidationResult(True)


class UnionValidator(TypeValidator):
    """Union validator."""

    def __init__(self, validators: Sequence[TypeValidator]) -> None:
        """Initialize union validator."""
        self.validators = validators

    def validate(self, value: Any) -> ValidationResult:
        """Validate value."""
        errors = []
        for validator in self.validators:
            try:
                result = validator.validate(value)
                if result.is_valid:
                    return result
            except ValueError as e:
                errors.append(str(e))
        raise ValueError(f"No validator accepted value: {value}. Errors: {errors}")


class TransformValidator(TypeValidator):
    """Transform validator."""

    def __init__(self, transform: Any) -> None:
        """Initialize transform validator."""
        self.transform = transform

    def validate(self, value: Any) -> ValidationResult:
        """Validate value."""
        try:
            _ = self.transform(value)
            return ValidationResult(True)
        except Exception as e:
            raise ValueError(f"Transform failed: {e}") from e


def test_type_validator_valid() -> None:
    """Test type validator with valid input."""
    validator = TypeValidator(str)
    result = validator.validate("test")
    assert isinstance(result, ValidationResult)
    assert result.is_valid


def test_type_validator_invalid() -> None:
    """Test type validator with invalid input."""
    validator = TypeValidator(str)
    with pytest.raises(ValueError):
        validator.validate(123)


def test_optional_validator_valid() -> None:
    """Test optional validator with valid input."""
    validator = OptionalValidator(TypeValidator(str))
    result = validator.validate("test")
    assert isinstance(result, ValidationResult)
    assert result.is_valid

    result = validator.validate(None)
    assert isinstance(result, ValidationResult)
    assert result.is_valid


def test_optional_validator_invalid() -> None:
    """Test optional validator with invalid input."""
    validator = OptionalValidator(TypeValidator(str))
    with pytest.raises(ValueError):
        validator.validate(123)


def test_list_validator_valid() -> None:
    """Test list validator with valid input."""
    validator = ListValidator(TypeValidator(str))
    result = validator.validate(["test1", "test2"])
    assert isinstance(result, ValidationResult)
    assert result.is_valid


def test_list_validator_invalid() -> None:
    """Test list validator with invalid input."""
    validator = ListValidator(TypeValidator(str))
    with pytest.raises(ValueError):
        validator.validate([123, "test"])


def test_dict_validator_valid() -> None:
    """Test dict validator with valid input."""
    validator = DictValidator(TypeValidator(str))
    result = validator.validate({"key": "value"})
    assert isinstance(result, ValidationResult)
    assert result.is_valid


def test_dict_validator_invalid() -> None:
    """Test dict validator with invalid input."""
    validator = DictValidator(TypeValidator(str))
    with pytest.raises(ValueError):
        validator.validate({"key": 123})


def test_union_validator_valid() -> None:
    """Test union validator with valid input."""
    validator = UnionValidator([TypeValidator(str), TypeValidator(int)])
    result = validator.validate("test")
    assert isinstance(result, ValidationResult)
    assert result.is_valid

    result = validator.validate(123)
    assert isinstance(result, ValidationResult)
    assert result.is_valid


def test_union_validator_invalid() -> None:
    """Test union validator with invalid input."""
    validator = UnionValidator([TypeValidator(str), TypeValidator(int)])
    with pytest.raises(ValueError):
        validator.validate(1.23)


def test_chain_validator_valid() -> None:
    """Test chain validator with valid input."""

    def transform(value: str) -> str:
        return value.upper()

    validator = ChainValidator([TypeValidator(str), TransformValidator(transform)])
    result = validator.validate("test")
    assert isinstance(result, ValidationResult)
    assert result.is_valid


def test_chain_validator_invalid() -> None:
    """Test chain validator with invalid input."""

    def transform(value: str) -> str:
        return value.upper()

    validator = ChainValidator([TypeValidator(str), TransformValidator(transform)])
    with pytest.raises(ValueError):
        validator.validate(123)
