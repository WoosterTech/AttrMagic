# Negation with Q Objects

AttrMagic supports advanced logical operations using Q objects, similar to Django's ORM. This allows you to create complex queries with negation using the `~` operator.

## Introduction to Q Objects

Q objects provide a way to encapsulate filter conditions and apply logical operations to them:

```python
from attrmagic import Q, ClassBase, SearchBase

class Employee(ClassBase):
    name: str
    department: str
    age: int
    salary: float
    active: bool

employees = SearchBase([
    Employee(name="Alice", department="Engineering", age=30, salary=95000, active=True),
    Employee(name="Bob", department="Sales", age=25, salary=75000, active=True),
    Employee(name="Carol", department="Engineering", age=35, salary=105000, active=False),
    Employee(name="David", department="HR", age=28, salary=65000, active=True),
])
```

## Basic Q Object Usage

### Creating Q Objects

```python
# Create Q objects for different conditions
engineering_filter = Q(department="Engineering")
senior_filter = Q(age__gte=30)
high_salary_filter = Q(salary__gt=90000)

# Use Q objects in filter methods
engineers = employees.filter(engineering_filter)
seniors = employees.filter(senior_filter)
```

### Q Objects vs. Keyword Arguments

```python
# These are equivalent:
result1 = employees.filter(Q(department="Engineering"))
result2 = employees.filter(department="Engineering")

# Q objects become useful with logical operations
```

## Negation with the ~ Operator

### Basic Negation

```python
# Find employees NOT in Engineering
non_engineers = employees.filter(~Q(department="Engineering"))

# Find employees NOT making more than 80000
lower_salary = employees.filter(~Q(salary__gt=80000))

# Find inactive employees (negating active=True)
inactive = employees.filter(~Q(active=True))
```

### Complex Negation

```python
# Find employees who are NOT (young AND in sales)
# Equivalent to: NOT (age < 30 AND department = "Sales")
not_young_sales = employees.filter(
    ~Q(age__lt=30),
    ~Q(department="Sales")
)

# Find employees who are NOT inactive OR are high earners
# This demonstrates De Morgan's laws in practice
complex_filter = employees.filter(
    ~Q(active=False)  # Must be active
    # OR we could combine with other conditions
)
```

## Combining Q Objects and Keyword Arguments

You can mix Q objects with traditional keyword arguments:

```python
# Mix Q objects with kwargs - all conditions are ANDed together
senior_active_non_hr = employees.filter(
    Q(age__gte=30),          # Q object
    ~Q(department="HR"),      # Negated Q object
    active=True              # Traditional kwarg
)

# Find active employees who are either senior OR high earners
# Note: This requires separate filter calls for OR logic
senior_or_high_earners = employees.filter(
    Q(active=True)  # Must be active
    # Then filter for senior OR high salary separately
)

# For true OR logic, you'd need multiple queries:
senior_active = employees.filter(age__gte=30, active=True)
high_earner_active = employees.filter(salary__gt=90000, active=True)
# Then combine the results as needed
```

## Advanced Patterns

### Multiple Negations

```python
# Find employees who are:
# - NOT in HR
# - NOT inactive
# - NOT low-paid (< 70000)
qualified_candidates = employees.filter(
    ~Q(department="HR"),
    ~Q(active=False),
    ~Q(salary__lt=70000)
)
```

### Nested Attribute Negation

```python
class Address(ClassBase):
    city: str
    state: str
    country: str

class EmployeeWithAddress(ClassBase):
    name: str
    address: Address
    department: str

employees_with_address = SearchBase([
    EmployeeWithAddress(
        name="Alice",
        department="Engineering",
        address=Address(city="San Francisco", state="CA", country="USA")
    ),
    EmployeeWithAddress(
        name="Bob",
        department="Sales",
        address=Address(city="New York", state="NY", country="USA")
    ),
])

# Find employees NOT in California
non_ca_employees = employees_with_address.filter(~Q(address__state="CA"))

# Find employees NOT in major tech cities
non_tech_hubs = employees_with_address.filter(
    ~Q(address__city="San Francisco"),
    ~Q(address__city="Seattle"),
    ~Q(address__city="Austin")
)
```

### Reusable Filter Patterns

```python
# Define reusable filters
class EmployeeFilters:
    @staticmethod
    def senior_employees():
        return Q(age__gte=30)

    @staticmethod
    def high_earners():
        return Q(salary__gt=90000)

    @staticmethod
    def engineering_dept():
        return Q(department="Engineering")

    @staticmethod
    def active_employees():
        return Q(active=True)

# Use reusable filters
senior_engineers = employees.filter(
    EmployeeFilters.senior_employees(),
    EmployeeFilters.engineering_dept(),
    EmployeeFilters.active_employees()
)

# Negate reusable filters
non_senior_non_engineers = employees.filter(
    ~EmployeeFilters.senior_employees(),
    ~EmployeeFilters.engineering_dept()
)
```

## Type Safety

Q objects maintain full type safety with modern Python type checkers:

```python
# Type checker understands the return type
engineering_filter: "Filter[Employee]" = Q(department="Engineering")
negated_filter: "Filter[Employee]" = ~engineering_filter

# No type checker warnings
result: SearchBase[Employee] = employees.filter(negated_filter)
```

## Performance Considerations

### Efficient Negation

```python
# Efficient: Single negated condition
non_engineers = employees.filter(~Q(department="Engineering"))

# Less efficient: Multiple separate negations
# (Though still valid and readable)
complex_filter = employees.filter(~Q(department="HR")) \
                          .filter(~Q(salary__lt=50000)) \
                          .filter(~Q(active=False))

# More efficient version of the above
complex_filter_better = employees.filter(
    ~Q(department="HR"),
    ~Q(salary__lt=50000),
    ~Q(active=False)
)
```

### Memory Usage

```python
# Q objects are lightweight and can be reused
base_filter = Q(active=True)
engineering_active = employees.filter(base_filter, department="Engineering")
sales_active = employees.filter(base_filter, department="Sales")

# Negated filters are also lightweight
inactive_filter = ~base_filter
inactive_employees = employees.filter(inactive_filter)
```

## Error Handling

### Invalid Q Object Construction

```python
try:
    # Q objects require exactly one keyword argument
    invalid_q = Q(department="Engineering", age__gt=30)
except ValueError as e:
    print(f"Error: {e}")  # "Q() objects must have exactly one keyword argument"

# Correct usage:
dept_filter = Q(department="Engineering")
age_filter = Q(age__gt=30)
result = employees.filter(dept_filter, age_filter)
```

### Debugging Complex Queries

```python
# Break down complex negated queries for debugging
print("Original employees:", len(employees))

non_hr = employees.filter(~Q(department="HR"))
print("Non-HR employees:", len(non_hr))

non_hr_active = non_hr.filter(Q(active=True))
print("Non-HR active employees:", len(non_hr_active))

final_result = non_hr_active.filter(Q(salary__gt=70000))
print("Final result:", len(final_result))
```

## Django ORM Comparison

If you're familiar with Django, here's how AttrMagic compares:

```python
# Django ORM
from django.db.models import Q
queryset.filter(~Q(department='Engineering'))
queryset.filter(Q(age__gte=30) & ~Q(department='HR'))

# AttrMagic (very similar!)
from attrmagic import Q
employees.filter(~Q(department='Engineering'))
employees.filter(Q(age__gte=30), ~Q(department='HR'))  # Multiple args = AND
```

The main difference is that AttrMagic doesn't have `&` and `|` operators for Q objects yet, so you combine conditions by passing multiple Q objects to `filter()` (which applies AND logic).

## Next Steps

- Explore [Advanced Filtering](advanced.md) for more complex patterns
- Check out the [API Reference](../reference/models.md) for complete Q object documentation
- See [Examples](../examples.md) for real-world use cases
