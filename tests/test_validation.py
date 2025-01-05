"""Test validation module."""

from dataclasses import dataclass
from typing import Any

import pytest

from pepperpy_core.exceptions import ValidationError
from pepperpy_core.validators import (
    DictValidator,
    EmailValidator,
    IPAddressValidator,
    ListValidator,
    PhoneNumberValidator,
    StringValidator,
    URLValidator,
)


@dataclass
class TestData:
    """Test data."""

    name: str
    value: Any


@pytest.fixture
def test_data() -> TestData:
    """Create test data."""
    return TestData(name="test", value=123)


def test_validate_string() -> None:
    """Test validate string."""
    validator = StringValidator()
    assert validator.validate("test") == "test"
    assert validator.validate("") == ""

    with pytest.raises(ValidationError):
        validator.validate(123)

    with pytest.raises(ValidationError):
        validator.validate(True)

    with pytest.raises(ValidationError):
        validator.validate([])


def test_validate_list() -> None:
    """Test validate list."""
    item_validator = StringValidator()
    validator = ListValidator(item_validator)
    assert validator.validate(["1", "2", "3"]) == ["1", "2", "3"]
    assert validator.validate([]) == []

    with pytest.raises(ValidationError):
        validator.validate("test")

    with pytest.raises(ValidationError):
        validator.validate(123)

    with pytest.raises(ValidationError):
        validator.validate(True)


def test_validate_dict() -> None:
    """Test validate dict."""
    key_validator = StringValidator()
    value_validator = StringValidator()
    validator = DictValidator(key_validator, value_validator)
    assert validator.validate({"test": "test"}) == {"test": "test"}
    assert validator.validate({}) == {}

    with pytest.raises(ValidationError):
        validator.validate("test")

    with pytest.raises(ValidationError):
        validator.validate(123)

    with pytest.raises(ValidationError):
        validator.validate(True)


def test_validate_email() -> None:
    """Test validate email."""
    validator = EmailValidator()
    assert validator.validate("test@example.com") == "test@example.com"
    assert validator.validate("test.user@example.co.uk") == "test.user@example.co.uk"

    with pytest.raises(ValidationError):
        validator.validate("invalid")

    with pytest.raises(ValidationError):
        validator.validate("invalid@")

    with pytest.raises(ValidationError):
        validator.validate("@invalid")

    with pytest.raises(ValidationError):
        validator.validate("invalid@invalid")

    with pytest.raises(ValidationError):
        validator.validate(123)


def test_validate_url() -> None:
    """Test validate URL."""
    validator = URLValidator()
    assert validator.validate("http://example.com") == "http://example.com"
    assert validator.validate("https://example.com") == "https://example.com"
    assert validator.validate("ftp://example.com") == "ftp://example.com"
    assert validator.validate("http://example.com/path") == "http://example.com/path"
    assert (
        validator.validate("https://example.com/path/to/resource")
        == "https://example.com/path/to/resource"
    )

    with pytest.raises(ValidationError):
        validator.validate("invalid")

    with pytest.raises(ValidationError):
        validator.validate("http://")

    with pytest.raises(ValidationError):
        validator.validate("http://invalid")

    with pytest.raises(ValidationError):
        validator.validate(123)


def test_validate_ip_address() -> None:
    """Test validate IP address."""
    validator = IPAddressValidator()
    assert validator.validate("192.168.0.1") == "192.168.0.1"
    assert validator.validate("10.0.0.0") == "10.0.0.0"
    assert validator.validate("172.16.0.1") == "172.16.0.1"
    assert validator.validate("255.255.255.255") == "255.255.255.255"
    assert validator.validate("0.0.0.0") == "0.0.0.0"

    with pytest.raises(ValidationError):
        validator.validate("invalid")

    with pytest.raises(ValidationError):
        validator.validate("256.256.256.256")

    with pytest.raises(ValidationError):
        validator.validate("1.2.3")

    with pytest.raises(ValidationError):
        validator.validate(123)


def test_validate_phone_number() -> None:
    """Test validate phone number."""
    validator = PhoneNumberValidator()
    assert validator.validate("+1234567890") == "+1234567890"
    assert validator.validate("+44 1234567890") == "+44 1234567890"
    assert validator.validate("+55 11 12345-6789") == "+55 11 12345-6789"
    assert validator.validate("+1-234-567-8900") == "+1-234-567-8900"
    assert validator.validate("+86 123 4567 8900") == "+86 123 4567 8900"

    with pytest.raises(ValidationError):
        validator.validate("invalid")

    with pytest.raises(ValidationError):
        validator.validate("123")

    with pytest.raises(ValidationError):
        validator.validate("abc123")

    with pytest.raises(ValidationError):
        validator.validate(123)

    with pytest.raises(ValidationError):
        validator.validate("1234567890")  # Missing + prefix
