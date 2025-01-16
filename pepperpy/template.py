"""Template module."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from pepperpy.core import PepperpyError
from pepperpy.module import BaseModule, ModuleConfig
from pepperpy.serialization import BaseSerializable


class TemplateError(PepperpyError):
    """Template error."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, details, cause)


@dataclass
class TemplateContext:
    """Template context."""

    name: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Template(BaseSerializable):
    """Template."""

    name: str
    content: str
    context: Optional[TemplateContext] = None

    def serialize(self) -> Dict[str, Any]:
        """Serialize template.

        Returns:
            Serialized template
        """
        return {
            "name": self.name,
            "content": self.content,
            "context": self.context.__dict__ if self.context else None,
        }

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Deserialize template.

        Args:
            data: Serialized template
        """
        self.name = data["name"]
        self.content = data["content"]
        if data.get("context"):
            self.context = TemplateContext(**data["context"])
        else:
            self.context = None


@dataclass
class TemplateConfig(ModuleConfig):
    """Template configuration."""

    name: str = "template_manager"
    metadata: Dict[str, Any] = field(default_factory=dict)


class TemplateManager(BaseModule[TemplateConfig]):
    """Template manager."""

    def __init__(self, config: Optional[TemplateConfig] = None) -> None:
        """Initialize template manager.

        Args:
            config: Template configuration
        """
        super().__init__(config or TemplateConfig())
        self._templates: Dict[str, Template] = {}

    def _ensure_initialized(self) -> None:
        """Ensure manager is initialized.

        Raises:
            TemplateError: If manager is not initialized
        """
        if not self.is_initialized:
            raise TemplateError(
                "Template manager is not initialized",
                {"manager_name": self.config.name},
            )

    async def _setup(self) -> None:
        """Set up template manager."""
        self._templates = {}

    async def _teardown(self) -> None:
        """Clean up template manager."""
        self._templates = {}

    def register(self, template: Template) -> None:
        """Register template.

        Args:
            template: Template to register

        Raises:
            TemplateError: If template cannot be registered
        """
        self._ensure_initialized()
        if template.name in self._templates:
            raise TemplateError(
                "Template already registered",
                {"name": template.name, "manager_name": self.config.name},
            )
        self._templates[template.name] = template

    def get(self, name: str) -> Template:
        """Get template.

        Args:
            name: Template name

        Returns:
            Template instance

        Raises:
            TemplateError: If template is not found
        """
        self._ensure_initialized()
        if name not in self._templates:
            raise TemplateError(
                "Template not found",
                {"name": name, "manager_name": self.config.name},
            )
        return self._templates[name]

    def unregister(self, name: str) -> None:
        """Unregister template.

        Args:
            name: Template name

        Raises:
            TemplateError: If template cannot be unregistered
        """
        self._ensure_initialized()
        if name not in self._templates:
            raise TemplateError(
                "Template not found",
                {"name": name, "manager_name": self.config.name},
            )
        del self._templates[name]

    def clear(self) -> None:
        """Clear all templates.

        Raises:
            TemplateError: If templates cannot be cleared
        """
        self._ensure_initialized()
        self._templates = {}


__all__ = [
    "Template",
    "TemplateConfig",
    "TemplateContext",
    "TemplateError",
    "TemplateManager",
]
