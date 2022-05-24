import sys

import pytest

from pugixml import pugi


def test_as_bool():
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node>"
        "<text1>0</text1>"
        "<text2>1</text2>"
        "<text3>true</text3>"
        "<text4>True</text4>"
        "<text5>Yes</text5>"
        "<text6>yes</text6>"
        "<text7>false</text7>"
        "</node>"
    )
    node = doc.child("node")

    assert not pugi.XMLText().as_bool()
    assert not node.child("text1").text().as_bool()
    assert node.child("text2").text().as_bool()
    assert node.child("text3").text().as_bool()
    assert node.child("text4").text().as_bool()
    assert node.child("text5").text().as_bool()
    assert node.child("text6").text().as_bool()
    assert not node.child("text7").text().as_bool()


def test_as_double():
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node>"
        "<text1>0</text1>"
        "<text2>1</text2>"
        "<text3>0.12</text3>"
        "<text4>-5.1</text4>"
        "<text5>3e-4</text5>"
        "<text6>3.14159265358979323846</text6>"
        "</node>"
    )
    node = doc.child("node")

    assert pugi.XMLText().as_double() == 0
    assert node.child("text1").text().as_double() == 0
    assert node.child("text2").text().as_double() == 1
    assert node.child("text3").text().as_double() == 0.12
    assert node.child("text4").text().as_double() == -5.1
    assert node.child("text5").text().as_double() == 3e-4
    assert node.child("text6").text().as_double() == 3.14159265358979323846


def test_as_float():
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node>"
        "<text1>0</text1>"
        "<text2>1</text2>"
        "<text3>0.12</text3>"
        "<text4>-5.1</text4>"
        "<text5>3e-4</text5>"
        "<text6>3.14159265358979323846</text6>"
        "</node>"
    )
    node = doc.child("node")

    assert pugi.XMLText().as_float() == 0
    assert node.child("text1").text().as_float() == 0
    assert node.child("text2").text().as_float() == 1
    assert node.child("text3").text().as_float() == pytest.approx(0.12)
    assert node.child("text4").text().as_float() == pytest.approx(-5.1)
    assert node.child("text5").text().as_float() == pytest.approx(3e-4)
    assert node.child("text6").text().as_float() == pytest.approx(
        3.14159265358979323846
    )


def test_as_int():
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node>"
        "<text1>1</text1>"
        "<text2>-1</text2>"
        "<text3>-2147483648</text3>"
        "<text4>2147483647</text4>"
        "<text5>0</text5>"
        "</node>"
    )
    node = doc.child("node")

    assert node.child("text1").text().as_int() == 1
    assert node.child("text2").text().as_int() == -1
    assert node.child("text3").text().as_int() == -2147483647 - 1
    assert node.child("text4").text().as_int() == 2147483647
    assert node.child("text5").text().as_int() == 0


def test_as_llong():
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node>"
        "<text1>1</text1>"
        "<text2>-1</text2>"
        "<text3>-9223372036854775808</text3>"
        "<text4>9223372036854775807</text4>"
        "<text5>0</text5>"
        "</node>"
    )
    node = doc.child("node")

    assert pugi.XMLText().as_llong() == 0
    assert node.child("text1").text().as_llong() == 1
    assert node.child("text2").text().as_llong() == -1
    assert node.child("text3").text().as_llong() == -9223372036854775807 - 1
    assert node.child("text4").text().as_llong() == 9223372036854775807
    assert node.child("text5").text().as_llong() == 0


def test_as_string():
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node>"
        "<a>foo</a>"
        "<b><node/><![CDATA[bar]]></b>"
        "<c><?pi value?></c>"
        "<d/>"
        "</node>",
        pugi.PARSE_DEFAULT | pugi.PARSE_PI,
    )
    node = doc.child("node")

    assert node.child("a").text().as_string() == "foo"
    assert node.child("a").first_child().text().as_string() == "foo"

    assert node.child("b").text().as_string() == "bar"
    assert node.child("b").last_child().text().as_string() == "bar"

    assert len(node.child("c").text().as_string()) == 0
    assert len(node.child("c").first_child().text().as_string()) == 0

    assert len(node.child("d").text().as_string()) == 0

    assert len(pugi.XMLNode().text().as_string()) == 0


def test_as_uint():
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node>"
        "<text1>0</text1>"
        "<text2>1</text2>"
        "<text3>2147483647</text3>"
        "<text4>4294967295</text4>"
        "<text5>0</text5>"
        "</node>"
    )
    node = doc.child("node")

    assert pugi.XMLText().as_uint() == 0
    assert node.child("text1").text().as_uint() == 0
    assert node.child("text2").text().as_uint() == 1
    assert node.child("text3").text().as_uint() == 2147483647
    assert node.child("text4").text().as_uint() == 4294967295
    assert node.child("text5").text().as_uint() == 0


def test_as_ullong():
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node>"
        "<text1>0</text1>"
        "<text2>1</text2>"
        "<text3>9223372036854775807</text3>"
        "<text4>18446744073709551615</text4>"
        "<text5>0</text5>"
        "</node>"
    )
    node = doc.child("node")

    assert pugi.XMLText().as_ullong() == 0
    assert node.child("text1").text().as_ullong() == 0
    assert node.child("text2").text().as_ullong() == 1
    assert node.child("text3").text().as_ullong() == 9223372036854775807
    assert node.child("text4").text().as_ullong() == 18446744073709551615
    assert node.child("text5").text().as_ullong() == 0


def test_bool():
    doc = pugi.XMLDocument()
    doc.load_string("<node>foo</node>")

    assert not pugi.XMLText()
    assert doc.child("node").text()


def test_data():
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node><a>foo</a><b><![CDATA[bar]]></b><c><?pi value?></c><d/></node>",
        pugi.PARSE_DEFAULT | pugi.PARSE_PI,
    )
    node = doc.child("node")

    assert node.child("a").text().data() == node.child("a").first_child()
    assert node.child("b").text().data() == node.child("b").first_child()
    assert node.child("c").text().data() == pugi.XMLNode()
    assert node.child("d").text().data() == pugi.XMLNode()
    assert pugi.XMLText().data() == pugi.XMLNode()


def test_defaults():
    text = pugi.XMLText()

    assert text.as_string("foo") == "foo"
    assert text.as_int(42) == 42
    assert text.as_uint(42) == 42
    assert text.as_double(42) == 42
    assert text.as_float(42) == 42
    assert text.as_bool(True) is True
    assert text.as_llong(42) == 42
    assert text.as_ullong(42) == 42


def test_get():
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node><a>foo</a><b><![CDATA[bar]]></b><c><?pi value?></c><d/></node>",
        pugi.PARSE_DEFAULT | pugi.PARSE_PI,
    )
    node = doc.child("node")

    assert node.child("a").text().get() == "foo"
    assert node.child("a").first_child().text().get() == "foo"

    assert node.child("b").text().get() == "bar"
    assert node.child("b").last_child().text().get() == "bar"

    assert len(node.child("c").text().get()) == 0
    assert len(node.child("c").first_child().text().get()) == 0

    assert len(node.child("d").text().get()) == 0

    assert len(pugi.XMLNode().text().get()) == 0


def test_repr():
    doc = pugi.XMLDocument()
    doc.load_string("<node>foo</node>")

    assert repr(pugi.XMLText()) == "<XMLText hash=0>"
    assert repr(doc.child("node").text()).startswith("<XMLText hash=0x")


def test_set_value():
    doc = pugi.XMLDocument()
    doc.load_string("<node/>")
    node = doc.child("node")

    assert node.append_child("text1").text().set("v1")
    assert not pugi.XMLText().set("v1")

    assert node.append_child("text2").text().set(-2147483647)
    assert node.append_child("text3").text().set(-2147483647 - 1)
    assert not pugi.XMLText().set(-2147483647 - 1)

    assert node.append_child("text4").text().set(4294967295)
    assert node.append_child("text5").text().set(4294967294)
    assert not pugi.XMLText().set(4294967295)

    assert node.append_child("text6").text().set(0.5)
    assert not pugi.XMLText().set(0.5)

    assert node.append_child("text7").text().set(0.25)
    assert not pugi.XMLText().set(0.25)

    assert node.append_child("text8").text().set(True)
    assert not pugi.XMLText().set(True)

    writer = pugi.StringWriter()
    node.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == (
        "<node>"
        "<text1>v1</text1>"
        "<text2>-2147483647</text2>"
        "<text3>-2147483648</text3>"
        "<text4>4294967295</text4>"
        "<text5>4294967294</text5>"
        "<text6>0.5</text6>"
        "<text7>0.25</text7>"
        "<text8>true</text8>"
        "</node>"
    )


def test_set_value_double():
    doc = pugi.XMLDocument()
    doc.load_string("<node/>")
    node = doc.child("node")

    assert node.append_child("text1").text().set(sys.float_info.max)

    writer = pugi.StringWriter()
    node.print(writer, flags=pugi.FORMAT_RAW)
    assert (
        writer.getvalue()
        == "<node><text1>1.7976931348623157e+308</text1></node>"
    )


# https://github.com/zeux/pugixml/blob/master/tests/test_dom_text.cpp
# dom_text_set_value_llong()
def test_set_value_long_long():
    doc = pugi.XMLDocument()
    doc.load_string("<node/>")
    node = doc.child("node")

    assert node.append_child("text1").text().set(-9223372036854775807)
    assert node.append_child("text2").text().set(-9223372036854775807 - 1)
    assert not pugi.XMLText().set(-9223372036854775807 - 1)

    assert node.append_child("text3").text().set(18446744073709551615)
    assert node.append_child("text4").text().set(18446744073709551614)
    assert not pugi.XMLText().set(18446744073709551615)

    writer = pugi.StringWriter()
    node.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == (
        "<node>"
        "<text1>-9223372036854775807</text1>"
        "<text2>-9223372036854775808</text2>"
        "<text3>18446744073709551615</text3>"
        "<text4>18446744073709551614</text4>"
        "</node>"
    )
