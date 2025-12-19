import io
from decimal import Decimal

from app.extensions import db
from app.models.account import Account
from app.models.user import User


def register(client, username: str, email: str, password: str = "password"):
    return client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )


def login(client, email: str, password: str = "password"):
    return client.post("/auth/login", json={"email": email, "password": password})


def test_auth_flow(client, app):
    resp = register(client, "alice", "alice@test.com")
    assert resp.status_code == 201

    resp = login(client, "alice@test.com")
    assert resp.status_code == 200

    resp = client.get("/auth/me")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["email"] == "alice@test.com"

    resp = client.post("/auth/logout")
    assert resp.status_code == 200


def test_transfer_and_balances(client, app):
    # User A
    register(client, "sender", "sender@test.com")
    login(client, "sender@test.com")

    # User B
    with app.app_context():
        recipient = User(username="recipient", email="recipient@test.com")
        recipient.set_password("password")
        db.session.add(recipient)
        db.session.commit()
        recipient_account = Account(number="99999", user_id=recipient.id, balance=Decimal("0.00"))
        db.session.add(recipient_account)
        db.session.commit()

    resp = client.post("/transfer", json={"target_account": "99999", "amount": "150.50"})
    assert resp.status_code == 200

    with app.app_context():
        sender = User.query.filter_by(email="sender@test.com").first()
        sender_account = Account.query.filter_by(user_id=sender.id).first()
        recipient_account = Account.query.filter_by(number="99999").first()
        assert sender_account.balance == Decimal("849.50")  # 1000 - 150.50
        assert recipient_account.balance == Decimal("150.50")


def test_deposit_and_withdraw(client, app):
    register(client, "bob", "bob@test.com")
    login(client, "bob@test.com")

    resp = client.post("/deposit", json={"amount": "500.00"})
    assert resp.status_code == 200

    resp = client.post("/withdraw", json={"amount": "200.00"})
    assert resp.status_code == 200

    with app.app_context():
        user = User.query.filter_by(email="bob@test.com").first()
        account = Account.query.filter_by(user_id=user.id).first()
        assert account.balance == Decimal("1300.00")  # 1000 + 500 - 200


def test_profile_upload_with_preferences(client, app):
    register(client, "charlie", "charlie@test.com")
    login(client, "charlie@test.com")

    image_bytes = io.BytesIO(b"fake-image-bytes")
    resp = client.put(
        "/users/profile",
        data={
            "preferences": '{"lang": "pt-BR", "theme": "light"}',
            "profile_image": (image_bytes, "avatar.png"),
        },
        content_type="multipart/form-data",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["user"]["preferences"]["lang"] == "pt-BR"
    assert data["user"]["profile_image"]


def test_profile_upload_rejects_large_file(client):
    register(client, "dave", "dave@test.com")
    login(client, "dave@test.com")

    big_bytes = io.BytesIO(b"0" * (3 * 1024 * 1024))
    resp = client.put(
        "/users/profile",
        data={"profile_image": (big_bytes, "big.png")},
        content_type="multipart/form-data",
    )
    assert resp.status_code in (400, 413)


def test_insufficient_funds_error(client, app):
    register(client, "eve", "eve@test.com")
    login(client, "eve@test.com")

    resp = client.post("/withdraw", json={"amount": "1000000.00"})
    assert resp.status_code == 400 or resp.status_code == 500


def test_rate_limit_register(client):
    for i in range(5):
        resp = register(client, f"u{i}", f"u{i}@test.com")
        assert resp.status_code in (201, 400)

    resp = register(client, "rate", "rate@test.com")
    assert resp.status_code == 429