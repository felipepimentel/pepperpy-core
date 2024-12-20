"""Common validators implementation."""

import re
from dataclasses import is_dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Pattern, TypeVar, get_args, get_origin
from uuid import UUID

from .base import ValidationContext, ValidationLevel, ValidationResult, Validator

T = TypeVar("T")

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

class DateTimeValidator(Validator[datetime]):
    """Validates datetime values."""
    
    def __init__(
        self,
        min_value: datetime | None = None,
        max_value: datetime | None = None,
        name: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize validator.
        
        Args:
            min_value: Minimum allowed datetime
            max_value: Maximum allowed datetime
            name: Validator name
            enabled: Whether validator is enabled
        """
        super().__init__(name=name, enabled=enabled)
        self.min_value = min_value
        self.max_value = max_value
        
    async def validate(
        self,
        value: datetime,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate datetime value.
        
        Args:
            value: Value to validate
            context: Optional validation context
            
        Returns:
            Validation result
        """
        if not isinstance(value, datetime):
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Expected datetime value, got {type(value).__name__}",
                context=context,
            )
            
        if self.min_value is not None and value < self.min_value:
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Value must be after {self.min_value}",
                context=context,
            )
            
        if self.max_value is not None and value > self.max_value:
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Value must be before {self.max_value}",
                context=context,
            )
            
        return ValidationResult(valid=True, context=context)

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

class DataclassValidator(Validator[Any]):
    """Validates dataclass instances."""
    
    def __init__(
        self,
        dataclass_type: type,
        validate_fields: bool = True,
        name: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize validator.
        
        Args:
            dataclass_type: Expected dataclass type
            validate_fields: Whether to validate dataclass fields
            name: Validator name
            enabled: Whether validator is enabled
        """
        super().__init__(name=name, enabled=enabled)
        if not is_dataclass(dataclass_type):
            raise ValueError(f"Type {dataclass_type.__name__} is not a dataclass")
        self.dataclass_type = dataclass_type
        self.validate_fields = validate_fields
        
    async def validate(
        self,
        value: Any,
        context: ValidationContext | None = None,
    ) -> ValidationResult | list[ValidationResult]:
        """Validate dataclass instance.
        
        Args:
            value: Value to validate
            context: Optional validation context
            
        Returns:
            Validation result(s)
        """
        if not isinstance(value, self.dataclass_type):
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Expected {self.dataclass_type.__name__} instance, got {type(value).__name__}",
                context=context,
            )
            
        if not self.validate_fields:
            return ValidationResult(valid=True, context=context)
            
        results: list[ValidationResult] = []
        
        for field in value.__dataclass_fields__.values():
            field_value = getattr(value, field.name)
            field_context = context.child(field.name) if context else ValidationContext(path=field.name)
            
            # Validate field type
            type_validator = TypeValidator(field.type)
            result = await type_validator.validate(field_value, field_context)
            if not result.valid:
                results.append(result)
                
            # Validate nested dataclass
            if is_dataclass(field.type):
                nested_validator = DataclassValidator(field.type)
                result = await nested_validator.validate(field_value, field_context)
                if isinstance(result, list):
                    results.extend(result)
                elif not result.valid:
                    results.append(result)
                    
        return results if results else ValidationResult(valid=True, context=context)

class EnumValidator(Validator[Any]):
    """Validates that a value is a valid enum member."""
    
    def __init__(
        self,
        enum_type: type[Enum],
        allow_names: bool = True,
        allow_values: bool = True,
        name: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize validator.
        
        Args:
            enum_type: Expected enum type
            allow_names: Whether to allow enum member names
            allow_values: Whether to allow enum member values
            name: Validator name
            enabled: Whether validator is enabled
        """
        super().__init__(name=name, enabled=enabled)
        if not issubclass(enum_type, Enum):
            raise ValueError(f"Type {enum_type.__name__} is not an Enum")
        self.enum_type = enum_type
        self.allow_names = allow_names
        self.allow_values = allow_values
        
    async def validate(
        self,
        value: Any,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate enum value.
        
        Args:
            value: Value to validate
            context: Optional validation context
            
        Returns:
            Validation result
        """
        if isinstance(value, self.enum_type):
            return ValidationResult(valid=True, context=context)
            
        if self.allow_names and isinstance(value, str):
            try:
                self.enum_type[value]
                return ValidationResult(valid=True, context=context)
            except KeyError:
                pass
                
        if self.allow_values:
            try:
                self.enum_type(value)
                return ValidationResult(valid=True, context=context)
            except ValueError:
                pass
                
        valid_values = []
        if self.allow_names:
            valid_values.extend([m.name for m in self.enum_type])
        if self.allow_values:
            valid_values.extend([m.value for m in self.enum_type])
            
        return ValidationResult(
            valid=False,
            level=ValidationLevel.ERROR,
            message=f"Value must be one of: {', '.join(map(str, valid_values))}",
            context=context,
        )

class DecimalValidator(Validator[Decimal | str | float | int]):
    """Validates decimal values."""
    
    def __init__(
        self,
        min_value: Decimal | None = None,
        max_value: Decimal | None = None,
        max_digits: int | None = None,
        decimal_places: int | None = None,
        name: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize validator.
        
        Args:
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            max_digits: Maximum total digits
            decimal_places: Maximum decimal places
            name: Validator name
            enabled: Whether validator is enabled
        """
        super().__init__(name=name, enabled=enabled)
        self.min_value = Decimal(str(min_value)) if min_value is not None else None
        self.max_value = Decimal(str(max_value)) if max_value is not None else None
        self.max_digits = max_digits
        self.decimal_places = decimal_places
        
    async def validate(
        self,
        value: Decimal | str | float | int,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate decimal value.
        
        Args:
            value: Value to validate
            context: Optional validation context
            
        Returns:
            Validation result
        """
        try:
            decimal_value = Decimal(str(value))
        except (TypeError, ValueError, decimal.InvalidOperation):
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Value must be a valid decimal number",
                context=context,
            )
            
        if self.min_value is not None and decimal_value < self.min_value:
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Value must be greater than or equal to {self.min_value}",
                context=context,
            )
            
        if self.max_value is not None and decimal_value > self.max_value:
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Value must be less than or equal to {self.max_value}",
                context=context,
            )
            
        if self.max_digits is not None or self.decimal_places is not None:
            str_value = str(decimal_value)
            if "." in str_value:
                integer_part, decimal_part = str_value.split(".")
            else:
                integer_part, decimal_part = str_value, ""
                
            if self.max_digits is not None:
                total_digits = len(integer_part.lstrip("-")) + len(decimal_part)
                if total_digits > self.max_digits:
                    return ValidationResult(
                        valid=False,
                        level=ValidationLevel.ERROR,
                        message=f"Value must have at most {self.max_digits} digits in total",
                        context=context,
                    )
                    
            if self.decimal_places is not None and len(decimal_part) > self.decimal_places:
                return ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Value must have at most {self.decimal_places} decimal places",
                    context=context,
                )
                
        return ValidationResult(valid=True, context=context)

class UUIDValidator(Validator[UUID | str]):
    """Validates UUID values."""
    
    def __init__(
        self,
        version: int | None = None,
        name: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize validator.
        
        Args:
            version: Required UUID version (1-5)
            name: Validator name
            enabled: Whether validator is enabled
        """
        super().__init__(name=name, enabled=enabled)
        if version is not None and version not in range(1, 6):
            raise ValueError("UUID version must be between 1 and 5")
        self.version = version
        
    async def validate(
        self,
        value: UUID | str,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate UUID value.
        
        Args:
            value: Value to validate
            context: Optional validation context
            
        Returns:
            Validation result
        """
        try:
            uuid_value = value if isinstance(value, UUID) else UUID(value)
        except (TypeError, ValueError, AttributeError):
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message="Value must be a valid UUID",
                context=context,
            )
            
        if self.version is not None and uuid_value.version != self.version:
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"UUID must be version {self.version}",
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

class TimezoneValidator(Validator[datetime]):
    """Validates datetime timezone."""
    
    def __init__(
        self,
        require_tzinfo: bool = True,
        allowed_timezones: list[timezone] | None = None,
        name: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize validator.
        
        Args:
            require_tzinfo: Whether to require timezone info
            allowed_timezones: List of allowed timezones
            name: Validator name
            enabled: Whether validator is enabled
        """
        super().__init__(name=name, enabled=enabled)
        self.require_tzinfo = require_tzinfo
        self.allowed_timezones = allowed_timezones
        
    async def validate(
        self,
        value: datetime,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate datetime timezone.
        
        Args:
            value: Value to validate
            context: Optional validation context
            
        Returns:
            Validation result
        """
        if not isinstance(value, datetime):
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Expected datetime value, got {type(value).__name__}",
                context=context,
            )
            
        if self.require_tzinfo and value.tzinfo is None:
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message="Datetime must have timezone information",
                context=context,
            )
            
        if self.allowed_timezones and value.tzinfo not in self.allowed_timezones:
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Timezone must be one of: {', '.join(tz.tzname(None) for tz in self.allowed_timezones)}",
                context=context,
            )
            
        return ValidationResult(valid=True, context=context)

# Common validator instances
required = RequiredValidator()
is_string = TypeValidator(str)
is_int = TypeValidator(int)
is_float = TypeValidator((int, float))
is_bool = TypeValidator(bool)
is_list = TypeValidator(list)
is_dict = TypeValidator(dict)
is_datetime = TypeValidator(datetime)
is_path = TypeValidator((str, Path))
is_decimal = TypeValidator((Decimal, str, float, int))
is_uuid = TypeValidator((UUID, str))

__all__ = [
    "RequiredValidator",
    "TypeValidator",
    "RangeValidator",
    "LengthValidator",
    "PatternValidator",
    "DateTimeValidator",
    "PathValidator",
    "DataclassValidator",
    "EnumValidator",
    "DecimalValidator",
    "UUIDValidator",
    "CallableValidator",
    "TimezoneValidator",
    "required",
    "is_string",
    "is_int",
    "is_float",
    "is_bool",
    "is_list",
    "is_dict",
    "is_datetime",
    "is_path",
    "is_decimal",
    "is_uuid",
] 