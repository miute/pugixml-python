# Python bindings for pugixml

[![PyPI](https://img.shields.io/pypi/v/pugixml)](https://pypi.org/project/pugixml/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pugixml)](https://pypi.org/project/pugixml/)
[![PyPI - License](https://img.shields.io/pypi/l/pugixml)](https://pypi.org/project/pugixml/)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/miute/pugixml-python/main.svg)](https://results.pre-commit.ci/latest/github/miute/pugixml-python/main)
[![tests](https://github.com/miute/pugixml-python/actions/workflows/tests.yml/badge.svg)](https://github.com/miute/pugixml-python/actions/workflows/tests.yml)
[![build](https://github.com/miute/pugixml-python/actions/workflows/build.yml/badge.svg)](https://github.com/miute/pugixml-python/actions/workflows/build.yml)

[pugixml](http://pugixml.org/) is a light-weight C++ XML processing library. It features:

> - DOM-like interface with rich traversal/modification capabilities
> - [Extremely fast](https://pugixml.org/benchmark.html) non-validating XML parser which constructs the DOM tree from > an XML file/buffer
> - XPath 1.0 implementation for complex data-driven tree queries
> - Full Unicode support with Unicode interface variants and automatic encoding conversions

## Documentation

- pugixml-python
  - [API Reference](https://miute.github.io/pugixml-python/)
- pugixml
  - [Quick start guide](https://pugixml.org/docs/quickstart.html)
  - [Reference manual](https://pugixml.org/docs/manual.html)

## Installation

### Installing a package from PyPI

```bash
pip install pugixml
```

### Building a package from source

- Requirements:
  - C++17 compatible compiler (see [supported compilers](https://github.com/pybind/pybind11#supported-platforms--compilers))
  - [CMake](https://cmake.org/) ≥ 3.15

- Installing a package from PyPI:

  ```bash
  pip install --no-binary=:all: pugixml
  ```

- Installing the development version from the git repository:

  ```bash
  pip install git+https://github.com/miute/pugixml-python.git
  ```

## License

- **pugixml-python** is licensed under the [MIT License](https://github.com/miute/pugixml-python/blob/main/LICENSE).
- **pugixml** is licensed under the [MIT License](https://github.com/zeux/pugixml/blob/master/LICENSE.md).
