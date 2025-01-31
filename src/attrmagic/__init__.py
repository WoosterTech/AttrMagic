"""Provides utilities for handling missing values using enums.

See: https://peps.python.org/pep-0484/#support-for-singleton-types-in-unions

Classes:
    Missing (enum.Enum): An enumeration to represent a missing value token.

Constants:
    MISSING (Missing): A constant representing the missing value token from the Missing enum.

__all__:
    List of public objects of this module, as interpreted by import *.

"""

from enum import Enum


class Missing(Enum):  # noqa: D101
    token = 0


MISSING = Missing.token

__all__ = ["MISSING", "Missing"]

try:
    from icecream import ic  # type: ignore[import-untyped]
except ImportError:
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa: E731

try:
    builtins = __import__("__builtins__")
except ImportError:
    builtins = __import__("builtins")


def install_icecream(alias="ic"):
    """Install the icecream module."""
    setattr(builtins, alias, ic)


install_icecream()


def uninstall_icecream(alias="ic"):
    """Uninstall the icecream module."""
    delattr(builtins, alias)
