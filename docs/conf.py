"""Sphinx configuration."""

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "PepperPy Core"
copyright = "2024, Felipe Pimentel"
author = "Felipe Pimentel"

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

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Source directory configuration
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
source_encoding = "utf-8"

# Output directory configuration
master_doc = "index"
