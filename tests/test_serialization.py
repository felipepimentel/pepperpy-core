"""Test serialization module."""

from dataclasses import dataclass
from typing import Any, TypeVar

import pytest

from pepperpy_core.serialization import JsonSerializer


@dataclass
class TestData:
    """Test data."""

    name: str
    value: Any


T = TypeVar("T")


@pytest.fixture
def test_data() -> TestData:
    """Create test data."""
    return TestData(name="test", value=123)


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
