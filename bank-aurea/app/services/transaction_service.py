from app.extensions import db
from app.models.transaction import Transaction
from app.models.account import Account
from app.exceptions import InsufficientFundsError, AccountNotFoundError, InvalidTransactionError
from decimal import Decimal

class TransactionService:
    
    def get_history(self, account_id):
        return Transaction.query.filter(
            (Transaction.source_account_id == account_id) | 
            (Transaction.target_account_id == account_id)
        ).order_by(Transaction.timestamp.desc()).all()

    def deposit(self, account_id, amount):
        if amount <= 0:
            raise InvalidTransactionError("Amount must be positive")
            
        account = db.session.get(Account, account_id)
        if not account:
            raise AccountNotFoundError("Account not found")
            
        account.balance += Decimal(str(amount))
        
        transaction = Transaction(
            target_account_id=account.id,
            amount=Decimal(str(amount)),
            type='deposit'
        )
        db.session.add(transaction)
        db.session.commit()
    
    def withdraw(self, account_id, amount):
        amount = Decimal(str(amount))
        if amount <= 0:
            raise InvalidTransactionError("Amount must be positive")

        try:
            # Atomic block with Row Locking (SELECT ... FOR UPDATE)
            # Note: SQLite ignores with_for_update(), but Postgres/MySQL respect it.
            account = db.session.query(Account).filter_by(id=account_id).with_for_update().one()
            
            if account.balance < amount:
                raise InsufficientFundsError("Insufficient funds")
                
            account.balance -= amount
            
            transaction = Transaction(
                source_account_id=account.id,
                amount=amount,
                type='withdrawal'
            )
            db.session.add(transaction)
            db.session.commit()
            return True, "Withdrawal successful"
        except AccountNotFoundError:
            raise
        except Exception as e:
            db.session.rollback()
            raise e

    def transfer(self, source_account_id, target_account_number, amount):
        amount = Decimal(str(amount))
        if amount <= 0:
            raise InvalidTransactionError("Amount must be positive")
            
        try:
            # Atomic block
            # Lock source first to prevent race conditions on balance check
            source = db.session.query(Account).filter_by(id=source_account_id).with_for_update().one()
            
            if source.balance < amount:
                raise InsufficientFundsError("Insufficient funds")
            
            # Lock target
            target = db.session.query(Account).filter_by(number=target_account_number).with_for_update().first()
            if not target:
                raise AccountNotFoundError("Target account not found")
                
            if source.id == target.id:
                 raise InvalidTransactionError("Cannot transfer to self")

            source.balance -= amount
            target.balance += amount
            
            transaction = Transaction(
                source_account_id=source.id,
                target_account_id=target.id,
                amount=amount,
                type='transfer'
            )
            
            db.session.add(transaction)
            db.session.commit()
            return True, "Transfer successful"
            
        except (InsufficientFundsError, AccountNotFoundError, InvalidTransactionError):
            db.session.rollback()
            raise # Re-raise known errors to controller
        except Exception as e:
            db.session.rollback()
            # Log this unexpected error
            raise e # Changed from `raise ef"Transfer failed: {str(e)}"` to `raise e` to match standard exception re-raising.
