"""CI/CD pipeline using Dagger.

This module provides a complete CI/CD pipeline using Dagger, including:
- Running tests with coverage
- Publishing to PyPI
- GitHub Actions integration

Usage:
    python ci_cd_pipeline.py ci       # Run tests
    python ci_cd_pipeline.py publish  # Run tests and publish to PyPI

GitHub Actions will automatically:
- Run tests on push/PR to main
- Publish to PyPI on new releases
"""

import os
import sys
from typing import Optional

import anyio
import dagger


async def run_tests(python_versions: list[str]) -> bool:
    """Run tests in a container across multiple Python versions using Poetry and pytest.

    Args:
        python_versions: List of Python versions to test against.

    Returns:
        bool: True if all tests pass, False otherwise.
    """
    async with dagger.Connection() as client:
        for version in python_versions:
            print(f"Running tests on Python {version}...")
            python = (
                client.container()
                .from_(f"python:{version}-slim")
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
                "--cov-report=xml",
                "--cov-report=term",
                "-v",
            ])

            try:
                print(await test.stdout())
                await test
            except dagger.ExecError as e:
                print(f"Tests failed on Python {version}: {e}")
                return False
    return True


async def lint_code() -> bool:
    """Run linters to enforce code style and quality."""
    async with dagger.Connection() as client:
        python = (
            client.container()
            .from_("python:3.12-slim")
            .with_exec(["pip", "install", "ruff"])
            .with_mounted_directory("/app", client.host().directory("."))
            .with_workdir("/app")
            .with_exec(["ruff", "."])
        )

        try:
            print("Running linter...")
            print(await python.stdout())
            await python
            return True
        except dagger.ExecError as e:
            print(f"Linter failed: {e}")
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
            print(await build.stdout())

            publish = build.with_exec(["poetry", "publish", "--no-interaction"])
            print(await publish.stdout())

            return True
        except dagger.ExecError as e:
            print(f"Publish failed: {e}")
            return False


async def main() -> None:
    """Run the CI/CD pipeline based on the provided command."""
    command = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CI_COMMAND", "ci")

    if command == "ci":
        print("Running lint...")
        if not await lint_code():
            sys.exit(1)
        print("Lint passed successfully!")

        print("Running tests...")
        python_versions = ["3.12", "3.11"]
        if not await run_tests(python_versions):
            sys.exit(1)
        print("Tests passed successfully!")

    elif command == "publish":
        print("Running lint and tests before publishing...")
        python_versions = ["3.12", "3.11"]
        if not await lint_code() or not await run_tests(python_versions):
            print("Lint or tests failed, aborting publish.")
            sys.exit(1)

        pypi_token = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("PYPI_TOKEN")
        if not await publish_package(pypi_token):
            sys.exit(1)
        print("Package published successfully!")

    else:
        print(f"Error: Unknown command '{command}'.")
        print("Available commands: ci, publish")
        sys.exit(1)


if __name__ == "__main__":
    anyio.run(main)
