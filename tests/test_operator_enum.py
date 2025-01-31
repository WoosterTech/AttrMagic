from attrmagic.operators import Operators


def test_evaluate():
    assert Operators.IEXACT.evaluate("hElLo", "hello")
