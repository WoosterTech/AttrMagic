# Installation

AttrMagic requires Python 3.12 or higher and depends on Pydantic for its core functionality.

## Installing from PyPI

The easiest way to install AttrMagic is using pip:

```bash
pip install attrmagic
```

## Installing with uv

If you're using [uv](https://docs.astral.sh/uv/) for dependency management:

```bash
uv add attrmagic
```

## Installing for Development

To contribute to AttrMagic or run the latest development version:

### Clone the Repository

```bash
git clone https://github.com/WoosterTech/AttrMagic.git
cd AttrMagic
```

### Install with uv (Recommended)

```bash
uv sync --all-extras
```

### Install with pip

```bash
pip install -e ".[dev,test,docs]"
```

## Dependencies

AttrMagic has minimal dependencies:

- **pydantic** (>=2.7) - Core functionality and type validation
- **pydantic-core** (>=2.27.2) - Low-level Pydantic operations

### Development Dependencies

If you're contributing to AttrMagic, additional dependencies include:

- **Testing**: pytest, pytest-cov, pytest-sugar, polyfactory
- **Linting**: ruff, basedpyright
- **Documentation**: mkdocs, mkdocs-material, mkdocstrings
- **Git hooks**: pre-commit
- **Release management**: commitizen

## Verification

Verify your installation by running:

```python
import attrmagic
print(attrmagic.__version__)
```

Or run a quick test:

```python
from attrmagic import ClassBase, Q

class TestItem(ClassBase):
    name: str
    value: int

item = TestItem(name="test", value=42)
print(item.getattr_path("name"))  # Should print: test
```

## Next Steps

Once installed, head over to the [Quick Start](quickstart.md) guide to begin using AttrMagic!
