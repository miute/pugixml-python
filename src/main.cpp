#include <filesystem>
#include <fstream>
#include <iomanip>
#include <limits>
#include <map>
#include <memory>
#include <optional>
#include <pugixml.hpp>
#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl/filesystem.h>
#include <sstream>

#ifndef MODULE_NAME
#error MODULE_NAME was not defined.
#endif // MODULE_NAME

namespace fs = std::filesystem;
namespace py = pybind11;

using namespace pugi;

static std::map<int, const char *> _xml_node_type_to_string{
    {node_null, "NODE_NULL"},       {node_document, "NODE_DOCUMENT"},
    {node_element, "NODE_ELEMENT"}, {node_pcdata, "NODE_PCDATA"},
    {node_cdata, "NODE_CDATA"},     {node_comment, "NODE_COMMENT"},
    {node_pi, "NODE_PI"},           {node_declaration, "NODE_DECLARATION"},
    {node_doctype, "NODE_DOCTYPE"},
};

static std::map<int, const char *> _xml_encoding_to_string{
    {encoding_auto, "ENCODING_AUTO"},         {encoding_utf8, "ENCODING_UTF8"},
    {encoding_utf16_le, "ENCODING_UTF16_LE"}, {encoding_utf16_be, "ENCODING_UTF16_BE"},
    {encoding_utf16, "ENCODING_UTF16"},       {encoding_utf32_le, "ENCODING_UTF32_LE"},
    {encoding_utf32_be, "ENCODING_UTF32_BE"}, {encoding_utf32, "ENCODING_UTF32"},
    {encoding_wchar, "ENCODING_WCHAR"},       {encoding_latin1, "ENCODING_LATIN1"},
};

static std::map<int, const char *> _xml_parse_status_to_string{
    {status_ok, "STATUS_OK"},
    {status_file_not_found, "STATUS_FILE_NOT_FOUND"},
    {status_io_error, "STATUS_IO_ERROR"},
    {status_out_of_memory, "STATUS_OUT_OF_MEMORY"},
    {status_internal_error, "STATUS_INTERNAL_ERROR"},
    {status_unrecognized_tag, "STATUS_UNRECOGNIZED_TAG"},
    {status_bad_pi, "STATUS_BAD_PI"},
    {status_bad_comment, "STATUS_BAD_COMMENT"},
    {status_bad_cdata, "STATUS_BAD_CDATA"},
    {status_bad_doctype, "STATUS_BAD_DOCTYPE"},
    {status_bad_pcdata, "STATUS_BAD_PCDATA"},
    {status_bad_start_element, "STATUS_BAD_START_ELEMENT"},
    {status_bad_attribute, "STATUS_BAD_ATTRIBUTE"},
    {status_bad_end_element, "STATUS_BAD_END_ELEMENT"},
    {status_end_element_mismatch, "STATUS_END_ELEMENT_MISMATCH"},
    {status_append_invalid_root, "STATUS_APPEND_INVALID_ROOT"},
    {status_no_document_element, "STATUS_NO_DOCUMENT_ELEMENT"},
};

struct XMLAttributeStruct {
  xml_attribute_struct *p_;
  XMLAttributeStruct(xml_attribute_struct *p) : p_(p) {}
  operator xml_attribute_struct *() { return p_; }
};

struct XMLNodeStruct {
  xml_node_struct *p_;
  XMLNodeStruct(xml_node_struct *p) : p_(p) {}
  operator xml_node_struct *() const { return p_; }
};

// xml_object_range<iterator> -> std::vector<vartype>
template <typename iterator, typename vartype> struct Iterator {
  std::vector<vartype> items_;
  size_t index_;

  Iterator(const xml_object_range<iterator> &it) : items_(it.begin(), it.end()), index_(0) {}

  auto get(const py::slice &slice) {
    size_t start = 0, stop = 0, step = 0, slice_length = 0;
    if (!slice.compute(size(), &start, &stop, &step, &slice_length)) {
      throw py::error_already_set();
    }
    auto result = new std::vector<vartype>(slice_length);
    for (size_t n = 0; n < slice_length; ++n) {
      (*result)[n] = items_[start];
      start += step;
    }
    return result;
  }

  vartype &operator[](long long n) {
    if (n < 0) {
      n += size();
    }
    if (n < 0 || static_cast<size_t>(n) >= size()) {
      throw py::index_error("index out of range: " + std::to_string(n));
    }
    return items_[n];
  }

  vartype &next() {
    if (index_ >= size()) {
      throw py::stop_iteration();
    }
    return items_[index_++];
  }

  void reset() { index_ = 0; }

  auto size() const { return items_.size(); }
};

class PyXMLWriter : public xml_writer {
public:
  using xml_writer::xml_writer;

  void write(const void *data, size_t size) override {
    PYBIND11_OVERRIDE_PURE(void, xml_writer, write, py::bytes(static_cast<const char *>(data), size), size);
  }
};

class PyXMLTreeWalker : public xml_tree_walker {
public:
  using xml_tree_walker::xml_tree_walker;

  bool begin(xml_node &node) override { PYBIND11_OVERRIDE(bool, xml_tree_walker, begin, node); }

  bool for_each(xml_node &node) override { PYBIND11_OVERRIDE_PURE(bool, xml_tree_walker, for_each, node); }

  bool end(xml_node &node) override { PYBIND11_OVERRIDE(bool, xml_tree_walker, end, node); }

  using xml_tree_walker::depth;
};

PYBIND11_MODULE(MODULE_NAME, m) {
  py::options options;

  //
  // pugixml.pugi module
  //
  m.doc() = "A light-weight, simple and fast XML parser for C++ with XPath support.";

  m.attr("PUGIXML_VERSION") = PUGIXML_VERSION;

  // Parsing options
  m.attr("PARSE_MINIMAL") = parse_minimal;
  m.attr("PARSE_PI") = parse_pi;
  m.attr("PARSE_COMMENTS") = parse_comments;
  m.attr("PARSE_CDATA") = parse_cdata;
  m.attr("PARSE_WS_PCDATA") = parse_ws_pcdata;
  m.attr("PARSE_ESCAPES") = parse_escapes;
  m.attr("PARSE_EOL") = parse_eol;
  m.attr("PARSE_WCONV_ATTRIBUTE") = parse_wconv_attribute;
  m.attr("PARSE_WNORM_ATTRIBUTE") = parse_wnorm_attribute;
  m.attr("PARSE_DECLARATION") = parse_declaration;
  m.attr("PARSE_DOCTYPE") = parse_doctype;
  m.attr("PARSE_WS_PCDATA_SINGLE") = parse_ws_pcdata_single;
  m.attr("PARSE_TRIM_PCDATA") = parse_trim_pcdata;
  m.attr("PARSE_FRAGMENT") = parse_fragment;
  m.attr("PARSE_EMBED_PCDATA") = parse_embed_pcdata;
  m.attr("PARSE_DEFAULT") = parse_default;
  m.attr("PARSE_FULL") = parse_full;

  // Formatting flags
  m.attr("FORMAT_INDENT") = format_indent;
  m.attr("FORMAT_WRITE_BOM") = format_write_bom;
  m.attr("FORMAT_RAW") = format_raw;
  m.attr("FORMAT_NO_DECLARATION") = format_no_declaration;
  m.attr("FORMAT_NO_ESCAPES") = format_no_escapes;
  m.attr("FORMAT_SAVE_FILE_TEXT") = format_save_file_text;
  m.attr("FORMAT_INDENT_ATTRIBUTES") = format_indent_attributes;
  m.attr("FORMAT_NO_EMPTY_ELEMENT_TAGS") = format_no_empty_element_tags;
  m.attr("FORMAT_SKIP_CONTROL_CHARS") = format_skip_control_chars;
  m.attr("FORMAT_ATTRIBUTE_SINGLE_QUOTE") = format_attribute_single_quote;
  m.attr("FORMAT_DEFAULT") = format_default;

  m.attr("DEFAULT_DOUBLE_PRECISION") = default_double_precision;
  m.attr("DEFAULT_FLOAT_PRECISION") = default_float_precision;

  py::enum_<xml_node_type>(m, "XMLNodeType", "Tree node types.")
      .value("NODE_NULL", node_null, "Empty (null) node handle.")
      .value("NODE_DOCUMENT", node_document, "A document tree's absolute root.")
      .value("NODE_ELEMENT", node_element, "Element tag, i.e. '<node/>'")
      .value("NODE_PCDATA", node_pcdata, "Plain character data, i.e. 'text'")
      .value("NODE_CDATA", node_cdata, "Character data, i.e. '<![CDATA[text]]>'")
      .value("NODE_COMMENT", node_comment, "Comment tag, i.e. '<!-- text -->'")
      .value("NODE_PI", node_pi, "Processing instruction, i.e. '<?name?>'")
      .value("NODE_DECLARATION", node_declaration, "Document declaration, i.e. '<?xml version=\"1.0\"?>'")
      .value("NODE_DOCTYPE", node_doctype, "Document type declaration, i.e. '<!DOCTYPE doc>'")
      .export_values();

  py::enum_<xml_encoding>(m, "XMLEncoding", "These flags determine the encoding of input/output data for XML document.")
      .value("ENCODING_AUTO", encoding_auto,
             "Auto-detect input encoding using BOM or '<' / '<?' detection; use UTF8 if BOM is not found.")
      .value("ENCODING_UTF8", encoding_utf8, "UTF8 encoding.")
      .value("ENCODING_UTF16_LE", encoding_utf16_le, "Little-endian UTF16.")
      .value("ENCODING_UTF16_BE", encoding_utf16_be, "Big-endian UTF16.")
      .value("ENCODING_UTF16", encoding_utf16, "UTF16 with native endianness.")
      .value("ENCODING_UTF32_LE", encoding_utf32_le, "Little-endian UTF32.")
      .value("ENCODING_UTF32_BE", encoding_utf32_be, "Big-endian UTF32.")
      .value("ENCODING_UTF32", encoding_utf32, "UTF32 with native endianness.")
      .value("ENCODING_WCHAR", encoding_wchar, "The same encoding wchar_t has (either UTF16 or UTF32).")
      .value("ENCODING_LATIN1", encoding_latin1, "ISO-8859-1 encoding (also known as Latin-1).")
      .export_values();

  py::enum_<xml_parse_status>(m, "XMLParseStatus",
                              "Parsing status, returned as part of :class:`XMLParseResult` object.")
      .value("STATUS_OK", status_ok, "No error.")
      .value("STATUS_FILE_NOT_FOUND", status_file_not_found, "File was not found during XMLDocument.load_file().")
      .value("STATUS_IO_ERROR", status_io_error, "Error reading from file/stream.")
      .value("STATUS_OUT_OF_MEMORY", status_out_of_memory, "Could not allocate memory.")
      .value("STATUS_INTERNAL_ERROR", status_internal_error, "Internal error occurred.")
      .value("STATUS_UNRECOGNIZED_TAG", status_unrecognized_tag, "Parser could not determine tag type.")
      .value("STATUS_BAD_PI", status_bad_pi,
             "Parsing error occurred while parsing document declaration/processing instruction.")
      .value("STATUS_BAD_COMMENT", status_bad_comment, "Parsing error occurred while parsing comment.")
      .value("STATUS_BAD_CDATA", status_bad_cdata, "Parsing error occurred while parsing CDATA section.")
      .value("STATUS_BAD_DOCTYPE", status_bad_doctype,
             "Parsing error occurred while parsing document type declaration.")
      .value("STATUS_BAD_PCDATA", status_bad_pcdata, "Parsing error occurred while parsing PCDATA section.")
      .value("STATUS_BAD_START_ELEMENT", status_bad_start_element,
             "Parsing error occurred while parsing start element tag.")
      .value("STATUS_BAD_ATTRIBUTE", status_bad_attribute, "Parsing error occurred while parsing element attribute.")
      .value("STATUS_BAD_END_ELEMENT", status_bad_end_element, "Parsing error occurred while parsing end element tag.")
      .value("STATUS_END_ELEMENT_MISMATCH", status_end_element_mismatch,
             "There was a mismatch of start-end tags (closing tag had incorrect name, some tag was not closed or there "
             "was an excessive closing tag).")
      .value("STATUS_APPEND_INVALID_ROOT", status_append_invalid_root,
             "Unable to append nodes since root type is not NODE_ELEMENT or NODE_DOCUMENT (exclusive to "
             "XMLNode.append_buffer()).")
      .value("STATUS_NO_DOCUMENT_ELEMENT", status_no_document_element,
             "Parsing resulted in a document without element nodes.")
      .export_values();

  py::enum_<xpath_value_type>(m, "XPathValueType", "XPath query return type.")
      .value("XPATH_TYPE_NONE", xpath_type_none, "Unknown type (query failed to compile).")
      .value("XPATH_TYPE_NODE_SET", xpath_type_node_set, "Node set (XPathNodeSet).")
      .value("XPATH_TYPE_NUMBER", xpath_type_number, "Number.")
      .value("XPATH_TYPE_STRING", xpath_type_string, "String.")
      .value("XPATH_TYPE_BOOLEAN", xpath_type_boolean, "Boolean.")
      .export_values();

  py::class_<XMLAttributeStruct> atst(m, "XMLAttributeStruct", R"doc(
      The internal object of the attribute.

      See Also:
          :meth:`XMLAttribute.__init__`, :meth:`XMLAttribute.internal_object`
      )doc");

  py::class_<XMLNodeStruct> nst(m, "XMLNodeStruct", R"doc(
      The internal object of the node.

      See Also:
          :meth:`XMLNode.__init__`, :meth:`XMLNode.internal_object`
      )doc");

  // pugi::xml_object_range<...>
  // pugi::xml_attribute_iterator
  // pugi::xml_node_iterator
  // pugi::xml_named_node_iterator
  py::class_<Iterator<xml_attribute_iterator, xml_attribute>> atit(m, "XMLAttributeIterator", R"doc(
      A collection of attributes.

      See Also:
          :meth:`XMLNode.attributes`
      )doc");

  py::class_<Iterator<xml_node_iterator, xml_node>> nit(m, "XMLNodeIterator", R"doc(
      A collection of nodes.

      See Also:
          :meth:`XMLNode.children`
      )doc");

  py::class_<Iterator<xml_named_node_iterator, xml_node>> nnit(m, "XMLNamedNodeIterator", R"doc(
      A collection of nodes specified by name.

      See Also:
          :meth:`XMLNode.children`
      )doc");

  py::class_<xml_writer, PyXMLWriter> xwt(m, "XMLWriter", R"doc(
      Writer interface for node printing.

      See :pugixml:`documentation <manual.html#saving.writer>` for details.

      Important:
          - Do not use ``XMLWriter`` directly.
          - You must override :meth:`.write` method in derived class.

      See Also:
          :class:`BytesWriter`, :class:`FileWriter`, :class:`PrintWriter`, :class:`StringWriter`,
          :meth:`XMLDocument.save`, :meth:`XMLNode.print`
      )doc");

  py::class_<xml_attribute> attr(m, "XMLAttribute", "A light-weight handle for manipulating attributes in DOM tree.");

  py::class_<xml_node> node(m, "XMLNode", "A light-weight handle for manipulating nodes in DOM tree.");

  py::class_<xml_text> text(m, "XMLText", R"doc(
      A helper for working with text inside PCDATA nodes.

      Examples:
          >>> from pugixml import pugi
          >>> doc = pugi.XMLDocument()
          >>> doc.load_string('<node/>')
          >>> node = doc.child('node')
          >>> a = node.append_child('a').append_child(pugi.NODE_CDATA)
          >>> a.text().set('foo')
          >>> b = node.append_child(pugi.NODE_PCDATA)
          >>> b.text().set('bar')
          >>> c = node.append_child(pugi.NODE_ELEMENT)
          >>> c.set_name('c')
          >>> c.text().set('baz')
          >>> node.print(pugi.PrintWriter(), indent=' ')
          <node>
           <a><![CDATA[foo]]></a>bar<c>baz</c>
          </node>
      )doc");

  py::class_<xml_tree_walker, PyXMLTreeWalker> trwk(m, "XMLTreeWalker", R"doc(
      Abstract tree walker class.

      Important:
          - Do not use ``XMLTreeWalker`` directly.
          - You must override any or all of :meth:`.begin`, :meth:`.end`,
            and :meth:`.for_each` methods in derived class.

      See Also:
          :meth:`XMLNode.traverse`
      )doc");

  py::class_<xml_parse_result> pr(m, "XMLParseResult", "Parsing result.");

  py::class_<xml_document, xml_node> xdoc(m, "XMLDocument", "Document class (DOM tree root).");

  py::class_<xpath_parse_result> xppr(m, "XPathParseResult", "XPath parsing result.");

  py::class_<xpath_variable> xpv(m, "XPathVariable", R"doc(
      A single XPath variable.

      See Also:
          :class:`XPathVariableSet`
      )doc");

  py::class_<xpath_variable_set> xpvs(m, "XPathVariableSet", R"doc(
      A set of XPath variables.

      See Also:
          :class:`XPathQuery`, :class:`XPathVariable`
      )doc");

  py::class_<xpath_query> xpq(m, "XPathQuery", R"doc(
      A compiled XPath expression object.

      See Also:
          :meth:`XMLNode.select_node`, :meth:`XMLNode.select_nodes`, :class:`XPathVariableSet`

      Examples:
          >>> from pugixml import pugi
          >>> doc = pugi.XMLDocument()
          >>> doc.load_string('<node attr="3"/>')
          >>> q = pugi.XPathQuery('node/@attr')
          >>> q.evaluate_boolean(doc)
          True
          >>> q.evaluate_number(doc)
          3.0
          >>> q.evaluate_string(doc)
          '3'
          >>> n = q.evaluate_node(doc)
          >>> bool(n)
          True
          >>> n.attribute().name()
          'attr'
          >>> ns = q.evaluate_node_set(doc)
          >>> bool(ns)
          True
          >>> ns.size()
          1
          >>> ns[0].attribute().name()
          'attr'
      )doc");

  // pugi::xpath_exception

  py::class_<xpath_node> xpn(m, "XPathNode", "XPath node class (either :class:`XMLNode` or :class:`XMLAttribute`.)");

  py::class_<xpath_node_set> xpns(m, "XPathNodeSet", "A fixed-size collection of XPath nodes.");

  //
  // pugi::xml_attribute_struct
  //
  atst.def(
      "__eq__", [](const XMLAttributeStruct &self, const XMLAttributeStruct &other) { return self.p_ == other.p_; },
      py::is_operator(), py::arg("other"),
      R"doc(
      Return self == other.

      Args:
          other (XMLAttributeStruct): The internal object of the attribute to compare.

      Returns:
          bool: The result of comparing pointers of the internal objects.
      )doc");

  atst.def(
      "__ne__", [](const XMLAttributeStruct &self, const XMLAttributeStruct &other) { return self.p_ != other.p_; },
      py::is_operator(), py::arg("other"),
      R"doc(
      Return self != other.

      Args:
          other (XMLAttributeStruct): The internal object of the attribute to compare.

      Returns:
          bool: The result of comparing pointers of the internal objects.
      )doc");

  //
  // pugi::xml_node_struct
  //
  nst.def(
      "__eq__", [](const XMLNodeStruct &self, const XMLNodeStruct &other) { return self.p_ == other.p_; },
      py::is_operator(), py::arg("other"),
      R"doc(
      Return self == other.

      Args:
          other (XMLNodeStruct): The internal object of the node to compare.

      Returns:
          bool: The result of comparing pointers of the internal objects.
      )doc");

  nst.def(
      "__ne__", [](const XMLNodeStruct &self, const XMLNodeStruct &other) { return self.p_ != other.p_; },
      py::is_operator(), py::arg("other"),
      R"doc(
      Return self != other.

      Args:
          other (XMLNodeStruct): The internal object of the node to compare.

      Returns:
          bool: The result of comparing pointers of the internal objects.
      )doc");

  //
  // pugi::xml_object_range<xml_attribute_iterator>
  // pugi::xml_attribute_iterator
  //
  atit.def("__getitem__", &Iterator<xml_attribute_iterator, xml_attribute>::operator[], py::arg("index"),
           "\tReturn the attribute at the specified index from the collection.")
      .def("__getitem__", &Iterator<xml_attribute_iterator, xml_attribute>::get, py::arg("slice"),
           "\tReturn a list of attributes at the specified :obj:`slice` from the collection.\n\n"
           "Args:\n"
           "    index (int): An index to specify position.\n"
           "    slice (slice): A slice object to specify range.\n\n"
           "Returns:\n"
           "    typing.Union[XMLAttribute, typing.List[XMLAttribute]]: The attribute(s) at the specified index/slice "
           "from the collection.");

  atit.def(
      "__iter__",
      [](Iterator<xml_attribute_iterator, xml_attribute> &self) -> Iterator<xml_attribute_iterator, xml_attribute> & {
        self.reset();
        return self;
      },
      R"doc(
      Return itself.

      Returns:
          XMLAttributeIterator: ``self``.
      )doc");

  atit.def("__len__", &Iterator<xml_attribute_iterator, xml_attribute>::size,
           R"doc(
           Return the collection size.

           Returns:
               int: The collection size.
           )doc");

  atit.def("__next__", &Iterator<xml_attribute_iterator, xml_attribute>::next,
           R"doc(
           Return the next attribute from the collection.

           Returns:
               XMLAttribute: The next attribute from the collection.
           )doc");

  //
  // pugi::xml_object_range<xml_node_iterator>
  // pugi::xml_node_iterator
  //
  nit.def("__getitem__", &Iterator<xml_node_iterator, xml_node>::operator[], py::arg("index"),
          "\tReturn the node at the specified index from the collection.")
      .def("__getitem__", &Iterator<xml_node_iterator, xml_node>::get, py::arg("slice"),
           "\tReturn a list of nodes at the specified :obj:`slice` from the collection.\n\n"
           "Args:\n"
           "    index (int): An index to specify position.\n"
           "    slice (slice): A slice object to specify range.\n\n"
           "Returns:\n"
           "    typing.Union[XMLNode, typing.List[XMLNode]]: The node(s) at the specified index/slice from "
           "the collection.");

  nit.def(
      "__iter__",
      [](Iterator<xml_node_iterator, xml_node> &self) -> Iterator<xml_node_iterator, xml_node> & {
        self.reset();
        return self;
      },
      R"doc(
      Return itself.

      Returns:
          XMLNodeIterator: ``self``.
      )doc");

  nit.def("__len__", &Iterator<xml_node_iterator, xml_node>::size,
          R"doc(
           Return the collection size.

           Returns:
               int: The collection size.
           )doc");

  nit.def("__next__", &Iterator<xml_node_iterator, xml_node>::next,
          R"doc(
          Return the next node from the collection.

          Returns:
              XMLNode: The next node from the collection.
          )doc");

  //
  // pugi::xml_object_range<xml_named_node_iterator>
  // pugi::xml_named_node_iterator
  //
  nnit.def("__getitem__", &Iterator<xml_named_node_iterator, xml_node>::operator[], py::arg("index"),
           "\tReturn the node at the specified index from the collection.")
      .def("__getitem__", &Iterator<xml_named_node_iterator, xml_node>::get, py::arg("slice"),
           "\tReturn a list of nodes at the specified :obj:`slice` from the collection.\n\n"
           "Args:\n"
           "    index (int): An index to specify position.\n"
           "    slice (slice): A slice object to specify range.\n\n"
           "Returns:\n"
           "    typing.Union[XMLNode, typing.List[XMLNode]]: The node(s) at the specified index/slice from "
           "the collection.");

  nnit.def(
      "__iter__",
      [](Iterator<xml_named_node_iterator, xml_node> &self) -> Iterator<xml_named_node_iterator, xml_node> & {
        self.reset();
        return self;
      },
      R"doc(
      Return itself.

      Returns:
          XMLNamedNodeIterator: ``self``.
      )doc");

  nnit.def("__len__", &Iterator<xml_named_node_iterator, xml_node>::size,
           R"doc(
           Return the collection size.

           Returns:
               int: The collection size.
           )doc");

  nnit.def("__next__", &Iterator<xml_named_node_iterator, xml_node>::next,
           R"doc(
           Return the next node from the collection.

           Returns:
               XMLNode: The next node from collection.
           )doc");

  //
  // pugi::xml_writer
  //
  xwt.def(py::init<>(), "Initialize ``XMLWriter``.");

  options.disable_function_signatures();
  xwt.def("write", &xml_writer::write, py::arg("data"), py::arg("size"),
          R"doc(
          write(self: pugixml.pugi.XMLWriter, data: bytes, size: int) -> None

          Write memory chunk into stream/file/whatever.

          Args:
              data (bytes): The chunk of data to write.
              size (int): The data size in bytes.
          )doc");
  options.enable_function_signatures();

  //
  // pugi::xml_attribute
  //
  attr.def(py::init<>(), "\tInitialize ``XMLAttribute`` as an empty attribute.")
      .def(py::init([](XMLAttributeStruct &p) { return std::make_unique<xml_attribute>(p); }), py::keep_alive<1, 2>(),
           py::arg("p"),
           "\tInitialize ``XMLAttribute`` with the internal object.\n\n"
           "Args:\n"
           "    p (XMLAttributeStruct): The internal object of the attribute to shallow copy.");

  attr.def(
      "__bool__", [](const xml_attribute &self) -> bool { return self; },
      R"doc(
      Determine if this attribute is not empty.

      Returns:
          bool: :obj:`True` if attribute is not empty, :obj:`False` otherwise.
      )doc");

  attr.def(
      "__eq__", [](const xml_attribute &self, const xml_attribute &other) { return self == other; }, py::is_operator(),
      py::arg("other"),
      R"doc(
      Return self == other.

      Args:
          other (XMLAttribute): The attribute to compare.

      Returns:
          bool: The result of comparing pointers of internal objects.
      )doc");

  attr.def(
      "__ge__", [](const xml_attribute &self, const xml_attribute &other) { return self >= other; }, py::is_operator(),
      py::arg("other"),
      R"doc(
      Return self >= other.

      Args:
          other (XMLAttribute): The attribute to compare.

      Returns:
          bool: The result of comparing pointers of internal objects.
      )doc");

  attr.def(
      "__gt__", [](const xml_attribute &self, const xml_attribute &other) { return self > other; }, py::is_operator(),
      py::arg("other"),
      R"doc(
      Return self > other.

      Args:
          other (XMLAttribute): The attribute to compare.

      Returns:
          bool: The result of comparing pointers of internal objects.
      )doc");

  attr.def("__hash__", &xml_attribute::hash_value,
           R"doc(
           Return the hash value (unique for handles to the same object).

           This is equivalent to :meth:`.hash_value`.

           Returns:
               int: The hash value.
           )doc");

  attr.def(
      "__le__", [](const xml_attribute &self, const xml_attribute &other) { return self <= other; }, py::is_operator(),
      py::arg("other"),
      R"doc(
      Return self <= other.

      Args:
          other (XMLAttribute): The attribute to compare.

      Returns:
          bool: The result of comparing pointers of internal objects.
      )doc");

  attr.def(
      "__lt__", [](const xml_attribute &self, const xml_attribute &other) { return self < other; }, py::is_operator(),
      py::arg("other"),
      R"doc(
      Return self < other.

      Args:
          other (XMLAttribute): The attribute to compare.

      Returns:
          bool: The result of comparing pointers of internal objects.
      )doc");

  attr.def(
      "__ne__", [](const xml_attribute &self, const xml_attribute &other) { return self != other; }, py::is_operator(),
      py::arg("other"),
      R"doc(
      Return self != other.

      Args:
          other (XMLAttribute): The attribute to compare.

      Returns:
          bool: The result of comparing pointers of internal objects.
      )doc");

  attr.def("__repr__", [](const xml_attribute &self) {
    std::stringstream ss;
    ss << "<XMLAttribute";

    const auto hash = self.hash_value();
    ss << " hash=0";
    if (hash) {
      ss << "x" << std::hex << std::uppercase << hash;
    }

    const auto name = self.name();
    if (!self.empty() && strlen(name)) {
      ss << " name=" << std::quoted(name, '\'');
    }

    ss << ">";
    return ss.str();
  });

  attr.def("empty", &xml_attribute::empty,
           R"doc(
           Determine if this attribute is empty.

           Returns:
               bool: :obj:`True` if attribute is empty, :obj:`False` otherwise.
           )doc");

  attr.def("name", &xml_attribute::name,
           R"doc(
           Return the attribute name.

           Returns:
               str: The attribute name, or the empty string if attribute is empty.
           )doc");

  attr.def("value", &xml_attribute::value,
           R"doc(
           Return the attribute value.

           Returns:
               str: The attribute value, or the empty string if attribute is empty.

           See Also:
               :meth:`.as_string`
           )doc");

  attr.def("as_string", &xml_attribute::as_string, py::arg("default") = PUGIXML_TEXT(""),
           R"doc(
           Return the attribute value.

           Args:
               default (str): The default value.

           Returns:
               str: The attribute value, or the default value if attribute is empty.
           )doc");

  attr.def("as_int", &xml_attribute::as_int, py::arg("default") = 0,
           R"doc(
           Return the attribute value as a number [INT_MIN, INT_MAX].

           Args:
               default (int): The default value.

           Returns:
               int: The attribute value as a number, or the default value if conversion did not succeed or attribute is empty.
           )doc");

  attr.def("as_uint", &xml_attribute::as_uint, py::arg("default") = 0,
           R"doc(
           Return the attribute value as a number [0, UINT_MAX].

           Args:
               default (int): The default value.

           Returns:
               int: The attribute value as a number, or the default value if conversion did not succeed or attribute is empty.
           )doc");

  attr.def("as_double", &xml_attribute::as_double, py::arg("default") = 0,
           R"doc(
           Return the attribute value as a number [DBL_MIN, DBL_MAX].

           Args:
               default (float): The default value.

           Returns:
               float: The attribute value as a number, or the default value if conversion did not succeed or attribute is empty.
           )doc");

  attr.def("as_float", &xml_attribute::as_float, py::arg("default") = 0,
           R"doc(
           Return the attribute value as a number [FLT_MIN, FLT_MAX].

           Args:
               default (float): The default value.

           Returns:
               float: The attribute value as a number, or the default value if conversion did not succeed or attribute is empty.
           )doc");

  attr.def("as_llong", &xml_attribute::as_llong, py::arg("default") = 0,
           R"doc(
           Return the attribute value as a number [LLONG_MIN, LLONG_MAX].

           Args:
               default (int): The default value.

           Returns:
               int: The attribute value as a number, or the default value if conversion did not succeed or attribute is empty.
           )doc");

  attr.def("as_ullong", &xml_attribute::as_ullong, py::arg("default") = 0,
           R"doc(
           Return the attribute value as a number [0, ULLONG_MAX].

           Args:
               default (int): The default value.

           Returns:
               int: The attribute value as a number, or the default value if conversion did not succeed or attribute is empty.
           )doc");

  attr.def("as_bool", &xml_attribute::as_bool, py::arg("default") = false,
           R"doc(
           Return the attribute value as a boolean.

           Args:
               default (bool): The default value.

           Returns:
               bool: The attribute value as a boolean (returns :obj:`True` if first character is in '1tTyY' set),
               or the default value if conversion did not succeed or attribute is empty.
           )doc");

  attr.def("set_name", &xml_attribute::set_name, py::arg("name"),
           R"doc(
           Set the attribute name.

           Args:
               name (str): The attribute name to set.

           Returns:
               bool: :obj:`False` if attribute is empty or there is not enough memory.
           )doc");

  attr.def("set_value", py::overload_cast<const char_t *>(&xml_attribute::set_value), py::arg("value"),
           "\tSet the attribute value.")
      .def("set_value", py::overload_cast<bool>(&xml_attribute::set_value), py::arg("value"),
           "\tSet the attribute value as a boolean (\"true\" or \"false\").")
      .def("set_value", py::overload_cast<double>(&xml_attribute::set_value), py::arg("value").noconvert(),
           "\tSet the attribute value as a number [DBL_MIN, DBL_MAX].")
      .def("set_value", py::overload_cast<double, int>(&xml_attribute::set_value), py::arg("value"),
           py::arg("precision"),
           "\tSet the attribute value as a number with the specified precision [DBL_MIN, DBL_MAX].")
      .def("set_value", py::overload_cast<long long>(&xml_attribute::set_value), py::arg("value"),
           "\tSet the attribute value as a number [LLONG_MIN, LLONG_MAX].")
      .def("set_value", py::overload_cast<unsigned long long>(&xml_attribute::set_value), py::arg("value"),
           "\tSet the attribute value as a number [0, ULLONG_MAX].\n\n"
           "Args:\n"
           "    value (typing.Union[str, bool, float, int]): The attribute value to set.\n"
           "    precision (int): The precision for the attribute value as a floating point number.\n\n"
           "Returns:\n"
           "    bool: :obj:`False` if attribute is empty or there is not enough memory.");

  attr.def("next_attribute", &xml_attribute::next_attribute,
           R"doc(
           Return the next attribute in the list of attributes of the parent node.

           Returns:
               XMLAttribute: The next sibling of this attribute, or empty attribute if not exists.
           )doc");

  attr.def("previous_attribute", &xml_attribute::previous_attribute,
           R"doc(
           Return the previous attribute in the list of attributes of the parent node.

           Returns:
               XMLAttribute: The previous sibling of this attribute, or empty attribute if not exists.
           )doc");

  attr.def("hash_value", &xml_attribute::hash_value,
           R"doc(
           Return the hash value (unique for handles to the same object).

           Returns:
               int: The hash value.
           )doc");

  attr.def(
      "internal_object",
      [](const xml_attribute &self) { return std::make_unique<XMLAttributeStruct>(self.internal_object()); },
      R"doc(
      Return the internal object.

      Returns:
          XMLAttributeStruct: The internal object of this attribute.
      )doc");

  //
  // pugi::xml_node
  //
  node.def(py::init<>(), "\tInitialize ``XMLNode`` as an empty node.")
      .def(py::init([](XMLNodeStruct &p) { return std::make_unique<xml_node>(p); }), py::keep_alive<1, 2>(),
           py::arg("p"),
           "\tInitialize ``XMLNode`` with the internal object.\n\n"
           "Args:\n"
           "    p (XMLNodeStruct): The internal object of the node to shallow copy.");

  node.def(
      "__bool__", [](const xml_node &self) -> bool { return self; },
      R"doc(
      Determine if this node is not empty.

      Returns:
          bool: :obj:`True` if node is not empty, :obj:`False` otherwise.
      )doc");

  node.def(
      "__eq__", [](const xml_node &self, const xml_node &other) { return self == other; }, py::is_operator(),
      py::arg("other"),
      R"doc(
      Return self == other.

      Args:
          other (XMLNode): The node to compare.

      Returns:
          bool: The result of comparing pointers of internal objects.
      )doc");

  node.def(
      "__ge__", [](const xml_node &self, const xml_node &other) { return self >= other; }, py::is_operator(),
      py::arg("other"),
      R"doc(
      Return self >= other.

      Args:
          other (XMLNode): The node to compare.

      Returns:
          bool: The result of comparing pointers of internal objects.
      )doc");

  node.def(
      "__gt__", [](const xml_node &self, const xml_node &other) { return self > other; }, py::is_operator(),
      py::arg("other"),
      R"doc(
      Return self > other.

      Args:
          other (XMLNode): The node to compare.

      Returns:
          bool: The result of comparing pointers of internal objects.
      )doc");

  node.def("__hash__", &xml_node::hash_value,
           R"doc(
           Return the hash value (unique for handles to the same object).

           This is equivalent to :meth:`.hash_value`.

           Returns:
               int: The hash value.
           )doc");

  node.def(
      "__le__", [](const xml_node &self, const xml_node &other) { return self <= other; }, py::is_operator(),
      py::arg("other"),
      R"doc(
      Return self <= other.

      Args:
          other (XMLNode): The node to compare.

      Returns:
          bool: The result of comparing pointers of internal objects.
      )doc");

  node.def(
      "__lt__", [](const xml_node &self, const xml_node &other) { return self < other; }, py::is_operator(),
      py::arg("other"),
      R"doc(
      Return self < other.

      Args:
          other (XMLNode): The node to compare.

      Returns:
          bool: The result of comparing pointers of internal objects.
      )doc");

  node.def(
      "__ne__", [](const xml_node &self, const xml_node &other) { return self != other; }, py::is_operator(),
      py::arg("other"),
      R"doc(
      Return self != other.

      Args:
          other (XMLNode): The node to compare.

      Returns:
          bool: The result of comparing pointers of internal objects.
      )doc");

  node.def("__repr__", [](const xml_node &self) {
    std::stringstream ss;
    ss << "<XMLNode";

    const auto hash = self.hash_value();
    ss << " hash=0";
    if (hash) {
      ss << "x" << std::hex << std::uppercase << hash;
    }

    const auto node_type = self.type();
    ss << " type=";
    if (_xml_node_type_to_string.count(node_type)) {
      ss << _xml_node_type_to_string[node_type];
    } else {
      ss << node_type;
    }

    const auto node_name = self.name();
    if (!self.empty() && strlen(node_name)) {
      ss << " name=" << std::quoted(node_name, '\'');
    }

    ss << ">";
    return ss.str();
  });

  node.def("empty", &xml_node::empty,
           R"doc(
           Determine if this node is empty.

           Returns:
               bool: :obj:`True` if node is empty, :obj:`False` otherwise.
           )doc");

  node.def("type", &xml_node::type,
           R"doc(
           Return the node type.

           Returns:
               XMLNodeType: The node type.
           )doc");

  node.def("name", &xml_node::name,
           R"doc(
           Return the node name.

           Returns:
               str: The node name, or the empty string if node is empty or it has no name.
           )doc");

  node.def("value", &xml_node::value,
           R"doc(
           Return the node value.

           Returns:
               str: The node value, or the empty string if node is empty or it has no value.

           Note:
               For <node>text</node> :meth:`.value` does not return "text"! Use :meth:`.child_value` or :meth:`.text` methods to access text inside nodes.
           )doc");

  node.def("first_attribute", &xml_node::first_attribute,
           R"doc(
           Return the first attribute in the list of attributes for this node.

           Returns:
               XMLAttribute: The attribute found, or empty attribute if not exists.

           See Also:
               :meth:`.last_attribute`
           )doc");

  node.def("last_attribute", &xml_node::last_attribute,
           R"doc(
           Return the last attribute in the list of attributes for this node.

           Returns:
               XMLAttribute: The attribute found, or empty attribute if not exists.

           See Also:
               :meth:`.first_attribute`
           )doc");

  node.def("first_child", &xml_node::first_child,
           R"doc(
           Return the first child node.

           Returns:
               XMLNode: The first child node, or empty node if not exists.

           See Also:
               :meth:`.last_child`
           )doc");

  node.def("last_child", &xml_node::last_child,
           R"doc(
           Return the last child node.

           Returns:
               XMLNode: The last child node, or empty node if not exists.

           See Also:
               :meth:`.first_child`
           )doc");

  node.def("next_sibling", py::overload_cast<>(&xml_node::next_sibling, py::const_),
           "\tReturn the next sibling node in the document tree.")
      .def("next_sibling", py::overload_cast<const char_t *>(&xml_node::next_sibling, py::const_), py::arg("name"),
           "\tReturn the next sibling node with the specified name in the document tree.\n\n"
           "Args:\n"
           "    name (str): The name of the target node.\n\n"
           "Returns:\n"
           "    XMLNode: The node found, or empty node if not exists.\n\n"
           "See Also:\n"
           "    :meth:`.previous_sibling`");

  node.def("previous_sibling", py::overload_cast<>(&xml_node::previous_sibling, py::const_),
           "\tReturn the previous sibling node in the document tree.")
      .def("previous_sibling", py::overload_cast<const char_t *>(&xml_node::previous_sibling, py::const_),
           py::arg("name"),
           "\tReturn the previous sibling node with the specified name in the document tree.\n\n"
           "Args:\n"
           "    name (str): The name of the target node.\n\n"
           "Returns:\n"
           "    XMLNode: The node found, or empty node if not exists.\n\n"
           "See Also:\n"
           "    :meth:`.next_sibling`");

  node.def("parent", &xml_node::parent,
           R"doc(
           Return the parent node.

           Returns:
               XMLNode: The parent node, or empty node if not exists.
           )doc");

  node.def("root", &xml_node::root,
           R"doc(
           Return the root of DOM tree this node belongs to.

           Returns:
               XMLNode: The root node, or empty node if not exists.
           )doc");

  node.def("text", &xml_node::text,
           R"doc(
           Return the text object for the current node.

           Returns:
               XMLText: The text object.
           )doc");

  node.def("child", &xml_node::child, py::arg("name"),
           R"doc(
           Return a child node with the specified name.

           Args:
               name (str): The node name to find.

           Returns:
               XMLNode: The first node found, or empty node if not exists.
           )doc");

  node.def("attribute", py::overload_cast<const char_t *>(&xml_node::attribute, py::const_), py::arg("name"),
           "\tReturn the attribute with the specified name for this node.")
      .def("attribute", py::overload_cast<const char_t *, xml_attribute &>(&xml_node::attribute, py::const_),
           py::arg("name"), py::arg("hint"),
           "\tReturn the attribute with the specified name and *hint* for this node.\n\n"
           "Args:\n"
           "    name (str): The attribute name to find.\n"
           "    hint (XMLAttribute): The attribute to start searching for in the attribute list of this node. "
           "If the attribute specified by *name* is found in the attribute list, *hint* is updated with the next "
           "attribute after the one found, or with an empty attribute if not found.\n\n"
           "Returns:\n"
           "    XMLAttribute: The first attribute found, or empty attribute if not exists.\n\n"
           "Examples:\n"
           "    >>> from pugixml import pugi\n"
           "    >>> doc = pugi.XMLDocument()\n"
           "    >>> doc.load_string('<node attr1=\"1\" attr2=\"2\" attr3=\"3\" />')\n"
           "    >>> node = doc.child('node')\n"
           "    >>> hint = pugi.XMLAttribute()\n"
           "    >>> node.attribute('attr2', hint).name()\n"
           "    'attr2'\n"
           "    >>> hint.name()\n"
           "    'attr3'\n"
           "    >>> node.attribute('attr1', hint).name()\n"
           "    'attr1'\n"
           "    >>> hint.name()\n"
           "    'attr2'\n"
           "    >>> node.attribute('attr3', hint).name()\n"
           "    'attr3'\n"
           "    >>> hint.empty()\n"
           "    True\n");

  node.def("child_value", py::overload_cast<>(&xml_node::child_value, py::const_),
           "\tReturn the value of the first child node with node type :attr:`NODE_PCDATA` or :attr:`NODE_CDATA`.")
      .def("child_value", py::overload_cast<const char_t *>(&xml_node::child_value, py::const_), py::arg("name"),
           "\tReturn the value of the child node with the specified name.\n\n"
           "Args:\n"
           "    name (str): The node name to find.\n\n"
           "Returns:\n"
           "    str: The value of the child node specified by name, the value of the first child node with node type "
           "    :attr:`NODE_PCDATA` or :attr:`NODE_CDATA`, or the empty string if not exists.\n\n"
           "Examples:\n"
           "    >>> from pugixml import pugi\n"
           "    >>> doc = pugi.XMLDocument()\n"
           "    >>> doc.load_string('<node><child1>value1</child1><child3><![CDATA[value3]]></child3>value4</node>')\n"
           "    >>> doc.child_value('node')\n"
           "    'value4'\n"
           "    >>> doc.child('node').child_value()\n"
           "    'value4'\n"
           "    >>> doc.child('node').child_value('child1')\n"
           "    'value1'\n"
           "    >>> doc.child('node').child_value('child3')\n"
           "    'value3'\n");

  node.def("set_name", &xml_node::set_name, py::arg("name"),
           R"doc(
           Set the node name.

           Args:
               name (str): The node name to set.

           Returns:
               bool: :obj:`False` if node is empty, there is not enough memory, or node can not have name.
           )doc");

  node.def("set_value", py::overload_cast<const char_t *>(&xml_node::set_value), py::arg("value"),
           "\tSet the node value.")
      .def(
          "set_value",
          [](xml_node &self, const char_t *value, size_t size) {
            size_t sz =
#ifdef PUGIXML_WCHAR_MODE
                wcslen(value);
#else
                strlen(value);
#endif
            return self.set_value(value, std::min(size, sz));
          },
          py::arg("value").none(false), py::arg("size"),
          "\tSet the node value with the specified length.\n\n"
          "Args:\n"
          "    value (str): The node value to set.\n"
          "    size (int): The length of the value.\n\n"
          "Returns:\n"
          "    bool: :obj:`False` if node is empty, there is not enough memory, or node can not have value.");

  node.def("append_attribute", &xml_node::append_attribute, py::arg("name"),
           R"doc(
           Add a new attribute with the specified name to the end of the list of attributes for this node.

           Args:
               name (str): The attribute name to add.

           Returns:
               XMLAttribute: The attribute added, or empty attribute if error occurs.

           See Also:
               :meth:`.prepend_attribute`, :meth:`.insert_attribute_after`, :meth:`.insert_attribute_before`
           )doc");

  node.def("prepend_attribute", &xml_node::prepend_attribute, py::arg("name"),
           R"doc(
           Add a new attribute with the specified name to the top of the list of attributes for this node.

           Args:
               name (str): The attribute name to add.

           Returns:
               XMLAttribute: The attribute added, or empty attribute if error occurs.

           See Also:
               :meth:`.append_attribute`, :meth:`.insert_attribute_after`, :meth:`.insert_attribute_before`
           )doc");

  node.def("insert_attribute_after", &xml_node::insert_attribute_after, py::arg("name"), py::arg("attr"),
           R"doc(
           Insert a new attribute with the specified name after *attr* in the list of attributes for this node.

           Args:
               name (str): The attribute name to insert.
               attr (XMLAttribute): The attribute in the attribute list for this node.

           Returns:
               XMLAttribute: The attribute inserted, or empty attribute if error occurs.

           See Also:
               :meth:`.append_attribute`, :meth:`.prepend_attribute`, :meth:`.insert_attribute_before`
           )doc");

  node.def("insert_attribute_before", &xml_node::insert_attribute_before, py::arg("name"), py::arg("attr"),
           R"doc(
           Insert a new attribute with the specified name before *attr* in the list of attributes for this node.

           Args:
               name (str): The attribute name to insert.
               attr (XMLAttribute): The attribute in the attribute list for this node.

           Returns:
               XMLAttribute: The attribute inserted, or empty attribute if error occurs.

           See Also:
               :meth:`.append_attribute`, :meth:`.prepend_attribute`, :meth:`.insert_attribute_after`
           )doc");

  node.def("append_copy", py::overload_cast<const xml_attribute &>(&xml_node::append_copy), py::arg("proto"),
           "\tAdd a copy of attribute *proto* to the end of the list of attributes for this node.")
      .def("append_copy", py::overload_cast<const xml_node &>(&xml_node::append_copy), py::arg("proto"),
           "\tAdd a copy of node *proto* to the end of the list of children.\n\n"
           "Args:\n"
           "    proto (typing.Union[XMLAttribute, XMLNode]): The attribute or node to add after copying.\n\n"
           "Returns:\n"
           "    typing.Union[XMLAttribute, XMLNode]:"
           "    The attribute/node added, or empty attribute/node if error occurs.\n\n"
           "See Also:\n"
           "    :meth:`.prepend_copy`, :meth:`.insert_copy_after`, :meth:`.insert_copy_before`\n\n"
           "Examples:\n"
           "    >>> from pugixml import pugi\n"
           "    >>> doc = pugi.XMLDocument()\n"
           "    >>> node = doc.append_child('node')\n"
           "    >>> attr1 = node.append_attribute('attr1')\n"
           "    >>> attr1.set_value(1)\n"
           "    >>> attr2 = node.append_copy(attr1)\n"
           "    >>> attr1 != attr2  # True\n"
           "    >>> attr2.set_name('attr2')\n"
           "    >>> doc.print(pugi.PrintWriter())\n"
           "    <node attr1=\"1\" attr2=\"1\"/>");

  node.def("prepend_copy", py::overload_cast<const xml_attribute &>(&xml_node::prepend_copy), py::arg("proto"),
           "\tAdd a copy of attribute *proto* to the top of the list of attributes for this node.")
      .def("prepend_copy", py::overload_cast<const xml_node &>(&xml_node::prepend_copy), py::arg("proto"),
           "\tAdd a copy of node *proto* to the top of the list of children.\n\n"
           "Args:\n"
           "    proto (typing.Union[XMLAttribute, XMLNode]): The attribute or node to add after copying.\n\n"
           "Returns:\n"
           "    typing.Union[XMLAttribute, XMLNode]:"
           "    The attribute/node added, or empty attribute/node if error occurs.\n\n"
           "See Also:\n"
           "    :meth:`.append_copy`, :meth:`.insert_copy_after`, :meth:`.insert_copy_before`");

  node.def("insert_copy_after",
           py::overload_cast<const xml_attribute &, const xml_attribute &>(&xml_node::insert_copy_after),
           py::arg("proto"), py::arg("attr"),
           "\tInsert a copy of attribute *proto* after *attr* in the list of attributes for this node.")
      .def("insert_copy_after", py::overload_cast<const xml_node &, const xml_node &>(&xml_node::insert_copy_after),
           py::arg("proto"), py::arg("node"),
           "\tInsert a copy of node *proto* after *node* in the list of children.\n\n"
           "Args:\n"
           "    proto (typing.Union[XMLAttribute, XMLNode]): The attribute or node to insert after copying.\n\n"
           "    attr (XMLAttribute): The attribute in the attribute list of this node.\n"
           "    node (XMLNode): The node in the children list.\n"
           "Returns:\n"
           "    typing.Union[XMLAttribute, XMLNode]:"
           "    The attribute/node inserted, or empty attribute/node if error occurs.\n\n"
           "See Also:\n"
           "    :meth:`.append_copy`, :meth:`.prepend_copy`, :meth:`.insert_copy_before`");

  node.def("insert_copy_before",
           py::overload_cast<const xml_attribute &, const xml_attribute &>(&xml_node::insert_copy_before),
           py::arg("proto"), py::arg("attr"),
           "\tInsert a copy of attribute *proto* before *attr* in the list of attributes for this node.")
      .def("insert_copy_before", py::overload_cast<const xml_node &, const xml_node &>(&xml_node::insert_copy_before),
           py::arg("proto"), py::arg("node"),
           "\tInsert a copy of node *proto* before *node* in the list of children.\n\n"
           "Args:\n"
           "    proto (typing.Union[XMLAttribute, XMLNode]): The attribute or node to insert after copying.\n\n"
           "    attr (XMLAttribute): The attribute in the attribute list of this node.\n"
           "    node (XMLNode): The node in the children list.\n"
           "Returns:\n"
           "    typing.Union[XMLAttribute, XMLNode]:"
           "    The attribute/node inserted, or empty attribute/node if error occurs.\n\n"
           "See Also:\n"
           "    :meth:`.append_copy`, :meth:`.prepend_copy`, :meth:`.insert_copy_after`");

  node.def("append_child", py::overload_cast<xml_node_type>(&xml_node::append_child),
           py::arg("node_type") = node_element,
           "\tAdd a new node with the specified node type to the end of the list of children.")
      .def("append_child", py::overload_cast<const char_t *>(&xml_node::append_child), py::arg("name"),
           "\tAdd a new node with the specified name to the end of the list of children.\n\n"
           "Args:\n"
           "    node_type (XMLNodeType): The node type to add.\n"
           "    name (str): The node name to add.\n\n"
           "Returns:\n"
           "    XMLNode: The node added, or empty node if error occurs.\n\n"
           "See Also:\n"
           "    :meth:`.prepend_child`, :meth:`.insert_child_after`, :meth:`.insert_child_before`");

  node.def("prepend_child", py::overload_cast<xml_node_type>(&xml_node::prepend_child),
           py::arg("node_type") = node_element,
           "\tAdd a new node with the specified node type to the top of the list of children.")
      .def("prepend_child", py::overload_cast<const char_t *>(&xml_node::prepend_child), py::arg("name"),
           "\tAdd a new node with the specified name to the top of the list of children.\n\n"
           "Args:\n"
           "    node_type (XMLNodeType): The node type to add.\n"
           "    name (str): The node name to add.\n\n"
           "Returns:\n"
           "    XMLNode: The node added, or empty node if error occurs.\n\n"
           "See Also:\n"
           "    :meth:`.append_child`, :meth:`.insert_child_after`, :meth:`.insert_child_before`");

  node.def("insert_child_after", py::overload_cast<xml_node_type, const xml_node &>(&xml_node::insert_child_after),
           py::arg("node_type"), py::arg("node"),
           "\tInsert a new node with the specified node type after *node* in the list of children.")
      .def("insert_child_after", py::overload_cast<const char_t *, const xml_node &>(&xml_node::insert_child_after),
           py::arg("name"), py::arg("node"),
           "\tInsert a new node with the specified name after *node* in the list of children.\n\n"
           "Args:\n"
           "    node_type (XMLNodeType): The node type to insert.\n"
           "    name (str): The node name to insert.\n"
           "    node (XMLNode): The node in the children list.\n\n"
           "Returns:\n"
           "    XMLNode: The node inserted, or empty node if error occurs.\n\n"
           "See Also:\n"
           "    :meth:`.append_child`, :meth:`.prepend_child`, :meth:`.insert_child_before`");

  node.def("insert_child_before", py::overload_cast<xml_node_type, const xml_node &>(&xml_node::insert_child_before),
           py::arg("node_type"), py::arg("node"),
           "\tInsert a new node with the specified node type before *node* in the list of children.")
      .def("insert_child_before", py::overload_cast<const char_t *, const xml_node &>(&xml_node::insert_child_before),
           py::arg("name"), py::arg("node"),
           "\tInsert a new node with the specified name before *node* in the list of children.\n\n"
           "Args:\n"
           "    node_type (XMLNodeType): The node type to insert.\n"
           "    name (str): The node name to insert.\n\n"
           "    node (XMLNode): The node in the children list.\n\n"
           "Returns:\n"
           "    XMLNode: The node inserted, or empty node if error occurs.\n\n"
           "See Also:\n"
           "    :meth:`.append_child`, :meth:`.prepend_child`, :meth:`.insert_child_after`");

  node.def("append_move", &xml_node::append_move, py::arg("moved"),
           R"doc(
           Move the specified node as the last child of this node.

           Args:
               moved (XMLNode): The node to move.

           Returns:
               XMLNode: The node moved, or empty node if error occurs.

           See Also:
               :meth:`.prepend_move`, :meth:`.insert_move_after`, :meth:`.insert_move_before`
           )doc");

  node.def("prepend_move", &xml_node::prepend_move, py::arg("moved"),
           R"doc(
           Move the specified node as the first child of this node.

           Args:
               moved (XMLNode): The node to move.

           Returns:
               XMLNode: The node moved, or empty node if error occurs.

           See Also:
               :meth:`.append_move`, :meth:`.insert_move_after`, :meth:`.insert_move_before`
           )doc");

  node.def("insert_move_after", &xml_node::insert_move_after, py::arg("moved"), py::arg("node"),
           R"doc(
           Move the specified node after *node* in the list of children.

           Args:
               moved (XMLNode): The node to move.
               node (XMLNode): The node in the children list.

           Returns:
               XMLNode: The node moved, or empty node if error occurs.

           See Also:
               :meth:`.append_move`, :meth:`.prepend_move`, :meth:`.insert_move_before`
           )doc");

  node.def("insert_move_before", &xml_node::insert_move_before, py::arg("moved"), py::arg("node"),
           R"doc(
           Move the specified node before *node* in the list of children.

           Args:
               moved (XMLNode): The node to move.
               node (XMLNode): The node in the children list.

           Returns:
               XMLNode: The node moved, or empty node if error occurs.

           See Also:
               :meth:`.append_move`, :meth:`.prepend_move`, :meth:`.insert_move_after`
           )doc");

  node.def("remove_attribute", py::overload_cast<const xml_attribute &>(&xml_node::remove_attribute), py::arg("attr"),
           "\tRemove the attribute with the specified *attr* from the list of attributes for this node.")
      .def("remove_attribute", py::overload_cast<const char_t *>(&xml_node::remove_attribute), py::arg("name"),
           "\tRemove the attribute with the specified name from the list of attributes for this node.\n\n"
           "Args:\n"
           "    attr (XMLAttribute): The attribute to remove.\n"
           "    name (str): The attribute name to remove.\n\n"
           "Returns:\n"
           "    bool: :obj:`False` if node is empty, *attr* is empty, attribute to be removed is not in the attribute "
           "list, "
           "or there is not enough memory.");

  node.def("remove_attributes", &xml_node::remove_attributes,
           R"doc(
           Remove all attributes from the node.

           Returns:
               bool: :obj:`False` if node is empty or there is not enough memory.
           )doc");

  node.def("remove_child", py::overload_cast<const xml_node &>(&xml_node::remove_child), py::arg("node"),
           "\tRemove the child node specified by *node* and its entire subtree (including all descendant nodes "
           "and attributes) from the document.")
      .def("remove_child", py::overload_cast<const char_t *>(&xml_node::remove_child), py::arg("name"),
           "\tRemove the child node specified by name and its entire subtree (including all descendant nodes and "
           "attributes) from the document.\n\n"
           "Args:\n"
           "    node (XMLNode): The node to remove.\n"
           "    name (str): The node name to remove.\n\n"
           "Returns:\n"
           "    bool: :obj:`False` if node is empty, *node* is empty, node to be removed is not in the children list, "
           "or there is not enough memory.");

  node.def("remove_children", &xml_node::remove_children,
           R"doc(
           Remove all child nodes of the node.

           Returns:
               bool: :obj:`False` if node is empty or there is not enough memory.
           )doc");

  options.disable_function_signatures();
  node.def(
      "append_buffer",
      [](xml_node &self, const char *contents, size_t size, unsigned int options, xml_encoding encoding) {
        return self.append_buffer(contents, size, options, encoding);
      },
      py::arg("contents"), py::arg("size"), py::arg("options") = parse_default, py::arg("encoding") = encoding_auto,
      R"doc(
      append_buffer(self: pugixml.pugi.XMLNode, contents: typing.Union[str, bytes], size: int, options: int = pugixml.pugi.PARSE_DEFAULT, encoding: pugixml.pugi.XMLEncoding = pugixml.pugi.ENCODING_AUTO) -> pugixml.pugi.XMLParseResult

      Parse a buffer as a fragment of the XML document and appends all nodes as children of the current node.

      Args:
          contents (typing.Union[str, bytes]): The XML document fragment to parse.
          size (int): The contents size in bytes.
          options (int): The :pugixml:`parsing options <manual.html#loading.options>`.
          encoding (XMLEncoding): The :pugixml:`input encoding <manual.html#loading.encoding>`.

      Returns:
          XMLParseResult: The result of the operation.
      )doc");
  options.enable_function_signatures();

  node.def(
      "find_attribute",
      [](const xml_node &self, const std::function<bool(const xml_attribute &)> &pred) {
        return self.find_attribute(pred);
      },
      py::arg("pred"),
      R"doc(
      Find the attribute using predicate.

      Args:
          pred (typing.Callable[[XMLAttribute], bool]): The function to find attribute.

      Returns:
          XMLAttribute: The first attribute for which predicate returned :obj:`True`.

      See Also:
          :meth:`.find_child`, :meth:`.find_node`

      Examples:
          >>> from pugixml import pugi
          >>> doc = pugi.XMLDocument()
          >>> doc.load_string('<node attr1="0" attr2="1"/>')
          >>> doc.child('node').find_attribute(lambda x: x.as_int() > 0).name()
          'attr2'
          >>> doc.child('node').find_attribute(lambda x: x.as_int() <= 0).name()
          'attr1'
      )doc");

  node.def(
      "find_child",
      [](const xml_node &self, const std::function<bool(const xml_node &)> &pred) { return self.find_child(pred); },
      py::arg("pred"),
      R"doc(
      Find the child node using predicate.

      Args:
          pred (typing.Callable[[XMLNode], bool]): The function to find child node.

      Returns:
          XMLNode: The first child for which predicate returned :obj:`True`.

      See Also:
          :meth:`.find_attribute`, :meth:`.find_node`

      Examples:
          >>> from pugixml import pugi
          >>> doc = pugi.XMLDocument()
          >>> doc.load_string('<node><child1/><child2/></node>')
          >>> doc.find_child(lambda x: x.name().startswith('child')).empty()
          True
          >>> doc.child('node').find_child(lambda x: x.name().startswith('child')).name()
          'child1'
      )doc");

  node.def(
      "find_node",
      [](const xml_node &self, const std::function<bool(const xml_node &)> &pred) { return self.find_node(pred); },
      py::arg("pred"),
      R"doc(
      Find the node from subtree using predicate.

      Args:
          pred (typing.Callable[[XMLNode], bool]): The function to find node from subtree.

      Returns:
          XMLNode: The first node from subtree (depth-first), for which predicate returned :obj:`True`.

      See Also:
          :meth:`.find_attribute`, :meth:`.find_child`

      Examples:
          >>> from pugixml import pugi
          >>> doc = pugi.XMLDocument()
          >>> doc.load_string('<node><child1/><child2/></node>')
          >>> doc.find_node(lambda x: x.name().startswith('child')).name()
          'child1'
          >>> doc.child('node').find_node(lambda x: x.name().startswith('child')).name()
          'child1'
      )doc");

  node.def("find_child_by_attribute",
           py::overload_cast<const char_t *, const char_t *, const char_t *>(&xml_node::find_child_by_attribute,
                                                                             py::const_),
           py::arg("name"), py::arg("attr_name"), py::arg("attr_value"),
           "\tFind the child node with the specified node name, attribute name, and attribute value.")
      .def("find_child_by_attribute",
           py::overload_cast<const char_t *, const char_t *>(&xml_node::find_child_by_attribute, py::const_),
           py::arg("attr_name"), py::arg("attr_value"),
           "\tFind the child node with the specified attribute name and attribute value.\n\n"
           "Args:\n"
           "    name (str): The node name to find.\n"
           "    attr_name (str): The attribute name to find.\n"
           "    attr_value (str): The attribute value to find.\n\n"
           "Returns:\n"
           "    XMLNode: The first child found, or empty node if not exists.");

  node.def("path", &xml_node::path, py::arg("delimiter") = '/',
           R"doc(
           Return the absolute node path from the root as a text string.

           Args:
               delimiter (str): The path separator.

           Returns:
               str: A path string.

           See Also:
               :meth:`.first_element_by_path`
           )doc");

  node.def("first_element_by_path", &xml_node::first_element_by_path, py::arg("path"), py::arg("delimiter") = '/',
           R"doc(
           Search for a node by path consisting of node names and '.' or '..' elements.

           Args:
               path (str): The path to search for the node.
               delimiter (str): The path separator.

           Returns:
               XMLNode: The first node found, or empty node if not exists.

           See Also:
               :meth:`.path`
           )doc");

  node.def("traverse", &xml_node::traverse, py::arg("walker"),
           R"doc(
           Traverse subtree recursively with :class:`XMLTreeWalker`.

           First, ``traverse()`` calls :meth:`XMLTreeWalker.begin` with the traversal root as its arguments.
           Then, :meth:`XMLTreeWalker.for_each` is called for all nodes in the traversal subtree in depth first order,
           excluding the traversal root, with the node as its arguments.
           Finally, :meth:`XMLTreeWalker.end` is called with traversal root as its argument.
           If ``begin``, ``end``, or any of the ``for_each`` returns :obj:`False`, the traversal is terminated and
           :obj:`False` is returned as the traversal result.

           See :pugixml:`documentation <manual.html#access.walker>` for more details.

           Args:
               walker (XMLTreeWalker): The walker object which implements :class:`XMLTreeWalker` interface.

           Returns:
               bool: :obj:`False` if :meth:`XMLTreeWalker.begin`, :meth:`XMLTreeWalker.end`,
               or any of the :meth:`XMLTreeWalker.for_each` returns :obj:`False`.

           Examples:
               >>> from pugixml import pugi
               ... class PrintWalker(pugi.XMLTreeWalker):
               ...     def for_each(self, node: pugi.XMLNode) -> bool:
               ...         print('%r depth=%d name=%r' % (node.type(), self.depth(), node.name()))
               ...         return True

               >>> doc = pugi.XMLDocument()
               >>> doc.load_string('<node><child1><child2/></child1><child3/></node>')
               >>> doc.traverse(PrintWalker())
               <XMLNodeType.NODE_ELEMENT: 2> depth=0 name='node'
               <XMLNodeType.NODE_ELEMENT: 2> depth=1 name='child1'
               <XMLNodeType.NODE_ELEMENT: 2> depth=2 name='child2'
               <XMLNodeType.NODE_ELEMENT: 2> depth=1 name='child3'
           )doc");

  node.def("select_node", py::overload_cast<const char_t *, xpath_variable_set *>(&xml_node::select_node, py::const_),
           py::arg("query"), py::arg("variables") = nullptr,
           "\tSelect a single node by evaluating XPath expression with variables.\n\n"
           "\tThis is equivalent to ``select_nodes(query, variables).first()``.")
      .def("select_node", py::overload_cast<const xpath_query &>(&xml_node::select_node, py::const_), py::arg("query"),
           "\tSelect a single node by evaluating XPath expression.\n\n"
           "\tThis is equivalent to ``select_nodes(query).first()``.\n\n"
           "Args:\n"
           "    query (typing.Union[str, XPathQuery]): The XPath expression.\n"
           "    variables (typing.Optional[XPathVariableSet]): The variables in *query*.\n\n"
           "Returns:\n"
           "    XPathNode: The first XPath node in the document order that matches the XPath expression, "
           "    or empty XPath node if node is empty or XPath expression does not match anything.\n\n"
           "See Also:\n"
           "    :meth:`.select_nodes`, :class:`XPathNode`, :meth:`XPathQuery.evaluate_node`\n\n"
           "Examples:\n"
           "    >>> from pugixml import pugi\n"
           "    >>> doc = pugi.XMLDocument()\n"
           "    >>> doc.load_string('<node><head id=\"1\"/><foo id=\"2\"/><foo id=\"3\"/><tail id=\"4\"/></node>')\n"
           "    >>> node = doc.select_node('//*[@id=\"2\"]')\n"
           "    >>> bool(node)\n"
           "    True\n"
           "    >>> node.node().print(pugi.PrintWriter())\n"
           "    <foo id=\"2\" />\n"
           "    >>> varset = pugi.XPathVariableSet()\n"
           "    >>> var = varset.add('id', pugi.XPATH_TYPE_NUMBER)\n"
           "    >>> var.set(3)\n"
           "    >>> node = doc.select_node('//*[@id=string($id)]', varset)\n"
           "    >>> bool(node)\n"
           "    True\n"
           "    >>> node.node().print(pugi.PrintWriter())\n"
           "    <foo id=\"3\" />\n"
           "    >>> var.set(5)\n"
           "    >>> node = doc.select_node('//*[@id=string($id)]', varset)\n"
           "    >>> bool(node)\n"
           "    False\n");

  node.def("select_nodes", py::overload_cast<const char_t *, xpath_variable_set *>(&xml_node::select_nodes, py::const_),
           py::arg("query"), py::arg("variables") = nullptr,
           "\tSelect the node set by evaluating XPath expression with variables.")
      .def("select_nodes", py::overload_cast<const xpath_query &>(&xml_node::select_nodes, py::const_),
           py::arg("query"),
           "\tSelect the node set by evaluating XPath expression.\n\n"
           "Args:\n"
           "    query (typing.Union[str, XPathQuery]): The XPath expression.\n"
           "    variables (typing.Optional[XPathVariableSet]): The variables in *query*.\n\n"
           "Returns:\n"
           "    XPathNodeSet: The XPath node set in the document order that matches the XPath expression, "
           "    or empty XPath node set if node is empty or XPath expression does not match anything.\n\n"
           "See Also:\n"
           "    :meth:`.select_node`, :class:`XPathNodeSet`, :meth:`XPathQuery.evaluate_node_set`\n\n"
           "Examples:\n"
           "    >>> from pugixml import pugi\n"
           "    >>> doc = pugi.XMLDocument()\n"
           "    >>> doc.load_string('<node><head id=\"1\"/><foo id=\"2\"/><foo id=\"3\"/><tail id=\"4\"/></node>')\n"
           "    >>> varset = pugi.XPathVariableSet()\n"
           "    >>> var = varset.add('name', pugi.XPATH_TYPE_STRING)\n"
           "    >>> query = pugi.XPathQuery('//*[local-name()=$name]', varset)\n"
           "    >>> var.set('foo')\n"
           "    >>> ns = doc.select_nodes(query)\n"
           "    >>> ns.size()\n"
           "    2\n"
           "    >>> ns[0].node().print(pugi.PrintWriter())\n"
           "    <foo id=\"2\" />\n"
           "    >>> ns[1].node().print(pugi.PrintWriter())\n"
           "    <foo id=\"3\" />\n"
           "    >>> var.set('tail')\n"
           "    >>> ns = doc.select_nodes(query)\n"
           "    >>> ns.size()\n"
           "    1\n"
           "    >>> ns[0].node().print(pugi.PrintWriter())\n"
           "    <tail id=\"4\" />\n");

  options.disable_function_signatures();
  node.def("print",
           py::overload_cast<xml_writer &, const char_t *, unsigned int, xml_encoding, unsigned int>(&xml_node::print,
                                                                                                     py::const_),
           py::arg("writer"), py::arg("indent") = PUGIXML_TEXT("\t"),
           py::arg_v("flags", format_default, "pugixml.pugi.FORMAT_DEFAULT"), py::arg("encoding") = encoding_auto,
           py::arg("depth") = 0,
           R"doc(
           print(self: pugixml.pugi.XMLNode, writer: pugixml.pugi.XMLWriter, indent: str = '\t', flags: int = pugixml.pugi.FORMAT_DEFAULT, encoding: pugixml.pugi.XMLEncoding = pugixml.pugi.ENCODING_AUTO, depth: int = 0) -> None

           Save a single subtree to *writer*.

           See :pugixml:`documentation <manual.html#saving.subtree>` for details.

           Args:
               writer (XMLWriter): The writer object which implements :class:`XMLWriter` interface.
               indent (str): The indentation character(s).
               flags (int): The :pugixml:`output options <manual.html#saving.options>`.
               encoding (XMLEncoding): The :pugixml:`output encoding <manual.html#saving.encoding>`.
               depth (int): The number of node's depth.

           See Also:
               :meth:`XMLDocument.save`, :class:`XMLWriter`

           Examples:
               >>> from pugixml import pugi
               >>> class SimpleWriter(pugi.XMLWriter):
               ...     def __init__(self) -> None:
               ...         super().__init__()
               ...         self._data = b''
               ...     def getvalue(self) -> bytes:
               ...         return self._data
               ...     def write(self, data: bytes, size: int) -> None:
               ...         self._data += data

               >>> doc = pugi.XMLDocument()
               >>> doc.load_string('<node><child1 a1="v1"><child2 a2="v2"/></child1></node>')
               >>> writer = SimpleWriter()
               >>> doc.print(writer, encoding=pugi.ENCODING_UTF32_BE)
               >>> writer.getvalue().decode('utf-32be')
               '<node>\n\t<child1 a1="v1">\n\t\t<child2 a2="v2" />\n\t</child1>\n</node>\n'
               >>> writer = SimpleWriter()
               >>> doc.child('node').first_child().print(writer, encoding=pugi.ENCODING_UTF32_BE)
               >>> writer.getvalue().decode('utf-32be')
               '<child1 a1="v1">\n\t<child2 a2="v2" />\n</child1>\n'
           )doc");
  options.enable_function_signatures();

  // xml_node::begin()
  // xml_node::end()
  // xml_node::attributes_begin()
  // xml_node::attributes_end()

  node.def(
          "children",
          [](const xml_node &self) { return std::make_unique<Iterator<xml_node_iterator, xml_node>>(self.children()); },
          py::keep_alive<0, 1>(), "\tReturn an iterator of children.")
      .def(
          "children",
          [](const xml_node &self, const char_t *name) {
            // auto it = self.children(name);
            // std::vector<xml_node> children(it.begin(), it.end());
            // NOTE:
            //  py::make_iterator(it.begin(), it.end()) returns empty nodes.
            //  py::make_iterator(children.begin(), children.end()) causes segmentation fault.
            return std::make_unique<Iterator<xml_named_node_iterator, xml_node>>(self.children(name));
          },
          py::keep_alive<0, 1>(), py::arg("name"),
          "\tReturn an iterator of children with the specified name.\n\n"
          "Args:\n"
          "    name (str): The node name to find.\n\n"
          "Returns:\n"
          "    typing.Union[XMLNodeIterator, XMLNamedNodeIterator]: A new iterator of children.");

  node.def(
      "attributes",
      [](const xml_node &self) {
        return std::make_unique<Iterator<xml_attribute_iterator, xml_attribute>>(self.attributes());
      },
      py::keep_alive<0, 1>(),
      R"doc(
      Return an iterator of attributes for this node.

      Returns:
          XMLAttributeIterator: A new iterator of attributes.
      )doc");

  node.def("offset_debug", &xml_node::offset_debug,
           R"doc(
           Return the node offset in the parsed file/string for debugging purposes.

           Returns:
               int: The offset to node’s data from the beginning of XML buffer.
               For more information on parsing offsets, see
               :pugixml:`parsing error handling documentation <manual.html#xml_parse_result::offset>`.
           )doc");

  node.def("hash_value", &xml_node::hash_value,
           R"doc(
           Return the hash value (unique for handles to the same object).

           Returns:
               int: The hash value.
           )doc");

  node.def(
      "internal_object", [](const xml_node &self) { return std::make_unique<XMLNodeStruct>(self.internal_object()); },
      R"doc(
      Return the internal object.

      Returns:
          XMLNodeStruct: The internal object of this node.
      )doc");

  //
  // pugi::xml_text
  //
  text.def(py::init<>(), "Initialize ``XMLText`` as an empty text.");

  text.def(
      "__bool__", [](const xml_text &self) -> bool { return self; },
      R"doc(
      Determine if this object is not empty.

      Returns:
          bool: :obj:`True` if object is not empty, :obj:`False` otherwise.
      )doc");

  text.def("__repr__", [](const xml_text &self) {
    std::stringstream ss;
    ss << "<XMLText";

    const auto hash = self.data().hash_value();
    ss << " hash=0";
    if (hash) {
      ss << "x" << std::hex << std::uppercase << hash;
    }

    ss << ">";
    return ss.str();
  });

  text.def("empty", &xml_text::empty,
           R"doc(
           Determine if this object is empty.

           Returns:
               bool: :obj:`True` if object is empty, :obj:`False` otherwise.
           )doc");

  text.def("get", &xml_text::get,
           R"doc(
           Return the contents.

           Returns:
               str: The contents, or the empty string if object is empty.

           See Also:
               :meth:`.as_string`
           )doc");

  text.def("as_string", &xml_text::as_string, py::arg("default") = PUGIXML_TEXT(""),
           R"doc(
           Return the contents.

           Args:
               default (str): The default value.

           Returns:
               str: The contents, or the default value if object is empty.
           )doc");

  text.def("as_int", &xml_text::as_int, py::arg("default") = 0,
           R"doc(
           Return the contents as a number [INT_MIN, INT_MAX].

           Args:
               default (int): The default value.

           Returns:
               int: The contents as a number, or the default value if conversion did not succeed or object is empty.
           )doc");

  text.def("as_uint", &xml_text::as_uint, py::arg("default") = 0,
           R"doc(
           Return the contents as a number [0, UINT_MAX].

           Args:
               default (int): The default value.

           Returns:
               int: The contents as a number, or the default value if conversion did not succeed or object is empty.
           )doc");

  text.def("as_double", &xml_text::as_double, py::arg("default") = 0,
           R"doc(
           Return the contents as a number [DBL_MIN, DBL_MAX].

           Args:
               default (float): The default value.

           Returns:
               float: The contents as a number, or the default value if conversion did not succeed or object is empty.
           )doc");

  text.def("as_float", &xml_text::as_float, py::arg("default") = 0,
           R"doc(
           Return the contents as a number [FLT_MIN, FLT_MAX].

           Args:
               default (float): The default value.

           Returns:
               float: The contents as a number, or the default value if conversion did not succeed or object is empty.
           )doc");

  text.def("as_llong", &xml_text::as_llong, py::arg("default") = 0,
           R"doc(
           Return the contents as a number [LLONG_MIN, LLONG_MAX].

           Args:
               default (int): The default value.

           Returns:
               int: The contents as a number, or the default value if conversion did not succeed or object is empty.
           )doc");

  text.def("as_ullong", &xml_text::as_ullong, py::arg("default") = 0,
           R"doc(
           Return the contents as a number [0, ULLONG_MAX].

           Args:
               default (int): The default value.

           Returns:
               int: The contents as a number, or the default value if conversion did not succeed or object is empty.
           )doc");

  text.def("as_bool", &xml_text::as_bool, py::arg("default") = false,
           R"doc(
           Return the contents as a boolean.

           Args:
               default (bool): The default value.

           Returns:
               bool: The contents as a boolean (returns :obj:`True` if first character is in '1tTyY' set),
               or the default value if conversion did not succeed or object is empty.
           )doc");

  text.def("set", py::overload_cast<const char_t *>(&xml_text::set), py::arg("value"), "\tSet the contents.")
      .def("set", py::overload_cast<bool>(&xml_text::set), py::arg("value"),
           "\tSet the contents as a boolean (\"true\" or \"false\").")
      .def("set", py::overload_cast<double>(&xml_text::set), py::arg("value").noconvert(),
           "\tSet the contents as a number [DBL_MIN, DBL_MAX].")
      .def("set", py::overload_cast<double, int>(&xml_text::set), py::arg("value"), py::arg("precision"),
           "\tSet the contents as a number with the specified precision [DBL_MIN, DBL_MAX].")
      .def("set", py::overload_cast<long long>(&xml_text::set), py::arg("value"),
           "\tSet the contents as a number [LLONG_MIN, LLONG_MAX].")
      .def("set", py::overload_cast<unsigned long long>(&xml_text::set), py::arg("value"),
           "\tSet the contents as a number [0, ULLONG_MAX].\n\n"
           "Args:\n"
           "    value (typing.Union[str, bool, float, int]): The contents to set.\n"
           "    precision (int): The precision for the contents as a floating point number.\n\n"
           "Returns:\n"
           "    bool: :obj:`False` if object is empty or there is not enough memory.");

  text.def("data", &xml_text::data,
           R"doc(
           Return the data node (:attr:`NODE_PCDATA` or :attr:`NODE_CDATA`) for this object.

           Returns:
               XMLNode: The data node for this object.
           )doc");

  // pugi::xml_node_iterator
  // pugi::xml_attribute_iterator
  // pugi::xml_named_node_iterator

  //
  // pugi::xml_tree_walker
  //
  trwk.def(py::init<>(), "Initialize ``XMLTreeWalker``.");

  trwk.def("begin", &xml_tree_walker::begin, py::arg("node"),
           R"doc(
           Called by :meth:`XMLNode.traverse` at the start of traversal.

           Args:
               node (XMLNode): The node of traversal root.

           Returns:
               bool: :obj:`True` if the traverse should continue, :obj:`False` otherwise.
           )doc");

  trwk.def("for_each", &xml_tree_walker::for_each, py::arg("node"),
           R"doc(
           Called by :meth:`XMLNode.traverse` for all nodes in the traversal subtree except the traversal root,
           in the depth first order.

           Args:
               node (XMLNode): The current node in the traversal subtree.

           Returns:
               bool: :obj:`True` if the traverse should continue, :obj:`False` otherwise.
           )doc");

  trwk.def("end", &xml_tree_walker::end, py::arg("node"),
           R"doc(
           Called by :meth:`XMLNode.traverse` at the end of traversal.

           Args:
               node (XMLNode): The node of traversal root.

           Returns:
               bool: :obj:`True` if the traverse should continue, :obj:`False` otherwise.
           )doc");

  trwk.def("depth", &PyXMLTreeWalker::depth,
           R"doc(
           Return the node's depth.

           Returns:
               int: The depth of current node.
           )doc");

  //
  // pugi::xml_parse_result
  //
  pr.def(py::init<>(), "Initialize ``XMLParseResult``.");

  pr.def(
      "__bool__", [](const xml_parse_result &self) -> bool { return self; },
      R"doc(
      Determine if the parsing result is not an error (:attr:`.status` == :attr:`STATUS_OK`).

      Returns:
          bool: :obj:`True` if the parsing result is not an error, :obj:`False` otherwise.
      )doc");

  pr.def("__repr__", [](const xml_parse_result &self) {
    std::stringstream ss;
    ss << "<XMLParseResult";

    const auto status = self.status;
    ss << " status=";
    if (_xml_parse_status_to_string.count(status)) {
      ss << _xml_parse_status_to_string[status];
    } else {
      ss << status;
    }

    ss << " offset=" << self.offset;

    const auto encoding = self.encoding;
    ss << " encoding=";
    if (_xml_encoding_to_string.count(encoding)) {
      ss << _xml_encoding_to_string[encoding];
    } else {
      ss << encoding;
    }

    ss << " description=" << std::quoted(self.description(), '\'');
    ss << ">";
    return ss.str();
  });

  pr.def_property_readonly(
      "status", [](const xml_parse_result &self) { return self.status; }, "XMLParseStatus: The parsing status.");

  pr.def_property_readonly(
      "offset", [](const xml_parse_result &self) { return self.offset; }, "int: The last parsed offset.");

  pr.def_property_readonly(
      "encoding", [](const xml_parse_result &self) { return self.encoding; },
      "XMLEncoding: The source document encoding.");

  pr.def("description", &xml_parse_result::description,
         R"doc(
         Return an error description.

         Returns:
             str: An error description.
         )doc");

  //
  // pugi::xml_document
  //
  xdoc.def(py::init<>(), "Initialize ``XMLDocument`` as an empty document.");

  xdoc.def("__repr__", [](const xml_document &self) {
    std::stringstream ss;
    ss << "<XMLDocument";
    ss << " hash=0x" << std::hex << std::uppercase << self.hash_value();
    ss << ">";
    return ss.str();
  });

  xdoc.def("reset", py::overload_cast<>(&xml_document::reset), "\tRemove all nodes.")
      .def("reset", py::overload_cast<const xml_document &>(&xml_document::reset), py::arg("proto"),
           "\tRemove all nodes, then copies the entire contents of the specified document.\n\n"
           "Args:\n"
           "    proto (XMLDocument): The XML document to copy.");

  options.disable_function_signatures();
  xdoc.def("load_string", &xml_document::load_string, py::arg("contents").none(false),
           py::arg("options") = parse_default,
           R"doc(
           load_string(self: pugixml.pugi.XMLDocument, contents: str, options: int = pugixml.pugi.PARSE_DEFAULT) -> pugixml.pugi.XMLParseResult

           Load a document from a string.

           No encoding conversions are applied.

           The existing document tree is destroyed.

           Args:
               contents (str): A document to parse.
               options (int): The :pugixml:`parsing options <manual.html#loading.options>`.

           Returns:
               XMLParseResult: The result of the operation.

           Examples:
               >>> from pugixml import pugi
               >>> doc = pugi.XMLDocument()
               >>> doc.load_string('<node><child/></node>')
           )doc");
  options.enable_function_signatures();

  options.disable_function_signatures();
  xdoc.def(
      "load_file",
      [](xml_document &self, const fs::path &path, unsigned int options, xml_encoding encoding) {
        return self.load_file(path.string<char>().c_str(), options, encoding);
      },
      py::arg("path"), py::arg("options") = parse_default, py::arg("encoding") = encoding_auto,
      R"doc(
      load_file(self: pugixml.pugi.XMLDocument, path: os.PathLike, options: int = pugixml.pugi.PARSE_DEFAULT, encoding: pugixml.pugi.XMLEncoding = pugixml.pugi.ENCODING_AUTO) -> pugixml.pugi.XMLParseResult

      Load a document from the existing file.

      The existing document tree is destroyed.

      Args:
          path (os.PathLike): The path-like object of the document to parse.
          options (int): The :pugixml:`parsing options <manual.html#loading.options>`.
          encoding (XMLEncoding): The :pugixml:`input encoding <manual.html#loading.encoding>`.

      Returns:
          XMLParseResult: The result of the operation.

      Examples:
          >>> from pugixml import pugi
          >>> doc = pugi.XMLDocument()
          >>> doc.load_file('tree.xml', pugi.PARSE_DEFAULT | pugi.PARSE_DECLARATION | pugi.PARSE_COMMENTS)
      )doc");
  options.enable_function_signatures();

  options.disable_function_signatures();
  xdoc.def(
      "load_buffer",
      [](xml_document &self, const char *contents, size_t size, unsigned int options, xml_encoding encoding) {
        return self.load_buffer(contents, size, options, encoding);
      },
      py::arg("contents"), py::arg("size"), py::arg("options") = parse_default, py::arg("encoding") = encoding_auto,
      R"doc(
      load_buffer(self: pugixml.pugi.XMLDocument, contents: typing.Union[str, bytes], size: int, options: int = pugixml.pugi.PARSE_DEFAULT, encoding: pugixml.pugi.XMLEncoding = pugixml.pugi.ENCODING_AUTO) -> pugixml.pugi.XMLParseResult

      Load a document from a buffer.

      The existing document tree is destroyed.

      Args:
          contents (typing.Union[str, bytes]): A document to parse.
          size (int): The contents size in bytes.
          options (int): The :pugixml:`parsing options <manual.html#loading.options>`.
          encoding (XMLEncoding): The :pugixml:`input encoding <manual.html#loading.encoding>`.

      Returns:
          XMLParseResult: The result of the operation.

      Examples:
          >>> from urllib.request import urlopen
          >>> from pugixml import pugi
          >>> doc = pugi.XMLDocument()
          >>> with urlopen('http://example.com/large.xml') as f:
          ...     contents = f.read()
          ...     doc.load_buffer(contents, len(contents))
      )doc");
  options.enable_function_signatures();

  options.disable_function_signatures();
  xdoc.def("save",
           py::overload_cast<xml_writer &, const char_t *, unsigned int, xml_encoding>(&xml_document::save, py::const_),
           py::arg("writer"), py::arg("indent") = PUGIXML_TEXT("\t"),
           py::arg_v("flags", format_default, "pugixml.pugi.FORMAT_DEFAULT"), py::arg("encoding") = encoding_auto,
           R"doc(
           save(self: pugixml.pugi.XMLDocument, writer: pugixml.pugi.XMLWriter, indent: str = '\t', flags: int = pugixml.pugi.FORMAT_DEFAULT, encoding: pugixml.pugi.XMLEncoding = pugixml.pugi.ENCODING_AUTO) -> None

           Save the XML document to *writer*.

           Semantics is slightly different from :meth:`XMLNode.print`,
           see :pugixml:`documentation <manual.html#saving.writer>` for details.

           Args:
               writer (XMLWriter): The writer object which implements :class:`XMLWriter` interface.
               indent (str): The indentation character(s).
               flags (int): The :pugixml:`output options <manual.html#saving.options>`.
               encoding (XMLEncoding): The :pugixml:`output encoding <manual.html#saving.encoding>`.

           See Also:
               :meth:`XMLNode.print`, :class:`XMLWriter`

           Examples:
               A simple example of saving an XML document to a file:

               >>> from pugixml import pugi
               >>> class FileWriter(pugi.XMLWriter):
               ...     def __init__(self, path) -> None:
               ...         super().__init__()
               ...         self._file = open(path, 'wb')
               ...     def close(self) -> None:
               ...         self._file.close()
               ...     def write(self, data: bytes, size: int) -> None:
               ...         self._file.write(data)

               >>> from contextlib import closing
               >>> doc = pugi.XMLDocument()
               >>> doc.append_child('node')
               >>> with closing(FileWriter('tree.xml')) as writer:
               ...     doc.save(writer)
           )doc");
  options.enable_function_signatures();

  options.disable_function_signatures();
  xdoc.def(
      "save_file",
      [](const xml_document &self, const fs::path &path, const char_t *indent, unsigned int flags,
         xml_encoding encoding) { return self.save_file(path.string<char>().c_str(), indent, flags, encoding); },
      py::arg("path"), py::arg("indent") = PUGIXML_TEXT("\t"),
      py::arg_v("flags", format_default, "pugixml.pugi.FORMAT_DEFAULT"), py::arg("encoding") = encoding_auto,
      R"doc(
      save_file(self: pugixml.pugi.XMLDocument, path: os.PathLike, indent: str = '\t', flags: int = pugixml.pugi.FORMAT_DEFAULT, encoding: pugixml.pugi.XMLEncoding = pugixml.pugi.ENCODING_AUTO) -> bool

      Save the XML document to a file.

      Args:
          path (os.PathLike): The path-like object to save the XML document.
          indent (str): The indentation character(s).
          flags (int): The :pugixml:`output options <manual.html#saving.options>`.
          encoding (XMLEncoding): The :pugixml:`output encoding <manual.html#saving.encoding>`.

      Returns:
          bool: :obj:`True` if the saving was successful, :obj:`False` otherwise.
      )doc");
  options.enable_function_signatures();

  xdoc.def("document_element", &xml_document::document_element,
           R"doc(
           Return the document element.

           Returns:
               XMLNode: The element whose parent is this document, or empty node if not exists.
           )doc");

  //
  // pugi::xpath_parse_result
  //
  xppr.def(py::init<>(), "Initialize ``XPathParseResult``.");

  xppr.def(
      "__bool__", [](const xpath_parse_result &self) -> bool { return self; },
      R"doc(
      Determine if the parsing result is not an error (:attr:`.error` is :obj:`None`).

      Returns:
          bool: :obj:`True` if the parsing result is not an error, :obj:`False` otherwise.
      )doc");

  xppr.def("__repr__", [](const xpath_parse_result &self) {
    std::stringstream ss;
    ss << "<XPathParseResult";

    ss << " error=";
    if (self.error) {
      ss << std::quoted(self.error, '\'');
    } else {
      ss << "None";
    }

    ss << " offset=" << self.offset;
    ss << " description=" << std::quoted(self.description(), '\'');
    ss << ">";
    return ss.str();
  });

  xppr.def_property_readonly(
      "error", [](const xpath_parse_result &self) -> std::optional<const char *> { return self.error; },
      "typing.Optional[str]: An error message. (:obj:`None` if no error)");

  xppr.def_property_readonly(
      "offset", [](const xpath_parse_result &self) { return self.offset; }, "int: The last parsed offset.");

  xppr.def("description", &xpath_parse_result::description,
           R"doc(
           Return an error description.

           Returns:
               str: An error description.
           )doc");

  //
  // pugi::xpath_variable
  //
  xpv.def("name", &xpath_variable::name,
          R"doc(
          Return the variable name.

          Returns:
              str: The variable name.
          )doc");

  xpv.def("type", &xpath_variable::type,
          R"doc(
          Return the variable type.

          Returns:
              XPathValueType: The variable type.
          )doc");

  xpv.def("get_boolean", &xpath_variable::get_boolean,
          R"doc(
          Return the variable value without type conversion.

          Returns:
              bool: The variable value, or :obj:`False` if variable type does not match.
          )doc");

  xpv.def("get_number", &xpath_variable::get_number,
          R"doc(
          Return the variable value without type conversion.

          Returns:
              float: The variable value, or ``float('nan')`` if variable type does not match.
          )doc");

  xpv.def("get_string", &xpath_variable::get_string,
          R"doc(
          Return the variable value without type conversion.

          Returns:
              str: The variable value, or the empty string if variable type does not match.
          )doc");

  xpv.def("get_node_set", &xpath_variable::get_node_set,
          R"doc(
          Return the variable value without type conversion.

          Returns:
              XPathNodeSet: The variable value, or empty node set if variable type does not match.
          )doc");

  // NOTE: Do not change the order of the method chaining. (double -> bool)
  xpv.def("set", py::overload_cast<double>(&xpath_variable::set), py::arg("value"),
          "\tSet the variable value as a number [DBL_MIN, DBL_MAX].")
      .def("set", py::overload_cast<bool>(&xpath_variable::set), py::arg("value"),
           "\tSet the variable value as a boolean.")
      .def("set", py::overload_cast<const char_t *>(&xpath_variable::set), py::arg("value"),
           "\tSet the variable value as a string.")
      .def("set", py::overload_cast<const xpath_node_set &>(&xpath_variable::set), py::arg("value"),
           "\tSet the variable value as the XPath node set.\n\n"
           "Args:\n"
           "    value (typing.Union[float, bool, str, XPathNodeSet]): The variable value to set.\n\n"
           "Returns:\n"
           "    bool: :obj:`False` if variable type does not match or there is not enough memory.");

  //
  // pugi::xpath_variable_set
  //
  xpvs.def(py::init<>(), "Initialize ``XPathVariableSet``.");
  // FIXME: xpath_variable_set(const xpath_variable_set &) causes access violation.
  // .def(py::init<const xpath_variable_set &>(), py::arg("other"));

  options.disable_function_signatures();
  xpvs.def("add", &xpath_variable_set::add, py::return_value_policy::reference, py::arg("name"), py::arg("value_type"),
           R"doc(
           add(self: pugixml.pugi.XPathVariableSet, name: str, value_type: pugixml.pugi.XPathValueType) -> typing.Optional[pugixml.pugi.XPathVariable]

           Add a new variable and return it, or return the existing one if the types match.

           Args:
               name (str): The variable name to add/get.
               value_type (XPathValueType): The variable type to add/get.

           Returns:
               typing.Optional[XPathVariable]: The variable added or the existing one if the types matches, or :obj:`None` if not exists or there is not enough memory.
           )doc");
  options.enable_function_signatures();

  // NOTE: Do not change the order of the method chaining. (double -> bool)
  xpvs.def("set", py::overload_cast<const char_t *, double>(&xpath_variable_set::set), py::arg("name"),
           py::arg("value"), "\tSet the value of an existing variable as a number [DBL_MIN, DBL_MAX].")
      .def("set", py::overload_cast<const char_t *, bool>(&xpath_variable_set::set), py::arg("name"), py::arg("value"),
           "\tSet the value of an existing variable as a boolean.")
      .def("set", py::overload_cast<const char_t *, const char_t *>(&xpath_variable_set::set), py::arg("name"),
           py::arg("value"), "\tSet the value of an existing variable as a string.")
      .def("set", py::overload_cast<const char_t *, const xpath_node_set &>(&xpath_variable_set::set), py::arg("name"),
           py::arg("value"),
           "\tSet the value of an existing variable as the XPath node set.\n\n"
           "No type conversion is performed.\n\n"
           "This is equivalent to ``add(name, value_type).set(value)``.\n\n"
           "Args:\n"
           "    name (str): The variable name to set.\n"
           "    value (typing.Union[float, bool, str, XPathNodeSet]): The variable value to set.\n\n"
           "Returns:\n"
           "    bool: :obj:`False` if there is no such variable or if types mismatch.");

  options.disable_function_signatures();
  xpvs.def("get", py::overload_cast<const char_t *>(&xpath_variable_set::get, py::const_),
           py::return_value_policy::reference, py::arg("name"),
           R"doc(
           get(self: pugixml.pugi.XPathVariableSet, name: str) -> typing.Optional[pugixml.pugi.XPathVariable]

           Return the existing variable with the specified name.

           Args:
               name (str): The variable name to get.

           Returns:
               typing.Optional[XPathVariable]: The variable if exists, :obj:`None` otherwise.
           )doc");
  options.enable_function_signatures();

  //
  // pugi::xpath_query
  //
  xpq.def(py::init<const char_t *, xpath_variable_set *>(), py::arg("query"), py::arg("variables") = nullptr,
          "\tInitialize ``XPathQuery`` with the XPath expression and variables.")
      .def(py::init<>(), "\tInitialize ``XPathQuery`` as an invalid expression.\n\n"
                         "Args:\n"
                         "    query (str): The XPath expression.\n"
                         "    variables (typing.Optional[XPathVariableSet]): The variables in *query*.");

  xpq.def(
      "__bool__", [](const xpath_query &self) -> bool { return self; },
      R"doc(
      Determine if this XPath expression is valid.

      Returns:
          bool: :obj:`True` if XPath expression is valid, :obj:`False` otherwise.
      )doc");

  xpq.def("return_type", &xpath_query::return_type,
          R"doc(
          Return the return type of the XPath expression.

          Returns:
              XPathValueType: The return type of the XPath expression.
          )doc");

  xpq.def("evaluate_boolean", &xpath_query::evaluate_boolean, py::arg("node"),
          "\tEvaluate the expression as a boolean value in the specified context; performs type conversion if "
          "necessary.")
      .def(
          "evaluate_boolean", [](const xpath_query &self, const xml_node &node) { return self.evaluate_boolean(node); },
          py::arg("node"),
          "\tEvaluate the expression as a boolean value in the specified context; performs type conversion if "
          "necessary.\n\n"
          "Args:\n"
          "    node (typing.Union[XPathNode, XMLNode]): The node to evaluate over.\n\n"
          "Returns:\n"
          "    bool: The value evaluated as a boolean, or :obj:`False` if error occurs.");

  xpq.def("evaluate_number", &xpath_query::evaluate_number, py::arg("node"),
          "\tEvaluate the expression as a number in the specified context; performs type conversion if "
          "necessary.")
      .def(
          "evaluate_number", [](const xpath_query &self, const xml_node &node) { return self.evaluate_number(node); },
          py::arg("node"),
          "\tEvaluate the expression as a number in the specified context; performs type conversion if "
          "necessary.\n\n"
          "Args:\n"
          "    node (typing.Union[XPathNode, XMLNode]): The node to evaluate over.\n\n"
          "Returns:\n"
          "    float: The value evaluated as a number, or ``float('nan')`` if error occurs.");

  xpq.def("evaluate_string", py::overload_cast<const xpath_node &>(&xpath_query::evaluate_string, py::const_),
          py::arg("node"),
          "\tEvaluate the expression as a string in the specified context; performs type conversion if necessary.")
      .def(
          "evaluate_string", [](const xpath_query &self, const xml_node &node) { return self.evaluate_string(node); },
          py::arg("node"),
          "\tEvaluate the expression as a string in the specified context; performs type conversion if necessary.\n\n"
          "Args:\n"
          "    node (typing.Union[XPathNode, XMLNode]): The node to evaluate over.\n\n"
          "Returns:\n"
          "    str: The value evaluated as a string, or the empty string if error occurs.");

  xpq.def("evaluate_node_set", &xpath_query::evaluate_node_set, py::arg("node"),
          "\tEvaluate the expression as a node set in the specified context; performs type conversion if necessary.")
      .def(
          "evaluate_node_set",
          [](const xpath_query &self, const xml_node &node) { return self.evaluate_node_set(node); }, py::arg("node"),
          "\tEvaluate the expression as a node set in the specified context; performs type conversion if necessary.\n\n"
          "Args:\n"
          "    node (typing.Union[XPathNode, XMLNode]): The node to evaluate over.\n\n"
          "Returns:\n"
          "    XPathNodeSet: The value evaluated as a node set, or empty node set if error occurs.\n\n"
          "See Also:\n"
          "    :meth:`XMLNode.select_nodes`");

  xpq.def("evaluate_node", &xpath_query::evaluate_node, py::arg("node"),
          "\tEvaluate the expression as a node set in the specified context; performs type conversion if necessary.")
      .def(
          "evaluate_node", [](const xpath_query &self, const xml_node &node) { return self.evaluate_node(node); },
          py::arg("node"),
          "\tEvaluate the expression as a node set in the specified context; performs type conversion if necessary.\n\n"
          "Args:\n"
          "    node (typing.Union[XPathNode, XMLNode]): The node to evaluate over.\n\n"
          "Returns:\n"
          "    XPathNode: The first node evaluated as a node set, or empty node if error occurs.\n\n"
          "See Also:\n"
          "    :meth:`XMLNode.select_node`");

  xpq.def("result", &xpath_query::result,
          R"doc(
          Return the parsing result.

          Returns:
              XPathParseResult: The parsing result.
          )doc");

  //
  // pugi::xpath_node
  //
  xpn.def(py::init<>(), "\tInitialize ``XPathNode`` as an empty XPath node.")
      .def(py::init<const xml_node &>(), py::arg("node"), "\tInitialize ``XPathNode`` with the node.")
      .def(py::init<const xml_attribute &, const xml_node &>(), py::arg("attribute"), py::arg("parent"),
           "\tInitialize ``XPathNode`` with the attribute and its parent node.\n\n"
           "Args:\n"
           "    node (XMLNode): The node to evaluate over.\n"
           "    attribute (XMLAttribute): The attribute to evaluate over.\n"
           "    parent (XMLNode): The parent node of *attribute*.");

  xpn.def(
      "__bool__", [](const xpath_node &self) -> bool { return self; },
      R"doc(
      Determine if this XPath node is not empty.

      Returns:
          bool: :obj:`True` if XPath node is not empty, :obj:`False` otherwise.
      )doc");

  xpn.def(
         "__eq__", [](const xpath_node &self, const xpath_node &other) { return self == other; }, py::is_operator(),
         py::arg("other"), "\tReturn self == other.")
      .def(
          "__eq__", [](const xpath_node &self, const xml_node &other) { return self == other; }, py::is_operator(),
          py::arg("other"),
          "\tReturn self == other.\n\n"
          "Args:\n"
          "    other (typing.Union[XPathNode, XMLNode]): The node to compare.\n\n"
          "Returns:\n"
          "    bool: The result of comparing pointers of internal objects.");

  xpn.def(
         "__ne__", [](const xpath_node &self, const xpath_node &other) { return self != other; }, py::is_operator(),
         py::arg("other"), "\tReturn self != other.")
      .def(
          "__ne__", [](const xpath_node &self, const xml_node &other) { return self != other; }, py::is_operator(),
          py::arg("other"),
          "\tReturn self != other.\n\n"
          "Args:\n"
          "    other (typing.Union[XPathNode, XMLNode]): The node to compare.\n\n"
          "Returns:\n"
          "    bool: The result of comparing pointers of internal objects.");

  xpn.def("node", &xpath_node::node,
          R"doc(
          Return the node if any.

          Returns:
              XMLNode: The node if any, empty node otherwise.
          )doc");

  xpn.def("attribute", &xpath_node::attribute,
          R"doc(
          Return the attribute if any.

          Returns:
              XMLAttribute: The attribute if any, empty attribute otherwise.
          )doc");

  xpn.def("parent", &xpath_node::parent,
          R"doc(
          Return the parent node.

          Returns:
              XMLNode: The parent of node.
          )doc");

  //
  // pugi::xpath_node_set
  //
  py::enum_<xpath_node_set::type_t>(xpns, "Type", "Collection type.")
      .value("TYPE_UNSORTED", xpath_node_set::type_unsorted, "Not ordered.")
      .value("TYPE_SORTED", xpath_node_set::type_sorted, "Sorted by document order (ascending).")
      .value("TYPE_SORTED_REVERSE", xpath_node_set::type_sorted_reverse, "Sorted by document order (descending).")
      .export_values();

  xpns.def(py::init<>(), "\tInitialize ``XPathNodeSet`` as an empty collection.")
      .def(py::init<const xpath_node_set &>(), py::arg("other"),
           "\tInitialize ``XPathNodeSet`` with a copy of the collection.\n\n"
           "Args:\n"
           "    other (XPathNodeSet): The collection to copy.");

  xpns.def(
          "__getitem__",
          [](const xpath_node_set &self, long long index) -> const xpath_node & {
            if (index < 0) {
              index += self.size();
            }
            if (index < 0 || static_cast<size_t>(index) >= self.size()) {
              throw py::index_error("index out of range: " + std::to_string(index));
            }
            return self[index];
          },
          py::arg("index"), "\tReturn the XPath node at the specified index from the collection.")
      .def(
          "__getitem__",
          [](const xpath_node_set &self, const py::slice &slice) {
            size_t start = 0, stop = 0, step = 0, slice_length = 0;
            if (!slice.compute(self.size(), &start, &stop, &step, &slice_length)) {
              throw py::error_already_set();
            }
            std::vector<xpath_node> result(slice_length);
            for (size_t n = 0; n < slice_length; ++n) {
              result[n] = self[start];
              start += step;
            }
            return result;
          },
          py::arg("slice"),
          "\tReturn a list of XPath nodes at the specified :obj:`slice` from the collection.\n\n"
          "Args:\n"
          "    index (int): An index to specify position.\n"
          "    slice (slice): A slice object to specify range.\n\n"
          "Returns:\n"
          "    typing.Union[XPathNode, typing.List[XPathNode]]: The XPath node(s) at the specified index/slice from "
          "collection.");

  options.disable_function_signatures();
  xpns.def(
      "__iter__", [](const xpath_node_set &self) { return py::make_iterator(self.begin(), self.end()); },
      py::keep_alive<0, 1>(),
      R"doc(
      __iter__(self: pugixml.pugi.XPathNodeSet) -> typing.Iterator[XPathNode]

      Return an iterator for this collection of XPath nodes.

      Returns:
          typing.Iterator[XPathNode]: A new iterator for collection of XPath nodes.
      )doc");
  options.enable_function_signatures();

  xpns.def("__len__", &xpath_node_set::size,
           R"doc(
           Return the collection size.

           This is equivalent to :meth:`.size`.

           Returns:
               int: The collection size.
           )doc");

  xpns.def("type", &xpath_node_set::type,
           R"doc(
           Return the collection type.

           Returns:
               XPathNodeSet.Type: The collection type.
           )doc");

  xpns.def("size", &xpath_node_set::size,
           R"doc(
           Return the collection size.

           Returns:
               int: The collection size.
           )doc");

  // xpath_node_set::begin()
  // xpath_node_set::end()

  xpns.def("sort", &xpath_node_set::sort, py::arg("reverse") = false,
           R"doc(
           Sort the collection in ascending/descending order by document order.

           Args:
               reverse (bool): If :obj:`True`, sort in descending order.
           )doc");

  xpns.def("first", &xpath_node_set::first,
           R"doc(
           Return the first node in the collection by document order.

           Returns:
               XPathNode: The first node in the collection, or empty node if the collection is empty.
           )doc");

  xpns.def("empty", &xpath_node_set::empty,
           R"doc(
           Determine if this collection is empty.

           Returns:
               bool: :obj:`True` if collection is empty, :obj:`False` otherwise.
           )doc");

  //
  // BytesWriter
  //
  struct BytesWriter : public xml_writer {
    std::string contents;
    void write(const void *data, size_t size) override { contents.append(static_cast<const char *>(data), size); }
  };

  py::class_<BytesWriter, xml_writer>(m, "BytesWriter", R"doc(
      (pugixml-python only) :class:`XMLWriter` implementation for :obj:`bytes`.

      See Also:
          :meth:`XMLNode.print`

      Examples:
          >>> from pugixml import pugi
          >>> doc = pugi.XMLDocument()
          >>> doc.append_child('node')
          >>> writer = pugi.BytesWriter()
          >>> doc.print(writer, flags=pugi.FORMAT_RAW, encoding=pugi.ENCODING_UTF32_BE)
          >>> writer.getvalue().decode('utf-32be')
          '<node/>'
      )doc")
      .def(py::init<>(), "Initialize ``BytesWriter``.")
      .def(
          "__len__", [](const BytesWriter &self) { return self.contents.size(); }, R"doc(
            Return the contents size in bytes.

            Returns:
                int: The contents size in bytes.
            )doc")
      .def(
          "getvalue", [](const BytesWriter &self) { return py::bytes(self.contents); }, R"doc(
          Return the entire contents of the buffer.

          Returns:
              bytes: The entire contents of the buffer.
          )doc");

  //
  // FileWriter
  //
  struct FileWriter : public xml_writer {
    std::ofstream file;
    FileWriter(const fs::path &path) {
      try {
        file.open(path, std::ios_base::out | std::ios_base::binary);
        file.exceptions(std::ios_base::failbit | std::ios_base::badbit);
      } catch (const std::exception &e) {
        PyErr_SetString(PyExc_OSError, e.what());
        throw py::error_already_set();
      }
    }
    void close() {
      if (file.is_open()) {
        file.close();
      }
    }
    void write(const void *data, size_t size) override {
      try {
        file.write(static_cast<const char *>(data), size);
      } catch (const std::exception &e) {
        PyErr_SetString(PyExc_OSError, e.what());
        throw py::error_already_set();
      }
    }
  };

  py::class_<FileWriter, xml_writer>(m, "FileWriter", R"doc(
      (pugixml-python only) :class:`XMLWriter` implementation for a file.

      Raises:
          OSError: When a file fails to open or write.

      See Also:
          :meth:`XMLDocument.save`, :meth:`XMLNode.print`

      Examples:
          >>> from contextlib import closing
          >>> from pugixml import pugi
          >>> doc = pugi.XMLDocument()
          >>> doc.load_string('<node><child>\U0001f308</child></node>')
          >>> with closing(pugi.FileWriter('tree.xml')) as writer:
          ...     doc.save(writer)
      )doc")
      .def(py::init<const fs::path &>(), py::arg("file"), R"doc(
        Initialize ``FileWriter``.

        Open a file for writing and associate it with this object.

        Args:
            file (os.PathLike): The path-like object of the file to save the XML document or a single subtree.

        Raises:
            OSError: When a file fails to open.
        )doc")
      .def("close", &FileWriter::close, "Close the associated file.");

  //
  // PrintWriter
  //
  struct PrintWriter : public xml_writer {
    void write(const void *data, size_t size) override {
      auto h = PyUnicode_FromStringAndSize(static_cast<const char *>(data), size);
      if (h == nullptr) {
        throw py::error_already_set();
      }
      py::print(py::str(h), py::arg("end") = "");
    }
  };

  py::class_<PrintWriter, xml_writer>(m, "PrintWriter", R"doc(
      (pugixml-python only) :class:`XMLWriter` implementation for :obj:`sys.stdout`.

      Note:
          ``PrintWriter`` works only with UTF-8 encoding.

      See Also:
          :meth:`XMLNode.print`

      Examples:
          >>> from pugixml import pugi
          >>> doc = pugi.XMLDocument()
          >>> doc.append_child('node')
          >>> doc.child('node').append_child('child')
          >>> doc.print(pugi.PrintWriter(), indent=' ')
          <node>
           <child />
          </node>
      )doc")
      .def(py::init<>(), "Initialize ``PrintWriter``.");

  //
  // StringWriter
  //
  struct StringWriter : public xml_writer {
    std::string contents;
    void write(const void *data, size_t size) override { contents.append(static_cast<const char *>(data), size); }
  };

  py::class_<StringWriter, xml_writer>(m, "StringWriter", R"doc(
      (pugixml-python only) :class:`XMLWriter` implementation for string.

      See Also:
          :meth:`XMLNode.print`

      Examples:
          >>> from pugixml import pugi
          >>> doc = pugi.XMLDocument()
          >>> doc.append_child('node')
          >>> writer = pugi.StringWriter()
          >>> doc.print(writer, flags=pugi.FORMAT_RAW)
          >>> writer.getvalue()
          '<node/>'
          >>> writer = pugi.StringWriter()
          >>> doc.print(writer, flags=pugi.FORMAT_RAW, encoding=pugi.ENCODING_UTF32_LE)
          >>> writer.getvalue()
          '<\x00\x00\x00n\x00\x00\x00o\x00\x00\x00d\x00\x00\x00e\x00\x00\x00/\x00\x00\x00>\x00\x00\x00'
          >>> writer.getvalue('utf-32le')
          '<node/>'
      )doc")
      .def(py::init<>(), "Initialize ``StringWriter``.")
      .def(
          "__len__", [](const StringWriter &self) { return self.contents.size(); }, R"doc(
            Return the contents size in bytes.

            Returns:
                int: The contents size in bytes.
            )doc")
      .def(
          "getvalue",
          [](const StringWriter &self, const char *encoding, const char *errors) {
            auto buf = py::bytes(self.contents);
            auto h = PyCodec_Decode(buf.ptr(), encoding, errors);
            if (h == nullptr) {
              throw py::error_already_set();
            }
            return py::str(h);
          },
          py::arg("encoding").none(false) = "utf-8", py::arg("errors") = "strict",
          R"doc(
          Return a :obj:`str` containing the entire contents of the buffer.

          Args:
              encoding (str): The codec registered for encoding to decode the buffer.
              errors (str): The desired error handling scheme. See :func:`codecs.decode` for details.

          Returns:
              str: The entire contents of the buffer.
          )doc");

  //
  // pugixml.pugi.limits submodule
  //
  auto m2 = m.def_submodule("limits");

  m2.doc() = "Maximum and minimum finite values.";

  m2.attr("DBL_MAX") = std::numeric_limits<double>::max();
  m2.attr("DBL_MIN") = std::numeric_limits<double>::min();
  m2.attr("FLT_MAX") = std::numeric_limits<float>::max();
  m2.attr("FLT_MIN") = std::numeric_limits<float>::min();
  m2.attr("INT_MAX") = std::numeric_limits<int>::max();
  m2.attr("INT_MIN") = std::numeric_limits<int>::min();
  m2.attr("LLONG_MAX") = std::numeric_limits<long long>::max();
  m2.attr("LLONG_MIN") = std::numeric_limits<long long>::min();
  m2.attr("UINT_MAX") = std::numeric_limits<unsigned int>::max();
  m2.attr("ULLONG_MAX") = std::numeric_limits<unsigned long long>::max();
}
