"""Provides utilities for attribute path manipulation and error handling.

Classes:
    AttrPath: A class for handling attribute paths.

Functions:
    getattr_path: Get an attribute path.
    setattr_path: Set an attribute path.

Exceptions:
    UnknownValueError: An exception for unknown values.
"""

from collections import deque
from collections.abc import Generator
from typing import Any, SupportsIndex, TypeVar, cast

from pydantic import BaseModel, model_validator

from attrmagic.operators import Operators

from .sentinels import MISSING, Missing
from .utils import override, path_as_parts

_T = TypeVar("_T")


def getattr_path(
    obj: object,
    path: "str | AttrPath",
    *,
    separator: str = "__",
    default: _T | Missing = MISSING,
) -> object | _T:
    """Get an attribute path, as defined by a string separated by '__'.

    Example:
    ```
    >>> foo = Foo(a=Bar(b=Baz(c=42)))
    >>> getattr_path(foo, 'a__b__c')
    42
    ```


    Args:
        obj: The object to get the attribute from.
        path: The path to the attribute.
        separator: The separator to use.
        default: The default value to return if the attribute is not found.

    Returns:
        The attribute at the given path.

    Raises:
        AttributeError: If the attribute does not exist, including any intermediate attributes.
    """
    if path == "":
        return obj
    current = obj
    attr_path = AttrPath.str_to_path(path, separator=separator)
    for name in attr_path:
        if default is MISSING:
            try:
                current = getattr(current, name)  # pyright: ignore[reportAny]
            except AttributeError as e:
                msg = f"'{type(obj).__name__}' object has no attribute path '{path}', since {e}"
                raise AttributeError(msg) from e

        else:
            current = getattr(current, name, MISSING)
            if current is MISSING:
                return default
        if current is None:
            return None
    return current


def setattr_path(
    obj: object, path: str, value: object, *, separator: str = "__"
) -> None:
    """Set an attribute path, as defined by a string separated by '__'.

    Example:
    ```
    >>> foo = Foo(a=Bar(b=Baz(c=42)))
    >>> setattr_path(foo, 'a__b__c', 43)
    >>> foo.a.b.c
    43
    ```

    Args:
        obj: The top-level object to set the attribute on.
        path: The path to the attribute.
        value: The value to set the attribute to.
        separator: The separator to use.
    """
    current = obj
    parts = path_as_parts(path, separator=separator)
    for name in list(parts)[:-1]:
        current = getattr(current, name)  # pyright: ignore[reportAny]
    setattr(current, parts[-1], value)


class AttrPath(BaseModel):
    """Represents a path-like structure using a string with a specified separator.

    Attributes:
        value (str): The string representation of the path.

    Methods:
        str_to_path(cls, value: "str | AttrPath") -> "AttrPath": Converts a string or AttrPath instance to an AttrPath instance.
        parts(): Returns the deque of parts.
        pop(index: int = -1): Removes and returns the part at the specified index.
        popleft(): Removes and returns the leftmost part.
        get(index: int): Returns the part at the specified index.
        render(): Joins the parts into a string using the separator and returns it.
        depth: Returns the number of parts in the path.
    """

    separator: str = "__"
    value: str
    _parts: deque[str] | None = None

    @model_validator(mode="before")
    @classmethod
    def value_as_string(cls, data: Any) -> Any:  # pyright: ignore[reportAny, reportExplicitAny]
        """Converts a sequence of values into a path string."""
        if isinstance(data, dict):
            if isinstance(data["value"], str):
                return data  # pyright: ignore[reportUnknownVariableType]

            separator = cast(
                "str",
                (
                    data["separator"]
                    if "separator" in data
                    else cls.get_field_default("separator")
                ),
            )
            data["value"] = separator.join(data["value"])  # pyright: ignore[reportUnknownArgumentType]
        return data  # pyright: ignore[reportUnknownVariableType]

    @classmethod
    def get_field_default(cls, field_name: str) -> Any:  # pyright: ignore[reportAny, reportExplicitAny]
        """Returns the default value for the specified field."""
        fields = cls.model_fields
        field = next(fields[name] for name in fields if name == field_name)
        return field.default  # pyright: ignore[reportAny]

    @classmethod
    def str_to_path(
        cls, value: "str | AttrPath", *, separator: str = "__"
    ) -> "AttrPath":
        """Converts a string or AttrPath instance to an AttrPath instance.

        Args:
            value: The string or AttrPath instance to convert. If an AttrPath instance is passed, it is returned as is.
            separator: The separator to use.

        Returns:
            An AttrPath instance.
        """
        if not isinstance(value, AttrPath):
            return cls(value=value, separator=separator)
        return value

    @override
    def __iter__(self) -> Generator[str, Any, None]:  # pyright: ignore[reportExplicitAny, reportIncompatibleMethodOverride]
        """Returns an iterator over the parts of the path."""
        yield from iter(self.parts)

    def __getitem__(self, index: SupportsIndex):
        """Returns the part at the specified index."""
        return self.parts[index]

    @property
    def parts(self) -> deque[str]:
        """Returns the parts attribute.

        Returns:
            list: The parts attribute.
        """
        if self._parts is None:
            self._parts = path_as_parts(self.value, separator=self.separator)
        return self._parts

    def pop(self, index: int = -1) -> str:
        """Removes and returns the part at the specified index."""
        parts = self.parts
        parts.rotate(-index)
        value = parts.popleft()
        parts.rotate(index)
        return value

    def popleft(self) -> str:
        """Removes and returns the leftmost part."""
        return self.parts.popleft()

    def render(self):
        """Joins the parts into a string using the separator and returns it."""
        return self.separator.join(self.parts)

    @override
    def __str__(self):  # noqa: D105
        return self.render()

    @property
    def depth(self):
        """Returns the number of parts in the path."""
        return len(self.parts)


class QueryPath(BaseModel):
    """Represents a query path."""

    attr_path: AttrPath
    operator: Operators = Operators.EXACT
    _separator: str = "__"

    @classmethod
    def from_string(cls, value: str, *, separator: str = "__") -> "QueryPath":
        """Creates a QueryPath instance from a string.

        Args:
            value: The string to convert.
            separator: The separator to use.

        Returns:
            A QueryPath instance.
        """
        parts = list(path_as_parts(value, separator=separator))

        operator_candidate = parts[-1].upper()
        if operator_candidate not in Operators.__members__:
            path = separator.join(parts)
            return cls(
                attr_path=AttrPath(value=path, separator=separator),
                _separator=separator,
            )
        path = separator.join(parts[:-1])
        return cls(
            attr_path=AttrPath(value=path, separator=separator),
            operator=Operators[operator_candidate],
            _separator=separator,
        )
