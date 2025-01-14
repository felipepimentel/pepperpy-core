"""Registry module."""

from typing import Generic, List, TypeVar

T = TypeVar("T")


class Registry(Generic[T]):
    """Registry for protocol implementations."""

    def __init__(self, protocol: type[T]) -> None:
        """Initialize registry.

        Args:
            protocol: Protocol to enforce
        """
        self._protocol = protocol
        self._implementations: dict[str, T] = {}

    def register(self, name: str, implementation: T | type[T]) -> None:
        """Register implementation.

        Args:
            name: Implementation name
            implementation: Implementation instance or class

        Raises:
            TypeError: If implementation does not implement protocol
            ValueError: If implementation name is already registered
        """
        if name in self._implementations:
            raise ValueError(f"Implementation {name} already registered")

        # If we got a class, instantiate it
        if isinstance(implementation, type):
            impl = implementation()
        else:
            impl = implementation

        # Check if implementation implements protocol
        if not isinstance(impl, self._protocol):
            raise TypeError(f"{impl.__class__.__name__} does not implement protocol")

        self._implementations[name] = impl

    def get(self, name: str) -> T:
        """Get implementation.

        Args:
            name: Implementation name

        Returns:
            Implementation instance

        Raises:
            KeyError: If implementation not found
        """
        if name not in self._implementations:
            raise KeyError(f"Implementation {name} not found")
        return self._implementations[name]

    def list_implementations(self) -> List[str]:
        """List registered implementations.

        Returns:
            List of implementation names.
        """
        return list(self._implementations.keys())

    def clear(self) -> None:
        """Clear all registered implementations."""
        self._implementations.clear()
