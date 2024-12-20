"""Security test configuration and fixtures."""

from dataclasses import dataclass, field
from typing import Any

import pytest
from pepperpy_core.security.config import SecurityConfig


@dataclass
class TestSecurityConfig(SecurityConfig):
    """Test security configuration."""

    # Required fields (herdado de SecurityConfig)
    name: str = "test-security"

    # Optional fields
    enabled: bool = True
    strict_mode: bool = False
    secret_key: str = "test-secret-key"
    token_expiration: int = 3600
    metadata: dict[str, Any] = field(default_factory=dict)


@pytest.fixture
def security_config() -> TestSecurityConfig:
    """Create security configuration.

    Returns:
        Security configuration
    """
    return TestSecurityConfig()
