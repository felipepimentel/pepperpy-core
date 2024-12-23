"""Script to run type checking."""

import subprocess
import sys


def main() -> int:
    """Run type checking."""
    try:
        subprocess.run(["mypy", "poetflow", "tests"], check=True)
        return 0
    except subprocess.CalledProcessError as e:
        return e.returncode


if __name__ == "__main__":
    sys.exit(main())
