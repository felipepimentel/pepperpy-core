# Template Module

The template module provides utilities for template rendering with simple variable substitution and metadata support.

## Overview

The template module implements a straightforward template rendering system that supports:
- Basic variable substitution using `{{variable}}` syntax
- Template context management
- Metadata support for both templates and contexts
- Error handling with detailed error messages

## Classes

### TemplateError

A specialized error class for template-related issues.

```python
class TemplateError(PepperpyError):
    def __init__(self, message: str, cause: Optional[Exception] = None, template_name: Optional[str] = None)
```

**Arguments:**
- `message`: Error message describing the issue
- `cause`: Optional underlying exception that caused the error
- `template_name`: Optional name of the template where the error occurred

### TemplateContext

A dataclass representing the context used for template rendering.

```python
@dataclass
class TemplateContext(BaseSerializable):
    variables: dict[str, Any]
    metadata: dict[str, Any] | None = None
```

**Attributes:**
- `variables`: Dictionary of variables to use in template rendering
- `metadata`: Optional metadata dictionary for additional context information

### Template

A dataclass representing a template with rendering capabilities.

```python
@dataclass
class Template(BaseSerializable):
    name: str
    content: str
    description: str | None = None
    metadata: dict[str, Any] | None = None
```

**Attributes:**
- `name`: Template name
- `content`: Template content with variables in `{{variable}}` format
- `description`: Optional template description
- `metadata`: Optional metadata dictionary

**Methods:**

#### render

```python
def render(self, context: TemplateContext) -> str
```

Renders the template using the provided context.

**Arguments:**
- `context`: Template context containing variables for substitution

**Returns:**
- The rendered template string with all variables replaced

**Raises:**
- `TemplateError`: If rendering fails

## Usage Examples

### Basic Template Rendering

```python
from pepperpy.template import Template, TemplateContext

# Create a template
template = Template(
    name="greeting",
    content="Hello {{name}}!",
    description="A simple greeting template"
)

# Create a context with variables
context = TemplateContext(
    variables={"name": "John"}
)

# Render the template
result = template.render(context)  # Returns: "Hello John!"
```

### Template with Metadata

```python
# Create a template with metadata
template = Template(
    name="email",
    content="Subject: {{subject}}\n\nDear {{recipient}},\n\n{{body}}\n\nBest regards,\n{{sender}}",
    description="Email template",
    metadata={
        "version": "1.0",
        "category": "communication"
    }
)

# Create a context with variables and metadata
context = TemplateContext(
    variables={
        "subject": "Meeting Invitation",
        "recipient": "Alice",
        "body": "Would you like to meet tomorrow at 2 PM?",
        "sender": "Bob"
    },
    metadata={
        "priority": "high",
        "department": "sales"
    }
)

# Render the template
result = template.render(context)
```

### Error Handling

```python
try:
    template = Template(
        name="report",
        content="Revenue: ${{revenue}}"
    )
    context = TemplateContext(
        variables={}  # Missing required variable
    )
    result = template.render(context)
except TemplateError as e:
    print(f"Template error: {e}")
    if e.template_name:
        print(f"Template name: {e.template_name}")
```

## Best Practices

1. **Template Names**: Use descriptive template names that reflect their purpose
2. **Variable Names**: Use clear and consistent variable names in templates
3. **Metadata Usage**: Use metadata to store template-specific configuration and context information
4. **Error Handling**: Always handle `TemplateError` exceptions appropriately
5. **Documentation**: Include descriptions for templates to aid maintainability

## See Also

- [Core Module](core.md) - Core functionality including base error classes
- [Serialization Module](serialization.md) - Base serialization support used by template classes 