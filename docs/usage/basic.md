# Basic Usage

This guide covers the fundamental concepts and usage patterns of AttrMagic.

## Core Classes

AttrMagic provides several key classes for different use cases:

### ClassBase

The foundation class that adds attribute path functionality to any Pydantic model:

```python
from attrmagic import ClassBase

class Person(ClassBase):
    name: str
    age: int

class Company(ClassBase):
    name: str
    employees: list[Person]

# Create instances
person = Person(name="Alice", age=30)
company = Company(name="TechCorp", employees=[person])

# Access nested attributes
print(company.getattr_path("employees__0__name"))  # "Alice"
```

### SearchBase

For searching and filtering collections of `ClassBase` objects. SearchBase works like Django QuerySets - operations return new instances without modifying the original:

```python
from attrmagic import SearchBase

# Create a collection
people = SearchBase([
    Person(name="Alice", age=30),
    Person(name="Bob", age=25),
    Person(name="Carol", age=35)
])

# Filter operations return new instances (immutable)
adults = people.filter(age__gte=30)
print(len(adults))  # 2
print(len(people))  # Still 3 - original unchanged

# Chain filters like Django QuerySets
young_adults = people.filter(age__gte=25).filter(age__lt=35)

# Use exclude to remove items
not_alice = people.exclude(name="Alice")

# Other queryset-like methods
print(people.count())     # 3
print(people.exists())    # True
print(people.first().name)  # "Alice"
print(people.last().name)   # "Carol"

# Create copies and empty querysets
all_people = people.all()   # Creates a copy
no_people = people.none()   # Empty queryset
```

### SimpleListRoot

A more general-purpose root model for lists:

```python
from attrmagic import SimpleListRoot

# Works with any objects, not just ClassBase
numbers = SimpleListRoot[int](root=[1, 2, 3, 4, 5])
high_numbers = numbers.filter(gt=3)  # [4, 5]
```

## Attribute Path Syntax

AttrMagic uses Django-style double underscore notation to traverse object hierarchies:

### Basic Paths

```python
class Address(ClassBase):
    street: str
    city: str
    zipcode: str

class Person(ClassBase):
    name: str
    address: Address

person = Person(
    name="Alice",
    address=Address(street="123 Main St", city="Springfield", zipcode="12345")
)

# Access nested attributes
city = person.getattr_path("address__city")  # "Springfield"
zipcode = person.getattr_path("address__zipcode")  # "12345"
```

### List Access

```python
class Team(ClassBase):
    name: str
    members: list[Person]

team = Team(name="Development", members=[person1, person2])

# Access list items by index
first_member = team.getattr_path("members__0__name")
first_city = team.getattr_path("members__0__address__city")
```

### Default Values

```python
# Provide defaults for missing attributes
country = person.getattr_path("address__country", default="USA")
phone = person.getattr_path("phone", default="Not provided")

# Without default, AttributeError is raised
try:
    missing = person.getattr_path("nonexistent__field")
except AttributeError as e:
    print(f"Attribute not found: {e}")
```

## Filtering Operations

### Basic Filtering

```python
employees = SearchBase([...])

# Exact matches
engineers = employees.filter(department="Engineering")
alice = employees.filter(name="Alice Johnson")

# Multiple criteria (AND logic)
senior_engineers = employees.filter(
    department="Engineering",
    age__gte=30,
    salary__gt=90000
)
```

### Operator Reference

| Operator | Description | Example |
|----------|-------------|---------|
| `exact` (default) | Exact match | `field="value"` |
| `gt` | Greater than | `age__gt=25` |
| `gte` | Greater than or equal | `age__gte=30` |
| `lt` | Less than | `salary__lt=100000` |
| `lte` | Less than or equal | `age__lte=65` |
| `contains` | String contains | `name__contains="Smith"` |
| `icontains` | Case-insensitive contains | `email__icontains="GMAIL"` |
| `startswith` | String starts with | `name__startswith="Dr"` |
| `istartswith` | Case-insensitive starts with | `name__istartswith="dr"` |
| `endswith` | String ends with | `email__endswith=".com"` |
| `iendswith` | Case-insensitive ends with | `email__iendswith=".COM"` |
| `in` | Value in list | `department__in=["Sales", "Marketing"]` |
| `range` | Value in range | `age__range=[25, 35]` |

### Working with Results

#### Getting Single Items

```python
# Get exactly one item (raises ValueError if 0 or >1 results)
manager = employees.get(role="Manager")

# Get with default
lead = employees.get(role="Lead", default=None)
if lead is None:
    print("No lead found")

# Get first match
first_engineer = employees.filter(department="Engineering")[0]
```

#### Iterating and Counting

```python
engineers = employees.filter(department="Engineering")

# Count
print(f"Engineers: {len(engineers)}")

# Iterate
for engineer in engineers:
    print(f"{engineer.name}: ${engineer.salary:,.2f}")

# Convert to list
engineer_list = list(engineers)

# Access by index
first_engineer = engineers[0]
last_engineer = engineers[-1]
```

#### Chaining Operations

```python
# Chain filters
result = employees.filter(department="Engineering") \
                 .filter(age__gte=30) \
                 .filter(salary__gt=90000)

# Combine with list operations
senior_engineer_names = [emp.name for emp in employees.filter(
    department="Engineering",
    age__gte=30
)]
```

## Error Handling

### Attribute Errors

```python
try:
    value = person.getattr_path("nonexistent__field")
except AttributeError as e:
    print(f"Path not found: {e}")

# Use defaults to avoid errors
value = person.getattr_path("nonexistent__field", default="N/A")
```

### Query Errors

```python
# Multiple results when expecting one
try:
    engineer = employees.get(department="Engineering")  # Multiple engineers!
except ValueError as e:
    print(f"Query error: {e}")
    # Use filter instead
    engineers = employees.filter(department="Engineering")

# No results when expecting one
try:
    ceo = employees.get(role="CEO")  # No CEO in dataset
except ValueError as e:
    print(f"Not found: {e}")
    # Use default
    ceo = employees.get(role="CEO", default=None)
```

## Performance Tips

### Efficient Queries

```python
# Good: Single filter with multiple criteria
efficient = employees.filter(
    department="Engineering",
    age__gte=30,
    salary__gt=90000
)

# Less efficient: Multiple separate filters
less_efficient = employees.filter(department="Engineering") \
                          .filter(age__gte=30) \
                          .filter(salary__gt=90000)
```

### Memory Usage

```python
# SearchBase creates copies for each filter
original = SearchBase([...])
filtered = original.filter(department="Engineering")  # New instance

# Original is unchanged
print(len(original))  # Original count
print(len(filtered))  # Filtered count

# Use model_copy() explicitly if needed
backup = original.model_copy()
```

## Next Steps

- Learn about [Advanced Filtering](advanced.md) techniques
- Explore [Negation with Q Objects](negation.md) for complex logic
- Check the [API Reference](../reference/models.md) for complete details
