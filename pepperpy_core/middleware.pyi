"""Type stubs for middleware module."""

from typing import Protocol

from pepperpy_core.event import Event

class EventMiddleware(Protocol):
    """Event middleware protocol."""

    def before(self, event: Event) -> None:
        """Called before event is handled."""
        ...

    def after(self, event: Event) -> None:
        """Called after event is handled."""
        ...

    def error(self, event: Event, error: Exception) -> None:
        """Called when error occurs during event handling."""
        ...
