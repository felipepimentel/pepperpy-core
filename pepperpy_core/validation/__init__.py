"""Validation package exports."""

from .base import (
    ValidationLevel,
    ValidationContext,
    ValidationResult,
    Validator,
    BatchValidator,
    ChainValidator,
)
from .validators import (
    RequiredValidator,
    TypeValidator,
    RangeValidator,
    LengthValidator,
    CompositeValidator,
    any_valid,
    all_valid,
)

# Common validator instances
required = RequiredValidator()
is_string = TypeValidator(str)
is_int = TypeValidator(int)
is_float = TypeValidator(float)
is_bool = TypeValidator(bool)
is_list = TypeValidator(list)
is_dict = TypeValidator(dict)

# Helper functions
def in_range(
    min_value: int | float | None = None,
    max_value: int | float | None = None,
    inclusive: bool = True,
) -> RangeValidator:
    """Create range validator."""
    return RangeValidator(min_value, max_value, inclusive)

def length_between(
    min_length: int | None = None,
    max_length: int | None = None,
) -> LengthValidator:
    """Create length validator."""
    return LengthValidator(min_length, max_length)

def any_of(*validators: Validator[Any]) -> CompositeValidator[Any]:
    """Create validator that passes if any validator passes."""
    return CompositeValidator(list(validators), any_valid)

def all_of(*validators: Validator[Any]) -> CompositeValidator[Any]:
    """Create validator that passes only if all validators pass."""
    return CompositeValidator(list(validators), all_valid)

__all__ = [
    # Base types
    "ValidationLevel",
    "ValidationContext",
    "ValidationResult",
    "Validator",
    "BatchValidator",
    "ChainValidator",
    
    # Validator classes
    "RequiredValidator",
    "TypeValidator",
    "RangeValidator",
    "LengthValidator",
    "CompositeValidator",
    
    # Common instances
    "required",
    "is_string",
    "is_int",
    "is_float",
    "is_bool",
    "is_list",
    "is_dict",
    
    # Helper functions
    "in_range",
    "length_between",
    "any_of",
    "all_of",
    "any_valid",
    "all_valid",
]
