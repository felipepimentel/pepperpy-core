"""CI/CD pipeline using Dagger."""

import argparse
import sys
from collections.abc import Awaitable, Callable

import dagger


async def setup_python(client: dagger.Client) -> dagger.Container:
    """Set up Python container with Poetry and dependencies."""
    return (
        client.container()
        .from_("python:3.12-slim")
        .with_exec(["pip", "install", "--no-cache-dir", "poetry"])
        .with_mounted_directory("/src", client.host().directory("."))
        .with_workdir("/src")
        .with_exec(["poetry", "install", "--with", "dev"])
    )


async def run_tests(python: dagger.Container) -> int:
    """Run tests with coverage."""
    test = python.with_exec([
        "poetry",
        "run",
        "pytest",
        "--cov=pepperpy_core",
        "--cov-report=xml",
        "--cov-report=term",
    ])

    # Export coverage report
    await test.file("coverage.xml").export("coverage.xml")
    return await test.exit_code()


async def run_lint(python: dagger.Container) -> int:
    """Run Ruff linting and formatting."""
    lint = python.with_exec(["poetry", "run", "ruff", "check", "."])
    format_check = python.with_exec(["poetry", "run", "ruff", "format", "--check", "."])

    if await lint.exit_code() != 0:
        return 1
    return await format_check.exit_code()


async def run_type_check(python: dagger.Container) -> int:
    """Run mypy type checking."""
    return await python.with_exec([
        "poetry",
        "run",
        "mypy",
        "pepperpy_core",
        "--strict",
    ]).exit_code()


async def run_security_check(python: dagger.Container) -> int:
    """Run Bandit security checks."""
    return await python.with_exec([
        "poetry",
        "run",
        "bandit",
        "-r",
        "pepperpy_core",
    ]).exit_code()


async def build_package(python: dagger.Container) -> int:
    """Build package with Poetry."""
    build = python.with_exec(["poetry", "build"])

    # Export built package
    await build.directory("dist").export("dist")
    return await build.exit_code()


async def run_ci(client: dagger.Client) -> int:
    """Run CI pipeline."""
    python = await setup_python(client)

    steps: list[Callable[[dagger.Container], Awaitable[int]]] = [
        run_tests,
        run_lint,
        run_type_check,
        run_security_check,
    ]

    for step in steps:
        if await step(python) != 0:
            return 1

    return 0


async def run_cd(client: dagger.Client) -> int:
    """Run CD pipeline."""
    python = await setup_python(client)

    # Run tests first
    if await run_tests(python) != 0:
        return 1

    # Build package
    if await build_package(python) != 0:
        return 1

    return 0


async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["ci", "cd"])
    args = parser.parse_args()

    pipeline: dict[str, Callable[[dagger.Client], Awaitable[int]]] = {
        "ci": run_ci,
        "cd": run_cd,
    }

    async with dagger.Connection() as client:
        exit_code = await pipeline[args.command](client)
        sys.exit(exit_code)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
