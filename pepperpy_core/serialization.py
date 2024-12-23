"""Serialization utilities."""

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Protocol, TypeVar, runtime_checkable


@runtime_checkable
class Serializable(Protocol):
    """Protocol for serializable objects."""

    def to_dict(self) -> dict[str, Any]:
        """Convert object to dictionary.

        Returns:
            Dictionary representation of object
        """
        ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Serializable":
        """Create object from dictionary.

        Args:
            data: Dictionary representation of object

        Returns:
            Created object
        """
        ...


T = TypeVar("T", bound=Serializable)


class JsonSerializer:
    """JSON serializer implementation."""

    def serialize(self, obj: Any) -> str:
        """Serialize object to JSON string.

        Args:
            obj: Object to serialize

        Returns:
            JSON string

        Raises:
            TypeError: If object cannot be serialized to JSON
        """
        if is_dataclass(obj):
            data = asdict(obj)
        elif hasattr(obj, "to_dict"):
            data = obj.to_dict()  # type: ignore
        elif hasattr(obj, "__dict__"):
            data = obj.__dict__
        else:
            data = obj

        return json.dumps(data)

    def deserialize(self, data: str) -> Any:
        """Deserialize JSON string to object.

        Args:
            data: JSON string to deserialize

        Returns:
            Deserialized object

        Raises:
            json.JSONDecodeError: If JSON string is invalid
        """
        return json.loads(data)


__all__ = [
    "Serializable",
    "JsonSerializer",
]