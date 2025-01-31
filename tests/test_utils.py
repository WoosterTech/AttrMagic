from contextlib import nullcontext
import pytest
from attrmagic import utils
from decimal import Decimal


@pytest.mark.parametrize(
    "value, expected",
    [
        (42, nullcontext(Decimal("42"))),
        (42.3, nullcontext(Decimal("42.3"))),
        ("42", nullcontext(Decimal("42"))),
        ("42.3", nullcontext(Decimal("42.3"))),
        (None, pytest.raises(ValueError)),
        ("hello", pytest.raises(ValueError)),
    ],
)
def test_coerce_to_dec(value, expected):
    with expected as e:
        assert utils.coerce_to_decimal(value) == e


@pytest.mark.parametrize(
    "value, expected",
    [
        (42, Decimal("42")),
        (42.3, Decimal("42.3")),
        ("42", Decimal("42")),
        ("42.3", Decimal("42.3")),
        ("hello", "hello"),
    ],
)
def test_decimal_or_string(value, expected):
    assert utils.decimal_or_string(value) == expected
