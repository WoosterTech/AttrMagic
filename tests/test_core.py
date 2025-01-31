from collections import deque
from contextlib import nullcontext
from typing import Any

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

from attrmagic import core
from attrmagic.sentinels import MISSING


def test_getattr_path():
    class Foo:
        def __init__(self, a):
            self.a = a

    foo = Foo(a=42)
    assert core.getattr_path(foo, "a") == 42
    with pytest.raises(AttributeError):
        core.getattr_path(foo, "b")


class Bar:
    def __init__(self, b):
        self.b = b


@pytest.fixture(scope="function")
def bar(request):
    return Bar(b=request.param)


def test_blank_path():
    bar_local = Bar(b=42)
    assert core.getattr_path(bar_local, "") == bar_local


@pytest.mark.parametrize(
    ("bar", "path", "default", "expected"),
    [
        (42, "a", MISSING, pytest.raises(AttributeError)),
        (42, "a", None, nullcontext(None)),
        (42, "a", 43, nullcontext(43)),
        (42, "b", None, nullcontext(42)),
        (42, "b", MISSING, nullcontext(42)),
        (None, "b", MISSING, nullcontext(None)),
    ],
    indirect=["bar"],
)
def test_param_getattr_path(bar: Bar, path: str, default: Any, expected):
    with expected as e:
        assert core.getattr_path(bar, path, default=default) == e


def test_getattr_nested_path():
    path = "b__b"
    bar = Bar(b=42)
    foo = Bar(b=bar)
    assert core.getattr_path(foo, path) == 42
    assert core.getattr_path(foo, "b") == bar
    with pytest.raises(AttributeError):
        assert core.getattr_path(foo, "a")


@pytest.fixture
def bar_default():
    return Bar(b=42)


def test_setattr_path_simple(bar_default: Bar):
    core.setattr_path(bar_default, "b", 43)
    assert bar_default.b == 43
    core.setattr_path(bar_default, "b", 44)
    assert bar_default.b == 44


def test_setattr_path_nested():
    bar_child = Bar(b=42)
    bar_parent = Bar(b=bar_child)

    core.setattr_path(bar_parent, "b__b", 43)
    assert bar_child.b == 43


class AttrPathFactory(ModelFactory[core.AttrPath]):
    separator = "__"
    value = "a__b__c"


def test_attr_path_creation():
    attr_path = AttrPathFactory.build()
    assert isinstance(attr_path, core.AttrPath)
    assert isinstance(attr_path.value, str)
    assert attr_path.value == "a__b__c"
    assert attr_path.depth == 3
    assert attr_path.parts == deque(["a", "b", "c"])
    first = attr_path.popleft()
    assert first == "a"
    assert attr_path.render() == "b__c"

    assert str(attr_path) == "b__c"

    assert attr_path[1] == "c"
    assert attr_path.pop() == "c"


def test_pop():
    attr_path = AttrPathFactory.build()
    assert attr_path.pop(1) == "b"
    assert attr_path.render() == "a__c"


def test_attr_str_to_path():
    path_str = "a__b__c"
    attr_path = core.AttrPath.str_to_path(path_str)

    assert isinstance(attr_path, core.AttrPath)
    assert isinstance(attr_path.value, str)
    assert attr_path.value == path_str
    assert attr_path.depth == 3
    assert attr_path.parts == deque(["a", "b", "c"])


def test_attr_from_parts():
    parts = ["a", "b", "c"]
    attr_path = core.AttrPath(value=parts)

    assert isinstance(attr_path, core.AttrPath)
    assert isinstance(attr_path.value, str)
    assert attr_path.value == "a__b__c"
    assert attr_path.depth == 3

    assert str(attr_path) == "a__b__c"


def test_attr_path_to_path():
    path_str = AttrPathFactory.build()

    attr_path = core.AttrPath.str_to_path(path_str)

    assert attr_path is path_str


def test_query_path():
    query_path = core.QueryPath.from_string("a__b__c")
    assert query_path.attr_path.render() == "a__b__c"
    assert query_path.operator == core.Operators.EXACT
    assert query_path._separator == "__"
    assert query_path.attr_path.separator == "__"


def test_query_path_iexact():
    query_path = core.QueryPath.from_string("a__b__c__iexact")
    assert query_path.attr_path.render() == "a__b__c"
    assert query_path.operator == core.Operators.IEXACT
    assert query_path._separator == "__"
    assert query_path.attr_path.separator == "__"
