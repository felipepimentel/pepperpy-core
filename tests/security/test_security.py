"""Security module tests."""

import pytest

from pepperpy_core.security import SecurityConfig


@pytest.mark.asyncio
async def test_security_config() -> None:
    """Test security configuration."""
    config = SecurityConfig(
        name="test-security",
        enabled=True,
        require_auth=False,
        metadata={"test": "value"},
    )
    assert config.name == "test-security"
    assert config.enabled is True
    assert config.require_auth is False
    assert config.metadata == {"test": "value"}
