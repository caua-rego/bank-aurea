"""
Clean Architecture Controller
- Responsibility: Handle HTTP Requests & Responses (JSON)
- Layer: Interface Adapters
- Dependencies: Services (Business Logic)
"""
from flask import Blueprint, request
from flask_login import login_required, current_user
from app.services.transaction_service import TransactionService
from app.models.account import Account
from app.exceptions import BankError
from app.extensions import limiter

main_bp = Blueprint('main', __name__)
transaction_service = TransactionService()

@main_bp.route('/')
def home():
    return {"message": "Bank Aurea API v6.1"}, 200

@main_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    account = Account.query.filter_by(user_id=current_user.id).first()
    transactions = transaction_service.get_history(account.id)
    
    # Serialize transactions
    tx_list = []
    for t in transactions:
        tx_list.append({
            "id": t.id,
            "amount": str(t.amount), # Decimal to string
            "type": t.type,
            "timestamp": t.timestamp.isoformat(),
            "source": t.source_account_id,
            "target": t.target_account_id
        })
        
    # Generate Fictitious Card Data (Deterministic based on Account ID)
    # Format: 4532 XXXX XXXX <ID padded>
    card_suffix = f"{account.id:04d}"
    card_number = f"4532 9812 7344 {card_suffix}"
    
    return {
        "account": {
            "number": account.number,
            "balance": str(account.balance)
        },
        "card": {
            "number": card_number,
            "holder": current_user.username.upper(),
            "expiry": "12/30",
            "cvv": "842"
        },
        "transactions": tx_list
    }, 200

@main_bp.route('/transfer', methods=['POST'])
@login_required
@limiter.limit("10 per minute")
def transfer():
    data = request.get_json()
    if not data:
        return {"error": "No input data"}, 400
        
    target_account = data.get('target_account')
    amount = data.get('amount')
    
    if not target_account or not amount:
        return {"error": "Missing target_account or amount"}, 400

    account = Account.query.filter_by(user_id=current_user.id).first()
    try:
        transaction_service.transfer(
            source_account_id=account.id,
            target_account_number=target_account,
            amount=amount
        )
        return {"success": True, "message": "Transfer successful"}, 200
    except BankError as e:
        return {"error": str(e)}, 400
    except Exception as e:
        return {"error": "An unexpected error occurred"}, 500

@main_bp.route('/deposit', methods=['POST'])
@login_required
@limiter.limit("5 per minute")
def deposit():
    data = request.get_json()
    amount = data.get('amount')
    if not amount:
        return {"error": "Missing amount"}, 400
        
    account = Account.query.filter_by(user_id=current_user.id).first()
    try:
        transaction_service.deposit(account.id, amount)
        return {"success": True, "message": "Deposit successful"}, 200
    except BankError as e:
        return {"error": str(e)}, 400

@main_bp.route('/withdraw', methods=['POST'])
@login_required
@limiter.limit("5 per minute")
def withdraw():
    data = request.get_json()
    amount = data.get('amount')
    if not amount:
        return {"error": "Missing amount"}, 400

    account = Account.query.filter_by(user_id=current_user.id).first()
    try:
        transaction_service.withdraw(account.id, amount)
        return {"success": True, "message": "Withdrawal successful"}, 200
    except BankError as e:
        return {"error": str(e)}, 400
