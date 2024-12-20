"""Common event types and utilities."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar

from .base import Event, EventMetadata

class SystemEventType(str, Enum):
    """System event types."""
    
    STARTUP = "system.startup"
    SHUTDOWN = "system.shutdown"
    ERROR = "system.error"
    WARNING = "system.warning"
    INFO = "system.info"
    
    MODULE_INIT = "system.module.init"
    MODULE_CLEANUP = "system.module.cleanup"
    MODULE_ERROR = "system.module.error"
    
    CONFIG_CHANGE = "system.config.change"
    CONFIG_ERROR = "system.config.error"
    
    SECURITY_LOGIN = "system.security.login"
    SECURITY_LOGOUT = "system.security.logout"
    SECURITY_ERROR = "system.security.error"

@dataclass
class SystemEventData:
    """Base system event data."""
    
    timestamp: datetime
    source: str
    message: str
    details: dict[str, Any]

class SystemEvent(Event[SystemEventData]):
    """System event implementation."""
    
    def __init__(
        self,
        event_type: SystemEventType,
        message: str,
        source: str = "",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize system event.
        
        Args:
            event_type: Event type
            message: Event message
            source: Event source
            details: Optional event details
        """
        super().__init__(
            name=event_type.value,
            payload=SystemEventData(
                timestamp=datetime.now(),
                source=source,
                message=message,
                details=details or {},
            ),
            metadata=EventMetadata(source=source),
        )

T = TypeVar("T")

@dataclass
class StateChangeEventData(Generic[T]):
    """State change event data."""
    
    old_state: T
    new_state: T
    timestamp: datetime = field(default_factory=datetime.now)
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

class StateChangeEvent(Event[StateChangeEventData[T]], Generic[T]):
    """State change event implementation."""
    
    def __init__(
        self,
        name: str,
        old_state: T,
        new_state: T,
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize state change event.
        
        Args:
            name: Event name
            old_state: Old state
            new_state: New state
            reason: Change reason
            metadata: Optional event metadata
        """
        super().__init__(
            name=name,
            payload=StateChangeEventData(
                old_state=old_state,
                new_state=new_state,
                reason=reason,
                metadata=metadata or {},
            ),
        )

def create_system_event(
    event_type: SystemEventType,
    message: str,
    source: str = "",
    details: dict[str, Any] | None = None,
) -> SystemEvent:
    """Create system event.
    
    Args:
        event_type: Event type
        message: Event message
        source: Event source
        details: Optional event details
        
    Returns:
        System event
    """
    return SystemEvent(
        event_type=event_type,
        message=message,
        source=source,
        details=details,
    )

__all__ = [
    "SystemEvent",
    "SystemEventData",
    "SystemEventType",
    "StateChangeEvent",
    "StateChangeEventData",
    "create_system_event",
] 