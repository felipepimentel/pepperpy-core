"""Sphinx configuration."""

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "PepperPy Core"
copyright = "2024, Felipe Pimentel"
author = "Felipe Pimentel"

# General configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# HTML output configuration
html_theme = "sphinx_rtd_theme"
html_static_path = ["static"]
html_theme_options = {
    "navigation_depth": 4,
    "titles_only": False,
}

# Source configuration
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
source_encoding = "utf-8"

# Extension configuration
autodoc_typehints = "description"
autodoc_member_order = "bysource"
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True

# Intersphinx configuration
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# MyST configuration
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]
