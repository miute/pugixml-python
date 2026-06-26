# Changelog

## Unreleased

### Changed

- Bump pugixml from 1.15 to 1.16 ([#200])
  - Add `pugixml.pugi.XMLNode.ensure_attribute(name: str)`
  - Add `pugixml.pugi.XMLNode.ensure_child(name: str)`
- Bump pybind11 from 2.13.6 to 3.0.4 ([#141], [#159], [#198])

### Added

- Add support for Python 3.14 ([#154])

### Removed

- Drop support for CMake older than 3.15 ([#130])
- Drop support for Python 3.9 ([#153])
- Drop support for macOS older than 14 ([#201])

## 0.7.0 - 2025-01-13

### Changed

- Bump pugixml from 1.14 to 1.15 ([#109])
- Bump pybind11 from 2.12.0 to 2.13.6

### Added

- Add support for Python 3.13

### Removed

- Drop support for Python 3.8

## 0.6.0 - 2024-04-30

Maintenance release.

### Changed

- Bump pybind11 from 2.11.1 to 2.12.0

### Removed

- Drop support for macOS 11
- Drop support for Python 3.7

### Fixed

- Fix problems with macOS builds ([#82], [#85])

## 0.5.0 - 2023-10-04

### Changed

- Bump pugixml from 1.13 to 1.14
  - Add `pugixml.pugi.PARSE_MERGE_PCDATA`
  - Add `pugixml.pugi.XMLAttribute.set_name(name: str, size: int)`
  - Add `pugixml.pugi.XMLNode.set_name(name: str, size: int)`
- Bump pybind11 from 2.10.1 to 2.11.1

### Added

- Add support for Python 3.12

### Fixed

- Remove unnecessary length check
  - `pugixml.pugi.XMLAttribute.set_value(value: str, size: int)`
  - `pugixml.pugi.XMLNode.set_value(value: str, size: int)`
  - `pugixml.pugi.XMLText.set(value: str, size: int)`

## 0.4.0 - 2022-11-11

### Changed

- Bump pugixml from [521b2cd](https://github.com/zeux/pugixml/tree/521b2cd854f8d65f173107d056d2b9c6d49b6563) to 1.13
  - Add `pugixml.pugi.XMLAttribute.set_value(value: str, size: int)`
  - Add `pugixml.pugi.XMLNode.set_value(value: str, size: int)`
  - Add `pugixml.pugi.XMLText.set(value: str, size: int)`
- Bump pybind11 from 2.10.0 to 2.10.1
- Improve type checking

## 0.3.0 - 2022-10-03

### Changed

- Bump pugixml from 1.12 to [521b2cd](https://github.com/zeux/pugixml/tree/521b2cd854f8d65f173107d056d2b9c6d49b6563)
- Bump pybind11 from 2.9.2 to 2.10.0
- Add `pugixml.pugi.StringWriter.__len__()`
- Change the parameters of `pugixml.pugi.StringWriter.getvalue()` to `getvalue(encoding: str = 'utf-8', errors: str = 'strict')`
- Update docstring

### Added

- Add support for Python 3.11
- Add `pugixml.pugi.BytesWriter` class
- Add `pugixml.pugi.FileWriter` class
- Add `pugixml.pugi.limits` submodule

### Fixed

- Fix `pugixml.pugi.PrintWriter` to raise an exception when encoding fails

## 0.2.0 - 2022-06-10

### Changed

- Add `pugixml.pugi.XMLAttribute.internal_object()`
- Add `pugixml.pugi.XMLAttribute.__init__(p: XMLAttributeStruct)`
- Add `pugixml.pugi.XMLNode.internal_object()`
- Add `pugixml.pugi.XMLNode.__init__(p: XMLNodeStruct)`

### Added

- Add `pugixml.pugi.XMLAttributeStruct` class
- Add `pugixml.pugi.XMLNodeStruct` class
- Add `pugixml.pugi.XMLAttributeIterator` class
- Add `pugixml.pugi.XMLNodeIterator` class
- Add `pugixml.pugi.XMLNamedNodeIterator` class

### Fixed

- Change the return type of `pugixml.pugi.XMLNode.attributes()`: `list[XMLAttribute]` → `XMLAttributeIterator`
- Change the return type of `pugixml.pugi.XMLNode.children()`: `list[XMLNode]` → `XMLNodeIterator`
- Change the return type of `pugixml.pugi.XMLNode.children(name: str)`: `list[XMLNode]` → `XMLNamedNodeIterator`

## 0.1.0 - 2022-05-27

Initial release.

[#82]: https://github.com/miute/pugixml-python/pull/82
[#85]: https://github.com/miute/pugixml-python/pull/85
[#109]: https://github.com/miute/pugixml-python/pull/109
[#130]: https://github.com/miute/pugixml-python/pull/130
[#141]: https://github.com/miute/pugixml-python/pull/141
[#153]: https://github.com/miute/pugixml-python/pull/153
[#154]: https://github.com/miute/pugixml-python/pull/154
[#159]: https://github.com/miute/pugixml-python/pull/159
[#198]: https://github.com/miute/pugixml-python/pull/198
[#200]: https://github.com/miute/pugixml-python/pull/200
[#201]: https://github.com/miute/pugixml-python/pull/201
