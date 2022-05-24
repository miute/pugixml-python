# Python bindings for pugixml

[pugixml](http://pugixml.org/) is a light-weight C++ XML processing library. It features:

- DOM-like interface with rich traversal/modification capabilities
- [Extremely fast](https://pugixml.org/benchmark.html) non-validating XML parser which constructs the DOM tree from an XML file/buffer
- XPath 1.0 implementation for complex data-driven tree queries
- Full Unicode support with Unicode interface variants and automatic encoding conversions

## Documentation

- pugixml-python
  - [API Reference](https://miute.github.io/pugixml-python/)
- pugixml
  - [Quick-start guide](https://pugixml.org/docs/quickstart.html)
  - [Reference manual](https://pugixml.org/docs/manual.html)

## Example

Loading XML document from file:

```python
from pugixml import pugi
doc = pugi.XMLDocument()
result = doc.load_file('xgconsole.xml')
if not result:
    print('parse error: status=%r description=%r' % (result.status, result.description()))
```

Searching for nodes/attributes with predicates:

```python
tools = doc.child('Profile').child('Tools')

# Find child via predicate (looks for direct children only)
node = tools.find_child(lambda x: x.attribute('AllowRemote').as_bool())
print(node.attribute('Filename').value())

# Find node via predicate (looks for all descendants in depth-first order)
node = doc.find_node(lambda x: x.attribute('AllowRemote').as_bool())
print(node.attribute('Filename').value())

# Find attribute via predicate
attr = tools.last_child().find_attribute(lambda x: x.name() == 'AllowRemote')
print(attr.value())
```

Selecting nodes via XPath expression:

```python
tools = doc.select_nodes('/Profile/Tools/Tool[@AllowRemote="true" and @DeriveCaptionFrom="lastparam"]')
for tool in tools:
    print(tool.node().attribute('Filename').value())
```

Using query objects and variables:

```python
varset = pugi.XPathVariableSet()
var = varset.add('remote', pugi.XPATH_TYPE_BOOLEAN)
query_remote_tools = pugi.XPathQuery('/Profile/Tools/Tool[@AllowRemote = string($remote)]', varset)

var.set(True)
tools_remote = query_remote_tools.evaluate_node_set(doc)
for tool in tools_remote:
    tool.node().print(pugi.PrintWriter())

var.set(False)
tools_local = query_remote_tools.evaluate_node_set(doc)
for tool in tools_local:
    tool.node().print(pugi.PrintWriter())
```

## Installation

### Installing a package from PyPI

```bash
pip install pugixml
```

### Building a package from source

- Requirements:
  - C++17 compatible compiler (see [supported compilers](https://github.com/pybind/pybind11#supported-compilers))
  - [CMake](https://cmake.org/) ≥ 3.12

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
