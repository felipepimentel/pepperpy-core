"""Test logging utilities."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from pepperpy_core.utils.logging import (
    LoggerMixin,
    get_logger,
    get_module_logger,
    get_package_logger,
)


def test_get_logger() -> None:
    """Test get_logger utility."""
    logger = get_logger("test")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test"


def test_get_module_logger() -> None:
    """Test get_module_logger utility."""
    logger = get_module_logger("test_module")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_module"


def test_get_package_logger() -> None:
    """Test get_package_logger utility."""
    logger = get_package_logger()
    assert isinstance(logger, logging.Logger)
    assert logger.name == "pepperpy_core"


class TestLoggerMixin:
    """Test LoggerMixin class."""

    @pytest.fixture
    def logger_mock(self) -> MagicMock:
        """Create a mock logger."""
        return MagicMock(spec=logging.Logger)

    @pytest.fixture
    def mixin(self, logger_mock: MagicMock) -> LoggerMixin:
        """Create a LoggerMixin instance with mocked logger."""
        with patch("pepperpy_core.utils.logging.get_logger", return_value=logger_mock):
            mixin = LoggerMixin()
            return mixin

    def test_logger_property(self, mixin: LoggerMixin, logger_mock: MagicMock) -> None:
        """Test logger property."""
        assert mixin.logger == logger_mock

    def test_log(self, mixin: LoggerMixin, logger_mock: MagicMock) -> None:
        """Test log method."""
        mixin.log(logging.INFO, "test message", extra={"key": "value"})
        logger_mock.log.assert_called_once_with(
            logging.INFO, "test message", extra={"key": "value"}
        )

    def test_debug(self, mixin: LoggerMixin, logger_mock: MagicMock) -> None:
        """Test debug method."""
        mixin.debug("test message", extra={"key": "value"})
        logger_mock.debug.assert_called_once_with(
            "test message", extra={"key": "value"}
        )

    def test_info(self, mixin: LoggerMixin, logger_mock: MagicMock) -> None:
        """Test info method."""
        mixin.info("test message", extra={"key": "value"})
        logger_mock.info.assert_called_once_with("test message", extra={"key": "value"})

    def test_warning(self, mixin: LoggerMixin, logger_mock: MagicMock) -> None:
        """Test warning method."""
        mixin.warning("test message", extra={"key": "value"})
        logger_mock.warning.assert_called_once_with(
            "test message", extra={"key": "value"}
        )

    def test_error(self, mixin: LoggerMixin, logger_mock: MagicMock) -> None:
        """Test error method."""
        mixin.error("test message", extra={"key": "value"})
        logger_mock.error.assert_called_once_with(
            "test message", extra={"key": "value"}
        )

    def test_critical(self, mixin: LoggerMixin, logger_mock: MagicMock) -> None:
        """Test critical method."""
        mixin.critical("test message", extra={"key": "value"})
        logger_mock.critical.assert_called_once_with(
            "test message", extra={"key": "value"}
        )
