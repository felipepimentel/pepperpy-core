"""Test callables module."""

import asyncio
import inspect
from typing import Callable as Call

import pytest

from pepperpy.callables import (
    AsyncCallable,
    Callable,
    Coroutine,
    validate_async_callable,
    validate_callable,
    validate_coroutine,
)


def test_callable_protocol() -> None:
    """Test callable protocol."""

    def func() -> None:
        pass

    class CallableClass:
        def __call__(self) -> None:
            pass

    assert isinstance(func, Callable)
    assert isinstance(CallableClass(), Callable)
    assert not isinstance(42, Callable)


def test_async_callable_protocol() -> None:
    """Test async callable protocol."""

    async def func() -> None:
        pass

    class AsyncCallableClass:
        async def __call__(self) -> None:
            pass

    assert isinstance(func, AsyncCallable)
    assert isinstance(AsyncCallableClass(), AsyncCallable)
    assert not isinstance(42, AsyncCallable)


def test_coroutine_protocol() -> None:
    """Test coroutine protocol."""

    async def func() -> None:
        pass

    coro = func()
    assert isinstance(coro, Coroutine)
    assert not isinstance(42, Coroutine)
    coro.close()  # Clean up


def test_validate_callable() -> None:
    """Test validate callable."""

    def func() -> None:
        pass

    class CallableClass:
        def __call__(self) -> None:
            pass

    # Test valid callables
    assert validate_callable(func) == func
    callable_obj = CallableClass()
    assert validate_callable(callable_obj) == callable_obj

    # Test invalid callables
    with pytest.raises(TypeError) as exc_info:
        validate_callable(42)
    assert "Expected callable" in str(exc_info.value)
    assert "int" in str(exc_info.value)


def test_validate_async_callable() -> None:
    """Test validate async callable."""

    async def func() -> None:
        pass

    class AsyncCallableClass:
        async def __call__(self) -> None:
            pass

    class SyncCallableClass:
        def __call__(self) -> None:
            pass

    # Test valid async callables
    assert validate_async_callable(func) == func
    async_callable_obj = AsyncCallableClass()
    assert validate_async_callable(async_callable_obj) == async_callable_obj

    # Test invalid async callables
    with pytest.raises(TypeError) as exc_info:
        validate_async_callable(42)
    assert "Expected callable" in str(exc_info.value)
    assert "int" in str(exc_info.value)

    with pytest.raises(TypeError) as exc_info:
        validate_async_callable(lambda: None)
    assert "Expected async callable" in str(exc_info.value)

    with pytest.raises(TypeError) as exc_info:
        validate_async_callable(SyncCallableClass())
    assert "Expected async callable" in str(exc_info.value)


def test_validate_coroutine() -> None:
    """Test validate coroutine."""

    async def func() -> None:
        pass

    # Test valid coroutine
    coro = func()
    assert validate_coroutine(coro) == coro
    coro.close()  # Clean up

    # Test invalid coroutine
    with pytest.raises(TypeError) as exc_info:
        validate_coroutine(42)
    assert "Expected coroutine" in str(exc_info.value)
    assert "int" in str(exc_info.value)

    with pytest.raises(TypeError) as exc_info:
        validate_coroutine(lambda: None)
    assert "Expected coroutine" in str(exc_info.value)
    assert "function" in str(exc_info.value)


def test_callable_with_args() -> None:
    """Test callable with arguments."""

    def func(x: int, y: str = "test") -> str:
        return f"{x} {y}"

    class CallableClass:
        def __call__(self, x: int, y: str = "test") -> str:
            return f"{x} {y}"

    # Test function
    assert isinstance(func, Callable)
    result = func(42)
    assert result == "42 test"
    result = func(42, "hello")
    assert result == "42 hello"

    # Test callable object
    callable_obj = CallableClass()
    assert isinstance(callable_obj, Callable)
    result = callable_obj(42)
    assert result == "42 test"
    result = callable_obj(42, "hello")
    assert result == "42 hello"


@pytest.mark.asyncio
async def test_async_callable_with_args() -> None:
    """Test async callable with arguments."""

    async def func(x: int, y: str = "test") -> str:
        await asyncio.sleep(0)  # Simulate async work
        return f"{x} {y}"

    class AsyncCallableClass:
        async def __call__(self, x: int, y: str = "test") -> str:
            await asyncio.sleep(0)  # Simulate async work
            return f"{x} {y}"

    # Test async function
    assert isinstance(func, AsyncCallable)
    result = await func(42)
    assert result == "42 test"
    result = await func(42, "hello")
    assert result == "42 hello"

    # Test async callable object
    async_callable_obj = AsyncCallableClass()
    assert isinstance(async_callable_obj, AsyncCallable)
    result = await async_callable_obj(42)
    assert result == "42 test"
    result = await async_callable_obj(42, "hello")
    assert result == "42 hello"


def test_coroutine_operations() -> None:
    """Test coroutine operations."""

    async def func() -> str:
        await asyncio.sleep(0)  # Simulate async work
        return "result"

    # Test isinstance
    coro = func()
    assert isinstance(coro, Coroutine)
    coro.close()

    # Test async generator operations
    async def gen_func():
        value = yield "start"
        assert value == "test"
        try:
            yield "middle"
        except ValueError:
            yield "error"
        yield "end"

    # Run the coroutine in an event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # Test send
        coro = gen_func()
        assert loop.run_until_complete(coro.__anext__()) == "start"  # Start coroutine
        assert loop.run_until_complete(coro.asend("test")) == "middle"  # Send value

        # Test throw
        assert (
            loop.run_until_complete(coro.athrow(ValueError)) == "error"
        )  # Throw exception
        assert (
            loop.run_until_complete(coro.asend(None)) == "end"
        )  # Continue after error

        # Test close
        coro = gen_func()
        loop.run_until_complete(coro.aclose())
        with pytest.raises(StopAsyncIteration):
            loop.run_until_complete(coro.__anext__())  # Can't send to closed coroutine
    finally:
        loop.close()


def test_callable_inspection() -> None:
    """Test callable inspection."""

    def func(x: int, y: str = "test") -> str:
        """Test function."""
        return f"{x} {y}"

    # Test function attributes
    assert func.__name__ == "func"
    assert func.__doc__ == "Test function."
    sig = inspect.signature(func)
    assert str(sig) == "(x: int, y: str = 'test') -> str"

    # Test callable validation
    validated = validate_callable(func)
    assert validated.__name__ == func.__name__
    assert validated.__doc__ == func.__doc__
    assert inspect.signature(validated) == sig


@pytest.mark.asyncio
async def test_async_callable_inspection() -> None:
    """Test async callable inspection."""

    async def func(x: int, y: str = "test") -> str:
        """Test async function."""
        await asyncio.sleep(0)
        return f"{x} {y}"

    # Test function attributes
    assert func.__name__ == "func"
    assert func.__doc__ == "Test async function."
    sig = inspect.signature(func)
    assert str(sig) == "(x: int, y: str = 'test') -> str"

    # Test async callable validation
    validated = validate_async_callable(func)
    assert validated.__name__ == func.__name__
    assert validated.__doc__ == func.__doc__
    assert inspect.signature(validated) == sig


def test_callable_type_hints() -> None:
    """Test callable type hints."""

    T = Call[[int, str], str]

    def func(x: int, y: str) -> str:
        return f"{x} {y}"

    # Test callable with type hints
    assert isinstance(func, Callable)
    typed_func: T = func
    result = typed_func(42, "test")
    assert result == "42 test"

    # Test callable validation with type hints
    validated = validate_callable(typed_func)
    assert isinstance(validated, Callable)
    result = validated(42, "test")
    assert result == "42 test"
