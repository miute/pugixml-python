# Configuration file for the Sphinx documentation builder.

# -- Path setup --------------------------------------------------------------

import enum
import inspect
import sys
from importlib.metadata import metadata
from pathlib import Path

path = str((Path(__file__).parent.parent / "src").resolve())
if path not in sys.path:
    sys.path.insert(0, path)


# -- Project information -----------------------------------------------------

md = metadata("pugixml")
project = "pugixml-python"
author = md["Author-email"]
author = author[: author.index("<")].strip()
copyright = f"2022, {author}"  # noqa: A001
version = release = md["Version"]


# -- General configuration ---------------------------------------------------

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


# -- Options for sphinx.ext.autodoc ------------------------------------------

exclude_members = [
    "__annotate_func__",
    "__annotations__",
    "__annotations_cache__",
    "__doc__",
    "__entries",
    "__format__",
    "__module__",
    "__new__",
    "__pybind11_native_enum__",
    "__repr__",
    "__weakref__",
    "_pybind11_conduit_v1_",
]

autodoc_class_signature = "separated"
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "private-members": True,
    "special-members": True,
    "inherited-members": False,
    "exclude-members": ",".join(exclude_members),
    "member-order": "groupwise",
    "show-inheritance": True,
    "class-doc-from": "class",
}
suppress_warnings = [
    "autosummary.import_cycle",
]


# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

extlinks = {"pugixml": ("https://pugixml.org/docs/%s", None)}

copybutton_prompt_is_regexp = True
copybutton_prompt_text = (
    r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
)


def process_docstring(app, obj_type, name, obj, options, lines):  # noqa: ANN001, ANN201, PLR0913
    _ = app, options
    if obj_type == "class":
        items = inspect.getmembers(obj, lambda x: isinstance(x, enum.Enum))
        if len(items) > 0:
            items = sorted(items, key=lambda x: x[1])
            lines.append(".. rubric:: Attributes")
            lines.append("")
            for member_name, member in items:
                lines.append(f".. autodata:: {name}.{member_name}")
                lines.append(f"   :annotation: = {member.value}")
                lines.append("")

        items = inspect.getmembers(obj, lambda x: isinstance(x, property))
        if len(items) > 0:
            lines.append(".. rubric:: Properties")
            lines.append("")
            for member_name, _ in items:
                lines.append(f".. autoattribute:: {member_name}")
                lines.append("")


def skip_member(app, obj_type, name, obj, skip, options):  # noqa: ANN001, ANN201, PLR0913
    _ = app, name, skip, options
    match obj_type:
        case "class":
            if isinstance(obj, enum.Enum) or not callable(obj):
                # Skip enum members and class attributes / properties.
                return True
    return None


def setup(app):  # noqa: ANN001, ANN201
    app.connect("autodoc-process-docstring", process_docstring)
    app.connect("autodoc-skip-member", skip_member)
