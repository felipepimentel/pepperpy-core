"""Test validators implementation."""

from typing import Protocol, runtime_checkable

import pytest

from pepperpy.validators import (
    DictValidator,
    EmailValidator,
    IntegerValidator,
    IPAddressValidator,
    ListValidator,
    PhoneNumberValidator,
    StringValidator,
    URLValidator,
    ValidationError,
    validate_protocol,
    validate_type,
)


@runtime_checkable
class TestProtocol(Protocol):
    """Test protocol."""

    def test_method(self) -> None:
        """Test method."""
        pass


class TestClass:
    """Test class."""

    def test_method(self) -> None:
        """Test method."""
        pass


def test_string_validator() -> None:
    """Test string validator."""
    validator = StringValidator()
    assert validator.validate("test") == "test"
    with pytest.raises(ValidationError):
        validator.validate(123)


def test_integer_validator() -> None:
    """Test integer validator."""
    validator = IntegerValidator()
    assert validator.validate(123) == 123
    with pytest.raises(ValidationError):
        validator.validate("test")
    with pytest.raises(ValidationError):
        validator.validate(True)


def test_list_validator() -> None:
    """Test list validator."""
    validator = ListValidator(StringValidator())
    assert validator.validate(["test"]) == ["test"]
    with pytest.raises(ValidationError):
        validator.validate("test")
    with pytest.raises(ValidationError):
        validator.validate([123])


def test_dict_validator() -> None:
    """Test dict validator."""
    validator = DictValidator(StringValidator(), IntegerValidator())
    assert validator.validate({"test": 123}) == {"test": 123}
    with pytest.raises(ValidationError):
        validator.validate("test")
    with pytest.raises(ValidationError):
        validator.validate({123: "test"})


def test_email_validator() -> None:
    """Test email validator."""
    validator = EmailValidator()
    assert validator.validate("test@example.com") == "test@example.com"
    with pytest.raises(ValidationError):
        validator.validate("test")
    with pytest.raises(ValidationError):
        validator.validate("test@")
    with pytest.raises(ValidationError):
        validator.validate("test@example")


def test_url_validator() -> None:
    """Test URL validator."""
    validator = URLValidator()
    assert validator.validate("http://example.com") == "http://example.com"
    assert validator.validate("https://example.com/path") == "https://example.com/path"
    with pytest.raises(ValidationError):
        validator.validate("test")
    with pytest.raises(ValidationError):
        validator.validate("http://")
    with pytest.raises(ValidationError):
        validator.validate("http://example")


def test_ip_address_validator() -> None:
    """Test IP address validator."""
    validator = IPAddressValidator()
    assert validator.validate("192.168.0.1") == "192.168.0.1"
    with pytest.raises(ValidationError):
        validator.validate("test")
    with pytest.raises(ValidationError):
        validator.validate("256.256.256.256")
    with pytest.raises(ValidationError):
        validator.validate("192.168.0")


def test_phone_number_validator() -> None:
    """Test phone number validator."""
    validator = PhoneNumberValidator()
    assert validator.validate("+1234567890") == "+1234567890"
    assert validator.validate("+1 234 567 890") == "+1 234 567 890"
    with pytest.raises(ValidationError):
        validator.validate("test")
    with pytest.raises(ValidationError):
        validator.validate("1234567890")
    with pytest.raises(ValidationError):
        validator.validate("+abcdefghij")


def test_validate_type() -> None:
    """Test validate type."""
    assert validate_type("test", str) == "test"
    with pytest.raises(TypeError):
        validate_type(123, str)


def test_validate_protocol() -> None:
    """Test validate protocol."""
    value = TestClass()
    assert validate_protocol(value, TestProtocol) == value
    with pytest.raises(TypeError):
        validate_protocol("test", TestProtocol)
