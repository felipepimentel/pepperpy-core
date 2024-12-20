"""Base validation types and interfaces."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Generic, TypeVar

from ..exceptions.base import ValidationError

class ValidationLevel(Enum):
    """Validation level types."""
    
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    
    def __str__(self) -> str:
        """Return string representation."""
        return self.value

@dataclass
class ValidationContext:
    """Validation context with metadata."""
    
    path: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    parent: "ValidationContext | None" = None
    _children: list["ValidationContext"] = field(default_factory=list, init=False)
    _cleanup_handlers: list[Callable[[], Any]] = field(default_factory=list, init=False)
    
    def __post_init__(self) -> None:
        """Validate context."""
        if not isinstance(self.path, str):
            raise ValidationError(f"path must be a string, got {type(self.path).__name__}")
        if not isinstance(self.metadata, dict):
            raise ValidationError(f"metadata must be a dictionary, got {type(self.metadata).__name__}")
            
    async def __aenter__(self) -> "ValidationContext":
        """Enter async context."""
        return self
        
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context and run cleanup handlers."""
        for handler in self._cleanup_handlers:
            try:
                result = handler()
                if hasattr(result, "__await__"):
                    await result
            except Exception:
                pass  # Ignore cleanup errors
                
    def add_cleanup(self, handler: Callable[[], Any]) -> None:
        """Add cleanup handler to run when context exits.
        
        Args:
            handler: Cleanup handler function
        """
        self._cleanup_handlers.append(handler)
        
    def child(self, path: str, **metadata: Any) -> "ValidationContext":
        """Create child context.
        
        Args:
            path: Child path
            **metadata: Additional metadata
            
        Returns:
            Child context
        """
        full_path = f"{self.path}.{path}" if self.path else path
        child_metadata = self.metadata.copy()
        child_metadata.update(metadata)
        child = ValidationContext(
            path=full_path,
            metadata=child_metadata,
            parent=self,
        )
        self._children.append(child)
        return child
        
    def get_root(self) -> "ValidationContext":
        """Get root context.
        
        Returns:
            Root context
        """
        current = self
        while current.parent is not None:
            current = current.parent
        return current
        
    def get_ancestors(self) -> list["ValidationContext"]:
        """Get all ancestor contexts.
        
        Returns:
            List of ancestor contexts from root to parent
        """
        ancestors: list[ValidationContext] = []
        current = self.parent
        while current is not None:
            ancestors.insert(0, current)
            current = current.parent
        return ancestors
        
    def get_children(self, recursive: bool = False) -> list["ValidationContext"]:
        """Get child contexts.
        
        Args:
            recursive: Whether to include descendants
            
        Returns:
            List of child contexts
        """
        if not recursive:
            return self._children.copy()
            
        children: list[ValidationContext] = []
        for child in self._children:
            children.append(child)
            children.extend(child.get_children(recursive=True))
        return children
        
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value, checking ancestors if not found.
        
        Args:
            key: Metadata key
            default: Default value if not found
            
        Returns:
            Metadata value
        """
        if key in self.metadata:
            return self.metadata[key]
            
        current = self.parent
        while current is not None:
            if key in current.metadata:
                return current.metadata[key]
            current = current.parent
            
        return default
        
    def set_metadata(self, key: str, value: Any, propagate: bool = False) -> None:
        """Set metadata value.
        
        Args:
            key: Metadata key
            value: Metadata value
            propagate: Whether to propagate to descendants
        """
        self.metadata[key] = value
        if propagate:
            for child in self.get_children(recursive=True):
                if key not in child.metadata:
                    child.metadata[key] = value
                    
    def clear_metadata(self, key: str, recursive: bool = False) -> None:
        """Clear metadata value.
        
        Args:
            key: Metadata key
            recursive: Whether to clear from descendants
        """
        self.metadata.pop(key, None)
        if recursive:
            for child in self.get_children(recursive=True):
                child.metadata.pop(key, None)
                
    def merge(self, other: "ValidationContext") -> None:
        """Merge another context into this one.
        
        Args:
            other: Context to merge
        """
        self.metadata.update(other.metadata)
        for child in other.get_children():
            child.parent = self
            self._children.append(child)

@dataclass
class ValidationResult:
    """Validation result with metadata."""
    
    valid: bool
    level: ValidationLevel = ValidationLevel.ERROR
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    context: ValidationContext | None = None
    details: list[str] = field(default_factory=list)
    cause: Exception | None = None
    
    def __post_init__(self) -> None:
        """Validate result."""
        if not isinstance(self.valid, bool):
            raise ValidationError(f"valid must be a boolean, got {type(self.valid).__name__}")
        if not isinstance(self.level, ValidationLevel):
            raise ValidationError(f"level must be a ValidationLevel, got {type(self.level).__name__}")
        if not isinstance(self.message, str):
            raise ValidationError(f"message must be a string, got {type(self.message).__name__}")
        if not isinstance(self.metadata, dict):
            raise ValidationError(f"metadata must be a dictionary, got {type(self.metadata).__name__}")
        if self.context is not None and not isinstance(self.context, ValidationContext):
            raise ValidationError(f"context must be a ValidationContext, got {type(self.context).__name__}")
        if not isinstance(self.details, list):
            raise ValidationError(f"details must be a list, got {type(self.details).__name__}")
        if self.cause is not None and not isinstance(self.cause, Exception):
            raise ValidationError(f"cause must be an Exception, got {type(self.cause).__name__}")

    def with_context(self, context: ValidationContext) -> "ValidationResult":
        """Create new result with context.
        
        Args:
            context: Validation context
            
        Returns:
            New result with context
        """
        return ValidationResult(
            valid=self.valid,
            level=self.level,
            message=self.message,
            metadata=self.metadata.copy(),
            context=context,
            details=self.details.copy(),
            cause=self.cause,
        )

    def with_message(self, message: str) -> "ValidationResult":
        """Create new result with message.
        
        Args:
            message: New message
            
        Returns:
            New result with message
        """
        return ValidationResult(
            valid=self.valid,
            level=self.level,
            message=message,
            metadata=self.metadata.copy(),
            context=self.context,
            details=self.details.copy(),
            cause=self.cause,
        )
        
    def with_level(self, level: ValidationLevel) -> "ValidationResult":
        """Create new result with level.
        
        Args:
            level: New validation level
            
        Returns:
            New result with level
        """
        return ValidationResult(
            valid=self.valid,
            level=level,
            message=self.message,
            metadata=self.metadata.copy(),
            context=self.context,
            details=self.details.copy(),
            cause=self.cause,
        )
        
    def with_metadata(self, **metadata: Any) -> "ValidationResult":
        """Create new result with additional metadata.
        
        Args:
            **metadata: Additional metadata
            
        Returns:
            New result with metadata
        """
        new_metadata = self.metadata.copy()
        new_metadata.update(metadata)
        return ValidationResult(
            valid=self.valid,
            level=self.level,
            message=self.message,
            metadata=new_metadata,
            context=self.context,
            details=self.details.copy(),
            cause=self.cause,
        )
        
    def with_details(self, *details: str) -> "ValidationResult":
        """Create new result with additional details.
        
        Args:
            *details: Additional detail messages
            
        Returns:
            New result with details
        """
        new_details = self.details.copy()
        new_details.extend(details)
        return ValidationResult(
            valid=self.valid,
            level=self.level,
            message=self.message,
            metadata=self.metadata.copy(),
            context=self.context,
            details=new_details,
            cause=self.cause,
        )
        
    def with_cause(self, cause: Exception) -> "ValidationResult":
        """Create new result with cause.
        
        Args:
            cause: Exception that caused validation failure
            
        Returns:
            New result with cause
        """
        return ValidationResult(
            valid=self.valid,
            level=self.level,
            message=self.message,
            metadata=self.metadata.copy(),
            context=self.context,
            details=self.details.copy(),
            cause=cause,
        )
        
    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """Merge another result into this one.
        
        Args:
            other: Result to merge
            
        Returns:
            New merged result
        """
        return ValidationResult(
            valid=self.valid and other.valid,
            level=max(self.level, other.level),
            message=f"{self.message}\n{other.message}" if self.message and other.message else self.message or other.message,
            metadata={**self.metadata, **other.metadata},
            context=self.context,  # Keep original context
            details=[*self.details, *other.details],
            cause=self.cause or other.cause,
        )
        
    def format_message(self, include_details: bool = True) -> str:
        """Format validation message.
        
        Args:
            include_details: Whether to include detail messages
            
        Returns:
            Formatted message
        """
        parts = []
        
        # Add context path
        if self.context and self.context.path:
            parts.append(f"[{self.context.path}]")
            
        # Add main message
        if self.message:
            parts.append(self.message)
            
        # Add details
        if include_details and self.details:
            parts.extend(f"- {detail}" for detail in self.details)
            
        # Add cause
        if self.cause:
            parts.append(f"Caused by: {str(self.cause)}")
            
        return "\n".join(parts)

T = TypeVar("T")

class Validator(Generic[T], ABC):
    """Base validator interface."""
    
    def __init__(self, name: str = "", enabled: bool = True) -> None:
        """Initialize validator.
        
        Args:
            name: Validator name
            enabled: Whether validator is enabled
        """
        self.name = name or self.__class__.__name__
        self.enabled = enabled
        self._condition: Callable[[T], bool] | None = None
        self._async_condition: Callable[[T], bool | Any] | None = None
        self._pre_validators: list[Validator[T]] = []
        self._post_validators: list[Validator[T]] = []
        self._error_handlers: list[Callable[[ValidationResult], None]] = []
        self._metadata: dict[str, Any] = {}
        
    @abstractmethod
    async def validate(
        self,
        value: T,
        context: ValidationContext | None = None,
    ) -> ValidationResult | list[ValidationResult]:
        """Validate value.
        
        Args:
            value: Value to validate
            context: Optional validation context
            
        Returns:
            Validation result(s)
            
        Raises:
            ValidationError: If validation fails
        """
        pass
    
    def when(self, condition: Callable[[T], bool]) -> "Validator[T]":
        """Add condition to validator.
        
        Args:
            condition: Validation condition
            
        Returns:
            Self for chaining
        """
        self._condition = condition
        return self
        
    def when_async(self, condition: Callable[[T], bool | Any]) -> "Validator[T]":
        """Add async condition to validator.
        
        Args:
            condition: Async validation condition
            
        Returns:
            Self for chaining
        """
        self._async_condition = condition
        return self
        
    async def should_validate(self, value: T) -> bool:
        """Check if validator should run.
        
        Args:
            value: Value to check
            
        Returns:
            True if validator should run
        """
        if not self.enabled:
            return False
            
        if self._condition and not self._condition(value):
            return False
            
        if self._async_condition:
            result = await self._async_condition(value)
            if not result:
                return False
                
        return True
        
    def before(self, validator: "Validator[T]") -> "Validator[T]":
        """Add validator to run before this one.
        
        Args:
            validator: Validator to run before
            
        Returns:
            Self for chaining
        """
        self._pre_validators.append(validator)
        return self
        
    def after(self, validator: "Validator[T]") -> "Validator[T]":
        """Add validator to run after this one.
        
        Args:
            validator: Validator to run after
            
        Returns:
            Self for chaining
        """
        self._post_validators.append(validator)
        return self
        
    def on_error(self, handler: Callable[[ValidationResult], None]) -> "Validator[T]":
        """Add error handler.
        
        Args:
            handler: Error handler function
            
        Returns:
            Self for chaining
        """
        self._error_handlers.append(handler)
        return self
        
    def with_metadata(self, **metadata: Any) -> "Validator[T]":
        """Add metadata to validator.
        
        Args:
            **metadata: Metadata to add
            
        Returns:
            Self for chaining
        """
        self._metadata.update(metadata)
        return self
        
    async def run(
        self,
        value: T,
        context: ValidationContext | None = None,
    ) -> list[ValidationResult]:
        """Run validator with pre and post validators.
        
        Args:
            value: Value to validate
            context: Optional validation context
            
        Returns:
            List of validation results
        """
        if not await self.should_validate(value):
            return []
            
        results: list[ValidationResult] = []
        
        # Run pre-validators
        for validator in self._pre_validators:
            if not await validator.should_validate(value):
                continue
                
            try:
                result = await validator.validate(value, context)
                if isinstance(result, list):
                    results.extend(result)
                else:
                    results.append(result)
            except Exception as e:
                result = ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Pre-validator {validator.name} failed: {e}",
                    metadata={
                        "error": str(e),
                        "validator": validator.name,
                        "stage": "pre",
                    },
                    context=context,
                    cause=e,
                )
                results.append(result)
                
        # Run main validator
        try:
            result = await self.validate(value, context)
            if isinstance(result, list):
                results.extend(result)
            else:
                results.append(result)
        except Exception as e:
            result = ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Validator {self.name} failed: {e}",
                metadata={
                    "error": str(e),
                    "validator": self.name,
                    "stage": "main",
                },
                context=context,
                cause=e,
            )
            results.append(result)
            
        # Run post-validators
        for validator in self._post_validators:
            if not await validator.should_validate(value):
                continue
                
            try:
                result = await validator.validate(value, context)
                if isinstance(result, list):
                    results.extend(result)
                else:
                    results.append(result)
            except Exception as e:
                result = ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Post-validator {validator.name} failed: {e}",
                    metadata={
                        "error": str(e),
                        "validator": validator.name,
                        "stage": "post",
                    },
                    context=context,
                    cause=e,
                )
                results.append(result)
                
        # Add validator metadata to results
        if self._metadata:
            for result in results:
                result.metadata.update(self._metadata)
                
        # Handle errors
        for result in results:
            if not result.valid:
                for handler in self._error_handlers:
                    try:
                        handler(result)
                    except Exception:
                        pass  # Ignore handler errors
                        
        return results

class BatchValidator(Validator[T]):
    """Validator that runs multiple validators."""
    
    def __init__(
        self,
        validators: list[Validator[T]],
        name: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize validator.
        
        Args:
            validators: List of validators to run
            name: Validator name
            enabled: Whether validator is enabled
        """
        super().__init__(name=name, enabled=enabled)
        self.validators = validators
        
    async def validate(
        self,
        value: T,
        context: ValidationContext | None = None,
    ) -> list[ValidationResult]:
        """Validate value with all validators.
        
        Args:
            value: Value to validate
            context: Optional validation context
            
        Returns:
            List of validation results
            
        Raises:
            ValidationError: If validation fails
        """
        if not await self.should_validate(value):
            return []
            
        results: list[ValidationResult] = []
        
        for validator in self.validators:
            if not await validator.should_validate(value):
                continue
                
            try:
                result = await validator.validate(value, context)
                if isinstance(result, list):
                    results.extend(result)
                else:
                    results.append(result)
            except Exception as e:
                results.append(ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Validator {validator.name} failed: {e}",
                    metadata={
                        "error": str(e),
                        "validator": validator.name,
                    },
                    context=context,
                ))
                
        return results

class ChainValidator(Validator[T]):
    """Validator that runs validators in sequence until one fails."""
    
    def __init__(
        self,
        validators: list[Validator[T]],
        name: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize validator.
        
        Args:
            validators: List of validators to run
            name: Validator name
            enabled: Whether validator is enabled
        """
        super().__init__(name=name, enabled=enabled)
        self.validators = validators
        
    async def validate(
        self,
        value: T,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate value with validators in sequence.
        
        Args:
            value: Value to validate
            context: Optional validation context
            
        Returns:
            Validation result
            
        Raises:
            ValidationError: If validation fails
        """
        if not await self.should_validate(value):
            return ValidationResult(valid=True)
            
        for validator in self.validators:
            if not await validator.should_validate(value):
                continue
                
            try:
                result = await validator.validate(value, context)
                if isinstance(result, list):
                    # Use first invalid result
                    for r in result:
                        if not r.valid:
                            return r
                elif not result.valid:
                    return result
            except Exception as e:
                return ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Validator {validator.name} failed: {e}",
                    metadata={
                        "error": str(e),
                        "validator": validator.name,
                    },
                    context=context,
                )
                
        return ValidationResult(valid=True)

__all__ = [
    "ValidationLevel",
    "ValidationContext",
    "ValidationResult",
    "Validator",
    "BatchValidator",
    "ChainValidator",
]
