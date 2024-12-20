"""Testing utilities for async code.

This module provides utilities for testing asynchronous code, including:
- Decorator for running async test functions
- Base class for async test cases
- Standalone function for running coroutines
"""

import asyncio
import functools
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

T = TypeVar("T", bound=Callable[..., Awaitable[Any]])


def async_test(func: T) -> Callable[..., Any]:
    """Decorator for running async test functions in a new event loop.
    
    Args:
        func: The async test function to decorate.
        
    Returns:
        A wrapped function that runs the async test in a new event loop.
        
    Example:
        @async_test
        async def test_something():
            result = await some_async_function()
            assert result == expected
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Run async function in event loop"""
        return asyncio.run(func(*args, **kwargs))

    return wrapper  # type: ignore


class AsyncTestCase:
    """Base class for async test cases.
    
    Provides setup and teardown of an event loop for the test case,
    and a helper method for running coroutines in tests.
    
    Example:
        class TestSomething(AsyncTestCase):
            async def test_feature(self):
                result = await self.run_async(some_async_function())
                self.assertEqual(result, expected)
    """

    loop: asyncio.AbstractEventLoop

    @classmethod
    def setUpClass(cls) -> None:
        """Set up test class by creating a new event loop."""
        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)

    @classmethod
    def tearDownClass(cls) -> None:
        """Tear down test class by closing the event loop."""
        cls.loop.close()
        asyncio.set_event_loop(None)

    def run_async(self, coro: Awaitable[T]) -> T:
        """Run a coroutine in the test loop.
        
        Args:
            coro: The coroutine to run.
            
        Returns:
            The result of the coroutine.
        """
        return self.loop.run_until_complete(coro)


def run_async(coro: Awaitable[T]) -> T:
    """Run a coroutine in a new event loop.
    
    This is a standalone function for running coroutines outside of a test case.
    It creates a new event loop, runs the coroutine, and cleans up the loop.
    
    Args:
        coro: The coroutine to run.
        
    Returns:
        The result of the coroutine.
        
    Example:
        result = run_async(some_async_function())
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
        asyncio.set_event_loop(None)
