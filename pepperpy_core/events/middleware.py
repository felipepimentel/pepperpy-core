"""Event middleware implementation."""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from ..exceptions.base import MiddlewareError
from ..validation.base import ValidationLevel, ValidationResult, Validator
from .base import Event

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

class LoggingMiddleware(EventMiddleware[T]):
    """Event logging middleware."""
    
    def __init__(self) -> None:
        """Initialize middleware."""
        self._processed_count = 0
        
    async def process(self, event: Event[T]) -> None:
        """Log event.
        
        Args:
            event: Event to log
        """
        print(f"Processing event: {event.name} ({event.metadata.timestamp})")
        self._processed_count += 1
            
    async def get_stats(self) -> dict[str, Any]:
        """Get middleware statistics.
        
        Returns:
            Middleware statistics
        """
        stats = await super().get_stats()
        stats.update({
            "processed_count": self._processed_count,
        })
        return stats

class MiddlewareChain(Generic[T]):
    """Event middleware chain."""
    
    def __init__(self) -> None:
        """Initialize chain."""
        self._middlewares: list[EventMiddleware[T]] = []
        
    def add(self, middleware: EventMiddleware[T]) -> None:
        """Add middleware to chain.
        
        Args:
            middleware: Middleware to add
        """
        self._middlewares.append(middleware)
        
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
        for middleware in self._middlewares:
            await middleware.process(event)
            
    async def get_stats(self) -> dict[str, Any]:
        """Get chain statistics.
        
        Returns:
            Chain statistics
        """
        stats = {
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
    "LoggingMiddleware",
    "MiddlewareChain",
] 