"""Event manager implementation."""

import asyncio
from collections import defaultdict
from typing import Any, Generic, TypeVar

from ..module.base import BaseModule
from .base import (
    AsyncEventHandler,
    Event,
    EventConfig,
    EventError,
    EventPriority,
    EventSubscription,
)
from .middleware import EventMiddleware, MiddlewareChain
from .persistence import EventPersistenceManager, EventStore

T = TypeVar("T")

class EventManager(BaseModule[EventConfig], Generic[T]):
    """Event manager implementation with type-safe event handling."""

    def __init__(
        self,
        event_store: EventStore[T] | None = None,
        auto_persist: bool = False,
    ) -> None:
        """Initialize event manager.
        
        Args:
            event_store: Optional event store for persistence
            auto_persist: Whether to automatically persist events
        """
        config = EventConfig(name="event-manager")
        super().__init__(config)
        self._handlers: dict[str, list[EventSubscription[T]]] = defaultdict(list)
        self._running_tasks: set[asyncio.Task[Any]] = set()
        self._middleware_chain = MiddlewareChain[T]()
        self._persistence: EventPersistenceManager[T] | None = None
        self._auto_persist = auto_persist
        self._event_queue: asyncio.Queue[Event[T]] = asyncio.Queue(maxsize=config.max_queue_size)
        self._batch_processor: asyncio.Task[Any] | None = None
        
        if event_store:
            self._persistence = EventPersistenceManager(event_store)

    async def _setup(self) -> None:
        """Setup event manager."""
        self._handlers.clear()
        self._running_tasks.clear()
        self._event_queue = asyncio.Queue(maxsize=self.config.max_queue_size)
        
        if self._persistence:
            await self._persistence.initialize()
            
        # Start batch processor
        self._batch_processor = asyncio.create_task(self._process_event_batches())

    async def _teardown(self) -> None:
        """Teardown event manager."""
        # Stop batch processor
        if self._batch_processor:
            self._batch_processor.cancel()
            try:
                await self._batch_processor
            except asyncio.CancelledError:
                pass
        
        # Cancel all running tasks
        for task in self._running_tasks:
            task.cancel()
        
        if self._running_tasks:
            await asyncio.gather(*self._running_tasks, return_exceptions=True)
        
        if self._persistence:
            await self._persistence.cleanup()
        
        self._handlers.clear()
        self._running_tasks.clear()
        self._event_queue = asyncio.Queue(maxsize=self.config.max_queue_size)

    async def _process_event_batches(self) -> None:
        """Process events in batches."""
        while True:
            try:
                batch: list[Event[T]] = []
                # Get first event with timeout
                try:
                    event = await asyncio.wait_for(
                        self._event_queue.get(),
                        timeout=self.config.batch_timeout,
                    )
                    batch.append(event)
                except asyncio.TimeoutError:
                    continue
                
                # Try to get more events without blocking
                while len(batch) < self.config.batch_size:
                    try:
                        event = self._event_queue.get_nowait()
                        batch.append(event)
                    except asyncio.QueueEmpty:
                        break
                
                # Process batch
                for event in batch:
                    await self._process_event(event)
                    self._event_queue.task_done()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error processing event batch: {e}")
                continue

    async def _process_event(self, event: Event[T]) -> None:
        """Process single event.
        
        Args:
            event: Event to process
        """
        # Process event through middleware chain first
        try:
            await self._middleware_chain.process(event)
        except Exception as e:
            raise EventError("Middleware processing failed", cause=e)
        
        # Persist event if configured
        if self._persistence and self._auto_persist:
            try:
                await self._persistence.persist_event(event)
            except Exception as e:
                raise EventError("Failed to persist event", cause=e)
        
        # Skip if no handlers
        if event.name not in self._handlers:
            return
            
        handlers = self._handlers[event.name]
        
        for subscription in handlers:
            validation = await subscription.can_handle(event)
            if not validation.valid:
                continue
                
            try:
                if self.config.enable_async_dispatch:
                    # Create task for async handler
                    task = asyncio.create_task(subscription.handler(event))
                    self._running_tasks.add(task)
                    task.add_done_callback(self._running_tasks.discard)
                else:
                    # Run handler synchronously
                    await subscription.handler(event)
                    
            except Exception as e:
                if self.config.error_handling_policy == "stop":
                    raise EventError(
                        f"Event handler failed for {event.name}", cause=e
                    )
                elif self.config.error_handling_policy == "retry":
                    if event.metadata.can_retry():
                        event.metadata.increment_retry()
                        await asyncio.sleep(event.metadata.retry_delay)
                        await self.emit(event)
                    else:
                        raise EventError(
                            f"Event handler failed after {event.metadata.max_retries} retries",
                            cause=e,
                        )

    def add_middleware(self, middleware: EventMiddleware[T]) -> None:
        """Add middleware to event processing pipeline.
        
        Args:
            middleware: Middleware to add
        """
        self._middleware_chain.add(middleware)

    def subscribe(
        self,
        event_name: str,
        handler: AsyncEventHandler[T],
        priority: EventPriority = EventPriority.NORMAL,
        filter_fn: Callable[[Event[T]], bool] | None = None,
        validator: Validator[Event[T]] | None = None,
    ) -> None:
        """Subscribe to event.
        
        Args:
            event_name: Event name
            handler: Event handler
            priority: Handler priority
            filter_fn: Optional event filter function
            validator: Optional event validator
            
        Raises:
            EventError: If too many handlers for event
        """
        self._ensure_initialized()
        
        handlers = self._handlers[event_name]
        if len(handlers) >= self.config.max_handlers_per_event:
            raise EventError(
                f"Too many handlers for event {event_name} "
                f"(max: {self.config.max_handlers_per_event})"
            )
        
        subscription = EventSubscription(
            handler=handler,
            priority=priority,
            filter_fn=filter_fn,
            validator=validator,
        )
        
        # Insert maintaining priority order (higher priority first)
        insert_idx = 0
        for idx, existing in enumerate(handlers):
            if existing.priority <= priority:
                insert_idx = idx
                break
            insert_idx = idx + 1
        
        handlers.insert(insert_idx, subscription)

    def unsubscribe(
        self,
        event_name: str,
        handler: AsyncEventHandler[T] | None = None,
    ) -> None:
        """Unsubscribe from event.
        
        Args:
            event_name: Event name
            handler: Optional handler to remove (if None, removes all handlers)
        """
        self._ensure_initialized()
        
        if event_name not in self._handlers:
            return
            
        if handler is None:
            del self._handlers[event_name]
        else:
            self._handlers[event_name] = [
                h for h in self._handlers[event_name]
                if h.handler != handler
            ]

    async def emit(self, event: Event[T]) -> None:
        """Emit event.
        
        Args:
            event: Event to emit
            
        Raises:
            EventError: If event emission fails or queue is full
        """
        self._ensure_initialized()
        
        try:
            await self._event_queue.put(event)
        except asyncio.QueueFull:
            raise EventError(
                f"Event queue is full (max size: {self.config.max_queue_size})"
            )

    async def replay_events(
        self,
        event_name: str | None = None,
        handler: AsyncEventHandler[T] | None = None,
    ) -> None:
        """Replay persisted events.
        
        Args:
            event_name: Optional event name filter
            handler: Optional handler for replayed events (if None, uses subscribed handlers)
            
        Raises:
            EventError: If replay fails or persistence not configured
        """
        if not self._persistence:
            raise EventError("Event persistence not configured")
            
        events = await self._persistence.load_events(event_name)
        
        for event in events:
            if handler:
                await handler(event)
            else:
                # Use normal emit but skip persistence
                old_auto_persist = self._auto_persist
                self._auto_persist = False
                try:
                    await self.emit(event)
                finally:
                    self._auto_persist = old_auto_persist

    async def get_stats(self) -> dict[str, Any]:
        """Get event manager statistics.
        
        Returns:
            Event manager statistics
        """
        stats = await super().get_stats()
        stats.update({
            "event_count": len(self._handlers),
            "events": {
                name: len(handlers)
                for name, handlers in self._handlers.items()
            },
            "running_tasks": len(self._running_tasks),
            "middleware_count": len(self._middleware_chain._middlewares),
            "persistence_enabled": self._persistence is not None,
            "auto_persist": self._auto_persist,
            "queue_size": self._event_queue.qsize(),
            "queue_full": self._event_queue.full(),
        })
        
        if self._persistence:
            persistence_stats = await self._persistence.get_stats()
            stats["persistence"] = persistence_stats
            
        return stats

__all__ = ["EventManager"] 