"""Defines models for attribute-based searching and filtering using Pydantic BaseModel.

Classes:
    ClassBase: A base Pydantic class that adds the ability to get attributes by path.
    SearchBase: A generic root model for searching and filtering lists of ClassBase objects.
"""

from collections.abc import Iterable
from functools import cached_property
from typing import Any, Generic, Literal, Self, SupportsIndex, TypeVar, overload

from pydantic import BaseModel, RootModel

from .core import AttrPath, QueryPath, getattr_path
from .operators import Operators
from .sentinels import MISSING, Missing
from .utils import override


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


SimpleBase = TypeVar("SimpleBase")


class SimpleBaseGenericList(list[SimpleBase], Generic[SimpleBase]): ...  # noqa: D101


class SimpleBaseGenericDict(dict[str, SimpleBase], Generic[SimpleBase]): ...  # noqa: D101


SimpleBaseGeneric = TypeVar(
    "SimpleBaseGeneric",
    SimpleBaseGenericList,
    SimpleBaseGenericDict,
)


class Filter(BaseModel, Generic[SimpleBase]):
    """A filter that can be applied to a list of objects."""

    path: QueryPath
    value: Any

    @cached_property
    def attr_path(self) -> AttrPath:
        """Get the attribute path."""
        return self.path.attr_path

    @cached_property
    def operator(self) -> Operators:
        """Get the operator."""
        return self.path.operator

    @classmethod
    def from_kwarg(cls, **kwargs) -> list[Self]:
        """Create a filter from a kwarg."""

        def qp(path: str) -> QueryPath:
            return QueryPath.from_string(path)

        return [cls(path=qp(path), value=value) for path, value in kwargs.items()]

    def evaluate(self, item: SimpleBase) -> bool:
        """Evaluate the filter against an item."""
        value = getattr_path(item, self.attr_path)
        return self.operator.evaluate(value, self.value)


SearchRoot = TypeVar("SearchRoot", bound=ClassBase)
_T = TypeVar("_T")

_DefaultT = TypeVar("_DefaultT")


class SimpleRoot(RootModel[list[SimpleBase]], Generic[SimpleBase]):  # noqa: D101
    def __iter__(self):  # noqa: D105
        return iter(self.root)

    @overload
    def __getitem__(self, item: SupportsIndex, /) -> SimpleBase: ...
    @overload
    def __getitem__(self, item: slice, /) -> list[SimpleBase]: ...
    def __getitem__(self, item):  # noqa: D105
        return self.root[item]

    @overload
    def __setitem__(self, key: SupportsIndex, value: _T) -> None: ...
    @overload
    def __setitem__(self, key: slice, value: Iterable[_T]) -> None: ...
    def __setitem__(self, key, value):  # noqa: D105
        self.root[key] = value

    def _get_filters(self, **kwargs) -> list[Filter[SimpleBase]]:
        return Filter.from_kwarg(**kwargs)

    def _filter_list(self, filters: Iterable[Filter[SimpleBase]]) -> Self:
        assert isinstance(self.root, list), "_filter_list requires that root is a list"
        for filter in filters:
            self.root = [item for item in self.root if filter.evaluate(item)]
        return self

    def filter(self, **kwargs) -> Self:
        """Find items that match the kwargs.

        Example:
        ```
        >>> search = SimpleRoot[list[Foo]](root=[Foo(a=1), Foo(a=2), Foo(a=3)])
        >>> search.filter(a__gt=1)
        SearchRoot([Foo(a=2), Foo(a=3)])
        >>> search = SimpleRoot[list[int]](root=[1, 2, 3])
        >>> search.filter(gt=1)
        SimpleRoot([2, 3])
        ```

        Args:
            kwargs: The attributes to filter by.
        """
        filters = self._get_filters(**kwargs)
        assert isinstance(self.root, list), "root must be a list"
        return self._filter_list(filters)

    @overload
    def get(
        self, *, default: SimpleBase | Missing = MISSING, **kwargs: Any
    ) -> SimpleBase: ...
    @overload
    def get(self, *, default: Literal[None], **kwargs: Any) -> SimpleBase | None: ...
    @overload
    def get(
        self, *, default: SimpleBase | Missing | None, **kwargs: Any
    ) -> SimpleBase | None: ...
    def get(
        self,
        *,
        default=MISSING,
        **kwargs,
    ):
        """Return the item that matches the kwargs or the default value.

        Raises:
            ValueError: If 0 or more than 1 items are returned.
        """
        items_list = self.model_copy().filter(**kwargs)

        if (list_len := len(items_list)) != 1:
            if default is MISSING:
                match list_len:
                    case 0:
                        msg = "get() returned no items"
                    case _:
                        msg = "get() returned more than one item"
                raise ValueError(msg)
            return default

        return items_list[0]

    def append(self, item: SimpleBase):
        """Append an item to the end of class."""
        self.root.append(item)

    def __add__(self, other: "SimpleRoot | Iterable[SimpleBase]") -> Self:  # noqa: D105
        match other:
            case SimpleRoot():
                self.root += other.root
            case Iterable():
                self.root += list(other)
            case _:
                raise NotImplementedError

        return self

    @override
    def __len__(self):  # noqa: D105
        return len(self.root)

    @override
    def __repr__(self):  # noqa: D105
        return f"{self.__class__.__name__}({self.root})"


class SearchBase(SimpleRoot[SearchRoot], Generic[SearchRoot]):
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

    def _compare(self, item: SearchRoot, lhs: str, rhs: Any, operator: Operators):
        value = item.getattr_path(attr_path=lhs)
        return operator.evaluate(value, rhs)

    def _split_kwarg(self, **kwargs) -> tuple[str, Any]:
        """Return tuple of lhs and rhs."""
        assert len(kwargs) <= 1, "only one kwarg is allowed beyond default"

        return next(iter(kwargs.items()))

    def _get_compare_tuple(self, **kwargs):
        """Return tuple of lhs, rhs, and operator."""
        lhs, rhs = self._split_kwarg(**kwargs)
        query_path = QueryPath.from_string(lhs)
        lhs, operator = query_path.attr_path, query_path.operator

        return lhs, rhs, operator

    def exclude(self, **kwargs) -> Self:
        """Remove items that match the kwargs."""
        lhs, rhs, operator = self._get_compare_tuple(**kwargs)

        self.root = [
            item for item in self.root if not self._compare(item, lhs, rhs, operator)
        ]

        return self
