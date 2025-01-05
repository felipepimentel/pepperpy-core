"""Test configuration."""

import asyncio
from typing import Any, AsyncGenerator, Generator

import pytest
import pytest_asyncio


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest."""
    config.addinivalue_line(
        "markers",
        "no_cover: mark test to be excluded from coverage",
    )


@pytest.fixture(scope="session")
def event_loop_policy() -> Generator[asyncio.AbstractEventLoopPolicy, None, None]:
    """Create an event loop policy for testing."""
    policy = asyncio.get_event_loop_policy()
    yield policy


@pytest_asyncio.fixture
async def test_module() -> AsyncGenerator[Any, None]:
    """Create a test module for testing."""
    from pepperpy_core.module import BaseModule, ModuleConfig

    class TestConfig(ModuleConfig):
        """Test configuration."""

        def __init__(self) -> None:
            """Initialize test configuration."""
            super().__init__(name="test-module")

    class TestModule(BaseModule[TestConfig]):
        """Test module implementation."""

        def __init__(self, config: TestConfig | None = None) -> None:
            """Initialize test module."""
            super().__init__(config or TestConfig())

        async def _setup(self) -> None:
            """Setup test module."""
            pass

        async def _teardown(self) -> None:
            """Teardown test module."""
            pass

    module = TestModule()
    await module.initialize()
    yield module
    await module.teardown()
