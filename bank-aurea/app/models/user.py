from flask_login import UserMixin
from flask import request, url_for
from app.extensions import db, bcrypt

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    profile_image = db.Column(db.String(255), nullable=True)
    preferences = db.Column(db.Text, nullable=True) # Stored as JSON string
    is_titanium = db.Column(db.Boolean, default=False)

    # Relationship to accounts (One User -> Many Accounts, usually 1 for this app but flexible)
    accounts = db.relationship('Account', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

    def get_tier(self):
        if self.is_titanium:
            return 'titanium'
        
        # Check balance
        # We assume Accounts are loaded. If not, this might trigger a query (lazy=True).
        # For safety, let's handle if accounts is empty.
        if not self.accounts:
            return 'free'
            
        # Assuming main account is the first one or summing all? 
        # Requirement said: "Account balance >= ..." implies aggregate or main.
        # Let's use the highest balance of any account or sum. 
        # Simplest: Sum of all accounts.
        total_balance = sum(account.balance for account in self.accounts)
        
        if total_balance >= 1000000:
            return 'adamantium'
        if total_balance >= 5000:
            return 'gold'
            
        return 'free'

    def to_dict(self):
        profile_image_url = self.profile_image
        if profile_image_url and not str(profile_image_url).startswith('http'):
            if str(profile_image_url).startswith('/static/'):
                profile_image_url = url_for('static', filename=profile_image_url.lstrip('/static/'), _external=True)
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_admin": self.is_admin,
            "profile_image": profile_image_url,
            "preferences": self.preferences, # JSON string, maybe parse it here if needed? kept as raw for consistency
            "tier": self.get_tier(),
            "is_titanium": self.is_titanium
        }

from app.extensions import login_manager

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
