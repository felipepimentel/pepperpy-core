"""PepperPy Core package."""

from pepperpy.cache import Cache, CacheConfig, CacheEntry, MemoryCache
from pepperpy.registry import Registry, RegistryError, RegistryProtocol
from pepperpy.utils.error import Error, ErrorLevel
from pepperpy.validators import (
    BaseValidator,
    ChainValidator,
    TypeValidator,
    ValidationResult,
)

__version__ = "0.0.0-dev"

__all__ = [
    # Cache
    "Cache",
    "CacheEntry",
    "CacheConfig",
    "MemoryCache",
    # Registry
    "Registry",
    "RegistryError",
    "RegistryProtocol",
    # Utils
    "Error",
    "ErrorLevel",
    # Validators
    "BaseValidator",
    "ChainValidator",
    "TypeValidator",
    "ValidationResult",
]
