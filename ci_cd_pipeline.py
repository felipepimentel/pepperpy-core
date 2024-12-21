"""CI/CD pipeline using Dagger."""

import argparse
import sys

import anyio
import dagger


async def setup_python(client: dagger.Client) -> dagger.Container:
    """Set up Python container with Poetry and dependencies."""
    return (
        client.container()
        .from_("python:3.12-slim")
        .with_exec(["pip", "install", "--no-cache-dir", "poetry"])
        .with_mounted_directory(
            "/src",
            client.host().directory(".", exclude=["dist/", ".venv/", "__pycache__/"]),
        )
        .with_workdir("/src")
        .with_exec(["poetry", "install", "--with", "dev"])
    )


async def run_tests(python: dagger.Container) -> bool:
    """Run tests with coverage."""
    test = await python.with_exec([
        "poetry",
        "run",
        "pytest",
        "--cov=pepperpy_core",
        "--cov-report=xml",
        "--cov-report=term",
    ]).exit_code()

    if test == 0:
        # Export coverage report
        await python.file("coverage.xml").export("coverage.xml")
        return True
    return False


async def run_lint(python: dagger.Container) -> bool:
    """Run Ruff linting and formatting."""
    lint = await python.with_exec(["poetry", "run", "ruff", "check", "."]).exit_code()
    if lint != 0:
        return False

    format_check = await python.with_exec([
        "poetry",
        "run",
        "ruff",
        "format",
        "--check",
        ".",
    ]).exit_code()
    return format_check == 0


async def run_type_check(python: dagger.Container) -> bool:
    """Run mypy type checking."""
    return (
        await python.with_exec([
            "poetry",
            "run",
            "mypy",
            "pepperpy_core",
            "--strict",
        ]).exit_code()
        == 0
    )


async def run_security_check(python: dagger.Container) -> bool:
    """Run Bandit security checks."""
    return (
        await python.with_exec([
            "poetry",
            "run",
            "bandit",
            "-r",
            "pepperpy_core",
        ]).exit_code()
        == 0
    )


async def build_package(python: dagger.Container) -> bool:
    """Build package with Poetry."""
    build = await python.with_exec(["poetry", "build"]).exit_code()

    if build == 0:
        # Export built package
        await python.directory("dist").export("dist")
        return True
    return False


async def run_ci(client: dagger.Client) -> bool:
    """Run CI pipeline."""
    python = await setup_python(client)

    steps = [
        ("Running tests", run_tests),
        ("Running linting", run_lint),
        ("Running type check", run_type_check),
        ("Running security check", run_security_check),
    ]

    for step_name, step in steps:
        print(f"\n=== {step_name} ===")
        if not await step(python):
            print(f"❌ {step_name} failed")
            return False
        print(f"✅ {step_name} passed")

    return True


async def run_cd(client: dagger.Client) -> bool:
    """Run CD pipeline."""
    python = await setup_python(client)

    steps = [
        ("Running tests", run_tests),
        ("Building package", build_package),
    ]

    for step_name, step in steps:
        print(f"\n=== {step_name} ===")
        if not await step(python):
            print(f"❌ {step_name} failed")
            return False
        print(f"✅ {step_name} passed")

    return True


async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["ci", "cd"])
    args = parser.parse_args()

    pipeline = {
        "ci": run_ci,
        "cd": run_cd,
    }

    connect = dagger.Connection(dagger.Config(log_output=sys.stderr))
    async with connect as client:
        success = await pipeline[args.command](client)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    anyio.run(main)
