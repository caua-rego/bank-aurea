"""Seed data for Bank Aurea.
Run with: FLASK_CONFIG=development python scripts/seed.py
Assumes migrations already applied (flask db upgrade).
"""
import os
from decimal import Decimal

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.account import Account


def ensure_user(username: str, email: str, password: str, is_admin: bool = False) -> User:
    user = User.query.filter_by(email=email).first()
    if user:
        return user

    user = User(username=username, email=email, is_admin=is_admin)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def ensure_account(user: User, number: str, balance: Decimal) -> Account:
    account = Account.query.filter_by(user_id=user.id, number=number).first()
    if account:
        return account
    account = Account(number=number, user_id=user.id, balance=balance)
    db.session.add(account)
    db.session.commit()
    return account


def main():
    app = create_app(os.getenv("FLASK_CONFIG") or "development")
    with app.app_context():
        admin = ensure_user("admin", "admin@aurea.local", "admin123", is_admin=True)
        user = ensure_user("demo", "demo@aurea.local", "demo123", is_admin=False)

        ensure_account(admin, "10001", Decimal("50000.00"))
        ensure_account(user, "20001", Decimal("2500.00"))
        ensure_account(user, "20002", Decimal("125.75"))

        print("Seed completed: admin@aurea.local / admin123, demo@aurea.local / demo123")

if __name__ == "__main__":
    main()
