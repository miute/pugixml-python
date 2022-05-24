import sys

from setuptools import setup

sys.path.append("")
from _build import build  # noqa

setup_kwargs = {}  # type: ignore
build(setup_kwargs)
setup(**setup_kwargs)
