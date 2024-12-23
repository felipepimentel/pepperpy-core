import os
import sys

import anyio
import dagger


async def build_and_test(client: dagger.Client) -> bool:
    """
    Build and test the package inside a container.

    Args:
        client (dagger.Client): The Dagger client instance.

    Returns:
        bool: True if tests pass, False otherwise.
    """
    python = (
        client.container()
        .from_("python:3.12-slim")
        .with_exec(["pip", "install", "poetry"])
        .with_mounted_directory("/app", client.host().directory("."))
        .with_workdir("/app")
        .with_exec(["poetry", "install"])
    )
    # Run tests
    result = await python.with_exec(["poetry", "run", "check"]).exit_code()
    if result != 0:
        print("Tests failed.")
    return result == 0


async def publish_package(client: dagger.Client) -> bool:
    """
    Publish package to PyPI
    """
    print("Starting publish process...")

    # Get PyPI token from environment
    pypi_token = os.getenv("PYPI_TOKEN")
    if not pypi_token:
        print("No PyPI token found")
        return False

    # Configure Poetry to use token authentication
    python = (
        client.container()
        .from_("python:3.12-slim")
        .with_exec(["pip", "install", "poetry"])
        .with_mounted_directory("/app", client.host().directory("."))
        .with_workdir("/app")
        .with_exec(["poetry", "install"])
        # Configurar o Poetry para usar autenticação com token
        .with_exec(["poetry", "config", "pypi-token.pypi", pypi_token])
        # Adicionando a flag --build ao comando publish
        .with_exec(["poetry", "publish", "--build", "--no-interaction"])
    )

    exit_code = await python.exit_code()

    if exit_code == 0:
        print("Package published successfully")
        return True
    else:
        print("Failed to publish package")
        return False


async def main() -> int:
    """
    Main function to orchestrate the pipeline.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    async with dagger.Connection() as client:
        # Run build and tests
        print("Starting build and test process...")
        if not await build_and_test(client):
            print("Build or tests failed. Exiting.")
            return 1

        # If tests pass, attempt to publish
        print("Build and tests passed. Starting publish process...")
        if not await publish_package(client):
            print("Publish process failed. Exiting.")
            return 1

    print("Pipeline completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(anyio.run(main))
