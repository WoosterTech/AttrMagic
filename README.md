## AttrMagic

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Inspired by [Django](https://www.djangoproject.com/)'s query structure.

`foo = bar.filter(obj__name__in=["john", "smith"])`

returns all objects in `bar` that have an object `obj` in them with an attribute `name` in the list.

## Testing

### Generate HTML Report

`pytest --cov=attrmagic --cov-report html tests/`
