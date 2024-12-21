import argparse
import os
import sys

import dagger


async def setup_environment(client: dagger.Client) -> dagger.Container:
    """
    Set up the base Python environment with Poetry and install dependencies.

    Args:
        client (dagger.Client): Dagger client instance.

    Returns:
        dagger.Container: Configured Python container.
    """
    python = client.container().from_("python:3.12-slim")
    python = python.with_exec(["pip", "install", "poetry"])
    source = client.host().directory(".")
    # Instalar dependências incluindo o grupo "dev"
    return (
        python.with_mounted_directory("/src", source)
        .with_workdir("/src")
        .with_exec(["poetry", "install", "--with", "dev"])
    )


async def run_tests(client: dagger.Client) -> int:
    """
    Run tests using pytest.

    Args:
        client (dagger.Client): Dagger client instance.

    Returns:
        int: Exit code of the tests.
    """
    python = await setup_environment(client)
    test = python.with_exec([
        "poetry",
        "run",
        "pytest",
        "--maxfail=1",
        "--disable-warnings",
    ])
    return await test.exit_code()


async def run_lint(client: dagger.Client) -> int:
    """
    Run linting using Ruff.

    Args:
        client (dagger.Client): Dagger client instance.

    Returns:
        int: Exit code of the linting process.
    """
    python = await setup_environment(client)
    lint = python.with_exec(["poetry", "run", "ruff", ".", "--fix"])
    return await lint.exit_code()


async def run_security(client: dagger.Client) -> int:
    """
    Run security analysis using Bandit.

    Args:
        client (dagger.Client): Dagger client instance.

    Returns:
        int: Exit code of the security scan.
    """
    python = await setup_environment(client)
    security = python.with_exec(["poetry", "run", "bandit", "-r", "."])
    return await security.exit_code()


async def build_package(client: dagger.Client) -> int:
    """
    Build the Python package.

    Args:
        client (dagger.Client): Dagger client instance.

    Returns:
        int: Exit code of the build process.
    """
    python = await setup_environment(client)
    build = python.with_exec(["poetry", "build"])
    return await build.exit_code()


async def publish_package(client: dagger.Client) -> int:
    """
    Publish the package to PyPI.

    Args:
        client (dagger.Client): Dagger client instance.

    Returns:
        int: Exit code of the publishing process.
    """
    python = await setup_environment(client)
    username = os.getenv("PYPI_USERNAME")
    password = os.getenv("PYPI_PASSWORD")

    if not username or not password:
        print("Error: Missing PyPI credentials in environment variables.")
        return 1

    publish = (
        python.with_env_variable("TWINE_USERNAME", username)
        .with_env_variable("TWINE_PASSWORD", password)
        .with_exec(["poetry", "publish", "--build"])
    )
    return await publish.exit_code()


async def main():
    """
    Entry point for the Dagger CI/CD pipeline. Executes the phase based on the CLI argument.
    """
    parser = argparse.ArgumentParser(description="Run CI/CD pipeline with Dagger.")
    parser.add_argument(
        "phase",
        choices=["test", "lint", "security", "build", "publish"],
        help="Phase of the pipeline to execute",
    )
    args = parser.parse_args()

    async with dagger.Connection() as client:
        phase_map = {
            "test": run_tests,
            "lint": run_lint,
            "security": run_security,
            "build": build_package,
            "publish": publish_package,
        }

        # Execute the specified phase
        exit_code = await phase_map[args.phase](client)
        sys.exit(exit_code)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
