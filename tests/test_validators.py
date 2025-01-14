"""Test validators module."""

from dataclasses import dataclass
from typing import Any

import pytest

from pepperpy.exceptions import ValidationError
from pepperpy.validators import (
    DictValidator,
    EmailValidator,
    IntegerValidator,
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


def test_dict_validator() -> None:
    """Test dict validator."""
    key_validator = StringValidator()
    value_validator = IntegerValidator()
    validator = DictValidator(key_validator, value_validator)

    # Test valid dictionary
    test_dict = {"a": 1, "b": 2, "c": 3}
    assert validator.validate(test_dict) == test_dict

    # Test invalid key type
    with pytest.raises(ValidationError):
        validator.validate({1: 1})

    # Test invalid value type
    with pytest.raises(ValidationError):
        validator.validate({"a": "1"})

    # Test invalid input type
    with pytest.raises(ValidationError):
        validator.validate("test")


def test_list_validator() -> None:
    """Test list validator."""
    item_validator = IntegerValidator()
    validator = ListValidator(item_validator)

    # Test valid list
    test_list = [1, 2, 3]
    assert validator.validate(test_list) == test_list

    # Test invalid item type
    with pytest.raises(ValidationError):
        validator.validate(["1", "2", "3"])

    # Test invalid input type
    with pytest.raises(ValidationError):
        validator.validate("test")


def test_string_validator() -> None:
    """Test string validator."""
    validator = StringValidator()

    # Test valid string
    assert validator.validate("test") == "test"
    assert validator.validate("") == ""

    # Test invalid types
    with pytest.raises(ValidationError):
        validator.validate(123)

    with pytest.raises(ValidationError):
        validator.validate(True)

    with pytest.raises(ValidationError):
        validator.validate([])


def test_integer_validator() -> None:
    """Test integer validator."""
    validator = IntegerValidator()

    # Test valid integers
    assert validator.validate(123) == 123
    assert validator.validate(0) == 0
    assert validator.validate(-123) == -123

    # Test invalid types
    with pytest.raises(ValidationError):
        validator.validate("123")

    with pytest.raises(ValidationError):
        validator.validate(123.45)

    with pytest.raises(ValidationError):
        validator.validate(True)

    with pytest.raises(ValidationError):
        validator.validate([])


def test_email_validator() -> None:
    """Test email validator."""
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


def test_url_validator() -> None:
    """Test URL validator."""
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


def test_ip_address_validator() -> None:
    """Test IP address validator."""
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


def test_phone_number_validator() -> None:
    """Test phone number validator."""
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
