"""Template rendering utilities.

This module provides utilities for template rendering, including:
- Template context management
- Simple variable substitution
- Template metadata support
"""

import re
from dataclasses import dataclass
from typing import Any, Optional

from .core import PepperpyError
from .serialization import BaseSerializable, Serializable


class TemplateError(PepperpyError):
    """Error raised when there are template-related issues.

    Args:
        message: Error message
        cause: Optional cause of the error
        template_name: Optional name of the template that caused the error
    """

    def __init__(
        self,
        message: str,
        cause: Optional[Exception] = None,
        template_name: Optional[str] = None,
    ) -> None:
        super().__init__(message, cause)
        self.template_name = template_name


@dataclass
class TemplateContext(BaseSerializable, Serializable):
    """Template context containing variables for rendering.

    Args:
        variables: Dictionary of variables to use in template rendering
        metadata: Optional metadata dictionary
    """

    variables: dict[str, Any]
    metadata: dict[str, Any] | None = None


@dataclass
class Template(BaseSerializable, Serializable):
    """Template definition with rendering capabilities.

    Args:
        name: Template name
        content: Template content with variables in {{variable}} format
        description: Optional template description
        metadata: Optional metadata dictionary
    """

    name: str
    content: str
    description: str | None = None
    metadata: dict[str, Any] | None = None

    def render(self, context: TemplateContext) -> str:
        """Render template with context.

        Args:
            context: Template context containing variables

        Returns:
            Rendered template string

        Raises:
            TemplateError: If rendering fails or if required variables are missing
        """
        try:
            # Find all required variables in the template
            required_vars = set(re.findall(r"\{\{(\w+)\}\}", self.content))
            missing_vars = required_vars - set(context.variables.keys())

            if missing_vars:
                raise TemplateError(
                    f"Missing required variables: {', '.join(missing_vars)}",
                    template_name=self.name,
                )

            result = self.content
            for key, value in context.variables.items():
                result = result.replace(f"{{{{{key}}}}}", str(value))
            return result
        except Exception as e:
            if not isinstance(e, TemplateError):
                e = TemplateError(
                    f"Failed to render template {self.name}: {str(e)}",
                    cause=e,
                    template_name=self.name,
                )
            raise e


__all__ = [
    "TemplateError",
    "TemplateContext",
    "Template",
]
