# Contributing

Thank you for your interest in contributing to AttrMagic! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/WoosterTech/AttrMagic.git
cd AttrMagic

# Install with uv (recommended)
uv sync --all-extras

# Or install with pip
pip install -e ".[dev,test,docs]"
```

### Install Pre-commit Hooks

```bash
pre-commit install
```

This will set up automatic code formatting and linting on commit.

## Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=attrmagic --cov-report=html

# Run specific test file
uv run pytest tests/test_models.py

# Run tests with verbose output
uv run pytest -v
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Run type checking
uv run basedpyright

# Run linting and formatting
uv run ruff check
uv run ruff format

# Run all checks (same as pre-commit)
uv run pre-commit run --all-files
```

### Documentation

Build and serve documentation locally:

```bash
# Install docs dependencies
uv sync --extra docs

# Serve documentation locally
uv run mkdocs serve

# Build documentation
uv run mkdocs build
```

The documentation will be available at `http://localhost:8000`.

## Project Structure

```
AttrMagic/
├── src/attrmagic/          # Main package
│   ├── __init__.py         # Public API
│   ├── models.py           # Core models and classes
│   ├── core.py             # Utility functions
│   ├── operators.py        # Filtering operators
│   ├── sentinels.py        # Sentinel values
│   └── utils.py            # Helper utilities
├── tests/                  # Test suite
├── docs/                   # Documentation
├── pyproject.toml          # Project configuration
└── mkdocs.yml              # Documentation configuration
```

## Making Changes

### Adding Features

1. **Create a branch**: `git checkout -b feature/your-feature-name`
2. **Write tests first**: Add tests in the appropriate test file
3. **Implement the feature**: Make your changes to the source code
4. **Update documentation**: Add or update relevant documentation
5. **Run tests**: Ensure all tests pass
6. **Submit PR**: Create a pull request

### Adding New Operators

To add a new filtering operator:

1. **Add the function** in `src/attrmagic/operators.py`:
   ```python
   @validate_call_lex
   def your_operator(value: _T, rhs: _T) -> bool:
       """Your operator description."""
       return your_logic_here
   ```

2. **Add to the Operators enum**:
   ```python
   class Operators(Enum):
       # ... existing operators
       YOUR_OPERATOR = member(your_operator)
   ```

3. **Write tests** in `tests/test_operator_funcs.py` and `tests/test_operator_enum.py`

4. **Update documentation** in `docs/reference/operators.md`

### Fixing Bugs

1. **Write a failing test** that reproduces the bug
2. **Fix the implementation** to make the test pass
3. **Ensure no regressions** by running the full test suite
4. **Update documentation** if needed

## Code Style

### General Guidelines

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write docstrings in Google format
- Keep functions focused and single-purpose
- Use descriptive variable and function names

### Example Function

```python
def filter_by_criteria[T](
    items: list[T],
    field_path: str,
    value: object,
    *,
    operator: Operators = Operators.EXACT
) -> list[T]:
    """Filter items by the specified criteria.

    Args:
        items: List of items to filter.
        field_path: Dot-separated path to the field.
        value: Value to compare against.
        operator: Comparison operator to use.

    Returns:
        Filtered list of items.

    Raises:
        AttributeError: If field_path doesn't exist on items.
    """
    # Implementation here
```

### Docstring Format

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int = 5) -> bool:
    """Brief description of what the function does.

    Longer description if needed. Can span multiple paragraphs.

    Args:
        param1: Description of param1.
        param2: Description of param2. Defaults to 5.

    Returns:
        Description of what is returned.

    Raises:
        ValueError: When this exception might be raised.

    Example:
        ```python
        result = example_function("hello", 10)
        ```
    """
```

## Testing Guidelines

### Test Organization

- **Unit tests**: Test individual functions and methods
- **Integration tests**: Test component interactions
- **Smoke tests**: Basic functionality verification

### Writing Tests

```python
import pytest
from attrmagic import ClassBase, SearchBase

class TestPerson(ClassBase):
    name: str
    age: int

def test_filter_by_age():
    """Test filtering by age."""
    people = SearchBase([
        TestPerson(name="Alice", age=30),
        TestPerson(name="Bob", age=25)
    ])

    adults = people.filter(age__gte=30)
    assert len(adults) == 1
    assert adults[0].name == "Alice"

def test_filter_nonexistent_field():
    """Test filtering by nonexistent field raises error."""
    people = SearchBase([TestPerson(name="Alice", age=30)])

    with pytest.raises(AttributeError):
        people.filter(nonexistent_field="value")
```

### Test Fixtures

Use pytest fixtures for reusable test data:

```python
@pytest.fixture
def sample_employees():
    """Create sample employee data for testing."""
    return SearchBase([
        Employee(name="Alice", department="Engineering", age=30),
        Employee(name="Bob", department="Sales", age=25),
    ])

def test_department_filter(sample_employees):
    """Test filtering by department."""
    engineers = sample_employees.filter(department="Engineering")
    assert len(engineers) == 1
```

## Documentation

### Writing Documentation

- Use clear, concise language
- Provide practical examples
- Include both basic and advanced usage patterns
- Keep API documentation up to date with code changes

### Documentation Structure

- **User guides**: How to accomplish tasks
- **API reference**: Complete method documentation
- **Examples**: Real-world usage scenarios
- **Contributing**: Development information

## Release Process

AttrMagic uses [Commitizen](https://commitizen-tools.github.io/commitizen/) for automated releases:

1. **Follow conventional commits**: Use `feat:`, `fix:`, `docs:`, etc.
2. **Version bumping**: Run `uv run cz bump` to create a new version
3. **Changelog**: Automatically updated with `cz bump`
4. **Tagging**: Git tags are automatically created

### Commit Message Format

```
type(scope): description

Body text if needed.

Footer if needed.
```

Examples:
- `feat(models): add negation support with Q objects`
- `fix(core): handle missing attributes gracefully`
- `docs(examples): add e-commerce use case`

## Getting Help

- **Issues**: Open an issue on GitHub for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Email**: Contact maintainers directly for sensitive issues

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Acknowledge different perspectives and experiences

Thank you for contributing to AttrMagic!
