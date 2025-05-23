from __future__ import annotations

import os
import tempfile
from contextlib import closing
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


# https://github.com/zeux/pugixml/blob/master/tests/test_dom_traverse.cpp
class _TestWalker(pugi.XMLTreeWalker):
    def __init__(self, stop_count: int = 0) -> None:
        super().__init__()
        self._call_count = 0
        self._stop_count = stop_count
        self._log = ""

    def begin(self, node: pugi.XMLNode) -> bool:
        self._log += f"|{self.depth()} <{node.name()}={node.value()}"
        self._call_count += 1
        return self._call_count != self._stop_count  # and super().begin(node)

    @property
    def call_count(self) -> int:
        return self._call_count

    def end(self, node: pugi.XMLNode) -> bool:
        self._log += f"|{self.depth()} >{node.name()}={node.value()}"
        self._call_count += 1
        return self._call_count != self._stop_count

    def for_each(self, node: pugi.XMLNode) -> bool:
        self._log += f"|{self.depth()} !{node.name()}={node.value()}"
        self._call_count += 1
        return self._call_count != self._stop_count  # and super().end(node)

    @property
    def log(self) -> str:
        return self._log


def test_append_attribute() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><child/></node>")
    node = doc.child("node")

    assert not pugi.XMLNode().append_attribute("a")
    assert not doc.append_attribute("a")

    a1 = node.append_attribute("a1")
    assert isinstance(a1, pugi.XMLAttribute)
    assert a1.set_value("v1")

    a2 = node.append_attribute("a2")
    assert isinstance(a2, pugi.XMLAttribute)
    assert a2.set_value("v2")

    a3 = node.child("child").append_attribute("a3")
    assert isinstance(a3, pugi.XMLAttribute)
    assert a3.set_value("v3")

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == '<node a1="v1" a2="v2"><child a3="v3"/></node>'

    with pytest.raises(TypeError):
        node.append_attribute(None)


# https://github.com/zeux/pugixml/blob/master/tests/test_dom_modify.cpp
def test_append_buffer() -> None:
    doc = pugi.XMLDocument()

    data = "<child1 id='1' /><child2>text</child2>"  # type: str | bytes
    result = doc.append_buffer(data, len(data))
    assert isinstance(result, pugi.XMLParseResult)
    assert result.status == pugi.STATUS_OK
    assert result.offset == 0
    assert result.encoding == pugi.ENCODING_UTF8

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == '<child1 id="1"/><child2>text</child2>'

    doc.load_string("<node>test</node>")
    node = doc.child("node")
    data = b"\x00\x00\x00<\x00\x00\x00n\x00\x00\x00/\x00\x00\x00>"
    result = node.append_buffer(data, len(data))
    assert result.status == pugi.STATUS_OK
    assert result.offset == 0
    assert result.encoding == pugi.ENCODING_UTF32_BE

    result = node.append_buffer(
        data, len(data), encoding=pugi.ENCODING_UTF32_BE
    )
    assert result.status == pugi.STATUS_OK
    assert result.offset == 0
    assert result.encoding == pugi.ENCODING_UTF32_BE

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<node>test<n/><n/></node>"


def test_append_child() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node>foo<child/></node>")
    node = doc.child("node")

    n1 = node.append_child()
    assert isinstance(n1, pugi.XMLNode)
    assert n1.set_name("n1")

    n2 = node.append_child()
    assert isinstance(n2, pugi.XMLNode)
    assert n2 != n1
    assert n2.set_name("n2")

    n3 = node.child("child").append_child(pugi.NODE_PCDATA)
    assert isinstance(n3, pugi.XMLNode)
    assert n3 != n2
    assert n3 != n1
    assert n3.set_value("n3")

    n4 = doc.append_child(pugi.NODE_COMMENT)
    assert isinstance(n4, pugi.XMLNode)
    assert n4 != n3
    assert n4 != n2
    assert n4 != n1
    assert n4.set_value("n4")

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == (
        "<node>foo<child>n3</child><n1/><n2/></node><!--n4-->"
    )

    n5 = doc.append_child("n5")
    assert isinstance(n5, pugi.XMLNode)
    assert n5.name() == "n5"
    assert n5.type() == pugi.NODE_ELEMENT
    assert doc.last_child() == n5

    with pytest.raises(TypeError):
        doc.append_child(None)


def test_append_copy_attribute() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node a1='v1'><child a2='v2'/><child/></node>")
    node = doc.child("node")
    child = node.child("child")

    a1 = node.attribute("a1")
    a2 = child.attribute("a2")

    a3 = node.append_copy(a1)
    assert isinstance(a3, pugi.XMLAttribute)
    assert a3 != a2
    assert a3 != a1

    a4 = node.append_copy(a2)
    assert isinstance(a4, pugi.XMLAttribute)
    assert a4 != a3
    assert a4 != a2
    assert a4 != a1

    a5 = node.last_child().append_copy(a1)
    assert isinstance(a5, pugi.XMLAttribute)
    assert a5 != a4
    assert a5 != a3
    assert a5 != a2
    assert a5 != a1

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == (
        '<node a1="v1" a1="v1" a2="v2"><child a2="v2"/><child a1="v1"/></node>'
    )

    a3.set_name("a3")
    a3.set_value("v3")

    a4.set_name("a4")
    a4.set_value("v4")

    a5.set_name("a5")
    a5.set_value("v5")

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == (
        '<node a1="v1" a3="v3" a4="v4"><child a2="v2"/><child a5="v5"/></node>'
    )


def test_append_copy_node() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node>foo<child/></node>")
    node = doc.child("node")

    n1 = node.append_copy(node.first_child())
    assert isinstance(n1, pugi.XMLNode)
    assert n1.value() == "foo"

    n2 = node.append_copy(node.child("child"))
    assert isinstance(n2, pugi.XMLNode)
    assert n2 != n1
    assert n2.name() == "child"

    n3 = node.child("child").append_copy(node.first_child())
    assert isinstance(n3, pugi.XMLNode)
    assert n3 != n2
    assert n3 != n1
    assert n3.value() == "foo"

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == (
        "<node>foo<child>foo</child>foo<child/></node>"
    )


def test_append_move() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node>foo<child/></node>")
    node = doc.child("node")

    n1 = node.append_move(node.first_child())
    assert isinstance(n1, pugi.XMLNode)
    assert n1 == node.last_child()
    assert n1.value() == "foo"

    n2 = node.append_move(node.last_child())
    assert isinstance(n2, pugi.XMLNode)
    assert n2 == n1
    assert n2.value() == "foo"

    n3 = node.child("child").append_move(node.last_child())
    assert isinstance(n3, pugi.XMLNode)
    assert n3 == n2
    assert n3 == n1
    assert n3.value() == "foo"

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<node><child>foo</child></node>"


def test_attribute() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node attr1='0' attr2='1'/>")
    node = doc.child("node")

    attr = node.attribute("n")
    assert isinstance(attr, pugi.XMLAttribute)
    assert attr == pugi.XMLAttribute()

    attr = node.attribute("attr1")
    assert isinstance(attr, pugi.XMLAttribute)
    assert attr.name() == "attr1"
    assert attr.value() == "0"

    attr = node.attribute("attr2")
    assert isinstance(attr, pugi.XMLAttribute)
    assert attr.name() == "attr2"
    assert attr.value() == "1"

    with pytest.raises(TypeError):
        _ = node.attribute(None)


def test_attribute_hinted() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node attr1='1' attr2='2' attr3='3' />")
    node = doc.child("node")
    attr1 = node.attribute("attr1")
    attr2 = node.attribute("attr2")
    attr3 = node.attribute("attr3")

    hint = pugi.XMLAttribute()
    assert not pugi.XMLNode().attribute("test", hint)
    assert not hint

    assert node.attribute("attr2", hint) == attr2
    assert hint == attr3
    assert node.attribute("attr3", hint) == attr3
    assert not hint

    assert node.attribute("attr1", hint) == attr1
    assert hint == attr2
    assert node.attribute("attr2", hint) == attr2
    assert hint == attr3
    assert node.attribute("attr1", hint) == attr1
    assert hint == attr2
    assert node.attribute("attr1", hint) == attr1
    assert hint == attr2

    assert not node.attribute("attr", hint)
    assert hint == attr2

    with pytest.raises(TypeError):
        _ = node.attribute(None, hint)


def test_attributes() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node1 attr1='value1' attr2='value2' /><node2 />")
    node = doc.child("node1")

    attrs = doc.attributes()
    assert isinstance(attrs, pugi.XMLAttributeIterator)
    _ = iter(attrs)  # object is iterable
    assert len(attrs) == 0
    with pytest.raises(IndexError):
        _ = attrs[0]

    attrs = node.attributes()
    assert isinstance(attrs, pugi.XMLAttributeIterator)
    _ = iter(attrs)  # object is iterable
    assert len(attrs) == 2
    assert attrs[0] == node.first_attribute()
    assert attrs[1] == node.last_attribute()
    with pytest.raises(IndexError):
        _ = attrs[2]
    assert attrs[-1] == node.last_attribute()
    assert attrs[-2] == node.first_attribute()
    with pytest.raises(IndexError):
        _ = attrs[-3]
    assert attrs[:] == [node.first_attribute(), node.last_attribute()]
    with pytest.raises(ValueError, match="slice step cannot be zero"):
        _ = attrs[::0]
    assert list(reversed(attrs)) == [
        node.last_attribute(),
        node.first_attribute(),
    ]


def test_bool() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node/>")

    assert not pugi.XMLNode()
    assert doc.child("node")


def test_bytes_writer() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node/>")

    writer = pugi.BytesWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW, encoding=pugi.ENCODING_UTF32_BE)

    assert len(writer) == 28
    assert writer.getvalue().decode("utf-32be") == "<node/>"


def test_child() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><child1/><child2/></node>")

    node = doc.child("node")
    assert isinstance(node, pugi.XMLNode)
    assert node.name() == "node"

    child1 = node.child("child1")
    assert isinstance(child1, pugi.XMLNode)
    assert child1.name() == "child1"

    child2 = node.child("child2")
    assert isinstance(child2, pugi.XMLNode)
    assert child2.name() == "child2"

    with pytest.raises(TypeError):
        _ = node.child(None)


def test_child_value() -> None:
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node>"
        "<novalue/>"
        "<child1>value1</child1>"
        "<child2>value2<n/></child2>"
        "<child3><![CDATA[value3]]></child3>"
        "value4</node>"
    )
    node = doc.child("node")

    assert node.child_value() == "value4"
    assert node.child("child1").child_value() == "value1"
    assert node.child("child2").child_value() == "value2"
    assert node.child("child3").child_value() == "value3"

    assert node.child_value("child3") == "value3"
    assert len(node.child_value("novalue")) == 0

    with pytest.raises(TypeError):
        _ = node.child_value(None)


# https://github.com/zeux/pugixml/blob/master/tests/test_dom_traverse.cpp
# dom_ranged_for()
def test_children() -> None:
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node attr1='1' attr2='2'>"
        "<test>3</test>"
        "<fake>5</fake>"
        "<test>4</test>"
        "</node>"
    )
    index = 1
    for n in doc.children():
        for a in n.attributes():
            assert a.as_int() == index
            index += 1
        for c in n.children("test"):
            assert c.text().as_int() == index
            index += 1
    assert index == 5

    with pytest.raises(TypeError):
        _ = doc.children(None)


# https://github.com/zeux/pugixml/blob/master/tests/test_dom_traverse.cpp
# dom_node_named_iterator
def test_children_name() -> None:
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node>"
        "<node1><child/></node1>"
        "<node2><child/><child/></node2>"
        "<node3/>"
        "<node4><child/><x/></node4>"
        "</node>"
    )

    node1 = doc.child("node").child("node1")
    node2 = doc.child("node").child("node2")
    node3 = doc.child("node").child("node3")
    node4 = doc.child("node").child("node4")

    node = doc.first_child()
    assert node == doc.last_child()

    r0 = doc.children()
    assert isinstance(r0, pugi.XMLNodeIterator)
    _ = iter(r0)  # object is iterable
    assert list(r0) == [node]
    assert len(r0) == 1
    assert r0[0] == node
    with pytest.raises(IndexError):
        _ = r0[1]
    assert r0[-1] == node
    with pytest.raises(IndexError):
        _ = r0[-2]

    r0 = node.children()
    assert isinstance(r0, pugi.XMLNodeIterator)
    _ = iter(r0)  # object is iterable
    assert list(r0) == [node1, node2, node3, node4]
    assert len(r0) == 4
    assert r0[0] == node1
    assert r0[1] == node2
    assert r0[2] == node3
    assert r0[3] == node4
    with pytest.raises(IndexError):
        _ = r0[4]
    assert r0[-1] == node4
    assert r0[-2] == node3
    assert r0[-3] == node2
    assert r0[-4] == node1
    with pytest.raises(IndexError):
        _ = r0[-5]
    assert r0[1:3] == [node2, node3]
    with pytest.raises(ValueError, match="slice step cannot be zero"):
        _ = r0[::0]
    assert list(reversed(r0)) == [node4, node3, node2, node1]

    r1 = node1.children("child")
    r2 = node2.children("child")
    r3 = node3.children("child")
    r4 = node4.children("child")
    assert isinstance(r1, pugi.XMLNamedNodeIterator)
    assert isinstance(r2, pugi.XMLNamedNodeIterator)
    assert isinstance(r3, pugi.XMLNamedNodeIterator)
    assert isinstance(r4, pugi.XMLNamedNodeIterator)
    _ = iter(r1)  # object is iterable
    _ = iter(r2)  # object is iterable
    _ = iter(r3)  # object is iterable
    _ = iter(r4)  # object is iterable

    assert len(r1) == 1
    assert r1[0] == node1.first_child() == node1.last_child()
    with pytest.raises(IndexError):
        _ = r1[1]
    assert r1[-1] == node1.first_child() == node1.last_child()
    with pytest.raises(IndexError):
        _ = r1[-2]

    assert len(r2) == 2
    assert r2[0] == node2.first_child()
    assert r2[1] == node2.last_child()
    assert r2[:] == [node2.first_child(), node2.last_child()]
    with pytest.raises(ValueError, match="slice step cannot be zero"):
        _ = r2[::0]
    assert list(reversed(r2)) == [node2.last_child(), node2.first_child()]

    assert len(r3) == 0

    assert len(r4) == 1
    assert r4[0] == node4.first_child()
    assert r4[0] != node4.last_child()


def test_empty() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node/>")

    assert pugi.XMLNode().empty()
    assert not doc.child("node").empty()


def test_file_writer() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><child>\U0001f308</child></node>")
    expected = "<node>\n\t<child>\U0001f308</child>\n</node>\n"

    with tempfile.TemporaryDirectory(prefix="pugixml-") as temp:
        file = Path(temp, f"test_file_writer-{os.getpid()}.xml")

        with closing(pugi.FileWriter(file)) as writer:
            doc.print(writer)
        with open(file, "rb") as f:
            assert f.read().decode() == expected

        with closing(pugi.FileWriter(file)) as writer:
            doc.print(writer, encoding=pugi.ENCODING_UTF16)
        with open(file, "rb") as f:
            assert f.read().decode("utf-16") == expected

        writer = pugi.FileWriter(file)
        doc.print(writer, encoding=pugi.ENCODING_UTF32)
        del writer
        with open(file, "rb") as f:
            assert f.read().decode("utf-32") == expected

        writer = pugi.FileWriter(file)
        writer.close()
        writer.close()
        del writer

        writer = pugi.FileWriter(file)
        del writer

        with pytest.raises(
            OSError,
            match="(stream error)|(iostream_category error)|(basic_ios::clear)",
        ):
            _ = pugi.FileWriter(".")

        writer = pugi.FileWriter(file)
        writer.close()
        with pytest.raises(
            OSError,
            match="(stream error)|(iostream_category error)|(basic_ios::clear)",
        ):
            doc.print(writer)


def test_find_attribute() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node attr1='0' attr2='1'/>")
    node = doc.child("node")

    assert doc.find_attribute(lambda _: True) == pugi.XMLAttribute()
    assert node.find_attribute(lambda _: True) == node.first_attribute()
    assert node.find_attribute(lambda _: False) == pugi.XMLAttribute()

    assert (
        node.find_attribute(lambda xattr: xattr.name().startswith("attr2"))
        == node.last_attribute()
    )
    assert (
        node.find_attribute(lambda xattr: xattr.name().startswith("attr"))
        == node.first_attribute()
    )


def test_find_child() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><child1/><child2/></node>")
    node = doc.child("node")

    assert (
        node.child("node").child("child1").find_child(lambda _: True)
        == pugi.XMLNode()
    )
    assert node.find_child(lambda _: True) == node.first_child()
    assert node.find_child(lambda _: False) == pugi.XMLNode()

    assert (
        node.find_child(lambda xnode: xnode.name().startswith("child2"))
        == node.last_child()
    )
    assert (
        node.find_child(lambda xnode: xnode.name().startswith("child"))
        == node.first_child()
    )


def test_find_child_by_attribute() -> None:
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node>"
        "<stub attr='value3' />"
        "<child1 attr='value1'/>"
        "<child2 attr='value2'/>"
        "<child2 attr='value3'/>"
        "</node>"
    )
    node = doc.child("node")

    assert (
        node.find_child_by_attribute("child2", "attr", "value3")
        == node.last_child()
    )
    assert (
        node.find_child_by_attribute("child2", "attr3", "value3")
        == pugi.XMLNode()
    )
    assert node.find_child_by_attribute("attr", "value2") == node.child(
        "child2"
    )
    assert node.find_child_by_attribute("attr3", "value") == pugi.XMLNode()

    with pytest.raises(TypeError):
        _ = node.find_child_by_attribute(
            None, "attr", "value3"
        )  # name is None

    with pytest.raises(TypeError):
        _ = node.find_child_by_attribute(
            "child2", None, "value3"
        )  # attr_name is None

    with pytest.raises(TypeError):
        _ = node.find_child_by_attribute(
            "child2", "attr", None
        )  # attr_value is None

    with pytest.raises(TypeError):
        _ = node.find_child_by_attribute(None, "value2")  # attr_name is None

    with pytest.raises(TypeError):
        _ = node.find_child_by_attribute("attr", None)  # attr_value is None


def test_find_node() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><child1/><child2/></node>")
    node = doc.child("node")

    assert (
        node.child("node").child("child1").find_node(lambda _: True)
        == pugi.XMLNode()
    )
    assert node.find_node(lambda _: True) == node.first_child()
    assert node.find_node(lambda _: False) == pugi.XMLNode()

    assert (
        node.find_node(lambda xnode: xnode.name().startswith("child2"))
        == node.last_child()
    )
    assert (
        node.find_node(lambda xnode: xnode.name().startswith("child"))
        == node.first_child()
    )

    assert (
        doc.find_node(lambda xnode: xnode.name().startswith("child"))
        == node.first_child()
    )
    assert (
        doc.find_node(lambda xnode: xnode.name().startswith("child2"))
        == node.last_child()
    )
    assert (
        doc.find_node(lambda xnode: xnode.name().startswith("child3"))
        == pugi.XMLNode()
    )


def test_first_element_by_path() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><child1>text<child2/></child1></node>")
    node = doc.child("node")

    assert doc.first_element_by_path("") == doc
    assert doc.first_element_by_path("/") == doc

    assert doc.first_element_by_path("/node/") == node
    assert doc.first_element_by_path("node/") == node
    assert doc.first_element_by_path("node") == node
    assert doc.first_element_by_path("/node") == node

    assert doc.first_element_by_path("/node/child2") == pugi.XMLNode()

    assert doc.first_element_by_path("\\node\\child1", "\\") == node.child(
        "child1"
    )

    with pytest.raises(TypeError):
        _ = doc.first_element_by_path(None, "/")  # path is None

    with pytest.raises(TypeError):
        _ = doc.first_element_by_path("/", None)  # delimiter is None


def test_first_last_attribute() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node attr1='0' attr2='1'/>")
    node = doc.child("node")

    attr = node.first_attribute()
    assert isinstance(attr, pugi.XMLAttribute)
    assert attr.name() == "attr1"

    attr = node.last_attribute()
    assert isinstance(attr, pugi.XMLAttribute)
    assert attr.name() == "attr2"

    attr = doc.first_attribute()
    assert isinstance(attr, pugi.XMLAttribute)
    assert attr.empty()

    attr = doc.last_attribute()
    assert isinstance(attr, pugi.XMLAttribute)
    assert attr.empty()


def test_first_last_child() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><child1/><child2/></node>")
    node = doc.child("node")

    child = node.first_child()
    assert isinstance(child, pugi.XMLNode)
    assert child.name() == "child1"

    child = node.last_child()
    assert isinstance(child, pugi.XMLNode)
    assert child.name() == "child2"

    child = doc.first_child()
    assert isinstance(child, pugi.XMLNode)
    assert child == node

    child = doc.last_child()
    assert isinstance(child, pugi.XMLNode)
    assert child == node


def test_hash_value() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node/>")
    node = doc.child("node")

    assert pugi.XMLNode().hash_value() == 0
    assert node.hash_value() > 0

    assert hash(node) == node.hash_value()


# def test_iter() -> None:
#     doc = pugi.XMLDocument()
#     doc.load_string(
#         "<?xml?><!DOCTYPE><?pi?><!--comment--><node>pcdata<![CDATA[cdata]]></node>",
#         pugi.PARSE_DEFAULT
#         | pugi.PARSE_PI
#         | pugi.PARSE_COMMENTS
#         | pugi.PARSE_DECLARATION
#         | pugi.PARSE_DOCTYPE,
#     )
#
#     t1 = list(doc)
#     t2 = doc.children()
#     assert len(t2) > 0
#     assert t2 == t1


def test_insert_attribute_after() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node a1='v1'><child a2='v2'/></node>")
    node = doc.child("node")
    child = node.child("child")

    assert (
        pugi.XMLNode().insert_attribute_after("a", pugi.XMLAttribute())
        == pugi.XMLAttribute()
    )

    a1 = node.attribute("a1")
    a2 = child.attribute("a2")

    assert (
        node.insert_attribute_after("a", pugi.XMLAttribute())
        == pugi.XMLAttribute()
    )
    assert node.insert_attribute_after("a", a2) == pugi.XMLAttribute()

    a3 = node.insert_attribute_after("a3", a1)
    assert isinstance(a3, pugi.XMLAttribute)
    assert a3.set_value("v3")

    a4 = node.insert_attribute_after("a4", a1)
    assert isinstance(a4, pugi.XMLAttribute)
    assert a4.set_value("v4")

    a5 = node.insert_attribute_after("a5", a3)
    assert isinstance(a5, pugi.XMLAttribute)
    assert a5.set_value("v5")

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert (
        writer.getvalue()
        == '<node a1="v1" a4="v4" a3="v3" a5="v5"><child a2="v2"/></node>'
    )

    with pytest.raises(TypeError):
        node.insert_attribute_after(None, a1)  # name is None


def test_insert_attribute_before() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node a1='v1'><child a2='v2'/></node>")
    node = doc.child("node")
    child = node.child("child")

    assert (
        pugi.XMLNode().insert_attribute_before("a", pugi.XMLAttribute())
        == pugi.XMLAttribute()
    )

    a1 = node.attribute("a1")
    a2 = child.attribute("a2")

    assert (
        node.insert_attribute_before("a", pugi.XMLAttribute())
        == pugi.XMLAttribute()
    )
    assert node.insert_attribute_before("a", a2) == pugi.XMLAttribute()

    a3 = node.insert_attribute_before("a3", a1)
    assert isinstance(a3, pugi.XMLAttribute)
    assert a3.set_value("v3")

    a4 = node.insert_attribute_before("a4", a1)
    assert isinstance(a4, pugi.XMLAttribute)
    assert a4.set_value("v4")

    a5 = node.insert_attribute_before("a5", a3)
    assert isinstance(a5, pugi.XMLAttribute)
    assert a5.set_value("v5")

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert (
        writer.getvalue()
        == '<node a5="v5" a3="v3" a4="v4" a1="v1"><child a2="v2"/></node>'
    )

    with pytest.raises(TypeError):
        node.insert_attribute_before(None, a1)  # name is None


def test_insert_child_after_name() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node>foo<child/></node>")
    node = doc.child("node")
    child = node.child("child")

    n1 = node.insert_child_after("n1", child)
    assert isinstance(n1, pugi.XMLNode)
    assert n1 != node
    assert n1 != child

    n2 = node.insert_child_after("n2", child)
    assert isinstance(n2, pugi.XMLNode)
    assert n2 != node
    assert n2 != child
    assert n2 != n1

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<node>foo<child/><n2/><n1/></node>"

    with pytest.raises(TypeError):
        node.insert_child_after(None, child)  # name is None


def test_insert_child_after_type() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node>foo<child/></node>")
    node = doc.child("node")
    child = node.child("child")

    n1 = node.insert_child_after(pugi.NODE_ELEMENT, child)
    assert isinstance(n1, pugi.XMLNode)
    assert n1 != node
    assert n1 != child
    assert n1.set_name("n1")

    n2 = node.insert_child_after(pugi.NODE_ELEMENT, child)
    assert isinstance(n2, pugi.XMLNode)
    assert n2 != node
    assert n2 != child
    assert n2 != n1
    assert n2.set_name("n2")

    n3 = node.insert_child_after(pugi.NODE_PCDATA, n2)
    assert isinstance(n3, pugi.XMLNode)
    assert n3 != node
    assert n3 != child
    assert n3 != n2
    assert n3 != n1
    assert n3.set_value("n3")

    n4 = node.insert_child_after(pugi.NODE_PI, node.first_child())
    assert isinstance(n4, pugi.XMLNode)
    assert n4 != node
    assert n4 != child
    assert n4 != n3
    assert n4 != n2
    assert n4 != n1
    assert n4.set_name("n4")

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<node>foo<?n4?><child/><n2/>n3<n1/></node>"


def test_insert_child_before_name() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node>foo<child/></node>")
    node = doc.child("node")
    child = node.child("child")

    n1 = node.insert_child_before("n1", child)
    assert isinstance(n1, pugi.XMLNode)
    assert n1 != node
    assert n1 != child

    n2 = node.insert_child_before("n2", child)
    assert isinstance(n2, pugi.XMLNode)
    assert n2 != node
    assert n2 != child
    assert n2 != n1

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<node>foo<n1/><n2/><child/></node>"

    with pytest.raises(TypeError):
        node.insert_child_before(None, child)  # name is None


def test_insert_child_before_type() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node>foo<child/></node>")
    node = doc.child("node")
    child = node.child("child")

    n1 = node.insert_child_before(pugi.NODE_ELEMENT, child)
    assert isinstance(n1, pugi.XMLNode)
    assert n1 != node
    assert n1 != child
    assert n1.set_name("n1")

    n2 = node.insert_child_before(pugi.NODE_ELEMENT, child)
    assert isinstance(n2, pugi.XMLNode)
    assert n2 != node
    assert n2 != child
    assert n2 != n1
    assert n2.set_name("n2")

    n3 = node.insert_child_before(pugi.NODE_PCDATA, n2)
    assert isinstance(n3, pugi.XMLNode)
    assert n3 != node
    assert n3 != child
    assert n3 != n2
    assert n3 != n1
    assert n3.set_value("n3")

    n4 = node.insert_child_before(pugi.NODE_PI, node.first_child())
    assert isinstance(n4, pugi.XMLNode)
    assert n4 != node
    assert n4 != child
    assert n4 != n3
    assert n4 != n2
    assert n4 != n1
    assert n4.set_name("n4")

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<node><?n4?>foo<n1/>n3<n2/><child/></node>"


def test_insert_copy_after_attribute() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node a1='v1'><child a2='v2'/>text</node>")
    node = doc.child("node")
    child = node.child("child")

    a1 = node.attribute("a1")
    a2 = child.attribute("a2")

    a3 = node.insert_copy_after(a1, a1)
    assert isinstance(a3, pugi.XMLAttribute)
    assert a3 != a2
    assert a3 != a1

    a4 = node.insert_copy_after(a2, a1)
    assert isinstance(a4, pugi.XMLAttribute)
    assert a4 != a3
    assert a4 != a2
    assert a4 != a1

    a5 = node.insert_copy_after(a4, a1)
    assert isinstance(a5, pugi.XMLAttribute)
    assert a5 != a4
    assert a5 != a3
    assert a5 != a2
    assert a5 != a1

    assert child.insert_copy_after(a4, a4) == pugi.XMLAttribute()

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == (
        '<node a1="v1" a2="v2" a2="v2" a1="v1"><child a2="v2"/>text</node>'
    )

    a3.set_name("a3")
    a3.set_value("v3")

    a4.set_name("a4")
    a4.set_value("v4")

    a5.set_name("a5")
    a5.set_value("v5")

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == (
        '<node a1="v1" a5="v5" a4="v4" a3="v3"><child a2="v2"/>text</node>'
    )


def test_insert_copy_after_node() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node>foo<child/></node>")
    node = doc.child("node")
    child = node.child("child")

    n1 = node.insert_copy_after(child, node.first_child())
    assert isinstance(n1, pugi.XMLNode)
    assert n1.name() == "child"

    n2 = node.insert_copy_after(node.first_child(), node.last_child())
    assert n2 != n1
    assert n2.value() == "foo"

    n3 = node.insert_copy_after(node.first_child(), node.first_child())
    assert n3 != n2
    assert n3 != n1
    assert n3.value() == "foo"

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<node>foofoo<child/><child/>foo</node>"


def test_insert_copy_before_attribute() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node a1='v1'><child a2='v2'/>text</node>")
    node = doc.child("node")
    child = node.child("child")

    a1 = node.attribute("a1")
    a2 = child.attribute("a2")

    a3 = node.insert_copy_before(a1, a1)
    assert isinstance(a3, pugi.XMLAttribute)
    assert a3 != a2
    assert a3 != a1

    a4 = node.insert_copy_before(a2, a1)
    assert isinstance(a4, pugi.XMLAttribute)
    assert a4 != a3
    assert a4 != a2
    assert a4 != a1

    a5 = node.insert_copy_before(a4, a1)
    assert isinstance(a5, pugi.XMLAttribute)
    assert a5 != a4
    assert a5 != a3
    assert a5 != a2
    assert a5 != a1

    assert child.insert_copy_before(a4, a4) == pugi.XMLAttribute()

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == (
        '<node a1="v1" a2="v2" a2="v2" a1="v1"><child a2="v2"/>text</node>'
    )

    a3.set_name("a3")
    a3.set_value("v3")

    a4.set_name("a4")
    a4.set_value("v4")

    a5.set_name("a5")
    a5.set_value("v5")

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == (
        '<node a3="v3" a4="v4" a5="v5" a1="v1"><child a2="v2"/>text</node>'
    )


def test_insert_copy_before_node() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node>foo<child/></node>")
    node = doc.child("node")
    child = node.child("child")

    n1 = node.insert_copy_before(child, node.first_child())
    assert isinstance(n1, pugi.XMLNode)
    assert n1.name() == "child"

    n2 = node.insert_copy_before(node.first_child(), node.last_child())
    assert isinstance(n2, pugi.XMLNode)
    assert n2 != n1
    assert n2.name() == "child"

    n3 = node.insert_copy_before(
        node.first_child().next_sibling(), node.first_child()
    )
    assert isinstance(n3, pugi.XMLNode)
    assert n3 != n2
    assert n3 != n1
    assert n3.value() == "foo"

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<node>foo<child/>foo<child/><child/></node>"


def test_insert_move_after() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node>foo<child>bar</child></node>")
    node = doc.child("node")
    child = node.child("child")

    n1 = node.insert_move_after(child, node.first_child())
    assert isinstance(n1, pugi.XMLNode)
    assert n1 == child
    assert n1.name() == "child"

    n2 = node.insert_move_after(node.first_child(), child)
    assert isinstance(n2, pugi.XMLNode)
    assert n2 != n1
    assert n2.value() == "foo"

    n3 = child.insert_move_after(node.last_child(), child.first_child())
    assert isinstance(n3, pugi.XMLNode)
    assert n3 == n2
    assert n3 != n1
    assert n3.value() == "foo"

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<node><child>barfoo</child></node>"


def test_insert_move_before() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node>foo<child>bar</child></node>")
    node = doc.child("node")
    child = node.child("child")

    n1 = node.insert_move_before(child, node.first_child())
    assert isinstance(n1, pugi.XMLNode)
    assert n1 == child
    assert n1.name() == "child"

    n2 = node.insert_move_before(node.last_child(), child)
    assert isinstance(n2, pugi.XMLNode)
    assert n2 != n1
    assert n2.value() == "foo"

    n3 = child.insert_move_before(node.first_child(), child.first_child())
    assert isinstance(n3, pugi.XMLNode)
    assert n3 == n2
    assert n3 != n1
    assert n3.value() == "foo"

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<node><child>foobar</child></node>"


def test_internal_object() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node attr='value'>value</node>")
    node = doc.child("node")

    node_copy = pugi.XMLNode(node.internal_object())
    assert node_copy == node
    assert node_copy.parent() == node.parent()

    assert node.internal_object() == node_copy.internal_object()
    assert node.internal_object() != pugi.XMLNode().internal_object()

    node_copy.set_name("n")
    assert node.name() == "n"


def test_name_value() -> None:
    doc = pugi.XMLDocument()
    doc.load_string(
        "<?xml?><!DOCTYPE id><?pi?><!--comment-->"
        "<node>pcdata<![CDATA[cdata]]></node>",
        pugi.PARSE_DEFAULT
        | pugi.PARSE_PI
        | pugi.PARSE_COMMENTS
        | pugi.PARSE_DECLARATION
        | pugi.PARSE_DOCTYPE,
    )

    children = doc.children()
    assert children[0].name() == "xml"
    assert len(children[1].name()) == 0
    assert children[2].name() == "pi"
    assert len(children[3].name()) == 0
    assert children[4].name() == "node"

    assert len(children[0].value()) == 0
    assert children[1].value() == "id"
    assert len(children[2].value()) == 0
    assert children[3].value() == "comment"
    assert len(children[4].value()) == 0

    children = children[4].children()
    assert len(children[0].name()) == 0
    assert len(children[1].name()) == 0

    assert children[0].value() == "pcdata"
    assert children[1].value() == "cdata"


def test_next_previous_sibling() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><child1/><child2/><child3/></node>")
    node = doc.child("node")

    child1 = node.child("child1")
    child2 = node.child("child2")
    child3 = node.child("child3")

    assert child1.next_sibling() == child2
    assert child3.next_sibling() == pugi.XMLNode()

    assert child1.previous_sibling() == pugi.XMLNode()
    assert child3.previous_sibling() == child2

    assert child1.next_sibling("child3") == child3
    assert child1.next_sibling("child") == pugi.XMLNode()

    assert child3.previous_sibling("child1") == child1
    assert child3.previous_sibling("child") == pugi.XMLNode()

    with pytest.raises(TypeError):
        _ = child1.next_sibling(None)

    with pytest.raises(TypeError):
        _ = child1.previous_sibling(None)


def test_offset_debug() -> None:
    doc = pugi.XMLDocument()
    doc.load_string(
        "<?xml?><!DOCTYPE><?pi?><!--comment-->"
        "<node>pcdata<![CDATA[cdata]]></node>",
        pugi.PARSE_DEFAULT
        | pugi.PARSE_PI
        | pugi.PARSE_COMMENTS
        | pugi.PARSE_DECLARATION
        | pugi.PARSE_DOCTYPE,
    )

    assert doc.offset_debug() == 0

    children = doc.children()
    assert children[0].offset_debug() == 2
    assert children[1].offset_debug() == 16
    assert children[2].offset_debug() == 19
    assert children[3].offset_debug() == 27
    assert children[4].offset_debug() == 38

    children = doc.child("node").children()
    assert children[0].offset_debug() == 43
    assert children[1].offset_debug() == 58


def test_operators() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><node1/><node2/></node>")
    node = doc.child("node")
    node1 = node.child("node1")
    node2 = node.child("node2")
    node3 = node.first_child()

    assert not (node1 == node2)  # noqa: SIM201
    assert node1 == node3
    assert not (node2 == node3)  # noqa: SIM201

    assert node1 != node2
    assert not (node1 != node3)  # noqa: SIM202
    assert node2 != node3

    assert node1 < node2
    assert not (node1 < node3)
    assert not (node2 < node3)

    assert node1 <= node2
    assert node1 <= node3
    assert not (node2 <= node3)

    assert not (node1 > node2)
    assert not (node1 > node3)
    assert node2 > node3

    assert not (node1 >= node2)
    assert node1 >= node3
    assert node2 >= node3


def test_parent() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><child/></node>")
    node = doc.child("node")

    parent = pugi.XMLNode().parent()
    assert isinstance(parent, pugi.XMLNode)
    assert parent == pugi.XMLNode()

    parent = node.child("child").parent()
    assert isinstance(parent, pugi.XMLNode)
    assert parent == node

    parent = node.parent()
    assert isinstance(parent, pugi.XMLNode)
    assert parent == doc


def test_path() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><child1>text<child2/></child1></node>")
    node = doc.child("node")

    assert len(doc.path()) == 0
    assert node.path() == "/node"
    assert node.child("child1").path() == "/node/child1"
    assert node.child("child1").child("child2").path() == "/node/child1/child2"
    assert node.child("child1").first_child().path() == "/node/child1/"

    assert node.child("child1").path("\\") == "\\node\\child1"

    doc.append_child(pugi.NODE_ELEMENT)
    assert doc.last_child().path() == "/"

    with pytest.raises(TypeError):
        _ = node.path(None)


def test_prepend_attribute() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><child/></node>")
    node = doc.child("node")

    assert not pugi.XMLNode().prepend_attribute("a")
    assert not doc.prepend_attribute("a")

    a1 = node.prepend_attribute("a1")
    assert isinstance(a1, pugi.XMLAttribute)
    assert a1.set_value("v1")

    a2 = node.prepend_attribute("a2")
    assert isinstance(a2, pugi.XMLAttribute)
    assert a2.set_value("v2")

    a3 = node.child("child").prepend_attribute("a3")
    assert isinstance(a3, pugi.XMLAttribute)
    assert a3.set_value("v3")

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == '<node a2="v2" a1="v1"><child a3="v3"/></node>'

    with pytest.raises(TypeError):
        node.prepend_attribute(None)


def test_prepend_copy_attribute() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node a1='v1'><child a2='v2'/><child/></node>")
    node = doc.child("node")
    child = node.child("child")

    a1 = node.attribute("a1")
    a2 = child.attribute("a2")

    a3 = node.prepend_copy(a1)
    assert isinstance(a3, pugi.XMLAttribute)
    assert a3 != a2
    assert a3 != a1

    a4 = node.prepend_copy(a2)
    assert isinstance(a4, pugi.XMLAttribute)
    assert a4 != a3
    assert a4 != a2
    assert a4 != a1

    a5 = node.last_child().prepend_copy(a1)
    assert isinstance(a5, pugi.XMLAttribute)
    assert a5 != a4
    assert a5 != a3
    assert a5 != a2
    assert a5 != a1

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == (
        '<node a2="v2" a1="v1" a1="v1"><child a2="v2"/><child a1="v1"/></node>'
    )

    a3.set_name("a3")
    a3.set_value("v3")

    a4.set_name("a4")
    a4.set_value("v4")

    a5.set_name("a5")
    a5.set_value("v5")

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == (
        '<node a4="v4" a3="v3" a1="v1"><child a2="v2"/><child a5="v5"/></node>'
    )


def test_prepend_copy_node() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node>foo<child/></node>")
    node = doc.child("node")

    n1 = node.prepend_copy(node.first_child())
    assert isinstance(n1, pugi.XMLNode)
    assert n1.value() == "foo"

    n2 = node.prepend_copy(node.child("child"))
    assert isinstance(n2, pugi.XMLNode)
    assert n2 != n1
    assert n2.name() == "child"

    n3 = node.child("child").prepend_copy(node.first_child().next_sibling())
    assert isinstance(n3, pugi.XMLNode)
    assert n3 != n2
    assert n3 != n1
    assert n3.value() == "foo"

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == (
        "<node><child>foo</child>foofoo<child/></node>"
    )


def test_prepend_child() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node>foo<child/></node>")
    node = doc.child("node")

    n1 = node.prepend_child()
    assert isinstance(n1, pugi.XMLNode)
    assert n1.set_name("n1")

    n2 = node.prepend_child()
    assert isinstance(n2, pugi.XMLNode)
    assert n2 != n1
    assert n2.set_name("n2")

    n3 = node.child("child").prepend_child(pugi.NODE_PCDATA)
    assert isinstance(n3, pugi.XMLNode)
    assert n3 != n2
    assert n3 != n1
    assert n3.set_value("n3")

    n4 = doc.prepend_child(pugi.NODE_COMMENT)
    assert isinstance(n4, pugi.XMLNode)
    assert n4 != n3
    assert n4 != n2
    assert n4 != n1
    assert n4.set_value("n4")

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == (
        "<!--n4--><node><n2/><n1/>foo<child>n3</child></node>"
    )

    n0 = node.prepend_child("n0")
    assert isinstance(n0, pugi.XMLNode)
    assert n0.name() == "n0"
    assert n0.type() == pugi.NODE_ELEMENT
    assert node.first_child() == n0

    with pytest.raises(TypeError):
        _ = node.prepend_child(None)


def test_prepend_move() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node>foo<child/></node>")
    node = doc.child("node")
    child = node.child("child")

    n1 = node.prepend_move(node.first_child())
    assert isinstance(n1, pugi.XMLNode)
    assert n1 == node.first_child()
    assert n1.value() == "foo"

    n2 = node.prepend_move(child)
    assert isinstance(n2, pugi.XMLNode)
    assert n2 == child
    assert n2 != n1
    assert n2.name() == "child"

    n3 = child.prepend_move(node.first_child().next_sibling())
    assert isinstance(n3, pugi.XMLNode)
    assert n3 != n2
    assert n3 == n1
    assert n3.value() == "foo"

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<node><child>foo</child></node>"


def test_print() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node attr='1'><child>\U0001f308</child></node>")
    writer = _TestWriter()
    doc.print(writer)
    assert (
        writer.getvalue()
        == b'<node attr="1">\n\t<child>\xf0\x9f\x8c\x88</child>\n</node>\n'
    )

    writer = _TestWriter()
    doc.print(writer, flags=pugi.FORMAT_INDENT_ATTRIBUTES)
    assert (
        writer.getvalue()
        == b'<node\n\tattr="1">\n\t<child>\xf0\x9f\x8c\x88</child>\n</node>\n'
    )

    writer = _TestWriter()
    doc.print(writer, indent="", encoding=pugi.ENCODING_UTF16_LE)
    assert writer.getvalue() == (
        b'<\x00n\x00o\x00d\x00e\x00 \x00a\x00t\x00t\x00r\x00=\x00"\x001\x00"'
        b"\x00>\x00\n\x00<\x00c\x00h\x00i\x00l\x00d\x00>\x00<\xd8\x08\xdf<"
        b"\x00/\x00c\x00h\x00i\x00l\x00d\x00>\x00\n\x00<\x00/\x00n\x00o\x00d"
        b"\x00e\x00>\x00\n\x00"
    )

    writer = _TestWriter()
    with pytest.raises(TypeError):
        doc.print(writer, indent=None)


def test_print_writer(capsys: pytest.CaptureFixture[str]) -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><child>\U0001f308</child></node>")

    writer = pugi.PrintWriter()
    doc.print(writer)

    captured = capsys.readouterr()
    assert captured.out == "<node>\n\t<child>\U0001f308</child>\n</node>\n"
    assert len(captured.err) == 0

    with pytest.raises(UnicodeDecodeError):
        doc.print(writer, encoding=pugi.ENCODING_UTF16)
    with pytest.raises(UnicodeDecodeError):
        doc.print(writer, encoding=pugi.ENCODING_UTF32)


def test_remove_attribute() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node a1='v1' a2='v2' a3='v3'><child a4='v4'/></node>")
    node = doc.child("node")
    child = node.child("child")

    assert not node.remove_attribute("a")
    assert not node.remove_attribute(pugi.XMLAttribute())
    assert not node.remove_attribute(child.attribute("a4"))

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == (
        '<node a1="v1" a2="v2" a3="v3"><child a4="v4"/></node>'
    )

    assert node.remove_attribute("a1")
    assert node.remove_attribute(node.attribute("a3"))
    assert child.remove_attribute("a4")

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == '<node a2="v2"><child/></node>'

    with pytest.raises(TypeError):
        node.remove_attribute(None)


def test_remove_attributes() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node a1='v1' a2='v2' a3='v3'><child a4='v4'/></node>")
    node = doc.child("node")
    child = node.child("child")

    assert child.remove_attributes()

    writer = pugi.StringWriter()
    child.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<child/>"

    assert node.remove_attributes()

    writer = pugi.StringWriter()
    node.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<node><child/></node>"


def test_remove_child() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><n1/><n2/><n3/><child><n4/></child></node>")
    node = doc.child("node")
    child = node.child("child")

    assert not node.remove_child("a")
    assert not node.remove_child(pugi.XMLNode())
    assert not node.remove_child(child.child("n4"))

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == (
        "<node><n1/><n2/><n3/><child><n4/></child></node>"
    )

    assert node.remove_child("n1")
    assert node.remove_child(node.child("n3"))
    assert child.remove_child("n4")

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<node><n2/><child/></node>"

    with pytest.raises(TypeError):
        node.remove_child(None)


def test_remove_children() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><n1/><n2/><n3/><child><n4/></child></node>")
    node = doc.child("node")
    child = node.child("child")

    assert child.remove_children()

    writer = pugi.StringWriter()
    child.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<child/>"

    assert node.remove_children()

    writer = pugi.StringWriter()
    node.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<node/>"


def test_repr() -> None:
    doc = pugi.XMLDocument()
    doc.load_string(
        "<?xml?><!DOCTYPE><?pi?><!--comment-->"
        "<node><child1>text<child2/></child1></node>",
        pugi.PARSE_DEFAULT
        | pugi.PARSE_PI
        | pugi.PARSE_COMMENTS
        | pugi.PARSE_DECLARATION
        | pugi.PARSE_DOCTYPE,
    )

    assert repr(pugi.XMLNode()).startswith("<XMLNode")
    assert repr(pugi.XMLNode()).endswith(" type=NODE_NULL>")

    children = doc.children()
    assert repr(children[0]).startswith("<XMLNode ")
    assert repr(children[0]).endswith(" type=NODE_DECLARATION name='xml'>")

    assert repr(children[1]).startswith("<XMLNode ")
    assert repr(children[1]).endswith(" type=NODE_DOCTYPE>")

    assert repr(children[2]).startswith("<XMLNode ")
    assert repr(children[2]).endswith(" type=NODE_PI name='pi'>")

    assert repr(children[3]).startswith("<XMLNode ")
    assert repr(children[3]).endswith(" type=NODE_COMMENT>")

    assert repr(children[4]).startswith("<XMLNode ")
    assert repr(children[4]).endswith(" type=NODE_ELEMENT name='node'>")


def test_root() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><child/></node>")
    node = doc.child("node")

    root = pugi.XMLNode().root()
    assert isinstance(root, pugi.XMLNode)
    assert root == pugi.XMLNode()

    root = node.child("child").root()
    assert isinstance(root, pugi.XMLNode)
    assert root == doc

    root = node.root()
    assert isinstance(root, pugi.XMLNode)
    assert root == doc


# https://github.com/zeux/pugixml/blob/master/tests/test_dom_modify.cpp
# dom_node_set_name()
def test_set_name() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node>text</node>")
    node = doc.child("node")

    assert node.set_name("n")
    assert not node.first_child().set_name("n")
    assert not pugi.XMLNode().set_name("n")

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<n>text</n>"

    with pytest.raises(TypeError):
        node.set_name(None)

    assert node.set_name("n1234", 3)
    assert node.name() == "n12"
    assert not pugi.XMLNode().set_name("n1234", 3)

    with pytest.raises(TypeError):
        node.set_name(None, 3)


def test_set_value() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node>text</node>")
    node = doc.child("node")

    assert node.first_child().set_value("no text")
    assert not node.set_value("no text")
    assert not pugi.XMLNode().set_value("no text")

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == "<node>no text</node>"

    child = node.first_child()
    assert child.set_value("no text", 2)  # len(value) > size
    assert child.value() == "no"

    assert child.set_value("no text", 16)  # len(value) <= size
    assert child.value() == "no text"

    assert child.set_value("no text", 0)  # size == 0
    assert len(child.value()) == 0

    assert not node.set_value("no text", 2)
    assert not pugi.XMLNode().set_value("no text", 2)

    with pytest.raises(TypeError):
        child.set_value(None)  # value is None

    with pytest.raises(TypeError):
        child.set_value(None, 2)  # value is None

    with pytest.raises(TypeError):
        child.set_value("no text", -1)  # negative size


def test_string_writer() -> None:
    doc = pugi.XMLDocument()
    src = "<node>\ud83c\udf08</node>"
    buf = src.encode("utf-16", "surrogatepass")
    result = doc.load_buffer(buf, len(buf))
    assert result

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW)
    assert len(writer) == 17
    assert writer.getvalue() == "<node>\U0001f308</node>"

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW, encoding=pugi.ENCODING_UTF16)
    assert len(writer) == 30
    with pytest.raises(UnicodeDecodeError):
        _ = writer.getvalue()
    with pytest.raises(UnicodeDecodeError):
        _ = writer.getvalue("utf-8")
    assert writer.getvalue("utf-16") == "<node>\U0001f308</node>"

    # using error handler
    src = "<node>\udf08</node>"
    buf = src.encode("utf-32", "surrogatepass")
    result = doc.load_buffer(buf, len(buf))
    assert result

    writer = pugi.StringWriter()
    doc.print(writer, flags=pugi.FORMAT_RAW, encoding=pugi.ENCODING_UTF32)
    assert len(writer) == 56
    with pytest.raises(UnicodeDecodeError):
        _ = writer.getvalue()
    with pytest.raises(UnicodeDecodeError):
        _ = writer.getvalue("utf-32")
    assert writer.getvalue("utf-32", "surrogatepass") == "<node>\udf08</node>"


def test_text() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><child>text</child></node>")
    node = doc.child("node")

    text = pugi.XMLNode().text()
    assert isinstance(text, pugi.XMLText)
    assert text.empty()

    text = node.child("child").text()
    assert isinstance(text, pugi.XMLText)
    assert not text.empty()
    assert text.get() == "text"


# https://github.com/zeux/pugixml/blob/master/tests/test_dom_traverse.cpp
def test_traverse() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><child>text</child></node>")
    walker = _TestWalker()
    assert doc.traverse(walker)
    assert walker.call_count == 5
    assert walker.log == "|-1 <=|0 !node=|1 !child=|2 !=text|-1 >="


def test_traverse_child() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><child>text</child></node><another>node</another>")
    walker = _TestWalker()
    assert doc.child("node").traverse(walker)
    assert walker.call_count == 4
    assert walker.log == "|-1 <node=|0 !child=|1 !=text|-1 >node="


def test_traverse_siblings() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><child/><child>text</child><child/></node>")
    walker = _TestWalker()
    assert doc.traverse(walker)
    assert walker.call_count == 7
    assert (
        walker.log
        == "|-1 <=|0 !node=|1 !child=|1 !child=|2 !=text|1 !child=|-1 >="
    )


def test_traverse_stop_begin() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><child>text</child></node>")
    walker = _TestWalker(1)
    assert not doc.traverse(walker)
    assert walker.call_count == 1
    assert walker.log == "|-1 <="


def test_traverse_stop_end() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><child>text</child></node>")
    walker = _TestWalker(5)
    assert not doc.traverse(walker)
    assert walker.call_count == 5
    assert walker.log == "|-1 <=|0 !node=|1 !child=|2 !=text|-1 >="


def test_traverse_stop_for_each() -> None:
    doc = pugi.XMLDocument()
    doc.load_string("<node><child>text</child></node>")
    walker = _TestWalker(3)
    assert not doc.traverse(walker)
    assert walker.call_count == 3
    assert walker.log == "|-1 <=|0 !node=|1 !child="


def test_type() -> None:
    doc = pugi.XMLDocument()
    doc.load_string(
        "<?xml?><!DOCTYPE><?pi?><!--comment-->"
        "<node>pcdata<![CDATA[cdata]]></node>",
        pugi.PARSE_DEFAULT
        | pugi.PARSE_PI
        | pugi.PARSE_COMMENTS
        | pugi.PARSE_DECLARATION
        | pugi.PARSE_DOCTYPE,
    )

    assert pugi.XMLNode().type() == pugi.NODE_NULL
    assert doc.type() == pugi.NODE_DOCUMENT
    assert [x.type() for x in doc.children()] == [
        pugi.NODE_DECLARATION,
        pugi.NODE_DOCTYPE,
        pugi.NODE_PI,
        pugi.NODE_COMMENT,
        pugi.NODE_ELEMENT,
    ]
    assert [x.type() for x in doc.child("node").children()] == [
        pugi.NODE_PCDATA,
        pugi.NODE_CDATA,
    ]
