import pytest
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.decorators import role_required

def test_jwt_login(client, app):
    # Register
    resp = client.post("/auth/register", json={
        "username": "jwtuser",
        "email": "jwt@test.com",
        "password": "password"
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert "access_token" in data
    token = data["access_token"]
    assert token is not None

    # Login
    resp = client.post("/auth/login", json={
        "email": "jwt@test.com",
        "password": "password"
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert "access_token" in data

def test_role_decorator(client, app):
    # Setup - Add endpoint with role_required
    @app.route("/admin-only", methods=["GET"])
    @role_required("admin")
    def admin_only():
        return jsonify(msg="Welcome Admin"), 200

    # 1. Normal User
    client.post("/auth/register", json={
        "username": "normal", 
        "email": "normal@test.com", 
        "password": "pass"
    })
    resp = client.post("/auth/login", json={"email": "normal@test.com", "password": "pass"})
    normal_token = resp.get_json()["access_token"]

    # Access without token
    resp = client.get("/admin-only")
    assert resp.status_code == 401 # Missing Authorization Header
    
    # Access with normal token
    resp = client.get("/admin-only", headers={"Authorization": f"Bearer {normal_token}"})
    assert resp.status_code == 403
    
    # 2. Admin User
    # Need to manually create admin for test since no endpoint makes admin
    from app.extensions import db
    from app.models.user import User
    
    with app.app_context():
        admin = User(username="admin", email="admin@test.com", is_admin=True)
        admin.set_password("pass")
        db.session.add(admin)
        db.session.commit()
        
    resp = client.post("/auth/login", json={"email": "admin@test.com", "password": "pass"})
    admin_token = resp.get_json()["access_token"]
    
    # Access with admin token
    resp = client.get("/admin-only", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
