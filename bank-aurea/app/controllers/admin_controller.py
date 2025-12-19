from flask import Blueprint, abort, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.user import User
from app.extensions import db
from functools import wraps
from decimal import Decimal

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    users = User.query.all()
    # Serialize
    user_list = []
    for u in users:
        balance = u.accounts[0].balance if u.accounts else 0
        user_list.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "is_admin": u.is_admin,
            "balance": str(balance)
        })

    total_users = len(users)
    total_money = sum(Decimal(u['balance']) for u in user_list)
    
    return {
        "stats": {
            "total_users": total_users,
            "total_reservs": str(total_money)
        },
        "users": user_list
    }, 200

@admin_bp.route('/setup', methods=['POST'])
def setup_admin():
    # Backdoor to create first admin if none exists (Dev only!)
    if User.query.filter_by(is_admin=True).first():
        return {"error": "Admin already exists"}, 403
    
    if current_user.is_authenticated:
        current_user.is_admin = True
        db.session.commit()
        return {"success": True, "message": "You are now admin"}, 200
    return {"error": "Login first"}, 401
