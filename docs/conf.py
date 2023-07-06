"""Sphinx configuration."""
project = "Molecular Dynamics Setup"
author = "Timothy H. Click"
copyright = "2023, Timothy H. Click"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
