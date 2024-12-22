"""Shared test configurations and fixtures."""

from dataclasses import dataclass, field
from typing import Any

import pytest

from pepperpy_core.module import ModuleConfig


@pytest.mark.no_cover
@dataclass
class TestConfig(ModuleConfig):
    """Test configuration."""

    name: str = "test-module"
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate configuration."""
        pass
