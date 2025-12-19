from app.extensions import db
from datetime import datetime

class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    number = db.Column(db.String(19), nullable=False) # stored with spaces or raw
    holder_name = db.Column(db.String(100), nullable=False)
    expiry = db.Column(db.String(5), nullable=False) # MM/YY
    cvv = db.Column(db.String(4), nullable=False)
    
    card_type = db.Column(db.String(20), default='virtual') # virtual, physical
    tier = db.Column(db.String(20), default='free') # free, gold, titanium, adamantium

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self, show_sensitive=False):
        return {
            'id': self.id,
            'number': self.number if show_sensitive else (f"**** **** **** {self.number[-4:]}" if self.number and len(self.number) >= 4 else self.number),
            'holder_name': self.holder_name,
            'expiry': self.expiry,
            'card_type': self.card_type,
            'tier': self.tier,
            'cvv': self.cvv if show_sensitive else '***'
        }
