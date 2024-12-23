"""CI/CD pipeline using Dagger.

This module provides a complete CI/CD pipeline using Dagger, including:
- Running tests with coverage
- Publishing to PyPI
- GitHub Actions integration

Usage:
    python ci_cd_pipeline.py ci     # Run tests
    python ci_cd_pipeline.py publish # Run tests and publish to PyPI

GitHub Actions will automatically:
- Run tests on push/PR to main
- Publish to PyPI on new releases
"""

import os
import sys
from typing import Optional

import anyio
import dagger


async def test() -> bool:
    """Run tests in a container."""
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

        # Run tests
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
            # Print test output
            print(await test.stdout())
            await test
            return True
        except dagger.ExecError as e:
            print(f"Tests failed with error: {e}")
            return False


async def publish(pypi_token: Optional[str] = None) -> bool:
    """Publish package to PyPI.

    Args:
        pypi_token: PyPI API token. If not provided, will try to get from environment.

    Returns:
        True if publish succeeded, False otherwise.
    """
    # Try to get token from environment if not provided
    if not pypi_token:
        pypi_token = os.environ.get("PYPI_TOKEN")
        if not pypi_token:
            print("No PyPI token provided and PYPI_TOKEN environment variable not set")
            return False

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
            print("Building package...")
            print(await build.stdout())

            # Show contents of dist directory
            ls_dist = build.with_exec(["ls", "-la", "dist"])
            print("Contents of dist directory:")
            print(await ls_dist.stdout())

            # Publish to PyPI
            publish = build.with_exec(["poetry", "publish", "--no-interaction"])
            print("Publishing to PyPI...")
            print(await publish.stdout())

            return True
        except dagger.ExecError as e:
            print(f"Publish failed with error: {e}")
            if hasattr(e, "stdout"):
                print("Stdout:", e.stdout)
            if hasattr(e, "stderr"):
                print("Stderr:", e.stderr)
            return False


async def main() -> None:
    """Run the pipeline."""
    # Get command from arguments or environment
    command = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CI_COMMAND", "ci")

    if command == "ci":
        # Run tests
        print("Running tests...")
        success = await test()
        if not success:
            sys.exit(1)
        print("Tests completed successfully!")

    elif command == "publish":
        # First run tests
        print("Running tests before publish...")
        success = await test()
        if not success:
            print("Tests failed, aborting publish")
            sys.exit(1)
        print("Tests passed, proceeding with publish...")

        # Get PyPI token from environment or command line
        pypi_token = os.environ.get("PYPI_TOKEN")
        if len(sys.argv) > 2:
            pypi_token = sys.argv[2]

        # Publish to PyPI
        success = await publish(pypi_token)
        if not success:
            sys.exit(1)
        print("Package published successfully!")

    else:
        print(f"Unknown command: {command}")
        print("Available commands: ci, publish")
        sys.exit(1)


# GitHub Actions configuration
GITHUB_WORKFLOW = """name: CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  release:
    types: [created]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry anyio dagger-io
          
      - name: Run CI
        run: python ci_cd_pipeline.py ci

  publish:
    needs: ci
    runs-on: ubuntu-latest
    if: github.event_name == 'release' && github.event.action == 'created'
    permissions:
      id-token: write
      contents: read
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry anyio dagger-io
          
      - name: Verify Poetry config
        run: |
          poetry --version
          poetry config --list
          
      - name: Publish to PyPI
        env:
          PYPI_TOKEN: ${{ secrets.PYPI_TOKEN }}
        run: |
          echo "Starting publish process..."
          python ci_cd_pipeline.py publish
"""


def setup_github_actions() -> None:
    """Set up GitHub Actions workflow file."""
    os.makedirs(".github/workflows", exist_ok=True)
    workflow_path = ".github/workflows/ci.yml"

    # Only write if file doesn't exist or is different
    if not os.path.exists(workflow_path):
        with open(workflow_path, "w") as f:
            f.write(GITHUB_WORKFLOW)
        print(f"Created GitHub Actions workflow at {workflow_path}")
    else:
        with open(workflow_path, "r") as f:
            current = f.read()
        if current != GITHUB_WORKFLOW:
            with open(workflow_path, "w") as f:
                f.write(GITHUB_WORKFLOW)
            print(f"Updated GitHub Actions workflow at {workflow_path}")


if __name__ == "__main__":
    # Set up GitHub Actions if running locally
    if not os.environ.get("GITHUB_ACTIONS"):
        setup_github_actions()

    # Run the pipeline
    anyio.run(main)
