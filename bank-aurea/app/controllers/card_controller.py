from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.extensions import db, csrf
from app.models.card import Card
import random
from datetime import datetime

card_bp = Blueprint('cards', __name__)

def generate_luhn_card_number(prefix='4000'):
    # Simple Luhn generator logic can be complex, for now we generate random 16 digits
    # and assume it's valid for this mvp context or implement basic luhn.
    
    # 1. Start with prefix
    number = [int(x) for x in prefix]
    
    # 2. Fill up to 15 digits
    while len(number) < 15:
        number.append(random.randint(0, 9))
    
    # 3. Calculate check digit
    digits = list(number)
    odd_sum = 0
    even_sum = 0
    
    # Reverse to process from right to left (check digit is index 0 in reversed thought)
    # But standard luhn: double every second digit from the right
    
    # Easier: Just iterate reversed
    # 15 digits. 
    # Index 14 (last one) is 'even' position from right (1-based index 1) -> wait, check digit IS the 16th.
    # So we have 15 digits. 
    # The check digit will be the 16th.
    
    # Algorithm:
    # Double every second digit from the right-most (which is the 15th digit here?)
    # Let's use a library or a robust snippet if needed, but for MVP:
    
    # Standard implementation:
    # 1. Double every second digit from the *right*, starting with the *check digit's neighbor*.
    # Since we are generating the check digit (16th), we start doubling from the 15th, then 13th...
    
    temp_sum = 0
    for i, digit in enumerate(reversed(number)):
        # i=0 is 15th digit (Odd position from right for check digit calc purposes?)
        # Actually: Payload is 15 digits. Check digit is 16th.
        # Pattern: Double, Single, Double, Single... starting from rightmost payload digit.
        
        val = digit
        if i % 2 == 0: # 1st, 3rd, 5th from right (indices 0, 2, 4...)
            val *= 2
            if val > 9: val -= 9
        temp_sum += val
        
    check_digit = (10 - (temp_sum % 10)) % 10
    number.append(check_digit)
    
    return "".join(map(str, number))

def get_expiry():
    # Current date + 4 years
    now = datetime.now()
    year = (now.year + 4) % 100
    month = now.month
    return f"{month:02d}/{year:02d}"

@card_bp.route('/', methods=['GET'])
@login_required
def get_cards():
    cards = Card.query.filter_by(user_id=current_user.id).all()
    return jsonify([c.to_dict() for c in cards])

@card_bp.route('/generate', methods=['POST'])
@csrf.exempt
@login_required
def generate_card():
    # 1. Check Card Limit
    current_count = Card.query.filter_by(user_id=current_user.id).count()
    if current_count >= 5:
        return jsonify({"error": "Maximum of 5 cards allowed."}), 400

    # 2. Rate Limiting (1 card per minute)
    last_card = Card.query.filter_by(user_id=current_user.id).order_by(Card.created_at.desc()).first()
    if last_card and (datetime.utcnow() - last_card.created_at).total_seconds() < 60:
        return jsonify({"error": "Please wait a moment before creating a new card."}), 429

    # Determine Tier
    # Logic: 
    # Adamantium: Balance >= 1M
    # Gold: Balance >= 5k
    # Free: < 5k
    # Titanium: Invite only (requires is_titanium flag on user)
    
    tier = 'free'
    main_account = current_user.accounts[0] if current_user.accounts else None
    
    if getattr(current_user, 'is_titanium', False):
        tier = 'titanium'
    elif main_account and main_account.balance >= 1000000:
        tier = 'adamantium'
    elif main_account and main_account.balance >= 5000:
        tier = 'gold'
        
    # Generate numbers
    # Prefix can correspond to tier?
    prefix = '4000' # Visa Default
    
    # Optional logic: custom prefixes per tier if desired, e.g.
    if tier == 'adamantium': prefix = '3700' # Amex
    if tier == 'titanium': prefix = '5500' # Mastercard

    # We can mix Luhn with timestamp rand to ensure uniqueness easily or just loop
    # For now, stick to random Luhn
    card_number = generate_luhn_card_number(prefix)
    
    # Format with spaces
    formatted = " ".join([card_number[i:i+4] for i in range(0, 16, 4)])
    
    # Get user choice for Type
    req_data = request.get_json() or {}
    requested_type = req_data.get('type', 'virtual') # 'virtual' or 'physical'
    
    if requested_type not in ['virtual', 'physical']:
        return jsonify({"error": "Invalid card type."}), 400
    
    new_card = Card(
        user_id=current_user.id,
        number=formatted,
        holder_name=current_user.username.upper(),
        expiry=get_expiry(),
        cvv=f"{random.randint(100,999)}",
        card_type=requested_type,
        tier=tier
    )
    
    db.session.add(new_card)
    db.session.commit()
    
    return jsonify(new_card.to_dict()), 201

@card_bp.route('/<int:card_id>', methods=['DELETE'])
@csrf.exempt
@login_required
def delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    
    if card.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    db.session.delete(card)
    db.session.commit()
    return jsonify({"message": "Card deleted successfully"}), 200

@card_bp.route('/<int:card_id>/reveal', methods=['GET'])
@login_required
def reveal_card(card_id):
    card = Card.query.get_or_404(card_id)
    
    if card.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    # Potential: Require password confirmation here? 
    # For now, relying on session auth as per plan.
    
    return jsonify(card.to_dict(show_sensitive=True)), 200
