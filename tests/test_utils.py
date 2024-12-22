"""Tests for the utils module."""

from datetime import UTC, datetime

from pepperpy_core.utils import (
    format_datetime,
    get_type_name,
    parse_datetime,
    safe_cast,
    utcnow,
)


def test_utcnow() -> None:
    """Test utcnow function."""
    now = utcnow()
    assert isinstance(now, datetime)
    assert now.tzinfo == UTC

    # Test that the time is close to the current time
    system_now = datetime.now(UTC)
    assert abs((now - system_now).total_seconds()) < 1


def test_format_datetime() -> None:
    """Test format_datetime function."""
    dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    formatted = format_datetime(dt)
    assert formatted == "2024-01-01T12:00:00+00:00"


def test_parse_datetime() -> None:
    """Test parse_datetime function."""
    dt_str = "2024-01-01T12:00:00+00:00"
    parsed = parse_datetime(dt_str)
    assert isinstance(parsed, datetime)
    assert parsed.year == 2024
    assert parsed.month == 1
    assert parsed.day == 1
    assert parsed.hour == 12
    assert parsed.minute == 0
    assert parsed.second == 0
    assert parsed.tzinfo is not None

    # Test invalid datetime string
    try:
        parse_datetime("invalid")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_get_type_name() -> None:
    """Test get_type_name function."""
    assert get_type_name(42) == "int"
    assert get_type_name("hello") == "str"
    assert get_type_name([1, 2, 3]) == "list"
    assert get_type_name({"a": 1}) == "dict"
    assert get_type_name(None) == "NoneType"


def test_safe_cast() -> None:
    """Test safe_cast function."""
    # Test successful casts
    assert safe_cast("42", int) == 42
    assert safe_cast(42, str) == "42"
    assert safe_cast("3.14", float) == 3.14
    assert safe_cast(True, int) == 1
    assert safe_cast([1, 2, 3], list) == [1, 2, 3]  # Identity cast

    # Test failed casts
    assert safe_cast("not a number", int) is None
    assert safe_cast("not a float", float) is None
    assert safe_cast(None, int) is None
    assert safe_cast({"a": 1}, datetime) is None  # dict cannot be converted to datetime
