"""Test validation functionality"""

from typing import Any

from pepperpy_core.validation import (
    ValidationLevel,
    ValidationResult,
    Validator,
)


class TestValidator(Validator):
    """Test validator implementation"""

    async def validate(self, value: Any) -> ValidationResult:
        return ValidationResult(valid=True, level=ValidationLevel.INFO)

    async def validate_many(self, values: list[Any]) -> list[ValidationResult]:
        return [await self.validate(value) for value in values]
