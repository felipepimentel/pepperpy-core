"""Pipeline implementation module."""

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from .exceptions import PepperpyError
from .module import BaseModule, ModuleConfig


class PipelineError(PepperpyError):
    """Pipeline specific error."""

    pass


@dataclass
class PipelineConfig(ModuleConfig):
    """Pipeline configuration."""

    # Required fields (inherited from ModuleConfig)
    name: str

    # Optional fields
    enabled: bool = True
    max_concurrent: int = 10
    timeout: float = 60.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate configuration."""
        if self.max_concurrent < 1:
            raise ValueError("max_concurrent must be greater than 0")
        if self.timeout <= 0:
            raise ValueError("timeout must be greater than 0")


InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")
StepInputT = TypeVar("StepInputT")
StepOutputT = TypeVar("StepOutputT")


@dataclass
class PipelineResult(Generic[OutputT]):
    """Result of pipeline execution."""

    output: OutputT
    metadata: dict[str, Any] = field(default_factory=dict)


class PipelineStep(Generic[StepInputT, StepOutputT]):
    """Base class for pipeline steps."""

    async def execute(self, input_data: StepInputT) -> StepOutputT:
        """Execute pipeline step.

        Args:
            input_data: Input data to process

        Returns:
            Processed output data
        """
        raise NotImplementedError


class Pipeline(Generic[InputT, OutputT]):
    """Base pipeline implementation."""

    def __init__(self, config: PipelineConfig) -> None:
        """Initialize pipeline.

        Args:
            config: Pipeline configuration
        """
        self.config = config
        self._steps: list[PipelineStep[Any, Any]] = []

    def add_step(self, step: PipelineStep[Any, Any]) -> None:
        """Add step to pipeline.

        Args:
            step: Pipeline step to add
        """
        self._steps.append(step)

    async def execute(self, input_data: InputT) -> PipelineResult[OutputT]:
        """Execute pipeline.

        Args:
            input_data: Input data to process

        Returns:
            Pipeline execution result
        """
        current_data: Any = input_data

        for step in self._steps:
            current_data = await step.execute(current_data)

        return PipelineResult[OutputT](
            output=current_data, metadata={"steps": len(self._steps)}
        )


class PipelineManager(BaseModule[PipelineConfig]):
    """Pipeline manager implementation."""

    def __init__(self) -> None:
        """Initialize pipeline manager."""
        config = PipelineConfig(name="pipeline-manager")
        super().__init__(config)
        self._active_pipelines: dict[str, Pipeline[Any, Any]] = {}

    async def _setup(self) -> None:
        """Setup pipeline manager."""
        self._active_pipelines.clear()

    async def _teardown(self) -> None:
        """Teardown pipeline manager."""
        self._active_pipelines.clear()

    async def get_stats(self) -> dict[str, Any]:
        """Get pipeline manager statistics.

        Returns:
            Pipeline manager statistics
        """
        self._ensure_initialized()
        return {
            "name": self.config.name,
            "enabled": self.config.enabled,
            "active_pipelines": len(self._active_pipelines),
            "max_concurrent": self.config.max_concurrent,
            "timeout": self.config.timeout,
        }

    def register_pipeline(self, name: str, pipeline: Pipeline[Any, Any]) -> None:
        """Register a pipeline.

        Args:
            name: Pipeline name
            pipeline: Pipeline instance
        """
        self._ensure_initialized()
        if len(self._active_pipelines) >= self.config.max_concurrent:
            raise PipelineError("Maximum number of concurrent pipelines reached")
        self._active_pipelines[name] = pipeline

    def get_pipeline(self, name: str) -> Pipeline[Any, Any]:
        """Get a registered pipeline.

        Args:
            name: Pipeline name

        Returns:
            Pipeline instance

        Raises:
            KeyError: If pipeline not found
        """
        self._ensure_initialized()
        if name not in self._active_pipelines:
            raise KeyError(f"Pipeline {name} not found")
        return self._active_pipelines[name]


__all__ = [
    "PipelineError",
    "PipelineConfig",
    "PipelineResult",
    "PipelineStep",
    "Pipeline",
    "PipelineManager",
]
