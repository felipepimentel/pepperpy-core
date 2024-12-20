"""Validation example."""

from typing import Any

from pepperpy_core.types import JsonDict
from pepperpy_core.validation import ValidationResult, Validator


class ValidatorConfig:
    """Validator configuration."""

    def __init__(
        self,
        name: str = "",
        enabled: bool = True,
        stop_on_error: bool = False,
        metadata: JsonDict | None = None,
    ) -> None:
        """Initialize configuration.
        
        Args:
            name: Validator name
            enabled: Whether validator is enabled
            stop_on_error: Whether to stop on first error
            metadata: Additional metadata
        """
        self.name = name
        self.enabled = enabled
        self.stop_on_error = stop_on_error
        self.metadata = metadata or {}


class DataValidator(Validator[Any]):
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
        }
