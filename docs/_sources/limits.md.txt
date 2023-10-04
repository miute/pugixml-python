# Limitations

## Unsupported APIs

The following APIs are not implemented.

### Structures/Classes

- pugi::xml_writer_file - Use {class}`pugixml.pugi.FileWriter` instead.
- pugi::xml_writer_stream
- pugi::xpath_exception

### Methods

- General
  - Move constructors
  - Assignment operators
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
  - print(std::basic_ostream, ...)
  - select_single_node(...)

## Changes

### Naming Conventions

Class and constant names are renamed based on [PEP 8](https://peps.python.org/pep-0008/#naming-conventions).

- Class Names: Use the CapWords style.
- Constants: Use the UPPER_CASE_WITH_UNDERSCORES style.
