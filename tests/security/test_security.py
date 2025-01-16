"""Test security module."""

from pepperpy.security import AuthInfo, SecurityConfig


def test_auth_info() -> None:
    """Test auth info."""
    auth_info = AuthInfo(
        username="test",
        password="test",
        token="test",
        metadata={"key": "value"},
    )
    assert auth_info.username == "test"
    assert auth_info.password == "test"
    assert auth_info.token == "test"
    assert auth_info.metadata == {"key": "value"}


def test_security_config() -> None:
    """Test security config."""
    auth_info = AuthInfo(username="test", password="test")
    config = SecurityConfig(
        enabled=True,
        auth_info=auth_info,
        require_auth=True,
        allow_anonymous=False,
    )
    assert config.enabled
    assert config.auth_info == auth_info
    assert config.require_auth
    assert not config.allow_anonymous
