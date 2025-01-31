"""Provides utility functions for manipulating path strings and coercing values to lists.

Functions:
    - path_as_parts: Convert a path string to a list of parts.
    - get_path_part: Get a part of a path string.
    - path_popleft: Remove the first part of a path string.
    - path_popright: Remove the last part of a path string.
    - coerce_to_list: Ensure that a value is a list.
"""

import functools
from collections import deque
from collections.abc import Callable
from decimal import Decimal, InvalidOperation
from typing import TypeVar


def path_as_parts(path: str, *, separator: str = "__") -> deque[str]:
    """Convert a path string to a list of parts.

    Args:
      path: The path string.
      separator: The separator to use.

    Returns:
        A list of parts.

    Examples:
        >>> path_as_parts("a__b__c")
        ["a", "b", "c"]

    """
    return deque(path.split(separator))


LEX_TYPES_PRIORITY = [Decimal, int, float, str]

LexType = Decimal | int | float | str


def coerce_to_decimal(value: LexType) -> Decimal:
    """Coerce a value to a Decimal.

    Args:
        value: The value to coerce.

    Returns:
        Decimal: The coerced value.

    Raises:
        ValueError: If the value cannot be coerced.
    """
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except InvalidOperation:
        raise ValueError(f"Cannot coerce value {value} to Decimal.") from None


def decimal_or_string(value: LexType) -> Decimal | str:
    """Coerce a value to a Decimal or a string.

    Args:
        value: The value to coerce.

    Returns:
        Decimal | str: The coerced value.

    Raises:
        ValueError: If the value cannot be coerced.
    """
    try:
        return coerce_to_decimal(value)
    except ValueError:
        return str(value)


ARGS = TypeVar("ARGS", tuple[Decimal | float | str], dict[str, Decimal | float | str])
ValueT = TypeVar("ValueT", Decimal, float, str)
RHS_T = TypeVar("RHS_T", Decimal, float, str)
T = TypeVar("T")


def validate_call_lex(
    func: Callable[[ValueT, RHS_T], T],
) -> Callable[[ValueT, RHS_T], T]:
    """Validate the call of a function with lexical arguments.

    Args:
        func: The function to validate

    Returns:
        Callable: The validated function
    """

    @functools.wraps(func)
    def wrapper(*args):
        args = (decimal_or_string(arg) for arg in args)
        return func(*args)

    return wrapper
