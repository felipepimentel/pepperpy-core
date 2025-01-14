"""Test security implementation."""

import pytest

from pepperpy.security import (
    AuthInfo,
    SecurityContext,
    SecurityError,
    SecurityLevel,
    SecurityManager,
    SecurityResult,
    SecurityValidator,
)


class TestValidator(SecurityValidator):
    """Test validator implementation."""

    async def _validate(
        self,
        value: str,
        context: SecurityContext | None = None,
    ) -> SecurityResult:
        """Validate value."""
        if not value:
            return SecurityResult(
                valid=False,
                level=SecurityLevel.HIGH,
                message="Value cannot be empty",
                context=context,
            )
        return SecurityResult(valid=True, context=context)


@pytest.mark.asyncio
async def test_security_manager_init() -> None:
    """Test security manager initialization."""
    manager = SecurityManager()
    assert manager.config.name == "security-manager"
    assert manager.config.enabled is True
    assert manager.config.level == SecurityLevel.HIGH


@pytest.mark.asyncio
async def test_security_manager_setup() -> None:
    """Test security manager setup."""
    manager = SecurityManager()
    await manager.initialize()
    assert manager.is_initialized
    assert len(manager._validators) == 0


@pytest.mark.asyncio
async def test_security_manager_teardown() -> None:
    """Test security manager teardown."""
    manager = SecurityManager()
    await manager.initialize()
    await manager.teardown()
    assert not manager.is_initialized
    assert len(manager._validators) == 0


@pytest.mark.asyncio
async def test_security_manager_add_validator() -> None:
    """Test add validator."""
    manager = SecurityManager()
    await manager.initialize()
    validator = TestValidator()
    await manager.add_validator(validator)
    assert validator in manager._validators


@pytest.mark.asyncio
async def test_security_manager_remove_validator() -> None:
    """Test remove validator."""
    manager = SecurityManager()
    await manager.initialize()
    validator = TestValidator()
    await manager.add_validator(validator)
    await manager.remove_validator(validator)
    assert validator not in manager._validators


@pytest.mark.asyncio
async def test_security_manager_validate() -> None:
    """Test validate."""
    manager = SecurityManager()
    await manager.initialize()
    validator = TestValidator()
    await manager.add_validator(validator)
    result = await manager.validate("test")
    assert result.valid is True


@pytest.mark.asyncio
async def test_security_manager_validate_invalid() -> None:
    """Test validate invalid."""
    manager = SecurityManager()
    await manager.initialize()
    validator = TestValidator()
    await manager.add_validator(validator)
    result = await manager.validate("")
    assert result.valid is False
    assert result.level == SecurityLevel.HIGH
    assert result.message == "Value cannot be empty"


@pytest.mark.asyncio
async def test_security_manager_authenticate() -> None:
    """Test authenticate."""
    manager = SecurityManager()
    await manager.initialize()
    auth_info = AuthInfo(username="test", password=["test"])
    manager.config.auth_info["test"] = auth_info
    await manager.authenticate(auth_info)


@pytest.mark.asyncio
async def test_security_manager_authenticate_invalid() -> None:
    """Test authenticate invalid."""
    manager = SecurityManager()
    await manager.initialize()
    auth_info = AuthInfo(username="test", password=["test"])
    with pytest.raises(SecurityError):
        await manager.authenticate(auth_info)
