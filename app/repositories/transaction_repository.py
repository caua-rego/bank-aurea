from app.extensions import db
from app.models.transaction import Transaction

class TransactionRepository:
    def add(self, transaction):
        db.session.add(transaction)
        # Commit should be handled by service for atomicity usually, but if granular:
        # db.session.commit() 
        # For atomic transfers, we might want to flush or leave commit to the service's transaction block.
        # But to keep simple consistent API, let's assume service manages session for bulk ops
        # or we commit here for single ops.
        # Let's leave commit out for atomic operations controlled by service, or pass a session.
        # For now, simplistic approach: adding to session.
        return transaction 

    def get_by_account(self, account_id):
        return Transaction.query.filter(
            (Transaction.source_account_id == account_id) | 
            (Transaction.target_account_id == account_id)
        ).order_by(Transaction.timestamp.desc()).all()
