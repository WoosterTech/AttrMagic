"""Defines models for attribute-based searching and filtering using Pydantic BaseModel.

Classes:
    ClassBase: A base Pydantic class that adds the ability to get attributes by path.
    SearchBase: A generic root model for searching and filtering lists of ClassBase objects.
"""

from collections.abc import Hashable, Iterable, Iterator, Mapping
from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Generic,
    Literal,
    Self,
    SupportsIndex,
    TypeVar,
    cast,
    overload,
)

from pydantic import BaseModel, RootModel
from pydantic_core.core_schema import ListSchema, ModelSchema

from attrmagic.core import AttrPath, QueryPath, getattr_path
from attrmagic.operators import Operators
from attrmagic.sentinels import MISSING, Missing
from attrmagic.utils import override

if TYPE_CHECKING:
    from _collections_abc import dict_items, dict_keys, dict_values

_T = TypeVar("_T")


class ClassBase(BaseModel):
    """Base pydantic class that adds the ability to get attributes by path."""

    def getattr_path(
        self,
        attr_path: str | AttrPath,
        *,
        separator: str = "__",
        default: _T | Missing = MISSING,
    ) -> object | _T:
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


class Filter(BaseModel, Generic[SimpleBase]):
    """A filter that can be applied to a list of objects."""

    path: QueryPath
    value: object

    @cached_property
    def attr_path(self) -> AttrPath:
        """Get the attribute path."""
        return self.path.attr_path

    @cached_property
    def operator(self) -> Operators:
        """Get the operator."""
        return self.path.operator

    @classmethod
    def from_kwarg(cls, **kwargs: object) -> list[Self]:
        """Create a filter from a kwarg."""

        def qp(path: str) -> QueryPath:
            return QueryPath.from_string(path)

        return [cls(path=qp(path), value=value) for path, value in kwargs.items()]

    def evaluate(self, item: SimpleBase) -> bool:
        """Evaluate the filter against an item."""
        value = getattr_path(item, self.attr_path)
        return self.operator.evaluate(value, self.value)  # pyright: ignore[reportArgumentType]


SearchRoot = TypeVar("SearchRoot", bound=ClassBase)


def _get_or_raise(obj: Mapping[str, _T], attr: str) -> _T:
    result = obj[attr]
    if result is None:
        raise AttributeError(f"Attribute '{attr}' not found in {obj}")
    return result


class SimpleListRoot(RootModel[list[SimpleBase]], Generic[SimpleBase]):  # noqa: D101
    @override
    def __iter__(self):  # noqa: D105  # pyright: ignore[reportIncompatibleMethodOverride]
        return iter(self.root)

    @overload
    def __getitem__(self, item: SupportsIndex, /) -> SimpleBase: ...
    @overload
    def __getitem__(self, item: slice, /) -> list[SimpleBase]: ...
    def __getitem__(self, item: SupportsIndex | slice) -> SimpleBase | list[SimpleBase]:  # noqa: D105
        return self.root[item]

    @overload
    def __setitem__(self, key: SupportsIndex, value: SimpleBase) -> None: ...
    @overload
    def __setitem__(self, key: slice, value: Iterable[SimpleBase]) -> None: ...
    def __setitem__(  # noqa: D105
        self, key: SupportsIndex | slice, value: SimpleBase | Iterable[SimpleBase]
    ) -> None:
        if isinstance(key, SupportsIndex) and not isinstance(value, Iterable):
            self.root[key] = value
        elif isinstance(key, slice) and isinstance(value, Iterable):
            self.root[key] = value
        else:
            raise TypeError(
                f"Invalid types for __setitem__: key={type(key)}, value={type(value)}"  # pyright: ignore[reportUnknownArgumentType]
            )

    def _get_filters(self, **kwargs: object) -> list[Filter[SimpleBase]]:
        return Filter[SimpleBase].from_kwarg(**kwargs)

    def _filter_list(self, filters: Iterable[Filter[SimpleBase]]) -> Self:
        assert isinstance(self.root, list), "_filter_list requires that root is a list"
        for filter in filters:
            self.root: list[SimpleBase] = [
                item for item in self.root if filter.evaluate(item)
            ]
        return self

    @property
    def base_type(self) -> type[SimpleBase]:
        """Get the base type of the items in the root list."""
        core_schema = self.__class__.__pydantic_core_schema__
        schema = cast("ListSchema", _get_or_raise(core_schema, "schema"))
        items_schema = cast("ModelSchema", _get_or_raise(schema, "items_schema"))
        return cast("type[SimpleBase]", _get_or_raise(items_schema, "cls"))

    def filter(self, **kwargs: object) -> Self:
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
        self, *, default: SimpleBase | Missing = MISSING, **kwargs: object
    ) -> SimpleBase: ...
    @overload
    def get(self, *, default: Literal[None], **kwargs: object) -> SimpleBase | None: ...
    def get(
        self,
        *,
        default: SimpleBase | Missing | None = MISSING,
        **kwargs: object,
    ) -> SimpleBase | None:
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

    def __add__(  # noqa: D105
        self, other: "SimpleListRoot[SimpleBase] | Iterable[SimpleBase]"
    ) -> Self:
        match other:
            case SimpleListRoot():
                self.root += other.root
            case Iterable():
                self.root += list(other)

        return self

    def __len__(self) -> int:  # noqa: D105
        return len(self.root)

    @override
    def __repr__(self):  # noqa: D105
        return f"{self.__class__.__name__}({self.root})"


_R = TypeVar("_R", bound=Hashable)
_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


class SimpleDict(RootModel[dict[_KT, _VT]], Generic[_KT, _VT]):
    """An implementation of Pydantic's BaseModel for dictionaries.

    Adds (most) methods from the built-in dict class.
    """

    def __len__(self) -> int:
        """Return the number of items in the dictionary."""
        return len(self.root)

    def keys(self) -> "dict_keys[_KT, _VT]":
        """Return a new view of the dictionary's keys."""
        return self.root.keys()

    def values(self) -> "dict_values[_KT, _VT]":
        """Return a new view of the dictionary's values."""
        return self.root.values()

    def items(self) -> "dict_items[_KT, _VT]":
        """Return a new view of the dictionary's items (key, value)."""
        return self.root.items()

    @overload  # type: ignore[override]
    def get(self, key: _KT, /) -> _VT | None: ...
    @overload
    def get(self, key: _KT, default: _VT, /) -> _VT: ...
    @overload
    def get(self, key: _KT, default: _T, /) -> _VT | _T: ...
    def get(
        self, key: _KT, default: _T | _VT | Missing = MISSING, /
    ) -> _VT | _T | None:
        """Return the value for key if key is in the dictionary, else default.

        Args:
            key: The key to get.
            default: The default value to return if the key is not found.
        """
        normal_default = default if default is not MISSING else None

        return self.root.get(key, normal_default)

    @overload
    def pop(self, key: _KT, /) -> _VT: ...
    @overload
    def pop(self, key: _KT, default: _VT, /) -> _VT: ...
    @overload
    def pop(self, key: _KT, default: _T, /) -> _VT | _T: ...
    def pop(self, key: _KT, default: _T | _VT | Missing = MISSING, /) -> _VT | _T:
        """Remove specified key and return the corresponding value.

        Args:
            key: The key to remove.
            default: The default value to return if the key is not found.
        """
        if default is MISSING:
            return self.root.pop(key)
        return self.root.pop(key, default)

    def __getitem__(self, key: _KT) -> _VT:
        """Return the value for key."""
        return self.root[key]

    def __setitem__(self, key: _KT, value: _VT) -> None:
        """Set the value for key."""
        self.root[key] = value

    def __delitem__(self, key: _KT) -> None:
        """Delete self[key]."""
        del self.root[key]

    @override
    def __eq__(self, value: object) -> bool:
        """Return self==value."""
        return self.root == value

    def __reversed__(self) -> Iterator[_KT]:
        """Return a reverse iterator over the keys of the dictionary."""
        return reversed(self.root)


class SimpleDictStr(RootModel[dict[str, _VT]], Generic[_VT]):  # noqa: D101
    pass


class SearchBase(SimpleListRoot[SearchRoot], Generic[SearchRoot]):
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

    def _compare(
        self, item: SearchRoot, lhs: str | AttrPath, rhs: object, operator: Operators
    ) -> bool:
        value = item.getattr_path(attr_path=lhs)
        return operator.evaluate(value, rhs)  # pyright: ignore[reportArgumentType]

    def _split_kwarg(self, **kwargs: _T) -> tuple[str, _T]:
        """Return tuple of lhs and rhs."""
        assert len(kwargs) <= 1, "only one kwarg is allowed beyond default"

        return next(iter(kwargs.items()))

    def _get_compare_tuple(self, **kwargs: _T) -> tuple[AttrPath, _T, Operators]:
        """Return tuple of lhs, rhs, and operator."""
        lhs, rhs = self._split_kwarg(**kwargs)
        query_path = QueryPath.from_string(lhs)
        lhs, operator = query_path.attr_path, query_path.operator

        return lhs, rhs, operator

    def exclude(self, **kwargs: object) -> Self:
        """Remove items that match the kwargs."""
        lhs, rhs, operator = self._get_compare_tuple(**kwargs)

        self.root: list[SearchRoot] = [
            item for item in self.root if not self._compare(item, lhs, rhs, operator)
        ]

        return self
