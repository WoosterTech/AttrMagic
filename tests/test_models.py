import enum

import pytest

from attrmagic.models import ClassBase, Q, SearchBase, SimpleDict, SimpleListRoot


class Bar(ClassBase):
    c: int


class Foo(ClassBase):
    a: Bar


class MyTestEnum(enum.Enum):
    A = 1
    B = 2
    C = 3


class SimpleDictTest(SimpleDict[str, MyTestEnum]): ...


# class BarSearch(SearchBase[Bar]):
#     pass

BarSearch = SearchBase[Bar]


@pytest.fixture
def bar_search():
    return BarSearch([Bar(c=1), Bar(c=2), Bar(c=3)])


def test_getattr_path():
    foo = Foo(a=Bar(c=42))
    assert foo.getattr_path("a__c") == 42
    assert foo.getattr_path("a__d", default="missing") == "missing"
    with pytest.raises(AttributeError):
        _ = foo.getattr_path("a__d")


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
    with pytest.raises(TypeError):
        bar_search + 1  # pyright: ignore[reportUnusedExpression]


def test_searchbase_iter(bar_search: BarSearch):
    assert list(bar_search) == [Bar(c=1), Bar(c=2), Bar(c=3)]


def test_searchbase_setitem(bar_search: BarSearch):
    bar_search[0] = Bar(c=4)
    assert bar_search[0].c == 4


def test_q_object_creation():
    """Test Q object creation."""
    filter_obj = Q(c__gt=1)
    assert filter_obj.path.attr_path.value == "c"
    assert filter_obj.path.operator.name == "GT"
    assert filter_obj.value == 1
    assert filter_obj.negated is False


def test_q_object_negation():
    """Test Q object negation using ~ operator."""
    filter_obj = Q(c__gt=1)
    negated_filter = ~filter_obj

    assert negated_filter.path.attr_path.value == "c"
    assert negated_filter.path.operator.name == "GT"
    assert negated_filter.value == 1
    assert negated_filter.negated is True


def test_filter_with_q_objects(bar_search: BarSearch):
    """Test filtering using Q objects."""
    # Test positive filter
    result = bar_search.filter(Q(c__gt=1))
    assert len(result) == 2
    assert result[0].c == 2
    assert result[1].c == 3


def test_filter_with_negated_q_objects(bar_search: BarSearch):
    """Test filtering using negated Q objects."""
    # Test negated filter
    result = bar_search.filter(~Q(c__gt=1))
    assert len(result) == 1
    assert result[0].c == 1


def test_filter_with_negated_q_objects_and_alternate_filter(bar_search: BarSearch):
    """Compare negated Q object filter with alternate filter."""
    # Test negated filter
    search_1 = bar_search.model_copy()
    search_2 = bar_search.model_copy()
    result = search_1.filter(~Q(c__gt=1))
    alternate = search_2.filter(c__lte=1)
    assert result == alternate
    assert len(result) == 1
    assert result[0].c == 1


def test_filter_negated_q_differrent_from_non_negated(bar_search: BarSearch):
    """Test that negated and non-negated Q object filters yield different results."""
    search_1 = bar_search.model_copy()
    search_2 = bar_search.model_copy()
    non_negated_result = search_1.filter(Q(c__gt=1))
    negated_result = search_2.filter(~Q(c__gt=1))

    assert non_negated_result != negated_result
    assert len(non_negated_result) == 2
    assert len(negated_result) == 1


def test_filter_with_multiple_q_objects():
    """Test filtering using multiple Q objects."""
    # Add more test data
    extended_search = BarSearch([Bar(c=1), Bar(c=2), Bar(c=3), Bar(c=4), Bar(c=5)])

    # Test multiple filters (AND logic)
    result = extended_search.filter(Q(c__gt=1), Q(c__lt=4))
    assert len(result) == 2
    assert result[0].c == 2
    assert result[1].c == 3


def test_filter_mixed_q_and_kwargs():
    """Test filtering using both Q objects and kwargs."""
    extended_search = BarSearch([Bar(c=1), Bar(c=2), Bar(c=3), Bar(c=4), Bar(c=5)])

    # Mix Q objects with kwargs
    result = extended_search.filter(Q(c__gt=1), c__lt=4)
    assert len(result) == 2
    assert result[0].c == 2
    assert result[1].c == 3


def test_q_multiple_kwargs_error():
    """Test that Q objects with multiple kwargs raise an error."""
    with pytest.raises(
        ValueError, match="Q\\(\\) objects must have exactly one keyword argument"
    ):
        _ = Q(c__gt=1, c__lt=4)


def test_searchbase_get(bar_search: BarSearch):
    assert bar_search.get(c__exact=2) == bar_search[1]
    with pytest.raises(ValueError):
        assert bar_search.get(c__exact=4) is None
    assert bar_search.get(c__exact=4, default=bar_search[0]) == bar_search[0]
    assert bar_search.get(c=2) == bar_search[1]
    assert bar_search.get(c=2, c__exact=2) == bar_search[1]
    assert bar_search.get(c__exact=4, default=None) is None


def test_repr(bar_search: BarSearch):
    assert repr(bar_search) == "SearchBase[Bar]([Bar(c=1), Bar(c=2), Bar(c=3)])"


def test_simple_dict():
    my_simple_dict = SimpleDictTest(root={"a": MyTestEnum.A, "b": MyTestEnum.B})

    assert my_simple_dict["a"] == MyTestEnum.A


def test_list_root_empty():
    empty = SimpleListRoot[int].empty()
    assert not empty.root


def test_dict_empty():
    empty = SimpleDict[str, int].empty()
    assert not empty.root
