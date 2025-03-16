# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
from __future__ import annotations

import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

sys.path.insert(0, str(Path("..", "src").resolve()))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = "PSNAWP"
project_copyright = datetime.now(timezone.utc).strftime("%Y, Yoshikage Kira")
author = "Yoshikage Kira (@isFakeAccount)"
release = metadata.version("psnawp")

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
extensions = [
    "myst_parser",
    "sphinx_copybutton",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
]

html_static_path = ["_static"]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
nitpick_ignore = [
    ("py:class", "Logging"),
]
add_module_names = False
suppress_warnings = ["ref.myst"]

# autosectionlabel configs
autosectionlabel_prefix_document = True

# autodoc Configs
autoclass_content = "both"
autodoc_default_options = {
    "members": True,
    "member-order": "alphabetical",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__, RequestBuilderHeaders",
    "ignore-module-all": True,
}

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
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
pygments_style = "stata-dark"
html_logo = "_static/psn_logo.png"
html_theme_options = {
    "repository_url": "https://github.com/isFakeAccount/psnawp",
    "use_repository_button": True,
}
intersphinx_mapping = {
    "python": ("https://docs.python.org", None),
    "requests": ("https://requests.readthedocs.io/en/latest/", None),
    "requests_ratelimiter": ("https://requests-ratelimiter.readthedocs.io/en/stable/", None),
}
html_title = "PSNAWP"
