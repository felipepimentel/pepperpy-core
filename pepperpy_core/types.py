"""Common types and interfaces."""

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class BaseConfig:
    """Base configuration class."""

    name: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate configuration."""
        pass


class BaseValidator(Protocol):
    """Base validator protocol."""

    def validate(self, value: Any) -> None:
        """Validate value.

        Args:
            value: Value to validate

        Raises:
            ValidationError: If validation fails
        """
        ...


class BaseSerializer(Protocol):
    """Base serializer protocol."""

    def serialize(self, value: Any) -> Any:
        """Serialize value.

        Args:
            value: Value to serialize

        Returns:
            Serialized value
        """
        ...

    def deserialize(self, value: Any) -> Any:
        """Deserialize value.

        Args:
            value: Value to deserialize

        Returns:
            Deserialized value
        """
        ...


class BaseFormatter(Protocol):
    """Base formatter protocol."""

    def format(self, value: Any) -> str:
        """Format value.

        Args:
            value: Value to format

        Returns:
            Formatted value
        """
        ...


class BaseParser(Protocol):
    """Base parser protocol."""

    def parse(self, value: str) -> Any:
        """Parse value.

        Args:
            value: Value to parse

        Returns:
            Parsed value
        """
        ...


class BaseConverter(Protocol):
    """Base converter protocol."""

    def convert(self, value: Any) -> Any:
        """Convert value.

        Args:
            value: Value to convert

        Returns:
            Converted value
        """
        ...


class BaseFilter(Protocol):
    """Base filter protocol."""

    def filter(self, value: Any) -> bool:
        """Filter value.

        Args:
            value: Value to filter

        Returns:
            True if value passes filter, False otherwise
        """
        ...


class BaseTransformer(Protocol):
    """Base transformer protocol."""

    def transform(self, value: Any) -> Any:
        """Transform value.

        Args:
            value: Value to transform

        Returns:
            Transformed value
        """
        ...


class BaseHandler(Protocol):
    """Base handler protocol."""

    def handle(self, value: Any) -> None:
        """Handle value.

        Args:
            value: Value to handle
        """
        ...


class BaseProcessor(Protocol):
    """Base processor protocol."""

    def process(self, value: Any) -> Any:
        """Process value.

        Args:
            value: Value to process

        Returns:
            Processed value
        """
        ...


class BaseProvider(Protocol):
    """Base provider protocol."""

    def provide(self) -> Any:
        """Provide value.

        Returns:
            Provided value
        """
        ...


class BaseConsumer(Protocol):
    """Base consumer protocol."""

    def consume(self, value: Any) -> None:
        """Consume value.

        Args:
            value: Value to consume
        """
        ...


class BasePublisher(Protocol):
    """Base publisher protocol."""

    def publish(self, value: Any) -> None:
        """Publish value.

        Args:
            value: Value to publish
        """
        ...


class BaseSubscriber(Protocol):
    """Base subscriber protocol."""

    def subscribe(self, value: Any) -> None:
        """Subscribe to value.

        Args:
            value: Value to subscribe to
        """
        ...


class BaseObserver(Protocol):
    """Base observer protocol."""

    def update(self, value: Any) -> None:
        """Update with value.

        Args:
            value: Value to update with
        """
        ...


class BaseSubject(Protocol):
    """Base subject protocol."""

    def attach(self, observer: BaseObserver) -> None:
        """Attach observer.

        Args:
            observer: Observer to attach
        """
        ...

    def detach(self, observer: BaseObserver) -> None:
        """Detach observer.

        Args:
            observer: Observer to detach
        """
        ...

    def notify(self) -> None:
        """Notify observers."""
        ...


__all__ = [
    "BaseConfig",
    "BaseValidator",
    "BaseSerializer",
    "BaseFormatter",
    "BaseParser",
    "BaseConverter",
    "BaseFilter",
    "BaseTransformer",
    "BaseHandler",
    "BaseProcessor",
    "BaseProvider",
    "BaseConsumer",
    "BasePublisher",
    "BaseSubscriber",
    "BaseObserver",
    "BaseSubject",
]
