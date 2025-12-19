"""
Clean Architecture Controller
- Responsibility: Handle Authentication Requests
- Layer: Interface Adapters
- Dependencies: AuthService (Business Logic)
"""
from flask import Blueprint, request
from flask_login import login_user, current_user, logout_user, login_required
from app.services.auth_service import AuthService
from app.extensions import limiter

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated:
        return {"message": "Already logged in"}, 200
        
    data = request.get_json()
    if not data:
        return {"error": "No input data provided"}, 400
        
    # Manual validation or use Form logic lightly?
    # Let's simple validate here for JSON API
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return {"error": "Missing fields"}, 400
        
    try:
        auth_service.register_user(username, email, password)
        return {"success": True, "message": "User registered"}, 201
    except Exception as e:
         return {"error": str(e)}, 400

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return {"success": True, "user": current_user.username}, 200
        
    data = request.get_json()
    if not data:
        return {"error": "No input data provided"}, 400
        
    email = data.get('email')
    password = data.get('password')
    
    user = auth_service.authenticate_user(email, password)
    if user:
        login_user(user)
        return {"success": True, "user": user.username, "is_admin": user.is_admin}, 200
    else:
        return {"error": "Invalid credentials"}, 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return {"success": True, "message": "Logged out"}, 200

@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_admin": current_user.is_admin
    }, 200
