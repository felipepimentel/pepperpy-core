"""Test template module."""

import pytest

from pepperpy.template import Template, TemplateContext, TemplateError


def test_template_context_init() -> None:
    """Test template context initialization."""
    context = TemplateContext(variables={"name": "test"})
    assert context.variables == {"name": "test"}
    assert context.metadata is None

    context = TemplateContext(variables={"name": "test"}, metadata={"source": "test"})
    assert context.variables == {"name": "test"}
    assert context.metadata == {"source": "test"}


def test_template_context_to_dict() -> None:
    """Test template context serialization."""
    context = TemplateContext(variables={"name": "test"}, metadata={"source": "test"})
    data = context.to_dict()
    assert data == {
        "variables": {"name": "test"},
        "metadata": {"source": "test"},
    }


def test_template_context_from_dict() -> None:
    """Test template context deserialization."""
    data = {
        "variables": {"name": "test"},
        "metadata": {"source": "test"},
    }
    context = TemplateContext.from_dict(data)
    assert context.variables == {"name": "test"}
    assert context.metadata == {"source": "test"}


def test_template_init() -> None:
    """Test template initialization."""
    template = Template(name="test", content="Hello {{name}}!")
    assert template.name == "test"
    assert template.content == "Hello {{name}}!"
    assert template.description is None
    assert template.metadata is None

    template = Template(
        name="test",
        content="Hello {{name}}!",
        description="Test template",
        metadata={"source": "test"},
    )
    assert template.name == "test"
    assert template.content == "Hello {{name}}!"
    assert template.description == "Test template"
    assert template.metadata == {"source": "test"}


def test_template_to_dict() -> None:
    """Test template serialization."""
    template = Template(
        name="test",
        content="Hello {{name}}!",
        description="Test template",
        metadata={"source": "test"},
    )
    data = template.to_dict()
    assert data == {
        "name": "test",
        "content": "Hello {{name}}!",
        "description": "Test template",
        "metadata": {"source": "test"},
    }


def test_template_from_dict() -> None:
    """Test template deserialization."""
    data = {
        "name": "test",
        "content": "Hello {{name}}!",
        "description": "Test template",
        "metadata": {"source": "test"},
    }
    template = Template.from_dict(data)
    assert template.name == "test"
    assert template.content == "Hello {{name}}!"
    assert template.description == "Test template"
    assert template.metadata == {"source": "test"}


def test_template_render() -> None:
    """Test template rendering."""
    template = Template(name="test", content="Hello {{name}}!")
    context = TemplateContext(variables={"name": "world"})
    result = template.render(context)
    assert result == "Hello world!"

    # Test multiple variables
    template = Template(name="test", content="{{greeting}} {{name}}!")
    context = TemplateContext(variables={"greeting": "Hi", "name": "world"})
    result = template.render(context)
    assert result == "Hi world!"


def test_template_render_error() -> None:
    """Test template rendering error."""
    template = Template(name="test", content="Hello {{name}}!")
    context = TemplateContext(variables={})

    with pytest.raises(TemplateError) as exc_info:
        template.render(context)
    assert "Missing required variables: name" in str(exc_info.value)
    assert exc_info.value.template_name == "test"


def test_template_render_multiple_missing_vars() -> None:
    """Test template rendering with multiple missing variables."""
    template = Template(name="test", content="{{greeting}} {{name}}!")
    context = TemplateContext(variables={})

    with pytest.raises(TemplateError) as exc_info:
        template.render(context)
    assert "Missing required variables: greeting, name" in str(exc_info.value)
    assert exc_info.value.template_name == "test"


def test_template_render_empty_content() -> None:
    """Test template rendering with empty content."""
    template = Template(name="test", content="")
    context = TemplateContext(variables={"name": "world"})
    result = template.render(context)
    assert result == ""


def test_template_render_empty_values() -> None:
    """Test template rendering with empty variable values."""
    template = Template(name="test", content="Hello {{name}}!")
    context = TemplateContext(variables={"name": ""})
    result = template.render(context)
    assert result == "Hello !"

    context = TemplateContext(variables={"name": None})
    result = template.render(context)
    assert result == "Hello None!"


def test_template_render_special_chars() -> None:
    """Test template rendering with special characters."""
    template = Template(
        name="test",
        content="Path: {{path}}, URL: {{url}}, HTML: {{html}}",
    )
    context = TemplateContext(
        variables={
            "path": "/home/user/file.txt",
            "url": "https://example.com?q=test&p=1",
            "html": "<script>alert('test')</script>",
        }
    )
    result = template.render(context)
    assert (
        result == "Path: /home/user/file.txt, "
        "URL: https://example.com?q=test&p=1, "
        "HTML: <script>alert('test')</script>"
    )


def test_template_render_extra_vars() -> None:
    """Test template rendering with extra variables in context."""
    template = Template(name="test", content="Hello {{name}}!")
    context = TemplateContext(variables={"name": "world", "extra": "unused"})
    result = template.render(context)
    assert result == "Hello world!"


def test_template_render_invalid_syntax() -> None:
    """Test template rendering with invalid variable syntax."""
    template = Template(name="test", content="Hello {name}!")  # Single braces
    context = TemplateContext(variables={"name": "world"})
    result = template.render(context)
    assert result == "Hello {name}!"  # Should not replace single braces

    template = Template(name="test", content="Hello {{{name}}}!")  # Triple braces
    result = template.render(context)
    assert result == "Hello {world}!"  # Should handle triple braces


def test_template_render_duplicate_vars() -> None:
    """Test template rendering with duplicate variables."""
    template = Template(name="test", content="{{name}}, {{name}}!")
    context = TemplateContext(variables={"name": "world"})
    result = template.render(context)
    assert result == "world, world!"


def test_template_render_nested_content() -> None:
    """Test template rendering with nested content."""
    template = Template(
        name="test",
        content="{{outer}} { {{inner}} }",
    )
    context = TemplateContext(
        variables={
            "outer": "Hello",
            "inner": "World",
        }
    )
    result = template.render(context)
    assert result == "Hello { World }"


def test_template_update() -> None:
    """Test template update method."""
    template = Template(
        name="test",
        content="Hello {{name}}!",
        description="Original description",
        metadata={"version": "1.0"},
    )

    # Update single field
    template.update(description="Updated description")
    assert template.description == "Updated description"
    assert template.metadata == {"version": "1.0"}

    # Update multiple fields
    template.update(
        content="Hi {{name}}!",
        metadata={"version": "2.0"},
    )
    assert template.content == "Hi {{name}}!"
    assert template.metadata == {"version": "2.0"}


def test_template_context_update() -> None:
    """Test template context update method."""
    context = TemplateContext(
        variables={"name": "test"},
        metadata={"version": "1.0"},
    )

    # Update variables
    context.update(variables={"name": "updated", "new": "value"})
    assert context.variables == {"name": "updated", "new": "value"}
    assert context.metadata == {"version": "1.0"}

    # Update metadata
    context.update(metadata={"version": "2.0", "status": "active"})
    assert context.metadata == {"version": "2.0", "status": "active"}
