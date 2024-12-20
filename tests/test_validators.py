"""Validator tests."""

import pytest
from pepperpy_core.validators import (
    LengthValidator,
    RegexValidator,
    TypeValidator,
    validate_many,
)


@pytest.mark.asyncio
async def test_regex_validation() -> None:
    """Test regex validation."""
    validator = RegexValidator(pattern=r"^test\d+$")
    assert await validator.validate("test123")
    assert not await validator.validate("invalid")


@pytest.mark.asyncio
async def test_regex_custom_message() -> None:
    """Test regex validation with custom message."""
    validator = RegexValidator(
        pattern=r"^test\d+$", message="Must start with 'test' followed by numbers"
    )
    assert validator.message == "Must start with 'test' followed by numbers"


@pytest.mark.asyncio
async def test_length_validation() -> None:
    """Test length validation."""
    validator = LengthValidator(min_length=2, max_length=5)
    assert await validator.validate("123")
    assert not await validator.validate("1")
    assert not await validator.validate("123456")


@pytest.mark.asyncio
async def test_type_validation() -> None:
    """Test type validation."""
    validator = TypeValidator(expected_type=int)
    assert await validator.validate(123)
    assert not await validator.validate("123")


@pytest.mark.asyncio
async def test_validate_many() -> None:
    """Test multiple validations."""
    validators = [
        RegexValidator(pattern=r"^test\d+$"),
        LengthValidator(min_length=6, max_length=10),
    ]
    assert await validate_many("test123", validators)
    assert not await validate_many("test", validators)
