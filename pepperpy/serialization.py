"""Serialization utilities."""

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Optional, Protocol, TypeVar, runtime_checkable

from .core import PepperpyError


class SerializationError(PepperpyError):
    """Serialization-related errors."""

    def __init__(
        self,
        message: str,
        cause: Optional[Exception] = None,
        object_type: Optional[str] = None,
        target_type: Optional[str] = None,
    ) -> None:
        """Initialize serialization error.

        Args:
            message: Error message
            cause: Optional cause of the error
            object_type: Optional type of the object that caused the error
            target_type: Optional target type for deserialization
        """
        super().__init__(message, cause)
        self.object_type = object_type
        self.target_type = target_type


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

        def _serialize_obj(o: Any) -> Any:
            if is_dataclass(o) and not isinstance(o, type):
                return asdict(o)
            elif hasattr(o, "to_dict"):
                return o.to_dict()
            elif hasattr(o, "__dict__"):
                return o.__dict__
            elif isinstance(o, (list, tuple)):
                return [_serialize_obj(item) for item in o]
            elif isinstance(o, dict):
                return {key: _serialize_obj(value) for key, value in o.items()}
            return o

        data = _serialize_obj(obj)
        return json.dumps(data)

    def deserialize(self, data: str, target_type: type[T] | None = None) -> Any:
        """Deserialize JSON string to object.

        Args:
            data: JSON string to deserialize
            target_type: Optional type to deserialize to

        Returns:
            Deserialized object

        Raises:
            json.JSONDecodeError: If JSON string is invalid
            TypeError: If target_type is provided but does not implement Serializable
        """
        try:
            deserialized = json.loads(data)
        except json.JSONDecodeError as err:
            raise ValueError("Invalid JSON string") from err

        if target_type is not None:
            if not issubclass(target_type, Serializable):
                raise TypeError("Target type must implement Serializable protocol")
            return target_type.from_dict(deserialized)

        return deserialized


__all__ = [
    "Serializable",
    "JsonSerializer",
]
