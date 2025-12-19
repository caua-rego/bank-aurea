# Bank Auréa v2.0 - Secure Banking Platform

Bank Auréa is a senior-level Flask application featuring a robust, modular architecture with military-grade security practices.

## Key Features

- **Secure Authentication**: User registration and login protected by `Flask-Login` and `BCrypt` hashing.
- **Atomic Transactions**: Money transfers are ACID-compliant, ensuring data integrity even during failures.
- **Robust Ledger**: Every financial movement is recorded in a detailed transaction history.
- **CSRF Protection**: All forms are secured against Cross-Site Request Forgery.
- **Clean Architecture**: Separation of concerns using Models, Repositories, Services, and Controllers.

## Tech Stack

- **Framework**: Flask
- **ORM**: SQLAlchemy
- **Auth**: Flask-Login, Flask-Bcrypt
- **Security**: Flask-WTF (CSRF)
- **Testing**: Pytest

## Setup & Run

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run Application**:
    ```bash
    python run.py
    ```

3.  **Run Tests**:
    ```bash
    pytest
    ```

## Architecture Overview

```
app/
├── models/         # User, Account, Transaction
├── repositories/   # Database Abstraction
├── services/       # Business Logic (Auth, Transactions)
├── controllers/    # Route Handlers
├── forms/          # Secure WTForms
├── templates/      # Jinja2 Views
└── extensions.py   # App Wiring
```
