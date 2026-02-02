# Examples

This page provides practical examples of using AttrMagic in real-world scenarios.

## Example 1: Employee Management System

A comprehensive example showing how to build an employee management system with AttrMagic.

```python
from datetime import date, datetime
from attrmagic import ClassBase, SearchBase, Q

class Address(ClassBase):
    street: str
    city: str
    state: str
    zipcode: str
    country: str = "USA"

class Skill(ClassBase):
    name: str
    level: str  # "Beginner", "Intermediate", "Advanced", "Expert"
    years_experience: int

class Department(ClassBase):
    name: str
    budget: float
    manager_id: str | None = None

class Employee(ClassBase):
    employee_id: str
    name: str
    email: str
    hire_date: date
    salary: float
    department: str
    address: Address
    skills: list[Skill]
    active: bool = True
    manager_id: str | None = None

# Create sample data
employees = SearchBase([
    Employee(
        employee_id="E001",
        name="Alice Johnson",
        email="alice.johnson@company.com",
        hire_date=date(2020, 3, 15),
        salary=95000,
        department="Engineering",
        address=Address(
            street="123 Tech Ave",
            city="San Francisco",
            state="CA",
            zipcode="94105"
        ),
        skills=[
            Skill(name="Python", level="Expert", years_experience=8),
            Skill(name="Machine Learning", level="Advanced", years_experience=5),
            Skill(name="Leadership", level="Intermediate", years_experience=3)
        ]
    ),
    Employee(
        employee_id="E002",
        name="Bob Smith",
        email="bob.smith@company.com",
        hire_date=date(2021, 7, 22),
        salary=75000,
        department="Sales",
        address=Address(
            street="456 Market St",
            city="New York",
            state="NY",
            zipcode="10001"
        ),
        skills=[
            Skill(name="Sales", level="Advanced", years_experience=6),
            Skill(name="Negotiation", level="Expert", years_experience=8),
            Skill(name="CRM Software", level="Intermediate", years_experience=4)
        ]
    ),
    Employee(
        employee_id="E003",
        name="Carol Williams",
        email="carol.williams@company.com",
        hire_date=date(2019, 11, 8),
        salary=105000,
        department="Engineering",
        address=Address(
            street="789 Innovation Blvd",
            city="Austin",
            state="TX",
            zipcode="73301"
        ),
        skills=[
            Skill(name="Java", level="Expert", years_experience=10),
            Skill(name="System Architecture", level="Advanced", years_experience=7),
            Skill(name="Team Management", level="Advanced", years_experience=5)
        ]
    )
])
```

### Common Queries

```python
# Find all engineers
engineers = employees.filter(department="Engineering")
print(f"Engineers: {len(engineers)}")

# Find high earners in California
ca_high_earners = employees.filter(
    address__state="CA",
    salary__gte=90000
)

# Find employees with expert-level skills
experts = employees.filter(skills__level="Expert")

# Find recently hired employees (after 2021)
recent_hires = employees.filter(hire_date__gte=date(2021, 1, 1))

# Complex query: Senior engineers with management experience
senior_engineer_managers = employees.filter(
    department="Engineering",
    salary__gte=100000,
    skills__name__icontains="management"
)

# Using Q objects for complex logic
experienced_non_sales = employees.filter(
    ~Q(department="Sales"),
    Q(hire_date__lt=date(2021, 1, 1))
)
```

### Analytics Queries

```python
# Department statistics
def get_department_stats(employees, dept_name):
    dept_employees = employees.filter(department=dept_name)
    if not dept_employees:
        return None

    salaries = [emp.salary for emp in dept_employees]
    return {
        "count": len(dept_employees),
        "avg_salary": sum(salaries) / len(salaries),
        "min_salary": min(salaries),
        "max_salary": max(salaries),
        "total_payroll": sum(salaries)
    }

# Get stats for all departments
departments = set(emp.department for emp in employees)
for dept in departments:
    stats = get_department_stats(employees, dept)
    print(f"{dept}: {stats}")
```

## Example 2: E-commerce Product Catalog

Managing a product catalog with complex filtering requirements.

```python
class Category(ClassBase):
    id: str
    name: str
    parent_id: str | None = None

class Review(ClassBase):
    user_id: str
    rating: int  # 1-5
    comment: str
    date: date

class Product(ClassBase):
    id: str
    name: str
    description: str
    price: float
    category: Category
    in_stock: bool
    stock_quantity: int
    tags: list[str]
    reviews: list[Review]

    @property
    def average_rating(self) -> float:
        if not self.reviews:
            return 0.0
        return sum(r.rating for r in self.reviews) / len(self.reviews)

# Create product catalog
products = SearchBase([
    Product(
        id="P001",
        name="Wireless Bluetooth Headphones",
        description="Premium noise-cancelling headphones",
        price=199.99,
        category=Category(id="C001", name="Electronics"),
        in_stock=True,
        stock_quantity=45,
        tags=["wireless", "bluetooth", "noise-cancelling", "premium"],
        reviews=[
            Review(user_id="U001", rating=5, comment="Great sound quality!", date=date(2024, 1, 15)),
            Review(user_id="U002", rating=4, comment="Good but expensive", date=date(2024, 1, 20))
        ]
    ),
    Product(
        id="P002",
        name="USB-C Charging Cable",
        description="Fast charging USB-C cable, 6ft length",
        price=12.99,
        category=Category(id="C002", name="Accessories"),
        in_stock=True,
        stock_quantity=150,
        tags=["usb-c", "charging", "cable", "fast-charging"],
        reviews=[
            Review(user_id="U003", rating=4, comment="Works well", date=date(2024, 2, 1)),
            Review(user_id="U004", rating=5, comment="Perfect length", date=date(2024, 2, 5))
        ]
    )
    # ... more products
])

# E-commerce queries
def search_products():
    # Find products in stock under $50
    affordable_in_stock = products.filter(
        in_stock=True,
        price__lt=50.00
    )

    # Find electronics with good reviews (4+ stars)
    # Note: This is a simplified version - you'd need custom logic for average rating
    electronics = products.filter(category__name="Electronics")
    good_electronics = [p for p in electronics if p.average_rating >= 4.0]

    # Find products with specific tags
    wireless_products = products.filter(tags__contains="wireless")

    # Find low stock items (less than 10)
    low_stock = products.filter(
        in_stock=True,
        stock_quantity__lt=10
    )

    # Complex search: Premium products with good reviews, excluding out of stock
    premium_available = products.filter(
        ~Q(in_stock=False),
        Q(price__gte=100.00),
        Q(tags__contains="premium")
    )

    return {
        "affordable_in_stock": affordable_in_stock,
        "good_electronics": SearchBase(good_electronics),
        "wireless_products": wireless_products,
        "low_stock": low_stock,
        "premium_available": premium_available
    }
```

## Example 3: Student Information System

Academic record management with complex relationships.

```python
class Course(ClassBase):
    code: str
    name: str
    credits: int
    department: str

class Grade(ClassBase):
    course: Course
    grade: str  # "A", "B", "C", "D", "F"
    semester: str
    year: int

    @property
    def grade_points(self) -> float:
        grade_map = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0}
        return grade_map.get(self.grade, 0.0)

class Student(ClassBase):
    student_id: str
    name: str
    email: str
    major: str
    graduation_year: int
    grades: list[Grade]
    active: bool = True

    @property
    def gpa(self) -> float:
        if not self.grades:
            return 0.0

        total_points = sum(g.grade_points * g.course.credits for g in self.grades)
        total_credits = sum(g.course.credits for g in self.grades)
        return total_points / total_credits if total_credits > 0 else 0.0

# Create student database
students = SearchBase([
    Student(
        student_id="S001",
        name="Emily Davis",
        email="emily.davis@university.edu",
        major="Computer Science",
        graduation_year=2024,
        grades=[
            Grade(
                course=Course(code="CS101", name="Intro to Programming", credits=3, department="Computer Science"),
                grade="A",
                semester="Fall",
                year=2020
            ),
            Grade(
                course=Course(code="MATH201", name="Calculus II", credits=4, department="Mathematics"),
                grade="B",
                semester="Spring",
                year=2021
            )
        ]
    )
    # ... more students
])

# Academic queries
def academic_reports():
    # Find students by major
    cs_students = students.filter(major="Computer Science")

    # Find students graduating this year
    current_graduates = students.filter(graduation_year=2024)

    # Find students with courses in specific departments
    math_students = students.filter(grades__course__department="Mathematics")

    # Find students with excellent grades (mostly A's)
    excellent_students = students.filter(grades__grade="A")

    # Find at-risk students (those with F grades)
    at_risk = students.filter(grades__grade="F")

    # Complex query: Active CS students graduating soon with good grades
    promising_cs_students = students.filter(
        Q(major="Computer Science"),
        Q(graduation_year__lte=2025),
        Q(active=True),
        ~Q(grades__grade="F")  # No failing grades
    )

    return {
        "cs_students": cs_students,
        "current_graduates": current_graduates,
        "promising_cs": promising_cs_students
    }
```

## Example 4: Event Management System

Managing events, attendees, and registrations.

```python
class Venue(ClassBase):
    name: str
    address: Address
    capacity: int
    amenities: list[str]

class Registration(ClassBase):
    attendee_email: str
    registration_date: datetime
    ticket_type: str  # "Regular", "VIP", "Student"
    payment_status: str  # "Pending", "Paid", "Refunded"

class Event(ClassBase):
    id: str
    title: str
    description: str
    start_date: datetime
    end_date: datetime
    venue: Venue
    category: str
    price: float
    max_attendees: int
    registrations: list[Registration]
    active: bool = True

    @property
    def available_spots(self) -> int:
        confirmed = len([r for r in self.registrations if r.payment_status == "Paid"])
        return self.max_attendees - confirmed

# Event management queries
events = SearchBase([...])  # Your events data

def event_queries():
    # Find upcoming events
    from datetime import datetime, timedelta
    now = datetime.now()
    upcoming = events.filter(
        start_date__gte=now,
        active=True
    )

    # Find events with available spots
    available_events = [e for e in events if e.available_spots > 0]

    # Find tech events in specific cities
    tech_events_sf = events.filter(
        category__icontains="technology",
        venue__address__city="San Francisco"
    )

    # Find expensive events (> $100) with VIP options
    premium_events = events.filter(
        price__gt=100.00,
        registrations__ticket_type="VIP"
    )

    # Complex query: Popular upcoming events with space
    popular_upcoming = events.filter(
        Q(start_date__gte=now),
        Q(active=True),
        ~Q(registrations__payment_status="Refunded")  # Exclude events with many refunds
    )

    # Filter results with available spots
    popular_with_space = [e for e in popular_upcoming if e.available_spots > 10]

    return SearchBase(popular_with_space)
```

## Example 5: Integration with Web Framework

Using AttrMagic in a FastAPI application.

```python
from fastapi import FastAPI, Query, HTTPException
from typing import Optional

app = FastAPI()

# Assuming you have your employees SearchBase from Example 1
global_employees = employees  # Your employee data

@app.get("/employees")
async def get_employees(
    department: Optional[str] = None,
    min_salary: Optional[float] = None,
    max_salary: Optional[float] = None,
    state: Optional[str] = None,
    skill: Optional[str] = None,
    active_only: bool = True
):
    """Get employees with optional filtering."""
    result = global_employees

    # Apply filters based on query parameters
    if active_only:
        result = result.filter(active=True)

    if department:
        result = result.filter(department=department)

    if min_salary:
        result = result.filter(salary__gte=min_salary)

    if max_salary:
        result = result.filter(salary__lte=max_salary)

    if state:
        result = result.filter(address__state=state)

    if skill:
        result = result.filter(skills__name__icontains=skill)

    return [emp.model_dump() for emp in result]

@app.get("/employees/{employee_id}")
async def get_employee(employee_id: str):
    """Get a specific employee by ID."""
    try:
        employee = global_employees.get(employee_id=employee_id)
        return employee.model_dump()
    except ValueError:
        raise HTTPException(status_code=404, detail="Employee not found")

@app.get("/departments/{dept_name}/stats")
async def get_department_stats(dept_name: str):
    """Get statistics for a specific department."""
    dept_employees = global_employees.filter(department=dept_name)

    if not dept_employees:
        raise HTTPException(status_code=404, detail="Department not found")

    salaries = [emp.salary for emp in dept_employees]

    return {
        "department": dept_name,
        "employee_count": len(dept_employees),
        "average_salary": sum(salaries) / len(salaries),
        "salary_range": {
            "min": min(salaries),
            "max": max(salaries)
        },
        "total_payroll": sum(salaries)
    }
```

These examples demonstrate AttrMagic's flexibility across different domains and use cases. The library's Django-inspired syntax makes it intuitive for developers familiar with ORM patterns, while its Pydantic foundation ensures type safety and data validation.
