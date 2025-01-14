"""Test package utilities."""

import importlib.metadata
from unittest.mock import patch

from pepperpy.package import get_package_name, get_package_version


def test_get_package_name() -> None:
    """Test get_package_name utility."""
    assert get_package_name() == "pepperpy"


def test_get_package_version_found() -> None:
    """Test get_package_version when package is found."""
    with patch("importlib.metadata.version", return_value="1.0.0"):
        assert get_package_version() == "1.0.0"


def test_get_package_version_not_found() -> None:
    """Test get_package_version when package is not found."""
    with patch(
        "importlib.metadata.version",
        side_effect=importlib.metadata.PackageNotFoundError("pepperpy"),
    ):
        assert get_package_version() == "0.0.0"
