from app.extensions import db

class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), unique=True, nullable=False) # Renamed from 'conta' to 'number'
    balance = db.Column(db.Numeric(10, 2), default=0.00)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Account {self.number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'balance': self.balance,
            'owner': self.owner.username
        }
