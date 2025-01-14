"""Script to run all code quality checks."""

import subprocess
import sys
from typing import List, Tuple


def run_command(command: List[str], description: str) -> Tuple[int, str, str]:
    """Run a command and return its exit code, stdout, and stderr.

    Args:
        command: The command to run as a list of strings.
        description: A description of the command being executed.

    Returns:
        A tuple containing the exit code, stdout, and stderr of the command.
    """
    print(f"\n🔄 {description}")
    try:
        process = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        return 0, process.stdout, process.stderr
    except subprocess.CalledProcessError as exc:
        return exc.returncode, exc.stdout, exc.stderr


def main() -> int:
    """Run all checks and report the results.

    Returns:
        Exit code: 0 if all checks pass, 1 otherwise.
    """
    checks = [
        (
            ["poetry", "run", "ruff", "format", "."],
            "Running code formatting with ruff format...",
        ),
        (
            ["poetry", "run", "ruff", "check", "."],
            "Running linting with ruff...",
        ),
        (
            ["poetry", "run", "mypy", "pepperpy", "tests"],
            "Running type checking with mypy...",
        ),
        (
            [
                "poetry",
                "run",
                "pytest",
                "--cov=pepperpy",
                "--cov-report=term-missing",
            ],
            "Running tests with pytest...",
        ),
    ]

    for command, description in checks:
        exit_code, stdout, stderr = run_command(command, description)

        if stdout:
            print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)

        if exit_code != 0:
            print(f"❌ {description} failed!")
            return 1

    print("\n✅ All checks passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
