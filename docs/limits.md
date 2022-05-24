# Limitations

## Unsupported APIs

The following APIs are not implemented.

### Structures/Classes

- pugi::xml_attribute_iterator
- pugi::xml_attribute_struct
- pugi::xml_named_node_iterator
- pugi::xml_node_iterator
- pugi::xml_node_struct
- pugi::xml_object_range
- pugi::xml_writer_file
- pugi::xml_writer_stream
- pugi::xpath_exception

### Methods

- General
  - Move constructors
  - Assignment operators
- pugi::xml_attribute
  - internal_object()
  - set_value(float, int)
  - set_value(float)
  - set_value(int)
  - set_value(long)
  - set_value(unsigned int)
  - set_value(unsigned long)
- pugi::xml_document
  - load(std::basic_istream, ...)
  - load_buffer_inplace_own(...)
  - load_buffer_inplace(...)
  - save(std::basic_ostream, ...)
- pugi::xml_node
  - attributes_begin()
  - attributes_end()
  - begin()
  - end()
  - internal_object()
  - print(std::basic_ostream, ...)
  - select_single_node(...)
- pugi::xml_text
  - set(float, int)
  - set(float)
  - set(int)
  - set(long)
  - set(unsigned int)
  - set(unsigned long)

## Changes

### Naming Conventions

Class and constant names are renamed based on [PEP 8](https://peps.python.org/pep-0008/#naming-conventions).

- Class Names: Use the CapWords style.
- Constants: Use the UPPER_CASE_WITH_UNDERSCORES style.

### API

- pugi.XMLNode (pugi::xml_node)
  - attributes() returns a list of attributes instead of an iterator.
  - children() returns a list of nodes instead of an iterator.
  - children(str) returns a list of nodes instead of an iterator.
