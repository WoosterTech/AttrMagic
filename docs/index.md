# AttrMagic

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**Query-like access to nested attributes with Django-inspired syntax**

AttrMagic provides a powerful and intuitive way to filter and query nested Python objects using a Django-inspired double underscore notation. Built on top of Pydantic, it offers type-safe attribute access with advanced filtering capabilities.

## Key Features

- **Django-inspired syntax**: Use familiar `field__operator=value` syntax
- **Deep attribute access**: Navigate nested object hierarchies with ease
- **Type safety**: Built on Pydantic for robust type checking
- **Flexible filtering**: Multiple operators (gt, lt, contains, startswith, etc.)
- **Negation support**: Use `~Q()` objects for complex logical operations
- **Performance optimized**: Efficient filtering with minimal overhead (aspirational)

## Quick Example

```python
from attrmagic import ClassBase, SearchBase, Q

class Person(ClassBase):
    name: str
    age: int
    department: str

class Company(ClassBase):
    employees: list[Person]

# Create sample data
company = Company(employees=[
    Person(name="Alice", age=30, department="Engineering"),
    Person(name="Bob", age=25, department="Sales"),
    Person(name="Charlie", age=35, department="Engineering"),
])

# Create a searchable collection
employees = SearchBase(company.employees)

# Filter using Django-style syntax
engineers = employees.filter(department="Engineering")
senior_engineers = employees.filter(department="Engineering", age__gte=30)

# Use Q objects with negation
non_sales = employees.filter(~Q(department="Sales"))

# Complex filtering
experienced_non_sales = employees.filter(
    ~Q(department="Sales"),
    Q(age__gt=28)
)
```

## Why AttrMagic?

- **Familiar syntax** if you know Django ORM
- **Type-safe** operations with full IDE support
- **Extensible** operator system
- **Clean API** for complex nested queries
- **Well-tested** with comprehensive test coverage

## Get Started

Ready to start using AttrMagic? Check out our [installation guide](installation.md) and [quick start tutorial](quickstart.md).

For more advanced usage patterns, see our [user guide](usage/basic.md) and explore the [API reference](reference/models.md).
