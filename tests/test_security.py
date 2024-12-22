"""Tests for the security module."""

import pytest
import pytest_asyncio

from pepperpy_core.security import (
    AuthInfo,
    SecurityConfig,
    SecurityContext,
    SecurityError,
    SecurityManager,
    require_auth,
    require_roles,
)


def test_security_config() -> None:
    """Test security configuration."""
    # Test default values
    config = SecurityConfig(name="test")
    assert config.name == "test"
    assert config.enabled is True
    assert config.require_auth is True
    assert isinstance(config.metadata, dict)
    assert len(config.metadata) == 0

    # Test custom values
    config = SecurityConfig(
        name="test",
        enabled=False,
        require_auth=False,
        metadata={"key": "value"},
    )
    assert config.name == "test"
    assert config.enabled is False
    assert config.require_auth is False
    assert config.metadata == {"key": "value"}

    # Test validation
    config.validate()  # Should not raise


def test_auth_info() -> None:
    """Test authentication information."""
    # Test default values
    auth_info = AuthInfo(user_id="test")
    assert auth_info.user_id == "test"
    assert isinstance(auth_info.roles, list)
    assert len(auth_info.roles) == 0
    assert isinstance(auth_info.permissions, list)
    assert len(auth_info.permissions) == 0
    assert isinstance(auth_info.metadata, dict)
    assert len(auth_info.metadata) == 0

    # Test custom values
    auth_info = AuthInfo(
        user_id="test",
        roles=["admin"],
        permissions=["read", "write"],
        metadata={"key": "value"},
    )
    assert auth_info.user_id == "test"
    assert auth_info.roles == ["admin"]
    assert auth_info.permissions == ["read", "write"]
    assert auth_info.metadata == {"key": "value"}


def test_security_context() -> None:
    """Test security context."""
    # Test unauthenticated context
    context = SecurityContext()
    assert context.auth_info is None
    assert not context.is_authenticated
    assert not context.has_role("admin")
    assert not context.has_permission("read")
    assert isinstance(context.metadata, dict)
    assert len(context.metadata) == 0

    # Test authenticated context
    auth_info = AuthInfo(
        user_id="test",
        roles=["admin"],
        permissions=["read", "write"],
        metadata={"key": "value"},
    )
    context = SecurityContext(auth_info=auth_info, metadata={"context_key": "value"})
    assert context.auth_info == auth_info
    assert context.is_authenticated
    assert context.has_role("admin")
    assert not context.has_role("user")
    assert context.has_permission("read")
    assert context.has_permission("write")
    assert not context.has_permission("delete")
    assert context.metadata == {"context_key": "value"}


@pytest.mark.asyncio
async def test_security_manager() -> None:
    """Test security manager."""
    # Test initialization
    manager = SecurityManager()
    assert isinstance(manager.config, SecurityConfig)
    assert manager.config.name == "security-manager"
    assert not manager.is_initialized

    # Test initialization with custom config
    config = SecurityConfig(name="test", enabled=False, require_auth=False)
    manager = SecurityManager()
    manager.config = config
    assert manager.config == config

    # Test setup and teardown
    await manager.initialize()
    assert manager.is_initialized
    context = manager.get_context()
    assert not context.is_authenticated

    # Test authentication
    auth_info = AuthInfo(
        user_id="test",
        roles=["admin"],
        permissions=["read", "write"],
    )
    await manager.authenticate(auth_info)
    context = manager.get_context()
    assert context.is_authenticated
    assert context.auth_info == auth_info

    # Test statistics
    stats = await manager.get_stats()
    assert stats["name"] == "test"
    assert stats["enabled"] is False
    assert stats["require_auth"] is False
    assert stats["is_authenticated"] is True
    assert stats["user_id"] == "test"
    assert stats["roles_count"] == 1
    assert stats["permissions_count"] == 2

    # Test cleanup
    await manager.teardown()
    assert not manager.is_initialized


@pytest_asyncio.fixture
async def security_manager() -> SecurityManager:
    """Create a security manager for testing."""
    manager = SecurityManager()
    await manager.initialize()
    yield manager
    await manager.teardown()


@pytest.mark.asyncio
async def test_require_auth_decorator(security_manager: SecurityManager) -> None:
    """Test require_auth decorator."""

    @require_auth()
    async def test_func() -> str:
        return "success"

    # Test unauthenticated access
    with pytest.raises(SecurityError, match="Authentication required"):
        await test_func()

    # Test authenticated access
    auth_info = AuthInfo(user_id="test")
    await security_manager.authenticate(auth_info)
    result = await test_func()
    assert result == "success"


@pytest.mark.asyncio
async def test_require_roles_decorator(security_manager: SecurityManager) -> None:
    """Test require_roles decorator."""

    @require_roles("admin", "user")
    async def test_func() -> str:
        return "success"

    # Test unauthenticated access
    with pytest.raises(SecurityError, match="Authentication required"):
        await test_func()

    # Test authenticated access without required roles
    auth_info = AuthInfo(user_id="test", roles=["guest"])
    await security_manager.authenticate(auth_info)
    with pytest.raises(SecurityError, match="Missing required role: admin"):
        await test_func()

    # Test authenticated access with one required role
    auth_info = AuthInfo(user_id="test", roles=["admin"])
    await security_manager.authenticate(auth_info)
    with pytest.raises(SecurityError, match="Missing required role: user"):
        await test_func()

    # Test authenticated access with all required roles
    auth_info = AuthInfo(user_id="test", roles=["admin", "user"])
    await security_manager.authenticate(auth_info)
    result = await test_func()
    assert result == "success"
