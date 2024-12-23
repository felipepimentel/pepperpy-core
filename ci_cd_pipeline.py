"""Simplified CI/CD pipeline using Dagger.

This module provides a minimal CI/CD pipeline using Dagger, focusing on:
- Running tests locally with Dagger
- Publishing to PyPI

Usage:
    python ci_cd_pipeline.py ci       # Run tests
    python ci_cd_pipeline.py publish  # Publish to PyPI
"""

import os
import sys
from typing import Optional

import anyio
import dagger


async def run_tests() -> bool:
    """Run tests in a container using Poetry and pytest."""
    async with dagger.Connection() as client:
        python = (
            client.container()
            .from_("python:3.12-slim")
            .with_exec(["pip", "install", "poetry"])
            .with_mounted_directory("/app", client.host().directory("."))
            .with_workdir("/app")
            .with_exec(["poetry", "install"])
        )

        test = python.with_exec([
            "poetry",
            "run",
            "pytest",
            "--cov=pepperpy_core",
            "--cov-report=term",
            "-v",
        ])

        try:
            print("Running tests...")
            print(await test.stdout())
            await test
            print("Tests passed successfully!")
            return True
        except dagger.ExecError as e:
            print(f"Tests failed: {e}")
            return False


async def publish_package(pypi_token: Optional[str] = None) -> bool:
    """Publish the package to PyPI.

    Args:
        pypi_token: PyPI API token. If not provided, retrieved from environment.

    Returns:
        bool: True if publishing succeeded, False otherwise.
    """
    pypi_token = pypi_token or os.environ.get("PYPI_TOKEN")
    if not pypi_token:
        print("Error: PyPI token is not provided.")
        return False

    async with dagger.Connection() as client:
        python = (
            client.container()
            .from_("python:3.12-slim")
            .with_exec(["pip", "install", "poetry"])
            .with_mounted_directory("/app", client.host().directory("."))
            .with_workdir("/app")
            .with_exec(["poetry", "install"])
        )

        python = python.with_secret_variable(
            "POETRY_PYPI_TOKEN_PYPI", client.set_secret("pypi_token", pypi_token)
        )

        try:
            build = python.with_exec(["poetry", "build"])
            print("Building package...")
            print(await build.stdout())

            publish = build.with_exec(["poetry", "publish", "--no-interaction"])
            print("Publishing package to PyPI...")
            print(await publish.stdout())

            print("Package published successfully!")
            return True
        except dagger.ExecError as e:
            print(f"Publish failed: {e}")
            return False


async def main() -> None:
    """Run the CI/CD pipeline based on the provided command."""
    command = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CI_COMMAND", "ci")

    if command == "ci":
        print("Running tests...")
        if not await run_tests():
            sys.exit(1)

    elif command == "publish":
        print("Publishing package...")
        pypi_token = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("PYPI_TOKEN")
        if not await publish_package(pypi_token):
            sys.exit(1)

    else:
        print(f"Error: Unknown command '{command}'.")
        print("Available commands: ci, publish")
        sys.exit(1)


if __name__ == "__main__":
    anyio.run(main)
