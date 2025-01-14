"""Test dependency management module."""

import pytest

from pepperpy.dependencies import (
    DependencyError,
    DependencyManager,
    check_dependency,
    get_installation_command,
    get_missing_dependencies,
    verify_dependencies,
)


def test_check_dependency() -> None:
    """Test check_dependency returns correct status."""
    # Test with installed package
    assert check_dependency("pytest") is True
    # Test with non-existent package
    assert check_dependency("nonexistent_package") is False


def test_get_missing_dependencies() -> None:
    """Test get_missing_dependencies returns correct list."""
    packages = ["pytest", "nonexistent_package"]
    missing = get_missing_dependencies(packages)
    assert missing == ["nonexistent_package"]


def test_verify_dependencies() -> None:
    """Test verify_dependencies raises error for missing packages."""
    # Test with installed packages
    verify_dependencies(["pytest"])

    # Test with missing package
    with pytest.raises(DependencyError) as exc_info:
        verify_dependencies(["nonexistent_package"])
    assert "Missing required dependencies: nonexistent_package" in str(exc_info.value)
    assert exc_info.value.package == "nonexistent_package"


def test_get_installation_command() -> None:
    """Test get_installation_command returns correct command."""
    # Test with poetry
    cmd = get_installation_command(["package1", "package2"], use_poetry=True)
    assert cmd == "poetry add package1 package2"

    # Test with pip
    cmd = get_installation_command(["package1", "package2"], use_poetry=False)
    assert cmd == "pip install package1 package2"


def test_dependency_manager_init() -> None:
    """Test DependencyManager initialization."""
    manager = DependencyManager()
    assert manager._provider_deps == {}
    assert manager._feature_deps == {}


def test_dependency_manager_register_provider() -> None:
    """Test registering provider dependencies."""
    manager = DependencyManager()
    manager.register_provider("test_provider", ["package1", "package2"])
    assert manager._provider_deps["test_provider"] == ["package1", "package2"]


def test_dependency_manager_register_feature() -> None:
    """Test registering feature dependencies."""
    manager = DependencyManager()
    manager.register_feature("test_feature", ["package1", "package2"])
    assert manager._feature_deps["test_feature"] == ["package1", "package2"]


def test_dependency_manager_verify_provider() -> None:
    """Test verifying provider dependencies."""
    manager = DependencyManager()
    manager.register_provider("test_provider", ["pytest", "nonexistent_package"])

    # Test with missing dependencies
    missing = manager.verify_provider("test_provider")
    assert missing == ["nonexistent_package"]

    # Test with unsupported provider
    with pytest.raises(ValueError) as exc_info:
        manager.verify_provider("unsupported_provider")
    assert "Provider unsupported_provider is not supported" in str(exc_info.value)


def test_dependency_manager_verify_feature() -> None:
    """Test verifying feature dependencies."""
    manager = DependencyManager()
    manager.register_feature("test_feature", ["pytest", "nonexistent_package"])

    # Test with missing dependencies
    missing = manager.verify_feature("test_feature")
    assert missing == ["nonexistent_package"]

    # Test with unsupported feature
    with pytest.raises(ValueError) as exc_info:
        manager.verify_feature("unsupported_feature")
    assert "Feature unsupported_feature is not supported" in str(exc_info.value)


def test_dependency_manager_check_provider_availability() -> None:
    """Test checking provider availability."""
    manager = DependencyManager()
    manager.register_provider("test_provider", ["pytest"])
    manager.register_provider("missing_provider", ["nonexistent_package"])

    # Test with available provider
    assert manager.check_provider_availability("test_provider") is True

    # Test with unavailable provider
    assert manager.check_provider_availability("missing_provider") is False

    # Test with unsupported provider
    assert manager.check_provider_availability("unsupported_provider") is False


def test_dependency_manager_check_feature_availability() -> None:
    """Test checking feature availability."""
    manager = DependencyManager()
    manager.register_feature("test_feature", ["pytest"])
    manager.register_feature("missing_feature", ["nonexistent_package"])

    # Test with available feature
    assert manager.check_feature_availability("test_feature") is True

    # Test with unavailable feature
    assert manager.check_feature_availability("missing_feature") is False

    # Test with unsupported feature
    assert manager.check_feature_availability("unsupported_feature") is False


def test_dependency_manager_get_available_providers() -> None:
    """Test getting available providers."""
    manager = DependencyManager()
    manager.register_provider("test_provider", ["pytest"])
    manager.register_provider("missing_provider", ["nonexistent_package"])

    available = manager.get_available_providers()
    assert available == {"test_provider"}


def test_dependency_manager_get_available_features() -> None:
    """Test getting available features."""
    manager = DependencyManager()
    manager.register_feature("test_feature", ["pytest"])
    manager.register_feature("missing_feature", ["nonexistent_package"])

    available = manager.get_available_features()
    assert available == {"test_feature"}


def test_dependency_manager_clear() -> None:
    """Test clearing registered dependencies."""
    manager = DependencyManager()
    manager.register_provider("test_provider", ["package1"])
    manager.register_feature("test_feature", ["package2"])

    manager.clear()
    assert manager._provider_deps == {}
    assert manager._feature_deps == {}
