# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import sys
from importlib.metadata import metadata
from pathlib import Path

path = str((Path(__file__).parent / ".." / "src").resolve())
if path not in sys.path:
    sys.path.append(path)
del path


# -- Project information -----------------------------------------------------

md = metadata("pugixml")
project = "pugixml-python"
author = md["Author-email"]
author = author[: author.index("<")].strip()
copyright = f"2022, {author}"  # noqa: A001
version = release = md["Version"]


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.extlinks",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
    "myst_parser",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_css_files = [
    "css/custom.css",
]

html_title = f"{project} {version}"

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

extlinks = {"pugixml": ("https://pugixml.org/docs/%s", None)}

napoleon_use_admonition_for_examples = True
# napoleon_use_rtype = False

copybutton_prompt_is_regexp = True
copybutton_prompt_text = (
    r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
)

autodoc_default_options = {
    "show-inheritance": True,
    "undoc-members": True,
    "special-members": True,
    "private-members": True,
    "exclude-members": "__annotations__, __module__, __repr__, _pybind11_conduit_v1_",
}

suppress_warnings = [
    "autosummary.import_cycle",
]
