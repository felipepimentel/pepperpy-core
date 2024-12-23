"""Tests for the types module."""

from typing import Any, Protocol, cast

import pytest

from pepperpy_core.types import (
    BaseConfig,
    BaseConsumer,
    BaseConverter,
    BaseFilter,
    BaseFormatter,
    BaseHandler,
    BaseObserver,
    BaseParser,
    BaseProcessor,
    BaseProvider,
    BasePublisher,
    BaseSerializer,
    BaseSubject,
    BaseSubscriber,
    BaseTransformer,
    BaseValidator,
)


def verify_protocol_compliance(
    protocol_cls: type[Protocol], implementation_cls: type[Any]
) -> None:
    """Verify that a class implements a protocol correctly."""
    try:
        # Create an instance with default arguments if possible
        try:
            instance = implementation_cls()
        except TypeError:
            # If the class requires arguments, create a mock instance
            instance = implementation_cls.__new__(implementation_cls)
            instance.__init__ = lambda *args, **kwargs: None  # type: ignore
            instance.__init__()
        # This will raise TypeError if the implementation doesn't satisfy the protocol
        cast(protocol_cls, instance)
    except TypeError as e:
        pytest.fail(
            f"{implementation_cls.__name__} does not implement "
            f"{protocol_cls.__name__} correctly: {e}"
        )


def test_base_config() -> None:
    """Test BaseConfig."""
    # Test with metadata
    config = BaseConfig(name="test", metadata={"key": "value"})
    assert config.name == "test"
    assert config.metadata == {"key": "value"}

    # Test without metadata
    config = BaseConfig(name="test")
    assert isinstance(config.metadata, dict)
    assert len(config.metadata) == 0

    # Test validate method
    config.validate()  # Should not raise

    # Test metadata mutation
    config.metadata["key"] = "value"
    assert config.metadata == {"key": "value"}

    # Test metadata independence
    config1 = BaseConfig(name="test1")
    config2 = BaseConfig(name="test2")
    config1.metadata["key"] = "value"
    assert "key" not in config2.metadata

    # Test type hints - these are static type checks
    # Note: Runtime type checking is not enforced by dataclasses by default
    config = BaseConfig(name="test")
    assert isinstance(config.name, str)
    assert isinstance(config.metadata, dict)


def test_base_validator() -> None:
    """Test BaseValidator."""

    class TestValidator(BaseValidator):
        def validate(self, value: str) -> None:
            if not isinstance(value, str):
                raise TypeError("Value must be a string")
            if not value:
                raise ValueError("Value cannot be empty")
            if len(value) > 10:
                raise ValueError("Value too long")

    # Verify protocol compliance
    verify_protocol_compliance(BaseValidator, TestValidator)

    validator = TestValidator()
    # Test valid cases
    validator.validate("test")  # Should not raise
    validator.validate("a" * 10)  # Should not raise

    # Test invalid cases
    with pytest.raises(ValueError, match="Value cannot be empty"):
        validator.validate("")
    with pytest.raises(ValueError, match="Value too long"):
        validator.validate("a" * 11)
    with pytest.raises(TypeError, match="Value must be a string"):
        validator.validate(123)  # type: ignore


def test_base_serializer() -> None:
    """Test BaseSerializer."""

    class TestSerializer(BaseSerializer):
        def serialize(self, value: str | bytes | None) -> bytes:
            if value is None:
                return b""
            if isinstance(value, bytes):
                return value
            return value.encode("utf-8")

        def deserialize(self, value: bytes | str | None) -> str:
            if value is None:
                return ""
            if isinstance(value, str):
                return value
            return value.decode("utf-8")

    # Verify protocol compliance
    verify_protocol_compliance(BaseSerializer, TestSerializer)

    serializer = TestSerializer()
    # Test string serialization
    assert serializer.serialize("test") == b"test"
    assert serializer.deserialize(b"test") == "test"

    # Test bytes passthrough
    assert serializer.serialize(b"test") == b"test"
    assert serializer.deserialize("test") == "test"

    # Test None handling
    assert serializer.serialize(None) == b""
    assert serializer.deserialize(None) == ""

    # Test special characters
    special = "Hello, 世界"
    assert serializer.deserialize(serializer.serialize(special)) == special


def test_base_formatter() -> None:
    """Test BaseFormatter."""

    class TestFormatter(BaseFormatter):
        def format(self, value: int | float | str) -> str:
            if isinstance(value, (int, float)):
                return f"{value:0.2f}"
            return str(value)

    # Verify protocol compliance
    verify_protocol_compliance(BaseFormatter, TestFormatter)

    formatter = TestFormatter()
    # Test integer formatting
    assert formatter.format(5) == "5.00"
    assert formatter.format(0) == "0.00"
    assert formatter.format(-5) == "-5.00"

    # Test float formatting
    assert formatter.format(5.123) == "5.12"
    assert formatter.format(0.0) == "0.00"
    assert formatter.format(-5.678) == "-5.68"

    # Test string passthrough
    assert formatter.format("test") == "test"


def test_base_parser() -> None:
    """Test BaseParser."""

    class TestParser(BaseParser):
        def parse(self, value: str) -> int | None:
            try:
                return int(value)
            except ValueError:
                return None

    # Verify protocol compliance
    verify_protocol_compliance(BaseParser, TestParser)

    parser = TestParser()
    # Test valid integers
    assert parser.parse("42") == 42
    assert parser.parse("-42") == -42
    assert parser.parse("0") == 0

    # Test invalid inputs
    assert parser.parse("not a number") is None
    assert parser.parse("12.34") is None
    assert parser.parse("") is None


def test_base_converter() -> None:
    """Test BaseConverter."""

    class TestConverter(BaseConverter):
        def convert(self, value: str | int | float) -> float:
            if isinstance(value, str):
                return float(value or 0)
            return float(value)

    # Verify protocol compliance
    verify_protocol_compliance(BaseConverter, TestConverter)

    converter = TestConverter()
    # Test string conversion
    assert converter.convert("42") == 42.0
    assert converter.convert("42.5") == 42.5
    assert converter.convert("") == 0.0

    # Test numeric conversion
    assert converter.convert(42) == 42.0
    assert converter.convert(42.5) == 42.5
    assert converter.convert(-42) == -42.0

    # Test type preservation
    result = converter.convert("42.5")
    assert isinstance(result, float)


def test_base_filter() -> None:
    """Test BaseFilter."""

    class TestFilter(BaseFilter):
        def __init__(self, min_value: int) -> None:
            self.min_value = min_value

        def filter(self, value: int | None) -> bool:
            if value is None:
                return False
            return value > self.min_value

    # Verify protocol compliance
    verify_protocol_compliance(BaseFilter, TestFilter)

    filter_obj = TestFilter(min_value=0)
    # Test valid cases
    assert filter_obj.filter(5) is True
    assert filter_obj.filter(1) is True

    # Test boundary cases
    assert filter_obj.filter(0) is False
    assert filter_obj.filter(-1) is False

    # Test None handling
    assert filter_obj.filter(None) is False


def test_base_transformer() -> None:
    """Test BaseTransformer."""

    class TestTransformer(BaseTransformer):
        def transform(self, value: str | None) -> str:
            if value is None:
                return ""
            return value.upper()

    # Verify protocol compliance
    verify_protocol_compliance(BaseTransformer, TestTransformer)

    transformer = TestTransformer()
    # Test normal transformation
    assert transformer.transform("test") == "TEST"
    assert transformer.transform("Test") == "TEST"
    assert transformer.transform("TEST") == "TEST"

    # Test empty string
    assert transformer.transform("") == ""

    # Test None handling
    assert transformer.transform(None) == ""

    # Test special characters
    assert transformer.transform("Hello, 世界") == "HELLO, 世界"


def test_base_handler() -> None:
    """Test BaseHandler."""

    class TestHandler(BaseHandler):
        def __init__(self) -> None:
            self.handled: list[str] = []
            self.error_count = 0

        def handle(self, value: str | None) -> None:
            if value is None:
                self.error_count += 1
                return
            self.handled.append(value)

    # Verify protocol compliance
    verify_protocol_compliance(BaseHandler, TestHandler)

    handler = TestHandler()
    # Test normal handling
    handler.handle("test1")
    handler.handle("test2")
    assert handler.handled == ["test1", "test2"]
    assert handler.error_count == 0

    # Test None handling
    handler.handle(None)
    assert handler.handled == ["test1", "test2"]
    assert handler.error_count == 1

    # Test empty string
    handler.handle("")
    assert handler.handled == ["test1", "test2", ""]
    assert handler.error_count == 1


def test_base_processor() -> None:
    """Test BaseProcessor."""

    class TestProcessor(BaseProcessor):
        def process(self, value: str | None) -> str:
            if value is None:
                return ""
            return value.strip().lower()

    # Verify protocol compliance
    verify_protocol_compliance(BaseProcessor, TestProcessor)

    processor = TestProcessor()
    # Test normal processing
    assert processor.process("  TEST  ") == "test"
    assert processor.process("Test") == "test"
    assert processor.process(" test ") == "test"

    # Test empty string
    assert processor.process("") == ""

    # Test None handling
    assert processor.process(None) == ""

    # Test whitespace only
    assert processor.process("   ") == ""


def test_base_provider() -> None:
    """Test BaseProvider."""

    class TestProvider(BaseProvider):
        def __init__(self, start: int = 0) -> None:
            self.counter = start
            self.active = True

        def provide(self) -> int | None:
            if not self.active:
                return None
            self.counter += 1
            return self.counter

        def stop(self) -> None:
            self.active = False

    # Verify protocol compliance
    verify_protocol_compliance(BaseProvider, TestProvider)

    # Test normal provision
    provider = TestProvider()
    assert provider.provide() == 1
    assert provider.provide() == 2
    assert provider.provide() == 3

    # Test custom start
    provider = TestProvider(start=10)
    assert provider.provide() == 11
    assert provider.provide() == 12

    # Test stop behavior
    provider.stop()
    assert provider.provide() is None


def test_base_consumer() -> None:
    """Test BaseConsumer."""

    class TestConsumer(BaseConsumer):
        def __init__(self) -> None:
            self.consumed: list[str] = []
            self.error_count = 0

        def consume(self, value: str | None) -> None:
            if value is None:
                self.error_count += 1
                return
            if value:  # Only consume non-empty strings
                self.consumed.append(value)

    # Verify protocol compliance
    verify_protocol_compliance(BaseConsumer, TestConsumer)

    consumer = TestConsumer()
    # Test normal consumption
    consumer.consume("test1")
    consumer.consume("test2")
    assert consumer.consumed == ["test1", "test2"]
    assert consumer.error_count == 0

    # Test None handling
    consumer.consume(None)
    assert consumer.consumed == ["test1", "test2"]
    assert consumer.error_count == 1

    # Test empty string
    consumer.consume("")
    assert consumer.consumed == ["test1", "test2"]
    assert consumer.error_count == 1


def test_base_publisher() -> None:
    """Test BasePublisher."""

    class TestPublisher(BasePublisher):
        def __init__(self) -> None:
            self.published: list[str] = []
            self.active = True

        def publish(self, value: str | None) -> None:
            if not self.active:
                return
            if value is not None:
                self.published.append(value)

        def stop(self) -> None:
            self.active = False

    # Verify protocol compliance
    verify_protocol_compliance(BasePublisher, TestPublisher)

    publisher = TestPublisher()
    # Test normal publishing
    publisher.publish("test1")
    publisher.publish("test2")
    assert publisher.published == ["test1", "test2"]

    # Test None handling
    publisher.publish(None)
    assert publisher.published == ["test1", "test2"]

    # Test after stop
    publisher.stop()
    publisher.publish("test3")
    assert publisher.published == ["test1", "test2"]


def test_base_subscriber() -> None:
    """Test BaseSubscriber."""

    class TestSubscriber(BaseSubscriber):
        def __init__(self) -> None:
            self.subscribed: list[str] = []
            self.active = True

        def subscribe(self, value: str | None) -> None:
            if not self.active:
                return
            if value is not None:
                self.subscribed.append(value)

        def unsubscribe(self) -> None:
            self.active = False

    # Verify protocol compliance
    verify_protocol_compliance(BaseSubscriber, TestSubscriber)

    subscriber = TestSubscriber()
    # Test normal subscription
    subscriber.subscribe("test1")
    subscriber.subscribe("test2")
    assert subscriber.subscribed == ["test1", "test2"]

    # Test None handling
    subscriber.subscribe(None)
    assert subscriber.subscribed == ["test1", "test2"]

    # Test after unsubscribe
    subscriber.unsubscribe()
    subscriber.subscribe("test3")
    assert subscriber.subscribed == ["test1", "test2"]


def test_base_observer() -> None:
    """Test BaseObserver."""

    class TestObserver(BaseObserver):
        def __init__(self) -> None:
            self.updates: list[str] = []
            self.active = True

        def update(self, value: str | None) -> None:
            if not self.active:
                return
            if value is not None:
                self.updates.append(value)

        def deactivate(self) -> None:
            self.active = False

    # Verify protocol compliance
    verify_protocol_compliance(BaseObserver, TestObserver)

    observer = TestObserver()
    # Test normal updates
    observer.update("test1")
    observer.update("test2")
    assert observer.updates == ["test1", "test2"]

    # Test None handling
    observer.update(None)
    assert observer.updates == ["test1", "test2"]

    # Test after deactivation
    observer.deactivate()
    observer.update("test3")
    assert observer.updates == ["test1", "test2"]


def test_base_subject() -> None:
    """Test BaseSubject."""

    class TestSubject(BaseSubject):
        def __init__(self) -> None:
            self.observers: list[BaseObserver] = []
            self.value = ""
            self.active = True

        def attach(self, observer: BaseObserver) -> None:
            if observer not in self.observers:
                self.observers.append(observer)

        def detach(self, observer: BaseObserver) -> None:
            if observer in self.observers:
                self.observers.remove(observer)

        def notify(self) -> None:
            if not self.active:
                return
            for observer in self.observers:
                observer.update(self.value)

        def set_value(self, value: str) -> None:
            self.value = value
            self.notify()

        def deactivate(self) -> None:
            self.active = False

    class TestObserver(BaseObserver):
        def __init__(self) -> None:
            self.updates: list[str] = []

        def update(self, value: str) -> None:
            self.updates.append(value)

    # Verify protocol compliance
    verify_protocol_compliance(BaseSubject, TestSubject)
    verify_protocol_compliance(BaseObserver, TestObserver)

    # Test normal observer pattern
    subject = TestSubject()
    observer1 = TestObserver()
    observer2 = TestObserver()

    # Test attach
    subject.attach(observer1)
    subject.attach(observer2)
    subject.set_value("test1")
    assert observer1.updates == ["test1"]
    assert observer2.updates == ["test1"]

    # Test duplicate attach
    subject.attach(observer1)
    subject.set_value("test2")
    assert observer1.updates == ["test1", "test2"]
    assert observer2.updates == ["test1", "test2"]

    # Test detach
    subject.detach(observer1)
    subject.set_value("test3")
    assert observer1.updates == ["test1", "test2"]
    assert observer2.updates == ["test1", "test2", "test3"]

    # Test detach non-existent
    subject.detach(observer1)  # Should not raise
    subject.set_value("test4")
    assert observer1.updates == ["test1", "test2"]
    assert observer2.updates == ["test1", "test2", "test3", "test4"]

    # Test after deactivation
    subject.deactivate()
    subject.set_value("test5")
    assert observer1.updates == ["test1", "test2"]
    assert observer2.updates == ["test1", "test2", "test3", "test4"]
