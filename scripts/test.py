"""Script to run tests."""

import subprocess
import sys


def main() -> int:
    """Run tests."""
    try:
        subprocess.run(
            ["pytest", "--cov=poetflow", "--cov-report=term-missing"],
            check=True,
        )
        return 0
    except subprocess.CalledProcessError as e:
        return e.returncode


if __name__ == "__main__":
    sys.exit(main())
