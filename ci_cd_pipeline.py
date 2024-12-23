"""CI/CD pipeline using Dagger."""

import sys

import anyio

from ci.main import test


async def main() -> None:
    """Run the pipeline."""
    command = sys.argv[1] if len(sys.argv) > 1 else "ci"

    if command == "ci":
        success = await test()
        if not success:
            sys.exit(1)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    anyio.run(main)
