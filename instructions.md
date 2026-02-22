### Actividad 6.2. Ejercicio de programación 3

**Programming Exercise**: Reservation System

**Description**
    **Req 1**. Implement a set of classes in Python that implements two abstractions:
        1. Hotel
        2. Reservation
        3. Customers
    **Req 2**. Implement a set of methods to handle the next persistent behaviors (stored in files):
        1. Hotels
            a. Create Hotel
            b. Delete Hotel
            c. Display Hotel information
            d. Modify Hotel Information
            e. Reserve a Room
            f. Cancel a Reservation
        2. Customer
            a. Create Customer
            b. Delete a Customer
            c. Display Customer Information
            d. Modify Customer Information
        3. Reservation
            a. Create a Reservation (Customer, Hotel)
            b. Cancel a Reservation
        You are free to decide the attributes within each class that enable the required behavior.
    **Req 3**. Implement unit test cases to exercise the methods in each class. Use the unittest module in Python.
    **Req 4**. The code coverage for all unittests should accumulate at least 85% of line coverage.
    **Req 5**. The program shall include the mechanism to handle invalid data in the file. Errors should be displayed in the console and the execution must continue.
    **Req 6**. Be compliant with PEP8.
    **Req 7**. The source code must show no warnings using Fleak and PyLint.

**Practice**
- Control structures
- Console Input/output
- Mathematical computation
- File management
- Error handling

**Test Cases and Evidence**
- Record the execution.
- Use files included in the assignment.




reservation-system/
├─ README.md
├─ pyproject.toml                 # Config opcional para black/isort/flake8
├─ requirements-dev.txt           # Herramientas de desarrollo (flake8, pylint, coverage, black, isort)
├─ data/
│  ├─ hotels.json
│  ├─ customers.json
│  └─ reservations.json
├─ src/
│  └─ reservations/
│     ├─ __init__.py
│     ├─ models.py                # Clases: Hotel, Customer, Reservation (dataclasses)
│     ├─ repository.py            # Capa de acceso a datos (JSON)
│     ├─ services.py              # Lógica: crear/modificar/etc., reservar/cancelar
│     ├─ validators.py            # Validaciones y utilidades (fechas, overlapping)
│     └─ errors.py                # Excepciones propias
├─ tests/
│  ├─ __init__.py
│  ├─ test_hotels.py
│  ├─ test_customers.py
│  ├─ test_reservations.py
│  └─ test_repository_validation.py
└─ scripts/
   └─ demo_seed.py                # Script opcional para poblar datos de prueba
