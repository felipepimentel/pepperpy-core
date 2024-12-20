"""Development tools for debugging, testing and profiling."""

import cProfile
import json
import pstats
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, TypeVar, cast

from ..types import JsonDict, JsonValue

T = TypeVar("T")

class LoggerProtocol(Protocol):
    """Protocol for logger interface."""
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        ...
        
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        ...

@dataclass
class Timer:
    """Simple timer for benchmarking."""
    
    name: str
    logger: LoggerProtocol | None = None
    _start: float = field(default=0.0, init=False)
    _end: float = field(default=0.0, init=False)
    
    def __enter__(self) -> "Timer":
        """Start timer."""
        self._start = time.perf_counter()
        return self
        
    def __exit__(self, *args: Any) -> None:
        """Stop timer and log result."""
        self._end = time.perf_counter()
        duration = self._end - self._start
        
        if self.logger:
            self.logger.info(
                f"{self.name} took {duration:.4f} seconds",
                timer=self.name,
                duration=duration,
            )

@dataclass
class Profiler:
    """Simple profiler for performance analysis."""
    
    name: str
    logger: LoggerProtocol | None = None
    output_path: Path | None = None
    _profiler: cProfile.Profile = field(default_factory=cProfile.Profile, init=False)
    
    def __enter__(self) -> "Profiler":
        """Start profiling."""
        self._profiler.enable()
        return self
        
    def __exit__(self, *args: Any) -> None:
        """Stop profiling and save results."""
        self._profiler.disable()
        
        stats = pstats.Stats(self._profiler)
        stats.sort_stats("cumulative")
        
        if self.output_path:
            stats.dump_stats(self.output_path)
            
        if self.logger:
            # Log top 10 functions
            self.logger.info(
                f"Profile results for {self.name}",
                profiler=self.name,
                stats=str(stats.print_stats(10)),
            )

@dataclass
class MockResponse:
    """Mock HTTP response for testing."""
    
    status: int = 200
    data: str | bytes | dict[str, Any] | None = None
    headers: dict[str, str] | None = field(default_factory=dict)
    
    async def json(self) -> JsonDict:
        """Get JSON response data."""
        if isinstance(self.data, (str, bytes)):
            return cast(JsonDict, json.loads(self.data))
        return cast(JsonDict, self.data or {})
        
    async def text(self) -> str:
        """Get text response data."""
        if isinstance(self.data, bytes):
            return self.data.decode()
        if isinstance(self.data, dict):
            return json.dumps(self.data)
        return str(self.data or "")

def mock_response(
    status: int = 200,
    data: str | bytes | dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> Callable[..., MockResponse]:
    """Create mock response factory."""
    def factory(*args: Any, **kwargs: Any) -> MockResponse:
        return MockResponse(status, data, headers)
    return factory

def debug_call(
    logger: LoggerProtocol,
    func_name: str,
    *args: Any,
    **kwargs: Any,
) -> None:
    """Log function call debug information."""
    logger.debug(
        f"Calling {func_name}",
        args=args,
        kwargs=kwargs,
    )

def debug_result(
    logger: LoggerProtocol,
    func_name: str,
    result: Any,
) -> None:
    """Log function result debug information."""
    logger.debug(
        f"Result from {func_name}",
        result=result,
    )

def debug_error(
    logger: LoggerProtocol,
    func_name: str,
    error: Exception,
) -> None:
    """Log function error debug information."""
    logger.debug(
        f"Error in {func_name}",
        error=str(error),
        error_type=type(error).__name__,
    ) 