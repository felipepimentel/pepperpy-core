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
