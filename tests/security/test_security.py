"""Security module tests."""

import pytest
from pepperpy_core.security.config import SecurityConfig


@pytest.mark.asyncio
async def test_security_config() -> None:
    """Test security configuration."""
    config = SecurityConfig(
        name="test-security",
        enabled=True,
        strict_mode=False,
        metadata={"test": "value"},
    )
    assert config.name == "test-security"
    assert config.enabled is True
    assert config.strict_mode is False
    assert config.metadata == {"test": "value"}
