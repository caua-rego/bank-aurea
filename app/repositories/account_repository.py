from app.extensions import db
from app.models.account import Account

class AccountRepository:
    def create(self, account):
        db.session.add(account)
        db.session.commit()
        return account

    def find_by_number(self, account_number):
        return Account.query.filter_by(number=account_number).first()
    
    def find_by_id(self, account_id):
        return db.session.get(Account, account_id)

    def update(self, account):
        db.session.commit()
        return account
