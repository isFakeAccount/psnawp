# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from configparser import ConfigParser
from datetime import datetime

sys.path.insert(1, os.path.abspath("../src"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = "PSNAWP"
copyright = datetime.today().strftime("%Y, Yoshikage Kira")
author = "Yoshikage Kira (@isFakeAccount)"
config = ConfigParser()
data = config.read('../setup.cfg')
release = config['metadata']['version']

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

source_suffix = ['.rst', '.md']
extensions = ["sphinx.ext.todo", "sphinx.ext.viewcode", "sphinx.ext.autodoc", "sphinx.ext.intersphinx", "myst_parser"]
add_module_names = False
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}
html_static_path = ["_static"]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
nitpick_ignore = [
    ("py:class", "Logging"),
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_materialdesign_theme"
pygments_style = "perldoc"
html_theme_options = {
    'header_links': [
        ('Home', 'index', False, 'home'),
        ("GitHub", "https://github.com/isFakeAccount/psnawp", True, 'link')
    ],
    'primary_color': 'light_blue',
    'accent_color': 'deep_purple',
    'fixed_drawer': False,
    'fixed_header': False,
    'header_waterfall': True,
    'header_scroll': False,

    'show_header_title': False,
    'show_drawer_title': True,
    'show_footer': True
}
intersphinx_mapping = {"python": ("https://docs.python.org", None),
                       "requests": ("https://requests.readthedocs.io/en/latest/", None)}
htmlhelp_basename = "PSNAWP"
suppress_warnings = ['ref.myst']
