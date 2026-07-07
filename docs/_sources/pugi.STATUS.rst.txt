Parsing Status
==============

.. currentmodule:: pugixml.pugi

Parsing status, returned as part of :class:`XMLParseResult` object.

.. seealso::

   :class:`XMLParseStatus`

.. rubric:: Attributes

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
