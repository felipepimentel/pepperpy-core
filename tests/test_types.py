"""Test types module."""

import asyncio
from typing import AsyncGenerator as AsyncGen
from typing import Generator as Gen
from typing import Protocol, runtime_checkable

import pytest

from pepperpy_core.types import (
    AsyncCallable,
    AsyncGenerator,
    BaseConfig,
    Callable,
    Coroutine,
    Generator,
    validate_async_callable,
    validate_async_generator,
    validate_callable,
    validate_coroutine,
    validate_generator,
    validate_protocol,
    validate_type,
)


@runtime_checkable
class TestProtocol(Protocol):
    """Test protocol."""

    def test(self) -> str:
        """Test method.

        Returns:
            Test string
        """
        ...


class ValidImplementation:
    """Valid implementation."""

    def test(self) -> str:
        """Test method.

        Returns:
            Test string
        """
        return "test"


class InvalidImplementation:
    """Invalid implementation."""

    def invalid(self) -> None:
        """Invalid method."""
        pass


def test_validate_protocol_valid() -> None:
    """Test validate protocol valid."""
    implementation = ValidImplementation()
    validated = validate_protocol(implementation, ValidImplementation)
    assert isinstance(validated, ValidImplementation)
    assert validated.test() == "test"


def test_validate_protocol_invalid() -> None:
    """Test validate protocol invalid."""
    implementation = InvalidImplementation()
    with pytest.raises(TypeError):
        validate_protocol(implementation, ValidImplementation)


def test_validate_type_valid() -> None:
    """Test validate type valid."""
    value = "test"
    validated = validate_type(value, str)
    assert isinstance(validated, str)
    assert validated == "test"


def test_validate_type_invalid() -> None:
    """Test validate type invalid."""
    value = 123
    with pytest.raises(TypeError):
        validate_type(value, str)


def test_validate_callable_valid() -> None:
    """Test validate callable valid."""

    def test_func(x: int) -> str:
        return str(x)

    validated = validate_callable(test_func)
    assert callable(validated)
    assert validated(123) == "123"


def test_validate_callable_invalid() -> None:
    """Test validate callable invalid."""
    value = "not_callable"
    with pytest.raises(TypeError):
        validate_callable(value)


@pytest.mark.asyncio
async def test_validate_async_callable_valid() -> None:
    """Test validate async callable valid."""

    async def test_func(x: int) -> str:
        await asyncio.sleep(0.1)
        return str(x)

    validated = validate_async_callable(test_func)
    assert asyncio.iscoroutinefunction(validated)
    result = await validated(123)
    assert result == "123"


@pytest.mark.asyncio
async def test_validate_async_callable_invalid() -> None:
    """Test validate async callable invalid."""

    def test_func(x: int) -> str:
        return str(x)

    with pytest.raises(TypeError):
        validate_async_callable(test_func)


@pytest.mark.asyncio
async def test_validate_coroutine_valid() -> None:
    """Test validate coroutine valid."""

    async def test_coro() -> str:
        await asyncio.sleep(0.1)
        return "test"

    coro = test_coro()
    validated = validate_coroutine(coro)
    assert asyncio.iscoroutine(validated)
    result = await validated
    assert result == "test"


@pytest.mark.asyncio
async def test_validate_coroutine_invalid() -> None:
    """Test validate coroutine invalid."""

    def test_func() -> str:
        return "test"

    with pytest.raises(TypeError):
        await validate_coroutine(test_func())


def test_base_config() -> None:
    """Test base config."""
    config = BaseConfig("test", metadata={"key": "value"})
    assert config.name == "test"
    assert config.metadata == {"key": "value"}


@pytest.fixture
def test_generator_values() -> list[int]:
    """Test generator values fixture."""
    return [1, 2, 3]


class TestGenerator:
    """Test generator implementation."""

    def __init__(self, values: list[int]) -> None:
        """Initialize test generator.

        Args:
            values: Values to generate
        """
        self.values = values
        self.index = 0

    def __iter__(self) -> "TestGenerator":
        """Get iterator.

        Returns:
            Generator iterator
        """
        return self

    def __next__(self) -> int:
        """Get next value.

        Returns:
            Next value

        Raises:
            StopIteration: When no more values are available
        """
        if self.index >= len(self.values):
            raise StopIteration
        value = self.values[self.index]
        self.index += 1
        return value


@pytest.fixture
def generator(test_generator_values: list[int]) -> TestGenerator:
    """Create test generator."""
    return TestGenerator(test_generator_values)


class TestAsyncGenerator:
    """Test async generator implementation."""

    def __init__(self, values: list[int]) -> None:
        """Initialize test async generator.

        Args:
            values: Values to generate
        """
        self.values = values
        self.index = 0

    def __aiter__(self) -> "TestAsyncGenerator":
        """Get async iterator.

        Returns:
            Async generator iterator
        """
        return self

    async def __anext__(self) -> int:
        """Get next value.

        Returns:
            Next value

        Raises:
            StopAsyncIteration: When no more values are available
        """
        if self.index >= len(self.values):
            raise StopAsyncIteration
        value = self.values[self.index]
        self.index += 1
        await asyncio.sleep(0.1)
        return value


@pytest.fixture
def async_generator(test_generator_values: list[int]) -> TestAsyncGenerator:
    """Create test async generator."""
    return TestAsyncGenerator(test_generator_values)


def test_generator_protocol(generator: TestGenerator) -> None:
    """Test generator protocol."""
    assert isinstance(generator, Generator)
    values = list(generator)
    assert values == [1, 2, 3]


@pytest.mark.asyncio
async def test_async_generator_protocol(async_generator: TestAsyncGenerator) -> None:
    """Test async generator protocol."""
    assert isinstance(async_generator, AsyncGenerator)
    values = []
    async for value in async_generator:
        values.append(value)
    assert values == [1, 2, 3]


def test_callable_protocol() -> None:
    """Test callable protocol."""

    def test_func(x: int) -> str:
        return str(x)

    assert isinstance(test_func, Callable)
    assert test_func(123) == "123"


@pytest.mark.asyncio
async def test_async_callable_protocol() -> None:
    """Test async callable protocol."""

    async def test_func(x: int) -> str:
        await asyncio.sleep(0.1)
        return str(x)

    assert isinstance(test_func, AsyncCallable)
    result = await test_func(123)
    assert result == "123"


@pytest.mark.asyncio
async def test_coroutine_protocol() -> None:
    """Test coroutine protocol."""

    async def test_coro() -> str:
        await asyncio.sleep(0.1)
        return "test"

    # Create and validate a coroutine
    test_func = test_coro  # Store the coroutine function
    coro = test_func()  # Create a coroutine
    assert isinstance(coro, Coroutine)
    result = await coro
    assert result == "test"


def test_generator_validation() -> None:
    """Test generator validation."""

    def test_gen() -> Gen[int, None, None]:
        yield 1
        yield 2
        yield 3

    validated = validate_generator(test_gen())
    assert isinstance(validated, Gen)
    assert list(validated) == [1, 2, 3]


def test_generator_validation_invalid() -> None:
    """Test generator validation invalid."""
    value = "not_a_generator"
    with pytest.raises(TypeError):
        validate_generator(value)


@pytest.mark.asyncio
async def test_async_generator_validation() -> None:
    """Test async generator validation."""

    async def test_gen() -> AsyncGen[int, None]:
        yield 1
        yield 2
        yield 3

    validated = validate_async_generator(test_gen())
    assert isinstance(validated, AsyncGen)
    values = []
    async for value in validated:
        values.append(value)
    assert values == [1, 2, 3]


@pytest.mark.asyncio
async def test_async_generator_validation_invalid() -> None:
    """Test async generator validation invalid."""
    value = "not_an_async_generator"
    with pytest.raises(TypeError):
        validate_async_generator(value)
