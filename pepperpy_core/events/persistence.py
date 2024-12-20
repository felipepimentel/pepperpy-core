"""Event persistence implementation."""

import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Generic, Iterator, TypeVar

from ..exceptions.base import PersistenceError
from ..module.base import BaseModule
from .base import Event, EventConfig, EventMetadata

T = TypeVar("T")

class EventStore(Generic[T], ABC):
    """Base event store interface."""
    
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
        batch_size: int = 100,
    ) -> list[Event[T]]:
        """Load events.
        
        Args:
            event_name: Optional event name filter
            start_time: Optional start time filter
            end_time: Optional end time filter
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
    
    def __init__(self, path: str | Path) -> None:
        """Initialize store.
        
        Args:
            path: Store file path
        """
        self.path = Path(path)
        self._lock = asyncio.Lock()
        self._batch_size = 100
        self._batch: list[Event[T]] = []
        self._batch_task: asyncio.Task[Any] | None = None
        
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
                await asyncio.sleep(1.0)
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error but continue processing
                print(f"Error processing event batch: {e}")
                
    async def _flush_batch(self) -> None:
        """Flush event batch to disk."""
        if not self._batch:
            return
            
        async with self._lock:
            try:
                events = self._batch
                self._batch = []
                
                # Convert events to JSON
                event_data = [
                    {
                        "name": event.name,
                        "payload": event.payload,
                        "metadata": asdict(event.metadata),
                    }
                    for event in events
                ]
                
                # Append to file
                with self.path.open("a") as f:
                    for data in event_data:
                        json.dump(data, f)
                        f.write("\n")
                        
            except Exception as e:
                # Restore batch on error
                self._batch.extend(events)
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
        batch_size: int = 100,
    ) -> list[Event[T]]:
        """Load events.
        
        Args:
            event_name: Optional event name filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            batch_size: Maximum number of events to load
            
        Returns:
            List of events
            
        Raises:
            PersistenceError: If loading fails
        """
        events: list[Event[T]] = []
        
        try:
            async with self._lock:
                with self.path.open("r") as f:
                    for line in f:
                        if not line.strip():
                            continue
                            
                        try:
                            data = json.loads(line)
                            
                            # Apply filters
                            if event_name and data["name"] != event_name:
                                continue
                                
                            metadata = EventMetadata(**data["metadata"])
                            if start_time and metadata.timestamp < start_time:
                                continue
                            if end_time and metadata.timestamp > end_time:
                                continue
                                
                            event = Event(
                                name=data["name"],
                                payload=data["payload"],
                                metadata=metadata,
                            )
                            events.append(event)
                            
                            if len(events) >= batch_size:
                                break
                                
                        except Exception as e:
                            # Log error but continue processing
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
        try:
            return {
                "path": str(self.path),
                "size": self.path.stat().st_size if self.path.exists() else 0,
                "batch_size": self._batch_size,
                "pending_events": len(self._batch),
            }
        except Exception as e:
            raise PersistenceError("Failed to get store statistics", cause=e)

class EventPersistenceManager(Generic[T]):
    """Event persistence manager."""
    
    def __init__(self, store: EventStore[T]) -> None:
        """Initialize manager.
        
        Args:
            store: Event store
        """
        self._store = store
        
    async def initialize(self) -> None:
        """Initialize manager."""
        if hasattr(self._store, "initialize"):
            await self._store.initialize()
            
    async def cleanup(self) -> None:
        """Cleanup manager."""
        if hasattr(self._store, "cleanup"):
            await self._store.cleanup()
            
    async def persist_event(self, event: Event[T]) -> None:
        """Persist event.
        
        Args:
            event: Event to persist
            
        Raises:
            PersistenceError: If persistence fails
        """
        await self._store.store(event)
        
    async def persist_events(self, events: list[Event[T]]) -> None:
        """Persist multiple events.
        
        Args:
            events: Events to persist
            
        Raises:
            PersistenceError: If persistence fails
        """
        await self._store.store_batch(events)
        
    async def load_events(
        self,
        event_name: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        batch_size: int = 100,
    ) -> list[Event[T]]:
        """Load events.
        
        Args:
            event_name: Optional event name filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            batch_size: Maximum number of events to load
            
        Returns:
            List of events
            
        Raises:
            PersistenceError: If loading fails
        """
        return await self._store.load(
            event_name=event_name,
            start_time=start_time,
            end_time=end_time,
            batch_size=batch_size,
        )
        
    async def get_stats(self) -> dict[str, Any]:
        """Get persistence statistics.
        
        Returns:
            Persistence statistics
            
        Raises:
            PersistenceError: If getting stats fails
        """
        return await self._store.get_stats()

__all__ = [
    "EventStore",
    "FileEventStore",
    "EventPersistenceManager",
] 