"""PepperPy Core package.

A robust and extensible Python framework for building event-driven applications.
This package provides core functionality for event handling, configuration
management, and plugin systems.
"""

import importlib.metadata
from pathlib import Path

# Package metadata
try:
    __version__ = importlib.metadata.version(__package__ or __name__)
except importlib.metadata.PackageNotFoundError:
    # Check for VERSION file
    version_file = Path(__file__).parent / "VERSION"
    if version_file.exists():
        __version__ = version_file.read_text().strip()
    else:
        __version__ = "0.0.0-dev"

__name__ = __package__ or Path(__file__).parent.name

# Public API exports
from pepperpy.cache import CacheError  # noqa: E402
from pepperpy.callables import (  # noqa: E402
    AsyncCallable,
    Callable,
    Coroutine,
)
from pepperpy.config import BaseConfig  # noqa: E402
from pepperpy.context import ContextError  # noqa: E402
from pepperpy.core import (  # noqa: E402
    PepperpyError,
    format_error_context,
    format_exception,
    get_error_type,
)
from pepperpy.event import (  # noqa: E402
    Event,
    EventBus,
    EventError,
    EventHandler,
    EventListener,
)
from pepperpy.generators import (  # noqa: E402
    AsyncGenerator,
    Generator,
)
from pepperpy.io import IOError  # noqa: E402
from pepperpy.logging import (  # noqa: E402
    LoggerMixin,
    get_logger,
    get_module_logger,
    get_package_logger,
)
from pepperpy.module import ModuleError  # noqa: E402
from pepperpy.network import NetworkError  # noqa: E402
from pepperpy.pipeline import PipelineError  # noqa: E402
from pepperpy.plugin import PluginError  # noqa: E402
from pepperpy.registry import RegistryError  # noqa: E402
from pepperpy.resources import ResourceError  # noqa: E402
from pepperpy.security import SecurityError  # noqa: E402
from pepperpy.serialization import SerializationError  # noqa: E402
from pepperpy.task import TaskError  # noqa: E402
from pepperpy.telemetry import TelemetryError  # noqa: E402
from pepperpy.validators import validate_protocol, validate_type  # noqa: E402

__all__ = [
    # Version info
    "__version__",
    # Error utilities
    "format_error_context",
    "format_exception",
    "get_error_type",
    # Event system
    "Event",
    "EventBus",
    "EventHandler",
    "EventListener",
    # Exceptions
    "PepperpyError",
    "CacheError",
    "ContextError",
    "EventError",
    "IOError",
    "ModuleError",
    "NetworkError",
    "PipelineError",
    "PluginError",
    "RegistryError",
    "ResourceError",
    "SecurityError",
    "SerializationError",
    "TaskError",
    "TelemetryError",
    # Logging
    "LoggerMixin",
    "get_logger",
    "get_module_logger",
    "get_package_logger",
    # Types
    "AsyncCallable",
    "AsyncGenerator",
    "BaseConfig",
    "Callable",
    "Coroutine",
    "Generator",
    # Validation
    "validate_type",
    "validate_protocol",
]
