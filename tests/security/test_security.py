"""Test security module."""

from typing import AsyncGenerator

import pytest

from pepperpy_core.security import AuthInfo, SecurityManager


@pytest.fixture
async def security_manager() -> AsyncGenerator[SecurityManager, None]:
    """Get security manager."""
    manager = SecurityManager()
    await manager.initialize()
    manager.config.auth_info["test"] = AuthInfo("test", ["test"])
    yield manager
    await manager.teardown()


@pytest.mark.asyncio
async def test_security_manager_config() -> None:
    """Test security manager configuration."""
    manager = SecurityManager()
    assert manager.config.name == "security-manager"
    assert manager.config.enabled is True
