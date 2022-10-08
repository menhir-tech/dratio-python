# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


import os
import sys

sys.path.append(os.path.abspath('../..'))
sys.path.append(os.path.abspath('..'))
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'dratio'
copyright = '2022, dratio.io'
author = 'dratio.io'
release = '0.0.4'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx_rtd_theme',
              'sphinx.ext.napoleon',
              'sphinx.ext.autodoc',
              'sphinx.ext.intersphinx',
              'sphinx.ext.autosummary']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Add mappings
intersphinx_mapping = {
    'requests': ('https://requests.readthedocs.io/en/latest/', None),
    'python': ('http://docs.python.org/3', None),
    'pandas': ('http://pandas.pydata.org/pandas-docs/dev', None),
    'geopandas': ('https://geopandas.org/en/latest/', None),
}

autodoc_default_options = {'members': True, 'inherited-members': True}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
#html_static_path = ['_static']
html_favicon = 'https://dratio.io/favicon/favicon.ico'
html_logo = "https://dratio.io/branding/logo.png"
html_theme_options = {
    'logo_only': True,
    # 'style_nav_header_background': '#FDFDFD',
}
