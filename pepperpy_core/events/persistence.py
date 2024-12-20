"""Event persistence implementation."""

import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Generic, Protocol, TypeVar

from ..exceptions.base import PersistenceError
from ..module.base import BaseModule
from .base import Event, EventConfig, EventMetadata, EventPayload, EventStatus

T = TypeVar("T")

class EventSerializer(Protocol[T]):
    """Event serialization protocol."""
    
    def serialize(self, event: Event[T]) -> bytes:
        """Serialize event to bytes.
        
        Args:
            event: Event to serialize
            
        Returns:
            Serialized event
            
        Raises:
            PersistenceError: If serialization fails
        """
        ...
        
    def deserialize(self, data: bytes) -> Event[T]:
        """Deserialize event from bytes.
        
        Args:
            data: Serialized event data
            
        Returns:
            Deserialized event
            
        Raises:
            PersistenceError: If deserialization fails
        """
        ...

class JsonEventSerializer(EventSerializer[T]):
    """JSON event serializer."""
    
    def serialize(self, event: Event[T]) -> bytes:
        """Serialize event to JSON bytes.
        
        Args:
            event: Event to serialize
            
        Returns:
            JSON bytes
            
        Raises:
            PersistenceError: If serialization fails
        """
        try:
            if isinstance(event.payload, EventPayload):
                payload = event.payload.to_dict()
            else:
                payload = event.payload
                
            data = {
                "name": event.name,
                "payload": payload,
                "metadata": asdict(event.metadata),
            }
            return json.dumps(data).encode()
        except Exception as e:
            raise PersistenceError("Failed to serialize event", cause=e)
            
    def deserialize(self, data: bytes) -> Event[T]:
        """Deserialize event from JSON bytes.
        
        Args:
            data: JSON bytes
            
        Returns:
            Deserialized event
            
        Raises:
            PersistenceError: If deserialization fails
        """
        try:
            raw = json.loads(data.decode())
            metadata = EventMetadata(**raw["metadata"])
            
            if isinstance(raw["payload"], dict):
                # Try to deserialize as EventPayload
                try:
                    payload = EventPayload.from_dict(raw["payload"])  # type: ignore
                except Exception:
                    payload = raw["payload"]
            else:
                payload = raw["payload"]
                
            return Event(
                name=raw["name"],
                payload=payload,  # type: ignore
                metadata=metadata,
            )
        except Exception as e:
            raise PersistenceError("Failed to deserialize event", cause=e)

class EventStore(Generic[T], ABC):
    """Base event store interface."""
    
    def __init__(self, serializer: EventSerializer[T] | None = None) -> None:
        """Initialize store.
        
        Args:
            serializer: Optional event serializer
        """
        self.serializer = serializer or JsonEventSerializer()
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize store.
        
        Raises:
            PersistenceError: If initialization fails
        """
        pass
        
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup store.
        
        Raises:
            PersistenceError: If cleanup fails
        """
        pass
    
    @abstractmethod
    async def store(self, event: Event[T]) -> None:
        """Store event.
        
        Args:
            event: Event to store
            
        Raises:
            PersistenceError: If storage fails
        """
        pass
    
    @abstractmethod
    async def store_batch(self, events: list[Event[T]]) -> None:
        """Store multiple events.
        
        Args:
            events: Events to store
            
        Raises:
            PersistenceError: If storage fails
        """
        pass
    
    @abstractmethod
    async def load(
        self,
        event_name: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        status: EventStatus | None = None,
        tags: list[str] | None = None,
        batch_size: int = 100,
    ) -> list[Event[T]]:
        """Load events.
        
        Args:
            event_name: Optional event name filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            status: Optional status filter
            tags: Optional tag filter (all tags must match)
            batch_size: Maximum number of events to load
            
        Returns:
            List of events
            
        Raises:
            PersistenceError: If loading fails
        """
        pass
    
    @abstractmethod
    async def get_stats(self) -> dict[str, Any]:
        """Get store statistics.
        
        Returns:
            Store statistics
            
        Raises:
            PersistenceError: If getting stats fails
        """
        pass

class FileEventStore(EventStore[T]):
    """File-based event store."""
    
    def __init__(
        self,
        path: str | Path,
        serializer: EventSerializer[T] | None = None,
        batch_size: int = 100,
        flush_interval: float = 1.0,
    ) -> None:
        """Initialize store.
        
        Args:
            path: Store file path
            serializer: Optional event serializer
            batch_size: Batch size for writes
            flush_interval: Interval between batch flushes
        """
        super().__init__(serializer)
        self.path = Path(path)
        self._lock = asyncio.Lock()
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._batch: list[Event[T]] = []
        self._batch_task: asyncio.Task[Any] | None = None
        self._stats = {
            "total_events": 0,
            "total_batches": 0,
            "failed_writes": 0,
            "last_write_time": None,
        }
        
    async def initialize(self) -> None:
        """Initialize store."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()
            
        # Start batch processor
        self._batch_task = asyncio.create_task(self._process_batch())
        
    async def cleanup(self) -> None:
        """Cleanup store."""
        # Stop batch processor
        if self._batch_task:
            self._batch_task.cancel()
            try:
                await self._batch_task
            except asyncio.CancelledError:
                pass
            
        # Flush remaining events
        if self._batch:
            await self._flush_batch()
            
    async def _process_batch(self) -> None:
        """Process event batch."""
        while True:
            try:
                if len(self._batch) >= self._batch_size:
                    await self._flush_batch()
                await asyncio.sleep(self._flush_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._stats["failed_writes"] += 1
                print(f"Error processing event batch: {e}")
                
    async def _flush_batch(self) -> None:
        """Flush event batch to disk."""
        if not self._batch:
            return
            
        async with self._lock:
            try:
                events = self._batch
                self._batch = []
                
                # Serialize and write events
                with self.path.open("ab") as f:
                    for event in events:
                        data = self.serializer.serialize(event)
                        f.write(data)
                        f.write(b"\n")
                        
                self._stats["total_events"] += len(events)
                self._stats["total_batches"] += 1
                self._stats["last_write_time"] = datetime.now()
                        
            except Exception as e:
                # Restore batch on error
                self._batch.extend(events)
                self._stats["failed_writes"] += 1
                raise PersistenceError("Failed to flush event batch", cause=e)
    
    async def store(self, event: Event[T]) -> None:
        """Store event.
        
        Args:
            event: Event to store
            
        Raises:
            PersistenceError: If storage fails
        """
        self._batch.append(event)
        
        if len(self._batch) >= self._batch_size:
            await self._flush_batch()
            
    async def store_batch(self, events: list[Event[T]]) -> None:
        """Store multiple events.
        
        Args:
            events: Events to store
            
        Raises:
            PersistenceError: If storage fails
        """
        self._batch.extend(events)
        
        if len(self._batch) >= self._batch_size:
            await self._flush_batch()
    
    async def load(
        self,
        event_name: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        status: EventStatus | None = None,
        tags: list[str] | None = None,
        batch_size: int = 100,
    ) -> list[Event[T]]:
        """Load events.
        
        Args:
            event_name: Optional event name filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            status: Optional status filter
            tags: Optional tag filter (all tags must match)
            batch_size: Maximum number of events to load
            
        Returns:
            List of events
            
        Raises:
            PersistenceError: If loading fails
        """
        events: list[Event[T]] = []
        
        try:
            async with self._lock:
                with self.path.open("rb") as f:
                    for line in f:
                        if not line.strip():
                            continue
                            
                        try:
                            event = self.serializer.deserialize(line)
                            
                            # Apply filters
                            if event_name and event.name != event_name:
                                continue
                                
                            if start_time and event.metadata.timestamp < start_time:
                                continue
                                
                            if end_time and event.metadata.timestamp > end_time:
                                continue
                                
                            if status and event.metadata.status != status:
                                continue
                                
                            if tags and not all(tag in event.metadata.tags for tag in tags):
                                continue
                                
                            events.append(event)
                            
                            if len(events) >= batch_size:
                                break
                                
                        except Exception as e:
                            print(f"Error loading event: {e}")
                            continue
                            
        except Exception as e:
            raise PersistenceError("Failed to load events", cause=e)
            
        return events
    
    async def get_stats(self) -> dict[str, Any]:
        """Get store statistics.
        
        Returns:
            Store statistics
            
        Raises:
            PersistenceError: If getting stats fails
        """
        return {
            **self._stats,
            "pending_events": len(self._batch),
            "store_path": str(self.path),
            "batch_size": self._batch_size,
            "flush_interval": self._flush_interval,
        }

class InMemoryEventStore(EventStore[T]):
    """In-memory event store."""
    
    def __init__(self, max_events: int = 10000) -> None:
        """Initialize store.
        
        Args:
            max_events: Maximum number of events to store
        """
        super().__init__()
        self.max_events = max_events
        self._events: list[Event[T]] = []
        self._lock = asyncio.Lock()
        self._stats = {
            "total_events": 0,
            "dropped_events": 0,
            "last_write_time": None,
        }
        
    async def initialize(self) -> None:
        """Initialize store."""
        pass
        
    async def cleanup(self) -> None:
        """Cleanup store."""
        self._events.clear()
        
    async def store(self, event: Event[T]) -> None:
        """Store event.
        
        Args:
            event: Event to store
            
        Raises:
            PersistenceError: If storage fails
        """
        async with self._lock:
            if len(self._events) >= self.max_events:
                self._events.pop(0)
                self._stats["dropped_events"] += 1
                
            self._events.append(event)
            self._stats["total_events"] += 1
            self._stats["last_write_time"] = datetime.now()
            
    async def store_batch(self, events: list[Event[T]]) -> None:
        """Store multiple events.
        
        Args:
            events: Events to store
            
        Raises:
            PersistenceError: If storage fails
        """
        async with self._lock:
            for event in events:
                if len(self._events) >= self.max_events:
                    self._events.pop(0)
                    self._stats["dropped_events"] += 1
                    
                self._events.append(event)
                self._stats["total_events"] += 1
                
            self._stats["last_write_time"] = datetime.now()
    
    async def load(
        self,
        event_name: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        status: EventStatus | None = None,
        tags: list[str] | None = None,
        batch_size: int = 100,
    ) -> list[Event[T]]:
        """Load events.
        
        Args:
            event_name: Optional event name filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            status: Optional status filter
            tags: Optional tag filter (all tags must match)
            batch_size: Maximum number of events to load
            
        Returns:
            List of events
            
        Raises:
            PersistenceError: If loading fails
        """
        async with self._lock:
            events = self._events
            
            if event_name:
                events = [e for e in events if e.name == event_name]
                
            if start_time:
                events = [e for e in events if e.metadata.timestamp >= start_time]
                
            if end_time:
                events = [e for e in events if e.metadata.timestamp <= end_time]
                
            if status:
                events = [e for e in events if e.metadata.status == status]
                
            if tags:
                events = [e for e in events if all(tag in e.metadata.tags for tag in tags)]
                
            return events[:batch_size]
    
    async def get_stats(self) -> dict[str, Any]:
        """Get store statistics.
        
        Returns:
            Store statistics
            
        Raises:
            PersistenceError: If getting stats fails
        """
        return {
            **self._stats,
            "current_events": len(self._events),
            "max_events": self.max_events,
        }

__all__ = [
    "EventSerializer",
    "JsonEventSerializer",
    "EventStore",
    "FileEventStore",
    "InMemoryEventStore",
] 