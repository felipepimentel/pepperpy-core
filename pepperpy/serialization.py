"""Serialization utilities."""

import json
from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, ClassVar, Optional, Protocol, TypeVar, runtime_checkable

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


T = TypeVar("T", bound="BaseSerializable")


@dataclass
class BaseSerializable:
    """Base class for serializable objects with enhanced features.

    This class provides advanced serialization capabilities including:
    - Field exclusion during serialization
    - Field validation during deserialization
    - Instance field updates
    - Improved string representation
    """

    # Class variables
    _exclude_fields: ClassVar[set[str]] = set()

    def to_dict(self, exclude: set[str] | None = None) -> dict[str, Any]:
        """Convert to dictionary.

        Args:
            exclude: Optional set of field names to exclude from the dictionary.

        Returns:
            Dictionary representation with optional field exclusion.
        """
        exclude_set = exclude or set()
        exclude_set.update(self._exclude_fields)

        data = asdict(self)
        return {k: v for k, v in data.items() if k not in exclude_set and v is not None}

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        """Create instance from dictionary.

        Args:
            data: Dictionary containing instance data.

        Returns:
            Instance of this class.

        Example:
            >>> data = {"field": "value"}
            >>> instance = BaseSerializable.from_dict(data)
        """
        # Filter out unknown fields
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)

    def update(self, **kwargs: Any) -> None:
        """Update instance fields with new values.

        Args:
            **kwargs: Field names and values to update.

        Example:
            >>> instance.update(field="new_value")
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self) -> str:
        """Get string representation.

        Returns:
            String representation of the instance.
        """
        fields = [f"{k}={v!r}" for k, v in self.to_dict().items()]
        return f"{self.__class__.__name__}({', '.join(fields)})"


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
    "BaseSerializable",
]
