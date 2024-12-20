"""Base event system types and interfaces."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Generic, Protocol, TypeVar
from uuid import UUID, uuid4

from ..config.base import BaseConfig
from ..exceptions.base import EventError
from ..validation.base import ValidationResult, Validator

class EventStatus(Enum):
    """Event status types."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

class EventPriority(Enum):
    """Event priority levels."""
    
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

    def __int__(self) -> int:
        """Convert to integer."""
        return self.value

    def __lt__(self, other: "EventPriority") -> bool:
        """Compare priorities."""
        return self.value < other.value

    def __gt__(self, other: "EventPriority") -> bool:
        """Compare priorities."""
        return self.value > other.value

@dataclass
class EventMetadata:
    """Event metadata."""
    
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    correlation_id: UUID = field(default_factory=uuid4)
    causation_id: UUID = field(default_factory=uuid4)
    metadata: dict[str, Any] = field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds
    status: EventStatus = EventStatus.PENDING
    processing_time: timedelta | None = None
    error_count: int = 0
    last_error: str | None = None
    tags: list[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Validate metadata."""
        if not isinstance(self.timestamp, datetime):
            raise EventError(f"timestamp must be a datetime, got {type(self.timestamp).__name__}")
        if not isinstance(self.source, str):
            raise EventError(f"source must be a string, got {type(self.source).__name__}")
        if not isinstance(self.correlation_id, UUID):
            raise EventError(f"correlation_id must be a UUID, got {type(self.correlation_id).__name__}")
        if not isinstance(self.causation_id, UUID):
            raise EventError(f"causation_id must be a UUID, got {type(self.causation_id).__name__}")
        if not isinstance(self.metadata, dict):
            raise EventError(f"metadata must be a dictionary, got {type(self.metadata).__name__}")
        if not isinstance(self.priority, EventPriority):
            raise EventError(f"priority must be an EventPriority, got {type(self.priority).__name__}")
        if not isinstance(self.retry_count, int):
            raise EventError(f"retry_count must be an integer, got {type(self.retry_count).__name__}")
        if self.retry_count < 0:
            raise EventError(f"retry_count must be non-negative, got {self.retry_count}")
        if not isinstance(self.max_retries, int):
            raise EventError(f"max_retries must be an integer, got {type(self.max_retries).__name__}")
        if self.max_retries < 0:
            raise EventError(f"max_retries must be non-negative, got {self.max_retries}")
        if not isinstance(self.retry_delay, (int, float)):
            raise EventError(f"retry_delay must be a number, got {type(self.retry_delay).__name__}")
        if self.retry_delay < 0:
            raise EventError(f"retry_delay must be non-negative, got {self.retry_delay}")
        if not isinstance(self.status, EventStatus):
            raise EventError(f"status must be an EventStatus, got {type(self.status).__name__}")
        if self.processing_time is not None and not isinstance(self.processing_time, timedelta):
            raise EventError(f"processing_time must be a timedelta, got {type(self.processing_time).__name__}")
        if not isinstance(self.error_count, int):
            raise EventError(f"error_count must be an integer, got {type(self.error_count).__name__}")
        if self.error_count < 0:
            raise EventError(f"error_count must be non-negative, got {self.error_count}")
        if self.last_error is not None and not isinstance(self.last_error, str):
            raise EventError(f"last_error must be a string, got {type(self.last_error).__name__}")
        if not isinstance(self.tags, list):
            raise EventError(f"tags must be a list, got {type(self.tags).__name__}")

    def can_retry(self) -> bool:
        """Check if event can be retried."""
        return self.retry_count < self.max_retries

    def increment_retry(self) -> None:
        """Increment retry count."""
        self.retry_count += 1
        self.status = EventStatus.RETRYING

    def start_processing(self) -> None:
        """Mark event as processing."""
        self.status = EventStatus.PROCESSING

    def complete_processing(self, processing_time: timedelta) -> None:
        """Mark event as completed.
        
        Args:
            processing_time: Time taken to process event
        """
        self.status = EventStatus.COMPLETED
        self.processing_time = processing_time

    def fail_processing(self, error: str) -> None:
        """Mark event as failed.
        
        Args:
            error: Error message
        """
        self.status = EventStatus.FAILED
        self.error_count += 1
        self.last_error = error

P = TypeVar("P", covariant=True)

class EventPayload(Protocol[P]):
    """Event payload protocol."""
    
    def to_dict(self) -> dict[str, Any]:
        """Convert payload to dictionary.
        
        Returns:
            Dictionary representation
        """
        ...
        
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EventPayload[P]":
        """Create payload from dictionary.
        
        Args:
            data: Dictionary data
            
        Returns:
            Event payload
        """
        ...

T = TypeVar("T")

@dataclass
class Event(Generic[T]):
    """Base event class with type-safe payload."""
    
    name: str
    payload: T
    metadata: EventMetadata = field(default_factory=EventMetadata)

    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if not isinstance(self.name, str):
            raise EventError(f"name must be a string, got {type(self.name).__name__}")
        if not self.name:
            raise EventError("Event name cannot be empty")
        if not isinstance(self.metadata, EventMetadata):
            raise EventError(f"metadata must be an EventMetadata, got {type(self.metadata).__name__}")

    def with_retry_policy(
        self,
        max_retries: int,
        retry_delay: float,
        priority: EventPriority | None = None,
    ) -> "Event[T]":
        """Create new event with retry policy.
        
        Args:
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
            priority: Optional priority override
            
        Returns:
            New event with retry policy
        """
        metadata = EventMetadata(
            timestamp=self.metadata.timestamp,
            source=self.metadata.source,
            correlation_id=self.metadata.correlation_id,
            causation_id=self.metadata.causation_id,
            metadata=self.metadata.metadata.copy(),
            priority=priority or self.metadata.priority,
            max_retries=max_retries,
            retry_delay=retry_delay,
            tags=self.metadata.tags.copy(),
        )
        return Event(self.name, self.payload, metadata)

    def with_tags(self, *tags: str) -> "Event[T]":
        """Create new event with tags.
        
        Args:
            *tags: Tags to add
            
        Returns:
            New event with tags
        """
        metadata = EventMetadata(
            timestamp=self.metadata.timestamp,
            source=self.metadata.source,
            correlation_id=self.metadata.correlation_id,
            causation_id=self.metadata.causation_id,
            metadata=self.metadata.metadata.copy(),
            priority=self.metadata.priority,
            max_retries=self.metadata.max_retries,
            retry_delay=self.metadata.retry_delay,
            tags=[*self.metadata.tags, *tags],
        )
        return Event(self.name, self.payload, metadata)

EventHandler = Callable[[Event[T]], None | bool]
AsyncEventHandler = Callable[[Event[T]], None | bool | Any]

@dataclass
class EventSubscription(Generic[T]):
    """Event subscription details."""
    
    handler: AsyncEventHandler[T]
    priority: EventPriority = EventPriority.NORMAL
    filter_fn: Callable[[Event[T]], bool] | None = None
    validator: Validator[Event[T]] | None = None
    
    def __post_init__(self) -> None:
        """Validate subscription."""
        if not callable(self.handler):
            raise EventError(f"handler must be callable, got {type(self.handler).__name__}")
        if not isinstance(self.priority, EventPriority):
            raise EventError(f"priority must be an EventPriority, got {type(self.priority).__name__}")
        if self.filter_fn is not None and not callable(self.filter_fn):
            raise EventError(f"filter_fn must be callable, got {type(self.filter_fn).__name__}")
        if self.validator is not None and not isinstance(self.validator, Validator):
            raise EventError(f"validator must be a Validator, got {type(self.validator).__name__}")

    async def can_handle(self, event: Event[T]) -> ValidationResult:
        """Check if handler can handle event.
        
        Args:
            event: Event to check
            
        Returns:
            Validation result
        """
        if self.filter_fn and not self.filter_fn(event):
            return ValidationResult(
                valid=False,
                message="Event filtered out by filter_fn",
            )
            
        if self.validator:
            return await self.validator.validate(event)
            
        return ValidationResult(valid=True)

@dataclass
class EventConfig(BaseConfig):
    """Event system configuration."""
    
    max_handlers_per_event: int = 100
    enable_async_dispatch: bool = True
    error_handling_policy: str = "continue"  # continue, stop, retry
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds
    max_queue_size: int = 1000  # for backpressure
    batch_size: int = 100  # for batch processing
    batch_timeout: float = 1.0  # seconds
    
    def __post_init__(self) -> None:
        """Validate configuration."""
        super().__post_init__()
        if not isinstance(self.max_handlers_per_event, int):
            raise EventError(f"max_handlers_per_event must be an integer, got {type(self.max_handlers_per_event).__name__}")
        if self.max_handlers_per_event < 1:
            raise EventError(f"max_handlers_per_event must be positive, got {self.max_handlers_per_event}")
        if not isinstance(self.enable_async_dispatch, bool):
            raise EventError(f"enable_async_dispatch must be a boolean, got {type(self.enable_async_dispatch).__name__}")
        if not isinstance(self.error_handling_policy, str):
            raise EventError(f"error_handling_policy must be a string, got {type(self.error_handling_policy).__name__}")
        if self.error_handling_policy not in ("continue", "stop", "retry"):
            raise EventError(f"Invalid error_handling_policy: {self.error_handling_policy}")
        if not isinstance(self.max_retries, int):
            raise EventError(f"max_retries must be an integer, got {type(self.max_retries).__name__}")
        if self.max_retries < 0:
            raise EventError(f"max_retries must be non-negative, got {self.max_retries}")
        if not isinstance(self.retry_delay, (int, float)):
            raise EventError(f"retry_delay must be a number, got {type(self.retry_delay).__name__}")
        if self.retry_delay < 0:
            raise EventError(f"retry_delay must be non-negative, got {self.retry_delay}")
        if not isinstance(self.max_queue_size, int):
            raise EventError(f"max_queue_size must be an integer, got {type(self.max_queue_size).__name__}")
        if self.max_queue_size < 1:
            raise EventError(f"max_queue_size must be positive, got {self.max_queue_size}")
        if not isinstance(self.batch_size, int):
            raise EventError(f"batch_size must be an integer, got {type(self.batch_size).__name__}")
        if self.batch_size < 1:
            raise EventError(f"batch_size must be positive, got {self.batch_size}")
        if not isinstance(self.batch_timeout, (int, float)):
            raise EventError(f"batch_timeout must be a number, got {type(self.batch_timeout).__name__}")
        if self.batch_timeout < 0:
            raise EventError(f"batch_timeout must be non-negative, got {self.batch_timeout}")

__all__ = [
    "Event",
    "EventConfig",
    "EventError",
    "EventHandler",
    "AsyncEventHandler",
    "EventMetadata",
    "EventPriority",
    "EventSubscription",
] 