# Advanced Filtering

This guide covers advanced filtering techniques and patterns for complex use cases.

## Multiple Criteria Filtering

### AND Logic (Default)

When you specify multiple criteria, they're combined with AND logic:

```python
from attrmagic import SearchBase, ClassBase

class Employee(ClassBase):
    name: str
    department: str
    age: int
    salary: float
    skills: list[str]

employees = SearchBase([...])

# All conditions must be true
senior_engineers = employees.filter(
    department="Engineering",  # AND
    age__gte=30,              # AND
    salary__gt=90000          # AND
)
```

### Working with Collections and Lists

```python
class Project(ClassBase):
    name: str
    team_members: list[Employee]
    budget: float
    status: str

projects = SearchBase([...])

# Filter by nested list attributes
large_teams = projects.filter(team_members__len__gte=5)

# Access specific team member attributes
# Note: This accesses the first team member (index 0)
projects_with_senior_lead = projects.filter(
    team_members__0__age__gte=35
)
```

## Pattern: Exclude vs. Filter with Negation

AttrMagic provides both `filter()` with negation and `exclude()` for removing items:

```python
# Using exclude() - removes matching items
non_engineers = employees.exclude(department="Engineering")

# Using filter() with Q negation - keeps non-matching items
from attrmagic import Q
also_non_engineers = employees.filter(~Q(department="Engineering"))

# These are equivalent, choose based on readability
```

### When to Use Each

```python
# Use exclude() for simple conditions
active_employees = employees.exclude(active=False)

# Use ~Q() for complex logic or when combining with other Q objects
complex_filter = employees.filter(
    Q(department="Engineering"),
    ~Q(salary__lt=80000),    # NOT low salary
    ~Q(experience__lt=2)     # NOT low experience
)
```

## Advanced String Filtering

### Case-Insensitive Operations

```python
# Find employees with emails containing specific domains (case-insensitive)
gmail_users = employees.filter(email__icontains="gmail")
corporate_emails = employees.filter(email__iendswith=".corp")

# Case-sensitive versions
exact_gmail = employees.filter(email__contains="@gmail.com")
```

### Complex String Patterns

```python
# Multiple string conditions
doctors = employees.filter(
    name__startswith="Dr.",
    email__endswith=".edu"
)

# Find employees with compound last names
hyphenated_names = employees.filter(name__contains="-")

# Find employees with specific title patterns
senior_titles = employees.filter(
    title__icontains="senior"
).filter(
    title__icontains="engineer"
)
```

## Numeric Range Operations

### Range Filtering

```python
# Age ranges
mid_career = employees.filter(age__range=[28, 45])

# Salary bands
mid_range_salary = employees.filter(salary__range=[75000, 125000])

# Combining ranges
experienced_mid_salary = employees.filter(
    age__range=[30, 50],
    salary__range=[80000, 120000],
    experience__range=[5, 15]
)
```

### Boundary Conditions

```python
# Inclusive boundaries with gte/lte
millennials = employees.filter(
    birth_year__gte=1981,
    birth_year__lte=1996
)

# Exclusive boundaries with gt/lt
strictly_between = employees.filter(
    salary__gt=75000,    # Excludes exactly 75000
    salary__lt=125000    # Excludes exactly 125000
)
```

## Working with Dates and Times

```python
from datetime import datetime, date

class EmployeeWithDates(ClassBase):
    name: str
    hire_date: date
    last_review: datetime
    contract_end: date | None

dated_employees = SearchBase([...])

# Filter by date ranges
recent_hires = dated_employees.filter(
    hire_date__gte=date(2023, 1, 1)
)

# Filter by date components (if your dates support it)
january_hires = dated_employees.filter(
    hire_date__month=1  # Note: This depends on your date implementation
)
```

## List and Collection Operations

### Membership Testing

```python
class EmployeeWithSkills(ClassBase):
    name: str
    skills: list[str]
    departments: list[str]

skilled_employees = SearchBase([...])

# Check if any skill matches
python_developers = skilled_employees.filter(skills__contains="Python")

# Check for specific department membership
multi_dept = skilled_employees.filter(departments__contains="Engineering")
```

### List Length Operations

```python
# Filter by number of skills
versatile = skilled_employees.filter(skills__len__gte=5)
specialists = skilled_employees.filter(skills__len__lte=2)

# Filter by department count
dedicated = skilled_employees.filter(departments__len=1)
cross_functional = skilled_employees.filter(departments__len__gt=1)
```

## Performance Optimization Patterns

### Query Ordering

```python
# More efficient: Filter by most selective criteria first
efficient_query = employees.filter(
    department="Engineering",      # Assuming this is most selective
    specialty="Machine Learning",  # Then this
    age__gte=30                   # Finally this
)

# Less efficient: Broad filters first
less_efficient = employees.filter(
    age__gte=18,                  # Very broad
    salary__gt=0,                 # Even broader
    department="Engineering"      # Most selective last
)
```

### Reusing Filter Objects

```python
# Create reusable filter components
base_employee_filter = employees.filter(active=True)

# Apply additional filters to the base
engineers = base_employee_filter.filter(department="Engineering")
sales_team = base_employee_filter.filter(department="Sales")
managers = base_employee_filter.filter(role="Manager")
```

### Avoiding Redundant Operations

```python
# Good: Single filter with multiple conditions
good = employees.filter(
    department="Engineering",
    age__gte=30,
    salary__gt=90000
)

# Less good: Chained filters (creates intermediate objects)
less_good = employees.filter(department="Engineering") \
                    .filter(age__gte=30) \
                    .filter(salary__gt=90000)
```

## Error Handling Patterns

### Graceful Degradation

```python
def find_employee_safely(employees, **criteria):
    """Find employee with graceful error handling."""
    try:
        return employees.get(**criteria)
    except ValueError as e:
        if "returned no items" in str(e):
            return None
        elif "returned more than one item" in str(e):
            # Return first match instead
            results = employees.filter(**criteria)
            return results[0] if results else None
        raise

# Usage
employee = find_employee_safely(employees, department="Engineering", role="Lead")
if employee:
    print(f"Found: {employee.name}")
else:
    print("No unique match found")
```

### Validation Before Filtering

```python
def safe_filter(employees, **criteria):
    """Filter with validation."""
    valid_fields = {'name', 'department', 'age', 'salary', 'active'}

    # Check for valid field names
    for field_path in criteria.keys():
        base_field = field_path.split('__')[0]
        if base_field not in valid_fields:
            raise ValueError(f"Invalid field: {base_field}")

    return employees.filter(**criteria)

# Usage
try:
    result = safe_filter(employees, department="Engineering", invalid_field="value")
except ValueError as e:
    print(f"Filter error: {e}")
```

## Custom Operator Patterns

While AttrMagic provides many operators, you might want custom logic:

```python
def filter_by_name_length(employees, min_length=None, max_length=None):
    """Custom filter by name length."""
    result = employees

    if min_length:
        result = [emp for emp in result if len(emp.name) >= min_length]

    if max_length:
        result = [emp for emp in result if len(emp.name) <= max_length]

    return SearchBase(result)

# Usage
short_names = filter_by_name_length(employees, max_length=10)
long_names = filter_by_name_length(employees, min_length=15)
```

## Combining AttrMagic with Other Tools

### With Pandas

```python
import pandas as pd

# Convert AttrMagic results to DataFrame
engineers = employees.filter(department="Engineering")
df = pd.DataFrame([emp.model_dump() for emp in engineers])

# Perform pandas operations
avg_salary = df['salary'].mean()
salary_stats = df['salary'].describe()
```

### With Standard Library

```python
from itertools import groupby
from operator import attrgetter

# Group employees by department
employees_list = list(employees)
by_dept = groupby(
    sorted(employees_list, key=attrgetter('department')),
    key=attrgetter('department')
)

for dept, group in by_dept:
    dept_employees = SearchBase(list(group))
    seniors = dept_employees.filter(age__gte=30)
    print(f"{dept}: {len(seniors)} senior employees")
```

## Next Steps

- Learn about [Negation with Q Objects](negation.md) for even more complex logic
- Check the [Examples](../examples.md) for real-world scenarios
- Explore the [API Reference](../reference/models.md) for complete method documentation
