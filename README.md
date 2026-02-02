## AttrMagic

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Inspired by [Django](https://www.djangoproject.com/)'s query structure.

`foo = bar.filter(obj__name__in=["john", "smith"])`

returns all objects in `bar` that have an object `obj` in them with an attribute `name` in the list.

## Quick Start

```python
from attrmagic import ClassBase, SearchBase, Q

class Person(ClassBase):
    name: str
    age: int
    department: str

# Create a searchable collection
people = SearchBase([
    Person(name="Alice", age=30, department="Engineering"),
    Person(name="Bob", age=25, department="Sales"),
    Person(name="Carol", age=35, department="Engineering"),
])

# Filter using Django-style syntax
engineers = people.filter(department="Engineering")
senior_engineers = people.filter(department="Engineering", age__gte=30)

# Use Q objects with negation
non_sales = people.filter(~Q(department="Sales"))
```

## Documentation

Full documentation is available at: [https://woostertech.github.io/AttrMagic/](https://woostertech.github.io/AttrMagic/)

Or build locally:
```bash
uv run mkdocs serve
```

## Installation

```bash
pip install attrmagic
```

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features including:
- 🚀 Lazy evaluation for better performance
- 🔗 Complex Q object operations (`&`, `|`)
- 📊 Aggregate functions and advanced filtering
- 🔌 Database backend integrations

## Testing

### Generate HTML Report

`pytest --cov=attrmagic --cov-report html tests/`
