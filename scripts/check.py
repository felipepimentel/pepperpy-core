#!/usr/bin/env python3
"""Code quality check script."""

import subprocess
import sys
from typing import List, Tuple


def run_command(command: List[str]) -> Tuple[int, str, str]:
    """Run a command and return its exit code and output."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr


def main() -> int:
    """Run code quality checks."""
    print("Running code quality checks...")
    print("\n1. Code formatting (ruff format)")
    exit_code, stdout, stderr = run_command(["ruff", "format", "."])
    if exit_code != 0:
        print("Code formatting failed:")
        print(stderr or stdout)
        return exit_code
    print(stdout or "No formatting issues found.")

    print("\n2. Linting (ruff check)")
    exit_code, stdout, stderr = run_command(["ruff", "check", "."])
    if exit_code != 0:
        print("Linting failed:")
        print(stderr or stdout)
        return exit_code
    print(stdout or "No linting issues found.")

    print("\n3. Type checking (mypy)")
    exit_code, stdout, stderr = run_command(["mypy", ".", "--exclude", "scripts/"])
    if exit_code != 0:
        print("Type checking failed:")
        print(stderr or stdout)
        return exit_code
    print(stdout or "No type checking issues found.")

    print("\nAll checks passed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
