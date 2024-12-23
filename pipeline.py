"""CI/CD pipeline using Dagger.

This module provides a complete CI/CD pipeline using Dagger, including:
- Running tests with coverage
- Publishing to PyPI
- GitHub Actions integration

Usage:
    python pipeline.py ci     # Run tests
    python pipeline.py publish # Run tests and publish to PyPI

GitHub Actions will automatically:
- Run tests on push/PR to main
- Publish to PyPI on new releases
"""

import os
import sys
from typing import Optional, Tuple

import anyio
import dagger


async def test(ignore_warnings: bool = True) -> Tuple[bool, str]:
    """Run tests in a container.

    Args:
        ignore_warnings: Whether to ignore pytest warnings

    Returns:
        Tuple of (success, output)
    """
    async with dagger.Connection() as client:
        # Get Python image
        python = (
            client.container()
            .from_("python:3.12-slim")
            .with_exec(["pip", "install", "poetry"])
            .with_mounted_directory("/app", client.host().directory("."))
            .with_workdir("/app")
            .with_exec(["poetry", "install"])
        )

        # Build pytest command
        pytest_cmd = [
            "poetry",
            "run",
            "pytest",
            "--cov=pepperpy_core",
            "--cov-report=xml",
            "--cov-report=term",
            "-v",
        ]

        # Add warning flags if needed
        if ignore_warnings:
            pytest_cmd.extend(["-W", "ignore"])

        # Run tests
        test = python.with_exec(pytest_cmd)

        try:
            # Get test output
            output = await test.stdout()
            print(output)
            await test
            return True, output
        except dagger.ExecError as e:
            error_msg = f"Tests failed with error: {e}"
            print(error_msg)
            return False, error_msg


async def publish(pypi_token: Optional[str] = None) -> Tuple[bool, str]:
    """Publish package to PyPI.

    Args:
        pypi_token: PyPI API token. If not provided, will try to get from environment.

    Returns:
        Tuple of (success, output)
    """
    # Try to get token from environment if not provided
    if not pypi_token:
        pypi_token = os.environ.get("PYPI_TOKEN")
        if not pypi_token:
            msg = "No PyPI token provided and PYPI_TOKEN environment variable not set"
            print(msg)
            return False, msg

    print("Starting publish process...")
    print(f"PyPI token present: {bool(pypi_token)}")

    async with dagger.Connection() as client:
        print("Connected to Dagger")

        # Get Python image
        python = (
            client.container()
            .from_("python:3.12-slim")
            .with_exec(["pip", "install", "poetry"])
            .with_mounted_directory("/app", client.host().directory("."))
            .with_workdir("/app")
            .with_exec(["poetry", "install"])
        )
        print("Container configured with Poetry")

        # Configure poetry with PyPI token as a secret
        secret = client.set_secret("pypi_token", pypi_token)
        python = python.with_secret_variable("POETRY_PYPI_TOKEN_PYPI", secret)
        print("PyPI token configured in container")

        try:
            # Build package
            build = python.with_exec(["poetry", "build"])
            build_output = await build.stdout()
            print("Building package...")
            print(build_output)

            # Show contents of dist directory
            ls_dist = build.with_exec(["ls", "-la", "dist"])
            ls_output = await ls_dist.stdout()
            print("Contents of dist directory:")
            print(ls_output)

            # Publish to PyPI
            publish = build.with_exec(["poetry", "publish", "--no-interaction"])
            publish_output = await publish.stdout()
            print("Publishing to PyPI...")
            print(publish_output)

            return True, "Package published successfully"
        except dagger.ExecError as e:
            error_msg = f"Publish failed with error: {e}"
            print(error_msg)
            if hasattr(e, "stdout"):
                print("Stdout:", e.stdout)
            if hasattr(e, "stderr"):
                print("Stderr:", e.stderr)
            return False, error_msg


async def main() -> None:
    """Run the pipeline."""
    # Get command from arguments or environment
    command = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CI_COMMAND", "ci")

    if command == "ci":
        # Run tests
        print("Running tests...")
        success, output = await test(ignore_warnings=True)
        if not success:
            sys.exit(1)
        print("Tests completed successfully!")

    elif command == "publish":
        # First run tests
        print("Running tests before publish...")
        success, output = await test(ignore_warnings=True)
        if not success:
            print("Tests failed, aborting publish")
            sys.exit(1)
        print("Tests passed, proceeding with publish...")

        # Get PyPI token from environment or command line
        pypi_token = os.environ.get("PYPI_TOKEN")
        if len(sys.argv) > 2:
            pypi_token = sys.argv[2]

        # Publish to PyPI
        success, output = await publish(pypi_token)
        if not success:
            sys.exit(1)
        print("Package published successfully!")

    else:
        print(f"Unknown command: {command}")
        print("Available commands: ci, publish")
        sys.exit(1)


if __name__ == "__main__":
    # Run the pipeline
    anyio.run(main)
