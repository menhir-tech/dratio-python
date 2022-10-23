# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


import os
import sys
import pkg_resources

sys.path.append(os.path.abspath('../..'))
sys.path.append(os.path.abspath('..'))
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

try:
    release = pkg_resources.get_distribution('dratio').version
except pkg_resources.DistributionNotFound:
    print('To build the documentation, the distribution information of '
          'dratio has to be available.  Either install the package '
          'into your development environment or run "setup.py develop" '
          'to setup the metadata. A virtualenv is recommended. ')
    sys.exit(1)

project = 'dratio'
copyright = '2022, dratio.io'
author = 'dratio.io'


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

autodoc_mock_imports = ["geopandas"]

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
