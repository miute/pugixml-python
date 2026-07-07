Encodings
=========

.. currentmodule:: pugixml.pugi

These flags determine the encoding of input/output data for XML document.

.. seealso::

   :class:`XMLEncoding`
   :meth:`XMLDocument.load_buffer`
   :meth:`XMLDocument.load_file`
   :meth:`XMLDocument.save`
   :meth:`XMLDocument.save_file`
   :meth:`XMLNode.append_buffer`
   :meth:`XMLNode.print`

.. rubric:: Attributes

.. autoattribute:: pugixml.pugi.ENCODING_AUTO

   Auto-detect input encoding using BOM or ‘<’ / ‘<?’ detection; use UTF8 if BOM is not found.

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
