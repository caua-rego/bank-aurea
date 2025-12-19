from datetime import datetime, timezone
from app.extensions import db

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    source_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True) # Nullable for Deposit
    target_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True) # Nullable for Withdrawal
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(db.String(20), nullable=False) # 'transfer', 'deposit', 'withdrawal'
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    source_account = db.relationship('Account', foreign_keys=[source_account_id], backref='sent_transactions')
    target_account = db.relationship('Account', foreign_keys=[target_account_id], backref='received_transactions')

    def __repr__(self):
        return f'<Transaction {self.type}: {self.amount}>'
