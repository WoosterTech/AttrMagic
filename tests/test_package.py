from attrmagic import __about__
import attrmagic


def test_about():
    assert isinstance(__about__.__version__, str)


def test_uninstall_icecream():
    attrmagic.uninstall_icecream()
    assert not hasattr(__builtins__, "ic")
