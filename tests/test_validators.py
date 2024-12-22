"""Validator tests."""

from pathlib import Path

import pytest

from pepperpy_core.exceptions import ValidationError
from pepperpy_core.validation import (
    LengthValidator,
    PathValidator,
    PatternValidator,
    RangeValidator,
    RequiredValidator,
    TypeValidator,
    ValidationContext,
    ValidationLevel,
    in_range,
    is_bool,
    is_dict,
    is_float,
    is_int,
    is_list,
    is_path,
    is_string,
    length_between,
    required,
)


def test_validation_level() -> None:
    """Test validation level enum."""
    assert str(ValidationLevel.INFO) == "info"
    assert str(ValidationLevel.WARNING) == "warning"
    assert str(ValidationLevel.ERROR) == "error"
    assert str(ValidationLevel.CRITICAL) == "critical"


@pytest.mark.asyncio
async def test_validation_context() -> None:
    """Test validation context."""
    # Test basic context
    context = ValidationContext(path="test.path", metadata={"key": "value"})
    assert context.path == "test.path"
    assert context.metadata == {"key": "value"}
    assert context.parent is None

    # Test invalid context
    with pytest.raises(ValidationError, match="path must be a string"):
        ValidationContext(path=123)  # type: ignore
    with pytest.raises(ValidationError, match="metadata must be a dictionary"):
        ValidationContext(path="test", metadata="invalid")  # type: ignore

    # Test context manager
    cleanup_called = False

    async def cleanup() -> None:
        nonlocal cleanup_called
        cleanup_called = True

    async with ValidationContext(path="test") as ctx:
        ctx._cleanup_handlers.append(cleanup)
        assert not cleanup_called

    assert cleanup_called

    # Test nested contexts
    parent = ValidationContext(path="parent")
    child = ValidationContext(path="child", parent=parent)
    assert child.parent == parent


@pytest.mark.asyncio
async def test_regex_validation() -> None:
    """Test regex validation."""
    # Test basic patterns
    validator = PatternValidator(pattern=r"^test\d+$")
    result = await validator.validate("test123")
    assert result.valid
    result = await validator.validate("invalid")
    assert not result.valid
    assert result.level == ValidationLevel.ERROR
    assert "must match pattern" in str(result.message)

    # Test with context
    context = ValidationContext(path="test.field")
    result = await validator.validate("invalid", context=context)
    assert result.context == context

    # Test with compiled pattern
    validator = PatternValidator(pattern=r"^test\d+$", name="test_pattern")
    assert validator.name == "test_pattern"
    result = await validator.validate("test123")
    assert result.valid


@pytest.mark.asyncio
async def test_length_validation() -> None:
    """Test length validation."""
    # Test basic length validation
    validator = LengthValidator(min_length=2, max_length=5)
    result = await validator.validate("123")
    assert result.valid
    result = await validator.validate("1")
    assert not result.valid
    assert ">= 2" in str(result.message)
    result = await validator.validate("123456")
    assert not result.valid
    assert "<= 5" in str(result.message)

    # Test with only min_length
    validator = LengthValidator(min_length=2)
    result = await validator.validate("123456")
    assert result.valid
    result = await validator.validate("1")
    assert not result.valid

    # Test with only max_length
    validator = LengthValidator(max_length=5)
    result = await validator.validate("123")
    assert result.valid
    result = await validator.validate("123456")
    assert not result.valid

    # Test with context
    context = ValidationContext(path="test.field")
    result = await validator.validate("123456", context=context)
    assert result.context == context


@pytest.mark.asyncio
async def test_type_validation() -> None:
    """Test type validation."""
    # Test single type
    validator = TypeValidator(expected_type=int)
    result = await validator.validate(123)
    assert result.valid
    result = await validator.validate("123")
    assert not result.valid
    assert "Expected type" in str(result.message)

    # Test multiple types
    validator = TypeValidator(expected_type=(int, str))
    result = await validator.validate(123)
    assert result.valid
    result = await validator.validate("123")
    assert result.valid
    result = await validator.validate(12.3)
    assert not result.valid

    # Test with context
    context = ValidationContext(path="test.field")
    result = await validator.validate(12.3, context=context)
    assert result.context == context


@pytest.mark.asyncio
async def test_required_validation() -> None:
    """Test required validation."""
    validator = RequiredValidator()
    result = await validator.validate("value")
    assert result.valid
    result = await validator.validate(None)
    assert not result.valid
    assert result.message == "Value is required"
    assert result.level == ValidationLevel.ERROR

    # Test with context
    context = ValidationContext(path="test.field")
    result = await validator.validate(None, context=context)
    assert result.context == context


@pytest.mark.asyncio
async def test_range_validation() -> None:
    """Test range validation."""
    # Test inclusive range
    validator = RangeValidator(min_value=0, max_value=10)
    result = await validator.validate(5)
    assert result.valid
    result = await validator.validate(0)
    assert result.valid
    result = await validator.validate(10)
    assert result.valid
    result = await validator.validate(-1)
    assert not result.valid
    assert "must be >=" in str(result.message)
    result = await validator.validate(11)
    assert not result.valid
    assert "must be <=" in str(result.message)

    # Test exclusive range
    validator = RangeValidator(min_value=0, max_value=10, inclusive=False)
    result = await validator.validate(5)
    assert result.valid
    result = await validator.validate(0)
    assert not result.valid
    assert "must be >" in str(result.message)
    result = await validator.validate(10)
    assert not result.valid
    assert "must be <" in str(result.message)

    # Test with only min_value
    validator = RangeValidator(min_value=0)
    result = await validator.validate(5)
    assert result.valid
    result = await validator.validate(-1)
    assert not result.valid

    # Test with only max_value
    validator = RangeValidator(max_value=10)
    result = await validator.validate(5)
    assert result.valid
    result = await validator.validate(11)
    assert not result.valid

    # Test with float values
    validator = RangeValidator(min_value=0.0, max_value=1.0)
    result = await validator.validate(0.5)
    assert result.valid
    result = await validator.validate(1.5)
    assert not result.valid

    # Test with context
    context = ValidationContext(path="test.field")
    result = await validator.validate(11, context=context)
    assert result.context == context


@pytest.mark.asyncio
async def test_path_validation() -> None:
    """Test path validation."""
    # Create test files and directories
    test_dir = Path("test_dir")
    test_file = test_dir / "test_file.txt"
    test_dir.mkdir(exist_ok=True)
    test_file.touch()

    try:
        # Test basic path validation
        validator = PathValidator()
        result = await validator.validate(test_dir)
        assert result.valid
        result = await validator.validate(test_file)
        assert result.valid
        result = await validator.validate("nonexistent")
        assert not result.valid
        assert "does not exist" in str(result.message)

        # Test file validation
        validator = PathValidator(must_be_file=True)
        result = await validator.validate(test_file)
        assert result.valid
        result = await validator.validate(test_dir)
        assert not result.valid
        assert "is not a file" in str(result.message)

        # Test directory validation
        validator = PathValidator(must_be_dir=True)
        result = await validator.validate(test_dir)
        assert result.valid
        result = await validator.validate(test_file)
        assert not result.valid
        assert "is not a directory" in str(result.message)

        # Test with string paths
        validator = PathValidator(must_be_file=True)
        result = await validator.validate(str(test_file))
        assert result.valid

        # Test with context
        context = ValidationContext(path="test.field")
        result = await validator.validate("nonexistent", context=context)
        assert result.context == context

    finally:
        # Clean up test files
        test_file.unlink()
        test_dir.rmdir()


@pytest.mark.asyncio
async def test_validate_many() -> None:
    """Test multiple validations."""
    # Test with pattern validator
    validator = PatternValidator(pattern=r"^test\d+$")
    results = await validator.validate_many(["test123", "test", "test456"])
    assert results[0].valid
    assert not results[1].valid
    assert results[2].valid

    # Test with type validator
    validator = TypeValidator(expected_type=int)
    results = await validator.validate_many([123, "123", 456])
    assert results[0].valid
    assert not results[1].valid
    assert results[2].valid

    # Test with context
    context = ValidationContext(path="test.field")
    results = await validator.validate_many([123, "123"], context=context)
    assert all(r.context == context for r in results)


@pytest.mark.asyncio
async def test_validator_enabled() -> None:
    """Test validator enabled flag."""
    validator = TypeValidator(expected_type=int, enabled=False)
    assert not validator.enabled
    result = await validator.validate("not an int")
    assert result.valid  # Should pass because validator is disabled
    assert result.level == ValidationLevel.INFO  # Should be INFO level when disabled


@pytest.mark.asyncio
async def test_common_validators() -> None:
    """Test common validator instances."""
    # Test required validator
    result = await required.validate("value")
    assert result.valid
    result = await required.validate(None)
    assert not result.valid

    # Test type validators
    result = await is_string.validate("test")
    assert result.valid
    result = await is_string.validate(123)
    assert not result.valid

    result = await is_int.validate(123)
    assert result.valid
    result = await is_int.validate("123")
    assert not result.valid

    result = await is_float.validate(123)
    assert result.valid
    result = await is_float.validate(123.45)
    assert result.valid
    result = await is_float.validate("123.45")
    assert not result.valid

    result = await is_bool.validate(True)
    assert result.valid
    result = await is_bool.validate(1)
    assert not result.valid

    result = await is_list.validate([1, 2, 3])
    assert result.valid
    result = await is_list.validate((1, 2, 3))
    assert not result.valid

    result = await is_dict.validate({"key": "value"})
    assert result.valid
    result = await is_dict.validate([("key", "value")])
    assert not result.valid

    result = await is_path.validate("test.txt")
    assert result.valid
    result = await is_path.validate(Path("test.txt"))
    assert result.valid
    result = await is_path.validate(123)
    assert not result.valid


@pytest.mark.asyncio
async def test_helper_functions() -> None:
    """Test validator helper functions."""
    # Test in_range helper
    validator = in_range(0, 10)
    result = await validator.validate(5)
    assert result.valid
    result = await validator.validate(-1)
    assert not result.valid

    # Test length_between helper
    validator = length_between(2, 5)
    result = await validator.validate("123")
    assert result.valid
    result = await validator.validate("1")
    assert not result.valid
