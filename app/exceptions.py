class BankError(Exception):
    """Base class for banking exceptions."""
    pass

class InsufficientFundsError(BankError):
    pass

class AccountNotFoundError(BankError):
    pass

class InvalidTransactionError(BankError):
    pass
