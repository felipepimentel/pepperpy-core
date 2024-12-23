"""Script to run all code quality checks."""

import subprocess
import sys
from typing import List, Tuple


def run_command(command: List[str], description: str) -> Tuple[int, str, str]:
    """Run a command and return its exit code and output."""
    print(f"\n🔄 {description}")
    try:
        process = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        return 0, process.stdout, process.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr


def main() -> int:
    """Run all checks."""
    checks = [
        (
            ["poetry", "run", "mypy", "poetflow", "tests"],
            "Running type checking with mypy...",
        ),
        (
            ["poetry", "run", "ruff", "check", "."],
            "Running linting with ruff...",
        ),
        (
            ["poetry", "run", "ruff", "format", "."],
            "Running code formatting with ruff format...",
        ),
        (
            ["poetry", "run", "pytest", "--cov=poetflow", "--cov-report=term-missing"],
            "Running tests with pytest...",
        ),
    ]

    failed = False
    for command, description in checks:
        exit_code, stdout, stderr = run_command(command, description)

        if stdout:
            print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)

        if exit_code != 0:
            failed = True
            print(f"❌ {description} failed!")
            break

    if not failed:
        print("\n✅ All checks passed!")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
