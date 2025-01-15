"""Test serialization module."""

from dataclasses import dataclass
from typing import Any, TypeVar

import pytest

from pepperpy.serialization import (
    BaseSerializable,
    JsonSerializer,
    SerializationError,
)


@dataclass
class TestData:
    """Test data."""

    name: str
    value: Any


class TestSerializable:
    """Test serializable implementation."""

    def __init__(self, name: str, value: Any) -> None:
        """Initialize test serializable."""
        self.name = name
        self.value = value

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {"name": self.name, "value": self.value}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TestSerializable":
        """Create from dictionary."""
        return cls(name=data["name"], value=data["value"])


@dataclass
class TestBaseSerializable(BaseSerializable):
    """Test base serializable implementation."""

    name: str
    value: Any
    _exclude_fields = {"value"}


T = TypeVar("T")


@pytest.fixture
def test_data() -> TestData:
    """Create test data."""
    return TestData(name="test", value=123)


@pytest.fixture
def test_serializable() -> TestSerializable:
    """Create test serializable."""
    return TestSerializable(name="test", value=123)


@pytest.fixture
def test_base_serializable() -> TestBaseSerializable:
    """Create test base serializable."""
    return TestBaseSerializable(name="test", value=123)


@pytest.fixture
def serializer() -> JsonSerializer:
    """Create a serializer."""
    return JsonSerializer()


def test_serializer_serialize(test_data: TestData, serializer: JsonSerializer) -> None:
    """Test serializer serialize."""
    data = serializer.serialize(test_data)
    assert isinstance(data, str)
    assert '"name": "test"' in data
    assert '"value": 123' in data


def test_serializer_deserialize(
    test_data: TestData, serializer: JsonSerializer
) -> None:
    """Test serializer deserialize."""
    data = '{"name": "test", "value": 123}'
    obj = serializer.deserialize(data)
    assert isinstance(obj, dict)
    assert obj["name"] == "test"
    assert obj["value"] == 123


def test_serializer_serialize_list(
    test_data: TestData, serializer: JsonSerializer
) -> None:
    """Test serializer serialize list."""
    data = serializer.serialize([test_data])
    assert isinstance(data, str)
    assert '"name": "test"' in data
    assert '"value": 123' in data


def test_serializer_deserialize_list(
    test_data: TestData, serializer: JsonSerializer
) -> None:
    """Test serializer deserialize list."""
    data = '[{"name": "test", "value": 123}]'
    obj = serializer.deserialize(data)
    assert isinstance(obj, list)
    assert len(obj) == 1
    assert obj[0]["name"] == "test"
    assert obj[0]["value"] == 123


def test_serializer_serialize_dict(
    test_data: TestData, serializer: JsonSerializer
) -> None:
    """Test serializer serialize dict."""
    data = serializer.serialize({"test": test_data})
    assert isinstance(data, str)
    assert '"test"' in data
    assert '"name": "test"' in data
    assert '"value": 123' in data


def test_serializer_deserialize_dict(
    test_data: TestData, serializer: JsonSerializer
) -> None:
    """Test serializer deserialize dict."""
    data = '{"test": {"name": "test", "value": 123}}'
    obj = serializer.deserialize(data)
    assert isinstance(obj, dict)
    assert "test" in obj
    assert obj["test"]["name"] == "test"
    assert obj["test"]["value"] == 123


def test_serializer_serialize_serializable(
    test_serializable: TestSerializable, serializer: JsonSerializer
) -> None:
    """Test serializer serialize serializable."""
    data = serializer.serialize(test_serializable)
    assert isinstance(data, str)
    assert '"name": "test"' in data
    assert '"value": 123' in data


def test_serializer_deserialize_serializable(
    test_serializable: TestSerializable, serializer: JsonSerializer
) -> None:
    """Test serializer deserialize serializable."""
    data = '{"name": "test", "value": 123}'
    obj = serializer.deserialize(data, TestSerializable)
    assert isinstance(obj, TestSerializable)
    assert obj.name == "test"
    assert obj.value == 123


def test_serializer_deserialize_invalid_json(serializer: JsonSerializer) -> None:
    """Test serializer deserialize invalid JSON."""
    with pytest.raises(ValueError):
        serializer.deserialize("invalid json")


def test_serializer_deserialize_invalid_target_type(serializer: JsonSerializer) -> None:
    """Test serializer deserialize invalid target type."""
    data = '{"name": "test", "value": 123}'
    with pytest.raises(TypeError):
        serializer.deserialize(data, TestData)


def test_base_serializable_to_dict(
    test_base_serializable: TestBaseSerializable,
) -> None:
    """Test base serializable to_dict."""
    data = test_base_serializable.to_dict()
    assert isinstance(data, dict)
    assert data == {"name": "test"}  # value is excluded


def test_base_serializable_to_dict_with_exclude(
    test_base_serializable: TestBaseSerializable,
) -> None:
    """Test base serializable to_dict with exclude."""
    data = test_base_serializable.to_dict(exclude={"name"})
    assert isinstance(data, dict)
    assert data == {}  # both name and value are excluded


def test_base_serializable_from_dict() -> None:
    """Test base serializable from_dict."""
    data = {"name": "test", "value": 123, "unknown": "field"}
    obj = TestBaseSerializable.from_dict(data)
    assert isinstance(obj, TestBaseSerializable)
    assert obj.name == "test"
    assert obj.value == 123
    assert not hasattr(obj, "unknown")


def test_base_serializable_update(test_base_serializable: TestBaseSerializable) -> None:
    """Test base serializable update."""
    test_base_serializable.update(name="new_name", value=456, unknown="field")
    assert test_base_serializable.name == "new_name"
    assert test_base_serializable.value == 456
    assert not hasattr(test_base_serializable, "unknown")


def test_base_serializable_repr(test_base_serializable: TestBaseSerializable) -> None:
    """Test base serializable repr."""
    assert (
        repr(test_base_serializable) == "TestBaseSerializable(name='test', value=123)"
    )


def test_serialization_error() -> None:
    """Test serialization error."""
    error = SerializationError(
        "test error",
        ValueError("cause"),
        "object_type",
        "target_type",
    )
    assert str(error) == "test error"
    assert isinstance(error.__cause__, ValueError)
    assert error.object_type == "object_type"
    assert error.target_type == "target_type"
