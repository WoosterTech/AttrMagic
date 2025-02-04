import pytest

from attrmagic.models import ClassBase, SearchBase


class Bar(ClassBase):
    c: int


class Foo(ClassBase):
    a: Bar


BarSearch = SearchBase[Bar]


@pytest.fixture
def bar_search():
    return BarSearch([Bar(c=1), Bar(c=2), Bar(c=3)])


def test_getattr_path():
    foo = Foo(a=Bar(c=42))
    assert foo.getattr_path("a__c") == 42
    assert foo.getattr_path("a__d", default="missing") == "missing"
    with pytest.raises(AttributeError):
        foo.getattr_path("a__d")


def test_searchbase_filter(bar_search: BarSearch):
    filtered = bar_search.filter(c__gt=1)
    assert len(filtered) == 2
    assert filtered[0].c == 2
    assert filtered[1].c == 3


def test_searchbase_exclude(bar_search: BarSearch):
    excluded = bar_search.exclude(c__gt=1)
    assert len(excluded) == 1
    assert excluded[0].c == 1


def test_searchbase_append(bar_search: BarSearch):
    bar_search_copy = bar_search.model_copy()

    bar_search_copy.append(Bar(c=2))
    assert len(bar_search_copy) == 4
    assert bar_search_copy[3].c == 2


def test_searchbase_add(bar_search: BarSearch):
    new_search = BarSearch([Bar(c=4)])

    search1 = bar_search
    search2 = new_search
    combined = search1 + search2
    assert len(combined) == 4
    assert combined[0].c == 1
    assert combined[3].c == 4


def test_searchbase_add_list(bar_search: BarSearch):
    new_search = [Bar(c=4)]

    search1 = bar_search
    search2 = new_search
    combined = search1 + search2
    assert len(combined) == 4
    assert combined[0].c == 1
    assert combined[3].c == 4


def test_searchbase_add_number(bar_search: BarSearch):
    with pytest.raises(NotImplementedError):
        bar_search + 1  # type: ignore[operator]


def test_searchbase_iter(bar_search: BarSearch):
    assert list(bar_search) == [Bar(c=1), Bar(c=2), Bar(c=3)]


def test_searchbase_setitem(bar_search: BarSearch):
    bar_search[0] = Bar(c=4)
    assert bar_search[0].c == 4


def test_searchbase_get(bar_search: BarSearch):
    assert bar_search.get(c__exact=2) == bar_search[1]
    with pytest.raises(ValueError):
        assert bar_search.get(c__exact=4) is None
    assert bar_search.get(c__exact=4, default=bar_search[0]) == bar_search[0]
    assert bar_search.get(c=2) == bar_search[1]
    assert bar_search.get(c=2, c__exact=2) == bar_search[1]


def test_repr(bar_search):
    assert repr(bar_search) == "SearchBase[Bar]([Bar(c=1), Bar(c=2), Bar(c=3)])"
