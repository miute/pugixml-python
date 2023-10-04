pugixml.pugi
============

.. currentmodule:: pugixml.pugi

.. rubric:: Attributes

Encodings
---------

These flags determine the encoding of input/output data for XML document.

.. seealso::

   :meth:`XMLDocument.load_buffer`,
   :meth:`XMLDocument.load_file`,
   :meth:`XMLDocument.save`,
   :meth:`XMLDocument.save_file`,
   :meth:`XMLNode.append_buffer`,
   :meth:`XMLNode.print`

.. autoattribute:: pugixml.pugi.ENCODING_AUTO

   Auto-detect input encoding using BOM or ``‘<’`` / ``‘<?’`` detection; use UTF8 if BOM is not found.

.. autoattribute:: pugixml.pugi.ENCODING_LATIN1

   ISO-8859-1 encoding (also known as Latin-1).

.. autoattribute:: pugixml.pugi.ENCODING_UTF16

   UTF16 with native endianness.

.. autoattribute:: pugixml.pugi.ENCODING_UTF16_BE

   Big-endian UTF16.

.. autoattribute:: pugixml.pugi.ENCODING_UTF16_LE

   Little-endian UTF16.

.. autoattribute:: pugixml.pugi.ENCODING_UTF32

   UTF32 with native endianness.

.. autoattribute:: pugixml.pugi.ENCODING_UTF32_BE

   Big-endian UTF32.

.. autoattribute:: pugixml.pugi.ENCODING_UTF32_LE

   Little-endian UTF32.

.. autoattribute:: pugixml.pugi.ENCODING_UTF8

   UTF8 encoding.

.. autoattribute:: pugixml.pugi.ENCODING_WCHAR

   The same encoding ``wchar_t`` has (either UTF16 or UTF32).

Output Options
--------------

These flags control the contents of the resulting tree for all saving functions.

.. note::

   This is a bitmask that customizes the output format:
   to enable a flag, use ``mask | flag``; to disable a flag, use ``mask & ~flag``.

.. seealso::

   :meth:`XMLDocument.save`,
   :meth:`XMLDocument.save_file`,
   :meth:`XMLNode.print`

.. autoattribute:: pugixml.pugi.FORMAT_ATTRIBUTE_SINGLE_QUOTE

   Use U+0027 (') instead of U+0022 (") for enclosing attribute values.
   This flag is off by default.

.. autoattribute:: pugixml.pugi.FORMAT_DEFAULT

   The default set of formatting flags.
   Nodes are indented depending on their depth in DOM tree, a default declaration is output if document has none.

.. autoattribute:: pugixml.pugi.FORMAT_INDENT

   Indent the nodes that are written to output stream with as many indentation strings as deep the node is in DOM tree.
   This flag is on by default.

.. autoattribute:: pugixml.pugi.FORMAT_INDENT_ATTRIBUTES

   Write every attribute on a new line with appropriate indentation. This flag is off by default.

.. autoattribute:: pugixml.pugi.FORMAT_NO_DECLARATION

   Omit default XML declaration even if there is no declaration in the document. This flag is off by default.

.. autoattribute:: pugixml.pugi.FORMAT_NO_EMPTY_ELEMENT_TAGS

   Don't output empty element tags, instead writing an explicit start and end tag even if there are no children.
   This flag is off by default.

.. autoattribute:: pugixml.pugi.FORMAT_NO_ESCAPES

   Don't escape attribute values and PCDATA contents. This flag is off by default.

.. autoattribute:: pugixml.pugi.FORMAT_RAW

   Use raw output mode (no indentation and no line breaks are written). This flag is off by default.

.. autoattribute:: pugixml.pugi.FORMAT_SAVE_FILE_TEXT

   Open file using text mode in :meth:`XMLDocument.save_file`.
   This enables special character (i.e. new-line) conversions on some systems.
   This flag is off by default.

.. autoattribute:: pugixml.pugi.FORMAT_SKIP_CONTROL_CHARS

   Skip characters belonging to range [0, 32) instead of "&#xNN;" encoding. This flag is off by default.

.. autoattribute:: pugixml.pugi.FORMAT_WRITE_BOM

   Write encoding-specific BOM to the output stream. This flag is off by default.

Node Types
----------

.. autoattribute:: pugixml.pugi.NODE_CDATA

   Character data, i.e. ``‘<![CDATA[text]]>’``

.. autoattribute:: pugixml.pugi.NODE_COMMENT

   Comment tag, i.e. ``‘<!– text –>’``

.. autoattribute:: pugixml.pugi.NODE_DECLARATION

   Document declaration, i.e. ``‘<?xml version=”1.0”?>’``

.. autoattribute:: pugixml.pugi.NODE_DOCTYPE

   Document type declaration, i.e. ``‘<!DOCTYPE doc>’``

.. autoattribute:: pugixml.pugi.NODE_DOCUMENT

   A document tree’s absolute root.

.. autoattribute:: pugixml.pugi.NODE_ELEMENT

   Element tag, i.e. ``‘<node/>’``

.. autoattribute:: pugixml.pugi.NODE_NULL

   Empty (null) node handle.

.. autoattribute:: pugixml.pugi.NODE_PCDATA

   Plain character data, i.e. ``‘text’``

.. autoattribute:: pugixml.pugi.NODE_PI

   Processing instruction, i.e. ``‘<?name?>’``

Parsing Options
---------------

These flags control the contents of the resulting tree for all loading functions.

.. note::

   This is a bitmask that customizes the parsing process:
   to enable a flag, use ``mask | flag``; to disable a flag, use ``mask & ~flag``.

.. seealso::

   :meth:`XMLDocument.load_buffer`,
   :meth:`XMLDocument.load_file`,
   :meth:`XMLDocument.load_string`,
   :meth:`XMLNode.append_buffer`

.. autoattribute:: pugixml.pugi.PARSE_CDATA

   This flag determines if CDATA sections (:attr:`NODE_CDATA`) are added to the DOM tree. This flag is on by default.

.. autoattribute:: pugixml.pugi.PARSE_COMMENTS

   This flag determines if comments (:attr:`NODE_COMMENT`) are added to the DOM tree. This flag is off by default.

.. autoattribute:: pugixml.pugi.PARSE_DECLARATION

   This flag determines if document declaration (:attr:`NODE_DECLARATION`) is added to the DOM tree.
   This flag is off by default.

.. autoattribute:: pugixml.pugi.PARSE_DEFAULT

   The default parsing mode.
   Elements, PCDATA and CDATA sections are added to the DOM tree, character/reference entities are expanded,
   End-of-Line characters are normalized, attribute values are normalized using CDATA normalization rules.

.. autoattribute:: pugixml.pugi.PARSE_DOCTYPE

   This flag determines if document type declaration (:attr:`NODE_DOCTYPE`) is added to the DOM tree. This flag is off by default.

.. autoattribute:: pugixml.pugi.PARSE_EMBED_PCDATA

   This flag determines if plain character data is be stored in the parent element's value.
   This significantly changes the structure of the document;
   this flag is only recommended for parsing documents with many PCDATA nodes in memory-constrained environments.
   This flag is off by default.

.. autoattribute:: pugixml.pugi.PARSE_EOL

   This flag determines if EOL characters are normalized (converted to #xA) during parsing. This flag is on by default.

.. autoattribute:: pugixml.pugi.PARSE_ESCAPES

   This flag determines if character and entity references are expanded during parsing. This flag is on by default.

.. autoattribute:: pugixml.pugi.PARSE_FRAGMENT

   This flag determines if plain character data that does not have a parent node is added to the DOM tree,
   and if an empty document is a valid document. This flag is off by default.

.. autoattribute:: pugixml.pugi.PARSE_FULL

   The full parsing mode.
   Nodes of all types are added to the DOM tree, character/reference entities are expanded,
   End-of-Line characters are normalized, attribute values are normalized using CDATA normalization rules.

.. autoattribute:: pugixml.pugi.PARSE_MERGE_PCDATA

	This flag determines whether determines whether the the two PCDATA should be merged or not, if no intermediatory data are parsed in the document.
	This flag is off by default.

.. autoattribute:: pugixml.pugi.PARSE_MINIMAL

   Minimal parsing mode (equivalent to turning all other flags off).
   Only elements and PCDATA sections are added to the DOM tree, no text conversions are performed.

.. autoattribute:: pugixml.pugi.PARSE_PI

   This flag determines if processing instructions (:attr:`NODE_PI`) are added to the DOM tree. This flag is off by default.

.. autoattribute:: pugixml.pugi.PARSE_TRIM_PCDATA

   This flag determines if leading and trailing whitespace is to be removed from plain character data.
   This flag is off by default.

.. autoattribute:: pugixml.pugi.PARSE_WCONV_ATTRIBUTE

   This flag determines if attribute values are normalized using CDATA normalization rules during parsing.
   This flag is on by default.

.. autoattribute:: pugixml.pugi.PARSE_WNORM_ATTRIBUTE

   This flag determines if attribute values are normalized using NMTOKENS normalization rules during parsing.
   This flag is off by default.

.. autoattribute:: pugixml.pugi.PARSE_WS_PCDATA

   This flag determines if plain character data (:attr:`NODE_PCDATA`) that consist only of whitespace are added to the DOM tree.
   This flag is off by default; turning it on usually results in slower parsing and more memory consumption.

.. autoattribute:: pugixml.pugi.PARSE_WS_PCDATA_SINGLE

   This flag determines if plain character data (:attr:`NODE_PCDATA`) that is the only child of the parent node and that consists only
   of whitespace is added to the DOM tree.
   This flag is off by default; turning it on may result in slower parsing and more memory consumption.

Parsing Status
--------------

Parsing status, returned as part of :class:`XMLParseResult` object.

.. autoattribute:: pugixml.pugi.STATUS_APPEND_INVALID_ROOT

   Unable to append nodes since root type is not :attr:`NODE_ELEMENT` or :attr:`NODE_DOCUMENT`
   (exclusive to :meth:`XMLNode.append_buffer`).

.. autoattribute:: pugixml.pugi.STATUS_BAD_ATTRIBUTE

   Parsing error occurred while parsing element attribute.

.. autoattribute:: pugixml.pugi.STATUS_BAD_CDATA

   Parsing error occurred while parsing CDATA section.

.. autoattribute:: pugixml.pugi.STATUS_BAD_COMMENT

   Parsing error occurred while parsing comment.

.. autoattribute:: pugixml.pugi.STATUS_BAD_DOCTYPE

   Parsing error occurred while parsing document type declaration.

.. autoattribute:: pugixml.pugi.STATUS_BAD_END_ELEMENT

   Parsing error occurred while parsing end element tag.

.. autoattribute:: pugixml.pugi.STATUS_BAD_PCDATA

   Parsing error occurred while parsing PCDATA section.

.. autoattribute:: pugixml.pugi.STATUS_BAD_PI

   Parsing error occurred while parsing document declaration/processing instruction.

.. autoattribute:: pugixml.pugi.STATUS_BAD_START_ELEMENT

   Parsing error occurred while parsing start element tag.

.. autoattribute:: pugixml.pugi.STATUS_END_ELEMENT_MISMATCH

   There was a mismatch of start-end tags
   (closing tag had incorrect name, some tag was not closed or there was an excessive closing tag).

.. autoattribute:: pugixml.pugi.STATUS_FILE_NOT_FOUND

   File was not found during :meth:`XMLDocument.load_file`.

.. autoattribute:: pugixml.pugi.STATUS_INTERNAL_ERROR

   Internal error occurred.

.. autoattribute:: pugixml.pugi.STATUS_IO_ERROR

   Error reading from file/stream.

.. autoattribute:: pugixml.pugi.STATUS_NO_DOCUMENT_ELEMENT

   Parsing resulted in a document without element nodes.

.. autoattribute:: pugixml.pugi.STATUS_OK

   No error.

.. autoattribute:: pugixml.pugi.STATUS_OUT_OF_MEMORY

   Could not allocate memory.

.. autoattribute:: pugixml.pugi.STATUS_UNRECOGNIZED_TAG

   Parser could not determine tag type.

XPath Query Return Type
-----------------------

.. autoattribute:: pugixml.pugi.XPATH_TYPE_BOOLEAN

   Boolean.

.. autoattribute:: pugixml.pugi.XPATH_TYPE_NODE_SET

   Node set (:class:`XPathNodeSet`).

.. autoattribute:: pugixml.pugi.XPATH_TYPE_NONE

   Unknown type (query failed to compile).

.. autoattribute:: pugixml.pugi.XPATH_TYPE_NUMBER

   Number.

.. autoattribute:: pugixml.pugi.XPATH_TYPE_STRING

   String.

Misc.
-----

.. autoattribute:: pugixml.pugi.PUGIXML_VERSION

   An integer literal representing the version of ``pugixml``; major * 1000 + minor * 10 + patch.

pugixml.pugi.limits
===================

.. automodule:: pugixml.pugi.limits

.. rubric:: Attributes

.. autoattribute:: pugixml.pugi.limits.DBL_MAX

   Maximum value of type ``double`` in C/C++.

.. autoattribute:: pugixml.pugi.limits.DBL_MIN

   Minimum value of type ``double`` in C/C++.

.. autoattribute:: pugixml.pugi.limits.FLT_MAX

   Maximum value of type ``float`` in C/C++.

.. autoattribute:: pugixml.pugi.limits.FLT_MIN

   Minimum value of type ``float`` in C/C++.

.. autoattribute:: pugixml.pugi.limits.INT_MAX

   Maximum value of type ``int`` in C/C++.

.. autoattribute:: pugixml.pugi.limits.INT_MIN

   Minimum value of type ``int`` in C/C++.

.. autoattribute:: pugixml.pugi.limits.LLONG_MAX

   Maximum value of type ``long long`` in C/C++.

.. autoattribute:: pugixml.pugi.limits.LLONG_MIN

   Minimum value of type ``long long`` in C/C++.

.. autoattribute:: pugixml.pugi.limits.UINT_MAX

   Maximum value of type ``unsigned int`` in C/C++.

.. autoattribute:: pugixml.pugi.limits.ULLONG_MAX

   Maximum value of type ``unsigned long long`` in C/C++.
