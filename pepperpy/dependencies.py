"""Dependency management utilities for PepperPy.

This module provides utilities for managing Python package dependencies, including:
- Checking if dependencies are installed
- Verifying required dependencies
- Managing provider-specific dependencies
- Managing feature-specific dependencies
- Generating installation commands
"""

import logging
from importlib import util
from typing import Optional

from .core import PepperpyError

logger = logging.getLogger(__name__)


class DependencyError(PepperpyError):
    """Error raised when there are dependency-related issues.

    Args:
        message: Error message
        cause: Optional cause of the error
        package: Optional name of the package that caused the error
    """

    def __init__(
        self,
        message: str,
        cause: Optional[Exception] = None,
        package: Optional[str] = None,
    ) -> None:
        super().__init__(message, cause)
        self.package = package


def check_dependency(package: str) -> bool:
    """Check if a Python package is installed.

    Args:
        package: Package name to check

    Returns:
        True if package is installed, False otherwise
    """
    return bool(util.find_spec(package))


def get_missing_dependencies(packages: list[str]) -> list[str]:
    """Get list of missing dependencies.

    Args:
        packages: List of package names to check

    Returns:
        List of missing package names
    """
    return [pkg for pkg in packages if not check_dependency(pkg)]


def verify_dependencies(packages: list[str]) -> None:
    """Verify that all required dependencies are installed.

    Args:
        packages: List of package names to verify

    Raises:
        DependencyError: If any dependencies are missing
    """
    missing = get_missing_dependencies(packages)
    if missing:
        # Raise error for first missing package
        raise DependencyError(
            f"Missing required dependencies: {', '.join(missing)}", package=missing[0]
        )


def get_installation_command(missing_deps: list[str], use_poetry: bool = True) -> str:
    """Get command to install missing dependencies.

    Args:
        missing_deps: List of missing package names
        use_poetry: Whether to use Poetry for installation

    Returns:
        Installation command string
    """
    deps_str = " ".join(missing_deps)
    return f"poetry add {deps_str}" if use_poetry else f"pip install {deps_str}"


class DependencyManager:
    """Manager for handling package dependencies.

    This class provides functionality for managing dependencies, including:
    - Registering provider and feature dependencies
    - Verifying dependencies are installed
    - Checking availability of providers and features
    - Getting installation commands
    """

    def __init__(self) -> None:
        self._provider_deps: dict[str, list[str]] = {}
        self._feature_deps: dict[str, list[str]] = {}

    def register_provider(self, provider: str, dependencies: list[str]) -> None:
        """Register dependencies for a provider.

        Args:
            provider: Provider name
            dependencies: List of package dependencies
        """
        self._provider_deps[provider] = dependencies

    def register_feature(self, feature: str, dependencies: list[str]) -> None:
        """Register dependencies for a feature.

        Args:
            feature: Feature name
            dependencies: List of package dependencies
        """
        self._feature_deps[feature] = dependencies

    def verify_provider(self, provider: str) -> list[str] | None:
        """Verify dependencies for a specific provider.

        Args:
            provider: Provider name

        Returns:
            List of missing dependencies if any, None if all dependencies are met

        Raises:
            ValueError: If provider is not supported
        """
        if provider not in self._provider_deps:
            raise ValueError(f"Provider {provider} is not supported")

        missing = get_missing_dependencies(self._provider_deps[provider])
        return missing if missing else None

    def verify_feature(self, feature: str) -> list[str] | None:
        """Verify dependencies for a specific feature.

        Args:
            feature: Feature name

        Returns:
            List of missing dependencies if any, None if all dependencies are met

        Raises:
            ValueError: If feature is not supported
        """
        if feature not in self._feature_deps:
            raise ValueError(f"Feature {feature} is not supported")

        missing = get_missing_dependencies(self._feature_deps[feature])
        return missing if missing else None

    def check_provider_availability(self, provider: str) -> bool:
        """Check if a provider is available for use.

        Args:
            provider: Provider name

        Returns:
            True if provider is available, False otherwise
        """
        try:
            missing = self.verify_provider(provider)
            return missing is None
        except ValueError:
            logger.warning(f"Provider {provider} is not supported")
            return False

    def check_feature_availability(self, feature: str) -> bool:
        """Check if a feature is available for use.

        Args:
            feature: Feature name

        Returns:
            True if feature is available, False otherwise
        """
        try:
            missing = self.verify_feature(feature)
            return missing is None
        except ValueError:
            logger.warning(f"Feature {feature} is not supported")
            return False

    def get_available_providers(self) -> set[str]:
        """Get set of available providers.

        Returns:
            Set of provider names that are available for use
        """
        return {
            provider
            for provider in self._provider_deps
            if self.check_provider_availability(provider)
        }

    def get_available_features(self) -> set[str]:
        """Get set of available features.

        Returns:
            Set of feature names that are available for use
        """
        return {
            feature
            for feature in self._feature_deps
            if self.check_feature_availability(feature)
        }

    def clear(self) -> None:
        """Clear all registered dependencies."""
        self._provider_deps.clear()
        self._feature_deps.clear()
