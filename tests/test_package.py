from attrmagic import __about__


def test_about():
    assert isinstance(__about__.__version__, str)
