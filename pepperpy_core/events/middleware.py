"""Event middleware implementation."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Generic, TypeVar

from ..exceptions.base import MiddlewareError
from ..validation.base import ValidationLevel, ValidationResult, Validator
from .base import Event, EventStatus

T = TypeVar("T")

class EventMiddleware(Generic[T], ABC):
    """Base event middleware interface."""
    
    @abstractmethod
    async def process(self, event: Event[T]) -> None:
        """Process event.
        
        Args:
            event: Event to process
            
        Raises:
            MiddlewareError: If processing fails
        """
        pass

    async def get_stats(self) -> dict[str, Any]:
        """Get middleware statistics.
        
        Returns:
            Middleware statistics
        """
        return {
            "type": self.__class__.__name__,
        }

class ValidationMiddleware(EventMiddleware[T]):
    """Event validation middleware."""
    
    def __init__(self, validator: Validator[Event[T]]) -> None:
        """Initialize middleware.
        
        Args:
            validator: Event validator
        """
        self.validator = validator
        self._processed_count = 0
        self._error_count = 0
        
    async def process(self, event: Event[T]) -> None:
        """Validate event.
        
        Args:
            event: Event to validate
            
        Raises:
            MiddlewareError: If validation fails
        """
        try:
            result = await self.validator.validate(event)
            self._processed_count += 1
            
            if not result.valid and result.level == ValidationLevel.CRITICAL:
                self._error_count += 1
                raise MiddlewareError(
                    f"Event validation failed: {result.message}",
                    details={
                        "event_name": event.name,
                        "validation_result": result,
                    },
                )
                
        except Exception as e:
            self._error_count += 1
            raise MiddlewareError("Event validation failed", cause=e)
            
    async def get_stats(self) -> dict[str, Any]:
        """Get middleware statistics.
        
        Returns:
            Middleware statistics
        """
        stats = await super().get_stats()
        stats.update({
            "processed_count": self._processed_count,
            "error_count": self._error_count,
            "validator": self.validator.__class__.__name__,
        })
        return stats

class TransformationMiddleware(EventMiddleware[T]):
    """Event transformation middleware."""
    
    def __init__(self, transform_fn: Callable[[Event[T]], Event[T]]) -> None:
        """Initialize middleware.
        
        Args:
            transform_fn: Event transformation function
        """
        self.transform_fn = transform_fn
        self._processed_count = 0
        self._error_count = 0
        
    async def process(self, event: Event[T]) -> None:
        """Transform event.
        
        Args:
            event: Event to transform
            
        Raises:
            MiddlewareError: If transformation fails
        """
        try:
            transformed = self.transform_fn(event)
            self._processed_count += 1
            
            # Update event in place
            event.name = transformed.name
            event.payload = transformed.payload
            event.metadata = transformed.metadata
            
        except Exception as e:
            self._error_count += 1
            raise MiddlewareError("Event transformation failed", cause=e)
            
    async def get_stats(self) -> dict[str, Any]:
        """Get middleware statistics.
        
        Returns:
            Middleware statistics
        """
        stats = await super().get_stats()
        stats.update({
            "processed_count": self._processed_count,
            "error_count": self._error_count,
        })
        return stats

class FilterMiddleware(EventMiddleware[T]):
    """Event filtering middleware."""
    
    def __init__(self, filter_fn: Callable[[Event[T]], bool]) -> None:
        """Initialize middleware.
        
        Args:
            filter_fn: Event filter function
        """
        self.filter_fn = filter_fn
        self._processed_count = 0
        self._filtered_count = 0
        
    async def process(self, event: Event[T]) -> None:
        """Filter event.
        
        Args:
            event: Event to filter
            
        Raises:
            MiddlewareError: If event should be filtered
        """
        self._processed_count += 1
        
        if not self.filter_fn(event):
            self._filtered_count += 1
            raise MiddlewareError(
                "Event filtered out",
                details={"event_name": event.name},
            )
            
    async def get_stats(self) -> dict[str, Any]:
        """Get middleware statistics.
        
        Returns:
            Middleware statistics
        """
        stats = await super().get_stats()
        stats.update({
            "processed_count": self._processed_count,
            "filtered_count": self._filtered_count,
        })
        return stats

class TimingMiddleware(EventMiddleware[T]):
    """Event timing middleware."""
    
    def __init__(self) -> None:
        """Initialize middleware."""
        self._processed_count = 0
        self._total_time = 0.0
        self._min_time = float("inf")
        self._max_time = 0.0
        
    async def process(self, event: Event[T]) -> None:
        """Track event timing.
        
        Args:
            event: Event to track
        """
        start_time = datetime.now()
        event.metadata.start_processing()
        
        try:
            yield  # Allow other middleware to process
        finally:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self._processed_count += 1
            self._total_time += duration
            self._min_time = min(self._min_time, duration)
            self._max_time = max(self._max_time, duration)
            
            event.metadata.complete_processing(end_time - start_time)
            
    async def get_stats(self) -> dict[str, Any]:
        """Get middleware statistics.
        
        Returns:
            Middleware statistics
        """
        stats = await super().get_stats()
        stats.update({
            "processed_count": self._processed_count,
            "total_time": self._total_time,
            "min_time": self._min_time if self._processed_count > 0 else 0,
            "max_time": self._max_time,
            "avg_time": self._total_time / self._processed_count if self._processed_count > 0 else 0,
        })
        return stats

class RetryMiddleware(EventMiddleware[T]):
    """Event retry middleware."""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0) -> None:
        """Initialize middleware.
        
        Args:
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._retry_count = 0
        self._success_count = 0
        self._failure_count = 0
        
    async def process(self, event: Event[T]) -> None:
        """Handle event retries.
        
        Args:
            event: Event to handle
            
        Raises:
            MiddlewareError: If retry limit exceeded
        """
        try:
            yield  # Allow other middleware to process
            self._success_count += 1
            
        except Exception as e:
            self._retry_count += 1
            
            if event.metadata.can_retry():
                event.metadata.increment_retry()
                raise MiddlewareError(
                    "Event processing failed, will retry",
                    cause=e,
                    details={
                        "event_name": event.name,
                        "retry_count": event.metadata.retry_count,
                        "retry_delay": event.metadata.retry_delay,
                    },
                )
            else:
                self._failure_count += 1
                event.metadata.fail_processing(str(e))
                raise MiddlewareError(
                    f"Event processing failed after {event.metadata.max_retries} retries",
                    cause=e,
                )
                
    async def get_stats(self) -> dict[str, Any]:
        """Get middleware statistics.
        
        Returns:
            Middleware statistics
        """
        stats = await super().get_stats()
        stats.update({
            "retry_count": self._retry_count,
            "success_count": self._success_count,
            "failure_count": self._failure_count,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
        })
        return stats

class MiddlewareChain(Generic[T]):
    """Event middleware chain."""
    
    def __init__(self) -> None:
        """Initialize chain."""
        self._middlewares: list[EventMiddleware[T]] = []
        self._stats = {
            "processed_count": 0,
            "error_count": 0,
            "last_error": None,
            "last_error_time": None,
        }
        
    def add(self, middleware: EventMiddleware[T], index: int | None = None) -> None:
        """Add middleware to chain.
        
        Args:
            middleware: Middleware to add
            index: Optional insertion index
        """
        if index is None:
            self._middlewares.append(middleware)
        else:
            self._middlewares.insert(index, middleware)
        
    def remove(self, middleware: EventMiddleware[T]) -> None:
        """Remove middleware from chain.
        
        Args:
            middleware: Middleware to remove
        """
        self._middlewares.remove(middleware)
        
    async def process(self, event: Event[T]) -> None:
        """Process event through middleware chain.
        
        Args:
            event: Event to process
            
        Raises:
            MiddlewareError: If processing fails
        """
        self._stats["processed_count"] += 1
        
        try:
            for middleware in self._middlewares:
                await middleware.process(event)
                
        except Exception as e:
            self._stats["error_count"] += 1
            self._stats["last_error"] = str(e)
            self._stats["last_error_time"] = datetime.now()
            raise
            
    async def get_stats(self) -> dict[str, Any]:
        """Get chain statistics.
        
        Returns:
            Chain statistics
        """
        stats = {
            **self._stats,
            "middleware_count": len(self._middlewares),
            "middleware_types": [m.__class__.__name__ for m in self._middlewares],
        }
        
        middleware_stats = []
        for middleware in self._middlewares:
            middleware_stats.append(await middleware.get_stats())
            
        stats["middlewares"] = middleware_stats
        return stats

__all__ = [
    "EventMiddleware",
    "ValidationMiddleware",
    "TransformationMiddleware",
    "FilterMiddleware",
    "TimingMiddleware",
    "RetryMiddleware",
    "MiddlewareChain",
] 