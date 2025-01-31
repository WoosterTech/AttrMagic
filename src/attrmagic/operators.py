"""Operators for use in attrmagic.

These operators are used to compare values in attrmagic.

Classes:
    Operators: An enumeration of operators.

Functions:
    equals: Compare two values for equality.
    not_equal: Compare two values for inequality.
    greater_than: Compare two values for greater than.
    greater_than_or_equal: Compare two values for greater than or equal to.
    less_than: Compare two values for less than.
    less_than_or_equal_to: Compare two values for less than or equal to.
    in_: Check if value is in rhs.
    contains: Check if value contains rhs.
    icontains: Check if value contains rhs, case-insensitive.
    startswith: Check if value starts with rhs.
    istartswith: Check if value starts with rhs, case-insensitive.
    endswith: Check if value ends with rhs.
    iendswith: Check if value ends with rhs, case-insensitive.
    iequal: Check if value is equal to rhs, case-insensitive.
    range: Check if value is within a range.
"""

from collections.abc import Iterable
from datetime import datetime
from decimal import Decimal
from enum import Enum, member
from typing import TypeVar

# from .utils import validate_call_lex
from pydantic import validate_call

from attrmagic.utils import validate_call_lex

T = TypeVar("T", Decimal, float, str)


@validate_call_lex
def equals(value: T, rhs: T) -> bool:
    """Compare two values for equality."""
    return value == rhs


@validate_call_lex
def not_equal(value: T, rhs: T) -> bool:
    """Compare two values for inequality."""
    return value != rhs


@validate_call_lex
def greater_than(value: T, rhs: T):
    """Compare two values for greater than.

    Example:
    ```
    >>> greater_than(5, 3)
    True
    >>> greater_than(3, 5)
    False
    ```

    Args:
        value: The value to compare [left-hand side]
        rhs: The value to compare against [right-hand side]
    """
    return value > rhs


@validate_call_lex
def greater_than_or_equal(value: T, rhs: T) -> bool:
    """Compare two values for greater than or equal to.

    Example:
    ```
    >>> greater_than_or_equal(5, 3)
    True
    >>> greater_than_or_equal(3, 5)
    False
    >>> greater_than_or_equal(3, 3)
    True
    ```

    Args:
        value: The value to compare [left-hand side]
        rhs: The value to compare against [right-hand side]
    """
    return value >= rhs


@validate_call_lex
def less_than(value: T, rhs: T):
    """Compare two values for less than.

    Example:
    ```
    >>> less_than(3, 5)
    True
    >>> less_than(5, 3)
    False
    ```

    Args:
        value: The value to compare [left-hand side]
        rhs: The value to compare against [right-hand side]
    """
    return value < rhs


@validate_call_lex
def less_than_or_equal_to(value: T, rhs: T):
    """Compare two values for less than or equal to.

    Example:
    ```
    >>> less_than_or_equal_to(3, 5)
    True
    >>> less_than_or_equal_to(5, 3)
    False
    >>> less_than_or_equal_to(3, 3)
    True
    ```

    Args:
        value: The value to compare [left-hand side]
        rhs: The value to compare against [right-hand side]
    """
    return value <= rhs


# @validate_call
def in_(value: T, rhs: "Iterable[T]") -> bool:
    """Check if value is in rhs.

    Example:
    ```
    >>> in_(3, [1, 2, 3, 4, 5])
    True
    >>> in_(6, [1, 2, 3, 4, 5])
    False
    ```

    Args:
        value: The value to check
        rhs: The iterable to check against
    """
    return value in rhs


# TODO: should this accept more types?
@validate_call
def contains(value: str, rhs: str) -> bool:
    """Check if value contains rhs.

    Example:
    ```
    >>> contains("hello", "he")
    True
    >>> contains("hello", "hi")
    False
    ```

    Args:
        value: The value to check
        rhs: The value to check against
    """
    return rhs in value


@validate_call
def icontains(value: str, rhs: str) -> bool:
    """Check if value contains rhs, case-insensitive.

    Example:
    ```
    >>> icontains("hello", "he")
    True
    >>> icontains("hello", "Hi")
    False
    >>> icontains("HeLlO", "he")
    True
    ```

    Args:
        value: The value to check
        rhs: The value to check against
    """
    return rhs.lower() in value.lower()


@validate_call
def startswith(value: str, rhs: str) -> bool:
    """Check if value starts with rhs.

    Example:
    ```
    >>> startswith("hello", "he")
    True
    >>> startswith("the", "he")
    False
    ```

    Args:
        value: The value to check
        rhs: The value to check against
    """
    return value.startswith(rhs)


@validate_call
def istartswith(value: str, rhs: str) -> bool:
    """Check if value starts with rhs, case-insensitive.

    Example:
    ```
    >>> istartswith("hello", "he")
    True
    >>> istartswith("the", "He")
    False
    >>> istartswith("HELLO", "he")
    True
    ```

    Args:
        value: The value to check
        rhs: The value to check against
    """
    return value.lower().startswith(rhs.lower())


@validate_call
def endswith(value: str, rhs: str) -> bool:
    """Check if value ends with rhs.

    Example:
    ```
    >>> endswith("hello", "lo")
    True
    >>> endswith("the", "he")
    True
    >>> endswith("the", "th")
    False
    >>> endswith("the", "Th")
    False
    ```

    Args:
        value: The value to check
        rhs: The value to check against
    """
    return value.endswith(rhs)


@validate_call
def iendswith(value: str, rhs: str):
    """Check if value ends with rhs, case-insensitive.

    Example:
    ```
    >>> iendswith("hello", "LO")
    True
    >>> iendswith("the", "HE")
    True
    >>> iendswith("the", "TH")
    False
    >>> iendswith("the", "Th")
    True
    ```

    Args:
        value: The value to check
        rhs: The value to check against
    """
    return value.lower().endswith(rhs.lower())


@validate_call
def iequal(value: str, rhs: str):
    """Check if value is equal to rhs, case-insensitive.

    Example:
    ```
    >>> iequal("hello", "HELLO")
    True
    >>> iequal("the", "THE")
    True
    >>> iequal("the", "TH")
    False
    >>> iequal("the", "Th")
    False
    ```

    Args:
        value: The value to check
        rhs: The value to check against
    """
    return value.lower() == rhs.lower()


R = TypeVar("R", datetime, Decimal, float, int, str)


@validate_call
def range(value: R, rhs: tuple[R, R]) -> bool:
    """Check if value is within a range.

    Example:
    ```
    >>> range(datetime(2021, 1, 1), (datetime(2020, 1, 1), datetime(2022, 1, 1)))
    True
    >>> range(datetime(2023, 1, 1), (datetime(2020, 1, 1), datetime(2022, 1, 1)))
    False
    ```

    Args:
        value: The value to check
        rhs: The range to check against
    """
    return rhs[0] <= value <= rhs[1]


class Operators(Enum):
    """An enumeration of operators."""

    EXACT = member(equals)
    IEXACT = member(iequal)
    CONTAINS = member(contains)
    ICONTAINS = member(icontains)
    IN = member(in_)
    GT = member(greater_than)
    GTE = member(greater_than_or_equal)
    LT = member(less_than)
    LTE = member(less_than_or_equal_to)
    NE = member(not_equal)
    STARTSWITH = member(startswith)
    ISTARTSWITH = member(istartswith)
    ENDSWITH = member(endswith)
    IENDSWITH = member(iendswith)
    RANGE = member(range)

    def evaluate(self, value: T, rhs: T) -> bool:
        """Evaluate the operator.

        Args:
            value: The value to compare
            rhs: The value to compare against

        Returns:
            bool: The result of the comparison
        """
        return self.value(value, rhs)
