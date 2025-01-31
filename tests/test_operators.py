from contextlib import nullcontext

import pytest

from attrmagic import operators


@pytest.mark.parametrize(
    "value, rhs, expected",
    [
        (42, 42, nullcontext(True)),
        (42, 43, nullcontext(False)),
        (42, "42", nullcontext(True)),
        ("42", "42", nullcontext(True)),
        ("42", 42, nullcontext(True)),
        ("42", "43", nullcontext(False)),
        (42.3, 42.3, nullcontext(True)),
        (42.3, 42.4, nullcontext(False)),
        (42.3, "42.3", nullcontext(True)),
        ("42.3", "42.3", nullcontext(True)),
        ("42.3", 42.3, nullcontext(True)),
        ("42.3", "42.4", nullcontext(False)),
        (None, None, nullcontext(True)),
        ("hello", "hello", nullcontext(True)),
        ("hello", 45, nullcontext(False)),
    ],
)
def test_equals(value, rhs, expected):
    with expected as e:
        assert operators.equals(value, rhs) == e


@pytest.mark.parametrize(
    "value, rhs, expected",
    [
        (42, 42, nullcontext(False)),
        (42, 43, nullcontext(True)),
        (42, "42", nullcontext(False)),
        ("42", "42", nullcontext(False)),
        ("42", 42, nullcontext(False)),
        ("42", "43", nullcontext(True)),
        (42.3, 42.3, nullcontext(False)),
        (42.3, 42.4, nullcontext(True)),
        (42.3, "42.3", nullcontext(False)),
        ("42.3", "42.3", nullcontext(False)),
        ("42.3", 42.3, nullcontext(False)),
        ("42.3", "42.4", nullcontext(True)),
        (None, None, nullcontext(False)),
        ("hello", "hello", nullcontext(False)),
        ("hello", 45, nullcontext(True)),
    ],
)
def test_not_equal(value, rhs, expected):
    with expected as e:
        assert operators.not_equal(value, rhs) == e


@pytest.mark.parametrize(
    "value, rhs, expected",
    [
        (42, 42, nullcontext(False)),
        (42, 43, nullcontext(False)),
        (43, 42, nullcontext(True)),
    ],
)
def test_greater_than(value, rhs, expected):
    with expected as e:
        assert operators.greater_than(value, rhs) == e


@pytest.mark.parametrize(
    "value, rhs, expected",
    [
        (42, 42, nullcontext(True)),
        (42, 43, nullcontext(False)),
        (43, 42, nullcontext(True)),
    ],
)
def test_greater_than_or_equal(value, rhs, expected):
    with expected as e:
        assert operators.greater_than_or_equal(value, rhs) == e


@pytest.mark.parametrize(
    "value, rhs, expected",
    [
        (42, 42, nullcontext(False)),
        (42, 43, nullcontext(True)),
        (43, 42, nullcontext(False)),
    ],
)
def test_less_than(value, rhs, expected):
    with expected as e:
        assert operators.less_than(value, rhs) == e


@pytest.mark.parametrize(
    "value, rhs, expected",
    [
        (42, 42, nullcontext(True)),
        (42, 43, nullcontext(True)),
        (43, 42, nullcontext(False)),
    ],
)
def test_less_than_or_equal(value, rhs, expected):
    with expected as e:
        assert operators.less_than_or_equal_to(value, rhs) == e


@pytest.mark.parametrize(
    "value, rhs, expected",
    [
        (42, [1, 42, 10_000], nullcontext(True)),
        (43, [1, 42, 10_000], nullcontext(False)),
    ],
)
def test_in(value, rhs, expected):
    with expected as e:
        assert operators.in_(value, rhs) == e


@pytest.mark.parametrize(
    "value, rhs, expected",
    [
        ("hello, world", ", wo", nullcontext(True)),
        ("hello, world", ", WO", nullcontext(False)),
        ("goodbye", ", wo", nullcontext(False)),
    ],
)
def test_contains(value, rhs, expected):
    with expected as e:
        assert operators.contains(value, rhs) == e


@pytest.mark.parametrize(
    "value, rhs, expected",
    [
        ("hello, world", ", wo", nullcontext(True)),
        ("hello, world", ", WO", nullcontext(True)),
        ("goodbye", ", wo", nullcontext(False)),
    ],
)
def test_icontains(value, rhs, expected):
    with expected as e:
        assert operators.icontains(value, rhs) == e


@pytest.mark.parametrize(
    "value, rhs, expected",
    [
        ("hello, world", "hell", nullcontext(True)),
        ("hello, world", "Hell", nullcontext(False)),
        ("goodbye", "ood", nullcontext(False)),
    ],
)
def test_startswith(value, rhs, expected):
    with expected as e:
        assert operators.startswith(value, rhs) == e


@pytest.mark.parametrize(
    "value, rhs, expected",
    [
        ("hello, world", "hell", nullcontext(True)),
        ("hello, world", "Hell", nullcontext(True)),
        ("goodbye", "ood", nullcontext(False)),
    ],
)
def test_istartswith(value, rhs, expected):
    with expected as e:
        assert operators.istartswith(value, rhs) == e


@pytest.mark.parametrize(
    "value, rhs, expected",
    [
        ("hello, world", "world", nullcontext(True)),
        ("hello, world", "World", nullcontext(False)),
        ("goodbye", "ood", nullcontext(False)),
    ],
)
def test_endswith(value, rhs, expected):
    with expected as e:
        assert operators.endswith(value, rhs) == e


@pytest.mark.parametrize(
    "value, rhs, expected",
    [
        ("hello, world", "world", nullcontext(True)),
        ("hello, world", "World", nullcontext(True)),
        ("goodbye", "ood", nullcontext(False)),
    ],
)
def test_iendswith(value, rhs, expected):
    with expected as e:
        assert operators.iendswith(value, rhs) == e
