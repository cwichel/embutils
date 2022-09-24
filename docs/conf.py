# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation: https://www.sphinx-doc.org/en/master/usage/configuration.html
#
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# -------------------------------------

# Built-in
import pathlib as pl
import sys
import time

# External
import toml


# -->> Definitions <<------------------
# Get repository path
PATH_REPOSITORY = pl.Path(__file__).absolute().parents[1]

# Add repository to system path
sys.path.insert(0, str(PATH_REPOSITORY))


# -->> Project <<----------------------
# Extract project information
with (PATH_REPOSITORY / "pyproject.toml").open(mode="r") as file:
    source = toml.loads(file.read())
    author = ", ".join(source["tool"]["poetry"]["authors"])
    project = source["tool"]["poetry"]["name"]
    release = source["tool"]["poetry"]["version"]
    version = source["tool"]["poetry"]["version"]
    project_copyright = f"{time.localtime().tm_year}, {project}"


# -->> General <<----------------------
# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_rtd_theme",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files. These patterns
# also affect html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# If true, `todo` and `todoList` produce output
todo_include_todos = True

# Define the class documentation source.
autoclass_content = "both"


# -->> HTML <<-------------------------
# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
