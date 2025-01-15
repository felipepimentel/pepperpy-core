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


def test_security_context_validation() -> None:
    """Test security context validation."""
    # Test valid context
    context = SecurityContext(path="/test", metadata={"key": "value"})
    assert context.path == "/test"
    assert context.metadata == {"key": "value"}
    assert context.parent is None
    assert context._children == []

    # Test invalid path type
    with pytest.raises(SecurityError) as exc_info:
        SecurityContext(path=42)  # type: ignore
    assert "path must be a string" in str(exc_info.value)
    assert "int" in str(exc_info.value)

    # Test invalid metadata type
    with pytest.raises(SecurityError) as exc_info:
        SecurityContext(path="/test", metadata=[])  # type: ignore
    assert "metadata must be a dictionary" in str(exc_info.value)
    assert "list" in str(exc_info.value)


def test_security_level_str() -> None:
    """Test security level string representation."""
    assert str(SecurityLevel.LOW) == "low"
    assert str(SecurityLevel.MEDIUM) == "medium"
    assert str(SecurityLevel.HIGH) == "high"
    assert str(SecurityLevel.CRITICAL) == "critical"


@pytest.mark.asyncio
async def test_security_validator_disabled() -> None:
    """Test disabled security validator."""
    validator = TestValidator(enabled=False)
    result = await validator.validate("test")
    assert result.valid is True
    assert result.level == SecurityLevel.LOW
    assert result.message == "Validator is disabled"


@pytest.mark.asyncio
async def test_security_manager_disabled() -> None:
    """Test disabled security manager."""
    manager = SecurityManager()
    await manager.initialize()
    manager.config.enabled = False

    validator = TestValidator()
    await manager.add_validator(validator)

    result = await manager.validate("")
    assert result.valid is True
    assert result.level == SecurityLevel.LOW
    assert result.message == "Security is disabled"


@pytest.mark.asyncio
async def test_security_manager_authenticate_missing_username() -> None:
    """Test authenticate with missing username."""
    manager = SecurityManager()
    await manager.initialize()
    auth_info = AuthInfo(username="", password=["test"])

    with pytest.raises(SecurityError) as exc_info:
        await manager.authenticate(auth_info)
    assert "Username is required" in str(exc_info.value)


@pytest.mark.asyncio
async def test_security_manager_authenticate_missing_password() -> None:
    """Test authenticate with missing password."""
    manager = SecurityManager()
    await manager.initialize()
    auth_info = AuthInfo(username="test", password=[])

    with pytest.raises(SecurityError) as exc_info:
        await manager.authenticate(auth_info)
    assert "Password is required" in str(exc_info.value)


@pytest.mark.asyncio
async def test_security_manager_authenticate_invalid_password() -> None:
    """Test authenticate with invalid password."""
    manager = SecurityManager()
    await manager.initialize()

    # Add valid credentials
    valid_auth = AuthInfo(username="test", password=["correct"])
    manager.config.auth_info["test"] = valid_auth

    # Try with invalid password
    invalid_auth = AuthInfo(username="test", password=["wrong"])
    with pytest.raises(SecurityError) as exc_info:
        await manager.authenticate(invalid_auth)
    assert "Invalid password" in str(exc_info.value)


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
