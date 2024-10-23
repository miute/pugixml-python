# Changelog

## WIP

- **New**
  - Add support for Python 3.13
- **Changed**
  - Update pybind11 from 2.12.0 to 2.13.6
- **Removed**
  - Drop support for Python 3.8

## v0.6.0 (2024-04-30)

Maintenance release.

- **Changed**
  - Update pybind11 from 2.11.1 to 2.12.0
- **Fixed**
  - Fix problems with macOS builds ([#82](https://github.com/miute/pugixml-python/pull/82), [#85](https://github.com/miute/pugixml-python/pull/85))
- **Removed**
  - Drop support for macOS 11
  - Drop support for Python 3.7

## v0.5.0 (2023-10-04)

- **New**
  - Add support for Python 3.12
  - Add support for pugixml 1.14
    - Add `pugixml.pugi.PARSE_MERGE_PCDATA`
    - Add `pugixml.pugi.XMLAttribute.set_name(name: str, size: int)`
    - Add `pugixml.pugi.XMLNode.set_name(name: str, size: int)`
- **Changed**
  - Update pybind11 from 2.10.1 to 2.11.1
- **Fixed**
  - Remove unnecessary length check:
    - `pugixml.pugi.XMLAttribute.set_value(value: str, size: int)`
    - `pugixml.pugi.XMLNode.set_value(value: str, size: int)`
    - `pugixml.pugi.XMLText.set(value: str, size: int)`

## v0.4.0 (2022-11-11)

- **New**
  - Add support for pugixml 1.13
    - Add `pugixml.pugi.XMLAttribute.set_value(value: str, size: int)`
    - Add `pugixml.pugi.XMLNode.set_value(value: str, size: int)`
    - Add `pugixml.pugi.XMLText.set(value: str, size: int)`
- **Changed**
  - Update pybind11 from 2.10.0 to 2.10.1
- **Improved**
  - Improve type checking

## v0.3.0 (2022-10-03)

- **New**
  - Add support for Python 3.11
  - Add `pugixml.pugi.BytesWriter` class
  - Add `pugixml.pugi.FileWriter` class
  - Add `pugixml.pugi.limits` submodule
- **Added**
  - Add `pugixml.pugi.StringWriter.__len__()`
- **Changed**
  - Update pugixml from 1.12 to [521b2cd](https://github.com/zeux/pugixml/tree/521b2cd854f8d65f173107d056d2b9c6d49b6563)
  - Update pybind11 from 2.9.2 to 2.10.0
- **Fixed**
  - Fix `pugixml.pugi.PrintWriter` to raise an exception when encoding fails
- **Improved**
  - Update docstring
  - Change arguments of `pugixml.pugi.StringWriter.getvalue()` → `getvalue(encoding: str = 'utf-8', errors: str = 'strict')`

## v0.2.0 (2022-06-10)

- **New**
  - Add `pugixml.pugi.XMLAttributeStruct` class
  - Add `pugixml.pugi.XMLNodeStruct` class
  - Add `pugixml.pugi.XMLAttributeIterator` class
  - Add `pugixml.pugi.XMLNodeIterator` class
  - Add `pugixml.pugi.XMLNamedNodeIterator` class
- **Added**
  - Add `pugixml.pugi.XMLAttribute.internal_object()`
  - Add `pugixml.pugi.XMLAttribute.__init__(p: XMLAttributeStruct)`
  - Add `pugixml.pugi.XMLNode.internal_object()`
  - Add `pugixml.pugi.XMLNode.__init__(p: XMLNodeStruct)`
- **Fixed**
  - Change return type of `pugixml.pugi.XMLNode.attributes() -> List[XMLAttribute]` → `XMLAttributeIterator`
  - Change return type of `pugixml.pugi.XMLNode.children() -> List[XMLNode]` → `XMLNodeIterator`
  - Change return type of `pugixml.pugi.XMLNode.children(name: str) -> List[XMLNode]` → `XMLNamedNodeIterator`

## v0.1.0 (2022-05-27)

Initial release.
