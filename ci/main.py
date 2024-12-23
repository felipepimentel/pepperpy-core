"""Dagger pipeline for CI/CD."""

import sys

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

        # Print test output
        print(await test.stdout())

        try:
            # Execute the test container and get the exit code
            await test
            return True
        except dagger.ExecError as e:
            print(f"Tests failed with error: {e}")
            return False


async def main() -> None:
    """Run the pipeline."""
    command = sys.argv[1] if len(sys.argv) > 1 else "test"

    if command == "test":
        success = await test()
        if not success:
            sys.exit(1)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    anyio.run(main)
