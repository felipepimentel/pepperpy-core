"""Serialization module."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol, runtime_checkable

from pepperpy.core import PepperpyError
from pepperpy.module import BaseModule, ModuleConfig


class SerializationError(PepperpyError):
    """Serialization error."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, details, cause)


@runtime_checkable
class BaseSerializable(Protocol):
    """Base serializable protocol."""

    def serialize(self) -> Dict[str, Any]:
        """Serialize object.

        Returns:
            Serialized object
        """
        ...

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Deserialize object.

        Args:
            data: Serialized object
        """
        ...


@dataclass
class SerializationConfig(ModuleConfig):
    """Serialization configuration."""

    name: str = "serialization_manager"
    metadata: Dict[str, Any] = field(default_factory=dict)


class SerializationManager(BaseModule[SerializationConfig]):
    """Serialization manager."""

    def __init__(self, config: Optional[SerializationConfig] = None) -> None:
        """Initialize serialization manager.

        Args:
            config: Serialization configuration
        """
        super().__init__(config or SerializationConfig())

    def _ensure_initialized(self) -> None:
        """Ensure manager is initialized.

        Raises:
            SerializationError: If manager is not initialized
        """
        if not self.is_initialized:
            raise SerializationError(
                "Serialization manager is not initialized",
                {"manager_name": self.config.name},
            )

    async def _setup(self) -> None:
        """Set up serialization manager."""
        pass

    async def _teardown(self) -> None:
        """Clean up serialization manager."""
        pass

    def serialize(self, obj: BaseSerializable) -> Dict[str, Any]:
        """Serialize object.

        Args:
            obj: Object to serialize

        Returns:
            Serialized object

        Raises:
            SerializationError: If object cannot be serialized
        """
        self._ensure_initialized()
        try:
            return obj.serialize()
        except Exception as e:
            raise SerializationError(
                "Failed to serialize object",
                {"object_type": type(obj).__name__},
                e,
            ) from e

    def deserialize(self, obj: BaseSerializable, data: Dict[str, Any]) -> None:
        """Deserialize object.

        Args:
            obj: Object to deserialize
            data: Serialized object

        Raises:
            SerializationError: If object cannot be deserialized
        """
        self._ensure_initialized()
        try:
            obj.deserialize(data)
        except Exception as e:
            raise SerializationError(
                "Failed to deserialize object",
                {"object_type": type(obj).__name__},
                e,
            ) from e


__all__ = [
    "BaseSerializable",
    "SerializationConfig",
    "SerializationError",
    "SerializationManager",
]
