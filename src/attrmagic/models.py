"""Defines models for attribute-based searching and filtering using Pydantic BaseModel.

Classes:
    ClassBase: A base Pydantic class that adds the ability to get attributes by path.
    SearchBase: A generic root model for searching and filtering lists of ClassBase objects.
"""

from collections.abc import Iterable
from typing import Any, Generic, Self, SupportsIndex, TypeVar, overload, override

from pydantic import BaseModel, RootModel, validate_call

from . import MISSING
from .core import QueryPath, getattr_path
from .operators import Operators


class ClassBase(BaseModel):
    """Base pydantic class that adds the ability to get attributes by path."""

    def getattr_path(self, attr_path, *, separator="__", default=MISSING) -> Any:
        """Get an attribute path, as defined by a string separated by '__'.

        Example:
        ```
        >>> foo = Foo(a=Bar(b=Baz(c=42)))
        >>> foo.getattr_path('a__b__c')
        42
        ```

        Args:
            attr_path: The path to the attribute.
            separator: The separator to use.
            default: The default value to return if the attribute is not found.

        Returns:
            The attribute at the given path.

        Raises:
            AttributeError: If the attribute does not exist, including any intermediate attributes.
        """
        return getattr_path(
            obj=self, path=attr_path, separator=separator, default=default
        )


SearchRoot = TypeVar("SearchRoot", bound=ClassBase)

_T = TypeVar("_T")


class SearchBase(RootModel[list[SearchRoot]], Generic[SearchRoot]):
    """A generic root model for searching and filtering lists of ClassBase objects.

    Example:
    ```
    >>> class Foo(ClassBase):
    ...     a: int
    ...
    >>> search = SearchBase([Foo(a=1), Foo(a=2), Foo(a=3)])
    >>> search.filter(a__gt=1)
    SearchBase([Foo(a=2), Foo(a=3)])
    ```
    """

    def __iter__(self):  # noqa: D105
        return iter(self.root)

    @overload
    def __getitem__(self, item: SupportsIndex, /) -> SearchRoot: ...
    @overload
    def __getitem__(self, item: slice, /) -> list[SearchRoot]: ...
    def __getitem__(self, item):  # noqa: D105
        return self.root[item]

    @overload
    def __setitem__(self, key: SupportsIndex, value: _T) -> None: ...
    @overload
    def __setitem__(self, key: slice, value: Iterable[_T]) -> None: ...
    def __setitem__(self, key, value):  # noqa: D105
        self.root[key] = value

    def get(self, *, default: Any | None = None, **kwargs) -> SearchRoot | None:
        """Return the item that matches the kwargs or the default value."""
        items_list = self.model_copy().filter(**kwargs)

        if len(items_list) != 1:
            return default

        return items_list[0]

    def _compare(self, item: SearchRoot, lhs: str, rhs: Any, operator: Operators):
        value = item.getattr_path(attr_path=lhs)
        return operator.evaluate(value, rhs)

    def _split_kwarg(self, **kwargs) -> tuple[str, Any]:
        """Return tuple of lhs and rhs."""
        if len(kwargs) > 1:
            msg = "only one kwarg is allowed beyond default"
            raise ValueError(msg)

        return next(iter(kwargs.items()))

    # def _split_lhs(
    #     self, lhs: str, *, separator: str = "__"
    # ) -> tuple[AttrPath, Operators]:
    #     """Return tuple of lhs and operator."""
    #     # pattern finds last group after last underscore
    #     query_path = QueryPath.from_string(lhs, separator=separator)
    #     return query_path.attr_path, query_path.operator

    def _get_compare_tuple(self, **kwargs):
        """Return tuple of lhs, rhs, and operator."""
        lhs, rhs = self._split_kwarg(**kwargs)
        query_path = QueryPath.from_string(lhs)
        lhs, operator = query_path.attr_path, query_path.operator

        return lhs, rhs, operator

    @validate_call
    def filter(self, **kwargs) -> Self:
        """Find items that match the kwargs.

        Example:
        ```
        >>> search = SearchBase([Foo(a=1), Foo(a=2), Foo(a=3)])
        >>> search.filter(a__gt=1)
        SearchBase([Foo(a=2), Foo(a=3)])
        ```

        Args:
            kwargs: The attributes to filter by.
        """
        lhs, rhs, operator = self._get_compare_tuple(**kwargs)

        self.root = [
            item for item in self.root if self._compare(item, lhs, rhs, operator)
        ]
        return self

    def exclude(self, **kwargs) -> Self:
        """Remove items that match the kwargs."""
        lhs, rhs, operator = self._get_compare_tuple(**kwargs)

        self.root = [
            item for item in self.root if not self._compare(item, lhs, rhs, operator)
        ]

        return self

    def append(self, item: SearchRoot):
        """Append an item to the end of class."""
        self.root.append(item)

    def __add__(self, other: "SearchBase | Iterable[SearchRoot]") -> Self:  # noqa: D105
        match other:
            case SearchBase():
                self.root += other.root
            case Iterable():
                self.root += list(other)
            case _:
                raise NotImplementedError

        return self

    @override
    def __len__(self):
        return len(self.root)

    @override
    def __repr__(self):
        return f"{self.__class__.__name__}({self.root})"
