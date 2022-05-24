import math

import pytest

from pugixml import pugi


# https://github.com/zeux/pugixml/blob/master/tests/test_xpath_api.cpp
# xpath_api_node_accessors()
def test_node_accessors():
    doc = pugi.XMLDocument()
    doc.load_string("<node attr='value'/>")

    null = pugi.XPathNode()
    node = doc.select_node("node")
    attr = doc.select_node("node/@attr")

    assert not null.node()
    assert not null.attribute()
    assert not null.parent()

    assert node.node() == doc.child("node")
    assert not node.attribute()
    assert node.parent() == doc

    assert not attr.node()
    assert attr.attribute() == doc.child("node").attribute("attr")
    assert attr.parent() == doc.child("node")


# https://github.com/zeux/pugixml/blob/master/tests/test_xpath_api.cpp
# xpath_api_node_bool_ops()
def test_node_bool():
    doc = pugi.XMLDocument()
    doc.load_string("<node attr='value'/>")

    assert doc.select_node("node")
    assert doc.select_node("node/@attr")


# https://github.com/zeux/pugixml/blob/master/tests/test_xpath_api.cpp
# xpath_api_node_eq_ops()
def test_node_eq():
    doc = pugi.XMLDocument()
    doc.load_string("<node attr='value'/>")

    n1 = doc.select_node("node")
    n2 = doc.select_node("node/@attr")

    assert n1
    assert n1 == n1
    assert not (n1 != n1)

    assert n2
    assert n2 == n2
    assert not (n2 != n2)


# https://github.com/zeux/pugixml/blob/master/tests/test_xpath_api.cpp
# xpath_api_nodeset_accessors()
def test_nodeset_accessors():
    doc = pugi.XMLDocument()
    doc.load_string("<node><foo/><foo/></node>")

    null = pugi.XPathNodeSet()
    assert null.size() == 0
    assert len(null) == 0
    assert null.type() == pugi.XPathNodeSet.TYPE_UNSORTED
    assert null.empty()
    assert not null.first()

    ns = doc.select_nodes("node/foo")
    assert isinstance(ns, pugi.XPathNodeSet)
    assert ns.size() == 2
    assert len(ns) == 2
    assert ns.type() == pugi.XPathNodeSet.TYPE_SORTED
    assert not ns.empty()
    assert ns[0].node().name() == "foo"
    assert ns[1].node().name() == "foo"
    assert ns.first() == ns[0]

    assert ns[0].node() == doc.child("node").first_child()
    assert ns[1].node() == doc.child("node").last_child()

    with pytest.raises(IndexError):
        _ = ns[2]
    assert ns[-1] == ns[1]
    assert ns[-2] == ns[0]
    with pytest.raises(IndexError):
        _ = ns[-3]

    assert ns[:2] == [ns[0], ns[1]]

    with pytest.raises(ValueError):
        _ = ns[::0]  # ValueError: slice step cannot be zero


# https://github.com/zeux/pugixml/blob/master/tests/test_xpath.cpp
# xpath_sort_attributes()
def test_nodeset_sort_attributes():
    doc = pugi.XMLDocument()
    doc.load_string("<node/>")
    n = doc.child("node")

    n.append_attribute("attr2")
    n.append_attribute("attr3")
    n.insert_attribute_before("attr1", n.attribute("attr2"))

    ns = n.select_nodes("@* | @*")

    ns.sort()
    assert [x.attribute().name() for x in ns] == ["attr1", "attr2", "attr3"]

    ns.sort(True)
    assert [x.attribute().name() for x in ns] == ["attr3", "attr2", "attr1"]


# https://github.com/zeux/pugixml/blob/master/tests/test_xpath.cpp
# xpath_sort_children()
def test_nodeset_sort_children():
    doc = pugi.XMLDocument()
    doc.load_string(
        "<node>"
        "<child><subchild id='1'/></child>"
        "<child><subchild id='2'/></child>"
        "</node>"
    )
    children = [
        doc.child("node").first_child().first_child(),
        doc.child("node").last_child().first_child(),
    ]

    ns = pugi.XPathNodeSet(
        doc.child("node").select_nodes(
            "child/subchild[@id=1] | child/subchild[@id=2]"
        )
    )

    ns.sort()
    assert [x.node() for x in ns] == [children[0], children[1]]

    ns.sort(True)
    assert [x.node() for x in ns] == [children[1], children[0]]


# https://github.com/zeux/pugixml/blob/master/tests/test_xpath_parse.cpp
# xpath_parse_result_default()
def test_parse_result_default():
    result = pugi.XPathParseResult()
    assert not result
    assert isinstance(result.error, str)
    assert result.offset == 0
    assert isinstance(result.description(), str)
    assert repr(result) == (
        "<XPathParseResult error='Internal error' offset=0 "
        "description='Internal error'>"
    )


# https://github.com/zeux/pugixml/blob/master/tests/test_xpath_parse.cpp
def test_query():
    c = pugi.XMLNode()

    q = pugi.XPathQuery("'a\"b'")
    assert q
    result = q.result()
    assert isinstance(result, pugi.XPathParseResult)
    assert result
    assert result.error is None
    assert result.offset == 0
    assert isinstance(result.description(), str)

    assert repr(result) == (
        "<XPathParseResult error=None offset=0 description='No error'>"
    )

    assert q.evaluate_string(c) == 'a"b'


# https://github.com/zeux/pugixml/blob/master/tests/test_xpath_api.cpp
# xpath_api_evaluate()
def test_query_evaluate():
    doc = pugi.XMLDocument()
    doc.load_string("<node attr='3'/>")

    q = pugi.XPathQuery("node/@attr")
    assert q.evaluate_boolean(doc)
    assert q.evaluate_number(doc) == 3
    assert q.evaluate_string(doc) == "3"

    ns = q.evaluate_node_set(doc)
    assert isinstance(ns, pugi.XPathNodeSet)
    assert ns.size() == 1
    assert ns[0].attribute() == doc.child("node").attribute("attr")

    nr = q.evaluate_node(doc)
    assert isinstance(nr, pugi.XPathNode)
    assert nr.attribute() == doc.child("node").attribute("attr")


# https://github.com/zeux/pugixml/blob/master/tests/test_xpath_api.cpp
# xpath_api_evaluate_attr()
def test_query_evaluate_attr():
    doc = pugi.XMLDocument()
    doc.load_string("<node attr='3'/>")

    q = pugi.XPathQuery(".")
    assert q
    n = pugi.XPathNode(doc.child("node").attribute("attr"), doc.child("node"))
    assert n

    assert q.evaluate_boolean(n)
    assert q.evaluate_number(n) == 3
    assert q.evaluate_string(n) == "3"

    ns = q.evaluate_node_set(n)
    assert isinstance(ns, pugi.XPathNodeSet)
    assert ns.size() == 1
    assert ns[0] == n

    nr = q.evaluate_node(n)
    assert isinstance(nr, pugi.XPathNode)
    assert nr == n


# https://github.com/zeux/pugixml/blob/master/tests/test_xpath_parse.cpp
def test_query_fail():
    q = pugi.XPathQuery('"')
    assert not q
    result = q.result()
    assert isinstance(result, pugi.XPathParseResult)
    assert not result
    assert isinstance(result.error, str)
    assert result.offset == 0
    assert isinstance(result.description(), str)
    assert repr(result).startswith("<XPathParseResult error='")
    assert repr(result).endswith("'>")

    q = pugi.XPathQuery("123a")
    assert not q
    result = q.result()
    assert isinstance(result, pugi.XPathParseResult)
    assert not result
    assert isinstance(result.error, str)
    assert result.offset == 3
    assert isinstance(result.description(), str)
    assert repr(result).startswith("<XPathParseResult error='")
    assert repr(result).endswith("'>")


# https://pugixml.org/docs/samples/xpath_variables.cpp
def test_query_vars():
    doc = pugi.XMLDocument()
    doc.load_string(
        '<Profile FormatVersion="1">'
        "<Tools>"
        '<Tool Filename="jam" AllowIntercept="true">'
        "<Description>Jamplus build system</Description>"
        "</Tool>"
        '<Tool Filename="mayabatch.exe" AllowRemote="true" '
        'OutputFileMasks="*.dae" DeriveCaptionFrom="lastparam" Timeout="40"/>'
        '<Tool Filename="meshbuilder_*.exe" AllowRemote="false" '
        'OutputFileMasks="*.mesh" DeriveCaptionFrom="lastparam" Timeout="10"/>'
        '<Tool Filename="texbuilder_*.exe" AllowRemote="true" '
        'OutputFileMasks="*.tex" DeriveCaptionFrom="lastparam"/>'
        '<Tool Filename="shaderbuilder_*.exe" AllowRemote="true" '
        'DeriveCaptionFrom="lastparam"/>'
        "</Tools>"
        "</Profile>"
    )
    children = doc.child("Profile").child("Tools").children()

    varset = pugi.XPathVariableSet()
    varset.add("remote", pugi.XPATH_TYPE_BOOLEAN)

    query_remote_tools = pugi.XPathQuery(
        "/Profile/Tools/Tool[@AllowRemote = string($remote)]", varset
    )
    assert query_remote_tools
    assert query_remote_tools.return_type() == pugi.XPATH_TYPE_NODE_SET

    varset.set("remote", True)
    tools_remote = query_remote_tools.evaluate_node_set(doc)
    assert isinstance(tools_remote, pugi.XPathNodeSet)

    varset.set("remote", False)
    tools_local = query_remote_tools.evaluate_node_set(doc)
    assert isinstance(tools_local, pugi.XPathNodeSet)

    assert not tools_remote.empty()
    assert tools_remote.type() == pugi.XPathNodeSet.TYPE_SORTED
    assert tools_remote.size() == 3
    assert len(tools_remote) == 3
    first = tools_remote.first()
    assert isinstance(first, pugi.XPathNode)
    assert first.node() == children[1]
    assert all(isinstance(x, pugi.XPathNode) for x in tools_remote)
    assert tools_remote[0].node() == children[1]
    assert tools_remote[1].node() == children[3]
    assert tools_remote[2].node() == children[4]

    assert not tools_local.empty()
    assert tools_local.type() == pugi.XPathNodeSet.TYPE_SORTED
    assert tools_local.size() == 1
    assert len(tools_local) == 1
    first = tools_local.first()
    assert isinstance(first, pugi.XPathNode)
    assert first.node() == children[2]
    assert all(isinstance(x, pugi.XPathNode) for x in tools_local)
    assert tools_local[0].node() == children[2]

    tools_local_imm = doc.select_nodes(
        "/Profile/Tools/Tool[@AllowRemote = string($remote)]", varset
    )
    assert isinstance(tools_local_imm, pugi.XPathNodeSet)
    assert tools_local_imm.size() == 1
    assert len(tools_local_imm) == 1
    assert tools_local_imm.first().node() == children[2]


# https://github.com/zeux/pugixml/blob/master/tests/test_xpath_api.cpp
# xpath_api_select_nodes()
def test_select_node():
    doc = pugi.XMLDocument()
    doc.load_string("<node><head/><foo id='1'/><foo/><tail/></node>")

    n1 = doc.select_node("node/foo")
    assert isinstance(n1, pugi.XPathNode)
    assert n1

    q = pugi.XPathQuery("node/foo")
    n2 = doc.select_node(q)
    assert isinstance(n2, pugi.XPathNode)
    assert n2

    assert n1.node().attribute("id").as_int() == 1
    assert n2.node().attribute("id").as_int() == 1

    n3 = doc.select_node("node/bar")
    assert isinstance(n3, pugi.XPathNode)
    assert not n3

    n4 = doc.select_node("node/head/following-sibling::foo")
    n5 = doc.select_node("node/tail/preceding-sibling::foo")
    assert isinstance(n4, pugi.XPathNode)
    assert isinstance(n5, pugi.XPathNode)
    assert n4
    assert n5

    assert n4.node().attribute("id").as_int() == 1
    assert n5.node().attribute("id").as_int() == 1


# https://github.com/zeux/pugixml/blob/master/tests/test_xpath_variables.cpp
# xpath_variables_type_boolean()
def test_variable_type_boolean():
    varset = pugi.XPathVariableSet()

    var = varset.add("target", pugi.XPATH_TYPE_BOOLEAN)
    assert isinstance(var, pugi.XPathVariable)

    assert var.type() == pugi.XPATH_TYPE_BOOLEAN
    assert var.name() == "target"

    assert not var.get_boolean()
    assert math.isnan(var.get_number())
    assert len(var.get_string()) == 0
    assert var.get_node_set().empty()

    assert var.set(True)
    assert not var.set(1.0)  # float
    assert not var.set(1)  # int
    assert not var.set("abc")
    assert not var.set(pugi.XPathNodeSet())

    assert var.get_boolean()
    assert math.isnan(var.get_number())
    assert len(var.get_string()) == 0
    assert var.get_node_set().empty()


def test_variable_type_nodeset():
    doc = pugi.XMLDocument()
    doc.load_string("<node/>")

    varset = pugi.XPathVariableSet()

    var = varset.add("target", pugi.XPATH_TYPE_NODE_SET)
    assert isinstance(var, pugi.XPathVariable)

    assert var.type() == pugi.XPATH_TYPE_NODE_SET
    assert var.name() == "target"

    assert not var.get_boolean()
    assert math.isnan(var.get_number())
    assert len(var.get_string()) == 0
    assert var.get_node_set().empty()

    assert not var.set(True)
    assert not var.set(1.0)  # float
    assert not var.set(1)  # int
    assert not var.set("abc")
    assert var.set(doc.select_nodes("*"))

    assert not var.get_boolean()
    assert math.isnan(var.get_number())
    assert len(var.get_string()) == 0
    assert not var.get_node_set().empty()

    ns = var.get_node_set()
    assert isinstance(ns, pugi.XPathNodeSet)
    assert ns.size() == 1
    assert ns[0] == doc.first_child()


def test_variable_type_number():
    varset = pugi.XPathVariableSet()

    var = varset.add("target", pugi.XPATH_TYPE_NUMBER)
    assert isinstance(var, pugi.XPathVariable)

    assert var.type() == pugi.XPATH_TYPE_NUMBER
    assert var.name() == "target"

    assert not var.get_boolean()
    assert var.get_number() == 0
    assert len(var.get_string()) == 0
    assert var.get_node_set().empty()

    assert not var.set(True)
    assert var.set(1.0)  # float
    assert var.set(1)  # int
    assert not var.set("abc")
    assert not var.set(pugi.XPathNodeSet())

    assert not var.get_boolean()
    assert var.get_number() == 1
    assert len(var.get_string()) == 0
    assert var.get_node_set().empty()


def test_variable_type_string():
    varset = pugi.XPathVariableSet()

    var = varset.add("target", pugi.XPATH_TYPE_STRING)
    assert isinstance(var, pugi.XPathVariable)

    assert var.type() == pugi.XPATH_TYPE_STRING
    assert var.name() == "target"

    assert not var.get_boolean()
    assert math.isnan(var.get_number())
    assert len(var.get_string()) == 0
    assert var.get_node_set().empty()

    assert not var.set(True)
    assert not var.set(1.0)  # float
    assert not var.set(1)  # int
    assert var.set("abc")
    assert not var.set(pugi.XPathNodeSet())

    assert not var.get_boolean()
    assert math.isnan(var.get_number())
    assert var.get_string() == "abc"
    assert var.get_node_set().empty()


# https://github.com/zeux/pugixml/blob/master/tests/test_xpath_variables.cpp
# xpath_variables_set_operations()
# xpath_variables_set_operations_set()
def test_variableset_operations():
    doc = pugi.XMLDocument()
    doc.load_string("<node/>")

    varset1 = pugi.XPathVariableSet()

    v1 = varset1.add("var1", pugi.XPATH_TYPE_NUMBER)
    v2 = varset1.add("var2", pugi.XPATH_TYPE_STRING)
    v3 = varset1.add("var3", pugi.XPATH_TYPE_NODE_SET)
    v4 = varset1.add("var4", pugi.XPATH_TYPE_BOOLEAN)
    assert isinstance(v1, pugi.XPathVariable)
    assert isinstance(v2, pugi.XPathVariable)
    assert isinstance(v3, pugi.XPathVariable)
    assert isinstance(v4, pugi.XPathVariable)
    assert v1 != v2
    assert v1 != v3
    assert v1 != v4
    assert v2 != v3
    assert v2 != v4
    assert v3 != v4

    assert varset1.add("var1", pugi.XPATH_TYPE_NUMBER) == v1
    assert varset1.add("var2", pugi.XPATH_TYPE_STRING) == v2
    assert varset1.add("var2", pugi.XPATH_TYPE_NODE_SET) is None
    assert varset1.add("var3", pugi.XPATH_TYPE_NODE_SET) == v3
    assert varset1.add("var4", pugi.XPATH_TYPE_BOOLEAN) == v4

    assert varset1.get("var1") == v1
    assert varset1.get("var2") == v2
    assert varset1.get("var") is None
    assert varset1.get("var11") is None
    assert varset1.get("var3") == v3
    assert varset1.get("var4") == v4

    # XPATH_TYPE_NUMBER
    assert varset1.set("var1", 1.0)  # float
    assert v1.get_number() == 1
    assert varset1.set("var1", 1)  # int
    assert v1.get_number() == 1
    assert not varset1.set("var1", "value")  # string
    assert not varset1.set("var1", doc.select_nodes("*"))  # XPath node set
    assert not varset1.set("var1", True)  # boolean

    # XPATH_TYPE_STRING
    assert not varset1.set("var2", 1.0)  # float
    assert not varset1.set("var2", 1)  # int
    assert varset1.set("var2", "value")  # string
    assert v2.get_string() == "value"
    assert not varset1.set("var2", doc.select_nodes("*"))  # XPath node set
    assert not varset1.set("var2", True)  # boolean

    # XPATH_TYPE_NODE_SET
    assert not varset1.set("var3", 1.0)  # float
    assert not varset1.set("var3", 1)  # int
    assert not varset1.set("var3", "value")  # string
    assert varset1.set("var3", doc.select_nodes("*"))  # XPath node set
    assert v3.type() == pugi.XPATH_TYPE_NODE_SET
    assert v3.get_node_set().size() == 1
    assert v3.get_node_set()[0] == doc.first_child()
    assert not varset1.set("var3", True)  # boolean

    # XPATH_TYPE_BOOLEAN
    assert not varset1.set("var4", 1.0)  # float
    assert not varset1.set("var4", 1)  # int
    assert not varset1.set("var4", "value")  # string
    assert not varset1.set("var4", doc.select_nodes("*"))  # XPath node set
    assert varset1.set("var4", True)  # boolean
    assert v4.get_boolean() is True
