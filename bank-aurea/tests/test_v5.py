import pytest
from app import create_app, db
from app.models.user import User
from app.models.account import Account
from decimal import Decimal
import time

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        # Cleanup
        import os
        db_path = "test_aurea.db"
        if os.path.exists(db_path):
             # os.remove(db_path) # Keep it if we want to inspect, or remove. 
             pass

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client, app):
    with app.app_context():
        client.post('/register', data={
            'username': 'prec', 'email': 'prec@test.com', 'password': 'password', 'confirm_password': 'password'
        }, follow_redirects=True)
    return client

def test_decimal_precision(auth_client, app):
    auth_client.post('/login', data={'email': 'prec@test.com', 'password': 'password'})
    
    # 0.1 + 0.2 check
    # Deposit 100.10
    auth_client.post('/deposit', data={'amount': '100.10'}, follow_redirects=True)
    # Deposit 200.20
    auth_client.post('/deposit', data={'amount': '200.20'}, follow_redirects=True)
    
    with app.app_context():
        u = User.query.filter_by(username='prec').first()
        # Start 1000 + 100.10 + 200.20 = 1300.30
        # If float: might be 1300.30000000004
        assert u.accounts[0].balance == Decimal('1300.30')
        assert isinstance(u.accounts[0].balance, Decimal)

def test_rate_limiter(client):
    # Spam register
    # Limit is 5 per minute
    for i in range(5):
        resp = client.get('/register')
        assert resp.status_code == 200
        
    resp = client.get('/register')
    assert resp.status_code == 429 # Too Many Requests

def test_insufficient_funds_exception(auth_client, app):
    auth_client.post('/login', data={'email': 'prec@test.com', 'password': 'password'})
    
    # Try to withdraw 1,000,000
    resp = auth_client.post('/withdraw', data={'amount': '1000000.00'}, follow_redirects=True)
    # Should flash error msg
    assert b'Insufficient funds' in resp.data
    
    with app.app_context():
        u = User.query.filter_by(username='prec').first()
        assert u.accounts[0].balance == Decimal('1000.00')
