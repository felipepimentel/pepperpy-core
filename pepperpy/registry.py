"""Registry module.

A generic registry for managing protocol implementations. This module provides a
type-safe container for registering and retrieving implementations of specific
protocols or interfaces.

The Registry pattern implemented here is independent of the module system and can
be used to manage any type of protocol implementation. This separation of
concerns allows for:

1. Type-safe registration and retrieval
2. Protocol-based implementation management
3. Flexible implementation discovery
4. Runtime protocol validation

Example:
    ```python
    from typing import Protocol

    class DataStore(Protocol):
        def save(self, data: bytes) -> None: ...
        def load(self) -> bytes: ...

    # Create registry for DataStore implementations
    registry = Registry[DataStore](DataStore)

    # Register implementations
    registry.register("memory", MemoryStore())
    registry.register("file", FileStore)  # Classes are instantiated automatically

    # Get implementation
    store = registry.get("memory")
    store.save(b"data")
    ```
"""

from typing import Generic, List, Optional, TypeVar

from .core import PepperpyError


class RegistryError(PepperpyError):
    """Registry-related errors."""

    def __init__(
        self,
        message: str,
        cause: Optional[Exception] = None,
        implementation_name: Optional[str] = None,
        protocol_name: Optional[str] = None,
    ) -> None:
        """Initialize registry error.

        Args:
            message: Error message
            cause: Optional cause of the error
            implementation_name: Optional name of the implementation that caused
                the error
            protocol_name: Optional name of the protocol that caused the error
        """
        super().__init__(message, cause)
        self.implementation_name = implementation_name
        self.protocol_name = protocol_name


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
