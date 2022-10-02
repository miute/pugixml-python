# CHANGELOG

## v0.3.0 / 2022-10-03

- New
  - Add support for Python 3.11
  - Add pugixml.pugi.BytesWriter class
  - Add pugixml.pugi.FileWriter class
- Added
  - Add pugixml.pugi.limits submodule
  - Add pugixml.pugi.StringWriter.\_\_len__()
- Fixed
  - Fix pugixml.pugi.PrintWriter to raise an exception when encoding fails
- Improved
  - Update pugixml to 521b2cd854f8d65f173107d056d2b9c6d49b6563
  - Update pybind11 to v2.10.0
  - Update docstring
  - Change args of pugixml.pugi.StringWriter.getvalue() → getvalue(encoding: str = 'utf-8', errors: str = 'strict')

## v0.2.0 / 2022-06-10

- New
  - Add pugixml.pugi.XMLAttributeStruct class
  - Add pugixml.pugi.XMLNodeStruct class
  - Add pugixml.pugi.XMLAttributeIterator class
  - Add pugixml.pugi.XMLNodeIterator class
  - Add pugixml.pugi.XMLNamedNodeIterator class
- Added
  - Add pugixml.pugi.XMLAttribute.internal_object()
  - Add pugixml.pugi.XMLAttribute.\_\_init__(p: XMLAttributeStruct)
  - Add pugixml.pugi.XMLNode.internal_object()
  - Add pugixml.pugi.XMLNode.\_\_init__(p: XMLNodeStruct)
- Fixed
  - Change return type of pugixml.pugi.XMLNode.attributes() -> List[XMLAttribute] → XMLAttributeIterator
  - Change return type of pugixml.pugi.XMLNode.children() -> List[XMLNode] → XMLNodeIterator
  - Change return type of pugixml.pugi.XMLNode.children(name: str) -> List[XMLNode] → XMLNamedNodeIterator

## v0.1.0 / 2022-05-27

Initial release.
