"""Test package metadata."""

import importlib.metadata
from pathlib import Path

import pepperpy


def test_package_name() -> None:
    """Test get_package_name returns the correct package name."""
    assert pepperpy.__name__ == "pepperpy"


def test_package_version() -> None:
    """Test get_package_version returns the correct version."""
    try:
        expected = importlib.metadata.version("pepperpy")
    except importlib.metadata.PackageNotFoundError:
        version_file = Path(__file__).parent.parent.parent / "pepperpy" / "VERSION"
        if version_file.exists():
            expected = version_file.read_text().strip()
        else:
            expected = "0.0.0-dev"

    assert pepperpy.__version__ == expected


def test_version() -> None:
    """Test package version."""
    assert isinstance(pepperpy.__version__, str)
    assert pepperpy.__version__ == "0.0.0-dev"
