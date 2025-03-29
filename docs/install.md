# Installation

## Installing a package from PyPI

```{code-block} bash
pip install pugixml
```

## Installing a package from source

- Requirements:
  - C++17 compatible compiler (see [supported compilers](https://github.com/pybind/pybind11#supported-compilers))
  - [CMake](https://cmake.org/) ≥ 3.15

- Installing a package from PyPI:

  ```{code-block} bash
  pip install --no-binary=:all: pugixml
  ```

- Installing the development version from the git repository:

  ```{code-block} bash
  pip install git+https://github.com/miute/pugixml-python.git
  ```
