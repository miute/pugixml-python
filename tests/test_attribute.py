import sys

import pytest

from pugixml import pugi


# https://github.com/zeux/pugixml/blob/master/tests/test_dom_traverse.cpp
def test_as_bool():
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node attr1='0' attr2='1' attr3='true' attr4='True' attr5='Yes' "
        "attr6='yes' attr7='false'/>"
    )
    node = doc.child("node")

    attr = node.attribute("attr1")
    assert attr.as_bool() is False
    assert attr.value() == "0"
    attr = node.attribute("attr2")
    assert attr.as_bool() is True
    assert attr.value() == "1"
    attr = node.attribute("attr3")
    assert attr.as_bool() is True
    assert attr.value() == "true"
    attr = node.attribute("attr4")
    assert attr.as_bool() is True
    assert attr.value() == "True"
    attr = node.attribute("attr5")
    assert attr.as_bool() is True
    assert attr.value() == "Yes"
    attr = node.attribute("attr6")
    assert attr.as_bool() is True
    assert attr.value() == "yes"
    attr = node.attribute("attr7")
    assert attr.as_bool() is False
    assert attr.value() == "false"


def test_as_double():
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node attr1='0' attr2='1' attr3='0.12' attr4='-5.1' attr5='3e-4' "
        "attr6='3.14159265358979323846'/>"
    )
    node = doc.child("node")

    attr = node.attribute("attr1")
    assert attr.as_double() == 0
    assert attr.value() == "0"
    attr = node.attribute("attr2")
    assert attr.as_double() == 1
    assert attr.value() == "1"
    attr = node.attribute("attr3")
    assert attr.as_double() == pytest.approx(0.12)
    assert attr.value() == "0.12"
    attr = node.attribute("attr4")
    assert attr.as_double() == pytest.approx(-5.1)
    assert attr.value() == "-5.1"
    attr = node.attribute("attr5")
    assert attr.as_double() == pytest.approx(3e-4)
    assert attr.value() == "3e-4"
    attr = node.attribute("attr6")
    assert attr.as_double() == pytest.approx(3.14159265358979323846)
    assert attr.value() == "3.14159265358979323846"


def test_as_float():
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node attr1='0' attr2='1' attr3='0.12' attr4='-5.1' "
        "attr5='3e-4' attr6='3.14159265358979323846'/>"
    )
    node = doc.child("node")

    attr = node.attribute("attr1")
    assert attr.as_float() == 0
    assert attr.value() == "0"
    attr = node.attribute("attr2")
    assert attr.as_float() == 1
    assert attr.value() == "1"
    attr = node.attribute("attr3")
    assert attr.as_float() == pytest.approx(0.12)
    assert attr.value() == "0.12"
    attr = node.attribute("attr4")
    assert attr.as_float() == pytest.approx(-5.1)
    assert attr.value() == "-5.1"
    attr = node.attribute("attr5")
    assert attr.as_float() == pytest.approx(3e-4)
    assert attr.value() == "3e-4"
    attr = node.attribute("attr6")
    assert attr.as_float() == pytest.approx(3.14159265358979323846)
    assert attr.value() == "3.14159265358979323846"


def test_as_int():
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node attr1='1' attr2='-1' attr3='-2147483648' attr4='2147483647' attr5='0'/>"
    )
    node = doc.child("node")

    attr = node.attribute("attr1")
    assert attr.as_int() == 1
    assert attr.value() == "1"
    attr = node.attribute("attr2")
    assert attr.as_int() == -1
    assert attr.value() == "-1"
    attr = node.attribute("attr3")
    assert attr.as_int() == -2147483647 - 1
    assert attr.value() == "-2147483648"
    attr = node.attribute("attr4")
    assert attr.as_int() == 2147483647
    assert attr.value() == "2147483647"
    attr = node.attribute("attr5")
    assert attr.as_int() == 0
    assert attr.value() == "0"


def test_as_llong():
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node attr1='1' attr2='-1' attr3='-9223372036854775808' "
        "attr4='9223372036854775807' attr5='0'/>"
    )
    node = doc.child("node")

    attr = node.attribute("attr1")
    assert attr.as_llong() == 1
    assert attr.value() == "1"
    attr = node.attribute("attr2")
    assert attr.as_llong() == -1
    assert attr.value() == "-1"
    attr = node.attribute("attr3")
    assert attr.as_llong() == -9223372036854775807 - 1
    assert attr.value() == "-9223372036854775808"
    attr = node.attribute("attr4")
    assert attr.as_llong() == 9223372036854775807
    assert attr.value() == "9223372036854775807"
    attr = node.attribute("attr5")
    assert attr.as_llong() == 0
    assert attr.value() == "0"


def test_as_string():
    doc = pugi.XMLDocument()
    doc.load_string("<node attr='1'/>")

    attr = doc.child("node").attribute("attr")
    assert attr.as_string() == "1"
    assert attr.value() == "1"


def test_as_uint():
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node attr1='0' attr2='1' attr3='2147483647' attr4='4294967295' attr5='0'/>"
    )
    node = doc.child("node")

    attr = node.attribute("attr1")
    assert attr.as_uint() == 0
    assert attr.value() == "0"
    attr = node.attribute("attr2")
    assert attr.as_uint() == 1
    assert attr.value() == "1"
    attr = node.attribute("attr3")
    assert attr.as_uint() == 2147483647
    assert attr.value() == "2147483647"
    attr = node.attribute("attr4")
    assert attr.as_uint() == 4294967295
    assert attr.value() == "4294967295"
    attr = node.attribute("attr5")
    assert attr.as_uint() == 0
    assert attr.value() == "0"


def test_as_ullong():
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node attr1='0' attr2='1' attr3='9223372036854775807' "
        "attr4='18446744073709551615' attr5='0'/>"
    )
    node = doc.child("node")

    attr = node.attribute("attr1")
    assert attr.as_ullong() == 0
    assert attr.value() == "0"
    attr = node.attribute("attr2")
    assert attr.as_ullong() == 1
    assert attr.value() == "1"
    attr = node.attribute("attr3")
    assert attr.as_ullong() == 9223372036854775807
    assert attr.value() == "9223372036854775807"
    attr = node.attribute("attr4")
    assert attr.as_ullong() == 18446744073709551615
    assert attr.value() == "18446744073709551615"
    attr = node.attribute("attr5")
    assert attr.as_ullong() == 0
    assert attr.value() == "0"


def test_bool():
    doc = pugi.XMLDocument()
    doc.load_string("<node attr1='0' />")

    assert not pugi.XMLAttribute()
    assert doc.child("node").attribute("attr1")


def test_defaults():
    doc = pugi.XMLDocument()
    doc.load_string("<node/>")
    node = doc.child("node")

    attr = node.append_attribute("attr")
    assert len(attr.value()) == 0
    assert attr.as_string("foo") == "foo"
    assert attr.as_int(42) == 42
    assert attr.as_uint(42) == 42
    assert attr.as_double(42) == 42
    assert attr.as_float(42) == 42
    assert attr.as_bool(True) is True
    assert attr.as_llong(42) == 42
    assert attr.as_ullong(42) == 42


def test_empty():
    doc = pugi.XMLDocument()
    doc.load_string("<node attr1='1' attr2='2'/>")
    node = doc.child("node")

    assert pugi.XMLAttribute().empty()
    assert not node.attribute("attr1").empty()
    assert not node.attribute("attr2").empty()


def test_hash_value():
    doc = pugi.XMLDocument()
    doc.load_string("<node attr1='1' attr2='2'/>")
    node = doc.child("node")

    attr1 = node.attribute("attr1")
    attr2 = node.attribute("attr2")

    assert pugi.XMLAttribute().hash_value() == 0
    assert attr1.hash_value() > 0
    assert attr2.hash_value() > 0
    assert attr1.hash_value() != attr2.hash_value()

    assert hash(attr1) == attr1.hash_value()
    assert hash(attr2) == attr2.hash_value()


def test_internal_object():
    doc = pugi.XMLDocument()
    doc.load_string("<node attr='value'>value</node>")
    node = doc.child("node")
    attr = node.first_attribute()

    attr_copy = pugi.XMLAttribute(attr.internal_object())
    assert attr_copy == attr

    assert attr.internal_object() == attr_copy.internal_object()
    assert attr.internal_object() != pugi.XMLAttribute().internal_object()

    attr_copy.set_name("n")
    attr_copy.set_value("v")
    assert attr.name() == "n"
    assert attr.value() == "v"


def test_next_previous_attribute():
    doc = pugi.XMLDocument()

    doc.load_string("<node attr1='1' attr2='2'/>")
    node = doc.child("node")
    attr1 = node.attribute("attr1")
    attr2 = node.attribute("attr2")

    assert attr1.next_attribute() == attr2
    assert attr2.next_attribute() == pugi.XMLAttribute()

    assert attr2.previous_attribute() == attr1
    assert attr1.previous_attribute() == pugi.XMLAttribute()


def test_operators():
    doc = pugi.XMLDocument()
    doc.load_string("<node attr1='0' attr2='0'/>")
    node = doc.child("node")
    attr1 = node.attribute("attr1")
    attr2 = node.attribute("attr2")
    attr3 = node.attribute("attr1")

    assert not (attr1 == attr2)
    assert attr1 == attr3
    assert not (attr2 == attr3)

    assert attr1 != attr2
    assert not (attr1 != attr3)
    assert attr2 != attr3

    assert attr1 < attr2
    assert not (attr1 < attr3)
    assert not (attr2 < attr3)

    assert attr1 <= attr2
    assert attr1 <= attr3
    assert not (attr2 <= attr3)

    assert not (attr1 > attr2)
    assert not (attr1 > attr3)
    assert attr2 > attr3

    assert not (attr1 >= attr2)
    assert attr1 >= attr3
    assert attr2 >= attr3


def test_repr():
    doc = pugi.XMLDocument()
    doc.load_string("<node attr1='1' attr2='2'/>")
    node = doc.child("node")

    attr1 = node.attribute("attr1")
    attr2 = node.attribute("attr2")
    attr3 = pugi.XMLAttribute()

    assert repr(attr1).startswith("<XMLAttribute hash=0x")
    assert repr(attr1).endswith(" name='attr1'>")

    assert repr(attr2).startswith("<XMLAttribute hash=0x")
    assert repr(attr2).endswith(" name='attr2'>")

    assert repr(attr3).startswith("<XMLAttribute hash=0")
    assert repr(attr3).endswith(">")


def test_set_name():
    doc = pugi.XMLDocument()
    doc.load_string("<node attr='value' />")

    attr = doc.child("node").attribute("attr")
    assert attr.name() == "attr"
    assert attr.set_name("n")
    assert attr.name() == "n"


def test_set_value():
    doc = pugi.XMLDocument()
    doc.load_string("<node/>")
    node = doc.child("node")

    assert node.append_attribute("attr1").set_value("v1")
    assert node.append_attribute("attr2").set_value(-2147483647)
    assert node.append_attribute("attr3").set_value(-2147483647 - 1)
    assert node.append_attribute("attr4").set_value(4294967295)
    assert node.append_attribute("attr5").set_value(4294967295 - 1)
    assert node.append_attribute("attr6").set_value(0.5)
    assert node.append_attribute("attr7").set_value(0.25)
    assert node.append_attribute("attr8").set_value(True)

    writer = pugi.StringWriter()
    node.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == (
        '<node attr1="v1" attr2="-2147483647" attr3="-2147483648" '
        'attr4="4294967295" attr5="4294967294" attr6="0.5" attr7="0.25" '
        'attr8="true"/>'
    )


def test_set_value_double():
    doc = pugi.XMLDocument()
    doc.load_string("<node/>")
    node = doc.child("node")

    assert node.append_attribute("attr").set_value(sys.float_info.max)

    writer = pugi.StringWriter()
    node.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == '<node attr="1.7976931348623157e+308"/>'

    attr = node.attribute("attr")
    assert attr.set_value(3.1415926, 4)
    assert attr.as_double() == 3.142

    writer = pugi.StringWriter()
    node.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == '<node attr="3.142"/>'


def test_set_value_long_long():
    doc = pugi.XMLDocument()
    doc.load_string("<node/>")
    node = doc.child("node")

    assert node.append_attribute("attr1").set_value(-9223372036854775807)
    assert node.append_attribute("attr2").set_value(-9223372036854775807 - 1)
    assert node.append_attribute("attr3").set_value(18446744073709551615)
    assert node.append_attribute("attr4").set_value(18446744073709551615 - 1)

    writer = pugi.StringWriter()
    node.print(writer, flags=pugi.FORMAT_RAW)
    assert writer.getvalue() == (
        '<node attr1="-9223372036854775807" attr2="-9223372036854775808" '
        'attr3="18446744073709551615" attr4="18446744073709551614"/>'
    )
