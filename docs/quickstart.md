# Quick Start

This guide will get you up and running with AttrMagic in just a few minutes.

## Basic Setup

First, let's create a simple data model using AttrMagic's `ClassBase`:

```python
from attrmagic import ClassBase, SearchBase

class Person(ClassBase):
    name: str
    age: int
    email: str
    department: str

class Address(ClassBase):
    street: str
    city: str
    country: str

class Employee(ClassBase):
    person: Person
    address: Address
    salary: float
    start_date: str
```

## Creating Sample Data

```python
employees = [
    Employee(
        person=Person(name="Alice Johnson", age=30, email="alice@company.com", department="Engineering"),
        address=Address(street="123 Main St", city="San Francisco", country="USA"),
        salary=95000.0,
        start_date="2022-01-15"
    ),
    Employee(
        person=Person(name="Bob Smith", age=25, email="bob@company.com", department="Sales"),
        address=Address(street="456 Oak Ave", city="New York", country="USA"),
        salary=75000.0,
        start_date="2023-03-20"
    ),
    Employee(
        person=Person(name="Carol Williams", age=35, email="carol@company.com", department="Engineering"),
        address=Address(street="789 Pine Rd", city="Austin", country="USA"),
        salary=105000.0,
        start_date="2021-11-08"
    ),
]
```

## Basic Filtering

Create a searchable collection and filter it:

```python
# Create a SearchBase collection
employee_search = SearchBase(employees)

# Filter by department
engineers = employee_search.filter(person__department="Engineering")
print(f"Found {len(engineers)} engineers")

# Filter by multiple criteria
senior_engineers = employee_search.filter(
    person__department="Engineering",
    person__age__gte=30
)
print(f"Found {len(senior_engineers)} senior engineers")

# Filter by nested attributes
sf_employees = employee_search.filter(address__city="San Francisco")
print(f"Found {len(sf_employees)} employees in San Francisco")
```

## Using Operators

AttrMagic supports various Django-style operators:

```python
# Greater than / less than
high_earners = employee_search.filter(salary__gt=90000)
young_employees = employee_search.filter(person__age__lt=30)

# String operations
gmail_users = employee_search.filter(person__email__contains="@company.com")
a_names = employee_search.filter(person__name__startswith="A")

# Range operations
mid_age = employee_search.filter(person__age__gte=25, person__age__lte=32)
```

## Working with Individual Records

Use the `get()` method to retrieve single records:

```python
# Get a specific employee
alice = employee_search.get(person__name="Alice Johnson")
print(f"Alice's salary: ${alice.salary:,.2f}")

# Get with default value
unknown = employee_search.get(person__name="Unknown Person", default=None)
if unknown is None:
    print("Employee not found")

# This would raise ValueError if multiple or no results
try:
    engineer = employee_search.get(person__department="Engineering")  # Multiple results!
except ValueError as e:
    print(f"Error: {e}")
```

## Direct Attribute Access

Access nested attributes directly:

```python
alice = employee_search.get(person__name="Alice Johnson")

# Traditional access
print(alice.person.address.city)

# AttrMagic attribute path access
print(alice.getattr_path("person__address__city"))
print(alice.getattr_path("address__city"))  # Also works!

# With default values
country = alice.getattr_path("address__country", default="Unknown")
missing = alice.getattr_path("person__nonexistent", default="Not found")
```

## Next Steps

Now that you've seen the basics, explore:

- [Advanced Filtering](usage/advanced.md) for complex queries
- [Negation with Q Objects](usage/negation.md) for logical operations
- [API Reference](reference/models.md) for complete documentation

## Common Patterns

### Chaining Filters

```python
result = employee_search.filter(
    person__department="Engineering"
).filter(
    salary__gt=90000
)
```

### Multiple Criteria

```python
# All criteria must match (AND logic)
result = employee_search.filter(
    person__age__gte=30,
    person__department="Engineering",
    address__country="USA"
)
```

### Working with Results

```python
engineers = employee_search.filter(person__department="Engineering")

# Iterate over results
for engineer in engineers:
    print(f"{engineer.person.name}: ${engineer.salary:,.2f}")

# Get count
print(f"Total engineers: {len(engineers)}")

# Convert to list
engineer_list = list(engineers)
```
