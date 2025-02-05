# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

sys.path.insert(0, os.path.abspath('../../'))

from fbchat_muqit import __version__

project = 'fbchat-muqit'
copyright = '2025, Muhammad MuQiT'
author = 'Muhammad MuQiT'
release = __version__
version = release
# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add the path to the fbchat_muqit package

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc.typehints',
    'sphinx.ext.intersphinx',
]

# Napoleon settings
napoleon_google_docstring = True 
napoleon_include_init_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'undoc-members': False,
    'show-inheritance': False,
    'private-members': False,  # Exclude private members
    'special-members': False,  # Exclude special methods
}

autodoc_member_order = "bysource"
autodoc_class_signature = "separated"

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']

html_show_sphinx = False
html_show_sourcelink = False
