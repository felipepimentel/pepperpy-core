"""Tests for the serialization module."""

import json
from dataclasses import dataclass
from typing import Any

import pytest

from pepperpy_core.serialization import JsonSerializer, Serializable


@dataclass
class TestData(Serializable):
    """Test data class."""

    name: str
    value: Any
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert object to dictionary."""
        data = {"name": self.name, "value": self.value}
        if self.metadata is not None:
            data["metadata"] = self.metadata
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TestData":
        """Create object from dictionary."""
        if not isinstance(data, dict):
            raise TypeError("Input must be a dictionary")
        if "name" not in data:
            raise KeyError("Missing required field: name")
        if "value" not in data:
            raise KeyError("Missing required field: value")
        return cls(
            name=data["name"],
            value=data["value"],
            metadata=data.get("metadata"),
        )


def test_serializable_protocol() -> None:
    """Test Serializable protocol."""
    # Test that TestData implements Serializable
    assert isinstance(TestData(name="test", value=42), Serializable)

    # Test to_dict
    data = TestData(name="test", value=42, metadata={"key": "value"})
    serialized = data.to_dict()
    assert isinstance(serialized, dict)
    assert serialized["name"] == "test"
    assert serialized["value"] == 42
    assert serialized["metadata"] == {"key": "value"}

    # Test from_dict
    deserialized = TestData.from_dict(serialized)
    assert isinstance(deserialized, TestData)
    assert deserialized.name == "test"
    assert deserialized.value == 42
    assert deserialized.metadata == {"key": "value"}

    # Test without metadata
    data = TestData(name="test", value=42)
    serialized = data.to_dict()
    assert "metadata" not in serialized
    deserialized = TestData.from_dict(serialized)
    assert deserialized.metadata is None


def test_serializable_list() -> None:
    """Test serialization of lists."""
    # Create test data
    data_list = [
        TestData(name="test1", value=42, metadata={"type": "number"}),
        TestData(name="test2", value="hello", metadata={"type": "string"}),
    ]

    # Test to_dict for list
    serialized = [item.to_dict() for item in data_list]
    assert isinstance(serialized, list)
    assert len(serialized) == 2
    assert all(isinstance(item, dict) for item in serialized)
    assert all("metadata" in item for item in serialized)

    # Test from_dict for list
    deserialized = [TestData.from_dict(item) for item in serialized]
    assert isinstance(deserialized, list)
    assert len(deserialized) == 2
    assert all(isinstance(item, TestData) for item in deserialized)
    assert deserialized[0].name == "test1"
    assert deserialized[0].value == 42
    assert deserialized[0].metadata == {"type": "number"}
    assert deserialized[1].name == "test2"
    assert deserialized[1].value == "hello"
    assert deserialized[1].metadata == {"type": "string"}


def test_serializable_validation() -> None:
    """Test serialization validation."""
    # Test missing required fields
    with pytest.raises(KeyError, match="Missing required field: name"):
        TestData.from_dict({})  # Missing name and value

    with pytest.raises(KeyError, match="Missing required field: value"):
        TestData.from_dict({"name": "test"})  # Missing value

    with pytest.raises(KeyError, match="Missing required field: name"):
        TestData.from_dict({"value": 42})  # Missing name

    # Test with invalid types
    with pytest.raises(TypeError, match="Input must be a dictionary"):
        TestData.from_dict([])  # type: ignore

    with pytest.raises(TypeError, match="Input must be a dictionary"):
        TestData.from_dict("not a dict")  # type: ignore


def test_serializable_edge_cases() -> None:
    """Test serialization edge cases."""
    # Test with None values
    data = TestData(name="test", value=None)
    serialized = data.to_dict()
    assert serialized["value"] is None
    deserialized = TestData.from_dict(serialized)
    assert deserialized.value is None

    # Test with empty strings
    data = TestData(name="", value="")
    serialized = data.to_dict()
    assert serialized["name"] == ""
    assert serialized["value"] == ""
    deserialized = TestData.from_dict(serialized)
    assert deserialized.name == ""
    assert deserialized.value == ""

    # Test with complex values
    complex_value = {
        "nested": {"key": "value"},
        "list": [1, 2, 3],
        "tuple": (4, 5, 6),
    }
    data = TestData(name="test", value=complex_value)
    serialized = data.to_dict()
    assert serialized["value"] == complex_value
    deserialized = TestData.from_dict(serialized)
    assert deserialized.value == complex_value


def test_json_serializer() -> None:
    """Test JSON serializer."""
    serializer = JsonSerializer()

    # Test with dataclass
    data = TestData(name="test", value=42, metadata={"key": "value"})
    json_str = serializer.serialize(data)
    assert isinstance(json_str, str)
    deserialized = serializer.deserialize(json_str)
    assert isinstance(deserialized, dict)
    assert deserialized["name"] == "test"
    assert deserialized["value"] == 42
    assert deserialized["metadata"] == {"key": "value"}

    # Test with dict
    data = {"name": "test", "value": 42}
    json_str = serializer.serialize(data)
    assert isinstance(json_str, str)
    deserialized = serializer.deserialize(json_str)
    assert deserialized == data

    # Test with list
    data = [1, 2, 3]
    json_str = serializer.serialize(data)
    assert isinstance(json_str, str)
    deserialized = serializer.deserialize(json_str)
    assert deserialized == data

    # Test with primitive types
    assert serializer.serialize(42) == "42"
    assert serializer.serialize("test") == '"test"'
    assert serializer.serialize(True) == "true"
    assert serializer.serialize(None) == "null"


def test_json_serializer_errors() -> None:
    """Test JSON serializer error handling."""
    serializer = JsonSerializer()

    # Test with invalid JSON
    with pytest.raises(json.JSONDecodeError):
        serializer.deserialize("invalid json")

    # Test with unserializable object
    class UnserializableObject:
        def __init__(self) -> None:
            self._value = object()  # An object() is not JSON serializable

    with pytest.raises(TypeError):
        serializer.serialize(UnserializableObject())


def test_json_serializer_with_to_dict() -> None:
    """Test JSON serializer with objects that have to_dict method."""
    serializer = JsonSerializer()

    class CustomObject:
        def __init__(self, value: str) -> None:
            self.value = value

        def to_dict(self) -> dict[str, Any]:
            return {"value": self.value}

    obj = CustomObject("test")
    json_str = serializer.serialize(obj)
    assert isinstance(json_str, str)
    deserialized = serializer.deserialize(json_str)
    assert deserialized == {"value": "test"}
