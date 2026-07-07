Output Options
==============

.. currentmodule:: pugixml.pugi

These flags control the contents of the resulting tree for all saving functions.

.. note::

   This is a bitmask that customizes the output format:
   to enable a flag, use ``mask | flag``; to disable a flag, use ``mask & ~flag``.

.. seealso::

   :meth:`XMLDocument.save`
   :meth:`XMLDocument.save_file`
   :meth:`XMLNode.print`

.. rubric:: Attributes

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
