"""Test generators module."""

import pytest

from pepperpy.generators import (
    AsyncGenerator,
    Generator,
    validate_async_generator,
    validate_generator,
)


def test_generator_protocol() -> None:
    """Test generator protocol."""

    def gen():
        yield 1
        yield 2

    class GeneratorClass:
        def __iter__(self):
            return self

        def __next__(self):
            raise StopIteration

    # Test valid generators
    assert isinstance(gen(), Generator)
    assert isinstance(GeneratorClass(), Generator)

    # Test invalid generators
    assert not isinstance(42, Generator)
    assert not isinstance("test", Generator)


@pytest.mark.asyncio
async def test_async_generator_protocol() -> None:
    """Test async generator protocol."""

    async def gen():
        yield 1
        yield 2

    class AsyncGeneratorClass:
        def __aiter__(self):
            return self

        async def __anext__(self):
            raise StopAsyncIteration

    # Test valid async generators
    assert isinstance(gen(), AsyncGenerator)
    assert isinstance(AsyncGeneratorClass(), AsyncGenerator)

    # Test invalid async generators
    assert not isinstance(42, AsyncGenerator)
    assert not isinstance("test", AsyncGenerator)


def test_validate_generator() -> None:
    """Test validate generator."""

    def gen():
        yield 1
        yield 2

    class GeneratorClass:
        def __iter__(self):
            return self

        def __next__(self):
            raise StopIteration

    # Test valid generators
    g = gen()
    assert validate_generator(g) == g

    g = GeneratorClass()
    assert validate_generator(g) == g

    # Test invalid generators
    with pytest.raises(TypeError) as exc_info:
        validate_generator(42)
    assert "Expected generator" in str(exc_info.value)
    assert "int" in str(exc_info.value)

    with pytest.raises(TypeError) as exc_info:
        validate_generator("test")
    assert "Expected generator" in str(exc_info.value)
    assert "str" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_async_generator() -> None:
    """Test validate async generator."""

    async def gen():
        yield 1
        yield 2

    class AsyncGeneratorClass:
        def __aiter__(self):
            return self

        async def __anext__(self):
            raise StopAsyncIteration

    # Test valid async generators
    g = gen()
    assert validate_async_generator(g) == g

    g = AsyncGeneratorClass()
    assert validate_async_generator(g) == g

    # Test invalid async generators
    with pytest.raises(TypeError) as exc_info:
        validate_async_generator(42)
    assert "Expected async generator" in str(exc_info.value)
    assert "int" in str(exc_info.value)

    with pytest.raises(TypeError) as exc_info:
        validate_async_generator("test")
    assert "Expected async generator" in str(exc_info.value)
    assert "str" in str(exc_info.value)


def test_generator_iteration() -> None:
    """Test generator iteration."""

    def gen():
        yield 1
        yield 2
        yield 3

    # Test iteration
    g = gen()
    assert list(g) == [1, 2, 3]

    # Test manual iteration
    g = gen()
    assert next(g) == 1
    assert next(g) == 2
    assert next(g) == 3
    with pytest.raises(StopIteration):
        next(g)


@pytest.mark.asyncio
async def test_async_generator_iteration() -> None:
    """Test async generator iteration."""

    async def gen():
        yield 1
        yield 2
        yield 3

    # Test iteration
    g = gen()
    result = []
    async for value in g:
        result.append(value)
    assert result == [1, 2, 3]

    # Test manual iteration
    g = gen()
    assert await g.__anext__() == 1
    assert await g.__anext__() == 2
    assert await g.__anext__() == 3
    with pytest.raises(StopAsyncIteration):
        await g.__anext__()
