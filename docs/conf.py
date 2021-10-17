# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
import os
import pathlib as pl
import sys
import time
import toml


ROOT = pl.Path(os.path.dirname(os.path.abspath(__file__))).parent
sys.path.insert(0, os.path.abspath(ROOT))


# -- Project information -----------------------------------------------------
base_file = ROOT / "pyproject.toml"
with open(file=base_file, mode="r") as f:
    conf = toml.loads(f.read())
    project     = conf['tool']['poetry']['name']
    author      = ','.join(conf['tool']['poetry']['authors'])
    version     = conf['tool']['poetry']['version']
    release     = conf['tool']['poetry']['version']
    copyright   = f'{time.localtime().tm_year}, {project}'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx_rtd_theme'
    ]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# If true, `todo` and `todoList` produce output
todo_include_todos = True

# Define the class documentation source.
autoclass_content = 'both'


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
