"""Tests for the serialization module."""

from dataclasses import dataclass, field
from typing import Any

import pytest

from pepperpy_core.serialization import JsonSerializer, Serializable


@pytest.fixture
def test_data() -> type[Serializable]:
    """Create a test data class."""

    @dataclass
    class Data:
        """Test data class."""

        name: str
        value: int
        metadata: dict[str, Any] = field(default_factory=dict)

        def to_dict(self) -> dict[str, Any]:
            """Convert to dictionary."""
            return {
                "name": self.name,
                "value": self.value,
                "metadata": self.metadata,
            }

        @classmethod
        def from_dict(cls, data: dict[str, Any]) -> "Data":
            """Create from dictionary."""
            if "name" not in data:
                raise KeyError("Name is required")
            if "value" not in data:
                raise KeyError("Value is required")
            if not isinstance(data["name"], str):
                raise TypeError("Name must be a string")
            if not isinstance(data["value"], int):
                raise TypeError("Value must be an integer")
            return cls(
                name=data["name"],
                value=data["value"],
                metadata=data.get("metadata", {}),
            )

    return Data


def test_serializable_protocol(test_data: type[Serializable]) -> None:
    """Test serializable protocol."""
    data = test_data("test", 42, {"key": "value"})
    assert isinstance(data, Serializable)

    # Test to_dict
    data_dict = data.to_dict()
    assert data_dict["name"] == "test"
    assert data_dict["value"] == 42
    assert data_dict["metadata"] == {"key": "value"}

    # Test from_dict
    new_data = test_data.from_dict(data_dict)
    assert new_data.name == "test"
    assert new_data.value == 42
    assert new_data.metadata == {"key": "value"}


def test_serializable_list(test_data: type[Serializable]) -> None:
    """Test serializable list."""
    data_list = [
        test_data("test1", 1),
        test_data("test2", 2, {"key": "value"}),
    ]

    # Convert to list of dicts
    dict_list = [data.to_dict() for data in data_list]
    assert len(dict_list) == 2
    assert dict_list[0]["name"] == "test1"
    assert dict_list[1]["name"] == "test2"

    # Convert back to objects
    new_list = [test_data.from_dict(d) for d in dict_list]
    assert len(new_list) == 2
    assert new_list[0].name == "test1"
    assert new_list[1].name == "test2"
    assert new_list[1].metadata == {"key": "value"}


def test_serializable_validation(test_data: type[Serializable]) -> None:
    """Test serializable validation."""
    # Test missing required field
    with pytest.raises(KeyError):
        test_data.from_dict({"value": 42})

    with pytest.raises(KeyError):
        test_data.from_dict({"name": "test"})


def test_serializable_edge_cases(test_data: type[Serializable]) -> None:
    """Test serializable edge cases."""
    # Test empty metadata
    data = test_data("test", 42)
    assert data.metadata == {}

    # Test None values
    with pytest.raises(TypeError):
        test_data.from_dict({"name": None, "value": 42})

    # Test invalid types
    with pytest.raises(TypeError):
        test_data.from_dict({"name": 42, "value": "test"})


def test_json_serializer(test_data: type[Serializable]) -> None:
    """Test JSON serializer."""
    serializer = JsonSerializer()
    data = test_data("test", 42, {"key": "value"})

    # Test serialization
    json_str = serializer.serialize(data)
    assert isinstance(json_str, str)
    assert "test" in json_str
    assert "42" in json_str
    assert "key" in json_str
    assert "value" in json_str

    # Test deserialization
    deserialized = serializer.deserialize(json_str, test_data)
    assert isinstance(deserialized, test_data)
    assert deserialized.name == "test"
    assert deserialized.value == 42
    assert deserialized.metadata == {"key": "value"}


def test_json_serializer_errors(test_data: type[Serializable]) -> None:
    """Test JSON serializer error handling."""
    serializer = JsonSerializer()

    # Test invalid JSON
    with pytest.raises(ValueError):
        serializer.deserialize("invalid json", test_data)

    # Test missing fields
    with pytest.raises(KeyError):
        serializer.deserialize('{"value": 42}', test_data)


def test_json_serializer_with_to_dict() -> None:
    """Test JSON serializer with to_dict method."""
    serializer = JsonSerializer()

    class CustomData:
        """Custom data class."""

        def __init__(self, name: str, value: int) -> None:
            """Initialize custom data."""
            self.name = name
            self.value = value

        def to_dict(self) -> dict[str, Any]:
            """Convert to dictionary."""
            return {"name": self.name, "value": self.value}

    data = CustomData("test", 42)
    json_str = serializer.serialize(data)
    assert isinstance(json_str, str)
    assert "test" in json_str
    assert "42" in json_str
