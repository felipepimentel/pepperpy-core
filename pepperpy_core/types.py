"""Core types and type definitions."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Protocol, TypeVar

# JSON types
JsonPrimitive = str | int | float | bool | None
JsonValue = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]
JsonDict = dict[str, JsonValue]
JsonList = list[JsonValue]


@dataclass
class BaseData:
    """Base data class for all data objects."""

    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate data object.

        Raises:
            ValueError: If validation fails
        """
        pass


@dataclass
class BaseConfigData(BaseData):
    """Base configuration data class."""

    name: str = field(default="")

    def validate(self) -> None:
        """Validate configuration data.

        Raises:
            ValueError: If validation fails
        """
        super().validate()
        if not self.name.strip():
            raise ValueError("name must not be empty")


class BaseValidator(Protocol[T]):
    """Base validator protocol."""

    async def validate(self, value: T) -> bool:
        """Validate value.

        Args:
            value: Value to validate

        Returns:
            True if value is valid
        """
        ...


class BaseFactory(Protocol[T]):
    """Base factory protocol."""

    def create(self) -> T:
        """Create new instance.

        Returns:
            New instance
        """
        ...


class BaseHandler(Protocol):
    """Base handler protocol."""

    async def handle(self, data: Any) -> Any:
        """Handle data.

        Args:
            data: Data to handle

        Returns:
            Handled data
        """
        ...


class BaseProcessor(Protocol):
    """Base processor protocol."""

    async def process(self, data: Any) -> Any:
        """Process data.

        Args:
            data: Data to process

        Returns:
            Processed data
        """
        ...


class BaseFormatter(Protocol):
    """Base formatter protocol."""

    def format(self, data: Any) -> str:
        """Format data.

        Args:
            data: Data to format

        Returns:
            Formatted string
        """
        ...


class BaseParser(Protocol):
    """Base parser protocol."""

    def parse(self, data: str) -> Any:
        """Parse data.

        Args:
            data: Data to parse

        Returns:
            Parsed data
        """
        ...


class BaseSerializer(Protocol):
    """Base serializer protocol."""

    def serialize(self, data: Any) -> bytes:
        """Serialize data.

        Args:
            data: Data to serialize

        Returns:
            Serialized data
        """
        ...

    def deserialize(self, data: bytes) -> Any:
        """Deserialize data.

        Args:
            data: Data to deserialize

        Returns:
            Deserialized data
        """
        ...


__all__ = [
    "JsonPrimitive",
    "JsonValue",
    "JsonDict",
    "JsonList",
    "BaseData",
    "BaseConfigData",
    "BaseValidator",
    "BaseFactory",
    "BaseHandler",
    "BaseProcessor",
    "BaseFormatter",
    "BaseParser",
    "BaseSerializer",
] 