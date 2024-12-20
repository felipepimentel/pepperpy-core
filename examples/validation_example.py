"""Validation example."""

from dataclasses import dataclass, field
from typing import Any

from pepperpy_core.types import JsonDict
from pepperpy_core.validation import Validator as BaseValidator
from pepperpy_core.validation.base import ValidationResult
from pepperpy_core.validation.types import ValidationData


@dataclass
class ValidatorConfig(ValidationData):
    """Validator configuration."""

    name: str = ""
    enabled: bool = True
    stop_on_error: bool = False
    metadata: JsonDict = field(default_factory=dict)


class DataValidator(BaseValidator):
    """Example data validator."""

    def __init__(self) -> None:
        """Initialize validator."""
        super().__init__()
        self.config = ValidatorConfig(name="validator")
        self._validations: int = 0
        self._errors: int = 0
        self._initialized: bool = False

    async def _setup(self) -> None:
        """Setup validator resources."""
        self._initialized = True

    async def _teardown(self) -> None:
        """Teardown validator resources."""
        self._validations = 0
        self._errors = 0
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Ensure validator is initialized."""
        if not self._initialized:
            raise RuntimeError("Validator not initialized")

    async def validate(self, value: Any) -> ValidationResult:
        """Validate data.

        Args:
            value: Value to validate

        Returns:
            Validation result
        """
        self._ensure_initialized()
        if not self.config.enabled:
            return ValidationResult(valid=True)

        # Simulate validation
        self._validations += 1
        errors: list[str] = []

        if not value:
            errors.append("Data cannot be empty")
            self._errors += 1

        if self.config.stop_on_error and errors:
            return ValidationResult(valid=False, message=errors[0] if errors else None)

        # Additional validation logic here...

        return ValidationResult(
            valid=len(errors) == 0, message=errors[0] if errors else None
        )

    async def get_stats(self) -> dict[str, Any]:
        """Get validator statistics."""
        self._ensure_initialized()
        return {
            "name": self.config.name,
            "enabled": self.config.enabled,
            "validations": self._validations,
            "errors": self._errors,
            "max_errors": self.config.max_errors,
        }
