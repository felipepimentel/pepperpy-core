"""Registry implementation module."""

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from .exceptions import PepperpyError
from .module import BaseModule, ModuleConfig


class RegistryError(PepperpyError):
    """Registry specific error."""

    pass


@dataclass
class RegistryConfig(ModuleConfig):
    """Registry configuration."""

    # Required fields (inherited from ModuleConfig)
    name: str

    # Optional fields
    enabled: bool = True
    max_items: int = 1000
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate configuration."""
        if self.max_items < 1:
            raise ValueError("max_items must be greater than 0")


T = TypeVar("T")


@dataclass
class RegistryItem(Generic[T]):
    """Registry item."""

    name: str
    value: T
    metadata: dict[str, Any] = field(default_factory=dict)


class Registry(Generic[T], BaseModule[RegistryConfig]):
    """Registry implementation."""

    def __init__(self) -> None:
        """Initialize registry."""
        config = RegistryConfig(name="registry")
        super().__init__(config)
        self._items: dict[str, RegistryItem[T]] = {}

    async def _setup(self) -> None:
        """Setup registry."""
        self._items.clear()

    async def _teardown(self) -> None:
        """Teardown registry."""
        self._items.clear()

    async def get_stats(self) -> dict[str, Any]:
        """Get registry statistics.

        Returns:
            Registry statistics
        """
        self._ensure_initialized()
        return {
            "name": self.config.name,
            "enabled": self.config.enabled,
            "total_items": len(self._items),
            "item_names": list(self._items.keys()),
            "max_items": self.config.max_items,
        }

    def register(
        self, name: str, value: T, metadata: dict[str, Any] | None = None
    ) -> None:
        """Register item.

        Args:
            name: Item name
            value: Item value
            metadata: Optional item metadata

        Raises:
            RegistryError: If registry is full or item already exists
        """
        self._ensure_initialized()

        if len(self._items) >= self.config.max_items:
            raise RegistryError("Registry is full")

        if name in self._items:
            raise RegistryError(f"Item {name} already exists")

        self._items[name] = RegistryItem(
            name=name,
            value=value,
            metadata=metadata or {},
        )

    def unregister(self, name: str) -> None:
        """Unregister item.

        Args:
            name: Item name

        Raises:
            KeyError: If item not found
        """
        self._ensure_initialized()

        if name not in self._items:
            raise KeyError(f"Item {name} not found")

        del self._items[name]

    def get(self, name: str) -> T:
        """Get item value.

        Args:
            name: Item name

        Returns:
            Item value

        Raises:
            KeyError: If item not found
        """
        self._ensure_initialized()

        if name not in self._items:
            raise KeyError(f"Item {name} not found")

        return self._items[name].value

    def get_item(self, name: str) -> RegistryItem[T]:
        """Get item.

        Args:
            name: Item name

        Returns:
            Registry item

        Raises:
            KeyError: If item not found
        """
        self._ensure_initialized()

        if name not in self._items:
            raise KeyError(f"Item {name} not found")

        return self._items[name]

    def list_items(self) -> list[RegistryItem[T]]:
        """List all items.

        Returns:
            List of registry items
        """
        self._ensure_initialized()
        return list(self._items.values())

    def clear(self) -> None:
        """Clear registry."""
        self._ensure_initialized()
        self._items.clear()


__all__ = [
    "RegistryError",
    "RegistryConfig",
    "RegistryItem",
    "Registry",
]
