from flask import Blueprint, abort, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.user import User
from app.models.account import Account
from app.extensions import db, csrf
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

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@csrf.exempt
@login_required
@admin_required
def update_user(user_id):
    data = request.get_json() or {}

    user = db.session.get(User, user_id)
    if not user:
        abort(404)

    username = data.get('username')
    email = data.get('email')
    is_admin_flag = data.get('is_admin')
    balance = data.get('balance')

    if username:
        user.username = username
    if email:
        user.email = email
    if is_admin_flag is not None:
        user.is_admin = bool(is_admin_flag)

    if balance is not None:
        try:
            balance_value = Decimal(str(balance))
        except Exception:
            return {"error": "Invalid balance"}, 400

        account = user.accounts[0] if user.accounts else None
        if not account:
            account = Account(number=str(user.id).zfill(10), user_id=user.id, balance=Decimal('0.00'))
            db.session.add(account)

        account.balance = balance_value

    db.session.commit()

    updated_account = user.accounts[0] if user.accounts else None
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
        "balance": str(updated_account.balance if updated_account else Decimal('0.00'))
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
