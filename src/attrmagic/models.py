"""Defines models for attribute-based searching and filtering using Pydantic BaseModel.

Classes:
    ClassBase: A base Pydantic class that adds the ability to get attributes by path.
    SearchBase: A generic root model for searching and filtering lists of ClassBase objects.
"""

from collections.abc import Iterable, Iterator, Mapping, Sequence
from decimal import Decimal
from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Literal,
    Self,
    SupportsIndex,
    cast,
    overload,
    override,
)

from pydantic import BaseModel, RootModel
from pydantic_core.core_schema import ListSchema, ModelSchema

from attrmagic.core import AttrPath, QueryPath, getattr_path
from attrmagic.operators import Operators
from attrmagic.sentinels import MISSING, Missing

if TYPE_CHECKING:  # pragma: no cover
    from _collections_abc import dict_items, dict_keys, dict_values


def Q(**kwargs: object) -> "Filter[object]":
    """Create a Filter object for queries, similar to Django's Q objects.

    Example:
    ```
    >>> from attrmagic.models import Q, SearchBase
    >>>
    >>> # Create filters
    >>> filter1 = Q(age__gt=18)
    >>> filter2 = Q(name__icontains='john')
    >>> negated_filter = ~Q(status='inactive')
    >>>
    >>> # Use in filter method
    >>> results = SearchBase([...]).filter(filter1, filter2, negated_filter)
    ```

    Args:
        kwargs: The field lookups for the filter.

    Returns:
        A Filter object that can be negated with ~ operator.
    """
    if len(kwargs) != 1:
        raise ValueError("Q() objects must have exactly one keyword argument")

    path_str, value = next(iter(kwargs.items()))
    query_path = QueryPath.from_string(path_str)
    return Filter(path=query_path, value=value)


class ClassBase(BaseModel):
    """Base pydantic class that adds the ability to get attributes by path."""

    def getattr_path[T](
        self,
        attr_path: str | AttrPath,
        *,
        separator: str = "__",
        default: T | Missing = MISSING,
    ) -> object | T:
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


class SimpleBaseGenericList[SimpleBase](list[SimpleBase]): ...  # noqa: D101


class SimpleBaseGenericDict[SimpleBase](dict[str, SimpleBase]): ...  # noqa: D101


class Filter[SimpleBase](BaseModel):
    """A filter that can be applied to a list of objects."""

    path: QueryPath
    value: object
    negated: bool = False

    @cached_property
    def attr_path(self) -> AttrPath:
        """Get the attribute path."""
        return self.path.attr_path

    @cached_property
    def operator(self) -> Operators:
        """Get the operator."""
        return self.path.operator

    def __invert__(self) -> Self:
        """Negate the filter using the ~ operator.

        Example:
        ```
        >>> filter = Filter(path=QueryPath.from_string('field__gt'), value=5)
        >>> negated_filter = ~filter
        ```
        """
        return self.model_copy(update={"negated": not self.negated})

    @classmethod
    def from_kwarg(cls, **kwargs: object) -> list[Self]:
        """Create a filter from a kwarg."""

        def qp(path: str) -> QueryPath:
            return QueryPath.from_string(path)

        return [cls(path=qp(path), value=value) for path, value in kwargs.items()]

    def evaluate(self, item: SimpleBase) -> bool:
        """Evaluate the filter against an item."""
        value = cast("Decimal | float | str", getattr_path(item, self.attr_path))
        result = self.operator.evaluate(value, self.value)  # pyright: ignore[reportArgumentType]
        return not result if self.negated else result


def _get_or_raise[T](obj: Mapping[str, T], attr: str) -> T:
    result = obj[attr]
    if result is None:
        raise AttributeError(f"Attribute '{attr}' not found in {obj}")
    return result


class SimpleListRoot[SimpleBase](RootModel[list[SimpleBase]]):
    """An implementation of Pydantic's RootModel for lists.

    Adds (most) methods from the built-in list class.

    Adds filtering capabilities via Filter objects.
    """

    root: list[SimpleBase]

    @classmethod
    def empty(cls) -> Self:
        """Create an empty instance of the class."""
        return cls(root=[])

    @override
    def __iter__(self) -> Iterator[SimpleBase]:  # pyright: ignore[reportIncompatibleMethodOverride]
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
    def __setitem__(self, key: slice, value: Sequence[SimpleBase]) -> None: ...
    def __setitem__(  # noqa: D105
        self, key: SupportsIndex | slice, value: SimpleBase | Sequence[SimpleBase]
    ) -> None:
        if isinstance(key, SupportsIndex) and not isinstance(value, Sequence):
            self.root[key] = value
        elif isinstance(key, slice) and isinstance(value, Sequence):
            self.root[key] = value
        else:
            raise TypeError(
                f"Invalid types for __setitem__: key={type(key)}, value={type(value)}"  # pyright: ignore[reportUnknownArgumentType]
            )

    def _get_filters(self, **kwargs: object) -> list[Filter[SimpleBase]]:
        return Filter[SimpleBase].from_kwarg(**kwargs)

    def _filter_list(self, filters: Iterable[Filter[SimpleBase]]) -> Self:
        assert isinstance(self.root, list), "_filter_list requires that root is a list"
        filtered_data = list(self.root)
        for filter in filters:
            filtered_data = [item for item in filtered_data if filter.evaluate(item)]
        return self.__class__(root=filtered_data)

    @property
    def base_type(self) -> type[SimpleBase]:
        """Get the base type of the items in the root list."""
        core_schema = self.__class__.__pydantic_core_schema__
        schema = cast("ListSchema", _get_or_raise(core_schema, "schema"))
        items_schema = cast("ModelSchema", _get_or_raise(schema, "items_schema"))
        return cast("type[SimpleBase]", _get_or_raise(items_schema, "cls"))

    def filter(self, *filters: "Filter[SimpleBase]", **kwargs: object) -> Self:
        """Return a new instance with items that match the kwargs or filter objects.

        This method does not modify the original instance, similar to Django querysets.

        Example:
        ```
        >>> search = SimpleRoot[list[Foo]](root=[Foo(a=1), Foo(a=2), Foo(a=3)])
        >>> filtered = search.filter(a__gt=1)  # Returns new instance
        >>> # Original search is unchanged
        >>> len(search)  # Still 3
        3
        >>> len(filtered)  # New instance has 2
        2
        >>>
        >>> # Chaining filters
        >>> result = search.filter(a__gt=1).filter(a__lt=3)
        >>>
        >>> # Using negated filters with ~ operator
        >>> from attrmagic.models import Filter
        >>> from attrmagic.core import QueryPath
        >>> negated_filter = ~Filter(path=QueryPath.from_string('a__gt'), value=1)
        >>> search.filter(negated_filter)
        SearchRoot([Foo(a=1)])
        ```

        Args:
            filters: Filter objects to apply.
            kwargs: The attributes to filter by.

        Returns:
            A new instance containing only items matching the filters.
        """
        kwarg_filters = self._get_filters(**kwargs)
        all_filters = list(filters) + kwarg_filters
        assert isinstance(self.root, list), "root must be a list"
        return self._filter_list(all_filters)

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

    def pop(self, index: SupportsIndex = -1, /) -> SimpleBase:
        """Remove and return item at index (default last)."""
        return self.root.pop(index)

    def append(self, item: SimpleBase):
        """Append an item to the end of class."""
        self.root.append(item)

    def __add__(  # noqa: D105
        self, other: "SimpleListRoot[SimpleBase] | Iterable[SimpleBase] | object"
    ) -> Self:
        match other:
            case SimpleListRoot():
                self.root += other.root  # pyright: ignore[reportUnknownMemberType]
            case Iterable():
                self.root += list(other)  # pyright: ignore[reportUnknownArgumentType]
            case _:
                return NotImplemented

        return self

    def __len__(self) -> int:  # noqa: D105
        return len(self.root)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.root})"


class SimpleDict[KeyT, ValueT](RootModel[dict[KeyT, ValueT]]):
    """An implementation of Pydantic's BaseModel for dictionaries.

    Adds (most) methods from the built-in dict class.
    """

    @classmethod
    def empty(cls) -> Self:
        """Create an empty instance of the class."""
        return cls(root={})

    def __len__(self) -> int:
        """Return the number of items in the dictionary."""
        return len(self.root)

    def keys(self) -> "dict_keys[KeyT, ValueT]":
        """Return a new view of the dictionary's keys."""
        return self.root.keys()

    def values(self) -> "dict_values[KeyT, ValueT]":
        """Return a new view of the dictionary's values."""
        return self.root.values()

    def items(self) -> "dict_items[KeyT, ValueT]":
        """Return a new view of the dictionary's items (key, value)."""
        return self.root.items()

    @overload  # type: ignore[override]
    def get(self, key: KeyT, /) -> ValueT | None: ...
    @overload
    def get(self, key: KeyT, default: ValueT, /) -> ValueT: ...
    @overload
    def get[T](self, key: KeyT, default: T, /) -> ValueT | T: ...
    def get[T](
        self, key: KeyT, default: T | ValueT | Missing = MISSING, /
    ) -> ValueT | T | None:
        """Return the value for key if key is in the dictionary, else default.

        Args:
            key: The key to get.
            default: The default value to return if the key is not found.
        """
        normal_default = default if default is not MISSING else None

        return self.root.get(key, normal_default)

    @overload
    def pop(self, key: KeyT, /) -> ValueT: ...
    @overload
    def pop(self, key: KeyT, default: ValueT, /) -> ValueT: ...
    @overload
    def pop[T](self, key: KeyT, default: T, /) -> ValueT | T: ...
    def pop[T](
        self, key: KeyT, default: T | ValueT | Missing = MISSING, /
    ) -> ValueT | T:
        """Remove specified key and return the corresponding value.

        Args:
            key: The key to remove.
            default: The default value to return if the key is not found.
        """
        if default is MISSING:
            return self.root.pop(key)
        return self.root.pop(key, default)

    def __getitem__(self, key: KeyT) -> ValueT:
        """Return the value for key."""
        return self.root[key]

    def __setitem__(self, key: KeyT, value: ValueT) -> None:
        """Set the value for key."""
        self.root[key] = value

    def __delitem__(self, key: KeyT) -> None:
        """Delete self[key]."""
        del self.root[key]

    @override
    def __eq__(self, value: object) -> bool:
        """Return self==value."""
        return self.root == value

    def __reversed__(self) -> Iterator[KeyT]:
        """Return a reverse iterator over the keys of the dictionary."""
        return reversed(self.root)

    def __contains__(self, key: KeyT) -> bool:
        """Return key in self."""
        return key in self.root


class SimpleDictStr[ValueT](RootModel[dict[str, ValueT]]):  # noqa: D101
    pass


class SearchBase[SearchRoot: ClassBase](SimpleListRoot[SearchRoot]):
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

    def _split_kwarg[T](self, **kwargs: T) -> tuple[str, T]:
        """Return tuple of lhs and rhs."""
        assert len(kwargs) <= 1, "only one kwarg is allowed beyond default"

        return next(iter(kwargs.items()))

    def _get_compare_tuple[T](self, **kwargs: T) -> tuple[AttrPath, T, Operators]:
        """Return tuple of lhs, rhs, and operator."""
        lhs, rhs = self._split_kwarg(**kwargs)
        query_path = QueryPath.from_string(lhs)
        lhs, operator = query_path.attr_path, query_path.operator

        return lhs, rhs, operator

    def exclude(self, **kwargs: object) -> Self:
        """Return a new instance excluding items that match the kwargs.

        This method does not modify the original instance, similar to Django querysets.

        Returns:
            A new instance excluding items matching the criteria.
        """
        lhs, rhs, operator = self._get_compare_tuple(**kwargs)

        excluded_data = [
            item for item in self.root if not self._compare(item, lhs, rhs, operator)
        ]

        return self.__class__(root=excluded_data)

    def all(self) -> Self:
        """Return a copy of this queryset (like Django's QuerySet.all()).

        Returns:
            A new instance with the same data.
        """
        return self.__class__(root=list(self.root))

    def none(self) -> Self:
        """Return an empty queryset of the same type (like Django's QuerySet.none()).

        Returns:
            A new empty instance of the same class.
        """
        return self.__class__.empty()

    def count(self) -> int:
        """Return the count of items (like Django's QuerySet.count()).

        Returns:
            The number of items in this queryset.
        """
        return len(self.root)

    def exists(self) -> bool:
        """Return True if the queryset contains any results (like Django's QuerySet.exists()).

        Returns:
            True if there are any items, False otherwise.
        """
        return len(self.root) > 0

    def first(self) -> SearchRoot | None:
        """Return the first item or None if empty (like Django's QuerySet.first()).

        Returns:
            The first item or None if the queryset is empty.
        """
        return self.root[0] if self.root else None

    def last(self) -> SearchRoot | None:
        """Return the last item or None if empty (like Django's QuerySet.last()).

        Returns:
            The last item or None if the queryset is empty.
        """
        return self.root[-1] if self.root else None
