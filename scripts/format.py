"""Script to run code formatting."""

import subprocess
import sys


def main() -> int:
    """Run code formatting."""
    try:
        subprocess.run(["ruff", "format", "."], check=True)
        return 0
    except subprocess.CalledProcessError as e:
        return e.returncode


if __name__ == "__main__":
    sys.exit(main())
