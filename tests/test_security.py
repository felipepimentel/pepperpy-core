"""Test security module."""

from typing import AsyncGenerator

import pytest

from pepperpy.exceptions import SecurityError
from pepperpy.security import AuthInfo, SecurityManager


@pytest.fixture
async def security_manager() -> AsyncGenerator[SecurityManager, None]:
    """Get security manager."""
    manager = SecurityManager()
    await manager.initialize()
    manager.config.auth_info["test"] = AuthInfo("test", ["test"])
    yield manager
    await manager.teardown()


@pytest.mark.asyncio
async def test_security_manager_authenticate_valid(
    security_manager: SecurityManager,
) -> None:
    """Test security manager authenticate valid."""
    auth_info = AuthInfo("test", ["test"])
    await security_manager.authenticate(auth_info)


@pytest.mark.asyncio
async def test_security_manager_authenticate_invalid_username(
    security_manager: SecurityManager,
) -> None:
    """Test security manager authenticate invalid username."""
    auth_info = AuthInfo("invalid", ["test"])
    with pytest.raises(SecurityError):
        await security_manager.authenticate(auth_info)


@pytest.mark.asyncio
async def test_security_manager_authenticate_invalid_password(
    security_manager: SecurityManager,
) -> None:
    """Test security manager authenticate invalid password."""
    auth_info = AuthInfo("test", ["invalid"])
    with pytest.raises(SecurityError):
        await security_manager.authenticate(auth_info)


@pytest.mark.asyncio
async def test_security_manager_authenticate_invalid_both(
    security_manager: SecurityManager,
) -> None:
    """Test security manager authenticate invalid both."""
    auth_info = AuthInfo("invalid", ["invalid"])
    with pytest.raises(SecurityError):
        await security_manager.authenticate(auth_info)


@pytest.mark.asyncio
async def test_security_manager_authenticate_empty(
    security_manager: SecurityManager,
) -> None:
    """Test security manager authenticate empty."""
    auth_info = AuthInfo("", [])
    with pytest.raises(SecurityError):
        await security_manager.authenticate(auth_info)
