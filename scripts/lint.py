"""Script to run linting checks."""

import subprocess
import sys


def main() -> int:
    """Run linting checks."""
    try:
        subprocess.run(["ruff", "check", "."], check=True)
        return 0
    except subprocess.CalledProcessError as e:
        return e.returncode


if __name__ == "__main__":
    sys.exit(main())
