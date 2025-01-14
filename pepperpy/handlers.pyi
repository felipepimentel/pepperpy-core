"""Type stubs for handlers module."""

from typing import Protocol

from pepperpy.event import Event

class EventHandler(Protocol):
    """Event handler protocol."""

    def handle(self, event: Event) -> None:
        """Handle event."""
        ...
