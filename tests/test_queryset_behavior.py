"""Tests for Django queryset-like immutable behavior."""

import pytest

from attrmagic.models import ClassBase, SearchBase


class Person(ClassBase):
    name: str
    age: int
    city: str


@pytest.fixture
def people_data() -> list[Person]:
    return [
        Person(name="Alice", age=25, city="New York"),
        Person(name="Bob", age=30, city="San Francisco"),
        Person(name="Charlie", age=35, city="New York"),
        Person(name="Diana", age=28, city="Los Angeles"),
    ]


@pytest.fixture
def people_queryset(people_data: list[Person]) -> SearchBase[Person]:
    return SearchBase[Person](people_data)


def test_filter_returns_new_instance(people_queryset: SearchBase[Person]):
    """Test that filter() returns a new instance and doesn't modify the original."""
    original_count = people_queryset.count()

    # Filter should return a new instance
    filtered = people_queryset.filter(age__gt=30)

    # Original should be unchanged
    assert people_queryset.count() == original_count
    assert filtered.count() == 1
    assert filtered is not people_queryset
    assert filtered[0].name == "Charlie"


def test_exclude_returns_new_instance(people_queryset: SearchBase[Person]):
    """Test that exclude() returns a new instance and doesn't modify the original."""
    original_count = people_queryset.count()

    # Exclude should return a new instance
    excluded = people_queryset.exclude(name="Alice")

    # Original should be unchanged
    assert people_queryset.count() == original_count
    assert excluded.count() == 3
    assert excluded is not people_queryset
    assert all(person.name != "Alice" for person in excluded)


def test_chaining_filters(people_queryset: SearchBase[Person]):
    """Test that filters can be chained like Django querysets."""
    result = people_queryset.filter(age__lt=35).filter(city="New York")

    assert result.count() == 1
    assert result[0].name == "Alice"

    # Original should still be unchanged
    assert people_queryset.count() == 4


def test_all_method(people_queryset: SearchBase[Person]):
    """Test the all() method creates a copy."""
    copy = people_queryset.all()

    assert copy.count() == people_queryset.count()
    assert copy is not people_queryset
    assert copy.root == people_queryset.root
    assert copy.root is not people_queryset.root  # Different list objects


def test_none_method(people_queryset: SearchBase[Person]):
    """Test the none() method returns empty queryset."""
    empty = people_queryset.none()

    assert empty.count() == 0
    assert empty.exists() is False
    assert empty is not people_queryset
    assert isinstance(empty, SearchBase)


def test_count_method(people_queryset: SearchBase[Person]):
    """Test the count() method."""
    assert people_queryset.count() == 4

    filtered = people_queryset.filter(age__gt=30)
    assert filtered.count() == 1


def test_exists_method(people_queryset: SearchBase[Person]):
    """Test the exists() method."""
    assert people_queryset.exists() is True

    empty = people_queryset.filter(age__gt=100)
    assert empty.exists() is False


def test_first_method(people_queryset: SearchBase[Person]):
    """Test the first() method."""
    first = people_queryset.first()
    assert first is not None
    assert first.name == "Alice"

    empty = people_queryset.filter(age__gt=100)
    assert empty.first() is None


def test_last_method(people_queryset: SearchBase[Person]):
    """Test the last() method."""
    last = people_queryset.last()
    assert last is not None
    assert last.name == "Diana"

    empty = people_queryset.filter(age__gt=100)
    assert empty.last() is None


def test_immutability_with_multiple_operations(people_queryset: SearchBase[Person]):
    """Test that multiple operations maintain immutability."""
    # Start with original
    original_count = people_queryset.count()

    # Chain multiple operations
    result = (
        people_queryset.filter(age__gt=25)
        .exclude(city="San Francisco")
        .filter(city="New York")
    )

    # Original should be completely unchanged
    assert people_queryset.count() == original_count
    assert all(
        person.name in ["Alice", "Bob", "Charlie", "Diana"]
        for person in people_queryset
    )

    # Result should only have Alice and Charlie from New York, age > 25, excluding SF
    assert result.count() == 1
    assert result[0].name == "Charlie"
