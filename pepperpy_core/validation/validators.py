"""Common validators implementation."""

import re
from pathlib import Path
from typing import Any, Callable, Pattern, TypeVar, get_args, get_origin

from .base import ValidationContext, ValidationLevel, ValidationResult, Validator

T = TypeVar("T")

class CompositeValidator(Validator[T]):
    """Validator that combines multiple validators with custom logic."""
    
    def __init__(
        self,
        validators: list[Validator[T]],
        combine_func: Callable[[list[ValidationResult]], ValidationResult],
        name: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize validator.
        
        Args:
            validators: List of validators to combine
            combine_func: Function to combine validation results
            name: Validator name
            enabled: Whether validator is enabled
        """
        super().__init__(name=name, enabled=enabled)
        self.validators = validators
        self.combine_func = combine_func
        
    async def validate(
        self,
        value: T,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate value with all validators and combine results.
        
        Args:
            value: Value to validate
            context: Optional validation context
            
        Returns:
            Combined validation result
        """
        if not await self.should_validate(value):
            return ValidationResult(valid=True)
            
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
                
        return self.combine_func(results)

def any_valid(results: list[ValidationResult]) -> ValidationResult:
    """Combine validation results with OR logic.
    
    Args:
        results: List of validation results
        
    Returns:
        Combined result that is valid if any result is valid
    """
    if not results:
        return ValidationResult(valid=True)
        
    valid_results = [r for r in results if r.valid]
    if valid_results:
        return valid_results[0]
        
    # Combine invalid results
    return ValidationResult(
        valid=False,
        level=max(r.level for r in results),
        message="\n".join(r.message for r in results if r.message),
        metadata={
            k: v
            for r in results
            for k, v in r.metadata.items()
        },
        details=[
            d
            for r in results
            for d in r.details
        ],
    )

def all_valid(results: list[ValidationResult]) -> ValidationResult:
    """Combine validation results with AND logic.
    
    Args:
        results: List of validation results
        
    Returns:
        Combined result that is valid only if all results are valid
    """
    if not results:
        return ValidationResult(valid=True)
        
    invalid_results = [r for r in results if not r.valid]
    if not invalid_results:
        return results[0]
        
    # Combine invalid results
    return ValidationResult(
        valid=False,
        level=max(r.level for r in invalid_results),
        message="\n".join(r.message for r in invalid_results if r.message),
        metadata={
            k: v
            for r in invalid_results
            for k, v in r.metadata.items()
        },
        details=[
            d
            for r in invalid_results
            for d in r.details
        ],
    )

class RequiredValidator(Validator[Any]):
    """Validates that a value is not None."""
    
    async def validate(
        self,
        value: Any,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate value is not None.
        
        Args:
            value: Value to validate
            context: Optional validation context
            
        Returns:
            Validation result
        """
        return ValidationResult(
            valid=value is not None,
            level=ValidationLevel.ERROR,
            message="Value is required and cannot be None",
            context=context,
        )

class TypeValidator(Validator[Any]):
    """Validates that a value is of a specific type."""
    
    def __init__(
        self,
        expected_type: type | tuple[type, ...] | Any,
        check_generic_args: bool = True,
        name: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize validator.
        
        Args:
            expected_type: Expected type or tuple of types
            check_generic_args: Whether to check generic type arguments
            name: Validator name
            enabled: Whether validator is enabled
        """
        super().__init__(name=name, enabled=enabled)
        self.expected_type = expected_type
        self.check_generic_args = check_generic_args
        
    async def validate(
        self,
        value: Any,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate value type.
        
        Args:
            value: Value to validate
            context: Optional validation context
            
        Returns:
            Validation result
        """
        if self.expected_type is Any:
            return ValidationResult(valid=True, context=context)
            
        valid = isinstance(value, self.expected_type)
        if not valid:
            type_names = (
                [t.__name__ for t in self.expected_type]
                if isinstance(self.expected_type, tuple)
                else [self.expected_type.__name__]
            )
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Expected type {'or '.join(type_names)}, got {type(value).__name__}",
                context=context,
            )
            
        # Check generic type arguments if requested
        if self.check_generic_args:
            origin = get_origin(self.expected_type)
            if origin is not None:
                args = get_args(self.expected_type)
                value_args = get_args(type(value))
                if len(args) != len(value_args):
                    return ValidationResult(
                        valid=False,
                        level=ValidationLevel.ERROR,
                        message=f"Expected {len(args)} type arguments, got {len(value_args)}",
                        context=context,
                    )
                for expected, actual in zip(args, value_args):
                    if expected is not Any and expected != actual:
                        return ValidationResult(
                            valid=False,
                            level=ValidationLevel.ERROR,
                            message=f"Expected type argument {expected.__name__}, got {actual.__name__}",
                            context=context,
                        )
                        
        return ValidationResult(valid=True, context=context)

class RangeValidator(Validator[int | float]):
    """Validates that a numeric value is within a range."""
    
    def __init__(
        self,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        inclusive: bool = True,
        allow_infinity: bool = False,
        name: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize validator.
        
        Args:
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            inclusive: Whether range bounds are inclusive
            allow_infinity: Whether to allow infinite values
            name: Validator name
            enabled: Whether validator is enabled
        """
        super().__init__(name=name, enabled=enabled)
        self.min_value = min_value
        self.max_value = max_value
        self.inclusive = inclusive
        self.allow_infinity = allow_infinity
        
    async def validate(
        self,
        value: int | float,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate value is within range.
        
        Args:
            value: Value to validate
            context: Optional validation context
            
        Returns:
            Validation result
        """
        if not isinstance(value, (int, float)):
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Expected numeric value, got {type(value).__name__}",
                context=context,
            )
            
        # Check for infinity
        if not self.allow_infinity and (value == float("inf") or value == float("-inf")):
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message="Infinite values are not allowed",
                context=context,
            )
            
        if self.min_value is not None:
            if self.inclusive and value < self.min_value:
                return ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Value must be greater than or equal to {self.min_value}",
                    context=context,
                )
            elif not self.inclusive and value <= self.min_value:
                return ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Value must be greater than {self.min_value}",
                    context=context,
                )
                
        if self.max_value is not None:
            if self.inclusive and value > self.max_value:
                return ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Value must be less than or equal to {self.max_value}",
                    context=context,
                )
            elif not self.inclusive and value >= self.max_value:
                return ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Value must be less than {self.max_value}",
                    context=context,
                )
                
        return ValidationResult(valid=True, context=context)

class LengthValidator(Validator[Any]):
    """Validates the length of a value."""
    
    def __init__(
        self,
        min_length: int | None = None,
        max_length: int | None = None,
        name: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize validator.
        
        Args:
            min_length: Minimum length
            max_length: Maximum length
            name: Validator name
            enabled: Whether validator is enabled
        """
        super().__init__(name=name, enabled=enabled)
        self.min_length = min_length
        self.max_length = max_length
        
    async def validate(
        self,
        value: Any,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate value length.
        
        Args:
            value: Value to validate
            context: Optional validation context
            
        Returns:
            Validation result
        """
        try:
            length = len(value)
        except (TypeError, AttributeError):
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Value of type {type(value).__name__} does not support length check",
                context=context,
            )
            
        if self.min_length is not None and length < self.min_length:
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Length must be at least {self.min_length}, got {length}",
                context=context,
            )
            
        if self.max_length is not None and length > self.max_length:
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Length must be at most {self.max_length}, got {length}",
                context=context,
            )
            
        return ValidationResult(valid=True, context=context)

class PatternValidator(Validator[str]):
    """Validates that a string matches a pattern."""
    
    def __init__(
        self,
        pattern: str | Pattern[str],
        flags: int = 0,
        name: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize validator.
        
        Args:
            pattern: Regular expression pattern
            flags: Regular expression flags
            name: Validator name
            enabled: Whether validator is enabled
        """
        super().__init__(name=name, enabled=enabled)
        self.pattern = pattern if isinstance(pattern, Pattern) else re.compile(pattern, flags)
        
    async def validate(
        self,
        value: str,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate string matches pattern.
        
        Args:
            value: Value to validate
            context: Optional validation context
            
        Returns:
            Validation result
        """
        if not isinstance(value, str):
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Expected string value, got {type(value).__name__}",
                context=context,
            )
            
        return ValidationResult(
            valid=bool(self.pattern.match(value)),
            level=ValidationLevel.ERROR,
            message=f"Value must match pattern '{self.pattern.pattern}'",
            context=context,
        )

class PathValidator(Validator[Path | str]):
    """Validates file system paths."""
    
    def __init__(
        self,
        must_exist: bool = True,
        must_be_file: bool = False,
        must_be_dir: bool = False,
        name: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize validator.
        
        Args:
            must_exist: Whether path must exist
            must_be_file: Whether path must be a file
            must_be_dir: Whether path must be a directory
            name: Validator name
            enabled: Whether validator is enabled
        """
        super().__init__(name=name, enabled=enabled)
        self.must_exist = must_exist
        self.must_be_file = must_be_file
        self.must_be_dir = must_be_dir
        
    async def validate(
        self,
        value: Path | str,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate path.
        
        Args:
            value: Value to validate
            context: Optional validation context
            
        Returns:
            Validation result
        """
        path = Path(value)
        
        if self.must_exist and not path.exists():
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Path {path} does not exist",
                context=context,
            )
            
        if self.must_be_file and not path.is_file():
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Path {path} is not a file",
                context=context,
            )
            
        if self.must_be_dir and not path.is_dir():
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Path {path} is not a directory",
                context=context,
            )
            
        return ValidationResult(valid=True, context=context)

class CallableValidator(Validator[Any]):
    """Validates values using a custom function."""
    
    def __init__(
        self,
        func: Callable[[Any], bool | ValidationResult],
        error_message: str = "Validation failed",
        name: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize validator.
        
        Args:
            func: Validation function
            error_message: Error message if validation fails
            name: Validator name
            enabled: Whether validator is enabled
        """
        super().__init__(name=name, enabled=enabled)
        self.func = func
        self.error_message = error_message
        
    async def validate(
        self,
        value: Any,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate value using custom function.
        
        Args:
            value: Value to validate
            context: Optional validation context
            
        Returns:
            Validation result
        """
        try:
            result = self.func(value)
        except Exception as e:
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Validation function failed: {e}",
                context=context,
            )
            
        if isinstance(result, ValidationResult):
            return result.with_context(context) if context else result
            
        return ValidationResult(
            valid=bool(result),
            level=ValidationLevel.ERROR,
            message=self.error_message,
            context=context,
        )

# Common validator instances
required = RequiredValidator()
is_string = TypeValidator(str)
is_int = TypeValidator(int)
is_float = TypeValidator((int, float))
is_bool = TypeValidator(bool)
is_list = TypeValidator(list)
is_dict = TypeValidator(dict)
is_path = TypeValidator((str, Path))

__all__ = [
    "RequiredValidator",
    "TypeValidator",
    "RangeValidator",
    "LengthValidator",
    "PatternValidator",
    "PathValidator",
    "CallableValidator",
    "required",
    "is_string",
    "is_int",
    "is_float",
    "is_bool",
    "is_list",
    "is_dict",
    "is_path",
] 