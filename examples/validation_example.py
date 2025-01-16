"""Validation example module."""

from dataclasses import dataclass, field
from typing import Any, Dict


class ValidationResult:
    """Validation result."""

    def __init__(self, is_valid: bool, message: str | None = None) -> None:
        """Initialize validation result.

        Args:
            is_valid: Whether validation passed
            message: Optional error message
        """
        self.is_valid = is_valid
        self.message = message

    def __str__(self) -> str:
        """Get string representation.

        Returns:
            String representation
        """
        return f"ValidationResult(is_valid={self.is_valid}, message={self.message})"


class ValidationError(Exception):
    """Validation error."""

    pass


class Validator:
    """Base validator class."""

    async def validate(self, data: Any) -> ValidationResult:
        """Validate data.

        Args:
            data: Data to validate

        Returns:
            Validation result

        Raises:
            ValidationError: If validation fails
        """
        raise NotImplementedError


@dataclass
class DataValidator(Validator):
    """Example data validator."""

    name: str = "data_validator"
    enabled: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)

    async def validate(self, data: Any) -> ValidationResult:
        """Validate data.

        Args:
            data: Data to validate

        Returns:
            Validation result

        Raises:
            ValidationError: If validation fails
        """
        if not self.enabled:
            return ValidationResult(is_valid=True)

        if not isinstance(data, dict):
            raise ValidationError("Data must be a dictionary")

        required_fields = ["name", "value"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            raise ValidationError(f"Missing required fields: {missing_fields}")

        if not isinstance(data["name"], str):
            raise ValidationError("Name must be a string")

        return ValidationResult(is_valid=True)


async def main() -> None:
    """Run example."""
    # Create validator
    validator = DataValidator(
        name="example_validator",
        enabled=True,
        settings={"strict": True},
    )

    # Valid data
    valid_data = {
        "name": "example",
        "value": 123,
    }

    try:
        result = await validator.validate(valid_data)
        print(f"Validation result: {result}")
    except ValidationError as e:
        print(f"Validation error: {e}")

    # Invalid data
    invalid_data = {
        "value": 123,
    }

    try:
        result = await validator.validate(invalid_data)
        print(f"Validation result: {result}")
    except ValidationError as e:
        print(f"Validation error: {e}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
