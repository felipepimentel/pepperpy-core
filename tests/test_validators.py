"""Validator tests."""

import pytest

from pepperpy_core.validation import (
    LengthValidator,
    PatternValidator,
    TypeValidator,
    ValidationResult,
)


@pytest.mark.asyncio
async def test_regex_validation() -> None:
    """Test regex validation."""
    validator = PatternValidator(pattern=r"^test\d+$")
    result = await validator.validate("test123")
    assert result.valid
    result = await validator.validate("invalid")
    assert not result.valid


@pytest.mark.asyncio
async def test_regex_custom_message() -> None:
    """Test regex validation with custom message."""
    validator = PatternValidator(
        pattern=r"^test\d+$",
        name="Must start with 'test' followed by numbers",
    )
    assert validator.name == "Must start with 'test' followed by numbers"


@pytest.mark.asyncio
async def test_length_validation() -> None:
    """Test length validation."""
    validator = LengthValidator(min_length=2, max_length=5)
    result = await validator.validate("123")
    assert result.valid
    result = await validator.validate("1")
    assert not result.valid
    result = await validator.validate("123456")
    assert not result.valid


@pytest.mark.asyncio
async def test_type_validation() -> None:
    """Test type validation."""
    validator = TypeValidator(expected_type=int)
    result = await validator.validate(123)
    assert result.valid
    result = await validator.validate("123")
    assert not result.valid


@pytest.mark.asyncio
async def test_validate_many() -> None:
    """Test multiple validations."""
    validator = PatternValidator(pattern=r"^test\d+$")
    results: list[ValidationResult] = await validator.validate_many(["test123", "test"])
    assert results[0].valid
    assert not results[1].valid
