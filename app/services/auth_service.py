from app.extensions import db
from app.models.user import User

class AuthService:
    def register_user(self, username, email, password):
        # Create User
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Auto-create Account (Simulated number generation)
        import random
        from decimal import Decimal
        account_number = str(random.randint(10000, 99999))
        from app.models.account import Account
        # Ensure uniqueness logic would go here in prod
        
        account = Account(number=account_number, user_id=user.id, balance=Decimal('1000.00')) # Bonus start balance
        db.session.add(account)
        db.session.commit()
        
        return user
    
    def authenticate_user(self, email, password):
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return user
        return None
