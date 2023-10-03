import os
import tempfile
from pathlib import Path

import pytest

from pugixml import pugi


class _TestWriter(pugi.XMLWriter):
    def __init__(self) -> None:
        super().__init__()
        self._contents = b""

    def getvalue(self) -> bytes:
        return self._contents

    def write(self, data: bytes, size: int) -> None:
        assert len(data) == size
        self._contents += data


here = Path(__file__).parent
testdata = (
    here / ".." / "src" / "third_party" / "pugixml" / "tests" / "data"
).resolve()


# https://github.com/zeux/pugixml/blob/master/tests/test_document.cpp
# document_element()
def test_document_element():
    doc = pugi.XMLDocument()

    node = doc.document_element()
    assert isinstance(node, pugi.XMLNode)
    assert node.empty()
    assert node == pugi.XMLNode()

    doc.load_string(
        "<?xml version='1.0'?><node><child/></node><!---->",
        pugi.PARSE_DEFAULT | pugi.PARSE_DECLARATION | pugi.PARSE_COMMENTS,
    )

    node = doc.document_element()
    assert isinstance(node, pugi.XMLNode)
    assert not node.empty()
    assert node == doc.child("node")


def test_hash_value():
    doc = pugi.XMLDocument()

    assert doc.hash_value() > 0
    assert hash(doc) == doc.hash_value()


# https://github.com/zeux/pugixml/blob/master/tests/test_document.cpp
# document_contents_preserve()
def test_load_buffer():
    doc = pugi.XMLDocument()

    contents = "<?xml?><node/>"  # type: str | bytes
    result = doc.load_buffer(contents, len(contents))
    assert isinstance(result, pugi.XMLParseResult)
    assert result.status == pugi.STATUS_OK
    assert result.offset == 0
    assert result.encoding == pugi.ENCODING_UTF8

    writer = pugi.StringWriter()
    doc.print(writer, indent="", flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<node/>"

    with open(testdata / "utftest_utf16_be_clean.xml", "rb") as f:
        contents = f.read()
        result = doc.load_buffer(
            contents,
            len(contents),
            options=pugi.PARSE_DEFAULT
            | pugi.PARSE_WS_PCDATA
            | pugi.PARSE_DECLARATION
            | pugi.PARSE_COMMENTS,
            encoding=pugi.ENCODING_UTF16_BE,
        )
        assert result.status == pugi.STATUS_OK
        assert result.offset == 0
        assert result.encoding == pugi.ENCODING_UTF16_BE

        with tempfile.TemporaryDirectory(prefix="pugixml-") as temp:
            path = Path(temp, "test_load_buffer-{}.xml".format(os.getpid()))
            assert doc.save_file(
                path,
                flags=pugi.FORMAT_RAW
                | pugi.FORMAT_NO_DECLARATION
                | pugi.FORMAT_WRITE_BOM,
                encoding=pugi.ENCODING_UTF16_BE,
            )

            with open(path, "rb") as f2:
                contents2 = f2.read()
                assert contents2 == contents


def test_load_file():
    doc = pugi.XMLDocument()

    result = doc.load_file(str(testdata / "small.xml"))  # string
    assert isinstance(result, pugi.XMLParseResult)
    assert result.status == pugi.STATUS_OK
    assert result.offset == 0
    assert result.encoding == pugi.ENCODING_UTF8

    writer = pugi.StringWriter()
    doc.print(writer, indent="", flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<node/>"

    result = doc.load_file(testdata / "small.xml")  # file-like object
    assert isinstance(result, pugi.XMLParseResult)
    assert result.status == pugi.STATUS_OK
    assert result.offset == 0
    assert result.encoding == pugi.ENCODING_UTF8

    writer = pugi.StringWriter()
    doc.print(writer, indent="", flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<node/>"

    result = doc.load_file(
        testdata / "small.xml",
        options=pugi.PARSE_DEFAULT,
        encoding=pugi.ENCODING_AUTO,
    )
    assert result.status == pugi.STATUS_OK
    assert result.offset == 0
    assert result.encoding == pugi.ENCODING_UTF8

    writer = pugi.StringWriter()
    doc.print(writer, indent="", flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<node/>"


def test_load_file_fail():
    doc = pugi.XMLDocument()

    with pytest.raises(TypeError):
        doc.load_file(object())

    result = doc.load_file(testdata / "filedoesnotexist")
    assert result.status == pugi.STATUS_FILE_NOT_FOUND


def test_load_string():
    doc = pugi.XMLDocument()

    result = doc.load_string(
        "<?xml?><!DOCTYPE><?pi?><!--comment--><node>pcdata<![CDATA[cdata]]></node>",
        pugi.PARSE_DEFAULT
        | pugi.PARSE_PI
        | pugi.PARSE_COMMENTS
        | pugi.PARSE_DECLARATION
        | pugi.PARSE_DOCTYPE,
    )
    assert isinstance(result, pugi.XMLParseResult)
    assert result.status == pugi.STATUS_OK
    assert result.offset == 0
    assert result.encoding == pugi.ENCODING_UTF8
    description = result.description()
    assert isinstance(description, str)
    assert description == "No error"

    assert repr(result).startswith("<XMLParseResult status=STATUS_OK ")
    assert repr(result).endswith(" description='No error'>")

    writer = pugi.StringWriter()
    doc.print(writer, indent="", flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == (
        "<?xml?>"
        "<!DOCTYPE >"
        "<?pi?>"
        "<!--comment-->"
        "<node>pcdata<![CDATA[cdata]]></node>"
    )


def test_load_string_fail():
    doc = pugi.XMLDocument()

    result = doc.load_string("<foo><bar/>")
    assert isinstance(result, pugi.XMLParseResult)
    assert result.status == pugi.STATUS_END_ELEMENT_MISMATCH
    assert result.offset == 10
    description = result.description()
    assert isinstance(description, str)
    assert description == "Start-end tags mismatch"

    assert repr(result).startswith(
        "<XMLParseResult status=STATUS_END_ELEMENT_MISMATCH "
    )
    assert repr(result).endswith(" description='Start-end tags mismatch'>")

    with pytest.raises(TypeError):
        doc.load_string(None)


# https://github.com/zeux/pugixml/blob/master/tests/test_parse.cpp
# TEST(parse_merge_pcdata)
def test_parse_merge_pcdata():
    doc = pugi.XMLDocument()

    flags = pugi.PARSE_MERGE_PCDATA
    result = doc.load_string(
        "<node>"
        "First text<!-- here is a mesh node -->Second text"
        "<![CDATA[someothertext]]>some more text<?include somedata?>Last text"
        "</node>",
        flags,
    )
    assert isinstance(result, pugi.XMLParseResult)
    assert result.status == pugi.STATUS_OK

    child = doc.child("node")
    assert child.first_child() == child.last_child()
    assert child.first_child().type() == pugi.NODE_PCDATA

    writer = pugi.StringWriter()
    doc.print(writer, indent="", flags=pugi.FORMAT_RAW)
    assert (
        writer.getvalue()
        == "<node>First textSecond textsome more textLast text</node>"
    )


def test_parse_result():
    result = pugi.XMLParseResult()
    assert not result
    assert result.status == pugi.STATUS_INTERNAL_ERROR
    assert result.offset == 0
    description = result.description()
    assert isinstance(description, str)
    assert description == "Internal error occurred"

    assert repr(result).startswith(
        "<XMLParseResult status=STATUS_INTERNAL_ERROR "
    )
    assert repr(result).endswith(" description='Internal error occurred'>")


def test_repr():
    doc = pugi.XMLDocument()

    assert repr(doc).startswith("<XMLDocument hash=0x")
    assert repr(doc).endswith(">")


def test_reset():
    doc = pugi.XMLDocument()

    doc.append_child().set_name("node")
    writer = pugi.StringWriter()
    doc.print(writer, indent="", flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<node/>"

    doc.reset()
    writer = pugi.StringWriter()
    doc.print(writer, indent="", flags=pugi.FORMAT_RAW)
    assert len(writer.getvalue()) == 0

    doc.load_string("<node><child/></node>")
    doc2 = pugi.XMLDocument()
    doc2.reset(doc)
    writer = pugi.StringWriter()
    doc2.print(writer, indent="", flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<node><child/></node>"


# https://github.com/zeux/pugixml/blob/master/tests/test_document.cpp
# document_save_bom()
def test_save():
    doc = pugi.XMLDocument()

    doc.load_string("<node/>")
    writer = pugi.StringWriter()
    doc.save(
        writer,
        flags=pugi.FORMAT_NO_DECLARATION | pugi.FORMAT_RAW,
        encoding=pugi.ENCODING_UTF8,
    )
    assert writer.getvalue() == "<node/>"

    doc.load_string("<n/>")
    writer = _TestWriter()
    doc.save(
        writer,
        flags=pugi.FORMAT_NO_DECLARATION
        | pugi.FORMAT_RAW
        | pugi.FORMAT_WRITE_BOM,
        encoding=pugi.ENCODING_UTF16_BE,
    )
    assert writer.getvalue() == b"\xfe\xff\x00<\x00n\x00/\x00>"

    writer = _TestWriter()
    with pytest.raises(TypeError):
        doc.save(writer, indent=None)  # indent is None


def test_save_file():
    doc = pugi.XMLDocument()

    doc.load_string("<node><child/></node>")
    with tempfile.TemporaryDirectory(prefix="pugixml-") as temp:
        path = Path(temp, "test_save_file-{}.xml".format(os.getpid()))
        assert doc.save_file(str(path))  # string
        with open(path, "rb") as f:
            contents = f.read()
            assert (
                contents
                == b'<?xml version="1.0"?>\n<node>\n\t<child />\n</node>\n'
            )

        assert doc.save_file(
            path, indent="", flags=pugi.FORMAT_RAW, encoding=pugi.ENCODING_UTF8
        )  # path-like object
        with open(path, "rb") as f:
            contents = f.read()
            assert contents == b'<?xml version="1.0"?><node><child/></node>'


def test_save_file_fail():
    doc = pugi.XMLDocument()

    doc.load_string("<node><child/></node>")
    with tempfile.TemporaryDirectory(prefix="pugixml-") as temp:
        with pytest.raises(TypeError):
            doc.save_file(object())

        path = Path(temp, "test_save_file_fail-{}.xml".format(os.getpid()))
        with pytest.raises(TypeError):
            doc.save_file(path, indent=None)  # indent is None
