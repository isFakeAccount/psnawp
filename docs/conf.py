# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
from __future__ import annotations

import os
import sys
from datetime import datetime
from importlib import metadata

sys.path.insert(1, os.path.abspath("../src"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = "PSNAWP"
copyright = datetime.today().strftime("%Y, Yoshikage Kira")
author = "Yoshikage Kira (@isFakeAccount)"
release = metadata.version("psnawp")

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
extensions = [
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "myst_parser",
]
add_module_names = False
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
    'ignore-module-all': True
}
html_static_path = ["_static"]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
nitpick_ignore = [
    ("py:class", "Logging"),
]

# myst_parser configs
myst_heading_anchors = 3
myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]
suppress_warnings = ['ref.myst']
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
pygments_style = "perldoc"
html_logo = "_static/psn_logo.png"
intersphinx_mapping = {"python": ("https://docs.python.org", None),
                       "requests": ("https://requests.readthedocs.io/en/latest/", None)}
htmlhelp_basename = "PSNAWP"
